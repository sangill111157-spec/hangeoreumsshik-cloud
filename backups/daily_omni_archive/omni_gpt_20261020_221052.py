#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RGON AUTO-EVOLVE BRAIN v1.0

실행:
    python -X utf8 rgon_auto_evolve_brain.py
    python -X utf8 rgon_auto_evolve_brain.py --ci
    python -X utf8 rgon_auto_evolve_brain.py --audit-only

설계:
- 표준 라이브러리 중심의 결정론적 Plan → Audit → Heal → Verify → Reflect 루프.
- DSPy/AlphaEvolve/Letta/Voyager/LangGraph의 설계 원리를 적용한 경량 구현이며,
  해당 제품의 SDK 또는 실제 모델 최적화 서비스를 사용한다고 가장하지 않는다.
- 생성된 다음 진화 지시문은 승인 대기열에만 저장하며 자동 실행하지 않는다.
- JS 수정은 Node.js 문법 검증이 가능한 경우에만 수행한다.
- 이미지 의미/워터마크 존재를 픽셀만으로 확정하지 않는다.
- 로컬 수정은 백업 후 원자적으로 수행한다. Git push 및 브라우저 재시작은 하지 않는다.
- CI 수정 결과는 아티팩트로 보관되며 저장소에 자동 커밋되지 않는다.
"""

from __future__ import annotations

import argparse
import ast
import copy
import datetime as dt
import hashlib
import importlib
import io
import json
import math
import os
import pickle
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

VERSION = "1.0"
TASK_ID = "TOP1_SELF_EVOLVING_BRAIN"
TITLE = "전 에이전트 합심·융합 자율 진화 두뇌(Auto-Evolve Brain) 상시 가동"
STATUS = "ACTIVE_TOTAL_WAR"
STYLES = ("반전형", "감성형", "비교형", "숫자충격형", "ASMR몰입형")
SHEET_IDS = (
    "1mIu1vXu0luRSDNyjE-WkJaz91otX0OvgaBVrJj6rwnY",
    "1gYDrCuqM2hKQbYyE3cYEZhJZEhrH_Is6tdUhsw-cgaw",
)
SHEET_TABS = ("RGON_두뇌장바구니_헌법", "RGON_진화일지")
MAX_TEXT = 12 * 1024 * 1024
MAX_JSON = 24 * 1024 * 1024

RULES = {
    "R1": {
        "title": "종이컵 정체성 보호",
        "instruction": (
            "disposable white paper cup, single-use takeaway paper cup, "
            "no handle, no ceramic mug, no saucer"
        ),
        "negative_prompt": "ceramic mug, handle, saucer, porcelain cup",
    },
    "R2": {
        "title": "광고 영상·음성 완전 합체",
        "instruction": (
            "edge-tts ko-KR-InJoonNeural narration + 62BPM ducking BGM; "
            "540x960, 30fps, 300 frames, H.264/yuv420p + AAC, "
            "10.000-second MP4; verify duration, frame count and non-silent audio"
        ),
    },
    "R3": {
        "title": "모달·캐시 회귀 방지",
        "instruction": (
            "Mount modal directly under document.body; use isolated stacking "
            "context and z-index:2147483647; version static asset URLs; "
            "do not assume z-index overrides browser top-layer elements."
        ),
    },
    "R4": {
        "title": "Genspark Copy 접두어 소독",
        "instruction": 'code = code.replace(/^Copy\\s*/i, "")',
    },
    "R5": {
        "title": "DOM 바인딩 방어",
        "instruction": (
            "Use optional chaining ?. for nullable DOM event bindings, "
            "or an explicitly verified null guard; never rewrite arbitrary "
            "JavaScript without syntax verification."
        ),
    },
    "R6": {
        "title": "이미지 워터마크·하단 영역 보호",
        "instruction": (
            "no watermark, no logo, no text, no signature; reject known "
            "watermarked outputs; inspect bottom region before use; "
            "crop only when a watermark-region provenance receipt explicitly "
            "authorizes a bottom crop; never claim semantic detection from "
            "filename or metadata alone"
        ),
    },
}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def run_command(args: list[str], timeout: int = 45) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        shell=False,
    )


class Project:
    def __init__(self, root: Path, ci: bool = False, audit_only: bool = False):
        self.root = root.resolve()
        self.ci = ci
        self.audit_only = audit_only
        self.private = self.root / ".rgon_auto_evolve_private"
        if self.private.is_symlink():
            raise RuntimeError("비공개 디렉터리가 심볼릭 링크입니다.")
        self.private.mkdir(parents=True, exist_ok=True)
        self.run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        self.backups = self.private / "backups" / self.run_id
        self.changes: list[dict] = []
        self.notes: list[str] = []
        self.lock_fd: int | None = None
        self.lock_path = self.private / "engine.lock"

    def path(self, relative: str) -> Path:
        candidate = self.root / relative
        try:
            candidate.resolve().relative_to(self.root)
        except ValueError:
            raise RuntimeError(f"프로젝트 외부 경로 차단: {relative}")
        cursor = candidate
        while cursor != self.root:
            if cursor.is_symlink():
                raise RuntimeError(f"심볼릭 링크 경로 차단: {relative}")
            cursor = cursor.parent
        return candidate

    def acquire(self) -> None:
        try:
            self.lock_fd = os.open(
                self.lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
            )
            os.write(
                self.lock_fd,
                json_bytes({"pid": os.getpid(), "created_at": now()}),
            )
        except FileExistsError:
            raise RuntimeError(
                f"다른 실행 또는 잔여 잠금이 있습니다: {self.lock_path}\n"
                "실행 중인 엔진이 없는 것을 확인한 후 잠금 파일을 수동 삭제하세요."
            )

    def release(self) -> None:
        if self.lock_fd is not None:
            os.close(self.lock_fd)
            self.lock_fd = None
            self.lock_path.unlink(missing_ok=True)

    def read(self, relative: str, maximum: int = MAX_TEXT) -> str:
        path = self.path(relative)
        if path.stat().st_size > maximum:
            raise ValueError(f"파일 크기 제한 초과: {relative}")
        return path.read_text(encoding="utf-8-sig")

    def load(self, relative: str, default: Any = None) -> Any:
        if not self.path(relative).exists():
            return copy.deepcopy(default)
        return json.loads(self.read(relative, MAX_JSON))

    def write(self, relative: str, data: bytes, reason: str) -> bool:
        path = self.path(relative)
        old = path.read_bytes() if path.exists() else None
        if old == data:
            return False
        if old is not None:
            backup = self.backups / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(old)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".evolve.tmp", dir=path.parent
        )
        try:
            with os.fdopen(fd, "wb") as output:
                output.write(data)
                output.flush()
                os.fsync(output.fileno())
            if old is not None:
                os.chmod(temporary, path.stat().st_mode & 0o777)
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        self.changes.append(
            {
                "path": relative,
                "reason": reason,
                "before_sha256": digest(old) if old is not None else None,
                "after_sha256": digest(data),
            }
        )
        return True

    def save(self, relative: str, value: Any, reason: str) -> bool:
        return self.write(relative, json_bytes(value), reason)

    def note(self, message: str) -> None:
        self.notes.append(message)


def preserve_object(value: Any) -> dict:
    if isinstance(value, dict):
        return copy.deepcopy(value)
    return {"legacy_data": value} if value is not None else {}


def ensure_ignore(project: Project) -> None:
    relative = ".gitignore"
    text = project.read(relative) if project.path(relative).exists() else ""
    rules = (
        ".rgon_auto_evolve_private/",
        "*.evolve.tmp",
        "*.pickle*",
        "config/token*",
    )
    missing = [rule for rule in rules if rule not in text.splitlines()]
    if missing:
        project.write(
            relative,
            (text.rstrip() + "\n\n# RGON Auto-Evolve private data\n"
             + "\n".join(missing) + "\n").encode("utf-8"),
            "진화 백업 및 OAuth 토큰 공개 방지",
        )


def register_top1_schedule(project: Project) -> dict:
    entry = {
        "priority": 1,
        "task_id": TASK_ID,
        "title": TITLE,
        "status": STATUS,
        "engine": "rgon_auto_evolve_brain.py",
        "version": VERSION,
        "updated_at": now(),
        "execution_policy": {
            "local": "explicit invocation",
            "ci": "daily GitHub Actions",
            "next_evolution": "commander approval required",
            "arbitrary_code_execution": False,
        },
    }
    for relative in ("brain_basket/master_schedule.json", "evolution_memory.json"):
        existing = preserve_object(project.load(relative, {}))
        merged = dict(entry)
        merged.update({k: v for k, v in existing.items() if k not in entry})
        if isinstance(merged.get("schedules"), list):
            other = [
                item for item in merged["schedules"]
                if not isinstance(item, dict) or item.get("task_id") != TASK_ID
            ]
            merged["schedules"] = [copy.deepcopy(entry)] + other
        project.save(relative, merged, "최고 1순위 스케줄 공식 등재")
    return entry


class AntibodyMemory:
    def __init__(self, project: Project):
        self.project = project
        self.relative = "brain_basket/antibody_memory.json"
        self.data = preserve_object(project.load(self.relative, {}))
        if not isinstance(self.data.get("antibodies"), dict):
            self.data["legacy_antibodies"] = self.data.get("antibodies")
            self.data["antibodies"] = {}
        self.rules = self.data["antibodies"]
        for key, value in RULES.items():
            previous = preserve_object(self.rules.get(key, {}))
            self.rules[key] = {
                **previous,
                **value,
                "id": key,
                "kind": "built_in",
                "enabled": True,
            }

    def add_antibody(self, category: str, evidence: str, instruction: str) -> str:
        key = "AUTO_" + digest(category.encode("utf-8"))[:16]
        previous = preserve_object(self.rules.get(key, {}))
        self.rules[key] = {
            **previous,
            "id": key,
            "kind": "observed_failure",
            "title": category,
            "instruction": instruction,
            "evidence": evidence[:1000],
            "first_seen": previous.get("first_seen", now()),
            "last_seen": now(),
            "observations": int(previous.get("observations", 0)) + 1,
            "enabled": True,
            "review_required": True,
        }
        return key

    def save(self) -> None:
        self.data.update(
            {
                "schema_version": 1,
                "updated_at": now(),
                "implementation": "deterministic filesystem antibody memory",
            }
        )
        self.project.save(self.relative, self.data, "항체 기억 및 실패 복기 갱신")


class PromptAndRecipeEvolver:
    def __init__(self, project: Project):
        self.project = project

    @staticmethod
    def find_style(value: Any, style: str) -> dict | None:
        if isinstance(value, dict):
            direct = value.get(style)
            if isinstance(direct, dict):
                return copy.deepcopy(direct)
            if isinstance(direct, str):
                return {"prompt": direct}
            if any(
                value.get(key) == style
                for key in ("style", "name", "type", "스타일", "유형")
            ):
                return copy.deepcopy(value)
            for key, child in value.items():
                if key == "rgon_evolved_styles":
                    continue
                found = PromptAndRecipeEvolver.find_style(child, style)
                if found is not None:
                    return found
        elif isinstance(value, list):
            for child in value:
                found = PromptAndRecipeEvolver.find_style(child, style)
                if found is not None:
                    return found
        return None

    def evolve(self) -> dict:
        relative = "ingredients_basket/grok_5_viral_recipes.json"
        raw = self.project.load(relative, {})
        document = preserve_object(raw)
        defaults = {
            "반전형": ("머그컵인 줄 알았죠?", "손잡이 없이 가볍게, 오늘은 종이컵.", "가볍게 바꿔보세요."),
            "감성형": ("작은 휴식 한 잔", "따뜻한 순간을 담는 하얀 종이컵.", "오늘의 여유를 담으세요."),
            "비교형": ("무겁게 들고 다니세요?", "손잡이 없는 종이컵으로 가볍게.", "지금 비교해 보세요."),
            "숫자충격형": ("딱 10초면 충분해요", "하얀 종이컵 하나로 간결한 순간.", "당신의 한 잔을 담으세요."),
            "ASMR몰입형": ("소리에 집중해 보세요", "종이컵에 음료가 차오르는 순간.", "잠깐, 한 잔의 휴식."),
        }
        evolved = {}
        for style in STYLES:
            recipe = self.find_style(raw, style) or {}
            hook, body, cta = defaults[style]
            recipe.setdefault("hook", hook)
            recipe.setdefault("body", body)
            recipe.setdefault("cta", cta)
            recipe.setdefault(
                "narration",
                f"{recipe['hook']} {recipe['body']} {recipe['cta']}",
            )
            original = recipe.get("prompt", "")
            if not isinstance(original, str):
                original = json.dumps(original, ensure_ascii=False)
            # 동일 항체 블록이 실행마다 중복 누적되지 않도록 한다.
            original = re.sub(
                r"\n?\[RGON_ANTIBODIES_BEGIN\].*?\[RGON_ANTIBODIES_END\]",
                "",
                original,
                flags=re.S,
            ).rstrip()
            block = (
                "\n[RGON_ANTIBODIES_BEGIN]\n"
                f"R1: {RULES['R1']['instruction']}\n"
                f"R6: {RULES['R6']['instruction']}\n"
                "[RGON_ANTIBODIES_END]"
            )
            recipe.update(
                {
                    "style": style,
                    "enabled": True,
                    "status": "ACTIVE",
                    "prompt": original + block,
                    "image_prompt": (
                        "Photorealistic commercial product photography, "
                        "vertical 9:16, wooden table, rolled paper rim, tapered body; "
                        + RULES["R1"]["instruction"]
                        + "; no watermark, no logo, no text, no signature"
                    ),
                    "negative_prompt": (
                        RULES["R1"]["negative_prompt"]
                        + ", watermark, logo, text, signature"
                    ),
                    "required_antibodies": ["R1", "R6"],
                    "timeline": [
                        {"start": 0, "end": 3, "text": recipe["hook"]},
                        {"start": 3, "end": 7, "text": recipe["body"]},
                        {"start": 7, "end": 10, "text": recipe["cta"]},
                    ],
                    "media_contract": RULES["R2"]["instruction"],
                }
            )
            evolved[style] = recipe

        # 기존 스키마를 삭제하거나 styles/recipes 키의 자료형을 변경하지 않는다.
        document["rgon_evolved_styles"] = evolved
        document["rgon_recipe_registry_version"] = 1
        self.project.save(relative, document, "5대 스타일 R1/R6 항체 주입")

        manifest = preserve_object(self.project.load("v5_manifest.json", {}))
        manifest["viral_recipe_registry"] = {
            "source": relative,
            "json_pointer": "/rgon_evolved_styles",
            "active_styles": list(STYLES),
            "count": len(evolved),
            "recipes": evolved,
            "integration": "data registry; existing UI adapter remains unchanged",
        }
        self.project.save(
            "v5_manifest.json", manifest, "STUDIO v5 5종 레시피 레지스트리 동기화"
        )
        return evolved


def javascript_mask(source: str) -> str:
    """주석·문자열을 공백 처리한다. 템플릿 문자열 내부는 보수적으로 전체 제외."""
    chars = list(source)
    index, length = 0, len(source)
    while index < length:
        start = index
        if source.startswith("//", index):
            end = source.find("\n", index)
            index = length if end < 0 else end
        elif source.startswith("/*", index):
            end = source.find("*/", index + 2)
            index = length if end < 0 else end + 2
        elif source[index] in "'\"`":
            quote = source[index]
            index += 1
            while index < length:
                if source[index] == "\\":
                    index += 2
                elif source[index] == quote:
                    index += 1
                    break
                else:
                    index += 1
        else:
            index += 1
            continue
        for position in range(start, min(index, length)):
            if chars[position] not in "\r\n":
                chars[position] = " "
    return "".join(chars)


DOM_BINDING = re.compile(
    r"\bdocument\.(?:getElementById|querySelector)\("
    r"\s*(?:'[^'\r\n]*'|\"[^\"\r\n]*\")\s*\)"
    r"(?P<dot>\.)(?P<method>addEventListener|removeEventListener)\s*\("
)


class SelfAuditorAndHealer:
    def __init__(self, project: Project, memory: AntibodyMemory):
        self.project = project
        self.memory = memory
        self.node = shutil.which("node")
        self.findings: list[dict] = []
        self.tests: list[dict] = []

    def finding(self, category: str, path: str, detail: str, healed=False) -> None:
        item = {
            "category": category,
            "path": path,
            "detail": detail,
            "healed": healed,
        }
        self.findings.append(item)
        self.memory.add_antibody(
            category,
            f"{path}: {detail}",
            f"다음 감사에서 {category} 회귀를 확인하고 검증 가능한 최소 수정만 적용한다.",
        )

    def test(self, name: str, passed: bool, detail: str, weight: int = 1) -> None:
        self.tests.append(
            {"name": name, "passed": bool(passed), "detail": detail, "weight": weight}
        )

    def check_js(self, source: str, module: bool = False) -> tuple[bool, str]:
        if not self.node:
            return False, "Node.js 없음: 문법 검증 및 자동 JS 치유 보류"
        with tempfile.TemporaryDirectory(prefix="rgon_jscheck_") as folder:
            file = Path(folder) / ("candidate.mjs" if module else "candidate.js")
            file.write_text(source, encoding="utf-8")
            result = run_command([self.node, "--check", str(file)])
            return result.returncode == 0, (result.stderr.strip() or "node --check 통과")[:1500]

    def heal_js(self, source: str) -> tuple[str, list[str]]:
        result = source
        actions = []
        # 실제 코드 파일 맨 앞의 Copy만 제거한다. 문자열/주석 내부는 수정하지 않는다.
        cleaned = re.sub(
            r"\ACopy\s*(?=(?:#!|(?:const|let|var|function|class|import|export|"
            r"async)\b|\(\s*\(|\(\s*function))",
            "",
            result,
            count=1,
            flags=re.I,
        )
        if cleaned != result:
            result = cleaned
            actions.append("R4: 파일 선두 Copy 접두어 제거")

        mask = javascript_mask(result)
        replacements = []
        for match in DOM_BINDING.finditer(result):
            if mask[match.start():match.start() + 8] == "document":
                replacements.append(match.start("dot"))
        for offset in reversed(replacements):
            result = result[:offset] + "?." + result[offset + 1:]
        if replacements:
            actions.append(f"R5: 직접 DOM 이벤트 바인딩 {len(replacements)}곳 보호")
        return result, actions

    def audit_javascript(self, relative: str, module: bool = False) -> None:
        if not self.project.path(relative).exists():
            self.test(relative, False, "필수 파일 없음", 2)
            self.finding("missing_required_file", relative, "필수 JS 파일 없음")
            return
        source = self.project.read(relative)
        candidate, actions = self.heal_js(source)
        final = source
        if actions:
            verified, detail = self.check_js(candidate, module)
            healed = verified and not self.project.audit_only
            if healed:
                self.project.write(relative, candidate.encode("utf-8"), "; ".join(actions))
                final = candidate
            self.finding(
                "javascript_antibody_violation",
                relative,
                "; ".join(actions) + ("; " + detail if not verified else ""),
                healed,
            )
        valid, detail = self.check_js(final, module)
        self.test(relative + ":syntax", valid, detail, 2)
        residual, _ = self.heal_js(final)
        self.test(
            relative + ":R4_R5",
            residual == final,
            "지원되는 직접 바인딩 및 파일 선두 Copy 검사; 별칭·동적 코드는 수동 검토 대상",
        )

    def audit_python(self) -> None:
        relative = "omni_bridge.py"
        if not self.project.path(relative).exists():
            self.test(relative, False, "필수 브리지 없음", 2)
            return
        try:
            ast.parse(self.project.read(relative), filename=relative)
            self.test(relative, True, "Python AST 검증 통과", 2)
        except SyntaxError as exc:
            self.test(relative, False, f"구문 오류: line {exc.lineno}", 2)
            self.finding("python_syntax_error", relative, f"line {exc.lineno}")

    def audit_html(self) -> None:
        relative = "rgon_alpha_chat.html"
        if not self.project.path(relative).exists():
            self.test(relative, False, "독대실 HTML 없음", 2)
            return
        source = self.project.read(relative)
        replacements = []
        scripts_ok = True
        script_count = 0
        for match in re.finditer(
            r"<script\b(?P<attrs>[^>]*)>(?P<code>.*?)</script\s*>",
            source,
            re.I | re.S,
        ):
            attrs, code = match["attrs"], match["code"]
            if re.search(r"\bsrc\s*=", attrs, re.I):
                continue
            type_match = re.search(
                r"\btype\s*=\s*['\"]([^'\"]+)['\"]", attrs, re.I
            )
            kind = type_match[1].lower() if type_match else ""
            if kind not in ("", "module", "text/javascript", "application/javascript"):
                continue
            if not code.strip():
                continue
            script_count += 1
            candidate, actions = self.heal_js(code)
            if actions:
                valid, detail = self.check_js(candidate, kind == "module")
                healed = valid and not self.project.audit_only
                if healed:
                    replacements.append((match.start("code"), match.end("code"), candidate))
                    code = candidate
                self.finding(
                    "html_inline_binding_violation",
                    relative,
                    "; ".join(actions) + ("" if valid else "; " + detail),
                    healed,
                )
            valid, _ = self.check_js(code, kind == "module")
            remaining, _ = self.heal_js(code)
            scripts_ok = scripts_ok and valid and remaining == code

        for start, end, code in reversed(replacements):
            source = source[:start] + code + source[end:]
        if replacements:
            self.project.write(relative, source.encode("utf-8"), "HTML 인라인 JS 최소 치유")

        self.test(
            "독대실 inline JS",
            script_count > 0 and scripts_ok,
            f"실행형 인라인 스크립트 {script_count}개 검사",
            2,
        )
        # 정적 단서일 뿐 실제 브라우저의 DOM/stacking 동작 검증은 아니다.
        z_hint = bool(re.search(r"z-index\s*:\s*2147483647", source, re.I))
        body_hint = bool(re.search(r"document\.body", source))
        self.test(
            "R3 모달 정적 계약",
            z_hint and body_hint,
            "최상위 z-index 및 document.body 단서 검사; 브라우저 실측 별도 필요",
        )
        if not (z_hint and body_hint):
            self.finding(
                "modal_contract_unverified", relative,
                "구조를 추정하여 HTML을 재조립하지 않음; R3 검토 필요"
            )

    def audit_shared_copy(self) -> None:
        relative = "omni_shared_clipboard.json"
        if not self.project.path(relative).exists():
            return
        data = self.project.load(relative)
        changed = 0

        def clean(value: Any) -> Any:
            nonlocal changed
            if isinstance(value, list):
                return [clean(item) for item in value]
            if isinstance(value, dict):
                output = {}
                for key, child in value.items():
                    if key in ("code", "source_code") and isinstance(child, str):
                        fixed = re.sub(r"\ACopy\s*", "", child, count=1, flags=re.I)
                        changed += fixed != child
                        output[key] = fixed
                    else:
                        output[key] = clean(child)
                return output
            return value

        cleaned = clean(data)
        if changed:
            healed = not self.project.audit_only
            if healed:
                self.project.save(relative, cleaned, "R4 공유함 코드 접두어 소독")
            self.finding(
                "shared_code_copy_prefix", relative,
                f"명시적 code/source_code 필드 {changed}곳", healed
            )
        self.project.note(
            "chrome.storage.local의 실시간 내용은 이 파일 기반 엔진이 직접 수정하지 않습니다."
        )

    def audit_image(self) -> None:
        relative = "ingredients_basket/sample_paper_cup.jpg"
        path = self.project.path(relative)
        if not path.exists():
            self.test("종이컵 이미지", False, "이미지 없음", 2)
            return
        try:
            from PIL import Image, ImageOps
        except ImportError:
            self.test("종이컵 이미지", False, "Pillow 없음: 이미지 검증 보류", 2)
            return

        receipt_relative = "ingredients_basket/image_provenance.json"
        receipt = preserve_object(self.project.load(receipt_relative, {}))
        before_hash = digest(path.read_bytes())
        binding_valid = receipt.get("sha256") == before_hash
        declared_watermark = binding_valid and receipt.get("watermark_detected") is True
        crop_verified = False

        if declared_watermark:
            # OCR/사람 검수 등 외부의 명시적 영역 판정이 있어야 크롭한다.
            fraction = receipt.get("watermark_bottom_fraction")
            authorized = receipt.get("crop_authorized") is True
            if (
                authorized
                and isinstance(fraction, (int, float))
                and not isinstance(fraction, bool)
                and 0 < fraction <= 0.20
                and not self.project.audit_only
            ):
                with Image.open(path) as opened:
                    image = ImageOps.exif_transpose(opened).convert("RGB")
                    cut = math.ceil(image.height * fraction)
                    image = image.crop((0, 0, image.width, image.height - cut))
                    image = ImageOps.fit(image, (540, 960), Image.Resampling.LANCZOS)
                    buffer = io.BytesIO()
                    image.save(buffer, format="JPEG", quality=95, subsampling=0)
                self.project.write(relative, buffer.getvalue(), "R6 승인된 하단 워터마크 영역 크롭")
                receipt.update(
                    {
                        "sha256": digest(buffer.getvalue()),
                        "watermark_detected": False,
                        "crop_applied_at": now(),
                        "review_status": "crop_applied_requires_visual_review",
                    }
                )
                self.project.save(receipt_relative, receipt, "이미지 크롭 출처 영수증 갱신")
                crop_verified = True
            self.finding(
                "known_image_watermark", relative,
                "SHA-256 결합 출처 영수증의 하단 워터마크 판정",
                crop_verified,
            )

        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                dimensions_ok = image.size == (540, 960)
            self.test("종이컵 이미지 형식", dimensions_ok, "JPEG 디코딩 및 540x960 검사")
        except Exception as exc:
            self.test("종이컵 이미지 형식", False, type(exc).__name__)
            return

        current_hash = digest(path.read_bytes())
        verified_clean = (
            receipt.get("sha256") == current_hash
            and receipt.get("watermark_detected") is False
            and receipt.get("review_status") in (
                "human_verified_clean", "trusted_local_render"
            )
        )
        self.test(
            "R1/R6 이미지 출처 검수",
            verified_clean,
            "출처 영수증 검수 필요; 이미지 의미/워터마크 자동 인식이라고 주장하지 않음",
            2,
        )
        if not verified_clean:
            self.finding(
                "image_semantics_unverified", relative,
                "손잡이·도자기·워터마크 유무에 대한 신뢰 가능한 시각 검수 영수증 필요"
            )

    def find_tool(self, name: str) -> str | None:
        executable = shutil.which(name)
        if executable:
            return executable
        for relative in (
            f"ffmpeg-8.0.1-full_build/bin/{name}.exe",
            f"ffmpeg-8.0.1-full_build/bin/{name}",
        ):
            candidate = self.project.path(relative)
            if candidate.is_file():
                return str(candidate)
        return None

    def audit_media(self) -> None:
        candidates = [
            "ingredients_basket/trimmed_ad_paper_cup_10s.mp4",
            "ingredients_basket/trimmed_ad_10s.mp4",
        ]
        relative = next(
            (name for name in candidates if self.project.path(name).is_file()), None
        )
        if not relative:
            self.test("광고 MP4", False, "검사할 완성본 MP4 없음", 3)
            return
        ffprobe, ffmpeg = self.find_tool("ffprobe"), self.find_tool("ffmpeg")
        if not ffprobe or not ffmpeg:
            self.test("광고 MP4", False, "ffprobe/ffmpeg 없음", 3)
            return
        path = str(self.project.path(relative))
        try:
            result = run_command(
                [
                    ffprobe, "-v", "error", "-count_frames",
                    "-show_streams", "-show_format", "-of", "json", path,
                ],
                timeout=120,
            )
            if result.returncode:
                raise ValueError("ffprobe 실패")
            info = json.loads(result.stdout)
            streams = info.get("streams", [])
            video = next(s for s in streams if s.get("codec_type") == "video")
            audio = next(s for s in streams if s.get("codec_type") == "audio")
            duration = float(info["format"]["duration"])
            frames = int(video.get("nb_read_frames") or video.get("nb_frames") or 0)
            numerator, denominator = video.get("avg_frame_rate", "0/1").split("/")
            fps = float(numerator) / float(denominator)
            video_ok = (
                video.get("codec_name") == "h264"
                and video.get("pix_fmt") == "yuv420p"
                and video.get("width") == 540
                and video.get("height") == 960
                and frames == 300
                and abs(fps - 30) < 0.001
                and abs(duration - 10.0) <= 0.025
            )
            audio_result = run_command(
                [
                    ffmpeg, "-hide_banner", "-nostdin", "-i", path,
                    "-map", "0:a:0", "-af", "volumedetect",
                    "-vn", "-f", "null", "-",
                ],
                timeout=120,
            )
            mean = re.search(
                r"mean_volume:\s*(-?inf|[-\d.]+)\s*dB",
                audio_result.stderr,
                re.I,
            )
            mean_db = float(mean[1]) if mean else float("-inf")
            audio_ok = (
                audio.get("codec_name") == "aac"
                and audio_result.returncode == 0
                and math.isfinite(mean_db)
                and mean_db > -65.0
            )
            self.test(
                "R2 MP4 영상 계약", video_ok,
                f"duration={duration:.6f}s frames={frames} fps={fps:.4f}", 3
            )
            self.test(
                "R2 AAC 비무음", audio_ok,
                f"mean_volume={mean_db}dB; 음성 종류·62BPM·덕킹 의미 검증은 별도 필요", 2
            )
            if not video_ok or not audio_ok:
                self.finding(
                    "media_contract_violation", relative,
                    f"video_ok={video_ok}, audio_ok={audio_ok}; 자동 재인코딩 대신 승인 과제로 대기"
                )
        except Exception as exc:
            self.test("광고 MP4", False, f"검증 실패: {type(exc).__name__}", 3)

    def audit_recipes(self) -> None:
        recipes = self.project.load("ingredients_basket/grok_5_viral_recipes.json", {})
        evolved = recipes.get("rgon_evolved_styles", {}) if isinstance(recipes, dict) else {}
        for style in STYLES:
            item = evolved.get(style, {})
            prompt = item.get("prompt", "") if isinstance(item, dict) else ""
            valid = (
                item.get("enabled") is True
                and RULES["R1"]["instruction"] in prompt
                and RULES["R6"]["instruction"] in prompt
            )
            self.test(f"레시피:{style}", valid, "5대 스타일 R1/R6 계약 검사")

    def run(self) -> dict:
        self.audit_javascript("rgon_aside_extension/background.js")
        self.audit_javascript("rgon_aside_extension/content_aside_bar.js")
        self.audit_python()
        self.audit_html()
        self.audit_shared_copy()
        self.audit_image()
        self.audit_media()
        self.audit_recipes()
        total = sum(item["weight"] for item in self.tests)
        passed = sum(item["weight"] for item in self.tests if item["passed"])
        score = round(100 * passed / total, 2) if total else 0.0
        return {
            "version": VERSION,
            "created_at": now(),
            "health_score": score,
            "score_scope": "가중 정적 검사 및 로컬 미디어 검증; 실제 서비스 SLA 점수 아님",
            "tests": self.tests,
            "findings": self.findings,
            "healed_count": sum(bool(item["healed"]) for item in self.findings),
            "notes": self.project.notes,
        }


class NextEvolutionGenerator:
    def __init__(self, project: Project):
        self.project = project

    def generate(self, report: dict) -> dict:
        failures = [item for item in report["tests"] if not item["passed"]]
        tasks = [
            f"- {item['name']}: {item['detail']}"
            for item in failures
        ] or [
            "- 모든 현재 검사를 유지하면서 실제 브라우저 통합 회귀 테스트를 추가한다.",
            "- 레시피별 광고 품질을 비교할 고정 평가셋과 승인된 벤치마크를 설계한다.",
        ]
        prompt = (
            "# RGON Next Evolution Prompt\n\n"
            f"현재 건강 점수: {report['health_score']}/100\n"
            "상태: 사령관님 승인 대기. 아래 텍스트 자체는 실행 권한이 아니다.\n\n"
            "## 다음 세대 과제\n"
            + "\n".join(tasks)
            + "\n\n## 공동 작업 순서\n"
            "1. 기준 확인 → 항체 기억 조회 → 최소 변경 계획 작성.\n"
            "2. Claude/GPT/Grok 등 사용 가능한 전문가에게 독립 검토를 요청한다.\n"
            "3. 변경 전 백업, 변경 후 AST/node --check/미디어 계약을 검증한다.\n"
            "4. 실패 시 원인을 기록하고 검증된 범위만 재시도한다.\n"
            "5. OAuth 토큰·비밀키·비공개 메모리는 전송하지 않는다.\n"
            "6. 무단 코드 실행·자동 배포·자동 Git push는 금지한다.\n\n"
            "## 반드시 유지할 항체\n"
            + "\n".join(f"- {key}: {value['instruction']}" for key, value in RULES.items())
            + "\n"
        )
        self.project.write(
            "brain_basket/next_evolution_prompt.txt",
            prompt.encode("utf-8"),
            "다음 세대 진화 지시문 생성",
        )
        # 실행 시각을 ID에 포함하지 않아 동일 과제가 매번 중복되지 않는다.
        identifier = "evolve_" + digest(prompt.encode("utf-8"))[:20]
        relative = "omni_dispatch_queue.json"
        existing = self.project.load(relative, {})
        if isinstance(existing, list):
            queue = existing
Copy
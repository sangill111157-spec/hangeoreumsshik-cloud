#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RGON Auto-Evolve Brain v1.0

Local-only fusion of persistent antibody memory, reflexion audit/heal,
prompt constraint checks, and a next-task writer. Mutates files only inside
this project tree. Never executes remote prompts. Never reads a pickle except
ROOT/token.pickle, and only to append a schedule row to the two named sheets.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

VERSION = "1.0"
TASK_ID = "TOP1_SELF_EVOLVING_BRAIN"
TITLE = "전 에이전트 합심·융합 자율 진화 두뇌(Auto-Evolve Brain) 상시 가동"
STATUS = "ACTIVE_TOTAL_WAR"
EXPLICIT_ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
SHEET_IDS = (
    "1mIu1vXu0luRSDNyjE-WkJaz91otX0OvgaBVrJj6rwnY",
    "1gYDrCuqM2hKQbYyE3cYEZhJZEhrH_Is6tdUhsw-cgaw",
)
SHEET_TABS = ("RGON_두뇌장바구니_헌법", "RGON_진화일지")
STYLE_NAMES = ("반전형", "감성형", "비교형", "숫자충격형", "ASMR몰입형")
KST = timezone(timedelta(hours=9))
MAX_TEXT = 1_500_000
TOKEN_MAX = 262_144
LOCK_STALE = 1200
WORKFLOW_MARK = "# RGON_EVOLVE_STEP"
PAPER_CLAUSE = (
    "Disposable paper cup only, never a ceramic mug. "
    "Exclude the bottom watermark band. No logo, no watermark text."
)
NAMED_FILES = (
    "rgon_aside_extension/background.js",
    "rgon_aside_extension/content_aside_bar.js",
    "omni_bridge.py",
    "rgon_alpha_chat.html",
)
TEXT_SUFFIXES = {".js", ".mjs", ".html", ".htm", ".py", ".json", ".txt", ".md"}
JS_EVENT_RE = re.compile(
    r"(document\.(?:getElementById|querySelector|querySelectorAll)\([^)\n]{1,180}\))"
    r"(?!\?)"
    r"(\s*\.\s*(?:addEventListener|removeEventListener|onclick|oninput|onchange|onsubmit))"
)
COPY_LINE_RE = re.compile(
    r"(?m)^(?:Copy[ \t]*)+"
    r"(?=(?:#!/|<!|import\b|const\b|let\b|var\b|function\b|\(function\b|"
    r"\{|\[|\"use strict\"|'use strict'))",
    re.I,
)
BUILTIN = (
    {"id": "R1", "rule": "도자기 머그컵 금지. 일회용 종이컵만 강제.", "enforce": "prompt"},
    {"id": "R2", "rule": "성우+BGM 10.000초 / 300프레임 고정.", "enforce": "scan"},
    {"id": "R3", "rule": "모달 z-index 최상위 및 캐시 버스트.", "enforce": "scan"},
    {"id": "R4", "rule": "Genspark Copy 접두어는 로드/저장/렌더 전에 제거.", "enforce": "heal"},
    {"id": "R5", "rule": "JS DOM 이벤트 바인딩은 옵셔널 체이닝 ?. 강제.", "enforce": "heal"},
    {"id": "R6", "rule": "Pollinations 하단 워터마크 영역은 감지 시 크롭.", "enforce": "heal"},
)


class EvolveBusy(RuntimeError):
    pass


def now_iso():
    return datetime.now(KST).isoformat(timespec="seconds")


def configure_stdio():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def resolve_root():
    here = Path(__file__).resolve().parent
    markers = (
        "rgon_aside_extension",
        "ingredients_basket",
        "brain_basket",
        "omni_bridge.py",
        "rgon_alpha_chat.html",
    )
    if any((here / name).exists() for name in markers) or here == EXPLICIT_ROOT:
        return here
    if EXPLICIT_ROOT.exists():
        return EXPLICIT_ROOT
    return here


def inside(root, path):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def rel(root, path):
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except (ValueError, OSError):
        return str(path)


class FileLock:
    def __init__(self, path):
        self.path = path
        self.fd = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fd = self._open()
        os.write(self.fd, str(os.getpid()).encode("ascii", "replace"))
        return self

    def _open(self):
        try:
            return os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                age = time.time() - self.path.stat().st_mtime
            except OSError:
                age = 0
            if age < LOCK_STALE:
                raise EvolveBusy("another evolve run holds the lock")
            try:
                self.path.unlink()
            except OSError as exc:
                raise EvolveBusy("stale lock could not be cleared") from exc
            return os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)

    def __exit__(self, exc_type, exc, tb):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        try:
            self.path.unlink()
        except OSError:
            pass
        return False


def read_json(path, default):
    if not path.exists() or not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        bad = path.with_name(path.name + ".corrupt-bak")
        if not bad.exists():
            try:
                shutil.copy2(path, bad)
            except OSError:
                pass
        return default


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def read_text(path):
    try:
        raw = path.read_bytes()
    except OSError:
        return None, None
    if len(raw) > MAX_TEXT:
        return None, None
    if raw.startswith(b"\xef\xbb\xbf"):
        try:
            return raw[3:].decode("utf-8"), "utf-8-sig"
        except UnicodeDecodeError:
            return None, None
    for enc in ("utf-8", "cp949"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return None, None


def write_text(path, text, enc):
    data = text.encode("utf-8" if enc == "utf-8-sig" else enc)
    if enc == "utf-8-sig":
        data = b"\xef\xbb\xbf" + data
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def backup_pair(path):
    first = path.with_name(path.name + ".bak-evolve")
    if not first.exists():
        shutil.copy2(path, first)
    run = path.with_name(path.name + ".bak-evolve-run")
    shutil.copy2(path, run)
    return run


def restore(path, run_backup):
    shutil.copy2(run_backup, path)


def skip_path(path):
    name = path.name.lower()
    if path.is_symlink():
        return True
    if ".bak-" in path.name or name.endswith(".tmp"):
        return True
    if name in {"token.pickle", "credentials.json", "rgon_auto_evolve_brain.py"}:
        return True
    return False


class AntibodyMemory:
    def __init__(self, path):
        self.path = path
        self.doc = read_json(path, {})
        if not isinstance(self.doc, dict):
            self.doc = {"legacy": self.doc}
        stored = self.doc.get("antibodies")
        self.antibodies = []
        seen = set()
        if isinstance(stored, list):
            for item in stored:
                if isinstance(item, dict) and item.get("id") and item["id"] not in seen:
                    seen.add(item["id"])
                    self.antibodies.append(item)
        for item in BUILTIN:
            if item["id"] not in seen:
                row = dict(item)
                row["hits"] = 0
                row["origin"] = "builtin"
                self.antibodies.append(row)
                seen.add(item["id"])

    def add_antibody(self, rule_id, rule, evidence):
        for item in self.antibodies:
            if item.get("id") == rule_id:
                item["hits"] = int(item.get("hits") or 0) + 1
                item["last_seen"] = now_iso()
                item["last_evidence"] = str(evidence)[:240]
                return item
        if sum(1 for item in self.antibodies if item.get("origin") == "discovered") >= 20:
            return None
        row = {
            "id": rule_id,
            "rule": rule,
            "enforce": "memory",
            "hits": 1,
            "origin": "discovered",
            "last_seen": now_iso(),
            "last_evidence": str(evidence)[:240],
        }
        self.antibodies.append(row)
        return row

    def hit(self, rule_id, evidence=""):
        return self.add_antibody(rule_id, rule_id, evidence)

    def save(self, schedule_doc):
        previous_runs = self.doc.get("runs") if isinstance(self.doc.get("runs"), list) else []
        rest = {
            key: value
            for key, value in self.doc.items()
            if key not in {"priority", "task_id", "title", "status", "antibodies", "tasks", "runs"}
        }
        out = {
            "priority": 1,
            "task_id": TASK_ID,
            "title": TITLE,
            "status": STATUS,
            "antibodies": self.antibodies,
            "tasks": schedule_doc.get("tasks", []),
            "runs": previous_runs[:30],
        }
        out.update(rest)
        self.doc = out
        write_json(self.path, out)
        return out


def find_token(root):
    candidates = (
        root / "token.pickle",
        root / "credentials" / "token.pickle",
        root / "tokens" / "token.pickle",
    )
    for path in candidates:
        if path.is_file() and not path.is_symlink() and inside(root, path):
            try:
                if path.stat().st_size <= TOKEN_MAX:
                    return path
            except OSError:
                continue
    return None


def load_sheets_service(token_path):
    import pickle
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    with token_path.open("rb") as handle:
        creds = pickle.load(handle)
    if not hasattr(creds, "valid"):
        raise RuntimeError("token.pickle is not an OAuth credential")
    if not creds.valid:
        if getattr(creds, "expired", False) and getattr(creds, "refresh_token", None):
            creds.refresh(Request())
            with token_path.open("wb") as handle:
                pickle.dump(creds, handle)
        else:
            raise RuntimeError("token invalid and not refreshable")
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def ensure_tab(service, spreadsheet_id, title):
    meta = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields="sheets.properties.title",
    ).execute()
    titles = [item.get("properties", {}).get("title", "") for item in meta.get("sheets", [])]
    if title in titles:
        return
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"addSheet": {"properties": {"title": title}}}]},
    ).execute()


def register_sheet_row(service, spreadsheet_id, title, row):
    ensure_tab(service, spreadsheet_id, title)
    quoted = "'" + title.replace("'", "''") + "'"
    existing = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=quoted + "!C1:C2000",
    ).execute()
    flat = [cell for cells in existing.get("values", []) for cell in cells]
    if TASK_ID in flat:
        return "present"
    header = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=quoted + "!A1:A1",
    ).execute()
    if not header.get("values"):
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=quoted + "!A1:F1",
            valueInputOption="RAW",
            body={"values": [["label", "priority", "task_id", "title", "status", "updated_at"]]},
        ).execute()
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=quoted + "!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()
    return "registered"


def register_top1_schedule(root):
    basket = root / "brain_basket"
    basket.mkdir(parents=True, exist_ok=True)
    record = {
        "priority": 1,
        "task_id": TASK_ID,
        "title": TITLE,
        "status": STATUS,
        "updated_at": now_iso(),
        "label": "[최고 1순위 스케줄]",
    }
    schedule_path = basket / "master_schedule.json"
    current = read_json(schedule_path, {})
    if not isinstance(current, dict):
        current = {"legacy": current}
    tasks = current.get("tasks") if isinstance(current.get("tasks"), list) else []
    tasks = [item for item in tasks if not (isinstance(item, dict) and item.get("task_id") == TASK_ID)]
    tasks.insert(0, record)
    rest = {
        key: value
        for key, value in current.items()
        if key not in {"priority", "task_id", "title", "status", "tasks"}
    }
    schedule = {
        "priority": 1,
        "task_id": TASK_ID,
        "title": TITLE,
        "status": STATUS,
        "tasks": tasks,
    }
    schedule.update(rest)
    write_json(schedule_path, schedule)

    memory = AntibodyMemory(basket / "evolution_memory.json")
    memory.save(schedule)
    row = ["[최고 1순위 스케줄]", "1", TASK_ID, TITLE, STATUS, record["updated_at"]]
    sheets = register_sheets(root, row)
    return {
        "record": record,
        "schedule_path": rel(root, schedule_path),
        "memory_path": rel(root, basket / "evolution_memory.json"),
        "sheets": sheets,
        "memory": memory,
        "schedule": schedule,
    }


def register_sheets(root, row):
    token_path = find_token(root)
    if token_path is None:
        return "skipped: no token.pickle"
    try:
        service = load_sheets_service(token_path)
    except Exception as exc:
        return "skipped: " + type(exc).__name__
    results = []
    for spreadsheet_id in SHEET_IDS:
        for title in SHEET_TABS:
            try:
                state = register_sheet_row(service, spreadsheet_id, title, row)
                results.append(spreadsheet_id[:6] + "/" + title + "=" + state)
            except Exception as exc:
                results.append(spreadsheet_id[:6] + "/" + title + "=" + type(exc).__name__)
    return "; ".join(results)


def iter_scan_files(root):
    seen = set()
    for relative in NAMED_FILES:
        path = root / relative
        if path.is_file() and not skip_path(path) and inside(root, path):
            seen.add(path.resolve())
            yield path
    extension = root / "rgon_aside_extension"
    basket = root / "ingredients_basket"
    roots = [path for path in (extension, basket) if path.is_dir()]
    for base in roots:
        for path in base.rglob("*"):
            if not path.is_file() or skip_path(path) or not inside(root, path):
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES | {".jpg", ".jpeg", ".mp4"}:
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            yield path


def paper_cup_path(root):
    direct = root / "ingredients_basket" / "sample_paper_cup.jpg"
    if direct.is_file() and not direct.is_symlink():
        return direct
    basket = root / "ingredients_basket"
    if not basket.is_dir():
        return None
    for path in basket.rglob("sample_paper_cup.jpg"):
        if path.is_file() and not path.is_symlink() and inside(root, path):
            return path
    return None


def probe_duration(path):
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    try:
        return float((proc.stdout or "").strip())
    except ValueError:
        return None


def watermark_exposed(path):
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        with Image.open(path) as image:
            if getattr(image, "n_frames", 1) > 1:
                return False
            gray = image.convert("L")
            width, height = gray.size
            if width < 80 or height < 80:
                return False
            band = max(16, int(height * 0.08))
            step = max(1, width // 80)

            def stats(y0, y1):
                vals = [gray.getpixel((x, y)) for y in range(y0, y1) for x in range(0, width, step)]
                if not vals:
                    return 0.0, 0.0
                mean = sum(vals) / len(vals)
                var = sum((value - mean) ** 2 for value in vals) / len(vals)
                return mean, var

            mean_b, var_b = stats(height - band, height)
            mean_a, var_a = stats(max(0, height - (band * 3)), height - band)
    except (OSError, ValueError):
        return None
    return var_b < 150 and var_a > (var_b * 2) and abs(mean_b - mean_a) > 18


def crop_bottom_band(path):
    from PIL import Image

    with Image.open(path) as image:
        if getattr(image, "n_frames", 1) > 1:
            return False
        rgb = image.convert("RGB")
        width, height = rgb.size
        band = max(16, int(height * 0.08))
        if height - band < 32:
            return False
        cropped = rgb.crop((0, 0, width, height - band))
        backup_pair(path)
        cropped.save(path, format="JPEG", quality=95)
    return True


class SelfAuditorAndHealer:
    def __init__(self, root, memory):
        self.root = root
        self.memory = memory
        self.changed = []
        self.checks = []

    def scan(self):
        findings = []
        present = {rel(self.root, path) for path in iter_scan_files(self.root)}
        for relative in NAMED_FILES:
            if relative not in present and not (self.root / relative).is_file():
                findings.append({"kind": "missing", "path": relative, "rule": "file"})
        copy_hits = 0
        dom_hits = 0
        eval_hits = 0
        z_missing = False
        for path in iter_scan_files(self.root):
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text, _enc = read_text(path)
            if text is None:
                continue
            relative = rel(self.root, path)
            if COPY_LINE_RE.search(text):
                copy_hits += 1
                findings.append({"kind": "copy", "path": relative, "rule": "R4"})
                self.memory.hit("R4", relative)
            if path.suffix.lower() in {".js", ".mjs", ".html", ".htm", ".py"} and JS_EVENT_RE.search(text):
                dom_hits += 1
                findings.append({"kind": "dom", "path": relative, "rule": "R5"})
                self.memory.hit("R5", relative)
            if path.suffix.lower() in {".js", ".mjs", ".html", ".htm"} and re.search(r"\beval\s*\(", text):
                eval_hits += 1
                self.memory.add_antibody("R7", "흡수 텍스트에 eval 실행 금지. 발견만 기록하고 자동 삭제하지 않음.", relative)
            if path.suffix.lower() in {".html", ".htm", ".js", ".mjs"} and re.search(r"modal|독대실", text, re.I):
                if not re.search(r"z-index\s*:\s*[0-9]{4,}", text, re.I):
                    z_missing = True
        if z_missing:
            findings.append({"kind": "z-index", "path": "modal", "rule": "R3"})
            self.memory.hit("R3", "modal without a 4-digit z-index")
        image = paper_cup_path(self.root)
        image_state = "absent"
        if image is not None:
            marker = self._crop_state()
            key = rel(self.root, image)
            if marker.get(key, {}).get("cropped_once"):
                image_state = "already-cropped"
            else:
                exposed = watermark_exposed(image)
                if exposed is None:
                    image_state = "unverified-no-pillow"
                elif exposed:
                    image_state = "exposed"
                    findings.append({"kind": "watermark", "path": key, "rule": "R6"})
                    self.memory.hit("R6", key)
                else:
                    image_state = "not-detected"
        durations = []
        basket = self.root / "ingredients_basket"
        if basket.is_dir():
            for path in basket.rglob("*.mp4"):
                if path.is_file() and not path.is_symlink() and inside(self.root, path):
                    duration = probe_duration(path)
                    durations.append({"path": rel(self.root, path), "seconds": duration})
                    if duration is not None and abs(duration - 10.0) > 0.05:
                        findings.append({"kind": "duration", "path": rel(self.root, path), "rule": "R2"})
                        self.memory.hit("R2", rel(self.root, path))
        return {
            "findings": findings,
            "copy_hits": copy_hits,
            "dom_hits": dom_hits,
            "eval_hits": eval_hits,
            "z_missing": z_missing,
            "image_state": image_state,
            "durations": durations,
            "missing": [item["path"] for item in findings if item["kind"] == "missing"],
        }

    def _crop_state_path(self):
        return self.root / "ingredients_basket" / ".r6_crop_state.json"

    def _crop_state(self):
        data = read_json(self._crop_state_path(), {})
        return data if isinstance(data, dict) else {}

    def heal(self, report):
        self.changed = []
        self.checks = []
        integrity_ok = True
        for path in list(iter_scan_files(self.root)):
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text, enc = read_text(path)
            if text is None or enc is None:
                continue
            updated = COPY_LINE_RE.sub("", text)
            if path.suffix.lower() in {".js", ".mjs", ".html", ".htm", ".py"}:
                updated = JS_EVENT_RE.sub(r"\1?\2", updated)
            if updated == text or not updated.strip():
                continue
            run_backup = backup_pair(path)
            write_text(path, updated, enc)
            ok, detail = self._verify(path)
            self.checks.append({"path": rel(self.root, path), "ok": ok, "detail": detail})
            if ok:
                self.changed.append(rel(self.root, path))
            else:
                restore(path, run_backup)
                integrity_ok = False
        if report.get("image_state") == "exposed":
            image = paper_cup_path(self.root)
            if image is not None:
                try:
                    if crop_bottom_band(image):
                        state = self._crop_state()
                        state[rel(self.root, image)] = {"cropped_once": True, "at": now_iso()}
                        write_json(self._crop_state_path(), state)
                        self.changed.append(rel(self.root, image))
                        self.checks.append({"path": rel(self.root, image), "ok": True, "detail": "cropped-once"})
                    else:
                        integrity_ok = False
                except Exception as exc:
                    self.checks.append({"path": rel(self.root, image), "ok": False, "detail": type(exc).__name__})
                    integrity_ok = False
        return {"changed": self.changed, "checks": self.checks, "integrity_ok": integrity_ok}

    def _verify(self, path):
        suffix = path.suffix.lower()
        if suffix in {".js", ".mjs"}:
            try:
                proc = subprocess.run(
                    ["node", "--check", str(path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
            except FileNotFoundError:
                return False, "node-missing"
            except subprocess.TimeoutExpired:
                return False, "node-timeout"
            if proc.returncode != 0:
                return False, "node-check-failed"
            return True, "node-check"
        if suffix == ".py":
            try:
                import py_compile
                py_compile.compile(str(path), doraise=True)
            except Exception:
                return False, "py-compile-failed"
            return True, "py-compile"
        return True, "text-only"


def recipe_path(root):
    return root / "ingredients_basket" / "grok_5_viral_recipes.json"


def manifest_paths(root):
    found = []
    for path in (root / "ingredients_basket" / "v5_manifest.json", root / "v5_manifest.json"):
        if path.exists():
            found.append(path)
    if not found:
        found.append(root / "ingredients_basket" / "v5_manifest.json")
    return found


def style_list(doc):
    if isinstance(doc, list):
        return doc, doc
    if isinstance(doc, dict):
        for key in ("recipes", "styles", "templates"):
            if isinstance(doc.get(key), list):
                return doc[key], doc
    return [], doc


def style_name(item):
    if not isinstance(item, dict):
        return ""
    for key in ("style_name", "name", "style"):
        value = item.get(key)
        if isinstance(value, str):
            return value.strip()
    return ""


def skeleton_style(name):
    return {
        "style_name": name,
        "hook_0_3s": name + " 훅",
        "body_3_7s": "{topic} 한 장면",
        "cta_7_10s": "저장하고 다시 봐",
        "narration_10s": "{topic}. 한 번만 다시 봐. 저장해.",
        "viral_title": "{topic} " + name,
        "adobe_firefly_prompt_en": "Vertical 9:16 photoreal commercial still of a disposable paper cup as {topic_en}. " + PAPER_CLAUSE,
        "suno_bgm_prompt_en": "10-second instrumental ad bed, no vocals, phone-speaker mix, no intro.",
        "antibodies": ["R1", "R2", "R6"],
    }


def wash_copy_value(value):
    if isinstance(value, str):
        return COPY_LINE_RE.sub("", value) if COPY_LINE_RE.search(value) else value
    if isinstance(value, list):
        return [wash_copy_value(item) for item in value]
    if isinstance(value, dict):
        return {key: wash_copy_value(item) for key, item in value.items()}
    return value


def inject_constraints(style):
    style = wash_copy_value(style)
    prompt = style.get("adobe_firefly_prompt_en")
    if not isinstance(prompt, str) or not prompt.strip():
        style["adobe_firefly_prompt_en"] = "Vertical 9:16 photoreal commercial still of {topic_en}. " + PAPER_CLAUSE
    elif PAPER_CLAUSE not in style["adobe_firefly_prompt_en"]:
        style["adobe_firefly_prompt_en"] = style["adobe_firefly_prompt_en"].rstrip() + " " + PAPER_CLAUSE
    if "ceramic mug" in style["adobe_firefly_prompt_en"].lower() and "never a ceramic mug" not in style["adobe_firefly_prompt_en"]:
        style["adobe_firefly_prompt_en"] += " Never a ceramic mug."
    ids = style.get("antibodies") if isinstance(style.get("antibodies"), list) else []
    for rule_id in ("R1", "R2", "R6"):
        if rule_id not in ids:
            ids.append(rule_id)
    style["antibodies"] = ids
    style["duration_seconds"] = 10.0
    style["frames"] = 300
    return style


def covered(style):
    blob = json.dumps(style, ensure_ascii=False)
    return PAPER_CLAUSE in blob and "R1" in blob and "R6" in blob


class PromptAndRecipeEvolver:
    def __init__(self, root, memory):
        self.root = root
        self.memory = memory

    def evolve(self):
        path = recipe_path(self.root)
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = read_json(path, [])
        styles, holder = style_list(raw if raw != {} else [])
        by_name = {}
        for item in styles:
            if isinstance(item, dict) and style_name(item):
                by_name[style_name(item)] = inject_constraints(item)
        for name in STYLE_NAMES:
            if name not in by_name:
                by_name[name] = skeleton_style(name)
                self.memory.add_antibody("R8", "누락된 바이럴 스타일은 삭제하지 말고 최소 레시피로 채운다.", name)
        ordered = [by_name[name] for name in STYLE_NAMES]
        extras = [item for item in styles if isinstance(item, dict) and style_name(item) not in STYLE_NAMES]
        final_styles = ordered + [inject_constraints(item) for item in extras]
        if isinstance(holder, dict) and holder is not raw:
            for key in ("recipes", "styles", "templates"):
                if isinstance(holder.get(key), list):
                    holder[key] = final_styles
                    payload = holder
                    break
            else:
                payload = final_styles
        elif isinstance(raw, dict) and any(isinstance(raw.get(key), list) for key in ("recipes", "styles", "templates")):
            for key in ("recipes", "styles", "templates"):
                if isinstance(raw.get(key), list):
                    raw[key] = final_styles
                    payload = raw
                    break
        else:
            payload = final_styles
        write_json(path, payload)
        alive = []
        for name in STYLE_NAMES:
            style = by_name[name]
            alive.append({"style_name": name, "alive": covered(style), "antibodies": style.get("antibodies", [])})
        manifest = {
            "version": "v5",
            "synced_at": now_iso(),
            "source": rel(self.root, path),
            "duration_seconds": 10.0,
            "frames": 300,
            "styles": alive,
        }
        written = []
        for target in manifest_paths(self.root):
            write_json(target, manifest)
            written.append(rel(self.root, target))
        return {"recipes": rel(self.root, path), "manifests": written, "alive": alive}


class NextEvolutionGenerator:
    def __init__(self, root):
        self.root = root

    def build(self, before, after, heal, recipes):
        gaps = []
        if after.get("missing"):
            gaps.append("없는 파일: " + ", ".join(after["missing"]))
        if after.get("copy_hits"):
            gaps.append("Copy 잔류가 치유 후에도 %s건" % after["copy_hits"])
        if after.get("dom_hits"):
            gaps.append("미보호 DOM이 치유 후에도 %s건" % after["dom_hits"])
        if after.get("image_state") == "exposed":
            gaps.append("sample_paper_cup.jpg 워터마크 감지가 남아 있음")
        if after.get("image_state") == "unverified-no-pillow":
            gaps.append("Pillow가 없어 R6을 눈으로 확인하지 못함")
        dead = [item["style_name"] for item in recipes.get("alive", []) if not item.get("alive")]
        if dead:
            gaps.append("레시피 항체 미주입: " + ", ".join(dead))
        for item in after.get("durations", []):
            if item.get("seconds") is not None and abs(item["seconds"] - 10.0) > 0.05:
                gaps.append(item["path"] + " 길이가 10.000초가 아님")
        if not gaps:
            gaps.append("자동 치유 범위는 통과. 다음은 사람 검토가 필요한 확장만 남김")
        lines = [
            "다음 세대 진화 지시문",
            "우선순위: 1",
            "대상: shin-agent 로컬 트리만. 외부 시스템 침투, 토큰 반출, 원격 코드 실행은 하지 말 것.",
            "현재 건강 점수: %s -> %s" % (before.get("score"), after.get("score")),
            "남은 틈:",
        ]
        lines.extend("- " + gap for gap in gaps)
        lines.extend([
            "다음 작업:",
            "1) 남은 Copy/DOM/워터마크 항목만 백업 후 수정하고 node --check 또는 py_compile로 확인할 것.",
            "2) 10초/300프레임이 아닌 MP4는 재인코딩하지 말고 목록만 올릴 것.",
            "3) 모달 z-index와 캐시 버스트는 기존 UI를 지우지 말고 수치만 보강할 것.",
            "4) 치유 결과를 검토한 뒤 사람이 원클릭으로 발사할 것. 이 파일을 자동 실행하지 말 것.",
        ])
        text = "\n".join(lines) + "\n"
        path = self.root / "brain_basket" / "next_evolution_prompt.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        queue_path = self.root / "omni_dispatch_queue.json"
        item = {
            "type": "OMNI_DISPATCH",
            "priority": 1,
            "task_id": "NEXT_EVOLUTION_" + datetime.now(KST).strftime("%Y%m%d%H%M%S"),
            "source": "rgon_auto_evolve_brain",
            "created_at": now_iso(),
            "auto_execute": False,
            "prompt": text,
        }
        self._enqueue(queue_path, item)
        return {"path": rel(self.root, path), "queue": rel(self.root, queue_path), "summary": gaps, "text": text}

    def _enqueue(self, path, item):
        current = read_json(path, [])
        if isinstance(current, list):
            queue = current
            holder = None
        elif isinstance(current, dict) and isinstance(current.get("queue"), list):
            queue = current["queue"]
            holder = current
        else:
            queue = []
            holder = {"legacy": current, "queue": queue} if current else None
        queue.append(item)
        own = [row for row in queue if isinstance(row, dict) and row.get("source") == "rgon_auto_evolve_brain"]
        if len(own) > 20:
            drop = len(own) - 20
            kept = []
            for row in queue:
                if drop and isinstance(row, dict) and row.get("source") == "rgon_auto_evolve_brain":
                    drop -= 1
                    continue
                kept.append(row)
            queue = kept
        if holder is None and isinstance(current, list):
            write_json(path, queue)
        elif holder is None:
            write_json(path, queue)
        else:
            holder["queue"] = queue
            write_json(path, holder)


def score_report(report, recipes, verified):
    score = 100
    score -= min(30, 15 * len(report.get("missing", [])))
    score -= min(20, 8 * report.get("copy_hits", 0))
    score -= min(20, 8 * report.get("dom_hits", 0))
    if report.get("z_missing"):
        score -= 8
    if report.get("image_state") == "exposed":
        score -= 15
    elif report.get("image_state") == "unverified-no-pillow":
        score -= 5
    for item in report.get("durations", []):
        if item.get("seconds") is not None and abs(item["seconds"] - 10.0) > 0.05:
            score -= 5
    dead = [item for item in recipes.get("alive", []) if not item.get("alive")]
    score -= min(25, 5 * len(dead))
    if not verified:
        score -= 10
    report["score"] = max(0, min(100, score))
    return report["score"]


def upgrade_external_kitchen_workflow(root):
    path = root / ".github" / "workflows" / "rgon_external_brain_kitchen.yml"
    path.parent.mkdir(parents=True, exist_ok=True)
    default = """name: RGON External Brain Kitchen
on:
  schedule:
    - cron: '0 17 * * *'
  workflow_dispatch:
permissions:
  contents: read
jobs:
  rgon_auto_evolve_brain:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install Pillow for image heal
        run: python -m pip install --disable-pip-version-check pillow
      - name: Unattended self audit and heal
        run: python rgon_auto_evolve_brain.py --ci
"""
    if not path.exists():
        path.write_text(default, encoding="utf-8", newline="\n")
        return "created"
    text = path.read_text(encoding="utf-8")
    has_cmd = "rgon_auto_evolve_brain.py --ci" in text
    has_dispatch = "workflow_dispatch" in text
    has_schedule = re.search(r"(?m)^\s*schedule\s*:", text) is not None
    if has_cmd and has_dispatch and has_schedule:
        return "present"
    backup = path.with_name(path.name + ".bak-evolve")
    if not backup.exists():
        backup.write_text(text, encoding="utf-8")
    updated = text
    if not has_schedule:
        updated2, count = re.subn(r"(?m)^(on:\s*\n)", "on:\n  schedule:\n    - cron: '0 17 * * *'\n", updated, count=1)
        if count:
            updated = updated2
        else:
            updated2, count = re.subn(
                r"(?m)^on:\s*workflow_dispatch\s*$",
                "on:\n  workflow_dispatch:\n  schedule:\n    - cron: '0 17 * * *'",
                updated,
                count=1,
            )
            if count:
                updated = updated2
    if "workflow_dispatch" not in updated:
        updated2, count = re.subn(r"(?m)^(on:\s*\n)", "on:\n  workflow_dispatch:\n", updated, count=1)
        if count:
            updated = updated2
    if "rgon_auto_evolve_brain.py --ci" not in updated:
        if re.search(r"(?m)^jobs:\s*$", updated):
            updated = updated.rstrip() + "\n\n" + WORKFLOW_MARK + "\n  rgon_auto_evolve_brain:\n    runs-on: ubuntu-latest\n    permissions:\n      contents: read\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with:\n          python-version: '3.11'\n      - name: Install Pillow for image heal\n        run: python -m pip install --disable-pip-version-check pillow\n      - name: Unattended self audit and heal\n        run: python rgon_auto_evolve_brain.py --ci\n"
        else:
            return "unchanged: jobs block not found"
    if updated == text:
        return "unchanged: trigger merge unsafe"
    path.write_text(updated, encoding="utf-8", newline="\n")
    return "upgraded"


def copy_clipboard(text, ci):
    if ci or os.name != "nt":
        return "skipped"
    try:
        subprocess.run(["clip"], input=text.encode("utf-16le"), timeout=5, check=False)
        return "copied"
    except (OSError, subprocess.TimeoutExpired):
        return "failed"


def run_pipeline(root, ci):
    registered = register_top1_schedule(root)
    memory = registered["memory"]
    auditor = SelfAuditorAndHealer(root, memory)
    evolver = PromptAndRecipeEvolver(root, memory)
    recipes = evolver.evolve()
    before = auditor.scan()
    score_report(before, recipes, True)
    heal = auditor.heal(before)
    recipes = evolver.evolve()
    after = auditor.scan()
    verified = all(item.get("ok") for item in heal["checks"]) and heal["integrity_ok"]
    score_report(after, recipes, verified)
    nxt = NextEvolutionGenerator(root).build(before, after, heal, recipes)
    workflow = upgrade_external_kitchen_workflow(root)
    clipboard = copy_clipboard(nxt["text"], ci)
    memory.doc.setdefault("runs", [])
    if not isinstance(memory.doc.get("runs"), list):
        memory.doc["runs"] = []
    memory.doc["runs"].insert(0, {
        "at": now_iso(),
        "before": before.get("score"),
        "after": after.get("score"),
        "changed": heal["changed"],
        "ci": ci,
    })
    memory.doc["runs"] = memory.doc["runs"][:30]
    memory.save(registered["schedule"])
    receipt = {
        "schedule": registered,
        "before": before,
        "after": after,
        "heal": heal,
        "recipes": recipes,
        "next": nxt,
        "workflow": workflow,
        "clipboard": clipboard,
        "integrity_ok": bool(heal["integrity_ok"]),
    }
    write_json(root / "brain_basket" / "last_evolve_receipt.json", {
        "at": now_iso(),
        "priority": 1,
        "task_id": TASK_ID,
        "status": STATUS,
        "sheets": registered["sheets"],
        "before": before.get("score"),
        "after": after.get("score"),
        "changed": heal["changed"],
        "checks": heal["checks"],
        "workflow": workflow,
        "next": nxt["summary"],
        "integrity_ok": receipt["integrity_ok"],
    })
    return receipt


def print_receipt(receipt):
    schedule = receipt["schedule"]
    print("[최고 1순위 스케줄 등재 영수증]")
    print("priority: 1")
    print("task_id: " + TASK_ID)
    print("title: " + TITLE)
    print("status: " + STATUS)
    print("local: " + schedule["schedule_path"])
    print("memory: " + schedule["memory_path"])
    print("sheets: " + schedule["sheets"])
    print("workflow: " + receipt["workflow"])
    print("")
    print("[자가 진단 & 치유 점수 (100점 만점)]")
    print("health_score_before: %s/100" % receipt["before"].get("score"))
    print("health_score_after: %s/100" % receipt["after"].get("score"))
    print("copy_before_after: %s -> %s" % (receipt["before"].get("copy_hits"), receipt["after"].get("copy_hits")))
    print("dom_before_after: %s -> %s" % (receipt["before"].get("dom_hits"), receipt["after"].get("dom_hits")))
    print("image: %s" % receipt["after"].get("image_state"))
    print("healed: " + (", ".join(receipt["heal"]["changed"]) if receipt["heal"]["changed"] else "none"))
    if receipt["heal"]["checks"]:
        for item in receipt["heal"]["checks"]:
            print("verify: %s %s" % (item["path"], item["detail"]))
    else:
        print("verify: no file changed")
    alive = sum(1 for item in receipt["recipes"].get("alive", []) if item.get("alive"))
    print("recipes_alive: %s/5" % alive)
    print("")
    print("[자동 생성된 다음 진화 과제 요약]")
    for gap in receipt["next"]["summary"]:
        print("- " + gap)
    print("queue: " + receipt["next"]["queue"])
    print("clipboard: " + receipt["clipboard"])


def main():
    configure_stdio()
    ci = "--ci" in sys.argv[1:]
    root = resolve_root()
    root.mkdir(parents=True, exist_ok=True)
    with FileLock(root / "brain_basket" / ".evolve.lock"):
        receipt = run_pipeline(root, ci)
    print_receipt(receipt)
    return 0 if receipt["integrity_ok"] else 1


if __name__ == "__main__":
    try:
        _code = main()
    except EvolveBusy as exc:
        print("[evolve] " + str(exc))
        raise SystemExit(1)
    except Exception:
        print("[evolve] failed: " + sys.exc_info()[0].__name__)
        raise SystemExit(1)
    if _code == 0:
        print("RGON AUTO-EVOLVE BRAIN v1.0 TOTAL WAR READY!")
    raise SystemExit(_code)
Copy
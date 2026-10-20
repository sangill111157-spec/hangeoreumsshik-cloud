# -*- coding: utf-8 -*-
"""
rgon_auto_evolve_brain.py  —  RGON 자가 진화 두뇌 엔진 v1.0 (TOP1 TOTAL WAR)

전 에이전트 융합 원리
  ① Letta/Voyager  : AntibodyMemory        — 항체(실패·교정 규칙) 금고 + 스킬 라이브러리
  ② LangGraph Reflexion : SelfAuditorAndHealer — 전수 스캔 → 건강 점수 → 자가 치유 → 재검증 → 롤백
  ③ DSPy           : PromptAndRecipeEvolver — Grok 5대 바이럴 레시피 항체 주입·적합도 진화·manifest 동기화
  ④ AlphaEvolve    : NextEvolutionGenerator — 후보 과제 생성 → 적합도 선택 → 다음 세대 지시문 대기열 등록

사용법
  python rgon_auto_evolve_brain.py            # 로컬 전체 실행 (진단+치유+시트+워크플로우+클립보드)
  python rgon_auto_evolve_brain.py --ci       # GitHub Actions 무인 실행 (클립보드/워크플로우 수정 생략)
  python rgon_auto_evolve_brain.py --audit-only   # 진단만 (치유 안 함)
  python rgon_auto_evolve_brain.py --dry-run      # 파일 쓰기 없이 시뮬레이션
  python rgon_auto_evolve_brain.py --no-sheets    # 구글 시트 등록 생략
"""
import os
import re
import sys
import json
import shutil
import hashlib
import argparse
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BRAIN_VERSION = "1.0"
KST = timezone(timedelta(hours=9))
STAMP = datetime.now(KST).strftime("%Y%m%d_%H%M%S")


def now():
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")


# =====================================================================
# 경로
# =====================================================================
BASE = Path(__file__).resolve().parent
BRAIN = BASE / "brain_basket"
ING = BASE / "ingredients_basket"
EXT = BASE / "rgon_aside_extension"
BRIDGE_PY = BASE / "omni_bridge.py"
CHAT_HTML = BASE / "rgon_alpha_chat.html"
WORKFLOW = BASE / ".github" / "workflows" / "rgon_external_brain_kitchen.yml"

MASTER_SCHEDULE = BRAIN / "master_schedule.json"
EVOLUTION_MEMORY = (BASE / "evolution_memory.json") if (BASE / "evolution_memory.json").exists() \
    else (BRAIN / "evolution_memory.json")
ANTIBODY_VAULT = BRAIN / "antibody_vault.json"
NEXT_PROMPT_TXT = BRAIN / "next_evolution_prompt.txt"
CLIPBOARD_SHARE = BRAIN / "clipboard_share.txt"
DISPATCH_QUEUE = BASE / "omni_dispatch_queue.json"
BACKUP_ROOT = BRAIN / "backups" / f"auto_evolve_{STAMP}"

RECIPES_JSON = ING / "grok_5_viral_recipes.json"
TOKEN_CANDIDATES = [BASE / "token.pickle", BRAIN / "token.pickle", BASE.parent / "token.pickle"]

SHEET_IDS = [
    "1mIu1vXu0luRSDNyjE-WkJaz91otX0OvgaBVrJj6rwnY",
    "1gYDrCuqM2hKQbYyE3cYEZhJZEhrH_Is6tdUhsw-cgaw",
]
TAB_CONSTITUTION = "RGON_두뇌장바구니_헌법"
TAB_EVOLOG = "RGON_진화일지"
SHEET_HEADER = ["등록시각", "우선순위", "task_id", "제목", "상태", "융합 원리", "엔진/비고"]

TOP1_ID = "TOP1_SELF_EVOLVING_BRAIN"
TOP1_TITLE = "전 에이전트 합심·융합 자율 진화 두뇌(Auto-Evolve Brain) 상시 가동"
TOP1_STATUS = "ACTIVE_TOTAL_WAR"
FUSION = ["DSPy", "AlphaEvolve", "Letta/Voyager", "LangGraph Reflexion"]

R6_CROP_RATIO = 0.08          # Pollinations 하단 워터마크 크롭 비율
R2_DURATION = 10.0            # R2: 10.000초
R2_FRAMES = 300               # R2: 300프레임 (30fps)

DRY = False                   # --dry-run 시 True


# =====================================================================
# 공용 유틸
# =====================================================================
_backed_up = set()


def rel(p):
    try:
        return str(Path(p).resolve().relative_to(BASE)).replace("\\", "/")
    except Exception:
        return str(p)


def sha1_bytes(b):
    return hashlib.sha1(b).hexdigest()


def sha1_file(p):
    return sha1_bytes(Path(p).read_bytes())


def read_text(p):
    raw = Path(p).read_bytes()
    for enc in ("utf-8-sig", "utf-8", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def backup(p):
    p = Path(p)
    if DRY or not p.exists() or str(p.resolve()) in _backed_up:
        return
    dst = BACKUP_ROOT / rel(p)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dst)
    _backed_up.add(str(p.resolve()))


def write_text(p, s):
    if DRY:
        return
    p = Path(p)
    backup(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def load_json(p, default):
    p = Path(p)
    if not p.exists():
        return default
    try:
        return json.loads(read_text(p))
    except Exception as e:
        print(f"  ⚠️ JSON 파싱 실패 {rel(p)}: {e} → 기본값 사용(원본은 백업)")
        backup(p)
        return default


def save_json(p, obj):
    write_text(p, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


# =====================================================================
# ① Letta/Voyager — 면역 기억 & 항체 금고
# =====================================================================
BUILTIN_ANTIBODIES = [
    {"id": "R1", "name": "종이컵 강제",
     "rule": "도자기 머그컵·유리컵·텀블러 금지 / 흰색 일회용 종이컵만 등장",
     "scope": "recipes,prompts,images", "severity": "critical"},
    {"id": "R2", "name": "10.000초·300프레임 강제",
     "rule": "성우 내레이션 + BGM 포함, 정확히 10.000초 / 30fps / 300프레임",
     "scope": "mp4,recipes", "severity": "high"},
    {"id": "R3", "name": "최상위 모달 & 캐시 방지",
     "rule": "모달 z-index 최상위(2147483647) + Cache-Control no-store meta 강제",
     "scope": "html,extension", "severity": "high"},
    {"id": "R4", "name": "Copy 접두어 소독",
     "rule": "Genspark 'Copy'/'Copy code' 접두어·잔류 줄 자동 제거",
     "scope": "js,py,html", "severity": "critical"},
    {"id": "R5", "name": "DOM 옵셔널 체이닝 강제",
     "rule": "document.getElementById/querySelector 결과 접근 시 ?. 또는 null 가드 강제",
     "scope": "js,html", "severity": "high"},
    {"id": "R6", "name": "Pollinations 워터마크 차단",
     "rule": "Pollinations 이미지 하단 워터마크 크롭 + nologo=true + 하단 안전 구도",
     "scope": "images,recipes,urls", "severity": "high"},
]


class AntibodyMemory:
    """Letta core/archival memory + Voyager skill library"""

    def __init__(self, path):
        self.path = path
        self.data = load_json(path, {})
        if not isinstance(self.data, dict):
            self.data = {}
        self.data.setdefault("version", BRAIN_VERSION)
        self.data.setdefault("generation", 0)
        self.data.setdefault("antibodies", [])
        self.data.setdefault("skill_library", {})
        self.data.setdefault("r6_cropped_hashes", [])
        self.data.setdefault("generated_history", {})
        self.data.setdefault("core_memory", {
            "persona": "RGON 자가 진화 두뇌 — 사령관님의 TOP1 스케줄을 상시 수행",
            "mission": TOP1_TITLE,
        })
        have = {a.get("id") for a in self.data["antibodies"]}
        for i, ab in enumerate(BUILTIN_ANTIBODIES):
            if ab["id"] not in have:
                self.data["antibodies"].insert(i, dict(ab, builtin=True, signature="BUILTIN:" + ab["id"],
                                                       created_at=now(), hits=0))
        self.new_this_run = []

    @property
    def antibodies(self):
        return self.data["antibodies"]

    def get(self, aid):
        return next((a for a in self.antibodies if a.get("id") == aid), None)

    def hit(self, aid, n=1):
        a = self.get(aid)
        if a:
            a["hits"] = int(a.get("hits", 0)) + n
            a["last_hit"] = now()

    def add_antibody(self, name, rule, signature, scope="auto", severity="medium", source="SelfAuditor"):
        for a in self.antibodies:
            if a.get("signature") == signature:
                a["hits"] = int(a.get("hits", 0)) + 1
                a["last_hit"] = now()
                return None
        nums = [int(a["id"][1:]) for a in self.antibodies if re.fullmatch(r"R\d+", str(a.get("id", "")))]
        nid = f"R{max(nums + [6]) + 1}"
        self.antibodies.append({"id": nid, "name": name, "rule": rule, "scope": scope,
                                "severity": severity, "signature": signature, "source": source,
                                "builtin": False, "created_at": now(), "hits": 1})
        self.new_this_run.append(nid)
        return nid

    def record_skill(self, skill, target):
        s = self.data["skill_library"].setdefault(skill, {"uses": 0})
        s["uses"] += 1
        s["last_target"] = target
        s["last_used"] = now()

    def save(self):
        self.data["updated_at"] = now()
        save_json(self.path, self.data)


# =====================================================================
# 탐지/치유 정규식 (R3·R4·R5·R6)
# =====================================================================
_LANG_HDR = r"(?:python|py|javascript|js|html|json|yaml|yml|bash|sh|css|text|plaintext)"
RE_COPY_HEAD = re.compile(
    r"\A\ufeff?[ \t\r\n]*(?:" + _LANG_HDR + r"[ \t]*\r?\n[ \t]*)?Copy(?:[ \t]+code)?"
    r"(?:(?![A-Za-z0-9_])|(?=(?:import|from|const|let|var|function|def|class|async|chrome|document|window)\b))"
    r"[ \t]*(?:\r?\n)?"
)
RE_COPY_LINE = re.compile(r"(?m)^[ \t]*(?:Copy|Copy code|Copied!|코드 복사)[ \t]*(?:\r?\n|\Z)")

_STR = r"""(?:'[^'\\\n]*(?:\\.[^'\\\n]*)*'|"[^"\\\n]*(?:\\.[^"\\\n]*)*"|`[^`\\$\n]*`)"""
_SEL = r"(document\s*\.\s*(?:getElementById|querySelector)\(\s*" + _STR + r"\s*\))"
RE_DOM_ASSIGN = re.compile(
    _SEL + r"\.(on[a-z]+|textContent|innerHTML|innerText|value|checked|disabled|src|href|title|placeholder|className)"
           r"(\s*(?:\+=|=(?![=>])))")
RE_DOM_READ = re.compile(
    _SEL + r"\.(value|textContent|innerText|innerHTML|checked|files)\b"
           r"(?!\s*(?:\+\+|--))(?!\s*(?:[-+*/%&|^]|\*\*|<<|>>>?|&&|\|\||\?\?)?=(?!=))")
RE_DOM_CALL = re.compile(
    _SEL + r"\.(addEventListener|removeEventListener|click|focus|blur|remove|append|appendChild|prepend|"
           r"replaceChildren|setAttribute|removeAttribute|toggleAttribute|scrollIntoView|insertAdjacentHTML|"
           r"insertAdjacentElement|dispatchEvent|classList|querySelector|querySelectorAll|closest|"
           r"getBoundingClientRect)\b")

RE_POLL_URL = re.compile(r"https?://image\.pollinations\.ai/prompt/[^\s'\"`<>)]*")
RE_NOCACHE = re.compile(r"http-equiv\s*=\s*[\"']?Cache-Control", re.I)
RE_ZTOP = re.compile(r"(?:z-index\s*:\s*|zIndex\s*[=:]\s*['\"]?)(\d{7,})", re.I)

NOCACHE_META = ('\n<!-- RGON-R3-NOCACHE -->\n'
                '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">\n'
                '<meta http-equiv="Pragma" content="no-cache">\n'
                '<meta http-equiv="Expires" content="0">\n')


def count_copy(text, lang):
    n = 1 if RE_COPY_HEAD.search(text) else 0
    if lang in ("js", "py"):
        n += len(RE_COPY_LINE.findall(text))
    return n


def strip_copy(text, lang):
    n = 0
    new, k = RE_COPY_HEAD.subn("", text, count=1)
    n += k
    if lang in ("js", "py"):
        new, k = RE_COPY_LINE.subn("", new)
        n += k
    return new, n


def count_dom(text):
    return len(RE_DOM_ASSIGN.findall(text)) + len(RE_DOM_READ.findall(text)) + len(RE_DOM_CALL.findall(text))


def protect_dom(text):
    total = 0
    text, k = RE_DOM_ASSIGN.subn(lambda m: f"({m.group(1)} || {{}}).{m.group(2)}{m.group(3)}", text)
    total += k
    text, k = RE_DOM_READ.subn(lambda m: f"{m.group(1)}?.{m.group(2)}", text)
    total += k
    text, k = RE_DOM_CALL.subn(lambda m: f"{m.group(1)}?.{m.group(2)}", text)
    total += k
    return text, total


def ensure_nocache(html):
    if RE_NOCACHE.search(html):
        return html, 0
    m = re.search(r"<head\b[^>]*>", html, re.I)
    if m:
        return html[:m.end()] + NOCACHE_META + html[m.end():], 1
    m = re.search(r"<html\b[^>]*>", html, re.I)
    if m:
        return html[:m.end()] + "\n<head>" + NOCACHE_META + "</head>" + html[m.end():], 1
    return NOCACHE_META + html, 1


def count_pollinations_logo(text):
    n = 0
    for m in RE_POLL_URL.finditer(text):
        if "nologo" not in text[m.start(): m.end() + 200]:
            n += 1
    return n


def add_nologo(url):
    if "nologo" in url:
        return url
    return url + ("&" if "?" in url else "?") + "nologo=true"


# =====================================================================
# ③ DSPy — 프롬프트 진화 & Grok 5대 레시피
# =====================================================================
FIVE_STYLES = [
    ("reversal", "반전형", ["반전", "reversal", "twist"]),
    ("emotional", "감성형", ["감성", "emotional"]),
    ("comparison", "비교형", ["비교", "comparison", "vs"]),
    ("number_shock", "숫자충격형", ["숫자", "number", "shock"]),
    ("asmr", "ASMR몰입형", ["asmr"]),
]

DEFAULT_PROMPTS = {
    "reversal": "[반전형] 0~3초: 평범한 책상 위 흰색 일회용 종이컵 커피 클로즈업 → 3~7초: 컵을 돌리는 순간 "
                "예상 못한 반전(라떼아트가 메시지로 변함) → 7~10초: 리액션 엔딩 컷. 세로 9:16, 시네마틱 조명.",
    "emotional": "[감성형] 비 오는 새벽 창가, 김이 오르는 흰색 일회용 종이컵을 두 손으로 감싸는 장면, 따뜻한 역광, "
                 "슬로모션, 잔잔한 피아노 BGM과 낮은 톤 성우 내레이션. 세로 9:16.",
    "comparison": "[비교형] 화면 좌우 분할: 왼쪽 일반 인스턴트 커피 vs 오른쪽 RGON 레시피 커피, 양쪽 모두 흰색 일회용 "
                  "종이컵, 색·거품·김 비교 매크로 클로즈업, 10초 안에 결론 컷. 세로 9:16.",
    "number_shock": "[숫자충격형] 첫 1초 화면 중앙 상단에 큰 숫자 임팩트, 흰색 일회용 종이컵에 커피를 붓는 고속 매크로 샷, "
                    "BGM 비트에 맞춘 빠른 컷 전환. 세로 9:16.",
    "asmr": "[ASMR몰입형] 흰색 일회용 종이컵에 얼음과 커피가 떨어지는 소리 중심 매크로 클로즈업, 종이컵 뚜껑 닫는 소리, "
            "극사실 질감, 어두운 배경 단일 스포트라이트. 세로 9:16.",
}

R1_CLAUSE = "[R1] 컵은 반드시 흰색 일회용 종이컵(white disposable paper cup) 단 하나만 등장."
R2_CLAUSE = "[R2] 성우 내레이션 + BGM 포함, 정확히 10.000초 · 30fps · 300프레임."
R6_CLAUSE = "[R6] 화면 하단 12%는 비워 두는 안전 구도, 워터마크·로고·서명·하단 자막 없음(clean frame, no watermark)."
NEGATIVE_TOKENS = ["ceramic mug", "porcelain cup", "mug", "glass cup", "tumbler", "watermark", "logo",
                   "signature", "text overlay", "bottom caption", "pollinations"]
PROMPT_KEYS = ["prompt", "grok_prompt", "video_prompt", "image_prompt", "template"]
NEG_KEYS = ["negative_prompt", "negative", "neg_prompt"]

RE_MUG_KO = re.compile(r"(?:도자기\s*)?머그\s*컵|머그잔|도자기\s*컵|유리\s*컵|텀블러")
RE_MUG_EN = re.compile(r"(?i)\b(?:ceramic\s+|porcelain\s+|glass\s+)?(?:mugs?|tumblers?)\b")


class PromptAndRecipeEvolver:
    def __init__(self, memory):
        self.mem = memory
        self.path = RECIPES_JSON
        self.manifest_path = next((p for p in (ING / "v5_manifest.json", BASE / "v5_manifest.json",
                                               BRAIN / "v5_manifest.json") if p.exists()),
                                  ING / "v5_manifest.json")
        self.report = {}

    # ---- 로드/정규화 ----
    def _load(self):
        raw = load_json(self.path, None)
        if raw is None:
            return "dict_recipes", {"version": "v5", "recipes": []}
        if isinstance(raw, list):
            return "list", raw
        if isinstance(raw, dict):
            if isinstance(raw.get("recipes"), list):
                return "dict_recipes", raw
            vals = [v for v in raw.values() if isinstance(v, dict)]
            if vals and len(vals) == len(raw):
                return "map", raw
            raw["recipes"] = []
            return "dict_recipes", raw
        return "dict_recipes", {"version": "v5", "recipes": []}

    @staticmethod
    def _items(shape, raw):
        if shape == "list":
            return [(None, r) for r in raw if isinstance(r, dict)]
        if shape == "map":
            return [(k, v) for k, v in raw.items()]
        return [(None, r) for r in raw["recipes"] if isinstance(r, dict)]

    @staticmethod
    def _match(key, r, words):
        hay = " ".join([str(key or "")] + [str(r.get(k, "")) for k in ("style", "name", "type", "title", "id", "key")])
        hay = hay.lower()
        return any(w.lower() in hay for w in words)

    def _find(self, shape, raw, words):
        for k, r in self._items(shape, raw):
            if self._match(k, r, words):
                return r
        return None

    @staticmethod
    def _pkey(r):
        return next((k for k in PROMPT_KEYS if isinstance(r.get(k), str)), "prompt")

    @staticmethod
    def _nkey(r):
        return next((k for k in NEG_KEYS if isinstance(r.get(k), str)), "negative_prompt")

    @staticmethod
    def fitness(r):
        p = r.get(PromptAndRecipeEvolver._pkey(r), "") or ""
        n = r.get(PromptAndRecipeEvolver._nkey(r), "") or ""
        checks = [
            bool(re.search(r"\[R1\b", p)) and not RE_MUG_KO.search(p) and not RE_MUG_EN.search(p),
            bool(re.search(r"\[R2\b", p)),
            bool(re.search(r"\[R6\b", p)),
            all(t in n.lower() for t in ("ceramic mug", "watermark", "logo")),
            60 <= len(p) <= 1500,
        ]
        return sum(checks) * 20

    # ---- 진단 ----
    def inspect(self):
        gaps = []
        if not self.path.exists():
            gaps.append({"rule": "MISSING", "detail": "grok_5_viral_recipes.json 없음", "penalty": 3})
        shape, raw = self._load()
        for sid, sko, words in FIVE_STYLES:
            r = self._find(shape, raw, words)
            if r is None:
                gaps.append({"rule": "R1", "detail": f"5대 레시피 누락: {sko}", "penalty": 2})
                continue
            p = r.get(self._pkey(r), "") or ""
            if not re.search(r"\[R1\b", p) or RE_MUG_KO.search(p) or RE_MUG_EN.search(p):
                gaps.append({"rule": "R1", "detail": f"{sko}: R1 종이컵 항체 미주입/머그 잔류", "penalty": 2})
            if not re.search(r"\[R6\b", p):
                gaps.append({"rule": "R6", "detail": f"{sko}: R6 워터마크 항체 미주입", "penalty": 1})
        return gaps

    # ---- 진화 ----
    def _fix_poll(self, obj):
        n = 0
        if isinstance(obj, dict):
            for k, v in list(obj.items()):
                if isinstance(v, str) and RE_POLL_URL.fullmatch(v.strip()) and "nologo" not in v:
                    obj[k] = add_nologo(v.strip())
                    n += 1
                else:
                    n += self._fix_poll(v)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                if isinstance(v, str) and RE_POLL_URL.fullmatch(v.strip()) and "nologo" not in v:
                    obj[i] = add_nologo(v.strip())
                    n += 1
                else:
                    n += self._fix_poll(v)
        return n

    def evolve(self):
        shape, raw = self._load()
        before = json.dumps(raw, ensure_ascii=False, sort_keys=True)
        rows, created, injected = [], [], 0
        for sid, sko, words in FIVE_STYLES:
            r = self._find(shape, raw, words)
            if r is None:
                r = {"id": sid, "style": sko, "prompt": DEFAULT_PROMPTS[sid], "negative_prompt": ""}
                if shape == "list":
                    raw.append(r)
                elif shape == "map":
                    raw[sko] = r
                else:
                    raw["recipes"].append(r)
                created.append(sko)
            old_fit = self.fitness(r)
            pk, nk = self._pkey(r), self._nkey(r)
            p = r.get(pk, "") or ""
            p2 = RE_MUG_KO.sub("흰색 일회용 종이컵", p)
            p2 = RE_MUG_EN.sub("white disposable paper cup", p2)
            adds = []
            if not re.search(r"\[R1\b", p2):
                adds.append(R1_CLAUSE)
            if not re.search(r"\[R2\b", p2):
                adds.append(R2_CLAUSE)
            if not re.search(r"\[R6\b", p2):
                adds.append(R6_CLAUSE)
            if adds:
                p2 = p2.rstrip() + "\n" + "\n".join(adds)
            if p2 != p:
                injected += 1
                r[pk] = p2
            neg = r.get(nk, "") or ""
            have = [t.strip().lower() for t in neg.split(",") if t.strip()]
            miss = [t for t in NEGATIVE_TOKENS if t not in have]
            if miss:
                r[nk] = ", ".join([t for t in [neg.strip().strip(",")] if t] + miss)
            r.setdefault("id", sid)
            r.setdefault("style", sko)
            r["duration_sec"] = R2_DURATION
            r["fps"] = 30
            r["frames"] = R2_FRAMES
            r["status"] = "LIVE"
            r["antibodies"] = sorted(set((r.get("antibodies") or []) + ["R1", "R2", "R6"]))
            new_fit = self.fitness(r)
            ev = r.get("evolution") if isinstance(r.get("evolution"), dict) else {}
            if new_fit != ev.get("fitness") or p2 != p:
                ev = {"generation": int(ev.get("generation", 0)) + 1, "fitness": new_fit,
                      "prev_fitness": old_fit, "updated_at": now(), "optimizer": "RGON-DSPy-lite"}
                r["evolution"] = ev
            rows.append({"id": r.get("id"), "style": sko, "status": "LIVE", "fitness": new_fit,
                         "generation": ev.get("generation", 1),
                         "prompt_sha1": sha1_bytes((r.get(pk) or "").encode("utf-8"))[:12]})
        poll_fixed = self._fix_poll(raw)
        if isinstance(raw, dict) and shape != "map":
            raw["updated_at"] = now()
            raw["antibody_guard"] = ["R1", "R2", "R6"]
        changed = json.dumps(raw, ensure_ascii=False, sort_keys=True) != before
        if changed or not self.path.exists():
            save_json(self.path, raw)

        # v5_manifest 동기화
        man = load_json(self.manifest_path, {})
        if not isinstance(man, dict):
            man = {"legacy": man}
        man["grok_5_viral_recipes"] = {
            "source": rel(self.path), "count": len(rows), "all_live": len(rows) == 5,
            "styles": [x["style"] for x in rows], "recipes": rows,
            "antibodies_enforced": ["R1", "R2", "R6"], "synced_at": now(),
            "synced_by": f"rgon_auto_evolve_brain v{BRAIN_VERSION}",
        }
        man["recipes_live"] = len(rows)
        save_json(self.manifest_path, man)
        if injected or created:
            self.mem.hit("R1", injected)
            self.mem.record_skill("DSPy_RECIPE_INJECT", rel(self.path))
        self.report = {"created": created, "injected": injected, "pollinations_fixed": poll_fixed,
                       "rows": rows, "manifest": rel(self.manifest_path), "changed": changed}
        return self.report


# =====================================================================
# ② LangGraph Reflexion — 자가 진단 & 자가 치유
# =====================================================================
CAPS = {"R1": 10, "R2": 15, "R3": 10, "R4": 20, "R5": 15, "R6": 15, "SYNTAX": 20, "MISSING": 10}


def fnd(rule, path, detail, penalty, healable=False, kind="info", lang=None):
    return {"rule": rule, "file": str(path), "rel": rel(path), "detail": detail,
            "penalty": penalty, "healable": healable, "kind": kind, "lang": lang}


def health_score(findings):
    per = {}
    for f in findings:
        per[f["rule"]] = per.get(f["rule"], 0) + f["penalty"]
    capped = {k: min(v, CAPS.get(k, 10)) for k, v in per.items()}
    return max(0, 100 - sum(capped.values())), capped


class SelfAuditorAndHealer:
    def __init__(self, memory, evolver):
        self.mem = memory
        self.evolver = evolver
        self.node = shutil.which("node")
        self.ffprobe = shutil.which("ffprobe")
        try:
            import PIL  # noqa: F401
            self.pil = True
        except ImportError:
            self.pil = False
        self.heal_log = []
        self.media_report = []

    # ---- 대상 ----
    def code_targets(self):
        out = []
        if EXT.exists():
            for p in sorted(EXT.rglob("*.js")):
                if "node_modules" in p.parts or "backups" in p.parts:
                    continue
                out.append((p, "js"))
        if BRIDGE_PY.exists():
            out.append((BRIDGE_PY, "py"))
        if CHAT_HTML.exists():
            out.append((CHAT_HTML, "html"))
        return out

    def watermark_images(self):
        seen, out = set(), []
        cands = [BASE / "sample_paper_cup.jpg", ING / "sample_paper_cup.jpg"]
        if ING.exists():
            cands += [p for p in ING.rglob("*") if p.is_file()
                      and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
                      and ("pollinations" in p.name.lower() or p.name.lower() == "sample_paper_cup.jpg")
                      and "backups" not in p.parts]
        for p in cands:
            if p.exists():
                k = str(p.resolve())
                if k not in seen:
                    seen.add(k)
                    out.append(p)
        return out

    # ---- 구문 검증 ----
    def _node_check_code(self, code, name="snippet.js"):
        if not self.node:
            return True, "node 없음(검증 생략)"
        is_mod = bool(re.search(r"(?m)^\s*(?:import\s+[\w{*'\"]|export\s+)", code))
        d = tempfile.mkdtemp(prefix="rgon_chk_")
        try:
            f = Path(d) / (Path(name).stem + (".mjs" if is_mod else ".js"))
            f.write_text(code, encoding="utf-8")
            r = subprocess.run([self.node, "--check", str(f)], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=60)
            return r.returncode == 0, (r.stderr or r.stdout).strip().splitlines()[-1:] and \
                (r.stderr or r.stdout).strip().splitlines()[0] or ""
        except Exception as e:
            return True, f"node 실행 실패: {e}"
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def syntax_failures(self, p, text, lang):
        if lang == "js":
            ok, msg = self._node_check_code(text, Path(p).name)
            return (0, "") if ok else (1, msg)
        if lang == "py":
            try:
                compile(text, str(p), "exec")
                return 0, ""
            except SyntaxError as e:
                return 1, f"line {e.lineno}: {e.msg}"
        if lang == "html":
            fails, msgs = 0, []
            for i, m in enumerate(re.finditer(r"<script\b([^>]*)>(.*?)</script\s*>", text, re.S | re.I)):
                attrs, code = m.group(1), m.group(2)
                if re.search(r"\bsrc\s*=", attrs, re.I):
                    continue
                t = re.search(r"\btype\s*=\s*[\"']?([^\"'\s>]+)", attrs, re.I)
                if t and t.group(1).lower() not in ("text/javascript", "module", "application/javascript"):
                    continue
                if not code.strip():
                    continue
                ok, msg = self._node_check_code(code, f"inline_{i}.js")
                if not ok:
                    fails += 1
                    msgs.append(f"script#{i}: {msg}")
            return fails, " | ".join(msgs)
        return 0, ""

    # ---- 미디어 (R2) ----
    def _probe(self, p):
        r = subprocess.run([self.ffprobe, "-v", "error", "-show_entries",
                            "format=duration:stream=codec_type,nb_frames,r_frame_rate",
                            "-of", "json", str(p)], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=90)
        j = json.loads(r.stdout or "{}")
        dur = float((j.get("format") or {}).get("duration") or 0)
        streams = j.get("streams") or []
        vs = [s for s in streams if s.get("codec_type") == "video"]
        au = [s for s in streams if s.get("codec_type") == "audio"]
        frames = None
        if vs:
            nb = str(vs[0].get("nb_frames", ""))
            if nb.isdigit():
                frames = int(nb)
            else:
                try:
                    num, den = vs[0].get("r_frame_rate", "0/1").split("/")
                    frames = int(round(float(num) / float(den) * dur))
                except Exception:
                    frames = None
        return dur, frames, len(au) > 0

    def audit_media(self):
        F, self.media_report = [], []
        mp4s = [p for p in sorted(ING.rglob("*.mp4")) if "backups" not in p.parts] if ING.exists() else []
        if not mp4s:
            F.append(fnd("R2", ING, "ingredients_basket에 MP4 없음", 5))
            return F
        for p in mp4s[:30]:
            if p.stat().st_size == 0:
                F.append(fnd("R2", p, "0바이트 MP4", 5))
                self.media_report.append({"file": rel(p), "ok": False, "reason": "0 bytes"})
                continue
            if not self.ffprobe:
                self.media_report.append({"file": rel(p), "ok": None, "reason": "ffprobe 없음"})
                continue
            try:
                dur, frames, has_audio = self._probe(p)
            except Exception as e:
                F.append(fnd("R2", p, f"ffprobe 실패: {e}", 3))
                continue
            ok_dur = abs(dur - R2_DURATION) <= 0.05
            ok_fr = frames is None or frames == R2_FRAMES
            if not (ok_dur and ok_fr):
                F.append(fnd("R2", p, f"길이 {dur:.3f}s / {frames}프레임 (기준 10.000s/300f)", 5))
            if not has_audio:
                F.append(fnd("R2", p, "오디오 트랙 없음(성우+BGM 누락)", 3))
            self.media_report.append({"file": rel(p), "duration": round(dur, 3), "frames": frames,
                                      "audio": has_audio, "ok": ok_dur and ok_fr and has_audio})
        return F

    # ---- 전수 진단 ----
    def audit(self, phase="pre"):
        F = []
        for p in (EXT / "background.js", EXT / "content_aside_bar.js", BRIDGE_PY, CHAT_HTML):
            if not p.exists():
                F.append(fnd("MISSING", p, "필수 파일 없음", 3))
        ztext = ""
        for p, lang in self.code_targets():
            text = read_text(p)
            c = count_copy(text, lang)
            if c:
                F.append(fnd("R4", p, f"Genspark Copy 잔류 {c}곳", min(5 * c, 10), True, "code", lang))
            if lang in ("js", "html"):
                d = count_dom(text)
                if d:
                    F.append(fnd("R5", p, f"미보호 DOM 접근 {d}곳 (?. 미적용)", d, True, "code", lang))
                pc = count_pollinations_logo(text)
                if pc:
                    F.append(fnd("R6", p, f"Pollinations URL nologo 누락 {pc}곳 (수동 확인)", 2 * pc))
                ztext += text
            if lang == "html" and not RE_NOCACHE.search(text):
                F.append(fnd("R3", p, "캐시 방지 meta(no-store) 없음", 5, True, "code", lang))
            fails, msg = self.syntax_failures(p, text, lang)
            if fails:
                F.append(fnd("SYNTAX", p, f"구문 검증 실패 {fails}건: {msg[:140]}", 10 * fails))
                self.mem.add_antibody("구문 오류 파일 배포 차단",
                                      f"{rel(p)} 구문 오류 감지 — 수정 전 배포/발사 금지 ({msg[:80]})",
                                      f"SYNTAX::{rel(p)}", scope=lang, severity="critical")
        if ztext:
            zs = [int(z) for z in RE_ZTOP.findall(ztext)]
            if not zs or max(zs) < 2147483000:
                F.append(fnd("R3", EXT / "content_aside_bar.js", "최상위 모달 z-index(2147483647) 미확인", 3))
        F += self.audit_media()
        crop_reg = set(self.mem.data["r6_cropped_hashes"])
        for p in self.watermark_images():
            if sha1_file(p) not in crop_reg:
                F.append(fnd("R6", p, "하단 워터마크 영역 노출(미크롭)", 10, self.pil, "image"))
        for g in self.evolver.inspect():
            F.append(fnd(g["rule"], self.evolver.path, g["detail"], g["penalty"], True, "recipe"))
        return F

    # ---- 치유 ----
    def heal_code_file(self, p, lang):
        text = read_text(p)
        new, acts = text, []
        new, n = strip_copy(new, lang)
        if n:
            acts.append(("R4", f"Copy 소독 {n}곳"))
        if lang in ("js", "html"):
            new, n = protect_dom(new)
            if n:
                acts.append(("R5", f"?./null 가드 {n}곳"))
        if lang == "html":
            new, n = ensure_nocache(new)
            if n:
                acts.append(("R3", "no-store meta 삽입"))
        if new == text:
            return
        before, _ = self.syntax_failures(p, text, lang)
        after, msg = self.syntax_failures(p, new, lang)
        if after > before:
            nid = self.mem.add_antibody("자가 치유 롤백 감시",
                                        f"{rel(p)} 자동 치유 후 구문 실패 → 원본 유지, 수동 교정 필요 ({msg[:80]})",
                                        f"HEAL_ROLLBACK::{rel(p)}", scope=lang, severity="high")
            self.heal_log.append({"file": rel(p), "result": "ROLLBACK", "detail": msg[:140], "antibody": nid})
            return
        write_text(p, new)
        verify = "검증 생략"
        if lang == "js":
            if self.node and not DRY:
                r = subprocess.run([self.node, "--check", str(p)], capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=60)
                verify = "node --check ✅" if r.returncode == 0 else "node --check ❌ " + r.stderr.strip()[:100]
            elif self.node:
                verify = "node --check ✅(메모리)"
        elif lang == "py":
            verify = "compile ✅"
        elif lang == "html":
            verify = "inline script node --check ✅" if self.node else "node 없음"
        for rule, _ in acts:
            self.mem.hit(rule)
            self.mem.record_skill({"R4": "R4_COPY_STRIP", "R5": "R5_OPTIONAL_CHAIN",
                                   "R3": "R3_NOCACHE_META"}[rule], rel(p))
        self.heal_log.append({"file": rel(p), "result": "HEALED",
                              "detail": ", ".join(a for _, a in acts), "verify": verify})

    def crop_watermark(self, p):
        if not self.pil:
            self.heal_log.append({"file": rel(p), "result": "SKIP", "detail": "Pillow 미설치 (pip install pillow)"})
            return
        from PIL import Image
        try:
            with Image.open(p) as im:
                im.load()
                w, h = im.size
                cut = max(1, int(round(h * R6_CROP_RATIO)))
                if h - cut < 64:
                    self.heal_log.append({"file": rel(p), "result": "SKIP", "detail": f"이미지 너무 작음 {w}x{h}"})
                    return
                out = im.crop((0, 0, w, h - cut))
                fmt = im.format or ("JPEG" if p.suffix.lower() in (".jpg", ".jpeg") else None)
            if fmt == "JPEG" and out.mode not in ("RGB", "L"):
                out = out.convert("RGB")
            old_hash = sha1_file(p)
            if not DRY:
                backup(p)
                kw = {"quality": 95} if fmt == "JPEG" else {}
                out.save(p, format=fmt, **kw)
                new_hash = sha1_file(p)
            else:
                new_hash = old_hash
            reg = self.mem.data["r6_cropped_hashes"]
            for hsh in (old_hash, new_hash):
                if hsh not in reg:
                    reg.append(hsh)
            self.mem.data["r6_cropped_hashes"] = reg[-500:]
            self.mem.hit("R6")
            self.mem.record_skill("R6_WATERMARK_CROP", rel(p))
            self.heal_log.append({"file": rel(p), "result": "HEALED",
                                  "detail": f"하단 {cut}px({int(R6_CROP_RATIO * 100)}%) 크롭 {w}x{h}→{w}x{h - cut}"})
        except Exception as e:
            self.heal_log.append({"file": rel(p), "result": "FAIL", "detail": str(e)[:140]})

    def heal(self, findings):
        files = {}
        for f in findings:
            if f["healable"] and f["kind"] == "code":
                files.setdefault(f["file"], f["lang"])
        for p, lang in files.items():
            self.heal_code_file(Path(p), lang)
        for f in findings:
            if f["healable"] and f["kind"] == "image":
                self.crop_watermark(Path(f["file"]))


# =====================================================================
# ④ AlphaEvolve — 다음 진화 과제 생성기
# =====================================================================
RULE_TASKS = {
    "R1": ("레시피 종이컵 항체 완전 고정", "5대 레시피 프롬프트에서 머그/유리컵 표현을 원천 차단하고 negative_prompt 고정", 5, 1),
    "R2": ("MP4 10.000초·300프레임 자동 교정 렌더러", "ffmpeg로 fps=30, tpad/apad, -frames:v 300 강제 + 성우·BGM 믹싱 검증 모듈", 5, 3),
    "R3": ("모달 최상위 Z-index·캐시 방지 고정", "content_aside_bar 모달 z-index 2147483647 + Shadow DOM 격리 + no-store", 4, 2),
    "R4": ("Copy 접두어 유입 경로 차단", "흡수기/붙여넣기 단계에서 cleanCopy 선적용 및 저장 직전 재소독", 4, 1),
    "R5": ("DOM 바인딩 안전 계층(safeBind) 도입", "모든 getElementById/querySelector 바인딩을 safeBind 헬퍼로 일원화", 4, 2),
    "R6": ("Pollinations 워터마크 전 경로 차단", "모든 이미지 URL에 nologo=true 주입 + 저장 시 하단 자동 크롭 훅", 4, 2),
    "SYNTAX": ("구문 오류 파일 즉시 복구", "node --check / compile 실패 파일을 백업 대조 후 정상 코드로 재작성", 5, 2),
    "MISSING": ("누락 핵심 파일 복원", "필수 파일(확장·브리지·독대실·레시피) 재생성 및 무결성 검증", 5, 2),
}
FRONTIER_TASKS = [
    ("reflexion_loop", "LangGraph Reflexion 루프: 발사→흡수→비평→재발사 자동화",
     "omni_bridge.py에 /reflect 엔드포인트를 추가해 흡수한 응답을 항체 규칙으로 채점하고, 미달이면 교정 지시를 붙여 자동 재발사", 5, 3),
    ("absorb_antibody_learning", "흡수함 응답 자동 채점 → 항체 자동 학습",
     "흡수 카드마다 R1~Rn 위반 여부를 자동 판정하고 새 실패 패턴을 add_antibody로 금고에 축적", 4, 2),
    ("recipe_ab_feedback", "5대 레시피 A/B 성과 피드백 진화",
     "조회수·완주율 입력을 받아 레시피별 적합도를 갱신하고 상위 변이만 다음 세대로 선택(DSPy optimizer + AlphaEvolve)", 4, 3),
    ("dashboard", "자가 진화 두뇌 대시보드",
     "rgon_alpha_chat.html에 건강 점수 추이·항체 목록·다음 과제 원클릭 발사 패널 추가", 3, 2),
    ("r2_render_guard", "R2 렌더 가드",
     "MP4 생성 직후 ffprobe로 10.000초/300프레임/오디오 트랙을 검사하고 불합격 시 자동 재렌더", 4, 2),
]


class NextEvolutionGenerator:
    def __init__(self, memory, ci=False, no_clipboard=False):
        self.mem = memory
        self.ci = ci
        self.no_clipboard = no_clipboard

    def _candidates(self, residual):
        hist = self.mem.data["generated_history"]
        by_rule = {}
        for f in residual:
            by_rule.setdefault(f["rule"], []).append(f)
        cands = []
        for rule, items in by_rule.items():
            title, detail, impact, effort = RULE_TASKS.get(rule, (f"{rule} 이슈 해결", "잔존 이슈 교정", 3, 2))
            urgency = min(10, sum(i["penalty"] for i in items))
            files = sorted({i["rel"] for i in items})[:4]
            cands.append({"key": f"fix_{rule}", "title": title, "rule": rule,
                          "detail": detail + " | 대상: " + ", ".join(files),
                          "evidence": [i["detail"] for i in items][:3],
                          "impact": impact, "effort": effort, "urgency": urgency})
        for key, title, detail, impact, effort in FRONTIER_TASKS:
            cands.append({"key": key, "title": title, "rule": "FRONTIER", "detail": detail,
                          "evidence": [], "impact": impact, "effort": effort, "urgency": 0})
        for c in cands:
            novelty = max(0, 3 - int(hist.get(c["key"], 0)))
            c["fitness"] = c["impact"] * 3 + c["urgency"] * 2 - c["effort"] + novelty
        return sorted(cands, key=lambda c: -c["fitness"])

    def generate(self, residual, score_pre, score_post, heal_log):
        gen = int(self.mem.data.get("generation", 0)) + 1
        self.mem.data["generation"] = gen
        top = self._candidates(residual)[:3]
        for c in top:
            self.mem.data["generated_history"][c["key"]] = int(self.mem.data["generated_history"].get(c["key"], 0)) + 1

        ab_lines = "\n".join(f"  - {a['id']}: {a['rule']}" for a in self.mem.antibodies)
        res_lines = "\n".join(f"  - [{f['rule']}] {f['rel']}: {f['detail']}" for f in residual[:12]) or "  - (없음)"
        heal_lines = "\n".join(f"  - {h['file']}: {h['result']} {h.get('detail', '')}" for h in heal_log[:10]) or "  - (치유 없음)"
        task_lines = []
        for i, c in enumerate(top, 1):
            ev = ("\n     근거: " + " / ".join(c["evidence"])) if c["evidence"] else ""
            task_lines.append(f"  {i}. {c['title']}  (적합도 {c['fitness']})\n     → {c['detail']}{ev}")
        text = (
            "웹 검색이나 외부 도구는 절대 호출하지 말고 즉시 Python 코드만 작성하라.\n"
            f"[RGON 자가 진화 두뇌 v{BRAIN_VERSION} — 제 {gen}세대 자동 진화 지시문]\n"
            f"생성 시각: {now()}\n"
            f"최고 1순위 스케줄: {TOP1_ID} ({TOP1_STATUS})\n"
            f"현재 건강 점수: {score_pre} → {score_post} / 100\n\n"
            f"[활성 항체 — 반드시 준수]\n{ab_lines}\n\n"
            f"[이번 실행 자가 치유 기록]\n{heal_lines}\n\n"
            f"[잔존 이슈]\n{res_lines}\n\n"
            "[이번 세대 진화 과제 — AlphaEvolve 적합도 상위 3]\n" + "\n".join(task_lines) + "\n\n"
            "[출력 요구사항]\n"
            f"  - `{BASE}` 기준 대상 파일 전체 코드를 단일 ```python 코드 블록으로 출력할 것\n"
            "  - 기존 기능 100% 유지, 모든 항체 규칙 위반 금지, 수정 파일은 실행 전 backups/에 자동 백업\n"
            f"  - 마지막 줄에 `RGON EVOLUTION GEN-{gen} COMPLETE!` 를 출력할 것\n"
        )
        write_text(NEXT_PROMPT_TXT, text)
        write_text(CLIPBOARD_SHARE, text)

        q = load_json(DISPATCH_QUEUE, {"version": BRAIN_VERSION, "queue": []})
        lst = q if isinstance(q, list) else q.setdefault("queue", [])
        for item in lst:
            if isinstance(item, dict) and item.get("source") == "rgon_auto_evolve_brain" \
                    and item.get("status") == "PENDING":
                item["status"] = "SUPERSEDED"
        lst.append({"id": f"evo_gen{gen}_{STAMP}", "type": "dispatch", "targets": ["claude", "gpt"],
                    "text": text, "status": "PENDING", "source": "rgon_auto_evolve_brain",
                    "generation": gen, "created_at": now(),
                    "tasks": [c["title"] for c in top]})
        if len(lst) > 50:
            del lst[:len(lst) - 50]
        if isinstance(q, dict):
            q["updated_at"] = now()
        save_json(DISPATCH_QUEUE, q)

        clip = "생략(CI/옵션)"
        if not self.ci and not self.no_clipboard and not DRY:
            clip = self._to_clipboard(text)
        return {"generation": gen, "tasks": top, "prompt_path": rel(NEXT_PROMPT_TXT),
                "queue_path": rel(DISPATCH_QUEUE), "clipboard": clip, "chars": len(text)}

    @staticmethod
    def _to_clipboard(text):
        try:
            if os.name == "nt":
                subprocess.run(["clip"], input=text.encode("utf-16"), check=True, timeout=10)
                return "✅ 클립보드 복사 완료"
            for cmd in (["pbcopy"], ["xclip", "-selection", "clipboard"], ["wl-copy"]):
                if shutil.which(cmd[0]):
                    subprocess.run(cmd, input=text.encode("utf-8"), check=True, timeout=10)
                    return "✅ 클립보드 복사 완료"
            return "⚠️ 클립보드 도구 없음(clipboard_share.txt 사용)"
        except Exception as e:
            return f"⚠️ 클립보드 실패: {e}"


# =====================================================================
# 구글 시트 연동
# =====================================================================
class SheetsLink:
    def __init__(self):
        self.svc = None
        self.err = None
        self.token = None

    def connect(self):
        tok = next((p for p in TOKEN_CANDIDATES if p.exists()), None)
        if not tok:
            self.err = "token.pickle 없음 → 시트 등록 건너뜀"
            return False
        try:
            import pickle
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request
        except ImportError as e:
            self.err = f"구글 API 라이브러리 없음({getattr(e, 'name', e)}) → pip install google-api-python-client google-auth"
            return False
        try:
            with open(tok, "rb") as f:
                creds = pickle.load(f)
            if not creds.valid:
                if getattr(creds, "expired", False) and getattr(creds, "refresh_token", None):
                    creds.refresh(Request())
                    if not DRY:
                        with open(tok, "wb") as f:
                            pickle.dump(creds, f)
                else:
                    self.err = "토큰 무효(재인증 필요)"
                    return False
            self.svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
            self.token = tok
            return True
        except Exception as e:
            self.err = f"시트 연결 실패: {str(e)[:120]}"
            return False

    def _ensure_tab(self, sid, tab):
        meta = self.svc.spreadsheets().get(spreadsheetId=sid, fields="sheets.properties(sheetId,title)").execute()
        m = {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta.get("sheets", [])}
        if tab in m:
            return m[tab]
        r = self.svc.spreadsheets().batchUpdate(
            spreadsheetId=sid, body={"requests": [{"addSheet": {"properties": {"title": tab}}}]}).execute()
        return r["replies"][0]["addSheet"]["properties"]["sheetId"]

    def register_top(self, sid, tab, row):
        gid = self._ensure_tab(sid, tab)
        vals = self.svc.spreadsheets().values().get(spreadsheetId=sid, range=f"'{tab}'!A1:H").execute().get("values", [])
        for r in vals:
            if TOP1_ID in r and len(r) > 1 and str(r[1]).strip() == "1":
                return "이미 등재(중복 방지)"
        if not vals:
            self.svc.spreadsheets().values().update(
                spreadsheetId=sid, range=f"'{tab}'!A1", valueInputOption="RAW",
                body={"values": [SHEET_HEADER, row]}).execute()
            return "신규 헤더 + 2행 등재"
        self.svc.spreadsheets().batchUpdate(spreadsheetId=sid, body={"requests": [{"insertDimension": {
            "range": {"sheetId": gid, "dimension": "ROWS", "startIndex": 1, "endIndex": 2},
            "inheritFromBefore": False}}]}).execute()
        self.svc.spreadsheets().values().update(
            spreadsheetId=sid, range=f"'{tab}'!A2", valueInputOption="RAW", body={"values": [row]}).execute()
        return "2행(최상단) 삽입 등재"

    def append(self, sid, tab, row):
        self._ensure_tab(sid, tab)
        vals = self.svc.spreadsheets().values().get(spreadsheetId=sid, range=f"'{tab}'!A1:A1").execute().get("values", [])
        body = {"values": ([SHEET_HEADER] if not vals else []) + [row]}
        self.svc.spreadsheets().values().append(
            spreadsheetId=sid, range=f"'{tab}'!A1", valueInputOption="RAW",
            insertDataOption="INSERT_ROWS", body=body).execute()
        return "append"


# =====================================================================
# 최고 1순위 스케줄 등재
# =====================================================================
def _top1_entry(old=None):
    e = {
        "priority": 1,
        "task_id": TOP1_ID,
        "title": TOP1_TITLE,
        "status": TOP1_STATUS,
        "fusion": FUSION,
        "engine": f"rgon_auto_evolve_brain.py v{BRAIN_VERSION}",
        "cadence": "상시 가동 + 매일 03:00 KST 외부 주방(GitHub Actions --ci) 무인 진화",
        "owner": "사령관님",
        "first_registered_at": (old or {}).get("first_registered_at") or (old or {}).get("registered_at") or now(),
        "registered_at": now(),
    }
    return e


def _find_old(obj):
    if isinstance(obj, list):
        return next((x for x in obj if isinstance(x, dict) and x.get("task_id") == TOP1_ID), None)
    if isinstance(obj, dict):
        if isinstance(obj.get("TOP_PRIORITY_1"), dict):
            return obj["TOP_PRIORITY_1"]
        for k in ("schedules", "schedule", "tasks", "items", "entries"):
            if isinstance(obj.get(k), list):
                r = _find_old(obj[k])
                if r:
                    return r
    return None


def _upsert_top1(obj, list_key_default=None):
    entry = _top1_entry(_find_old(obj))
    if isinstance(obj, list):
        obj = [x for x in obj if not (isinstance(x, dict) and x.get("task_id") == TOP1_ID)]
        obj.insert(0, entry)
        return obj, "list[0]"
    if not isinstance(obj, dict):
        obj = {}
    if not obj and list_key_default:
        obj[list_key_default] = []
    where = ["TOP_PRIORITY_1"]
    for k in ("schedules", "schedule", "tasks", "items", "entries"):
        if isinstance(obj.get(k), list):
            obj[k] = [x for x in obj[k] if not (isinstance(x, dict) and x.get("task_id") == TOP1_ID)]
            obj[k].insert(0, entry)
            where.append(f"{k}[0]")
            break
    new = {"TOP_PRIORITY_1": entry}
    for k, v in obj.items():
        if k != "TOP_PRIORITY_1":
            new[k] = v
    return new, " + ".join(where)


def register_top1_schedule(sheets, use_sheets=True):
    BRAIN.mkdir(parents=True, exist_ok=True)
    receipt = {"task_id": TOP1_ID, "title": TOP1_TITLE, "priority": 1, "status": TOP1_STATUS,
               "files": [], "sheets": []}
    for path, lk in ((MASTER_SCHEDULE, "schedules"), (EVOLUTION_MEMORY, None)):
        obj, where = _upsert_top1(load_json(path, {}), lk)
        save_json(path, obj)
        receipt["files"].append(f"{rel(path)} → {where}")
    if not use_sheets or DRY:
        receipt["sheets"].append("시트 등록 생략(옵션/dry-run)")
        return receipt
    if not sheets.connect():
        receipt["sheets"].append(sheets.err)
        return receipt
    row = [now(), 1, TOP1_ID, TOP1_TITLE, TOP1_STATUS, " + ".join(FUSION),
           f"rgon_auto_evolve_brain.py v{BRAIN_VERSION}"]
    for sid in SHEET_IDS:
        for tab in (TAB_CONSTITUTION, TAB_EVOLOG):
            try:
                res = sheets.register_top(sid, tab, row)
            except Exception as e:
                res = f"실패: {str(e)[:100]}"
            receipt["sheets"].append(f"{sid[:10]}… / {tab}: {res}")
    return receipt


def log_run(sheets, run):
    obj = load_json(EVOLUTION_MEMORY, {})
    if isinstance(obj, dict):
        runs = obj.setdefault("auto_evolve_runs", [])
        runs.append(run)
        obj["auto_evolve_runs"] = runs[-100:]
        obj["last_health_score"] = run["health_after"]
    elif isinstance(obj, list):
        obj.append(dict(run, type="AUTO_EVOLVE_RUN"))
    save_json(EVOLUTION_MEMORY, obj)
    out = []
    if sheets.svc and not DRY:
        row = [now(), "RUN", TOP1_ID, f"건강 {run['health_before']}→{run['health_after']}",
               f"치유 {run['heals']}건 / 신규 항체 {','.join(run['new_antibodies']) or '-'}",
               " | ".join(run["next_tasks"])[:300], f"GEN-{run['generation']}{' (CI)' if run['ci'] else ''}"]
        for sid in SHEET_IDS:
            try:
                sheets.append(sid, TAB_EVOLOG, row)
                out.append(f"{sid[:10]}… / {TAB_EVOLOG}: 실행 일지 append")
            except Exception as e:
                out.append(f"{sid[:10]}… / {TAB_EVOLOG}: 실패 {str(e)[:80]}")
    return out


# =====================================================================
# 외부 주방 워크플로우 업그레이드
# =====================================================================
WF_START = "# >>> RGON-AUTO-EVOLVE-BRAIN v1.0 >>>"
WF_END = "# <<< RGON-AUTO-EVOLVE-BRAIN <<<"
JOB_LINES = r'''# >>> RGON-AUTO-EVOLVE-BRAIN v1.0 >>>
rgon_auto_evolve_brain:
  name: "🧠 RGON Auto-Evolve Brain (TOP1 무인 자가 진단·치유)"
  runs-on: ubuntu-latest
  timeout-minutes: 30
  permissions:
    contents: write
  steps:
    - name: Checkout
      uses: actions/checkout@v4
    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"
    - name: Setup Node (node --check)
      uses: actions/setup-node@v4
      with:
        node-version: "20"
    - name: Install deps
      run: |
        sudo apt-get update -y >/dev/null 2>&1 || true
        sudo apt-get install -y ffmpeg >/dev/null 2>&1 || true
        python -m pip install --upgrade pip
        pip install pillow google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 || true
    - name: Restore Google token (optional secret RGON_TOKEN_PICKLE_B64)
      env:
        RGON_TOKEN_PICKLE_B64: ${{ secrets.RGON_TOKEN_PICKLE_B64 }}
      run: |
        if [ -n "$RGON_TOKEN_PICKLE_B64" ]; then echo "$RGON_TOKEN_PICKLE_B64" | base64 -d > token.pickle; fi
    - name: Run Auto-Evolve Brain (CI)
      run: python rgon_auto_evolve_brain.py --ci
    - name: Commit self-heal results
      run: |
        rm -f token.pickle
        git config user.name "rgon-brain-bot"
        git config user.email "rgon-brain-bot@users.noreply.github.com"
        for p in brain_basket ingredients_basket rgon_aside_extension omni_bridge.py rgon_alpha_chat.html omni_dispatch_queue.json evolution_memory.json; do
          if [ -e "$p" ]; then git add -A -- "$p"; fi
        done
        git reset -q -- brain_basket/backups 2>/dev/null || true
        if git diff --cached --quiet; then echo "변경 없음"; exit 0; fi
        git commit -m "🧠 RGON Auto-Evolve Brain: nightly self-diagnosis & self-heal"
        git pull --rebase --autostash || true
        git push || echo "push 실패 — 다음 실행 시 재시도"
# <<< RGON-AUTO-EVOLVE-BRAIN <<<'''

WF_ON_BLOCK = ('on:\n'
               '  schedule:\n'
               '    - cron: "0 18 * * *"   # 매일 03:00 KST\n'
               '  workflow_dispatch:\n')


def _job_block(ind):
    return "\n".join((ind + ln) if ln else ln for ln in JOB_LINES.splitlines()) + "\n"


def _ensure_triggers(text):
    notes = []
    m = re.search(r"(?m)^([\"']?on[\"']?)\s*:\s*(.*)$", text)
    if not m:
        return WF_ON_BLOCK + "\n" + text, ["on: 블록 신규 추가"]
    inline = m.group(2).split("#")[0].strip()
    if inline:
        evs = [e.strip() for e in inline.strip("[]").split(",") if e.strip()]
        block = "on:\n" + "".join(f"  {e}:\n" for e in evs if e not in ("schedule", "workflow_dispatch"))
        block += '  schedule:\n    - cron: "0 18 * * *"   # 매일 03:00 KST\n  workflow_dispatch:'
        text = text[:m.start()] + block + text[m.end():]
        return text, [f"on: {inline} → 블록형 변환 + schedule/workflow_dispatch 추가"]
    add = ""
    if not re.search(r"(?m)^\s+schedule\s*:", text):
        add += '  schedule:\n    - cron: "0 18 * * *"   # 매일 03:00 KST\n'
        notes.append("schedule cron 추가")
    if not re.search(r"(?m)^\s+workflow_dispatch\s*:", text):
        add += "  workflow_dispatch:\n"
        notes.append("workflow_dispatch 추가")
    if add:
        text = text[:m.end()] + "\n" + add.rstrip("\n") + text[m.end():]
    return text, notes


def upgrade_workflow():
    if not WORKFLOW.exists():
        content = ("name: RGON External Brain Kitchen\n\n" + WF_ON_BLOCK +
                   "\npermissions:\n  contents: write\n\njobs:\n" + _job_block("  "))
        write_text(WORKFLOW, content)
        return f"{rel(WORKFLOW)} 신규 생성 (cron 03:00 KST + 수동 실행)"
    text = read_text(WORKFLOW)
    text = re.sub(re.escape(WF_START) + r".*?" + re.escape(WF_END) + r"[ \t]*\r?\n?", "", text, flags=re.S)
    text = re.sub(r"(?m)^[ \t]+(?=" + re.escape(WF_START) + ")", "", text)
    text, notes = _ensure_triggers(text)
    jm = re.search(r"(?m)^jobs\s*:\s*$", text)
    if jm:
        after = text[jm.end():]
        nm = re.search(r"(?m)^([ \t]+)\S", after)
        ind = nm.group(1) if nm else "  "
        text = text[:jm.end()] + "\n" + _job_block(ind).rstrip("\n") + text[jm.end():]
    else:
        text = text.rstrip("\n") + "\n\njobs:\n" + _job_block("  ")
    write_text(WORKFLOW, text)
    return f"{rel(WORKFLOW)} 업그레이드 (rgon_auto_evolve_brain --ci 잡 주입" + \
        (", " + ", ".join(notes) if notes else "") + ")"


# =====================================================================
# 출력
# =====================================================================
def bar(score):
    n = int(score) // 5
    return "█" * n + "░" * (20 - n)


def print_box(title):
    print("\n" + "═" * 70)
    print(f"  {title}")
    print("═" * 70)


# =====================================================================
# MAIN
# =====================================================================
def main():
    global DRY
    ap = argparse.ArgumentParser(description="RGON Auto-Evolve Brain v" + BRAIN_VERSION)
    ap.add_argument("--ci", action="store_true", help="GitHub Actions 무인 모드")
    ap.add_argument("--audit-only", action="store_true", help="진단만 수행(치유 안 함)")
    ap.add_argument("--dry-run", action="store_true", help="파일 쓰기 없이 시뮬레이션")
    ap.add_argument("--no-sheets", action="store_true", help="구글 시트 연동 생략")
    ap.add_argument("--no-clipboard", action="store_true", help="클립보드 복사 생략")
    args = ap.parse_args()
    DRY = args.dry_run

    print("=" * 70)
    print(f"  🧠 RGON AUTO-EVOLVE BRAIN v{BRAIN_VERSION}  |  {now()}")
    print(f"  📁 BASE: {BASE}")
    print(f"  ⚙️  모드: {'CI 무인' if args.ci else '로컬'}"
          f"{' / 진단 전용' if args.audit_only else ''}{' / DRY-RUN' if DRY else ''}")
    print("=" * 70)

    mem = AntibodyMemory(ANTIBODY_VAULT)
    sheets = SheetsLink()

    # 1) TOP1 스케줄 등재
    receipt = register_top1_schedule(sheets, use_sheets=not args.no_sheets)

    # 2) Reflexion: 진단 → 치유 → 레시피 진화 → 재진단
    evolver = PromptAndRecipeEvolver(mem)
    auditor = SelfAuditorAndHealer(mem, evolver)
    pre = auditor.audit("pre")
    score_pre, per_pre = health_score(pre)
    recipe_report = {}
    if not args.audit_only:
        auditor.heal(pre)
        recipe_report = evolver.evolve()
    post = auditor.audit("post")
    score_post, per_post = health_score(post)

    # 3) 외부 주방 워크플로우 (CI에서는 워크플로우 파일 자체 수정 금지)
    wf_result = "CI 모드 — 워크플로우 수정 생략" if args.ci else upgrade_workflow()

    # 4) AlphaEvolve 다음 세대 과제
    nxt = NextEvolutionGenerator(mem, ci=args.ci, no_clipboard=args.no_clipboard).generate(
        post, score_pre, score_post, auditor.heal_log)

    run = {"ts": now(), "ci": args.ci, "generation": nxt["generation"],
           "health_before": score_pre, "health_after": score_post,
           "heals": sum(1 for h in auditor.heal_log if h["result"] == "HEALED"),
           "new_antibodies": list(mem.new_this_run),
           "next_tasks": [t["title"] for t in nxt["tasks"]]}
    sheet_log = log_run(sheets, run)
    mem.save()

    # ===== 영수증 출력 =====
    print_box("🧾 [최고 1순위 스케줄 등재 영수증]")
    print(f"  priority : {receipt['priority']}")
    print(f"  task_id  : {receipt['task_id']}")
    print(f"  title    : {receipt['title']}")
    print(f"  status   : {receipt['status']}")
    print(f"  fusion   : {' + '.join(FUSION)}")
    for f in receipt["files"]:
        print(f"  📄 {f}")
    for s in receipt["sheets"] + sheet_log:
        print(f"  📊 {s}")
    print(f"  🏭 외부 주방: {wf_result}")

    print_box("🩺 [자가 진단 & 치유 점수 (100점 만점)]")
    print(f"  치유 전 : {score_pre:>3}/100  {bar(score_pre)}")
    print(f"  치유 후 : {score_post:>3}/100  {bar(score_post)}")
    if per_post:
        print("  잔존 감점: " + ", ".join(f"{k} -{v}" for k, v in sorted(per_post.items())))
    print(f"  도구 상태: node={'✅' if auditor.node else '❌'}  ffprobe={'✅' if auditor.ffprobe else '❌'}"
          f"  Pillow={'✅' if auditor.pil else '❌'}")
    print("  ── 자가 치유 기록 ──")
    if auditor.heal_log:
        for h in auditor.heal_log:
            mark = {"HEALED": "✅", "ROLLBACK": "↩️", "SKIP": "⏭️", "FAIL": "❌"}.get(h["result"], "•")
            print(f"   {mark} {h['file']}: {h.get('detail', '')} {('[' + h['verify'] + ']') if h.get('verify') else ''}")
    else:
        print("   (치유 대상 없음 또는 진단 전용 모드)")
    if recipe_report:
        print(f"  ── Grok 5대 레시피 ── 신규 {len(recipe_report['created'])} / 항체 주입 {recipe_report['injected']}"
              f" / nologo 보정 {recipe_report['pollinations_fixed']} → {recipe_report['manifest']}")
        for r in recipe_report["rows"]:
            print(f"   🟢 {r['style']:<8} LIVE  적합도 {r['fitness']:>3}  GEN-{r['generation']}")
    if auditor.media_report:
        ok = sum(1 for m in auditor.media_report if m.get("ok"))
        print(f"  ── MP4(R2) ── 합격 {ok}/{len(auditor.media_report)}")
    if post:
        print("  ── 잔존 이슈 (상위 8) ──")
        for f in post[:8]:
            print(f"   ⚠️ [{f['rule']}] {f['rel']}: {f['detail']}")
    print(f"  🧬 항체 금고: {len(mem.antibodies)}종"
          + (f"  (신규: {', '.join(mem.new_this_run)})" if mem.new_this_run else ""))

    print_box(f"🚀 [자동 생성된 다음 진화 과제 요약 — GEN-{nxt['generation']}]")
    for i, t in enumerate(nxt["tasks"], 1):
        print(f"  {i}. {t['title']}  (적합도 {t['fitness']})")
        print(f"     → {t['detail'][:110]}")
    print(f"  📝 지시문: {nxt['prompt_path']} ({nxt['chars']:,}자)")
    print(f"  📮 발사 대기열: {nxt['queue_path']} (PENDING)")
    print(f"  📋 클립보드: {nxt['clipboard']}")
    if not DRY and _backed_up:
        print(f"  📦 백업: {rel(BACKUP_ROOT)} ({len(_backed_up)}개 파일)")
    print("\nRGON AUTO-EVOLVE BRAIN v1.0 TOTAL WAR READY!")


if __name__ == "__main__":
    main()

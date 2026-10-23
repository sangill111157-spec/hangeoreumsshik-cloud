# -*- coding: utf-8 -*-
"""
step18_white_blood_cell_immune_engine.py
RGON Step 18 — R18 백혈구(WBC) 자가치유 면역 엔진 장착 스크립트 (v11.17-WBC)

작업 1: rgon_white_blood_cell.py + rgon_immune_ledger.json (항체 R1~R18)
작업 2: 실행 스크립트 상단/하단에 [RGON-WBC-GUARD-V18] 세이프가드 마커 장착
작업 3: CLAUDE.md / RGON_PHILOSOPHY.md / CODE_MAP.md / RGON_EVOLUTION_LOG.md /
        rgon_brain_snapshot.json / .rgon_file_hashes.json 동기화 (R1~R18)
작업 4: 삼성(三省) 전·중·후 SHA-256 검증 + git pull --rebase + push + MessageBoxW
"""
from __future__ import annotations

import ast
import datetime
import hashlib
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import time

VERSION = "v11.17-WBC"
STEP = 18
ANTIBODY_RANGE = "R1~R18"
R18_ID = "R18"
R18_TITLE = "백혈구(WBC) 자가치유 면역 엔진"
R18_DESC = (
    "오류 지문 채취(Fingerprint) · AST/JSON 무결성 순찰 · 자동 백업 복원(Rollback) · "
    "상선약수(上善若水) 우회 실행(Bypass) · 주역 64괘 연동 · "
    "동일 오류 3회 반복 시 중복 경보 차단(Anti-Repeat Suppression)"
)
PRINCIPLE = "만물은 하나로 이어져 있으며, 한 걸음씩 나아가면 반드시 이루어진다."

START_MARK = "[RGON-STEP18-WBC-START]"
END_MARK = "[RGON-STEP18-WBC-END]"
GUARD_START = "# [RGON-WBC-GUARD-V18-START]"
GUARD_END = "# [RGON-WBC-GUARD-V18-END]"

WBC_NAME = "rgon_white_blood_cell.py"
LEDGER_NAME = "rgon_immune_ledger.json"
HEXAGRAM_NAME = "rgon_hexagram_engine.py"
SNAPSHOT_NAME = "rgon_brain_snapshot.json"
BASELINE_NAME = ".rgon_file_hashes.json"

CANDIDATE_ROOTS = [
    r"C:\Users\sangi\Downloads\shin-agent",
    r"C:\Users\user\shin-agent",
    r"C:\Users\sangi\shin-agent",
    r"C:\Users\user\Downloads\shin-agent",
]

SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".rgon_backup", ".idea", ".vscode",
}

EXCLUDE_GUARD_NAMES = {
    WBC_NAME,
    HEXAGRAM_NAME,
    "__init__.py",
    "setup.py",
    "conftest.py",
    "s_run.py",
    "step18_white_blood_cell_immune_engine.py",
}

ANCHOR_FILES = (
    "CLAUDE.md",
    "CODE_MAP.md",
    "RGON_PHILOSOPHY.md",
    "RGON_EVOLUTION_LOG.md",
    SNAPSHOT_NAME,
    HEXAGRAM_NAME,
    "rgon_alpha_chat.html",
)


def kst_now():
    return datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    ).replace(tzinfo=None)


NOW = kst_now()
TODAY = NOW.strftime("%Y-%m-%d")
TS = NOW.strftime("%Y%m%d_%H%M%S")
BT = chr(96)
FENCE = BT * 3


def c(text):
    return BT + str(text) + BT


def console_utf8():
    for name in ("stdout", "stderr"):
        st = getattr(sys, name, None)
        if st is not None and hasattr(st, "reconfigure"):
            try:
                st.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def say(msg):
    try:
        print("[STEP18-WBC] " + str(msg), flush=True)
    except Exception:
        pass


# =====================================================================
# 경로 탐색 / 백업 / 보호 해시 (삼성 三省)
# =====================================================================
def score_dir(path):
    if not path or not os.path.isdir(path):
        return -1
    score = 1
    for a in ANCHOR_FILES:
        if os.path.exists(os.path.join(path, a)):
            score += 10
    if os.path.isdir(os.path.join(path, ".git")):
        score += 5
    try:
        for fn in os.listdir(path):
            if fn.lower().endswith((".py", ".html", ".json", ".md")):
                score += 1
    except Exception:
        pass
    return score


def locate_root():
    env = os.environ.get("RGON_ROOT", "").strip()
    pool = []
    if env:
        pool.append(env)
    pool.extend(CANDIDATE_ROOTS)
    try:
        here = os.path.abspath(os.path.dirname(__file__))
        pool.extend([here, os.path.dirname(here)])
    except Exception:
        pass
    pool.append(os.getcwd())

    for root in (r"C:\Users\sangi", r"C:\Users\user"):
        if not os.path.isdir(root):
            continue
        for sub in ("", "Downloads", "Desktop", "Documents"):
            base = os.path.join(root, sub) if sub else root
            if not os.path.isdir(base):
                continue
            try:
                for fn in os.listdir(base):
                    if "shin-agent" in fn.lower() or "hangeoreum" in fn.lower():
                        pool.append(os.path.join(base, fn))
            except Exception:
                pass

    best_path, best_score = None, -1
    seen = set()
    for p in pool:
        if not p:
            continue
        ap = os.path.abspath(p)
        key = os.path.normcase(ap)
        if key in seen:
            continue
        seen.add(key)
        sc = score_dir(ap)
        if sc > best_score:
            best_score, best_path = sc, ap
    return best_path or os.path.abspath(os.getcwd())


ROOT = ""
BACKUP_ROOT = ""
BASE_HASH = {}
BASE_BYTES = {}


def rel(path):
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except Exception:
        return path.replace("\\", "/")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def is_protected(path):
    low = os.path.basename(path).lower()
    return low.endswith(".html") or low.endswith(".js") or low == "manifest.json"


def scan_protected():
    out = {}
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".rgon_backup")]
        for fn in fns:
            full = os.path.join(dp, fn)
            if is_protected(full):
                try:
                    out[rel(full)] = sha256_file(full)
                except Exception:
                    pass
    return out


def snapshot_protected_bytes(hashes):
    snap = {}
    for r in hashes:
        full = os.path.join(ROOT, r.replace("/", os.sep))
        try:
            with open(full, "rb") as f:
                snap[r] = f.read()
        except Exception:
            pass
    return snap


def verify_stage(label):
    cur = scan_protected()
    changed = [r for r, h in BASE_HASH.items() if cur.get(r) != h]
    added = [r for r in cur if r not in BASE_HASH]
    for r in changed:
        raw = BASE_BYTES.get(r)
        if raw is not None:
            full = os.path.join(ROOT, r.replace("/", os.sep))
            try:
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "wb") as f:
                    f.write(raw)
                say("삼성(三省) 보호 복원: " + r)
            except Exception:
                pass
    cur2 = scan_protected()
    changed2 = [r for r, h in BASE_HASH.items() if cur2.get(r) != h]
    ok = len(changed2) == 0
    say("삼성(三省) [%s] 보호 파일 %d개 -> 변경 %d건 (%s)"
        % (label, len(BASE_HASH), len(changed2), "OK" if ok else "WARN"))
    return {"stage": label, "total": len(BASE_HASH), "changed": changed2, "added": added, "ok": ok}


def backup_file(path):
    if not os.path.isfile(path):
        return None
    r = rel(path).replace("/", "__").replace(":", "_")
    dst = os.path.join(BACKUP_ROOT, r + "." + TS + ".bak")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(path, dst)
    return dst


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def write_text_Checked(path, content, check_py=False):
    if is_protected(path):
        raise RuntimeError("보호 대상 파일 수정 차단(R14/R18): " + path)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    backup_file(path)
    tmp = path + ".wbc_tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    if check_py or path.lower().endswith(".py"):
        ast.parse(content, filename=path)
        py_compile.compile(tmp, doraise=True)
    os.replace(tmp, path)


def read_json(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except Exception:
        return None


def write_json_safely(path, data):
    if is_protected(path):
        return "blocked(protected)"
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(text)
    if os.path.isfile(path):
        try:
            if read_text(path) == text:
                return "unchanged"
        except Exception:
            pass
    write_text_Checked(path, text, check_py=False)
    return "updated"


# =====================================================================
# 작업 1: rgon_white_blood_cell.py 본체 생성
# =====================================================================
WBC_SOURCE = '''# -*- coding: utf-8 -*-
"""
rgon_white_blood_cell.py
RGON 백혈구(WBC: White Blood Cell) 자가치유 면역 엔진 (v11.17-WBC / 항체 R18)

6대 면역 기능:
  1. fingerprint(exc, context) : 오류 지문 채취 & 동일 지문 3회 이상 반복 경보 억제
  2. patrol(root_dir)          : Python AST / JSON / HTML 마커 무결성 순찰 & 0~100 건강 점수
  3. auto_restore(file_path)   : 손상 파일 격리 후 가장 최근 정상 백업본으로 자동 복원
  4. run_safely / shield / adapt_dict : 상선약수(上善若水) 우회 실행 (프로세스 중단 방지)
  5. link_hexagram()           : rgon_hexagram_engine.py 연동 (점검 강화 모드 판단)
  6. CLI                       : --patrol / --status / --heal <file> / --self-test
"""
from __future__ import annotations

import argparse
import ast
import datetime
import functools
import hashlib
import importlib.util
import json
import os
import py_compile
import re
import shutil
import sys
import traceback

WBC_VERSION = "v11.17-WBC"
ANTIBODY_RANGE = "R1~R18"
LEDGER_FILENAME = "rgon_immune_ledger.json"
HEXAGRAM_FILENAME = "rgon_hexagram_engine.py"
PRINCIPLE = "만물은 하나로 이어져 있으며, 한 걸음씩 나아가면 반드시 이루어진다."

PROTECTED_EXTS = (".html", ".js")
PROTECTED_NAMES = ("manifest.json",)
SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".rgon_backup", ".idea", ".vscode",
}

CAUTION_HEX_NUMBERS = {6, 12, 23, 29, 36, 39, 47}
CAUTION_KEYWORDS = ("송", "비", "박", "감", "명이", "蹇", "곤", "험", "경계", "주의", "신중", "점검")

DEFAULT_ANTIBODIES = [
    {"id": "R1",  "title": "단일 진실 공급원(SSOT) 준수 및 중복 상태 금지", "step": 1},
    {"id": "R2",  "title": "전 영역 UTF-8 입출력 명시 (Windows cp949 인코딩 오류 면역)", "step": 2},
    {"id": "R3",  "title": "작업 전 타임스탬프 백업 강제 및 원본 보존", "step": 3},
    {"id": "R4",  "title": "마커 기반 멱등(Idempotent) 패치로 재실행 안전 보장", "step": 4},
    {"id": "R5",  "title": "외부 네트워크·서브프로세스 타임아웃 및 안전 기본값", "step": 5},
    {"id": "R6",  "title": "로컬 브리지(8765) 오프라인 시 정적 폴백 동작 보장", "step": 6},
    {"id": "R7",  "title": "모바일·데스크톱 아코디언 바 겹침 방지 및 접힘 기본값", "step": 7},
    {"id": "R8",  "title": "실시간 브리핑 바 독립 데이터 경로 유지 및 잔상 차단", "step": 8},
    {"id": "R9",  "title": "단일 클린 엔진 통합 및 구 패치 블록 정리", "step": 9},
    {"id": "R10", "title": "실제 실행 경로(Downloads\\\\shin-agent) 자동 탐색 및 동기화", "step": 10},
    {"id": "R11", "title": "Shadow DOM open 전환 및 흡수기 4버튼 정밀 타겟팅", "step": 11},
    {"id": "R12", "title": "흡수기 버튼 단일 배지(V12) 정리 및 중복 렌더링 차단", "step": 12},
    {"id": "R13", "title": "유튜브 트렌드 & AI 스킬 흡수기 V13 정적 JSON 폴백 연동", "step": 13},
    {"id": "R14", "title": "MutationObserver·setInterval DOM 재배치 루프 영구 금지", "step": 14},
    {"id": "R15", "title": "단발성 placeOnce(data-placed=1) 정적 배치 원칙", "step": 15},
    {"id": "R16", "title": "카파시 4대 원칙(CLAUDE.md) + CODE_MAP.md + 보호 파일 해시 잠금", "step": 16},
    {"id": "R17", "title": "창립자 만물일체·한걸음씩 철학 + 명심보감·도덕경·주역 64괘 엔진", "step": 17},
    {"id": "R18", "title": "백혈구(WBC) 자가치유 면역 엔진 — 오류 지문·AST/JSON 순찰·백업 복원·상선약수 우회·중복 경보 억제", "step": 18},
]


def _kst_now():
    return datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    ).replace(tzinfo=None)


def _now_iso():
    return _kst_now().isoformat(timespec="seconds")


def _console_utf8():
    for name in ("stdout", "stderr"):
        st = getattr(sys, name, None)
        if st is not None and hasattr(st, "reconfigure"):
            try:
                st.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def resolve_root(root_dir=None):
    if root_dir and os.path.isdir(root_dir):
        return os.path.abspath(root_dir)
    try:
        here = os.path.abspath(os.path.dirname(__file__))
        if os.path.isdir(here):
            return here
    except Exception:
        pass
    for cand in (
        r"C:\\Users\\sangi\\Downloads\\shin-agent",
        r"C:\\Users\\user\\shin-agent",
        os.getcwd(),
    ):
        if cand and os.path.isdir(cand):
            return os.path.abspath(cand)
    return os.path.abspath(os.getcwd())


def is_protected_file(path):
    base = os.path.basename(path).lower()
    if base in PROTECTED_NAMES:
        return True
    return any(base.endswith(ext) for ext in PROTECTED_EXTS)


def _rel(path, root):
    try:
        return os.path.relpath(path, root).replace("\\\\", "/")
    except Exception:
        return path.replace("\\\\", "/")


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


# =====================================================================
# 면역 원장 (rgon_immune_ledger.json)
# =====================================================================
def ledger_path(root_dir=None):
    return os.path.join(resolve_root(root_dir), LEDGER_FILENAME)


def _default_ledger():
    return {
        "schema": "rgon.immune.ledger.v1",
        "version": WBC_VERSION,
        "current_step": 18,
        "antibody_range": ANTIBODY_RANGE,
        "principle": PRINCIPLE,
        "updated_at_kst": _now_iso(),
        "health_score": 100,
        "inspection_mode": "standard",
        "today_hexagram": {},
        "suppressed_count": 0,
        "antibodies": list(DEFAULT_ANTIBODIES),
        "fingerprints": {},
        "healed_events": [],
        "bypass_log": [],
        "patrol_history": [],
    }


def load_ledger(root_dir=None):
    path = ledger_path(root_dir)
    base = _default_ledger()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                base.update(loaded)
        except Exception:
            pass
    existing = {}
    for item in base.get("antibodies", []):
        if isinstance(item, dict) and item.get("id"):
            existing[item["id"]] = item
    for ab in DEFAULT_ANTIBODIES:
        merged = dict(ab)
        prev = existing.get(ab["id"])
        if isinstance(prev, dict):
            merged.update(prev)
        merged["title"] = ab["title"]
        merged["step"] = ab["step"]
        existing[ab["id"]] = merged
    def _ab_key(k):
        m = re.search(r"(\\d+)", str(k))
        return int(m.group(1)) if m else 999
    base["antibodies"] = [existing[k] for k in sorted(existing.keys(), key=_ab_key)]
    base["version"] = WBC_VERSION
    base["current_step"] = max(int(base.get("current_step") or 18), 18)
    base["antibody_range"] = ANTIBODY_RANGE
    base["principle"] = PRINCIPLE
    if not isinstance(base.get("fingerprints"), dict):
        base["fingerprints"] = {}
    if not isinstance(base.get("healed_events"), list):
        base["healed_events"] = []
    if not isinstance(base.get("bypass_log"), list):
        base["bypass_log"] = []
    if not isinstance(base.get("patrol_history"), list):
        base["patrol_history"] = []
    return base


def save_ledger(ledger, root_dir=None):
    root = resolve_root(root_dir)
    path = ledger_path(root)
    ledger["version"] = WBC_VERSION
    ledger["antibody_range"] = ANTIBODY_RANGE
    ledger["updated_at_kst"] = _now_iso()
    ledger["healed_events"] = ledger.get("healed_events", [])[-120:]
    ledger["bypass_log"] = ledger.get("bypass_log", [])[-120:]
    ledger["patrol_history"] = ledger.get("patrol_history", [])[-40:]
    text = json.dumps(ledger, ensure_ascii=False, indent=2) + "\\n"
    json.loads(text)
    tmp = path + ".wbc_tmp"
    with open(tmp, "w", encoding="utf-8", newline="\\n") as f:
        f.write(text)
    os.replace(tmp, path)
    return path


# =====================================================================
# 1. 오류 지문 채취 (Fingerprint) & 3회 이상 반복 경보 억제
# =====================================================================
def compute_fingerprint(exc, context="", tb_str=""):
    exc_type = type(exc).__name__ if isinstance(exc, BaseException) else str(exc)
    msg = str(exc) if exc is not None else ""
    norm_msg = re.sub(r"0x[0-9a-fA-F]+", "0xADDR", msg)
    norm_msg = re.sub(r"\\d+", "N", norm_msg)[:160]
    top_loc = ""
    if tb_str:
        lines = [ln.strip() for ln in tb_str.splitlines() if "File " in ln]
        if lines:
            top_loc = re.sub(r"line \\d+", "line L", lines[-1])[:160]
    raw = "%s|%s|%s|%s" % (exc_type, context, top_loc, norm_msg)
    return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:16]


def fingerprint(exc, context="runtime", root_dir=None, threshold=3):
    root = resolve_root(root_dir)
    tb_str = ""
    try:
        if isinstance(exc, BaseException) and exc.__traceback__ is not None:
            tb_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        else:
            tb_str = traceback.format_exc()
    except Exception:
        tb_str = ""
    fp = compute_fingerprint(exc, context=context, tb_str=tb_str)
    ledger = load_ledger(root)
    fps = ledger.setdefault("fingerprints", {})
    rec = fps.get(fp) or {
        "fingerprint": fp,
        "exc_type": type(exc).__name__ if isinstance(exc, BaseException) else "Error",
        "context": str(context),
        "sample_message": str(exc)[:240],
        "first_seen_kst": _now_iso(),
        "last_seen_kst": _now_iso(),
        "count": 0,
        "suppressed": False,
        "known_remedy": _suggest_remedy(exc),
    }
    rec["count"] = int(rec.get("count", 0)) + 1
    rec["last_seen_kst"] = _now_iso()
    rec["sample_message"] = str(exc)[:240]
    suppressed = rec["count"] >= int(threshold)
    rec["suppressed"] = suppressed
    if suppressed:
        ledger["suppressed_count"] = int(ledger.get("suppressed_count", 0)) + 1
    fps[fp] = rec
    try:
        save_ledger(ledger, root)
    except Exception:
        pass
    return {
        "fingerprint": fp,
        "count": rec["count"],
        "suppressed": suppressed,
        "should_alert": not suppressed,
        "remedy": rec.get("known_remedy", ""),
    }


def _suggest_remedy(exc):
    name = type(exc).__name__ if isinstance(exc, BaseException) else str(exc)
    table = {
        "UnicodeDecodeError": "R2 항체: open(..., encoding='utf-8', errors='replace') 적용",
        "UnicodeEncodeError": "R2 항체: 콘솔 UTF-8 재설정 및 utf-8 인코딩 명시",
        "JSONDecodeError": "R18 항체: 손상 JSON 백업 복원(auto_restore) 또는 안전 기본값 우회",
        "SyntaxError": "R18 항체: 최근 정상 스냅샷/백업에서 자동 복원(auto_restore)",
        "FileNotFoundError": "R10/R18 항체: 경로 자동 탐색(resolve_root) 또는 기본 파일 생성",
        "KeyError": "R18 상선약수: adapt_dict 안전 키 매핑 및 기본값 반환",
        "TimeoutError": "R5/R18 항체: 타임아웃 우회 후 캐시/폴백 데이터 사용",
    }
    return table.get(name, "R18 상선약수(上善若水): 안전 기본값 우회 및 면역 원장 기록")


# =====================================================================
# 2. 주역 64괘 연동 (rgon_hexagram_engine.py)
# =====================================================================
def link_hexagram(root_dir=None):
    root = resolve_root(root_dir)
    hex_path = os.path.join(root, HEXAGRAM_FILENAME)
    info = {
        "available": False,
        "number": None,
        "name": "중천건(重天乾)",
        "summary": "자강불식(自強不息) — 스스로 강건히 쉬지 않고 정진한다",
        "inspection_mode": "standard",
    }
    if not os.path.isfile(hex_path):
        return info
    try:
        spec = importlib.util.spec_from_file_location("rgon_hexagram_engine", hex_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            raw = None
            for fn_name in (
                "get_today_hexagram", "today_hexagram", "daily_hexagram",
                "get_daily_hexagram", "cast_today", "get_hexagram_of_day",
            ):
                fn = getattr(mod, fn_name, None)
                if callable(fn):
                    try:
                        raw = fn()
                        break
                    except TypeError:
                        try:
                            raw = fn(_kst_now().date())
                            break
                        except Exception:
                            pass
            if raw is None and hasattr(mod, "HEXAGRAMS"):
                hx = getattr(mod, "HEXAGRAMS")
                if isinstance(hx, (list, tuple)) and hx:
                    idx = _kst_now().timetuple().tm_yday % len(hx)
                    raw = hx[idx]
            info["available"] = True
            if isinstance(raw, dict):
                num = raw.get("number") or raw.get("no") or raw.get("id") or raw.get("index")
                name = raw.get("name") or raw.get("title") or raw.get("kr") or info["name"]
                summ = (
                    raw.get("wisdom") or raw.get("advice") or raw.get("meaning")
                    or raw.get("summary") or raw.get("action") or info["summary"]
                )
                info.update({"number": num, "name": str(name), "summary": str(summ)})
            elif raw is not None:
                info["summary"] = str(raw)[:200]
    except Exception as e:
        info["error"] = str(e)[:160]

    text_blob = "%s %s" % (info.get("name", ""), info.get("summary", ""))
    num = info.get("number")
    if (isinstance(num, int) and num in CAUTION_HEX_NUMBERS) or any(
        k in text_blob for k in CAUTION_KEYWORDS
    ):
        info["inspection_mode"] = "reinforced"
    return info


# =====================================================================
# 3. 백업 스냅샷 & 손상 파일 자동 복원 (Rollback & Quarantine)
# =====================================================================
def _snapshot_store_dir(root):
    d = os.path.join(root, ".rgon_backup", "wbc_snapshots")
    os.makedirs(d, exist_ok=True)
    return d


def _quarantine_dir(root):
    d = os.path.join(root, ".rgon_backup", "wbc_quarantine")
    os.makedirs(d, exist_ok=True)
    return d


def save_clean_snapshot(file_path, root_dir=None):
    root = resolve_root(root_dir)
    if not os.path.isfile(file_path) or is_protected_file(file_path):
        return None
    r = _rel(file_path, root).replace("/", "__").replace(":", "_")
    dst = os.path.join(_snapshot_store_dir(root), r + ".clean")
    try:
        shutil.copy2(file_path, dst)
        return dst
    except Exception:
        return None


def _is_candidate_valid(candidate_path, target_ext):
    try:
        with open(candidate_path, "r", encoding="utf-8", errors="replace") as f:
            txt = f.read()
        if target_ext == ".py":
            ast.parse(txt, filename=candidate_path)
            return True
        if target_ext == ".json":
            json.loads(txt)
            return True
        return len(txt) > 0
    except Exception:
        return False


def find_latest_valid_backup(file_path, root_dir=None):
    root = resolve_root(root_dir)
    base = os.path.basename(file_path)
    rel_key = _rel(file_path, root).replace("/", "__").replace(":", "_")
    ext = os.path.splitext(base)[1].lower()
    backup_root = os.path.join(root, ".rgon_backup")
    if not os.path.isdir(backup_root):
        return None
    candidates = []
    for dp, _, fns in os.walk(backup_root):
        if "wbc_quarantine" in dp:
            continue
        for fn in fns:
            if fn.startswith(rel_key) or fn.startswith(base) or (base in fn):
                full = os.path.join(dp, fn)
                try:
                    candidates.append((os.path.getmtime(full), full))
                except Exception:
                    pass
    candidates.sort(key=lambda x: x[0], reverse=True)
    for _, cand in candidates:
        if _is_candidate_valid(cand, ext):
            return cand
    return None


def auto_restore(file_path, reason="corruption_detected", root_dir=None):
    root = resolve_root(root_dir)
    full = file_path if os.path.isabs(file_path) else os.path.join(root, file_path)
    rel_p = _rel(full, root)
    event = {
        "timestamp_kst": _now_iso(),
        "file": rel_p,
        "reason": str(reason)[:200],
        "restored": False,
        "source_backup": None,
        "quarantined_to": None,
    }
    if is_protected_file(full):
        event["note"] = "보호 대상 파일(.html/.js/manifest.json)은 자동 덮어쓰기 금지(R16/R18)"
        _append_heal_event(event, root)
        return event

    cand = find_latest_valid_backup(full, root)
    if not cand:
        event["note"] = "유효한 정상 백업본을 찾지 못함"
        _append_heal_event(event, root)
        return event

    try:
        if os.path.isfile(full):
            qname = rel_p.replace("/", "__") + "." + _kst_now().strftime("%Y%m%d_%H%M%S") + ".corrupt"
            qpath = os.path.join(_quarantine_dir(root), qname)
            shutil.copy2(full, qpath)
            event["quarantined_to"] = _rel(qpath, root)
        shutil.copy2(cand, full)
        event["restored"] = True
        event["source_backup"] = _rel(cand, root)
    except Exception as e:
        event["error"] = str(e)[:200]

    _append_heal_event(event, root)
    return event


def _append_heal_event(event, root):
    try:
        ledger = load_ledger(root)
        ledger.setdefault("healed_events", []).append(event)
        save_ledger(ledger, root)
    except Exception:
        pass


# =====================================================================
# 4. 상선약수(上善若水) 우회 실행기 — 물처럼 막힌 곳을 돌아 흐른다
# =====================================================================
def adapt_dict(data, key_aliases=None, defaults=None):
    """외부 JSON/API 응답 키 이름이 바뀌어도 별칭(alias)과 기본값으로 흡수한다."""
    if not isinstance(data, dict):
        data = {}
    out = dict(data)
    if isinstance(key_aliases, dict):
        for canonical, aliases in key_aliases.items():
            if canonical in out and out[canonical] is not None:
                continue
            for alt in (aliases if isinstance(aliases, (list, tuple)) else [aliases]):
                if alt in data and data[alt] is not None:
                    out[canonical] = data[alt]
                    break
    if isinstance(defaults, dict):
        for k, v in defaults.items():
            if k not in out or out[k] is None:
                out[k] = v
    return out


def run_safely(fn, *args, default=None, fallback=None, context=None, root_dir=None, **kwargs):
    """함수를 안전하게 실행하고, 예외 발생 시 지문 기록 후 fallback/default로 우회한다."""
    ctx = context or getattr(fn, "__name__", "callable")
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        fp_info = fingerprint(exc, context=ctx, root_dir=root_dir)
        root = resolve_root(root_dir)
        try:
            ledger = load_ledger(root)
            ledger.setdefault("bypass_log", []).append({
                "timestamp_kst": _now_iso(),
                "context": str(ctx),
                "exc_type": type(exc).__name__,
                "message": str(exc)[:200],
                "fingerprint": fp_info.get("fingerprint"),
                "suppressed": fp_info.get("suppressed", False),
                "action": "fallback_callable" if callable(fallback) else "default_value",
            })
            save_ledger(ledger, root)
        except Exception:
            pass
        if callable(fallback):
            try:
                return fallback(*args, **kwargs)
            except Exception:
                return default
        return default


def shield(default=None, fallback=None, context=None):
    """데코레이터 형태 상선약수 방어막."""
    def _wrap(fn):
        @functools.wraps(fn)
        def _inner(*args, **kwargs):
            return run_safely(
                fn, *args,
                default=default,
                fallback=fallback,
                context=context or fn.__name__,
                **kwargs,
            )
        return _inner
    return _wrap


def install_excepthook(script_name="script", root_dir=None):
    """스크립트 전역 미처리 예외 후크 장착 (백혈구 세이프가드용)."""
    prev_hook = sys.excepthook

    def _wbc_hook(exc_type, exc_value, exc_tb):
        try:
            tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            fp = compute_fingerprint(exc_value, context=script_name, tb_str=tb_str)
            fingerprint(exc_value, context=script_name, root_dir=root_dir)
            sys.stderr.write(
                "[RGON-WBC] 예외 감지 (%s in %s, fp=%s)\\n"
                % (getattr(exc_type, "__name__", str(exc_type)), script_name, fp)
            )
        except Exception:
            pass
        if callable(prev_hook):
            prev_hook(exc_type, exc_value, exc_tb)

    sys.excepthook = _wbc_hook
    return _wbc_hook


# =====================================================================
# 5. 백혈구 무결성 순찰 (patrol) — AST / JSON / HTML 마커 / 보호 해시
# =====================================================================
MARKER_PAIR_RE = re.compile(r"\\[([A-Z0-9_-]+)-(START|END)\\]")


def _check_marker_balance(text):
    counts = {}
    for m in MARKER_PAIR_RE.finditer(text):
        prefix, kind = m.group(1), m.group(2)
        slot = counts.setdefault(prefix, {"START": 0, "END": 0})
        slot[kind] += 1
    unbalanced = []
    for prefix, slot in counts.items():
        if slot["START"] != slot["END"]:
            unbalanced.append("%s(S=%d,E=%d)" % (prefix, slot["START"], slot["END"]))
    return unbalanced


def patrol(root_dir=None, auto_heal=True):
    root = resolve_root(root_dir)
    hex_info = link_hexagram(root)
    py_checked = 0
    json_checked = 0
    html_checked = 0
    py_errors = []
    json_errors = []
    html_marker_warnings = []
    healed_now = []

    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".rgon_backup")]
        for fn in fns:
            full = os.path.join(dp, fn)
            rel_p = _rel(full, root)
            low = fn.lower()
            if low.endswith(".py"):
                py_checked += 1
                try:
                    with open(full, "r", encoding="utf-8", errors="replace") as f:
                        src = f.read()
                    ast.parse(src, filename=rel_p)
                    save_clean_snapshot(full, root)
                except Exception as exc:
                    fingerprint(exc, context="patrol:py:" + rel_p, root_dir=root)
                    healed = False
                    if auto_heal and not is_protected_file(full):
                        ev = auto_restore(full, reason="SyntaxError: " + str(exc)[:120], root_dir=root)
                        healed = bool(ev.get("restored"))
                        if healed:
                            healed_now.append(rel_p)
                    if not healed:
                        py_errors.append({"file": rel_p, "error": str(exc)[:180]})
            elif low.endswith(".json"):
                json_checked += 1
                try:
                    with open(full, "r", encoding="utf-8", errors="replace") as f:
                        raw = f.read()
                    json.loads(raw)
                    if not is_protected_file(full):
                        save_clean_snapshot(full, root)
                except Exception as exc:
                    fingerprint(exc, context="patrol:json:" + rel_p, root_dir=root)
                    healed = False
                    if auto_heal and not is_protected_file(full):
                        ev = auto_restore(full, reason="JSONDecodeError: " + str(exc)[:120], root_dir=root)
                        healed = bool(ev.get("restored"))
                        if healed:
                            healed_now.append(rel_p)
                    if not healed:
                        json_errors.append({"file": rel_p, "error": str(exc)[:180]})
            elif low.endswith(".html"):
                html_checked += 1
                try:
                    with open(full, "r", encoding="utf-8", errors="replace") as f:
                        ht = f.read()
                    unb = _check_marker_balance(ht)
                    if unb:
                        html_marker_warnings.append({"file": rel_p, "unbalanced": unb})
                except Exception:
                    pass

    baseline_path = os.path.join(root, ".rgon_file_hashes.json")
    protected_drift = []
    if os.path.isfile(baseline_path):
        try:
            with open(baseline_path, "r", encoding="utf-8", errors="replace") as f:
                base_data = json.load(f)
            base_files = base_data.get("files", base_data) if isinstance(base_data, dict) else {}
            if isinstance(base_files, dict):
                for r, old_h in base_files.items():
                    if not is_protected_file(r):
                        continue
                    fp = os.path.join(root, r.replace("/", os.sep))
                    if os.path.isfile(fp):
                        with open(fp, "rb") as bf:
                            cur_h = _sha256_bytes(bf.read())
                        if cur_h != old_h:
                            protected_drift.append(r)
        except Exception:
            pass

    penalty = (
        len(py_errors) * 15
        + len(json_errors) * 15
        + len(html_marker_warnings) * 5
        + len(protected_drift) * 10
    )
    health_score = max(0, min(100, 100 - penalty))

    report = {
        "timestamp_kst": _now_iso(),
        "version": WBC_VERSION,
        "health_score": health_score,
        "inspection_mode": hex_info.get("inspection_mode", "standard"),
        "today_hexagram": hex_info,
        "py_checked": py_checked,
        "json_checked": json_checked,
        "html_checked": html_checked,
        "py_errors": py_errors,
        "json_errors": json_errors,
        "html_marker_warnings": html_marker_warnings,
        "protected_drift": protected_drift,
        "healed_now": healed_now,
    }

    ledger = load_ledger(root)
    ledger["health_score"] = health_score
    ledger["inspection_mode"] = report["inspection_mode"]
    ledger["today_hexagram"] = hex_info
    ledger.setdefault("patrol_history", []).append({
        "timestamp_kst": report["timestamp_kst"],
        "health_score": health_score,
        "py_checked": py_checked,
        "json_checked": json_checked,
        "html_checked": html_checked,
        "errors": len(py_errors) + len(json_errors),
        "healed": len(healed_now),
    })
    save_ledger(ledger, root)
    return report


# =====================================================================
# 6. 자가 테스트 (--self-test) & CLI
# =====================================================================
def self_test(root_dir=None):
    root = resolve_root(root_dir)
    sandbox = os.path.join(root, ".rgon_backup", "wbc_selftest")
    os.makedirs(sandbox, exist_ok=True)
    sample = os.path.join(sandbox, "_wbc_dummy_sample.py")
    good_code = "# -*- coding: utf-8 -*-\\nVALUE = 42\\n"
    with open(sample, "w", encoding="utf-8", newline="\\n") as f:
        f.write(good_code)
    save_clean_snapshot(sample, root)

    with open(sample, "w", encoding="utf-8", newline="\\n") as f:
        f.write("def broken(:\\n    pass\\n")
    ev = auto_restore(sample, reason="self_test_syntax_error", root_dir=root)
    with open(sample, "r", encoding="utf-8", errors="replace") as f:
        restored_txt = f.read()
    ast.parse(restored_txt)

    def _boom():
        raise KeyError("simulated_missing_key")

    val = run_safely(_boom, default="WATER_BYPASS_OK", context="self_test_bypass", root_dir=root)
    mapped = adapt_dict({"new_title": "RGON"}, key_aliases={"title": ["new_title", "name"]}, defaults={"score": 100})
    try:
        os.remove(sample)
    except Exception:
        pass
    return {
        "restore_ok": bool(ev.get("restored")) and ("VALUE = 42" in restored_txt),
        "bypass_ok": val == "WATER_BYPASS_OK",
        "adapt_ok": mapped.get("title") == "RGON" and mapped.get("score") == 100,
    }


def format_status(root_dir=None):
    root = resolve_root(root_dir)
    ledger = load_ledger(root)
    hx = ledger.get("today_hexagram") or link_hexagram(root)
    lines = [
        "============================================================",
        " RGON 백혈구(WBC) 자가치유 면역 엔진 상태판 (" + WBC_VERSION + ")",
        "============================================================",
        " 작업 폴더     : " + root,
        " 건강 점수     : %s / 100 (점검 모드: %s)" % (ledger.get("health_score", 100), ledger.get("inspection_mode", "standard")),
        " 항체 범위     : %s (총 %d개)" % (ledger.get("antibody_range", ANTIBODY_RANGE), len(ledger.get("antibodies", []))),
        " 오늘의 괘     : %s — %s" % (hx.get("name", "-"), hx.get("summary", "-")),
        " 지문 기록 수  : %d개 (중복 경보 억제 누적: %d회)" % (len(ledger.get("fingerprints", {})), int(ledger.get("suppressed_count", 0))),
        " 치유 이력 수  : %d건 / 상선약수 우회: %d건" % (len(ledger.get("healed_events", [])), len(ledger.get("bypass_log", []))),
        " 철학 원칙     : " + PRINCIPLE,
        "============================================================",
    ]
    return "\\n".join(lines)


def main(argv=None):
    _console_utf8()
    parser = argparse.ArgumentParser(description="RGON 백혈구(WBC) 자가치유 면역 엔진")
    parser.add_argument("--patrol", action="store_true", help="전체 무결성 순찰 실행")
    parser.add_argument("--status", action="store_true", help="현재 면역 원장 상태 출력")
    parser.add_argument("--heal", metavar="FILE", help="지정 파일 백업 복원 시도")
    parser.add_argument("--self-test", action="store_true", help="자가 복원/우회 셀프 테스트")
    parser.add_argument("--root", default=None, help="작업 폴더 경로 지정")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    if args.heal:
        ev = auto_restore(args.heal, reason="manual_cli_heal", root_dir=root)
        print(json.dumps(ev, ensure_ascii=False, indent=2))
        return 0 if ev.get("restored") else 1
    if args.self_test:
        res = self_test(root)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if all(res.values()) else 1
    if args.patrol:
        rep = patrol(root, auto_heal=True)
        print(
            "[RGON-WBC] 순찰 완료: 건강 %d/100 | py=%d(오류 %d) | json=%d(오류 %d) | html=%d | 치유=%d"
            % (
                rep["health_score"],
                rep["py_checked"], len(rep["py_errors"]),
                rep["json_checked"], len(rep["json_errors"]),
                rep["html_checked"], len(rep["healed_now"]),
            )
        )
        return 0
    if args.status:
        print(format_status(root))
        return 0

    patrol(root, auto_heal=True)
    print(format_status(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def install_wbc_module():
    wbc_path = os.path.join(ROOT, WBC_NAME)
    write_text_Checked(wbc_path, WBC_SOURCE.lstrip("\n"), check_py=True)
    say("[1] 생성/검증 완료: " + WBC_NAME)
    rc, out = run_wbc(["--self-test"])
    say("[1] WBC 셀프 테스트(rc=%s): %s" % (rc, out.replace("\n", " ")))


def run_wbc(args):
    wbc_path = os.path.join(ROOT, WBC_NAME)
    try:
        cp = subprocess.run(
            [sys.executable, wbc_path] + list(args),
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        return cp.returncode, (cp.stdout + cp.stderr).strip()
    except Exception as e:
        return -1, str(e)


# =====================================================================
# 작업 2: 주요 실행 스크립트에 [RGON-WBC-GUARD-V18] 세이프가드 장착
# =====================================================================
PREFERRED_TARGETS = [
    "rgon_youtube_skill_scout.py",
    "control_tower_bot.py",
    "telegram_morning_report.py",
    "update_3channels_analytics.py",
    "github_scout_adapter.py",
]


def discover_targets():
    found = []
    seen = set()
    for name in PREFERRED_TARGETS:
        p = os.path.join(ROOT, name)
        if os.path.isfile(p):
            found.append(name)
            seen.add(name.lower())
    try:
        for fn in sorted(os.listdir(ROOT)):
            low = fn.lower()
            if not low.endswith(".py") or low in seen or fn in EXCLUDE_GUARD_NAMES:
                continue
            if re.match(r"^step\d+_", low):
                continue
            if any(k in low for k in ("scout", "bot", "report", "analytics", "tower", "agent", "bridge")):
                found.append(fn)
                seen.add(low)
    except Exception:
        pass
    return found


def build_guard_block(script_name):
    return "\n".join([
        GUARD_START,
        "try:",
        "    import rgon_white_blood_cell as _rgon_wbc",
        "    _rgon_wbc.install_excepthook(" + repr(script_name) + ")",
        "except Exception:",
        "    _rgon_wbc = None",
        GUARD_END,
    ])


def find_insertion_line(src):
    lines = src.splitlines(keepends=True)
    try:
        tree = ast.parse(src)
    except Exception:
        return 0
    insert_after_line = 0
    idx = 0
    while idx < len(lines) and (lines[idx].startswith("#!") or "coding" in lines[idx] or not lines[idx].strip()):
        insert_after_line = idx + 1
        idx += 1
    body = tree.body
    pos = 0
    if pos < len(body):
        first = body[pos]
        if (
            isinstance(first, ast.Expr)
            and isinstance(getattr(first, "value", None), ast.Constant)
            and isinstance(first.value.value, str)
        ):
            insert_after_line = max(insert_after_line, getattr(first, "end_lineno", first.lineno))
            pos += 1
    while pos < len(body):
        stmt = body[pos]
        if isinstance(stmt, ast.ImportFrom) and stmt.module == "__future__":
            insert_after_line = max(insert_after_line, getattr(stmt, "end_lineno", stmt.lineno))
            pos += 1
        else:
            break
    return insert_after_line


def inject_guard(rel_name):
    path = os.path.join(ROOT, rel_name)
    if not os.path.isfile(path) or is_protected(path):
        return "skipped"
    src = read_text(path)
    try:
        ast.parse(src, filename=rel_name)
    except Exception as e:
        return "skipped_invalid_source(%s)" % e

    block = build_guard_block(rel_name)
    pat = re.compile(re.escape(GUARD_START) + r".*?" + re.escape(GUARD_END), re.S)
    if GUARD_START in src and GUARD_END in src:
        new_src = pat.sub(lambda _m: block, src, count=1)
    else:
        lines = src.splitlines(keepends=True)
        ins = find_insertion_line(src)
        prefix = "".join(lines[:ins])
        suffix = "".join(lines[ins:])
        if prefix and not prefix.endswith("\n"):
            prefix += "\n"
        new_src = prefix + block + "\n" + suffix

    if new_src == src:
        return "unchanged"
    ast.parse(new_src, filename=rel_name)
    write_text_Checked(path, new_src, check_py=True)
    return "guarded"


# =====================================================================
# 작업 3 & 4: 문서/스냅샷 R18 동기화
# =====================================================================
def hexagram_label_from_file():
    ledger = read_json(os.path.join(ROOT, LEDGER_NAME))
    if isinstance(ledger, dict):
        hx = ledger.get("today_hexagram")
        if isinstance(hx, dict) and hx.get("name"):
            return "%s — %s" % (hx.get("name"), hx.get("summary", ""))
    return "중천건(重天乾) — 자강불식(自強不息)"


def upsert_md(path, body, title_if_new, refresh_refs=True):
    wrapped = "<!-- " + START_MARK + " -->\n" + body.strip() + "\n<!-- " + END_MARK + " -->"
    if os.path.isfile(path):
        src = read_text(path)
    else:
        src = title_if_new + "\n\n"
    if refresh_refs:
        src = src.replace("R1~R17", "R1~R18").replace("v11.16-SOUL", VERSION)
    pat = re.compile(
        r"<!--\s*" + re.escape(START_MARK) + r"\s*-->.*?<!--\s*" + re.escape(END_MARK) + r"\s*-->",
        re.S,
    )
    if pat.search(src):
        new_src = pat.sub(lambda _m: wrapped, src, count=1)
    elif START_MARK in src and END_MARK in src:
        pat2 = re.compile(re.escape(START_MARK) + r".*?" + re.escape(END_MARK), re.S)
        new_src = pat2.sub(lambda _m: wrapped, src, count=1)
    else:
        if not src.endswith("\n"):
            src += "\n"
        new_src = src + "\n" + wrapped + "\n"
    if os.path.isfile(path) and new_src == read_text(path):
        return "unchanged"
    write_text_Checked(path, new_src, check_py=False)
    return "updated"


def doc_claude(health, guarded):
    g = ", ".join(c(x) for x in guarded) if guarded else "(없음)"
    return "\n".join([
        "## R18. 백혈구(WBC) 자가치유 면역 엔진 (" + VERSION + " · 항체 " + ANTIBODY_RANGE + ")",
        "",
        "- **엔진 본체**: " + c(WBC_NAME) + " / **면역 원장**: " + c(LEDGER_NAME),
        "- **핵심 역할**: " + R18_DESC,
        "- **세이프가드 장착 스크립트**: " + g,
        "- **현재 건강 점수**: **" + str(health) + " / 100**",
        "- **CLI 점검 명령**: " + c("python rgon_white_blood_cell.py --patrol") + " / " + c("python rgon_white_blood_cell.py --status"),
        "- **절대 금기 준수**: " + c(".html") + " / " + c(".js") + " / " + c("manifest.json") + " 수정 0건, " + c("MutationObserver") + " · " + c("setInterval") + " DOM 루프 금지(R14).",
    ])


def doc_philosophy():
    return "\n".join([
        "## 제5장. 백혈구(WBC) 자가치유 면역의 도(道) — 항체 R18 (" + VERSION + ")",
        "",
        "> **" + PRINCIPLE + "**",
        "",
        "- **명심보감 삼성(三省) 순찰**: 파일 손상 여부를 전·중·후로 살피고, 구문/JSON 파손 시 최근 정상 백업으로 스스로 치유한다.",
        "- **도덕경 상선약수(上善若水) 우회**: 외부 환경이 변해 막히더라도 멈추지 않고 " + c("run_safely") + " · " + c("adapt_dict") + " 로 물처럼 돌아 흐른다.",
        "- **주역 64괘 연동**: " + c(HEXAGRAM_NAME) + " 의 오늘의 괘가 험난·경계 괘일 때 점검 모드를 강화(reinforced)한다.",
        "- **중복 경보 억제**: 동일 오류 지문(Fingerprint)이 3회 이상 반복되면 중복 경보를 잠재우고 면역 원장에만 조용히 기록한다.",
    ])


def doc_codemap(guarded):
    g = ", ".join(c(x) for x in guarded) or "(없음)"
    return "\n".join([
        "## Step 18 코드 맵 (" + VERSION + ")",
        "",
        "- " + c(WBC_NAME) + ": 백혈구 자가치유 & 면역 순찰 엔진 (patrol / run_safely / shield / adapt_dict / fingerprint / install_excepthook / link_hexagram)",
        "- " + c(LEDGER_NAME) + ": 면역 원장 (antibodies R1~R18, healed_events, bypass_log, fingerprints, suppressed_count, health_score)",
        "- " + c("step18_white_blood_cell_immune_engine.py") + ": Step 18 설치 스크립트 (멱등)",
        "- 세이프가드 장착 대상: " + g,
        "- 백업: " + c(".rgon_backup/step18_*") + ", 스냅샷: " + c(".rgon_backup/wbc_snapshots") + ", 격리: " + c(".rgon_backup/wbc_quarantine"),
    ])


def doc_evolution(health, guarded, hexa):
    return "\n".join([
        "## " + TODAY + " Step 18: " + VERSION,
        "",
        "- 신규 항체 **" + R18_ID + "** 확립 -> 항체 범위 " + ANTIBODY_RANGE,
        "- " + R18_DESC,
        "- 세이프가드 장착: " + (", ".join(guarded) or "(없음)"),
        "- 첫 순찰 건강 점수: " + str(health) + "/100 / 오늘의 괘: " + str(hexa),
        "- 원리: " + PRINCIPLE,
    ])


def update_snapshot(path, health, guarded, hexa):
    data = read_json(path)
    if not isinstance(data, dict):
        if not os.path.isfile(path) and os.path.normpath(os.path.dirname(path)) != os.path.normpath(ROOT):
            return "skip(missing)"
        data = {}
    data["version"] = VERSION
    data["current_step"] = STEP
    data["antibody_range"] = ANTIBODY_RANGE
    data["antibody_count"] = 18
    ab = data.get("antibodies")
    entry = {"id": R18_ID, "title": R18_DESC, "step": STEP, "added_kst": TODAY}
    if isinstance(ab, list):
        found = False
        for i, it in enumerate(ab):
            ident = it.get("id") if isinstance(it, dict) else str(it)
            if str(ident).startswith("R18"):
                ab[i] = entry if isinstance(it, dict) else R18_ID + ": " + R18_DESC
                found = True
        if not found:
            if ab and not isinstance(ab[0], dict):
                ab.append(R18_ID + ": " + R18_DESC)
            else:
                ab.append(entry)
    elif isinstance(ab, dict):
        ab[R18_ID] = R18_DESC
    else:
        data["antibodies"] = [entry]
    data["white_blood_cell"] = {"engine": WBC_NAME, "ledger": LEDGER_NAME, "health_score": health,
                                "guarded_scripts": guarded, "today_hexagram": hexa, "principle": PRINCIPLE}
    data["updated_at_kst"] = kst_now().isoformat(timespec="seconds")
    return write_json_safely(path, data)


# =====================================================================
# 작업 5: 베이스라인 / Git / MessageBox
# =====================================================================
def update_baseline(hashes):
    path = os.path.join(ROOT, BASELINE_NAME)
    old = read_json(path)
    data = old if isinstance(old, dict) else {}
    data["algorithm"] = "sha256"
    data["files"] = hashes
    data["file_count"] = len(hashes)
    data["version"] = VERSION
    data["verified_by"] = "step18 삼성(三省) 검증"
    data["updated_at_kst"] = kst_now().isoformat(timespec="seconds")
    return write_json_safely(path, data)


def git(args, timeout=180):
    try:
        cp = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=timeout)
        return cp.returncode, (cp.stdout + cp.stderr).strip()
    except Exception as e:
        return -1, str(e)


def git_sync():
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        return "Git 저장소 아님 (건너뜀)"
    git(["add", "-A"])
    for n in (WBC_NAME, LEDGER_NAME):
        if os.path.isfile(os.path.join(ROOT, n)):
            git(["add", "-f", n])
    rc, out = git(["diff", "--cached", "--quiet"])
    committed = False
    if rc != 0:
        rc, out = git(["commit", "-m", "feat(step18): R18 백혈구(WBC) 자가치유 면역 엔진 " + VERSION])
        committed = rc == 0
        say("git commit -> %s" % ("OK" if committed else out[:200]))
    for i in range(3):
        rc, out = git(["pull", "--rebase", "origin", "main"])
        if rc != 0:
            git(["rebase", "--abort"])
            say("pull 실패 (%d/3): %s" % (i + 1, out[:200]))
            time.sleep(2 ** (i + 1))
            continue
        rc, out = git(["push", "origin", "main"])
        if rc == 0:
            return "push 성공" + (" (커밋 생성)" if committed else " (변경 없음)")
        say("push 실패 (%d/3): %s" % (i + 1, out[:200]))
        time.sleep(2 ** (i + 1))
    return "push 실패 (3회 재시도 후, 로컬 커밋 %s)" % ("있음" if committed else "없음")


def message_box(title, text):
    say(text.replace("\n", " | "))
    if os.name != "nt":
        return
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x40 | 0x40000)
    except Exception:
        pass


# =====================================================================
# 메인
# =====================================================================
def main():
    global ROOT, BACKUP_ROOT, BASE_HASH, BASE_BYTES
    console_utf8()
    ROOT = locate_root()
    BACKUP_ROOT = os.path.join(ROOT, ".rgon_backup", "step18_" + TS)
    os.makedirs(BACKUP_ROOT, exist_ok=True)
    say("작업 폴더: " + ROOT)

    BASE_HASH = scan_protected()
    BASE_BYTES = snapshot_protected_bytes(BASE_HASH)
    stages = [verify_stage("전(前)")]

    install_wbc_module()

    guarded = []
    for t in discover_targets():
        try:
            r = inject_guard(t)
        except Exception as e:
            r = "error:%s" % e
        say("[2] %s -> %s" % (t, r))
        if r.startswith(("guarded", "unchanged")):
            guarded.append(t)

    rc, out = run_wbc(["--patrol"])
    say("[3] 첫 백혈구 순찰 rc=%s (%s)" % (rc, out.replace("\n", " ")))
    ledger = read_json(os.path.join(ROOT, LEDGER_NAME)) or {}
    health = ledger.get("health_score", 0) if isinstance(ledger, dict) else 0
    hexa = hexagram_label_from_file()
    stages.append(verify_stage("중(中)"))

    upsert_md(os.path.join(ROOT, "CLAUDE.md"), doc_claude(health, guarded), "# CLAUDE.md")
    upsert_md(os.path.join(ROOT, "RGON_PHILOSOPHY.md"), doc_philosophy(), "# RGON PHILOSOPHY")
    upsert_md(os.path.join(ROOT, "CODE_MAP.md"), doc_codemap(guarded), "# CODE MAP")
    upsert_md(os.path.join(ROOT, "RGON_EVOLUTION_LOG.md"), doc_evolution(health, guarded, hexa),
              "# RGON EVOLUTION LOG", refresh_refs=False)
    for sub in ("", "dashboard", "docs"):
        p = os.path.join(ROOT, sub, SNAPSHOT_NAME) if sub else os.path.join(ROOT, SNAPSHOT_NAME)
        try:
            say("[4] %s -> %s" % (rel(p), update_snapshot(p, health, guarded, hexa)))
        except Exception as e:
            say("[4] %s -> error:%s" % (rel(p), e))

    final = verify_stage("후(後)")
    stages.append(final)
    all_ok = all(s["ok"] for s in stages)
    if all_ok:
        update_baseline(BASE_HASH)
    rc_st, out_st = run_wbc(["--status"])
    say("[5] 상태판:\n" + out_st)

    git_result = git_sync()
    stages.append(verify_stage("동기화 후"))
    all_ok = all(s["ok"] for s in stages)

    text = "\n".join([
        "RGON Step 18 완료 (" + VERSION + ")",
        "",
        "백혈구 건강 점수: %s / 100" % health,
        "항체: " + ANTIBODY_RANGE,
        "보호 파일 %d개 삼성 해시 검증: %s" % (len(BASE_HASH), "변경 0건 통과" if all_ok else "이상 감지(원복 시도함)"),
        "세이프가드 장착: %d개" % len(guarded),
        "오늘의 괘: " + str(hexa),
        "Git: " + git_result,
        "",
        PRINCIPLE,
    ])
    message_box("RGON 백혈구 면역 엔진", text)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

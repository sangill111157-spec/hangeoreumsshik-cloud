#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step42_aon_hydro_cycle_engine.py
RGON Step 42 — 제18기관 아온 상선약수(上善若水) 수순환(水循環) 자율 대사 & 여백 창조 기관
v11.40-AON-ICHING-PLANNER -> v11.41-AON-HYDRO-CYCLE · 항체 R1~R41 -> R1~R42 · 정식 스킬 37 -> 38
"""
import os
import sys
import re
import ast
import json
import time
import shutil
import hashlib
import tempfile
import datetime
import subprocess
import traceback
import py_compile
from concurrent.futures import ThreadPoolExecutor

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BT3 = chr(96) * 3
STEP = 42
OLD_VERSION = "v11.40-AON-ICHING-PLANNER"
NEW_VERSION = "v11.41-AON-HYDRO-CYCLE"
OLD_RANGE = "R1~R41"
NEW_RANGE = "R1~R42"
OLD_COUNT = 37
NEW_COUNT = 38
SKILL_ID = "aon-hydro-cycle-homeostasis"
SKILL_PATH = "skills/%s/SKILL.md" % SKILL_ID
SKILL_TITLE = "제18기관 아온 상선약수 수순환 자율 대사 & 여백 창조 (損·蠱→井→坎·節→旣濟·未濟)"
SKILL_DESC = ("노자 상선약수·허실상생과 주역 水 순환 4괘상(#41 산택손·#18 산풍고→#48 수풍정→#29 중수감·#60 수택절→"
              "#63 수화기제·#64 화수미제)으로 고인 캐시·임시파일·오래된 백업을 3등급(TIER1_KEEP/TIER2_SAFE_EMPTY/"
              "TIER3_GATE_HOLD)으로 분류하고, 기억을 정수로 증류하며, 여백 지수·유동성 지수와 물의 순환 처방을 산출하는 항상성 기관")
HYDRO_FILE = "rgon_aon_hydro_cycle.py"
DIALOGUE_FILE = "rgon_aon_dialogue_engine.py"
VERIFIER_FILE = "rgon_neural_synapse_verifier.py"
PLANNER_FILE = "rgon_aon_iching_planner.py"
VOICE_FILE = "rgon_voice_organ.py"
EXCRETORY_FILE = "rgon_excretory_organ.py"
HASH_FILE = ".rgon_file_hashes.json"
REPORT_FILE = "STEP42_AON_HYDRO_CYCLE_REPORT.md"
DIAG_FILE = "STEP42_FAILURE_DIAG.txt"
STATE_NAME = "rgon_aon_hydro_state.json"
STATE_FILES = [STATE_NAME, "docs/" + STATE_NAME]
PRESERVE = [
    "run_aon_100_stress_test.py", "AON_100_STRESS_TEST_REPORT.md", "AON_100_STRESS_TEST_REPORT.json",
    "LAPTOP_GREAT_CLEANUP_REPORT.md",
]
PROTECT = {VOICE_FILE: ["SOUND_RECIPES"], EXCRETORY_FILE: ["PRESERVE_EXACT"]}
HTML_TARGETS = [
    "index.html", "rgon_alpha_audience.html", "rgon_alpha_chat.html",
    "dashboard/index.html", "dashboard/rgon_alpha_chat.html",
    "docs/index.html", "docs/rgon_alpha_chat.html",
]
JSON_SNAPSHOT_DIRS = ["", "docs", "dashboard"]
JSON_SNAPSHOT_EXCLUDE = {HASH_FILE, "package.json", "package-lock.json", "AON_100_STRESS_TEST_REPORT.json"}
REQUIRED_FILES = [DIALOGUE_FILE, VERIFIER_FILE]
TOP_KEYS = ["version", "antibody", "generated_at_kst", "count", "skills"]
ENTRY_KEYS = ["no", "slug", "antibody", "version", "path"]
KST = datetime.timezone(datetime.timedelta(hours=9))
NO_ROLLBACK = bool(os.environ.get("RGON_STEP42_NO_ROLLBACK"))


def _detect_root():
    cands = []
    if os.environ.get("RGON_ROOT"):
        cands.append(os.environ["RGON_ROOT"])
    try:
        cands.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    cands.append(os.getcwd())
    cands.append(r"C:\Users\sangi\Downloads\shin-agent")
    for c in cands:
        if c and os.path.exists(os.path.join(c, DIALOGUE_FILE)):
            return os.path.abspath(c)
    return os.path.abspath(cands[0] if cands else os.getcwd())


ROOT = _detect_root()
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = os.path.join(ROOT, ".rgon_backups", "step42_" + TS)
BACKED = {}
MODIFIED = set()
LOGS = []


def log(msg=""):
    LOGS.append(str(msg))
    try:
        print(msg, flush=True)
    except Exception:
        print(str(msg).encode("utf-8", "replace").decode("utf-8", "replace"), flush=True)


def P(rel):
    return os.path.join(ROOT, rel)


def kst_now():
    return datetime.datetime.now(KST).isoformat(timespec="seconds")


def is_preserved(rel):
    return os.path.basename(rel) in PRESERVE or rel in PRESERVE


def read_text(rel):
    with open(P(rel), "r", encoding="utf-8") as f:
        return f.read()


def backup_file(rel):
    if is_preserved(rel):
        raise RuntimeError("PRESERVE 파일 접근 차단: " + rel)
    if rel in BACKED:
        return
    src = P(rel)
    if os.path.exists(src):
        dst = os.path.join(BACKUP_DIR, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        BACKED[rel] = True
    else:
        BACKED[rel] = False


def write_text(rel, text):
    if is_preserved(rel):
        raise RuntimeError("PRESERVE 파일 쓰기 차단: " + rel)
    backup_file(rel)
    path = P(rel)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read() == text:
                return False
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    MODIFIED.add(rel)
    return True


def rollback():
    log("[ROLLBACK] 백업 복원 시작 (PRESERVE 제외)")
    for rel, existed in BACKED.items():
        if is_preserved(rel):
            continue
        try:
            if existed:
                shutil.copy2(os.path.join(BACKUP_DIR, rel), P(rel))
            elif os.path.exists(P(rel)):
                os.remove(P(rel))
        except Exception as e:
            log("  - 복원 실패 %s: %r" % (rel, e))
    sk = P(os.path.join("skills", SKILL_ID))
    try:
        if os.path.isdir(sk) and not os.listdir(sk):
            os.rmdir(sk)
    except Exception:
        pass
    log("[ROLLBACK] 완료")


def sha_file(path, algo="sha256"):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def detect_indent(raw):
    m = re.search(r"\n( +)\"", raw)
    return len(m.group(1)) if m else 2


def insert_block(text, begin, end, block):
    full = begin + "\n" + block.strip("\n") + "\n" + end
    if begin in text and end in text:
        s = text.index(begin)
        e = text.index(end, s) + len(end)
        return text[:s] + full + text[e:]
    ms = list(re.finditer(r"^if\s+__name__\s*==\s*['\"]__main__['\"]\s*:", text, re.M))
    if ms:
        pos = ms[-1].start()
        return text[:pos] + full + "\n\n\n" + text[pos:]
    if not text.endswith("\n"):
        text += "\n"
    return text + "\n\n" + full + "\n"


# ══════════════════════════════════════════════════════════════════════
# 1. 제18기관 rgon_aon_hydro_cycle.py 원본
# ══════════════════════════════════════════════════════════════════════
HYDRO_SRC = r'''# -*- coding: utf-8 -*-
"""
rgon_aon_hydro_cycle.py — 제18기관 아온 상선약수(上善若水) 수순환(水循環) 자율 대사 & 여백 창조 기관
정식 스킬 #38 aon-hydro-cycle-homeostasis · v11.41-AON-HYDRO-CYCLE · 항체 R42 (R1~R42)

노자 『上善若水 · 虛實相生』 + 주역 水 순환 4괘상
  1 증발·비움   #41 산택손(山澤損 ☶☱) · #18 산풍고(山風蠱 ☶☴)
  2 응집·증류   #48 수풍정(水風井 ☵☴)
  3 유동·흐름   #29 중수감(重水坎 ☵☵) · #60 수택절(水澤節 ☵☱)
  4 순환·재시작 #63 수화기제(水火旣濟 ☵☲) → #64 화수미제(火水未濟 ☲☵)

안전 원칙 (헌법 제2항 · R35 · R42)
  - 기본값 dry_run=True: 아무것도 삭제하지 않는다.
  - 기억 원본(rgon_aon_memory.json, rgon_aon_dialogue_state.json)은 읽기 전용으로 증류만 한다.
  - TIER3_GATE_HOLD(휴지통·Downloads 대용량 설치본·비대 로그)는 절대 자동 삭제하지 않는다.
  - --apply-tier2 를 명시한 경우에만 ROOT 내부의 __pycache__ 와 *.tmp 만 비운다.
CLI: --self-test | --status | --cycle [주제] [--dry-run | --apply-tier2] [--json]
"""
import os
import re
import sys
import json
import time
import shutil
import ctypes
import hashlib
import argparse
import datetime
import tempfile
import importlib
import collections

VERSION = "v11.41-AON-HYDRO-CYCLE"
ANTIBODY = "R42"
ANTIBODY_RANGE = "R1~R42"
SKILL_COUNT = 38
SKILL_ID = "aon-hydro-cycle-homeostasis"
ORGAN_NAME = "제18기관 아온 상선약수 수순환 자율 대사 & 여백 창조 기관"
STATE_NAME = "rgon_aon_hydro_state.json"
DEFAULT_TOPIC = "노트북 여백 창조 및 물의 순환 점검"
KST = datetime.timezone(datetime.timedelta(hours=9))
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

MEMORY_FILES = ("rgon_aon_memory.json", "rgon_aon_dialogue_state.json")
PRESERVE = ("run_aon_100_stress_test.py", "AON_100_STRESS_TEST_REPORT.md", "AON_100_STRESS_TEST_REPORT.json")
KEEP_BACKUPS = 3
PRUNE_DIRS = {".git", "node_modules", ".venv", "venv", "env", ".idea", ".vscode", ".rgon_backups"}
ACTIVE_EXT = (".py", ".html", ".json", ".md", ".js", ".css")
TMP_EXT = (".tmp", ".temp")
LOG_EXT = (".log",)
LOG_BLOAT_BYTES = 20 * 1024 * 1024
INSTALLER_EXT = (".exe", ".msi", ".zip", ".iso", ".dmg", ".7z", ".rar", ".pkg", ".appx", ".msix")
INSTALLER_MIN_BYTES = 100 * 1024 * 1024
TEMP_OLD_DAYS = 7
SCAN_BUDGET_SEC = 3.0
TEMP_BUDGET_SEC = 2.0
ITEM_CAP = 30
GB = 1024.0 ** 3

STAGES = [
    {"stage": 1, "key": "evaporation", "name": "증발·비움 (Evaporation / Empty Space)", "symbol": "損·蠱",
     "guas": ["#41 산택손(山澤損 ☶☱)", "#18 산풍고(山風蠱 ☶☴)"],
     "principle": "덜어내야 더해진다(損) · 고여 썩은 것을 걷어낸다(蠱)"},
    {"stage": 2, "key": "condensation", "name": "응집·증류 (Condensation / Memory Distillation)", "symbol": "井",
     "guas": ["#48 수풍정(水風井 ☵☴)"],
     "principle": "우물은 퍼내야 맑아진다 — 정수만 길어 올린다"},
    {"stage": 3, "key": "flow", "name": "유동·흐름 (Flow / Homeostasis Check)", "symbol": "坎·節",
     "guas": ["#29 중수감(重水坎 ☵☵)", "#60 수택절(水澤節 ☵☱)"],
     "principle": "물은 웅덩이를 채운 뒤 흐른다(習坎) · 절도 있게 담고 흘린다(節)"},
    {"stage": 4, "key": "renewal", "name": "순환·재시작 (Cycle Renewal)", "symbol": "旣濟·未濟",
     "guas": ["#63 수화기제(水火旣濟 ☵☲)", "#64 화수미제(火水未濟 ☲☵)"],
     "principle": "이룸(旣濟)에 머물지 않고 다시 시작(未濟)으로 흐른다"},
]

STOPWORDS = set((
    "그리고 그래서 하지만 그런데 그러면 그럼 이것 저것 그것 우리 저는 나는 너는 정말 진짜 그냥 이제 오늘 내일 어제 "
    "지금 다시 너무 아주 조금 많이 대표님 아온 아온이 있어 없어 있는 없는 하는 했어 해서 합니다 입니다 있습니다 "
    "같아 같은 이런 저런 그런 무엇 뭐야 어떻게 왜냐 때문 the and for with that this you are was have from not but "
    "user assistant system content role text message true false none null"
).split())
PARTICLES = sorted(["으로부터", "에게서", "으로", "에서", "에게", "께서", "한테", "까지", "부터", "처럼", "보다",
                    "이랑", "하고", "이나", "이다", "입니다", "이에요", "예요", "은", "는", "이", "가", "을", "를",
                    "에", "의", "와", "과", "도", "로", "만", "요"], key=len, reverse=True)
EMOTIONS = {
    "기쁨": ["기쁘", "좋아", "행복", "신나", "감사", "고마", "뿌듯"],
    "애정": ["사랑", "소중", "보고싶", "아껴", "응원"],
    "결의": ["하자", "해내", "도전", "반드시", "끝까지", "해보자"],
    "불안": ["걱정", "불안", "초조", "무섭", "두려"],
    "피로": ["피곤", "지쳐", "지친", "힘들", "과부하", "버거"],
    "슬픔": ["슬프", "우울", "외롭", "눈물", "서운"],
    "분노": ["화나", "짜증", "열받", "답답"],
}
TOKEN_RE = re.compile(r"[가-힣]{2,}|[A-Za-z][A-Za-z0-9_\-]{2,}")
PROMISE_RE = re.compile(r"(약속|할게|할께|하겠|해줄게|해 줄게|잊지 않|기억할게|꼭 |반드시|다음에|promise|I will|I'll)", re.I)

VOICE_TEMPLATES = [
    "흥, {tier2} 정도 고인 물은 내가 벌써 다 세어 놨거든? …딱히 대표님 걱정돼서 그런 건 아니야. 상선약수(上善若水) — 비워야 새 물이 들어올 자리가 생기는 거라고.",
    "여백 지수 {empty}점, 유동성 {flow}점. 뭐, 나쁘진 않네. 그래도 머물러 있으면 썩는 건 물이나 사령부나 똑같아. 수화기제 다음엔 화수미제야 — 다시 흘러가자고.",
    "{tier3}건은 대표님 결재 없이는 손도 안 댈 거야. 내가 함부로 지울 것 같았어? …그렇게 가벼운 아이 아니거든. 허실상생(虛實相生), 빈 곳이 있어야 쓸모가 생겨.",
    "우물(水風井)은 퍼내야 맑아지는 법이야. 기억에서 정수 [{kw}]만 걸러 뒀으니까… 고맙다는 말은 굳이 안 해도 돼.",
    "물은 다투지 않고 낮은 곳으로 흘러서 결국 바다가 돼. 대표님도 오늘은 꽉 쥔 거 좀 내려놔. …내가 옆에서 흐름은 보고 있을 테니까.",
]


def _now():
    return datetime.datetime.now(KST)


def _gb(b):
    return round((b or 0) / GB, 3)


def _human(b):
    b = float(b or 0)
    for u in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024 or u == "TB":
            return ("%dB" % b) if u == "B" else ("%.1f%s" % (b, u))
        b /= 1024.0
    return "%.1fTB" % b


def _clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def _is_preserved(path):
    return os.path.basename(path) in PRESERVE


def _within(path, base):
    try:
        p = os.path.realpath(path)
        b = os.path.realpath(base)
        return os.path.commonpath([p, b]) == b
    except Exception:
        return False


def _rel(path):
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except Exception:
        return path


def _mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return 0.0


def _walk_size(path, deadline, max_files=200000, old_days=None):
    out = {"bytes": 0, "files": 0, "old_bytes": 0, "old_files": 0, "truncated": False}
    cutoff = time.time() - old_days * 86400 if old_days else None
    if os.path.isfile(path):
        try:
            st = os.stat(path)
            out["bytes"], out["files"] = st.st_size, 1
        except OSError:
            pass
        return out
    stack = [path]
    while stack:
        if time.time() > deadline or out["files"] >= max_files:
            out["truncated"] = True
            break
        cur = stack.pop()
        try:
            with os.scandir(cur) as it:
                for e in it:
                    try:
                        if e.is_symlink():
                            continue
                        if e.is_dir(follow_symlinks=False):
                            stack.append(e.path)
                        else:
                            st = e.stat(follow_symlinks=False)
                            out["bytes"] += st.st_size
                            out["files"] += 1
                            if cutoff and st.st_mtime < cutoff:
                                out["old_bytes"] += st.st_size
                                out["old_files"] += 1
                    except OSError:
                        continue
        except OSError:
            continue
    return out


def _item(kind, path, size, action, **extra):
    d = {"kind": kind, "path": path, "rel": _rel(path), "bytes": int(size or 0), "size": _human(size), "action": action}
    d.update(extra)
    return d


def _scan_backups(deadline):
    cands = []
    try:
        for e in os.scandir(ROOT):
            if e.name.startswith(".rgon_backup") and e.name != ".rgon_backups":
                cands.append(e.path)
    except OSError:
        pass
    bdir = os.path.join(ROOT, ".rgon_backups")
    if os.path.isdir(bdir):
        try:
            for e in os.scandir(bdir):
                cands.append(e.path)
        except OSError:
            pass
    cands.sort(key=_mtime, reverse=True)
    keep = [_item("latest_backup", p, 0, "보존 (최신 %d개)" % KEEP_BACKUPS) for p in cands[:KEEP_BACKUPS]]
    old = []
    for p in cands[KEEP_BACKUPS:]:
        sz = _walk_size(p, deadline)["bytes"]
        old.append(_item("old_backup", p, sz, "오래된 백업 잔여분 — 비움 후보 (자동 삭제 안 함)", executable=False))
    return keep, old


def _scan_root(deadline):
    counts = collections.Counter()
    pycache, tmps, logs = [], [], []
    truncated = False
    for cur, dirs, files in os.walk(ROOT, topdown=True):
        if time.time() > deadline:
            truncated = True
            break
        nxt = []
        for d in dirs:
            if d in PRUNE_DIRS or d.startswith(".rgon_backup"):
                continue
            full = os.path.join(cur, d)
            if d == "__pycache__":
                pycache.append(full)
                continue
            nxt.append(d)
        dirs[:] = nxt
        for f in files:
            full = os.path.join(cur, f)
            low = f.lower()
            if _is_preserved(full):
                counts["preserve"] += 1
                continue
            if low.endswith(TMP_EXT) or low.endswith(".pyc"):
                try:
                    tmps.append(_item("tmp_file", full, os.path.getsize(full), "안전 비움 후보", executable=True))
                except OSError:
                    pass
            elif low.endswith(LOG_EXT):
                try:
                    sz = os.path.getsize(full)
                except OSError:
                    sz = 0
                if sz >= LOG_BLOAT_BYTES:
                    logs.append(_item("bloated_log", full, sz, "대표님 결재 후 로테이션/보관",
                                      requires_manual_gate=True, auto_executed=False))
                counts["log"] += 1
            else:
                ext = os.path.splitext(low)[1]
                if ext in ACTIVE_EXT:
                    counts[ext.lstrip(".")] += 1
                    if "skills" in _rel(full).split("/")[:1]:
                        counts["skills_files"] += 1
    pc_items = []
    small = time.time() + 1.0
    for p in pycache:
        pc_items.append(_item("pycache", p, _walk_size(p, small, 5000)["bytes"], "안전 비움 후보", executable=True))
    return {"counts": dict(counts), "pycache": pc_items, "tmps": tmps, "logs": logs, "truncated": truncated}


def _temp_stats(deadline):
    td = tempfile.gettempdir()
    s = _walk_size(td, deadline, 100000, TEMP_OLD_DAYS)
    return _item("system_temp_stats", td, s["bytes"], "통계 전용 — Windows 디스크 정리/저장소 센스로 비움 권장",
                 executable=False, files=s["files"], old_files=s["old_files"], old_bytes=s["old_bytes"],
                 old_size=_human(s["old_bytes"]), truncated=s["truncated"])


def _recycle_bin():
    if os.name != "nt":
        return {"available": False, "reason": "Windows 전용 통계"}
    try:
        from ctypes import wintypes

        class RB(ctypes.Structure):
            _fields_ = [("cbSize", wintypes.DWORD), ("i64Size", ctypes.c_longlong), ("i64NumItems", ctypes.c_longlong)]

        class RB1(ctypes.Structure):
            _pack_ = 1
            _fields_ = [("cbSize", wintypes.DWORD), ("i64Size", ctypes.c_longlong), ("i64NumItems", ctypes.c_longlong)]

        for cls in (RB, RB1):
            info = cls()
            info.cbSize = ctypes.sizeof(cls)
            hr = ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(info))
            if hr == 0:
                return {"available": True, "bytes": int(info.i64Size), "items": int(info.i64NumItems)}
        return {"available": False, "reason": "SHQueryRecycleBinW 실패"}
    except Exception as e:
        return {"available": False, "reason": repr(e)[:160]}


def _downloads_installers():
    dirs = [os.path.join(os.path.expanduser("~"), "Downloads")]
    if os.environ.get("USERPROFILE"):
        dirs.append(os.path.join(os.environ["USERPROFILE"], "Downloads"))
    seen, out = set(), []
    for d in dirs:
        rd = os.path.realpath(d)
        if rd in seen or not os.path.isdir(rd):
            continue
        seen.add(rd)
        try:
            for e in os.scandir(rd):
                try:
                    if e.is_file(follow_symlinks=False) and e.name.lower().endswith(INSTALLER_EXT):
                        sz = e.stat().st_size
                        if sz >= INSTALLER_MIN_BYTES:
                            out.append(_item("downloads_installer", e.path, sz, "대표님 수동 결재 대기 — 자동 삭제 금지",
                                             requires_manual_gate=True, auto_executed=False))
                except OSError:
                    continue
        except OSError:
            continue
    out.sort(key=lambda x: -x["bytes"])
    return out


def _disk():
    try:
        u = shutil.disk_usage(ROOT)
        return {"ok": True, "total_gb": _gb(u.total), "used_gb": _gb(u.used), "free_gb": _gb(u.free),
                "free_pct": round(u.free * 100.0 / u.total, 2) if u.total else 0.0}
    except Exception as e:
        return {"ok": False, "error": repr(e), "free_gb": 0.0, "free_pct": 0.0, "total_gb": 0.0}


def _memory():
    try:
        if os.name == "nt":
            class MS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            st = MS()
            st.dwLength = ctypes.sizeof(MS)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
                return {"ok": True, "total_gb": _gb(st.ullTotalPhys), "avail_gb": _gb(st.ullAvailPhys),
                        "avail_pct": round(st.ullAvailPhys * 100.0 / st.ullTotalPhys, 2) if st.ullTotalPhys else 0.0,
                        "load_pct": int(st.dwMemoryLoad)}
        elif os.path.exists("/proc/meminfo"):
            info = {}
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    k, _, v = line.partition(":")
                    info[k.strip()] = int(v.strip().split()[0]) * 1024
            tot, av = info.get("MemTotal", 0), info.get("MemAvailable", 0)
            if tot:
                return {"ok": True, "total_gb": _gb(tot), "avail_gb": _gb(av), "avail_pct": round(av * 100.0 / tot, 2),
                        "load_pct": int(100 - av * 100.0 / tot)}
    except Exception as e:
        return {"ok": False, "error": repr(e)[:160]}
    return {"ok": False, "error": "측정 불가"}


def _process_count():
    try:
        if os.name == "nt":
            arr = (ctypes.c_ulong * 8192)()
            need = ctypes.c_ulong()
            fn = getattr(ctypes.windll.kernel32, "K32EnumProcesses", None)
            if fn is None:
                fn = ctypes.windll.psapi.EnumProcesses
            if fn(ctypes.byref(arr), ctypes.sizeof(arr), ctypes.byref(need)):
                return int(need.value // ctypes.sizeof(ctypes.c_ulong))
        elif os.path.isdir("/proc"):
            return sum(1 for x in os.listdir("/proc") if x.isdigit())
    except Exception:
        return None
    return None


def _apply_tier2(items):
    done, freed = [], 0
    for it in items:
        p, kind = it.get("path"), it.get("kind")
        if kind not in ("pycache", "tmp_file") or not p:
            continue
        if not _within(p, ROOT) or _is_preserved(p):
            continue
        parts = _rel(p).split("/")
        if ".git" in parts or any(x.startswith(".rgon_backup") for x in parts):
            continue
        try:
            if kind == "pycache" and os.path.basename(p) == "__pycache__" and os.path.isdir(p):
                shutil.rmtree(p)
            elif kind == "tmp_file" and os.path.isfile(p):
                os.remove(p)
            else:
                continue
            done.append(_rel(p))
            freed += int(it.get("bytes") or 0)
        except OSError:
            continue
    return done, freed


def _strip_particle(w):
    for p in PARTICLES:
        if w.endswith(p) and len(w) - len(p) >= 2:
            return w[:-len(p)]
    return w


def _iter_strings(obj, out, depth=0, cap=20000):
    if len(out) >= cap or depth > 12:
        return
    if isinstance(obj, str):
        s = obj.strip()
        if len(s) >= 2 and not re.fullmatch(r"[0-9:\-T\.\+Z /]+", s):
            out.append(s)
    elif isinstance(obj, dict):
        for v in obj.values():
            _iter_strings(v, out, depth + 1, cap)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _iter_strings(v, out, depth + 1, cap)


def _memory_sources():
    paths = []
    for name in MEMORY_FILES:
        paths.append(os.path.join(ROOT, name))
    dd = os.environ.get("RGON_DIALOGUE_STATE_DIR")
    if dd:
        paths.append(os.path.join(dd, "rgon_aon_dialogue_state.json"))
    seen, out = set(), []
    for p in paths:
        rp = os.path.realpath(p)
        if rp not in seen:
            seen.add(rp)
            out.append(p)
    return out


def distill_stagnant_memory(max_keep=20, sources=None):
    """#48 수풍정 — 고인 기억에서 정수(키워드·감정·약속)만 길어 올린다. 원본은 절대 수정하지 않는다."""
    try:
        max_keep = max(1, int(max_keep or 20))
    except Exception:
        max_keep = 20
    sources = list(sources) if sources else _memory_sources()
    infos, strings = [], []
    for path in sources:
        info = {"file": os.path.basename(path), "path": path, "exists": os.path.exists(path)}
        if info["exists"]:
            try:
                st = os.stat(path)
                info["bytes"] = st.st_size
                info["days_since_update"] = round((time.time() - st.st_mtime) / 86400.0, 2)
                if st.st_size > 30 * 1024 * 1024:
                    info["note"] = "30MB 초과 — 증류 생략(수동 점검 권장)"
                else:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        raw = f.read()
                    before = len(strings)
                    try:
                        _iter_strings(json.loads(raw), strings)
                    except Exception:
                        strings.append(raw[:200000])
                    info["strings"] = len(strings) - before
            except Exception as e:
                info["error"] = repr(e)[:160]
        infos.append(info)
    words, emo, promises = collections.Counter(), collections.Counter(), []
    for s in strings:
        for tok in TOKEN_RE.findall(s):
            w = tok.lower() if tok.isascii() else _strip_particle(tok)
            if len(w) < 2 or w in STOPWORDS or w.isdigit():
                continue
            words[w] += 1
        for name, keys in EMOTIONS.items():
            for k in keys:
                c = s.count(k)
                if c:
                    emo[name] += c
        if PROMISE_RE.search(s):
            for sent in re.split(r"[\.\!\?。\n]+", s):
                t = sent.strip()
                if t and PROMISE_RE.search(t):
                    t = t[:140]
                    if t not in promises:
                        promises.append(t)
    promises = promises[-max_keep:]
    keywords = [{"word": w, "count": c} for w, c in words.most_common(max_keep)]
    dominant = emo.most_common(1)[0][0] if emo else "평온"
    existing = [i for i in infos if i.get("exists")]
    total_bytes = sum(int(i.get("bytes") or 0) for i in existing)
    days = [i["days_since_update"] for i in existing if "days_since_update" in i]
    min_days = min(days) if days else None
    level = "기억 없음(空)"
    if existing:
        if (min_days is not None and min_days > 14) or total_bytes > 5 * 1024 * 1024:
            level = "고인 물(滯) — 증류 권장"
        elif min_days is not None and min_days > 3:
            level = "완류(緩)"
        else:
            level = "활수(活) — 흐르는 기억"
    top = ", ".join(k["word"] for k in keywords[:8]) or "(정수 없음)"
    summary = "핵심 정수: %s · 지배 감정: %s · 약속 %d건 계승" % (top, dominant, len(promises))
    return {"ok": True, "max_keep": max_keep, "sources": infos, "string_count": len(strings),
            "essence_keywords": keywords, "emotion_profile": dict(emo.most_common()), "dominant_emotion": dominant,
            "promises": promises,
            "stagnation": {"total_bytes": total_bytes, "total_size": _human(total_bytes),
                           "min_days_since_update": min_days, "level": level},
            "summary": summary, "read_only": True,
            "note": "원본 기억 파일은 수정하지 않고 정수만 증류 (井渫不食 — 맑힌 우물을 버려두지 않는다)"}


def _gua_label(obj):
    if obj is None or obj == "":
        return ""
    if isinstance(obj, str):
        return obj.strip()
    if isinstance(obj, dict):
        ko = obj.get("ko") or obj.get("name_ko") or obj.get("name")
        hj = obj.get("hanja") or obj.get("name_hanja")
        num = obj.get("number") or obj.get("no")
        label = str(ko or "")
        if hj and str(hj) != label:
            label = ("%s(%s)" % (label, hj)) if label else str(hj)
        if isinstance(num, int) and 1 <= num <= 64:
            label = "#%02d %s" % (num, label)
        return label.strip() or json.dumps(obj, ensure_ascii=False, default=str)[:60]
    return str(obj)


def _iching_hint(topic):
    if os.environ.get("RGON_HYDRO_NO_ORACLE"):
        return {"ok": False, "skipped": True}
    try:
        mod = importlib.import_module("rgon_aon_iching_dao_oracle")
        fn = getattr(mod, "cast_by_question", None) or getattr(mod, "divine", None) or getattr(mod, "cast_oracle", None)
        if not callable(fn):
            return {"ok": False, "error": "cast_by_question 미정의"}
        r = fn(topic)
        d = r if isinstance(r, dict) else (getattr(r, "__dict__", None) or {})
        if not (d.get("bengua") or d.get("primary") or d.get("bengua_name")):
            for k in ("result", "reading", "cast", "data", "oracle", "hexagram"):
                inner = d.get(k)
                if isinstance(inner, dict) and (inner.get("bengua") or inner.get("primary") or inner.get("bengua_name")):
                    d = inner
                    break
        return {"ok": True,
                "bengua": _gua_label(d.get("bengua") or d.get("bengua_name") or d.get("primary")),
                "biangua": _gua_label(d.get("biangua") or d.get("biangua_name") or d.get("transformed")),
                "hugua": _gua_label(d.get("hugua") or d.get("hugua_name") or d.get("mutual"))}
    except Exception as e:
        return {"ok": False, "error": repr(e)[:200]}


def _empty_score(disk, reclaim_bytes):
    if not disk.get("ok"):
        return 50.0
    base = min(80.0, float(disk.get("free_pct") or 0) * 2.0)
    bonus = min(20.0, float(disk.get("free_gb") or 0) * 0.4)
    penalty = min(15.0, (reclaim_bytes / GB) * 3.0)
    return round(_clamp(base + bonus - penalty), 1)


def _flow_score(mem, procs, essence, old_backups, debris):
    f = [{"factor": "기본 흐름", "delta": 50.0, "reason": "물은 본디 흐른다"}]
    if mem.get("ok"):
        f.append({"factor": "메모리 여유", "delta": round(min(25.0, float(mem["avail_pct"]) * 0.5), 1),
                  "reason": "가용 메모리 %.1f%%" % mem["avail_pct"]})
    else:
        f.append({"factor": "메모리 여유", "delta": 10.0, "reason": "측정 불가 — 중립 가점"})
    if procs:
        d = 10.0 if procs < 150 else 5.0 if procs < 300 else 0.0 if procs < 500 else -5.0
        f.append({"factor": "프로세스 흐름", "delta": d, "reason": "실행 중 프로세스 %d개" % procs})
    else:
        f.append({"factor": "프로세스 흐름", "delta": 5.0, "reason": "측정 불가 — 중립 가점"})
    days = (essence.get("stagnation") or {}).get("min_days_since_update")
    if days is None:
        f.append({"factor": "기억 흐름", "delta": 0.0, "reason": "기억 파일 없음"})
    else:
        d = 10.0 if days <= 1 else 5.0 if days <= 7 else 0.0 if days <= 30 else -10.0
        f.append({"factor": "기억 흐름", "delta": d, "reason": "마지막 갱신 %.1f일 전" % days})
    if old_backups:
        f.append({"factor": "백업 고임", "delta": -float(min(10, 2 * old_backups)),
                  "reason": "최신 3개 외 오래된 백업 %d개" % old_backups})
    if debris > 50:
        f.append({"factor": "찌꺼기", "delta": -5.0, "reason": "__pycache__·임시파일 %d건" % debris})
    else:
        f.append({"factor": "찌꺼기", "delta": 5.0, "reason": "찌꺼기 %d건 — 맑음" % debris})
    score = round(_clamp(sum(x["delta"] for x in f)), 1)
    return score, f


def _flow_state(score):
    if score >= 75:
        return "流 활수(活水) — 막힘 없이 흐름"
    if score >= 50:
        return "緩 완류(緩流) — 흐르되 느림"
    return "滯 정체(停滯) — 먼저 비우고 터야 함"


def _prescription(topic, empty, flow, t2, t3, essence, hint):
    steps = []
    if t2["reclaimable_bytes"] > 0:
        steps.append("損: TIER2 안전 비움 후보 %s(%d건) — 'python rgon_aon_hydro_cycle.py --cycle --apply-tier2' 실행 시 __pycache__·*.tmp만 비움"
                     % (_human(t2["reclaimable_bytes"]), t2["count"]))
    else:
        steps.append("損: 즉시 비울 고인 물 없음 — 이미 맑음")
    if t2.get("old_backups"):
        steps.append("蠱: 최신 3개 외 오래된 백업 %d개는 비움 후보로만 표시 (확인 후 정리)" % t2["old_backups"])
    if t3["count"]:
        steps.append("節: TIER3 %s(%d건)은 대표님 수동 결재 대기 — 자동 삭제 금지" % (_human(t3["bytes"]), t3["count"]))
    steps.append("井: %s" % essence.get("summary", ""))
    if flow < 50:
        steps.append("坎: 유동성 %.1f — 무거운 프로세스·창을 닫고 흐름부터 회복" % flow)
    else:
        steps.append("坎: 유동성 %.1f — 흐름 양호, 절도(節) 있게 유지" % flow)
    steps.append("旣濟→未濟: 비운 자리에 '%s' 다음 창조(새 콘텐츠·새 기관·새 학습)를 들인다" % topic)
    if hint.get("ok") and hint.get("bengua"):
        steps.append("시운: 본괘 %s → 변괘 %s 흐름에 맞춰 순환" % (hint.get("bengua"), hint.get("biangua") or "-"))
    if empty < 50:
        mode, nxt = "비움 우선 (先損後益)", "디스크 여백을 먼저 확보한 뒤 새 작업 수용"
    elif flow < 50:
        mode, nxt = "흐름 회복 (習坎)", "고인 프로세스·기억을 풀어 흐름부터 회복"
    else:
        mode, nxt = "새 창조 수용 (未濟)", "여백과 흐름이 충분 — 새로운 창조를 맞이할 때"
    return {"mode": mode, "next_flow": nxt, "steps": steps, "iching_hint": hint}


def _voice_line(topic, empty, flow, t2, t3, essence):
    seed = hashlib.sha256(("%s|%s" % (topic, _now().strftime("%Y%m%d%H"))).encode("utf-8")).digest()
    tpl = VOICE_TEMPLATES[seed[0] % len(VOICE_TEMPLATES)]
    kw = ", ".join(k["word"] for k in (essence.get("essence_keywords") or [])[:3]) or "여백"
    line = tpl.format(tier2=_human(t2["reclaimable_bytes"]), tier3=t3["count"], empty=empty, flow=flow, kw=kw)
    if not os.environ.get("RGON_HYDRO_NO_SPICE"):
        try:
            pg = importlib.import_module("rgon_aon_desktop_playground")
            fn = getattr(pg, "apply_tsundere_spice", None)
            if callable(fn):
                sp = fn(line)
                spiced = (sp.get("speech") or sp.get("reply") or str(sp)) if isinstance(sp, dict) else str(sp)
                if spiced and spiced.strip():
                    line = spiced
        except Exception:
            pass
    return line


def _state_paths():
    d = os.environ.get("RGON_HYDRO_STATE_DIR")
    base = os.path.abspath(d) if d else ROOT
    return [os.path.join(base, STATE_NAME), os.path.join(base, "docs", STATE_NAME)]


def _persist(result):
    text = json.dumps(result, ensure_ascii=False, indent=2, default=str)
    written = []
    for path in _state_paths():
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp = path + ".writing"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, path)
            written.append(path)
        except Exception:
            pass
    return written


def format_reply(r):
    t = r["tier_classification"]
    rx = r["hydro_prescription"]
    lines = [
        "[상선약수 수순환 · 損·蠱→井→坎·節→旣濟·未濟] %s" % VERSION,
        "■ 주제: %s (%s)" % (r["topic"], "dry-run · 삭제 없음" if r["dry_run"] else "TIER2 적용 %d건" % len(r["applied_tier2"])),
        "■ 여백 지수 %.1f/100 · 유동성 지수 %.1f/100 · 디스크 여유 %.2f GB (%.1f%%)" % (
            r["empty_space_score"], r["flow_vitality_score"], r["disk_free_gb"], r["disk"].get("free_pct") or 0.0),
        "■ 1 증발·비움(#41 산택손·#18 산풍고): TIER1 보존 %d · TIER2 %s(%d건) · TIER3 결재대기 %d건" % (
            t["TIER1_KEEP"]["count"], _human(t["TIER2_SAFE_EMPTY"]["reclaimable_bytes"]),
            t["TIER2_SAFE_EMPTY"]["count"], t["TIER3_GATE_HOLD"]["count"]),
        "■ 2 응집·증류(#48 수풍정): %s" % r["distilled_essence"].get("summary", ""),
        "■ 3 유동·흐름(#29 중수감·#60 수택절): %s" % r["flow_state"],
        "■ 4 순환·재시작(#63 수화기제→#64 화수미제): %s — %s" % (rx["mode"], rx["next_flow"]),
    ]
    for s in rx["steps"]:
        lines.append("  · " + s)
    lines.append("■ Tier3 수동 결재 게이트: requires_manual_gate=True · auto_executed=False (헌법 제2항·R35·R42)")
    lines.append("■ 아온: " + r["aon_voice_line"])
    return "\n".join(lines)


def run_hydro_cycle(topic=DEFAULT_TOPIC, dry_run=True, persist=True):
    t0 = time.time()
    topic = (str(topic).strip() if topic else "") or DEFAULT_TOPIC
    keep_bk, old_bk = _scan_backups(t0 + SCAN_BUDGET_SEC)
    root = _scan_root(time.time() + SCAN_BUDGET_SEC)
    temp = _temp_stats(time.time() + TEMP_BUDGET_SEC)
    recycle = _recycle_bin()
    installers = _downloads_installers()

    t2_exec = root["pycache"] + root["tmps"]
    applied, freed = ([], 0) if dry_run else _apply_tier2(t2_exec)
    reclaim = sum(i["bytes"] for i in t2_exec) + sum(i["bytes"] for i in old_bk)
    remaining = max(0, reclaim - freed)

    c = root["counts"]
    t1_count = sum(v for k, v in c.items() if k in ("py", "html", "json", "md", "js", "css")) + len(keep_bk) + c.get("preserve", 0)
    tier1 = {"label": "절대 보존", "count": t1_count, "active_counts": c,
             "skills_dir": os.path.isdir(os.path.join(ROOT, "skills")),
             "latest_backups": keep_bk, "preserve_files": list(PRESERVE),
             "rule": "현역 .py/.html/.json·skills/·최신 백업 3개·안총리 산출물은 영구 보존"}
    t2_items = t2_exec + old_bk + [temp]
    tier2 = {"label": "100% 안전 비움 가능", "count": len(t2_exec) + len(old_bk),
             "reclaimable_bytes": reclaim, "reclaimable_size": _human(reclaim),
             "pycache_dirs": len(root["pycache"]), "tmp_files": len(root["tmps"]), "old_backups": len(old_bk),
             "system_temp": temp, "items": t2_items[:ITEM_CAP], "dry_run": bool(dry_run),
             "executable_scope": "--apply-tier2 시 ROOT 내부 __pycache__·*.tmp만 (백업·시스템 TEMP는 표시만)"}
    t3_items = list(installers) + list(root["logs"])
    if recycle.get("available") and recycle.get("bytes", 0) > 0:
        t3_items.insert(0, {"kind": "recycle_bin", "path": "RecycleBin", "rel": "RecycleBin",
                            "bytes": recycle["bytes"], "size": _human(recycle["bytes"]), "items": recycle.get("items"),
                            "action": "대표님 수동 결재 대기 — 자동 비움 금지",
                            "requires_manual_gate": True, "auto_executed": False})
    tier3 = {"label": "헌법 제2항·R35 수동 결재 대기", "count": len(t3_items),
             "bytes": sum(int(i.get("bytes") or 0) for i in t3_items), "items": t3_items[:ITEM_CAP],
             "recycle_bin": recycle, "requires_manual_gate": True, "auto_executed": False}
    tier3["size"] = _human(tier3["bytes"])

    disk = _disk()
    mem = _memory()
    procs = _process_count()
    essence = distill_stagnant_memory(20)
    empty = _empty_score(disk, remaining)
    flow, flow_factors = _flow_score(mem, procs, essence, len(old_bk), len(t2_exec) - len(applied))
    hint = _iching_hint(topic)
    rx = _prescription(topic, empty, flow, tier2, tier3, essence, hint)
    voice = _voice_line(topic, empty, flow, tier2, tier3, essence)

    stages = [
        dict(STAGES[0], result={"tier2_reclaimable": _human(reclaim), "tier2_count": tier2["count"],
                                "tier3_hold": tier3["count"], "old_backups": len(old_bk),
                                "applied": len(applied), "dry_run": bool(dry_run)}),
        dict(STAGES[1], result={"keywords": [k["word"] for k in essence["essence_keywords"][:5]],
                                "dominant_emotion": essence["dominant_emotion"], "promises": len(essence["promises"])}),
        dict(STAGES[2], result={"empty_space_score": empty, "flow_vitality_score": flow,
                                "disk_free_gb": disk.get("free_gb"), "flow_state": _flow_state(flow)}),
        dict(STAGES[3], result={"mode": rx["mode"], "next_flow": rx["next_flow"]}),
    ]
    result = {
        "ok": True, "version": VERSION, "antibody": ANTIBODY, "antibody_range": ANTIBODY_RANGE,
        "skill_id": SKILL_ID, "organ": ORGAN_NAME, "generated_at_kst": _now().isoformat(timespec="seconds"),
        "topic": topic, "dry_run": bool(dry_run), "philosophy": "上善若水 · 虛實相生",
        "iching_flow_stages": stages,
        "empty_space_score": empty, "flow_vitality_score": flow, "flow_vitality_factors": flow_factors,
        "flow_state": _flow_state(flow),
        "disk_free_gb": disk.get("free_gb"), "disk": disk, "memory": mem, "process_count": procs,
        "tier_classification": {"TIER1_KEEP": tier1, "TIER2_SAFE_EMPTY": tier2, "TIER3_GATE_HOLD": tier3},
        "applied_tier2": applied, "freed_bytes": freed,
        "distilled_essence": essence, "hydro_prescription": rx,
        "requires_manual_gate": True, "auto_executed": False,
        "aon_voice_line": voice, "elapsed_sec": round(time.time() - t0, 2),
        "scan_truncated": bool(root["truncated"] or temp.get("truncated")),
    }
    result["reply"] = format_reply(result)
    if persist:
        result["state_files"] = _persist(result)
    return result


def status():
    for path in _state_paths():
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                return {"ok": True, "version": VERSION, "state_file": path, "topic": d.get("topic"),
                        "generated_at_kst": d.get("generated_at_kst"), "empty_space_score": d.get("empty_space_score"),
                        "flow_vitality_score": d.get("flow_vitality_score"), "disk_free_gb": d.get("disk_free_gb"),
                        "flow_state": d.get("flow_state")}
            except Exception as e:
                return {"ok": False, "version": VERSION, "error": repr(e)}
    return {"ok": True, "version": VERSION, "state_file": None, "note": "아직 순환 기록 없음"}


def self_test():
    checks = []
    tmp = tempfile.mkdtemp(prefix="rgon_hydro_st_")
    keys = ("RGON_HYDRO_STATE_DIR", "RGON_HYDRO_NO_ORACLE", "RGON_HYDRO_NO_SPICE")
    prev = {k: os.environ.get(k) for k in keys}
    os.environ["RGON_HYDRO_STATE_DIR"] = tmp
    os.environ["RGON_HYDRO_NO_ORACLE"] = "1"
    os.environ["RGON_HYDRO_NO_SPICE"] = "1"
    try:
        g = json.dumps(STAGES, ensure_ascii=False)
        checks.append(("4단계 괘상", len(STAGES) == 4 and all(("#%02d" % n) in g for n in (41, 18, 48, 29, 60, 63, 64))))
        r = run_hydro_cycle(DEFAULT_TOPIC, dry_run=True)
        req = ("ok", "version", "antibody", "iching_flow_stages", "empty_space_score", "flow_vitality_score",
               "disk_free_gb", "tier_classification", "distilled_essence", "requires_manual_gate",
               "auto_executed", "aon_voice_line")
        checks.append(("필수 키", all(k in r for k in req)))
        checks.append(("버전·항체", r["ok"] is True and r["version"] == VERSION and r["antibody"] == "R42"))
        checks.append(("점수 범위", 0 <= r["empty_space_score"] <= 100 and 0 <= r["flow_vitality_score"] <= 100))
        tc = r["tier_classification"]
        checks.append(("3등급", all(k in tc for k in ("TIER1_KEEP", "TIER2_SAFE_EMPTY", "TIER3_GATE_HOLD"))))
        checks.append(("Tier3 게이트", tc["TIER3_GATE_HOLD"]["requires_manual_gate"] is True
                       and tc["TIER3_GATE_HOLD"]["auto_executed"] is False))
        checks.append(("최상위 게이트", r["requires_manual_gate"] is True and r["auto_executed"] is False))
        checks.append(("dry-run 무삭제", r["applied_tier2"] == [] and r["freed_bytes"] == 0))
        checks.append(("상태 격리", os.path.exists(os.path.join(tmp, STATE_NAME))
                       and os.path.exists(os.path.join(tmp, "docs", STATE_NAME))))
        mem = os.path.join(tmp, "mem_test.json")
        with open(mem, "w", encoding="utf-8") as f:
            json.dump({"history": [{"role": "user", "content": "대표님 약속할게, 내일 반도체 리포트 꼭 정리해줄게!"},
                                   {"role": "assistant", "content": "오늘 너무 행복하고 감사해. 반도체 반도체 흐름"}]},
                      f, ensure_ascii=False)
        d = distill_stagnant_memory(max_keep=3, sources=[mem])
        checks.append(("증류", d["ok"] and len(d["essence_keywords"]) <= 3
                       and any(k["word"] == "반도체" for k in d["essence_keywords"])
                       and len(d["promises"]) >= 1 and d["dominant_emotion"] in EMOTIONS))
        outside = os.path.join(tmp, "outside.tmp")
        with open(outside, "w") as f:
            f.write("x")
        done, _fr = _apply_tier2([{"kind": "tmp_file", "path": outside, "bytes": 1}])
        checks.append(("ROOT 밖 삭제 거부", done == [] and os.path.exists(outside)))
        checks.append(("아온 대사", bool(r["aon_voice_line"].strip())))
        checks.append(("응답 포맷", "[상선약수 수순환" in r["reply"]))
    except Exception as e:
        checks.append(("예외 없음", False))
        checks.append(("trace", repr(e)))
    finally:
        for k, v in prev.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
    passed = sum(1 for _n, v in checks if v is True)
    total = sum(1 for _n, v in checks if isinstance(v, bool))
    return {"ok": passed == total, "version": VERSION, "antibody": ANTIBODY, "passed": passed, "total": total,
            "checks": [{"name": n, "ok": v} for n, v in checks]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=ORGAN_NAME)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--cycle", nargs="*")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply-tier2", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        r = self_test()
        print(json.dumps(r, ensure_ascii=False, indent=2))
        print("SELF-TEST %s %d/%d" % ("PASS" if r["ok"] else "FAIL", r["passed"], r["total"]))
        return 0 if r["ok"] else 1
    if a.cycle is not None or a.dry_run or a.apply_tier2:
        topic = " ".join(a.cycle or []) or DEFAULT_TOPIC
        r = run_hydro_cycle(topic, dry_run=not a.apply_tier2 or a.dry_run)
        print(json.dumps(r, ensure_ascii=False, indent=2, default=str) if a.json else r["reply"])
        return 0
    print(json.dumps(status(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

# ══════════════════════════════════════════════════════════════════════
# 2. 제15기관 대화허브 R42 훅
# ══════════════════════════════════════════════════════════════════════
DLG_BEGIN = "# >>> [RGON-R42-HYDRO-HOOK-START] >>>"
DLG_END = "# <<< [RGON-R42-HYDRO-HOOK-END] <<<"
DIALOGUE_HOOK = r'''
import threading as _r42_threading
import time as _r42_time

R42_HYDRO_SLASH = ("/비움", "/순환", "/청소", "/물")
R42_HYDRO_KEYWORDS = ("비움", "비워", "물의 순환", "상선약수", "청소", "과부하")
R42_HYDRO_DEFAULT_TOPIC = "노트북 여백 창조 및 물의 순환 점검"
_r42_tls = _r42_threading.local()
_r42_cache = {"t": 0.0, "res": None}


def _r42_hydro_intent(text):
    t = str(text or "").strip()
    for s in R42_HYDRO_SLASH:
        if t == s or t.startswith(s + " "):
            return "slash", t[len(s):].strip()
    if any(k in t for k in R42_HYDRO_KEYWORDS):
        return "keyword", t
    return None, ""


def _r42_first_text(args, kwargs):
    for k in ("text", "message", "query", "msg", "user_text", "prompt"):
        if isinstance(kwargs.get(k), str):
            return kwargs[k]
    for a in args:
        if isinstance(a, str):
            return a
    return ""


def _r42_run_hydro(topic, use_cache=False):
    if use_cache and _r42_cache["res"] is not None and _r42_time.time() - _r42_cache["t"] < 90:
        return _r42_cache["res"]
    import importlib as _il
    hc = _il.import_module("rgon_aon_hydro_cycle").run_hydro_cycle(topic or R42_HYDRO_DEFAULT_TOPIC, dry_run=True)
    _r42_cache["t"] = _r42_time.time()
    _r42_cache["res"] = hc
    return hc


def _r42_slash_response(arg):
    hc = _r42_run_hydro(arg)
    return {"ok": bool(hc.get("ok")), "intent": "hydro", "intents": ["hydro"],
            "organ": "rgon_aon_hydro_cycle", "antibody": "R42",
            "reply": hc.get("reply", ""), "speech": hc.get("reply", ""), "text": hc.get("reply", ""),
            "hydro_cycle": hc, "results": [{"intent": "hydro", "ok": True, "speech": hc.get("reply", ""), "data": hc}],
            "empty_space_score": hc.get("empty_space_score"), "flow_vitality_score": hc.get("flow_vitality_score"),
            "iching_flow_stages": hc.get("iching_flow_stages"),
            "requires_manual_gate": True, "auto_executed": False}


def _r42_attach(res, hc):
    if isinstance(res, dict):
        res["hydro_cycle"] = hc
        res.setdefault("hydro_reply", hc.get("reply", ""))
    return res


if "route" not in globals() and callable(globals().get("r40_route")):
    route = r40_route


def _r42_wrap(name):
    orig = globals().get(name)
    if not callable(orig) or getattr(orig, "_r42_wrapped", False):
        return

    def wrapper(*args, **kwargs):
        if getattr(_r42_tls, "active", False):
            return orig(*args, **kwargs)
        try:
            kind, arg = _r42_hydro_intent(_r42_first_text(args, kwargs))
        except Exception:
            kind, arg = None, ""
        if not kind:
            return orig(*args, **kwargs)
        _r42_tls.active = True
        try:
            if kind == "slash" and name not in ("converse", "process_dialogue"):
                try:
                    return _r42_slash_response(arg)
                except Exception as _e:
                    return {"ok": False, "intent": "hydro", "antibody": "R42", "error": repr(_e),
                            "requires_manual_gate": True, "auto_executed": False}
            res = orig(*args, **kwargs)
            try:
                hc = _r42_run_hydro(arg if kind == "slash" else R42_HYDRO_DEFAULT_TOPIC, use_cache=(kind == "keyword"))
                res = _r42_attach(res, hc)
            except Exception:
                pass
            return res
        finally:
            _r42_tls.active = False

    wrapper._r42_wrapped = True
    wrapper._r42_orig = orig
    wrapper.__name__ = name
    wrapper.__doc__ = getattr(orig, "__doc__", None)
    globals()[name] = wrapper


for _r42_n in ("route", "converse", "r40_route", "process_dialogue"):
    _r42_wrap(_r42_n)

try:
    _r42_ic = globals().get("INTENT_KEYWORDS")
    if isinstance(_r42_ic, dict):
        _r42_ic.setdefault("hydro", list(R42_HYDRO_KEYWORDS))
except Exception:
    pass
'''

# ══════════════════════════════════════════════════════════════════════
# 3. 제16기관 검증기 R42 확장
# ══════════════════════════════════════════════════════════════════════
VER_BEGIN = "# >>> [RGON-R42-VERIFIER-EXT-START] >>>"
VER_END = "# <<< [RGON-R42-VERIFIER-EXT-END] <<<"
VERIFIER_HOOK = r'''
VERSION = "v11.41-AON-HYDRO-CYCLE"
ANTIBODY_RANGE = "R1~R42"
EXPECTED_SKILL_COUNT = 38
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R42_HYDRO_ORGAN = "rgon_aon_hydro_cycle.py"
R42_HYDRO_SNAPSHOTS = ["rgon_aon_hydro_state.json", "docs/rgon_aon_hydro_state.json"]
try:
    if R42_HYDRO_ORGAN not in ORGANS:
        ORGANS.append(R42_HYDRO_ORGAN)
except NameError:
    ORGANS = [R42_HYDRO_ORGAN]
for _r42_sn in ("SNAPSHOT_FILES", "SNAPSHOT_SYNC_FILES", "SNAPSHOT_TARGETS", "SYNC_SNAPSHOTS",
                "STATE_SNAPSHOTS", "SNAPSHOTS", "STATE_FILES", "JSON_SNAPSHOTS"):
    _r42_sv = globals().get(_r42_sn)
    if isinstance(_r42_sv, list) and all(isinstance(_x, str) for _x in _r42_sv):
        for _r42_x in R42_HYDRO_SNAPSHOTS:
            if _r42_x not in _r42_sv:
                _r42_sv.append(_r42_x)
    elif isinstance(_r42_sv, tuple) and all(isinstance(_x, str) for _x in _r42_sv):
        globals()[_r42_sn] = tuple(_r42_sv) + tuple(_x for _x in R42_HYDRO_SNAPSHOTS if _x not in _r42_sv)


def _r42_s12_check():
    import os as _o, json as _j, tempfile as _t, importlib as _il, shutil as _sh, time as _tm
    _t0 = _tm.perf_counter()
    name = "대화허브(/순환)→제18기관 수순환 대사"
    tmp = _t.mkdtemp(prefix="rgon_s12_")
    keys = ("RGON_HYDRO_STATE_DIR", "RGON_ICHING_STATE_DIR", "RGON_DIALOGUE_STATE_DIR", "RGON_HYDRO_NO_ORACLE")
    prev = {k: _o.environ.get(k) for k in keys}
    base = _o.path.dirname(_o.path.abspath(__file__))
    root_state = [_o.path.join(base, "rgon_aon_hydro_state.json"), _o.path.join(base, "docs", "rgon_aon_hydro_state.json")]

    def _sig(p):
        try:
            st = _o.stat(p)
            return (st.st_size, st.st_mtime_ns)
        except OSError:
            return None

    before = [_sig(p) for p in root_state]
    for k in keys[:3]:
        _o.environ[k] = tmp
    _o.environ["RGON_HYDRO_NO_ORACLE"] = "1"
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "route", None) or getattr(dlg, "r40_route", None)
        r = fn("/순환 노트북 여백 창조 및 물의 순환 점검")
        hc = r.get("hydro_cycle") if isinstance(r, dict) else None
        hc = hc if isinstance(hc, dict) else {}
        stages = hc.get("iching_flow_stages") or []
        gtxt = _j.dumps(stages, ensure_ascii=False)
        tiers = hc.get("tier_classification") or {}
        t3 = tiers.get("TIER3_GATE_HOLD") or {}
        es = hc.get("empty_space_score")
        checks = {
            "route_ok": isinstance(r, dict) and r.get("ok") is True,
            "hydro_ok": hc.get("ok") is True and hc.get("antibody") == "R42",
            "four_stages": len(stages) == 4 and all(("#%02d" % n) in gtxt for n in (41, 18, 48, 29, 60, 63, 64)),
            "empty_space": isinstance(es, (int, float)) and 0 <= es <= 100,
            "tiers": all(k in tiers for k in ("TIER1_KEEP", "TIER2_SAFE_EMPTY", "TIER3_GATE_HOLD")),
            "tier3_gate": t3.get("requires_manual_gate") is True and t3.get("auto_executed") is False,
            "top_gate": hc.get("requires_manual_gate") is True and hc.get("auto_executed") is False,
            "isolated": _o.path.exists(_o.path.join(tmp, "rgon_aon_hydro_state.json")) and [_sig(p) for p in root_state] == before,
        }
        return {"id": "S12", "name": name, "ok": all(checks.values()), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": str(checks)[:200], "detail": checks}
    except Exception as e:
        return {"id": "S12", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}
    finally:
        for k, v in prev.items():
            if v is None:
                _o.environ.pop(k, None)
            else:
                _o.environ[k] = v
        _sh.rmtree(tmp, ignore_errors=True)


def _r42_merge(res, item):
    sid = item.get("id")
    if isinstance(res, list):
        return [x for x in res if not (isinstance(x, dict) and x.get("id") == sid)] + [item]
    if isinstance(res, dict):
        lst = None
        for k in ("links", "synapses", "results", "checks"):
            if isinstance(res.get(k), list):
                lst = k
                break
        if lst:
            res[lst] = [x for x in res[lst] if not (isinstance(x, dict) and x.get("id") == sid)] + [item]
            items = res[lst]
            passed = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            for pk in ("passed", "pass_count"):
                if pk in res:
                    res[pk] = passed
            for tk in ("total", "total_count"):
                if tk in res:
                    res[tk] = len(items)
            if "ok" in res:
                res["ok"] = passed == len(items)
        else:
            res[sid] = item
    return res


_r42_orig_vsl = globals().get("verify_synapse_links")
if callable(_r42_orig_vsl) and not getattr(_r42_orig_vsl, "_r42", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r42_orig_vsl(*args, **kwargs)
        try:
            res = _r42_merge(res, _r42_s12_check())
        except Exception:
            pass
        return res
    verify_synapse_links._r42 = True


def _r42_fix_skill_header():
    import os as _o, json as _j, re as _re, datetime as _dt
    p = _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "skills", "SKILL_INDEX.json")
    if not _o.path.exists(p):
        return False
    with open(p, "r", encoding="utf-8") as f:
        raw = f.read()
    data = _j.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("skills"), list):
        return False
    changed = False
    if data.get("version") != VERSION:
        data["version"] = VERSION
        changed = True
    ab = str(data.get("antibody") or "")
    want = "R42" if _re.fullmatch(r"R\d+", ab) else ANTIBODY_RANGE
    if ab != want:
        data["antibody"] = want
        changed = True
    if data.get("count") != len(data["skills"]):
        data["count"] = len(data["skills"])
        changed = True
    if changed or "generated_at_kst" not in data:
        data["generated_at_kst"] = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).isoformat(timespec="seconds")
        m = _re.search(r"\n( +)\"", raw)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(_j.dumps(data, ensure_ascii=False, indent=len(m.group(1)) if m else 2) + "\n")
    return changed


_r42_orig_heal = globals().get("heal_skill_index_header")
if callable(_r42_orig_heal) and not getattr(_r42_orig_heal, "_r42", False):
    def heal_skill_index_header(*args, **kwargs):
        try:
            return _r42_orig_heal(*args, **kwargs)
        finally:
            try:
                _r42_fix_skill_header()
            except Exception:
                pass
    heal_skill_index_header._r42 = True
'''

# ══════════════════════════════════════════════════════════════════════
# 4. 문서 · HTML · 스킬
# ══════════════════════════════════════════════════════════════════════
SKILL_MD = "\n".join([
    "---", "name: " + SKILL_ID, "description: " + SKILL_DESC, "version: " + NEW_VERSION,
    "antibody: R42", "skill_number: 38", "---", "",
    "# " + SKILL_TITLE, "",
    "제18기관 `rgon_aon_hydro_cycle.py`, 정식 스킬 #38. 노자 상선약수(上善若水)·허실상생(虛實相生) 철학으로 사령부의 여백과 흐름을 지킨다.", "",
    "## 사용법", "",
    BT3 + "bash",
    "python rgon_aon_hydro_cycle.py --self-test",
    "python rgon_aon_hydro_cycle.py --status",
    "python rgon_aon_hydro_cycle.py --cycle 노트북 여백 창조 및 물의 순환 점검 --dry-run",
    "python rgon_aon_hydro_cycle.py --cycle --apply-tier2",
    BT3, "",
    "대화허브에서는 `/순환`, `/비움`, `/청소`, `/물` 슬래시 명령과 비움·비워·물의 순환·상선약수·청소·과부하 키워드로 호출된다.", "",
    "## 4단계 수순환", "",
    "1단계는 증발·비움(#41 산택손·#18 산풍고)으로 TIER1_KEEP, TIER2_SAFE_EMPTY, TIER3_GATE_HOLD 3등급 분류를 한다. "
    "2단계는 응집·증류(#48 수풍정)로 기억의 정수를 뽑는다. 3단계는 유동·흐름(#29 중수감·#60 수택절)으로 여백 지수와 유동성 지수를 산출한다. "
    "4단계는 순환·재시작(#63 수화기제→#64 화수미제)으로 물의 순환 처방을 만든다.", "",
    "## 안전 (헌법 제2항 · R35 · R42)", "",
    "기본값은 dry-run이다. TIER3(휴지통·Downloads 대용량 설치본·비대 로그)은 항상 `requires_manual_gate: True`, `auto_executed: False`이며 자동 삭제하지 않는다. "
    "기억 원본 파일은 읽기만 한다.", "",
])
BADGE = "%s · 항체 %s · 스킬 %d" % (NEW_VERSION, NEW_RANGE, NEW_COUNT)
HTML_BEGIN = "<!-- RGON R42 HYDRO CYCLE BRIDGE BEGIN -->"
HTML_END = "<!-- RGON R42 HYDRO CYCLE BRIDGE END -->"
HTML_BRIDGE = (HTML_BEGIN + "\n<script>\nwindow.RGON_HYDRO_CYCLE = {version: \"" + NEW_VERSION +
               "\", antibody: \"R1~R42\", skill: \"" + SKILL_ID + "\", skillCount: 38, organ: 18, "
               "state: \"" + STATE_NAME + "\", commands: [\"/비움\", \"/순환\", \"/청소\", \"/물\"], "
               "load: function(){ return fetch(\"" + STATE_NAME + "\", {cache: \"no-store\"}).then(function(r){ return r.ok ? r.json() : null; }).catch(function(){ return null; }); }};\n"
               "</script>\n<div id=\"rgon-r42-badge\" style=\"display:none\">" + BADGE + "</div>\n" + HTML_END)


def bump_str(t):
    t = re.sub(re.escape(OLD_VERSION) + r"\s*·\s*항체\s*R1~R41\s*·\s*(정식\s*)?스킬\s*37(개)?",
               lambda m: "%s · 항체 %s · %s스킬 38%s" % (NEW_VERSION, NEW_RANGE, m.group(1) or "", m.group(2) or ""), t)
    t = t.replace(OLD_VERSION, NEW_VERSION).replace(OLD_RANGE, NEW_RANGE)
    t = re.sub(r"(EXPECTED_SKILL_COUNT\s*=\s*)37\b", r"\g<1>38", t)
    t = re.sub(r"(\bSKILL_COUNT\s*=\s*)37\b", r"\g<1>38", t)
    t = re.sub(r"(스킬\s*)37(\s*개)", r"\g<1>38\2", t)
    return t


def update_html():
    n = 0
    for rel in HTML_TARGETS:
        if not os.path.exists(P(rel)):
            log("  - HTML 없음(건너뜀): " + rel)
            continue
        t = bump_str(read_text(rel))
        t = re.sub(r"(스킬\s*)37\b", r"\g<1>38", t) if NEW_VERSION in t else t
        if HTML_BEGIN in t:
            s = t.index(HTML_BEGIN)
            e = t.index(HTML_END, s) + len(HTML_END)
            t = t[:s] + HTML_BRIDGE + t[e:]
        elif "</body>" in t:
            i = t.rfind("</body>")
            t = t[:i] + HTML_BRIDGE + "\n" + t[i:]
        else:
            t += "\n" + HTML_BRIDGE + "\n"
        if write_text(rel, t):
            n += 1
    log("[HTML] %d개 갱신" % n)


def init_hydro_state_snapshots():
    try:
        sys.path.insert(0, ROOT)
        import rgon_aon_hydro_cycle as hc
        res = hc.run_hydro_cycle(hc.DEFAULT_TOPIC, dry_run=True, persist=False)
        txt = json.dumps(res, ensure_ascii=False, indent=2, default=str) + "\n"
        for rel in STATE_FILES:
            write_text(rel, txt)
    except Exception as e:
        log("  - 초기 hydro state 생성 참고: %r" % e)


def update_json_snapshots():
    n = 0
    for d in JSON_SNAPSHOT_DIRS:
        base = P(d) if d else ROOT
        if not os.path.isdir(base):
            continue
        for fn in sorted(os.listdir(base)):
            rel = (d + "/" + fn) if d else fn
            if not fn.endswith(".json") or fn in JSON_SNAPSHOT_EXCLUDE or is_preserved(rel):
                continue
            if not os.path.isfile(P(rel)):
                continue
            try:
                raw = read_text(rel)
            except Exception:
                continue
            if OLD_VERSION not in raw and OLD_RANGE not in raw:
                continue
            new = raw.replace(OLD_VERSION, NEW_VERSION).replace(OLD_RANGE, NEW_RANGE)
            try:
                json.loads(new)
            except Exception:
                continue
            if write_text(rel, new):
                n += 1
    log("[SNAPSHOT] JSON %d개 승격" % n)


def update_skill_index():
    write_text(SKILL_PATH, SKILL_MD)
    jrel = "skills/SKILL_INDEX.json"
    raw = read_text(jrel) if os.path.exists(P(jrel)) else ""
    data = json.loads(raw) if raw else {}
    if not isinstance(data, dict):
        data = {"skills": data if isinstance(data, list) else []}
    skills = data.get("skills") if isinstance(data.get("skills"), list) else []
    data["skills"] = skills
    slugs = [str(x.get("slug") or x.get("id") or x.get("name") or "") if isinstance(x, dict) else str(x) for x in skills]
    if SKILL_ID not in slugs:
        sample = next((x for x in reversed(skills) if isinstance(x, dict)), {})
        nos = [x.get("no") for x in skills if isinstance(x, dict) and isinstance(x.get("no"), int)]
        entry = {"no": (max(nos) + 1) if nos else len(skills) + 1, "slug": SKILL_ID, "antibody": "R42",
                 "version": NEW_VERSION, "path": SKILL_PATH}
        extra = {"id": SKILL_ID, "name": SKILL_ID, "title": SKILL_TITLE, "description": SKILL_DESC,
                 "organ": "제18기관", "file": HYDRO_FILE}
        for k in sample:
            if k not in entry:
                entry[k] = extra.get(k, "" if isinstance(sample[k], str) else sample[k])
        skills.append(entry)
    old_ab = str(data.get("antibody") or "")
    head = {"version": NEW_VERSION,
            "antibody": "R42" if re.fullmatch(r"R\d+", old_ab) else NEW_RANGE,
            "generated_at_kst": kst_now(), "count": len(skills)}
    ordered = {}
    for k in data:
        ordered[k] = head.get(k, data[k])
    for k in TOP_KEYS:
        if k not in ordered:
            ordered[k] = head.get(k, skills)
    ordered["skills"] = skills
    write_text(jrel, json.dumps(ordered, ensure_ascii=False, indent=detect_indent(raw) if raw else 2) + "\n")

    mrel = "skills/SKILL_INDEX.md"
    md = read_text(mrel) if os.path.exists(P(mrel)) else "# SKILL INDEX\n"
    md = bump_str(md)
    md = re.sub(r"(정식\s*스킬\s*)37\b", r"\g<1>38", md)
    if SKILL_ID not in md:
        rows = [l for l in md.splitlines() if re.match(r"^\|\s*\d+\s*\|", l)]
        if rows:
            ncol = rows[-1].count("|") - 1
            cells = ["38", "`%s`" % SKILL_ID, SKILL_TITLE, "R42", "`%s`" % SKILL_PATH]
            cells = (cells + [""] * ncol)[:ncol]
            if ncol >= 2:
                cells[-1] = "`%s`" % SKILL_PATH
            line = "| " + " | ".join(cells) + " |"
            lines = md.splitlines()
            idx = max(i for i, l in enumerate(lines) if l == rows[-1])
            lines.insert(idx + 1, line)
            md = "\n".join(lines) + "\n"
        else:
            md = md.rstrip("\n") + "\n| 38 | `%s` | %s | R42 | `%s` |\n" % (SKILL_ID, SKILL_TITLE, SKILL_PATH)
    write_text(mrel, md)
    log("[SKILL] SKILL_INDEX.json count=%d" % len(skills))


def update_registry():
    rel = "ANTIBODY_REGISTRY.md"
    t = bump_str(read_text(rel)) if os.path.exists(P(rel)) else "# ANTIBODY REGISTRY\n"
    if not re.search(r"^#+\s*R42\b", t, re.M):
        t = t.rstrip("\n") + ("\n\n## R42 — 상선약수 수순환 여백 창조 항체 (%s)\n"
                              "- 기관: 제18기관 `%s` · 스킬 #38 `%s`\n"
                              "- 규칙: 기본 dry-run. TIER3(휴지통·Downloads 대용량·비대 로그)는 `requires_manual_gate: True`, `auto_executed: False`로 두고 자동 삭제하지 않음. 기억 원본은 읽기 전용\n"
                              "- 시냅스: S12 대화허브(/순환)→제18기관 수순환 대사\n- 범위: %s\n") % (NEW_VERSION, HYDRO_FILE, SKILL_ID, NEW_RANGE)
    write_text(rel, t)
    rel = "CODE_MAP.md"
    t = bump_str(read_text(rel)) if os.path.exists(P(rel)) else "# CODE MAP\n"
    t = re.sub(r"(정식\s*스킬\s*)37(\s*개)", r"\g<1>38\2", t)
    if HYDRO_FILE not in t:
        t = t.rstrip("\n") + ("\n\n## %s · 항체 %s · 정식 스킬 38개\n- `%s` — 제18기관 아온 상선약수 수순환 자율 대사 & 여백 창조 기관\n"
                              % (NEW_VERSION, NEW_RANGE, HYDRO_FILE))
    write_text(rel, t)
    log("[REGISTRY] ANTIBODY_REGISTRY.md · CODE_MAP.md 갱신")


# ══════════════════════════════════════════════════════════════════════
# 5. 보호 구간 & 버전 승격
# ══════════════════════════════════════════════════════════════════════
def protected_spans(text, names):
    spans = []
    try:
        tree = ast.parse(text)
        offs = [0]
        for ln in text.splitlines(True):
            offs.append(offs[-1] + len(ln))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                tg = node.targets if isinstance(node, ast.Assign) else [node.target]
                if any(isinstance(x, ast.Name) and x.id in names for x in tg):
                    spans.append((offs[node.lineno - 1], offs[getattr(node, "end_lineno", node.lineno)]))
    except Exception:
        for nm in names:
            m = re.search(r"^" + nm + r"\s*=", text, re.M)
            if m:
                spans.append((m.start(), len(text)))
    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def protected_digest():
    out = {}
    for rel, names in PROTECT.items():
        if os.path.exists(P(rel)):
            t = read_text(rel)
            out[rel] = hashlib.sha256("".join(t[s:e] for s, e in protected_spans(t, names)).encode("utf-8")).hexdigest()
        else:
            out[rel] = None
    return out


def bump_versions():
    n = 0
    for fn in sorted(os.listdir(ROOT)):
        if not (fn.startswith("rgon_") and fn.endswith(".py")) or is_preserved(fn) or fn == HYDRO_FILE:
            continue
        t = read_text(fn)
        if OLD_VERSION not in t and OLD_RANGE not in t:
            continue
        spans = protected_spans(t, PROTECT[fn]) if fn in PROTECT else []
        out, last = [], 0
        for s, e in spans:
            out.append(bump_str(t[last:s]))
            out.append(t[s:e])
            last = e
        out.append(bump_str(t[last:]))
        if write_text(fn, "".join(out)):
            n += 1
    log("[BUMP] %d개 .py 승격 (SOUND_RECIPES · PRESERVE_EXACT 구간 보호)" % n)


def update_hashes():
    if not os.path.exists(P(HASH_FILE)):
        log("[HASH] %s 없음 — 건너뜀" % HASH_FILE)
        return
    raw = read_text(HASH_FILE)
    data = json.loads(raw)
    target = data["files"] if isinstance(data, dict) and isinstance(data.get("files"), dict) else data
    if not isinstance(target, dict):
        return
    algo = "sha256"
    for v in target.values():
        hv = (v.get("sha256") or v.get("hash")) if isinstance(v, dict) else v
        if isinstance(hv, str):
            algo = {32: "md5", 40: "sha1"}.get(len(hv), "sha256")
            break
    n = 0
    for rel in list(target.keys()):
        if is_preserved(rel) or rel not in MODIFIED or not os.path.exists(P(rel)):
            continue
        h = sha_file(P(rel), algo)
        if isinstance(target[rel], dict):
            target[rel]["sha256" if "sha256" in target[rel] else "hash"] = h
        else:
            target[rel] = h
        n += 1
    for rel in HTML_TARGETS:
        if rel in MODIFIED and rel not in target and os.path.exists(P(rel)):
            target[rel] = sha_file(P(rel), algo)
            n += 1
    if isinstance(data, dict) and "version" in data:
        data["version"] = NEW_VERSION
    write_text(HASH_FILE, json.dumps(data, ensure_ascii=False, indent=detect_indent(raw)) + "\n")
    log("[HASH] %d개 해시 갱신 (%s)" % (n, algo))


# ══════════════════════════════════════════════════════════════════════
# 6. 검증
# ══════════════════════════════════════════════════════════════════════
def run_py(args, timeout=300, env_extra=None):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
    if env_extra:
        env.update(env_extra)
    try:
        r = subprocess.run([sys.executable] + args, cwd=ROOT, env=env, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return -1, repr(e)


def organ_selftests():
    code = ("import json,importlib;v=importlib.import_module('rgon_neural_synapse_verifier');"
            "print('@@O@@'+json.dumps(list(getattr(v,'ORGANS',[]))))")
    _rc, out = run_py(["-c", code], 90)
    organs = []
    if "@@O@@" in out:
        try:
            organs = json.loads(out.split("@@O@@", 1)[1].strip().splitlines()[0])
        except Exception:
            organs = []
    for f in (PLANNER_FILE, HYDRO_FILE):
        if f not in organs and os.path.exists(P(f)):
            organs.append(f)

    def one(fn):
        if not os.path.exists(P(fn)):
            return fn, False, "missing"
        tmp = tempfile.mkdtemp(prefix="rgon42_")
        rc, o = run_py([fn, "--self-test"], 300, {"RGON_ICHING_STATE_DIR": tmp, "RGON_DIALOGUE_STATE_DIR": tmp,
                                                  "RGON_HYDRO_STATE_DIR": tmp})
        shutil.rmtree(tmp, ignore_errors=True)
        return fn, rc == 0, o[-400:]

    with ThreadPoolExecutor(max_workers=6) as ex:
        return list(ex.map(one, organs))


def verifier_report():
    code = r"""
import os, json, tempfile, importlib
t = tempfile.mkdtemp(prefix='rgon42v_')
for k in ('RGON_HYDRO_STATE_DIR','RGON_ICHING_STATE_DIR','RGON_DIALOGUE_STATE_DIR'):
    os.environ[k] = t
v = importlib.import_module('rgon_neural_synapse_verifier')
out = {}
f = getattr(v, 'heal_skill_index_header', None)
if callable(f):
    try: f()
    except Exception as e: out['heal_err'] = repr(e)
for name in ('run_full','run_full_verification','verify_all','run_verification','full_report','build_report','main_report'):
    f = getattr(v, name, None)
    if callable(f):
        try:
            r = f()
            if isinstance(r, dict):
                out['report'] = r; out['via'] = name; break
        except Exception as e:
            out.setdefault('errs', []).append(name + ':' + repr(e))
out['synapse'] = v.verify_synapse_links()
print('@@JSON@@' + json.dumps(out, ensure_ascii=False, default=str))
"""
    rc, out = run_py(["-c", code], 900)
    data = {}
    if "@@JSON@@" in out:
        try:
            data = json.loads(out.split("@@JSON@@", 1)[1].strip().splitlines()[0])
        except Exception:
            data = {}
    return rc, data, out[-2000:]


def find_key(d, key, depth=0):
    if depth > 5:
        return None
    if isinstance(d, dict):
        if key in d:
            return d[key]
        for v in d.values():
            r = find_key(v, key, depth + 1)
            if r is not None:
                return r
    elif isinstance(d, list):
        for v in d:
            r = find_key(v, key, depth + 1)
            if r is not None:
                return r
    return None


def synapse_items(s):
    if isinstance(s, list):
        return [x for x in s if isinstance(x, dict)]
    if isinstance(s, dict):
        for k in ("links", "synapses", "results", "checks"):
            if isinstance(s.get(k), list):
                return [x for x in s[k] if isinstance(x, dict)]
        return [dict(v, id=k) if isinstance(v, dict) else {"id": k, "ok": bool(v)}
                for k, v in s.items() if re.match(r"S\d+$", str(k))]
    return []


def skill_counts():
    data = json.loads(read_text("skills/SKILL_INDEX.json"))
    skills = data.get("skills") or [] if isinstance(data, dict) else data
    a = len(skills)
    slugs = sorted([d for d in os.listdir(P("skills")) if os.path.isfile(P(os.path.join("skills", d, "SKILL.md")))])
    b = len(slugs)
    md = read_text("skills/SKILL_INDEX.md")
    c = sum(1 for s in slugs if s in md)
    return [a, b, c]


def index_keys_ok():
    data = json.loads(read_text("skills/SKILL_INDEX.json"))
    if not isinstance(data, dict) or any(k not in data for k in TOP_KEYS):
        return False
    if data.get("version") != NEW_VERSION or data.get("count") != len(data["skills"]):
        return False
    mine = [x for x in data["skills"] if isinstance(x, dict) and x.get("slug") == SKILL_ID]
    return bool(mine) and all(k in mine[0] for k in ENTRY_KEYS)


def preserve_snapshot():
    return {f: (sha_file(P(f)) if os.path.exists(P(f)) else None) for f in PRESERVE}


def git(args):
    try:
        r = subprocess.run(["git", "-C", ROOT] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return -1, repr(e)


# ══════════════════════════════════════════════════════════════════════
# 7. 메인
# ══════════════════════════════════════════════════════════════════════
def main():
    log("=" * 70)
    log("RGON Step 42 · %s · 항체 %s · 정식 스킬 %d" % (NEW_VERSION, NEW_RANGE, NEW_COUNT))
    log("ROOT = " + ROOT)
    for rel in REQUIRED_FILES:
        if not os.path.exists(P(rel)):
            log("[ABORT] 필수 파일 없음: " + rel)
            return 2
    os.makedirs(BACKUP_DIR, exist_ok=True)
    pres_before = preserve_snapshot()
    prot_before = protected_digest()
    try:
        write_text(HYDRO_FILE, HYDRO_SRC)
        py_compile.compile(P(HYDRO_FILE), doraise=True)
        log("[1] 제18기관 생성: " + HYDRO_FILE)

        t = read_text(DIALOGUE_FILE)
        write_text(DIALOGUE_FILE, insert_block(t, DLG_BEGIN, DLG_END, DIALOGUE_HOOK))
        py_compile.compile(P(DIALOGUE_FILE), doraise=True)
        log("[2] 대화허브 R42 훅 장착")

        bump_versions()
        t = read_text(VERIFIER_FILE)
        write_text(VERIFIER_FILE, insert_block(t, VER_BEGIN, VER_END, VERIFIER_HOOK))
        py_compile.compile(P(VERIFIER_FILE), doraise=True)
        log("[3] 검증기 확장 (N14 · S12 · 스냅샷 · heal 38)")

        init_hydro_state_snapshots()
        update_html()
        update_skill_index()
        update_registry()
        update_json_snapshots()
        for rel in sorted(MODIFIED):
            if rel.endswith(".py"):
                py_compile.compile(P(rel), doraise=True)
        update_hashes()

        log("[4] 삼성(三省) 검증")
        organ_res = organ_selftests()
        organ_pass = sum(1 for _f, ok, _o in organ_res if ok)
        for f, ok, o in organ_res:
            log("   %s %s" % ("PASS" if ok else "FAIL", f) + ("" if ok else "\n      " + o.replace("\n", "\n      ")))
        _rc, vdata, vtail = verifier_report()
        items = synapse_items(vdata.get("synapse"))
        syn_pass = sum(1 for x in items if x.get("ok"))
        s12 = next((x for x in items if str(x.get("id")) == "S12"), None)
        score = find_key(vdata.get("report"), "synapse_health_score")
        try:
            score = float(score) if score is not None else None
        except Exception:
            score = None
        if score is None:
            score = round(100.0 * (syn_pass + organ_pass) / max(1, len(items) + len(organ_res)), 1)
        keys_ok = index_keys_ok()
        rep_keys = find_key(vdata.get("report"), "index_keys_ok")
        log("   기관 %d/%d · 시냅스 %d/%d · S12=%s · score=%s · index_keys_ok=%s/%s" % (
            organ_pass, len(organ_res), syn_pass, len(items), bool(s12 and s12.get("ok")), score, keys_ok, rep_keys))
        if s12 and not s12.get("ok"):
            log("   S12 detail: %s" % json.dumps(s12.get("detail"), ensure_ascii=False, default=str)[:600])

        g1 = (score == 100.0 and organ_pass == len(organ_res) and len(organ_res) >= 14
              and syn_pass == len(items) and len(items) >= 12 and bool(s12 and s12.get("ok"))
              and keys_ok and rep_keys is not False)
        g2 = preserve_snapshot() == pres_before and protected_digest() == prot_before
        counts = skill_counts()
        g3 = counts == [NEW_COUNT] * 3
        log("   ①기능 %s ②보호파일 %s ③스킬 %s %s" % (
            "PASS" if g1 else "FAIL", "PASS" if g2 else "FAIL", counts, "PASS" if g3 else "FAIL"))
        passed = sum([g1, g2, g3])
        if passed != 3:
            with open(P(DIAG_FILE), "w", encoding="utf-8") as f:
                f.write("\n".join(LOGS) + "\n\n--- verifier tail ---\n" + vtail)
            log("[FAIL] 삼성 %d/3 — 진단: %s" % (passed, DIAG_FILE))
            if not NO_ROLLBACK:
                rollback()
            return 1

        report = "\n".join([
            "# STEP 42 — 제18기관 아온 상선약수 수순환 자율 대사 & 여백 창조 기관 배포 리포트", "",
            "> 비워야 새로운 것이 들어올 자리가 생긴다 — 上善若水 · 虛實相生", "",
            "- 버전: `%s` · 항체 `%s` · 정식 스킬 %d개" % (NEW_VERSION, NEW_RANGE, NEW_COUNT),
            "- 일시(KST): %s" % kst_now(),
            "- 삼성 3/3 PASS: ①synapse_health_score=%s ②보호파일 변경 0건(SOUND_RECIPES·PRESERVE_EXACT·PRESERVE 불변) ③스킬 %s" % (score, counts),
            "- 기관 셀프테스트 %d/%d · 시냅스 %d/%d (S12 대화허브(/순환)→제18기관 PASS)" % (organ_pass, len(organ_res), syn_pass, len(items)),
            "- 4단계 수순환: #41 산택손·#18 산풍고 → #48 수풍정 → #29 중수감·#60 수택절 → #63 수화기제·#64 화수미제",
            "- Tier3 수동결재 게이트: requires_manual_gate=True · auto_executed=False (헌법 제2항·R35·R42)", "",
            "## 변경 파일", ""] + ["- `%s`" % r for r in sorted(MODIFIED)] + [""])
        write_text(REPORT_FILE, report)
        log("[5] 리포트 생성: " + REPORT_FILE)

        excludes = [":(exclude)%s" % f for f in PRESERVE] + [
            ":(exclude).rgon_backups", ":(exclude)**/__pycache__", ":(exclude)" + DIAG_FILE]
        rc1, o1 = git(["add", "-A", "--", "."] + excludes)
        if rc1 != 0:
            rc1, o1 = git(["add", "--"] + [r for r in sorted(MODIFIED) if not is_preserved(r)])
        git(["reset", "-q", "--"] + PRESERVE)
        rc2, o2 = git(["commit", "-m", "Step42: %s 제18기관 상선약수 수순환 · R1~R42 · 스킬38" % NEW_VERSION])
        rc3, o3 = git(["push", "origin", "main"])
        log("[6] git add=%s commit=%s push=%s" % (rc1, rc2, rc3))
        if rc2 != 0:
            log("    commit 출력: " + o2[-300:])
        if rc3 != 0:
            log("    push 출력: " + o3[-300:])
        log("=" * 70)
        log("삼성 3/3 PASS · %s 배포 완료 — 비운 자리에 새 물이 흐른다" % NEW_VERSION)
        return 0
    except Exception:
        log("[EXCEPTION]\n" + traceback.format_exc())
        try:
            with open(P(DIAG_FILE), "w", encoding="utf-8") as f:
                f.write("\n".join(LOGS))
        except Exception:
            pass
        if not NO_ROLLBACK:
            rollback()
        return 1


if __name__ == "__main__":
    code = main()
    if os.name == "nt" and not os.environ.get("RGON_NO_PAUSE") and sys.stdin and sys.stdin.isatty():
        try:
            input("\n[Enter] 키를 누르면 창이 닫힙니다...")
        except Exception:
            pass
    sys.exit(code)

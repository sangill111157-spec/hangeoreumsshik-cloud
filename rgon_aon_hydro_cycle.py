# -*- coding: utf-8 -*-
"""
rgon_aon_hydro_cycle.py — 제18기관 아온 상선약수(上善若水) 수순환(水循環) 자율 대사 & 여백 창조 기관
정식 스킬 #38 aon-hydro-cycle-homeostasis · v11.55-AON-TELEGRAM-MESSENGER · 항체 R42 (R1~R56)

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

VERSION = "v11.55-AON-TELEGRAM-MESSENGER"
ANTIBODY = "R42"
ANTIBODY_RANGE = "R1~R56"
SKILL_COUNT = 39
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

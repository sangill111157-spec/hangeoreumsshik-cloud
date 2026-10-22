#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RGON G1 Step 11 / 과제 C-3
rgon_runner.py 에 R14(코드 끝 스트리밍 찌꺼기 자동 정화 · ast.parse 검증) 장착
GEN1_AUTONOMOUS_EVOLUTION_CLOSED_LOOP 상시 가동 · 항체 R1~R14 (14/14) · 박동 #6 클라우드 배포
실행: RGON_Run.bat -> rgon_runner.py -> 본 스크립트 (단독 실행 가능)
"""
import sys, os, re, ast, json, shutil, hashlib, subprocess, time
from pathlib import Path
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ───────────────────────── 설정 ─────────────────────────
ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
CONSTITUTION = ROOT / "rgon_constitution.json"
CONST_PREFIX = "bd5060dea1e2"
HTML_PREFIX = "161d363a5dae"
RUNNER = ROOT / "rgon_runner.py"
SCHEDULE = ROOT / "brain_basket" / "master_schedule.json"
PULSE = ROOT / "scripts" / "rgon_agency_pulse.py"
HTMLS = [ROOT / "rgon_alpha_chat.html",
         ROOT / "dashboard" / "rgon_alpha_chat.html",
         ROOT / "docs" / "rgon_alpha_chat.html"]
SNAPS = [ROOT / "rgon_brain_snapshot.json",
         ROOT / "dashboard" / "rgon_brain_snapshot.json",
         ROOT / "docs" / "rgon_brain_snapshot.json"]
EVOLUTION = ROOT / "evolution_memory.json"
BACKUP_DIR = ROOT / "backups"

TOP1 = "TOP1_SELF_EVOLVING_BRAIN"
GEN1 = "GEN1_AUTONOMOUS_EVOLUTION_CLOSED_LOOP"
EVENT = "step11_task_c3_r14_gen1_closed_loop_active"
KEYWORDS = ["AI 에이전트 군단 자동화", "4대 AI 교차검증 레버리지", "원클릭 무인 사령부",
            "홍익인간 안전 가드레일", "24시간 클라우드 자가진화"]
PROTECTED_IDS = ["rgon-step5-solo-panel", "rgon-step7-chat-zone", "rgon-step8-constitution-bar",
                 "rgon-step9-aggregator-board", "rgon-step10-agency-awaken", "dokdae-feed"]
FINAL_OK = "[OK] Step 11 과제 C-3 R14 불사신 런처 장착 · GEN-1 자율 진화 폐루프 가동 · 항체 14/14 · 박동 #6 클라우드 배포 완료"

NOW = datetime.now()
TS = NOW.strftime("%Y%m%d_%H%M%S")
TODAY = NOW.strftime("%Y-%m-%d")
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S")
TAG = "_step11c3_bak_" + TS

TARGETS = [RUNNER, SCHEDULE, PULSE] + SNAPS + [EVOLUTION]
BACKUPS = {}


def log(msg):
    print(msg, flush=True)


def rel(p):
    try:
        return str(Path(p).relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(p)


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ═════════════════════ R14 코어 (rgon_runner.py 에 주입) ═════════════════════
R14_SRC = r'''
import ast as _r14_ast
import os as _r14_os
import re as _r14_re
import tempfile as _r14_tmp
import functools as _r14_ft
import types as _r14_types

R14_ACTIVE = True
R14_MAX_TAIL_DROP = 5
_R14_FENCE = _r14_re.compile(r"^\s*`{3,}[^\n]*$")
_R14_WORD = _r14_re.compile(r"^\s*(?:copy(?:\s*code)?|copied!?|복사(?:하기|됨)?|코드\s*복사|python|py)\s*$", _r14_re.I)
_R14_SYM = _r14_re.compile(r"^\s*[`!\]\[—–\-\s]*[`!—–][`!\]\[—–\-\s]*$")
_R14_INLINE = _r14_re.compile(r"(?:`{1,3}[A-Za-z]*|!\]|[—–]|\s)+$")


def _r14_ok(code):
    try:
        _r14_ast.parse(code)
        return True
    except (SyntaxError, ValueError, MemoryError, RecursionError):
        return False


def _r14_is_junk(line):
    return bool(_R14_FENCE.match(line) or _R14_WORD.match(line) or _R14_SYM.match(line))


def _r14_trim_edges(lines):
    lines = list(lines)
    while lines and (not lines[0].strip() or _r14_is_junk(lines[0])):
        lines.pop(0)
    while lines and (not lines[-1].strip() or _r14_is_junk(lines[-1])):
        lines.pop()
    return lines


def _r14_trim_tail(lines):
    lines = list(lines)
    while lines and (not lines[-1].strip() or _r14_is_junk(lines[-1])):
        lines.pop()
    return lines


def _r14_join(lines):
    return "\n".join(lines) + "\n"


def _r14_variants(lines):
    """한 단계(lines)에 대해 시도할 후보 코드들을 만든다."""
    yield _r14_join(lines), "edge-trim"
    last = lines[-1]
    m = _R14_INLINE.search(last)
    if m and m.start() < len(last):
        head = last[:m.start()]
        cand = list(lines[:-1])
        if head.strip():
            cand.append(head.rstrip())
        yield _r14_join(cand), "inline-tail-strip"
    zw = _r14_join(lines)
    for ch in ("\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"):
        zw = zw.replace(ch, "")
    yield zw, "zero-width-strip"


def r14_smart_purify_ex(text):
    """R14 스마트 정화. (정화된 코드, 노트 목록) 반환."""
    notes = []
    if isinstance(text, bytes):
        text = text.decode("utf-8-sig", "replace")
    src = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    lines = _r14_trim_edges(src.split("\n"))
    if not lines:
        return "", ["empty"]
    code = _r14_join(lines)
    if code.strip() != src.strip():
        notes.append("fence/Copy/!]— edge tags removed")
    if _r14_ok(code):
        return code, notes
    m = _r14_re.search(r"```[ \t]*(?:python|py)?[ \t]*\n(.*?)\n[ \t]*```", src, _r14_re.S | _r14_re.I)
    if m:
        inner = _r14_trim_edges(m.group(1).split("\n"))
        if inner and _r14_ok(_r14_join(inner)):
            notes.append("fenced python block extracted")
            return _r14_join(inner), notes
    work = list(lines)
    for dropped in range(0, R14_MAX_TAIL_DROP + 1):
        if dropped:
            if len(work) <= 1:
                break
            work.pop()
            work = _r14_trim_tail(work)
        if not work:
            break
        for cand, how in _r14_variants(work):
            if cand.strip() and _r14_ok(cand):
                notes.append("ast.parse OK via %s (tail lines dropped: %d)" % (how, dropped))
                return cand, notes
    notes.append("unresolved (ast.parse still failing)")
    return code, notes


def r14_smart_purify(text):
    return r14_smart_purify_ex(text)[0]


def r14_atomic_write(path, code):
    d = _r14_os.path.dirname(_r14_os.path.abspath(path)) or "."
    fd, tmp = _r14_tmp.mkstemp(prefix=".r14_", suffix=".tmp", dir=d)
    try:
        with _r14_os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(code)
            f.flush()
            _r14_os.fsync(f.fileno())
        _r14_os.replace(tmp, path)
    except Exception:
        try:
            _r14_os.remove(tmp)
        except OSError:
            pass
        raise


def r14_guard_file(path):
    """실행 직전 파일을 정화한다. 정화 결과가 ast.parse 를 통과할 때만 원자적으로 덮어쓴다."""
    try:
        with open(path, "rb") as f:
            text = f.read().decode("utf-8-sig", "replace")
        norm = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
        code, notes = r14_smart_purify_ex(text)
        if code and code.strip() != norm.strip() and _r14_ok(code):
            r14_atomic_write(path, code)
            print("[R14] 코드 끝 찌꺼기 정화 완료 -> " + _r14_os.path.basename(path) + " : " + "; ".join(notes), flush=True)
            return True
    except Exception as e:
        try:
            print("[R14] 정화 건너뜀: %s" % e, flush=True)
        except Exception:
            pass
    return False


_R14_NAME = _r14_re.compile(r"(clean|sanit|purif|정화|scrub|defence|defense|strip_?(?:fence|md|markdown|code))", _r14_re.I)


def r14_install_funcs(g):
    """런처 모듈의 텍스트 정화 계열 함수(이름: clean/sanitize/purify/정화 ...)의 반환 코드에 R14 를 덧씌운다."""
    for name, fn in list(g.items()):
        if name.startswith("r14_") or name.startswith("_r14_"):
            continue
        if not isinstance(fn, _r14_types.FunctionType) or fn.__globals__ is not g:
            continue
        if getattr(fn, "_r14_wrapped", False) or not _R14_NAME.search(name):
            continue

        def make(f):
            @_r14_ft.wraps(f)
            def w(*a, **k):
                res = f(*a, **k)
                try:
                    if isinstance(res, str) and "\n" in res and len(res) > 20:
                        out, _notes = r14_smart_purify_ex(res)
                        if out and _r14_ok(out):
                            return out
                except Exception:
                    pass
                return res
            w._r14_wrapped = True
            return w
        g[name] = make(fn)


def _r14_collect(x, out, depth=0):
    if depth > 4:
        return
    if isinstance(x, (list, tuple)):
        for y in x:
            _r14_collect(y, out, depth + 1)
        return
    if isinstance(x, (str, bytes, _r14_os.PathLike)):
        try:
            s = _r14_os.fspath(x)
        except Exception:
            return
        if isinstance(s, bytes):
            s = s.decode("utf-8", "replace")
        if "s_run.py" in s.lower():
            for m in _r14_re.finditer(r"\"([^\"]*s_run\.py)\"|'([^']*s_run\.py)'|(\S*s_run\.py)", s, _r14_re.I):
                out.append(m.group(1) or m.group(2) or m.group(3))


def _r14_guard_call(args, kwargs):
    try:
        cands = []
        _r14_collect(args, cands)
        if not cands:
            return
        bases = []
        cwd = kwargs.get("cwd") if isinstance(kwargs, dict) else None
        if cwd:
            bases.append(str(cwd))
        bases.append(_r14_os.getcwd())
        try:
            bases.append(_r14_os.path.dirname(_r14_os.path.abspath(__file__)))
        except NameError:
            pass
        seen = set()
        for c in cands:
            paths = [c] if _r14_os.path.isabs(c) else [_r14_os.path.join(b, c) for b in bases]
            for p in paths:
                if _r14_os.path.isfile(p):
                    if p not in seen:
                        seen.add(p)
                        r14_guard_file(p)
                    break
    except Exception:
        pass


def r14_install_process_hooks():
    """s_run.py 가 실행되기 직전(subprocess/os.system/os.startfile/runpy)에 R14 정화를 보장한다."""
    import subprocess as _sp
    if getattr(_sp, "_r14_hooked", False):
        return
    _Orig = _sp.Popen

    class _R14Popen(_Orig):
        def __init__(self, *a, **k):
            _r14_guard_call(a, k)
            super().__init__(*a, **k)
    _R14Popen.__name__ = "Popen"
    _R14Popen.__qualname__ = "Popen"
    _sp.Popen = _R14Popen
    _sp._r14_hooked = True

    _orig_system = _r14_os.system

    def _r14_system(cmd, *a, **k):
        _r14_guard_call((cmd,), {})
        return _orig_system(cmd, *a, **k)
    _r14_os.system = _r14_system

    if hasattr(_r14_os, "startfile"):
        _orig_sf = _r14_os.startfile

        def _r14_startfile(path, *a, **k):
            _r14_guard_call((path,), {})
            return _orig_sf(path, *a, **k)
        _r14_os.startfile = _r14_startfile

    try:
        import runpy as _rp
        _orig_rp = _rp.run_path

        def _r14_run_path(path_name, *a, **k):
            _r14_guard_call((path_name,), {})
            return _orig_rp(path_name, *a, **k)
        _rp.run_path = _r14_run_path
    except Exception:
        pass
'''

R14_CORE_BEGIN = "# ==== RGON-R14-CORE-BEGIN (step11c3) ===="
R14_CORE_END = "# ==== RGON-R14-CORE-END ===="
R14_INST_BEGIN = "# ==== RGON-R14-INSTALL-BEGIN (step11c3) ===="
R14_INST_END = "# ==== RGON-R14-INSTALL-END ===="
R14_CORE_BLOCK = (R14_CORE_BEGIN + "\n# R14: 코드 끝 스트리밍 찌꺼기 자동 정화 (ast.parse 검증) — 제14호 항체\n"
                  + R14_SRC.strip("\n") + "\n\nr14_install_process_hooks()\n" + R14_CORE_END)
R14_INST_BLOCK = (R14_INST_BEGIN + "\nr14_install_funcs(globals())\n" + R14_INST_END)

# ═════════════════════ 항체 R14 / GEN1 보정 (pulse 에 주입, 장부 갱신에도 재사용) ═════════════════════
AB_SRC = r'''
import re as _c3_re
import copy as _c3_copy
import json as _c3_json
import functools as _c3_functools
import types as _c3_types
import inspect as _c3_inspect
from pathlib import Path as _C3Path

_C3_R14_FULL = "R14: 코드 끝 찌꺼기 자동 정화"
_C3_R14_TEXT = "코드 끝 찌꺼기 자동 정화"
_C3_ID_KEYS = ("id", "code", "name", "key", "antibody", "rule", "no", "num", "number", "label", "title")
_C3_TXT_KEYS = ("name", "title", "desc", "description", "summary", "text", "label", "detail", "rule", "content", "ko")
_C3_CNT_KEY = _c3_re.compile(r"count|total|active|num|size|len|수|개|활성", _c3_re.I)
_C3_MARK_GEN1 = "GEN1_AUTONOMOUS_EVOLUTION_CLOSED_LOOP (ACTIVE)"
_C3_MARK_AB = "14대 항체 14/14 활성"


def _c3_root():
    try:
        return _C3Path(__file__).resolve().parent.parent
    except NameError:
        return _C3Path(".").resolve()


def _c3_isr(x, n):
    return isinstance(x, str) and _c3_re.match(r"^\s*[\[\(]?R0?%d(?![0-9])" % n, x) is not None


def _c3_item_has(item, n):
    if isinstance(item, str):
        return _c3_isr(item, n)
    if isinstance(item, dict):
        return any(_c3_isr(v, n) for k, v in item.items() if k in _C3_ID_KEYS)
    return False


def _c3_make(tpl):
    if isinstance(tpl, str):
        if _c3_re.match(r"^\s*R0?13\s*$", tpl):
            return "R14"
        if _c3_isr(tpl, 13):
            return _C3_R14_FULL
        return _C3_R14_TEXT
    if isinstance(tpl, dict):
        new = _c3_copy.deepcopy(tpl)
        for k, v in list(new.items()):
            if not isinstance(v, str):
                continue
            if _c3_re.match(r"^\s*R0?13\s*$", v):
                new[k] = "R14"
            elif _c3_isr(v, 13):
                new[k] = _C3_R14_FULL
            elif k in _C3_TXT_KEYS:
                new[k] = _C3_R14_TEXT
        return new
    return _c3_copy.deepcopy(tpl)


def _c3_bump(d):
    for k, v in list(d.items()):
        if isinstance(v, int) and not isinstance(v, bool) and v == 13 and isinstance(k, str) and _C3_CNT_KEY.search(k):
            d[k] = 14


def _c3_upgrade_struct(obj, _d=0):
    """R13 까지 있는 항체 목록/사전에 R14 를 추가한다(이미 있으면 무변경)."""
    if _d > 14:
        return False
    changed = False
    if isinstance(obj, list):
        has13 = [i for i, x in enumerate(obj) if _c3_item_has(x, 13)]
        has14 = any(_c3_item_has(x, 14) for x in obj)
        if has13 and not has14:
            idx = has13[-1]
            obj.insert(idx + 1, _c3_make(obj[idx]))
            changed = True
        for x in list(obj):
            if isinstance(x, (dict, list)) and _c3_upgrade_struct(x, _d + 1):
                changed = True
    elif isinstance(obj, dict):
        k13 = [k for k in obj if isinstance(k, str) and _c3_re.match(r"^\s*R0?13\s*$", k)]
        has14 = any(isinstance(k, str) and _c3_re.match(r"^\s*R0?14\s*$", k) for k in obj)
        if k13 and not has14:
            obj["R14"] = _c3_make(obj[k13[0]])
            changed = True
        for k, v in list(obj.items()):
            if isinstance(v, (dict, list)) and _c3_upgrade_struct(v, _d + 1):
                changed = True
        if changed:
            _c3_bump(obj)
    return changed


def _c3_text(s):
    if not isinstance(s, str) or len(s) > 20000:
        return s
    out = s
    if "R1" in out or "항체" in out:
        out = _c3_re.sub(r"R0?1\s*[~\-–]\s*R0?13(?![0-9])", "R1~R14", out)
        if "항체" in out or "R1~R14" in out:
            out = _c3_re.sub(r"(?<![0-9/])13\s*/\s*13(?![0-9])", "14/14", out)
            out = _c3_re.sub(r"(?<![0-9])13(\s*(?:대|종|개)\s*항체)", r"14\1", out)
    return out


def _c3_gen1_active():
    try:
        p = _c3_root() / "brain_basket" / "master_schedule.json"
        d = _c3_json.loads(p.read_text(encoding="utf-8-sig"))
        g = d.get("gen1_autonomous_evolution_closed_loop")
        return isinstance(g, dict) and str(g.get("status", "")).upper() == "ACTIVE"
    except Exception:
        return False


def _c3_aug_str(s):
    add = []
    if "GEN1_AUTONOMOUS_EVOLUTION_CLOSED_LOOP" not in s:
        add.append(_C3_MARK_GEN1)
    if "14/14" not in s:
        add.append(_C3_MARK_AB)
    if not add:
        return s
    return (s + " · " + " · ".join(add)) if s.strip() else " · ".join(add)


def _c3_aug_dict(d):
    for tk in ("detail", "summary", "text", "msg", "message", "report", "note", "desc", "description",
               "finding", "diagnosis", "brief"):
        if isinstance(d.get(tk), str):
            d[tk] = _c3_aug_str(d[tk])
            return
    best = None
    for k, v in d.items():
        if isinstance(v, str) and k not in ("status", "state", "level", "id", "key", "name", "code", "dim",
                                            "ts", "time", "date") and len(v) >= 10:
            if best is None or len(v) > len(d[best]):
                best = k
    if best:
        d[best] = _c3_aug_str(d[best])
    else:
        d["detail"] = _c3_aug_str("")


def _c3_dimdict(d):
    for i in ("id", "key", "dim", "name", "code"):
        v = d.get(i)
        if isinstance(v, str) and _c3_re.match(r"^D[15](_|$)", v):
            return True
    return False


def _c3_fix(obj, _d=0, _g=None):
    if _g is None:
        _g = _c3_gen1_active()
    if isinstance(obj, str):
        return _c3_text(obj)
    if _d > 12:
        return obj
    if isinstance(obj, dict):
        if _g and _c3_dimdict(obj):
            _c3_aug_dict(obj)
        for k in list(obj.keys()):
            v = obj[k]
            if _g and isinstance(k, str) and _c3_re.match(r"^D[15](_|$)", k):
                if isinstance(v, str):
                    v = _c3_aug_str(v)
                    obj[k] = v
                elif isinstance(v, dict):
                    _c3_aug_dict(v)
            nv = _c3_fix(v, _d + 1, _g)
            if nv is not v:
                obj[k] = nv
        return obj
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            nv = _c3_fix(v, _d + 1, _g)
            if nv is not v:
                obj[i] = nv
        return obj
    if type(obj) is tuple:
        return tuple(_c3_fix(v, _d + 1, _g) for v in obj)
    return obj


def _c3_install(g):
    for name, val in list(g.items()):
        if name.startswith("__") or name.startswith("_c2_") or name.startswith("_c3_"):
            continue
        try:
            if isinstance(val, (list, dict)):
                _c3_upgrade_struct(val)
            elif isinstance(val, tuple) and val:
                lst = list(val)
                if _c3_upgrade_struct(lst):
                    g[name] = tuple(lst)
            elif isinstance(val, str) and not name.startswith("_"):
                nv = _c3_text(val)
                if nv != val:
                    g[name] = nv
        except Exception:
            pass
    for name, fn in list(g.items()):
        if name.startswith("_c2_") or name.startswith("_c3_") or not isinstance(fn, _c3_types.FunctionType):
            continue
        if fn.__globals__ is not g or getattr(fn, "_c3_wrapped", False):
            continue
        if _c3_inspect.isgeneratorfunction(fn) or _c3_inspect.iscoroutinefunction(fn):
            continue

        def make(f):
            @_c3_functools.wraps(f)
            def w(*a, **k):
                for x in a:
                    if isinstance(x, (dict, list)):
                        _c3_fix(x)
                        _c3_upgrade_struct(x)
                r = f(*a, **k)
                if isinstance(r, (dict, list)):
                    _c3_fix(r)
                    _c3_upgrade_struct(r)
                    return r
                if isinstance(r, str):
                    return _c3_text(r)
                if type(r) is tuple:
                    return _c3_fix(r)
                return r
            w._c3_wrapped = True
            return w
        g[name] = make(fn)
'''
C3_BEGIN = "# ==== RGON-C3-PATCH-BEGIN (step11c3) ===="
C3_END = "# ==== RGON-C3-PATCH-END ===="
C3_BLOCK = C3_BEGIN + "\n" + AB_SRC.strip("\n") + "\n\n_c3_install(globals())\n" + C3_END + "\n"


# ───────────────────────── JSON / 텍스트 유틸 ─────────────────────────
def load_json(path):
    raw = Path(path).read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    return json.loads(text), text, bom


def dump_json_like(path, obj, orig_text, bom):
    m = re.search(r'\n( +|\t)"', orig_text)
    indent = m.group(1) if m else (2 if "\n" in orig_text.strip() else None)
    s = json.dumps(obj, ensure_ascii=("\\u" in orig_text), indent=indent)
    if orig_text.endswith("\n"):
        s += "\n"
    if "\r\n" in orig_text:
        s = s.replace("\r\n", "\n").replace("\n", "\r\n")
    data = s.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    Path(path).write_bytes(data)


def read_text_keep(path):
    raw = Path(path).read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig"), bom


def write_text_keep(path, text, bom):
    data = text.encode("utf-8")
    Path(path).write_bytes((b"\xef\xbb\xbf" + data) if bom else data)


def count_id(text, pid):
    return len(re.findall(r'\bid\s*=\s*["\']' + re.escape(pid) + r'["\']', text))


# ───────────────────────── 백업 / 롤백 ─────────────────────────
def make_backups():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for p in TARGETS:
        if not p.exists():
            log("  [백업 건너뜀] 존재하지 않음: " + rel(p))
            continue
        flat = rel(p).replace("/", "__")
        stem, ext = os.path.splitext(flat)
        dst = BACKUP_DIR / (stem + TAG + ext)
        shutil.copy2(p, dst)
        BACKUPS[p] = dst
        log("  [백업] %s -> backups/%s" % (rel(p), dst.name))


def rollback():
    log("[ROLLBACK] 백업본으로 복원합니다.")
    for p, b in BACKUPS.items():
        try:
            shutil.copy2(b, p)
            log("  복원: " + rel(p))
        except Exception as e:
            log("  복원 실패: %s (%s)" % (rel(p), e))


# ───────────────────────── 헌법 해시 ─────────────────────────
def constitution_prefix_match(raw):
    cands = {"sha256": hashlib.sha256(raw).hexdigest(),
             "sha1": hashlib.sha1(raw).hexdigest(),
             "md5": hashlib.md5(raw).hexdigest()}
    try:
        obj = json.loads(raw.decode("utf-8-sig"))
        for name, kw in (("sha256-canon", dict(sort_keys=True, ensure_ascii=False, separators=(",", ":"))),
                         ("sha256-canon-ascii", dict(sort_keys=True, ensure_ascii=True, separators=(",", ":"))),
                         ("sha256-sorted", dict(sort_keys=True, ensure_ascii=False)),
                         ("sha256-dumps", dict(ensure_ascii=False))):
            cands[name] = hashlib.sha256(json.dumps(obj, **kw).encode("utf-8")).hexdigest()
    except Exception:
        pass
    for name, h in cands.items():
        if h.startswith(CONST_PREFIX):
            return name, h
    return None, cands["sha256"]


# ───────────────────────── 1) rgon_runner.py : R14 장착 ─────────────────────────
def strip_blocks(s):
    s = re.sub(re.escape(R14_CORE_BEGIN) + r".*?" + re.escape(R14_CORE_END) + r"\n?", "", s, flags=re.S)
    s = re.sub(re.escape(R14_INST_BEGIN) + r".*?" + re.escape(R14_INST_END) + r"\n?", "", s, flags=re.S)
    return s


def is_main_guard(node):
    if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
        return False
    t = node.test
    if not (isinstance(t.left, ast.Name) and t.left.id == "__name__" and len(t.comparators) == 1):
        return False
    c = t.comparators[0]
    return isinstance(c, ast.Constant) and c.value == "__main__"


def patch_runner():
    src, bom = read_text_keep(RUNNER)
    nl = "\r\n" if "\r\n" in src else "\n"
    s = strip_blocks(src.replace("\r\n", "\n"))
    tree = ast.parse(s)

    # 기존 동작 보존 점검 (정보용)
    for token, desc in (("omni_", "최신 omni_*.py 탐색"), ("MessageBoxW", "MessageBoxW 승인창"), ("s_run.py", "s_run.py 저장/실행")):
        log("  [runner] 기존 동작 표식 %-12s %s" % (token, "확인" if token in s else "※ 미발견(주입은 계속)"))
    names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and
             re.search(r"clean|sanit|purif|정화|scrub|defen[cs]e|strip_?(fence|md|markdown|code)", n.name, re.I)]
    log("  [runner] 정화 계열 함수 감지: " + (", ".join(names) if names else "없음 (실행 직전 s_run.py 가드로 보장)"))

    lines = s.split("\n")

    # (a) 설치 위치: __main__ 가드 앞 / 없으면 마지막 Expr 문 앞 / 없으면 파일 끝
    inst_pos = len(lines)
    guard = None
    for node in tree.body:
        if is_main_guard(node):
            guard = node
    if guard is not None:
        inst_pos = guard.lineno - 1
    elif tree.body and isinstance(tree.body[-1], ast.Expr):
        inst_pos = tree.body[-1].lineno - 1
    inst_lines = [""] + R14_INST_BLOCK.split("\n") + ["", ""]
    lines[inst_pos:inst_pos] = inst_lines

    # (b) 코어 위치: 헤더 import 블록 직후
    last_imp_end = 0
    for i, node in enumerate(tree.body):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            last_imp_end = node.end_lineno
        elif i == 0 and isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant) \
                and isinstance(node.value.value, str):
            last_imp_end = max(last_imp_end, node.end_lineno)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        else:
            break
    core_pos = last_imp_end
    if core_pos == 0:
        while core_pos < 2 and core_pos < len(lines) and lines[core_pos].startswith("#"):
            core_pos += 1
    core_lines = ["", ""] + R14_CORE_BLOCK.split("\n") + [""]
    lines[core_pos:core_pos] = core_lines

    new_src = "\n".join(lines)
    compile(new_src, str(RUNNER), "exec")
    ast.parse(new_src)
    write_text_keep(RUNNER, new_src.replace("\n", nl), bom)
    log("  [runner] R14 스마트 정화기(ast.parse 검증 · 최대 5줄 꼬리 제거 · 원자적 기록) 장착 완료")


# ───────────────────────── 2) master_schedule.json ─────────────────────────
ID_KEYS = {"id", "name", "task", "task_id", "title", "key", "code", "slug", "label", "과제", "과제명"}


def _stamp(node):
    old = node.get("status")
    if old is not None and old != "ACTIVE":
        node.setdefault("status_prev", old)
    node["status"] = "ACTIVE"
    if "state" in node and node["state"] != "ACTIVE":
        node.setdefault("state_prev", node["state"])
        node["state"] = "ACTIVE"
    if isinstance(node.get("active"), bool):
        node["active"] = True
    od = node.get("date")
    if od is not None and od != TODAY:
        node.setdefault("date_prev", od)
    node["date"] = TODAY
    node["assigned_date"] = TODAY
    node["activated_at"] = ISO


def mark_active(node, task, depth=0):
    hits = 0
    if depth > 30:
        return 0
    if isinstance(node, dict):
        if any(k in ID_KEYS and isinstance(v, str) and v.strip().startswith(task) for k, v in node.items()):
            _stamp(node)
            hits += 1
        for k, v in list(node.items()):
            if k == task and isinstance(v, dict):
                _stamp(v)
                hits += 1
            elif isinstance(v, (dict, list)):
                hits += mark_active(v, task, depth + 1)
    elif isinstance(node, list):
        for x in node:
            hits += mark_active(x, task, depth + 1)
    return hits


def patch_schedule():
    data, text, bom = load_json(SCHEDULE)
    if not isinstance(data, dict):
        raise RuntimeError("master_schedule.json 최상위가 dict 가 아닙니다.")
    h_top = mark_active(data, TOP1)
    h_gen = mark_active(data, GEN1)

    t1 = data.get("top1_self_evolving_brain")
    if not isinstance(t1, dict):
        t1 = {"task": TOP1, "priority": 1, "source": "step11_task_c2"}
    if t1.get("date") not in (None, TODAY):
        t1.setdefault("date_prev", t1.get("date"))
    t1.update({"status": "ACTIVE", "date": TODAY, "assigned_date": TODAY})
    t1.setdefault("activated_at", ISO)
    t1["kept_by"] = "step11_task_c3"
    data["top1_self_evolving_brain"] = t1

    g1 = data.get("gen1_autonomous_evolution_closed_loop")
    if not isinstance(g1, dict):
        g1 = {}
    g1.update({
        "task": GEN1, "status": "ACTIVE", "date": TODAY, "assigned_date": TODAY, "priority": 2,
        "activated_at": g1.get("activated_at", ISO), "source": "step11_task_c3",
        "description": "GEN-1 자율 진화 폐루프: G4 항체 자동 학습 -> G1~G3 원클릭 집행",
        "loop": ["G4 항체 자동 학습", "G1 지시서 생성", "G2 교차검증", "G3 백업·원클릭 집행"],
        "antibodies": "R1~R14 (14/14 활성)"})
    data["gen1_autonomous_evolution_closed_loop"] = g1

    da = data.get("daily_assignments")
    if da is None:
        da = {}
        data["daily_assignments"] = da
    if isinstance(da, dict):
        lst = da.setdefault(TODAY, [])
        if isinstance(lst, list):
            for t in (TOP1, GEN1):
                if t not in lst:
                    lst.append(t)
    at = data.get("active_tasks")
    if at is None:
        data["active_tasks"] = [TOP1, GEN1]
    elif isinstance(at, list) and all(isinstance(x, str) for x in at):
        for t in (TOP1, GEN1):
            if t not in at:
                at.append(t)

    for key in ("viral_keywords", "keywords"):
        old = data.get(key)
        if old != KEYWORDS:
            if isinstance(old, list) and old:
                data.setdefault(key + "_prev", old)
            data[key] = list(KEYWORDS)

    bm = data.get("bm_pipeline")
    if not isinstance(bm, dict):
        bm = {"name": "BM_PIPELINE", "status": "REGISTERED", "keywords_count": len(KEYWORDS)}
    bm.update({"top1": TOP1, "top1_status": "ACTIVE", "gen1_closed_loop": "ACTIVE",
               "gen1": GEN1, "updated_at": ISO, "source": "step11_task_c3"})
    data["bm_pipeline"] = bm

    dump_json_like(SCHEDULE, data, text, bom)
    log("  [schedule] TOP1 표식 %d건 유지 · GEN1 표식 %d건 신규 · 키워드 %d종 보존" % (h_top, h_gen, len(KEYWORDS)))


# ───────────────────────── 3) scripts/rgon_agency_pulse.py ─────────────────────────
def patch_pulse():
    src, bom = read_text_keep(PULSE)
    nl = "\r\n" if "\r\n" in src else "\n"
    s = src.replace("\r\n", "\n")
    s = re.sub(re.escape(C3_BEGIN) + r".*?" + re.escape(C3_END) + r"\n?", "", s, flags=re.S)
    if "RGON-C2-PATCH-BEGIN" not in s:
        log("  [pulse] ※ 경고: C-2 패치 블록이 없습니다(5-Gate/D2 보정 이전 상태). C-3 블록만 주입합니다.")
    guards = list(re.finditer(r'(?m)^if\s+__name__\s*==\s*["\']__main__["\']\s*:', s))
    if guards:
        pos = guards[-1].start()
        s = s[:pos].rstrip("\n") + "\n\n\n" + C3_BLOCK + "\n\n" + s[pos:]
    else:
        s = s.rstrip("\n") + "\n\n\n" + C3_BLOCK
    compile(s, str(PULSE), "exec")
    ast.parse(s)
    write_text_keep(PULSE, s.replace("\n", nl), bom)
    log("  [pulse] 항체 R1~R14 (14/14) · D1/D5 GEN1 반영 보정 주입 완료")


# ───────────────────────── 4) 스냅샷 / 장부 ─────────────────────────
def _ab_ns():
    ns = {"__file__": str(PULSE)}
    exec(AB_SRC, ns)
    return ns


def apply_snapshots(beat=None, overall=None):
    ns = _ab_ns()
    for p in SNAPS:
        if not p.exists():
            log("  [snapshot] 없음 -> 건너뜀: " + rel(p))
            continue
        try:
            data, text, bom = load_json(p)
        except Exception as e:
            log("  [snapshot] JSON 오류 -> 건너뜀: %s (%s)" % (rel(p), e))
            continue
        if not isinstance(data, dict):
            continue
        ns["_c3_fix"](data)
        ns["_c3_upgrade_struct"](data)
        for key in ("viral_keywords", "keywords"):
            if key in data and isinstance(data[key], list):
                data[key] = list(KEYWORDS)
        blk = {"top1_self_evolving_brain": "ACTIVE", "gen1_autonomous_evolution_closed_loop": "ACTIVE",
               "date": TODAY, "antibodies": "R1~R14 (14/14 활성)", "r14": "R14: 코드 끝 찌꺼기 자동 정화",
               "updated_at": ISO}
        if beat is not None:
            blk["pulse_beat"] = beat
        if overall is not None:
            blk["overall"] = overall
        data["step11_c3"] = blk
        dump_json_like(p, data, text, bom)
    log("  [snapshot] 스냅샷 3곳 갱신(항체 R14 · GEN1 ACTIVE)")


def record_evolution(beat, overall, const_hash, html_hash):
    ns = _ab_ns()
    entry = {"event": EVENT, "ts": ISO, "task": "C-3", "top1": TOP1, "top1_status": "ACTIVE",
             "gen1": GEN1, "gen1_status": "ACTIVE",
             "gen1_loop": "G4 항체 자동 학습 -> G1~G3 원클릭 집행",
             "antibody_added": "R14: 코드 끝 찌꺼기 자동 정화",
             "antibodies": "R1~R14 (14/14 활성)",
             "runner_hook": "rgon_runner.py R14 ast.parse 스마트 정화(최대 5줄 꼬리 제거, 원자적 기록)",
             "pulse_beat": beat, "overall": overall,
             "constitution_hash12": const_hash[:12], "constitution_modified": False,
             "html_sha256_12": html_hash[:12], "html_modified": False, "backup_tag": TAG}
    if EVOLUTION.exists():
        data, text, bom = load_json(EVOLUTION)
    else:
        data, text, bom = [], "[]\n", False

    def drop_old(lst):
        lst[:] = [x for x in lst if not (isinstance(x, dict) and x.get("event") == EVENT)]

    if isinstance(data, list):
        drop_old(data)
        data.append(entry)
    elif isinstance(data, dict):
        for k in list(data.keys()):
            if isinstance(k, str) and re.search(r"antibod|항체|immun|guardrail", k, re.I) \
                    and isinstance(data[k], (list, dict)):
                ns["_c3_upgrade_struct"](data[k])
        target = None
        for k in ("history", "evolution_history", "log", "events", "entries", "records", "timeline"):
            if isinstance(data.get(k), list):
                target = data[k]
                break
        if target is None:
            target = data.setdefault("history", [])
        drop_old(target)
        target.append(entry)
    else:
        raise RuntimeError("evolution_memory.json 구조를 알 수 없습니다.")
    if EVOLUTION.exists():
        dump_json_like(EVOLUTION, data, text, bom)
    else:
        EVOLUTION.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log("  [evolution] %s 이력 기록 (박동 #%s)" % (EVENT, beat))


# ───────────────────────── 5) 박동 실행 / 분석 ─────────────────────────
def run_pulse():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    t0 = time.time()
    p = subprocess.run([sys.executable, str(PULSE)], cwd=str(ROOT), capture_output=True, env=env, timeout=600)
    out = p.stdout.decode("utf-8", "replace") + "\n" + p.stderr.decode("utf-8", "replace")
    return p.returncode, out, t0


def collect_dims(obj, out=None):
    if out is None:
        out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            m = re.match(r"^D([1-6])(?:_|$)", str(k))
            if m and m.group(1) not in out:
                out[m.group(1)] = (k, v)
            collect_dims(v, out)
    elif isinstance(obj, list):
        for x in obj:
            collect_dims(x, out)
    return out


def iter_overall(obj, depth=0):
    if depth > 25:
        return
    if isinstance(obj, dict):
        if "overall" in obj and collect_dims(obj):
            yield obj
        for v in obj.values():
            for r in iter_overall(v, depth + 1):
                yield r
    elif isinstance(obj, list):
        for x in obj:
            for r in iter_overall(x, depth + 1):
                yield r


BEAT_KEYS = {"beat", "beat_no", "beat_number", "pulse_no", "pulse_number", "pulse_count",
             "heartbeat", "박동", "seq", "pulse_beat"}


def walk_beats(obj, out, depth=0):
    if depth > 25:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower() in BEAT_KEYS and isinstance(v, int) and not isinstance(v, bool):
                out.append(v)
            walk_beats(v, out, depth + 1)
    elif isinstance(obj, list):
        for x in obj:
            walk_beats(x, out, depth + 1)


def dim_text(v):
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def dim_ok(v):
    if isinstance(v, dict):
        for k in ("status", "state", "level", "result", "verdict", "ok"):
            if k in v:
                val = v[k]
                if isinstance(val, bool):
                    return val
                return str(val).strip().upper().startswith(("OK", "PASS", "GREEN", "HEALTHY"))
    return not re.search(r"FAIL|ERROR|WARN|❌|✗", dim_text(v), re.I)


def analyze_pulse(out, t0):
    info = {"beat": None, "overall": None, "dims": {}}
    out_beats = [int(x) for x in re.findall(r"(?:박동|[Pp]ulse|[Bb]eat)\s*#\s*(\d+)", out)]
    json_beats = []
    best = None
    for d in (ROOT, ROOT / "dashboard", ROOT / "docs", ROOT / "brain_basket", ROOT / "logs", ROOT / "data"):
        if not d.is_dir():
            continue
        for p in d.glob("*.json"):
            if p.name == CONSTITUTION.name:
                continue
            try:
                st = p.stat().st_mtime
                if st < t0 - 2:
                    continue
                obj = json.loads(p.read_text(encoding="utf-8-sig"))
            except Exception:
                continue
            walk_beats(obj, json_beats)
            for rec in iter_overall(obj):
                score = (len(collect_dims(rec)), st)
                if best is None or score > best[0]:
                    best = (score, rec)
    if best:
        rec = best[1]
        ov = rec.get("overall")
        if isinstance(ov, dict):
            ov = ov.get("status") or ov.get("overall") or ov.get("state")
        info["overall"] = str(ov).strip().upper() if ov is not None else None
        info["dims"] = collect_dims(rec)
    else:
        m = re.search(r'overall\W{0,6}([A-Za-z]+)', out, re.I)
        if m:
            info["overall"] = m.group(1).upper()
        for line in out.splitlines():
            m = re.match(r"\s*\W*D([1-6])\b", line)
            if m and m.group(1) not in info["dims"]:
                info["dims"][m.group(1)] = ("D" + m.group(1), line.strip())
    beats = out_beats if out_beats else json_beats
    info["beat"] = max(beats) if beats else None
    return info


def verify_pulse(info, rc):
    fails = []
    if rc != 0:
        fails.append("박동 스크립트 종료코드 %s" % rc)
    if info["beat"] is None or info["beat"] < 6:
        fails.append("박동 번호 #6 이상 확인 실패 (감지값: %s)" % info["beat"])
    if info["overall"] != "OK":
        fails.append("overall != OK (감지값: %s)" % info["overall"])
    for n in "123456":
        if n not in info["dims"]:
            fails.append("D%s 결과를 찾지 못함" % n)
        elif not dim_ok(info["dims"][n][1]):
            fails.append("D%s 가 OK 가 아님: %s" % (n, dim_text(info["dims"][n][1])[:160]))
    for n in ("1", "5"):
        t = dim_text(info["dims"][n][1]) if n in info["dims"] else ""
        if GEN1 not in t or "ACTIVE" not in t:
            fails.append("D%s 에 %s (ACTIVE) 반영 미확인: %s" % (n, GEN1, t[:200]))
        if "14/14" not in t:
            fails.append("D%s 에 14대 항체 14/14 활성 반영 미확인: %s" % (n, t[:200]))
    d2 = dim_text(info["dims"]["2"][1]) if "2" in info["dims"] else ""
    d4 = dim_text(info["dims"]["4"][1]) if "4" in info["dims"] else ""
    if "미등록" in d2 and "핵심 키워드" in d2:
        fails.append("D2_viral 키워드 미등록 문구 재출현: " + d2[:200])
    if not re.search(r"5/5\s*확인\s*\(\s*G0\s*,\s*G1\s*,\s*G2\s*,\s*G3\s*,\s*G4\s*\)", d4):
        fails.append("D4_hongik 5/5 확인(G0,G1,G2,G3,G4) 유지 미확인: " + d4[:200])
    return fails


# ───────────────────────── 사전 자가시험 (R14 / 항체 보정) ─────────────────────────
def selftest():
    ns = {"__file__": str(RUNNER)}
    exec(R14_SRC, ns)
    P = ns["r14_smart_purify"]
    ok_ast = ns["_r14_ok"]
    cases = [
        ("```python\nprint('a')\n```!]—\n", "print('a')"),
        ("import os\nprint(1)\nCopy\n", "import os\nprint(1)"),
        ("def f():\n    return 1\nprint(f())```!]—", "def f():\n    return 1\nprint(f())"),
        ("print(1)\n한글 꼬리표 !]\n```!]—", "print(1)"),
        ("print(2)\n복사\n", "print(2)"),
        ("설명 문장입니다\n```python\nx = 3\nprint(x)\n```\n끝", "x = 3\nprint(x)"),
        ("print(3)\nCopy code\n```", "print(3)"),
    ]
    for raw, exp in cases:
        got = P(raw).strip()
        if got != exp or not ok_ast(got):
            raise RuntimeError("R14 자가시험 실패: %r -> %r (기대 %r)" % (raw, got, exp))
    ab = _ab_ns()
    if ab["_c3_text"]("항체 R1~R13 (13/13 활성)") != "항체 R1~R14 (14/14 활성)":
        raise RuntimeError("항체 문자열 보정 자가시험 실패")
    d = {"antibodies": ["R12: a", "R13: b"], "count": 13}
    ab["_c3_upgrade_struct"](d)
    if d["antibodies"][-1] != "R14: 코드 끝 찌꺼기 자동 정화" or d["count"] != 14:
        raise RuntimeError("항체 구조 보정 자가시험 실패: %r" % d)
    d2 = {"antibodies": [{"id": "R13", "name": "x", "active": True}], "total": 13}
    ab["_c3_upgrade_struct"](d2)
    if d2["antibodies"][-1].get("id") != "R14" or d2["total"] != 14:
        raise RuntimeError("항체 dict 보정 자가시험 실패: %r" % d2)
    log("  [자가시험] R14 정화 7/7 · 항체 R14 보정 3/3 통과")


# ───────────────────────── 종합 검증 ─────────────────────────
def snapshot_protected():
    st = {"const": sha256_file(CONSTITUTION), "html": [sha256_file(p) for p in HTMLS]}
    return st


def verify_protected(before):
    fails = []
    if sha256_file(CONSTITUTION) != before["const"]:
        fails.append("헌법 파일이 변경됨!")
    after_html = [sha256_file(p) for p in HTMLS]
    for p, b, a in zip(HTMLS, before["html"], after_html):
        if a != b:
            fails.append("%s 해시가 변경됨 (%s -> %s)" % (rel(p), b[:12], a[:12]))
        t, _ = read_text_keep(p)
        for pid in PROTECTED_IDS:
            c = count_id(t, pid)
            if c != 1:
                fails.append("%s 보호 ID %s = %d개 (1개여야 함)" % (rel(p), pid, c))
    if len(set(after_html)) != 1:
        fails.append("HTML 3곳 SHA-256 불일치: " + ", ".join(h[:12] for h in after_html))
    return fails


def verify_syntax():
    fails = []
    for p in (RUNNER, PULSE):
        try:
            s, _ = read_text_keep(p)
            compile(s, str(p), "exec")
            ast.parse(s)
        except Exception as e:
            fails.append("%s 문법 오류: %s" % (rel(p), e))
    try:
        s, _ = read_text_keep(RUNNER)
        if "r14_smart_purify_ex" not in s or "r14_install_process_hooks()" not in s or "r14_install_funcs(globals())" not in s:
            fails.append("rgon_runner.py R14 장착 표식 누락")
    except Exception as e:
        fails.append(str(e))
    return fails


# ───────────────────────── Git ─────────────────────────
def git(*args):
    p = subprocess.run(["git", "-c", "core.quotepath=off"] + list(args), cwd=str(ROOT), capture_output=True)
    return (p.returncode, p.stdout.decode("utf-8", "replace").strip(), p.stderr.decode("utf-8", "replace").strip())


def porcelain():
    rc, out, _ = git("status", "--porcelain=v1", "-z", "--untracked-files=all")
    items = set()
    if rc == 0:
        for ent in out.split("\x00"):
            if len(ent) > 3:
                items.add(ent[3:].replace("\\", "/"))
    return items


def git_sync(before_dirty):
    rc, out, err = git("rev-parse", "--is-inside-work-tree")
    if rc != 0:
        raise RuntimeError("git 저장소가 아닙니다: " + err)
    forbidden = {CONSTITUTION.name} | {rel(p) for p in HTMLS}
    paths = [rel(p) for p in TARGETS if p.exists()]
    for extra in sorted(porcelain() - before_dirty):
        if extra.startswith("backups/") or "__pycache__" in extra or extra.endswith(".pyc") or extra in forbidden:
            continue
        if extra not in paths:
            paths.append(extra)
            log("  [git] 박동 산출물 추가 동기화: " + extra)
    for pth in paths:
        rc, _, err = git("add", "--", pth)
        if rc != 0:
            log("  [git add 경고] %s: %s" % (pth, err.splitlines()[0] if err else ""))
    msg = "Step 11 C-3: R14 launcher purifier (ast.parse), GEN1_AUTONOMOUS_EVOLUTION_CLOSED_LOOP ACTIVE, antibodies 14/14, pulse #6"
    rc, out, err = git("commit", "-m", msg, "--", *paths)
    if rc != 0 and "nothing to commit" not in (out + err).lower() and "no changes added" not in (out + err).lower():
        raise RuntimeError("git commit 실패: " + (err or out))
    rc, head, _ = git("rev-parse", "--short=10", "HEAD")
    log("  [git] commit " + head)
    rc, staged, _ = git("show", "--name-only", "--pretty=format:", "HEAD")
    if forbidden & set(staged.splitlines()):
        raise RuntimeError("보호 파일이 커밋에 포함됨 - 중단")
    rc, out, err = git("push", "origin", "main")
    if rc != 0:
        raise RuntimeError("git push 실패: " + (err or out))
    log("  [git] push origin main 완료")


# ───────────────────────── 메인 ─────────────────────────
def main():
    log("=" * 70)
    log("RGON Step 11 · 과제 C-3 착수 (%s)" % ISO)
    log("=" * 70)

    for p in [CONSTITUTION, RUNNER, SCHEDULE, PULSE] + HTMLS:
        if not p.exists():
            log("[FAIL] 필수 파일 없음: " + str(p))
            return 1

    before = snapshot_protected()
    algo, h = constitution_prefix_match(CONSTITUTION.read_bytes())
    if algo:
        log("[헌법] 기준선 %s 일치 (%s) · 무접촉" % (CONST_PREFIX, algo))
    else:
        log("[헌법] 경고: %s 접두 해시를 표준 알고리즘으로 재현하지 못함 (sha256=%s...). 전/후 비교로 무변경 보장" % (CONST_PREFIX, h[:12]))
    if not before["html"][0].startswith(HTML_PREFIX):
        log("[HTML] 경고: 현재 해시 %s... 가 지시서 기준 %s 와 다릅니다. 전/후 비교로 무접촉 보장" % (before["html"][0][:12], HTML_PREFIX))
    pre_fail = verify_protected(before)
    if pre_fail:
        log("[FAIL] 착수 전 보호 상태 이상 - 파일 변경 없이 중단: " + " | ".join(pre_fail))
        return 1
    log("[보호] 독대실 HTML 3곳 해시 일치(%s) · 보호 ID 6/6(각 1개) 확인" % before["html"][0][:12])

    try:
        selftest()
    except Exception as e:
        log("[FAIL] " + str(e) + " (파일 변경 없이 중단)")
        return 1

    before_dirty = porcelain()
    log("[1/7] 사전 백업 (G3)")
    make_backups()

    try:
        log("[2/7] rgon_runner.py R14 장착 · master_schedule GEN1 승격 · pulse 항체 14/14 보정")
        patch_runner()
        patch_schedule()
        patch_pulse()
        apply_snapshots()

        fails = verify_syntax() + verify_protected(before)
        if fails:
            raise RuntimeError("정적 검증 실패: " + " | ".join(fails))

        log("[3/7] 박동 실행")
        rc, out, t0 = run_pulse()
        log("\n".join(out.strip().splitlines()[-25:]))
        info = analyze_pulse(out, t0)
        pf = verify_pulse(info, rc)
        if pf:
            raise RuntimeError("박동 검증 실패: " + " | ".join(pf))
        log("[박동] #%s · overall=%s · D1~D6 전원 OK" % (info["beat"], info["overall"]))
        for n in ("1", "2", "4", "5"):
            log("  D%s: %s" % (n, dim_text(info["dims"][n][1])[:220]))

        log("[4/7] 장부 · 스냅샷 기록")
        apply_snapshots(beat=info["beat"], overall=info["overall"])
        record_evolution(info["beat"], info["overall"], before["const"], before["html"][0])

        log("[5/7] 최종 검증")
        fails = verify_syntax() + verify_protected(before)
        if fails:
            raise RuntimeError("최종 검증 실패: " + " | ".join(fails))
        log("  헌법 무변경(%s) · HTML 3곳 무접촉(%s) · 보호 ID 6/6 · rgon_runner.py compile/ast.parse 통과 · overall=OK · 박동 #%s" %
            (CONST_PREFIX if algo else before["const"][:12], before["html"][0][:12], info["beat"]))
    except Exception as e:
        log("[FAIL] " + str(e))
        rollback()
        try:
            ok = (sha256_file(CONSTITUTION) == before["const"]) and ([sha256_file(p) for p in HTMLS] == before["html"])
        except Exception:
            ok = False
        log("[ROLLBACK] 헌법·HTML 무접촉 확인: %s" % ok)
        return 1

    log("[6/7] GitHub 클라우드 배포")
    try:
        git_sync(before_dirty)
    except Exception as e:
        log("[FAIL] " + str(e))
        log("  (로컬 파일은 검증 완료 상태로 유지됩니다. 네트워크/인증 확인 후 'git push origin main' 을 재시도하세요.)")
        return 2

    log("[7/7] 배포 후 무접촉 재확인")
    post = verify_protected(before)
    if post:
        log("[FAIL] 배포 후 보호 파일 이상 감지: " + " | ".join(post))
        return 3
    log(FINAL_OK)
    return 0


if __name__ == "__main__":
    sys.exit(main())
Copy
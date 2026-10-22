import glob,os,ctypes,subprocess


# ==== RGON-R14-CORE-BEGIN (step11c3) ====
# R14: 코드 끝 스트리밍 찌꺼기 자동 정화 (ast.parse 검증) — 제14호 항체
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
        notes.append("fence//!]— edge tags removed")
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

r14_install_process_hooks()
# ==== RGON-R14-CORE-END ====

f=sorted(glob.glob(chr(39)+'omni_*.py'[1:]) if 0 else glob.glob('omni_*.py')+glob.glob(os.path.expanduser('~/Downloads/omni_*.py')),key=os.path.getmtime)[-1]
t=open(f,encoding='utf-8').read().replace('Copy','').strip()
open('s_run.py','w',encoding='utf-8').write(t+'\n')
if ctypes.windll.user32.MessageBoxW(0,os.path.basename(f),'RGON RUN',0x40024)==6: subprocess.run(['python','-X','utf8','s_run.py'])


# ==== RGON-R14-INSTALL-BEGIN (step11c3) ====
r14_install_funcs(globals())
# ==== RGON-R14-INSTALL-END ====



# [STEP11_E3_TG_REPORT_HOOK]
def _send_runner_tg_report(fname, returncode):
    try:
        import urllib.request, urllib.parse
        env_p = os.path.join(r"C:\Users\sangi\Downloads\shin-agent", ".env.telegram.local")
        if not os.path.isfile(env_p):
            return
        tok, cid = None, None
        for ln in open(env_p, encoding="utf-8").read().splitlines():
            if ln.startswith("TELEGRAM_BOT_TOKEN="): tok = ln.split("=", 1)[1].strip()
            elif ln.startswith("TELEGRAM_CHAT_ID="): cid = ln.split("=", 1)[1].strip()
        if tok and cid:
            st = "✅ 성공" if returncode == 0 else f"⚠️ 코드 {returncode}"
            msg = f"👑 [RGON_Run.bat 실행 완료]\n📄 파일: {fname}\n📊 결과: {st}"
            data = urllib.parse.urlencode({"chat_id": cid, "text": msg}).encode("utf-8")
            urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{tok}/sendMessage", data=data), timeout=8)
    except Exception:
        pass

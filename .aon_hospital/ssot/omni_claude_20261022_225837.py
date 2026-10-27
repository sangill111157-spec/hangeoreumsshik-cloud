#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_finish_step2_step3.py  (Windows / Python 3 표준 라이브러리 전용)

대시보드 오픈 / 무창 패치 / 8765 브리지 저장 / 아카이브 정리 / 기억 저장소 스캔 / 텔레그램 마감 보고
- 프로세스 종료 로직 없음 (실행 여부만 조회, 기동만 수행)
- 수정되는 모든 파일은 *.bak_YYYYmmdd_HHMMSS 로 백업
"""
import ast
import base64
import configparser
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

if os.name != "nt":
    sys.exit("이 스크립트는 Windows 전용입니다.")

CNW = 0x08000000        # CREATE_NO_WINDOW (백그라운드 보조 작업 전용, 대시보드 오픈에는 사용 안 함)
DETACHED = 0x00000008
NEWGRP = 0x00000200

ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
DESKTOP = Path(r"C:\Users\sangi\Desktop")
DASH = ROOT / "rgon_alpha_audience.html"
SELF = Path(__file__).resolve()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

WATCHER = ROOT / "rgon_auto_watcher.py"
HEARTBEAT = ROOT / "rgon_agency_heartbeat.py"
TELEGRAM = ROOT / "rgon_telegram_bridge.py"
BRIDGE = ROOT / "rgon_bridge_8765.py"
PATCH_TARGETS = [WATCHER, HEARTBEAT, TELEGRAM]
BRIEFING_TASKS = [r"RGON_Morning_Briefing_0700", r"\ConnectAI_Daily_Briefing"]
KEYWORDS = ("memory", "handover", "state", "status", "constitution", "briefing", "log", "history")
KEEP_NAMES = {SELF.name.lower(), "s_run.py"}


def say(msg=""):
    print(msg, flush=True)


def section(title):
    say("")
    say("=" * 78)
    say(title)
    say("=" * 78)


def hidden_si():
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0
    return si


def run_hidden(cmd, timeout=60):
    """보조 작업(조회/하트비트/텔레그램)을 창 없이 실행 → (rc, stdout, stderr)"""
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout, creationflags=CNW,
                           startupinfo=hidden_si(), cwd=str(ROOT))
        dec = lambda b: (b or b"").decode("utf-8", "replace")
        return p.returncode, dec(p.stdout), dec(p.stderr)
    except Exception as e:
        return -1, "", f"{type(e).__name__}: {e}"


def ps(script, timeout=60):
    enc = base64.b64encode(("[Console]::OutputEncoding=[Text.Encoding]::UTF8;" + script).encode("utf-16le")).decode()
    return run_hidden(["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden",
                       "-ExecutionPolicy", "Bypass", "-EncodedCommand", enc], timeout=timeout)


def backup(path):
    b = path.with_name(path.name + f".bak_{STAMP}")
    shutil.copy2(path, b)
    return b


def human(n):
    n = float(n)
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return f"{int(n)}B" if u == "B" else f"{n:.1f}{u}"
        n /= 1024


def guard(name, fn, default=None):
    try:
        return fn()
    except Exception:
        say(f"  [오류] {name}\n" + traceback.format_exc(limit=3))
        return default


# ───────────────────── 1. 대시보드 ─────────────────────
def find_chrome():
    for base in (os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                 os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
                 os.environ.get("LOCALAPPDATA", "")):
        if base:
            c = Path(base) / "Google" / "Chrome" / "Application" / "chrome.exe"
            if c.exists():
                return c
    return None


def git_remote():
    cfg = ROOT / ".git" / "config"
    if not cfg.exists():
        return "(.git/config 없음)"
    text = cfg.read_text(encoding="utf-8", errors="replace")
    try:
        cp = configparser.ConfigParser(strict=False, interpolation=None)
        cp.read_string(text)
        return cp.get('remote "origin"', "url")
    except Exception:
        m = re.search(r'\[remote "origin"\][^\[]*?url\s*=\s*(\S+)', text, re.S)
        return m.group(1) if m else "(remote origin URL 없음)"


def step_dashboard():
    section("[1] 대시보드 바로가기 생성 및 화면 오픈")
    res = {"shortcuts": 0, "opened": False, "remote": ""}
    if not DASH.exists():
        say(f"  [경고] 대시보드 파일이 없습니다: {DASH}")
    uri = DASH.as_uri()
    chrome = find_chrome()
    DESKTOP.mkdir(parents=True, exist_ok=True)

    if chrome:
        body = f'@echo off\r\nstart "" "{chrome}" --app="{uri}" --new-window --window-size=1440,920\r\nexit\r\n'
    else:
        body = f'@echo off\r\nstart "" "{DASH}"\r\nexit\r\n'
    bat = DESKTOP / "👑_RGON_대시보드_열기.bat"
    try:
        bat.write_text(body, encoding="mbcs", errors="replace", newline="")
        say(f"  생성: {bat}")
        res["shortcuts"] += 1
    except OSError as e:
        say(f"  .bat 생성 실패: {e}")

    url_file = DESKTOP / "RGON_Dashboard.url"
    try:
        url_file.write_text(f"[InternetShortcut]\r\nURL={uri}\r\n", encoding="utf-8")
        say(f"  생성: {url_file}")
        res["shortcuts"] += 1
    except OSError as e:
        say(f"  .url 생성 실패: {e}")

    # 창 숨김 플래그 없이 오픈 (화면 전면 표시)
    try:
        os.startfile(str(DASH))
        res["opened"] = True
        say("  os.startfile 로 대시보드 오픈")
    except Exception as e:
        say(f"  os.startfile 실패: {e}")
    if chrome:
        try:
            subprocess.Popen([str(chrome), f"--app={uri}", "--new-window", "--window-size=1440,920"])
            res["opened"] = True
            say(f"  Chrome 앱 모드 오픈: {uri}")
        except Exception as e:
            say(f"  Chrome 오픈 실패: {e}")
    else:
        say("  Chrome 미설치 → 기본 브라우저만 사용")

    res["remote"] = git_remote()
    say(f"  Git remote origin URL: {res['remote']}")
    return res


# ───────────────────── 2. 무창 패치 / 브리지 / 기동 / 예약작업 ─────────────────────
MARK = "RGON_NOWINDOW_SHIM"
SHIM = '''# ---- RGON_NOWINDOW_SHIM_BEGIN (subprocess 호출 시 콘솔 창 깜빡임 방지) ----
import subprocess as _rg_sp, sys as _rg_sys
if _rg_sys.platform == "win32" and not getattr(_rg_sp, "_rgon_patched", False):
    _rg_orig_init = _rg_sp.Popen.__init__
    def _rg_init(self, *a, **kw):
        kw["creationflags"] = kw.get("creationflags", 0) | 0x08000000
        si = kw.get("startupinfo")
        if si is None:
            si = _rg_sp.STARTUPINFO()
        si.dwFlags |= _rg_sp.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        kw["startupinfo"] = si
        _rg_orig_init(self, *a, **kw)
    _rg_sp.Popen.__init__ = _rg_init
    _rg_sp._rgon_patched = True
# ---- RGON_NOWINDOW_SHIM_END ----
'''


def patch_no_window(path):
    if not path.exists():
        return "파일 없음(건너뜀)"
    src = path.read_text(encoding="utf-8-sig", errors="replace")
    if MARK in src:
        return "이미 패치됨"
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return f"원본 문법 오류로 중단: {e}"
    after = 0
    for i, node in enumerate(tree.body):
        is_doc = (i == 0 and isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant)
                  and isinstance(node.value.value, str))
        is_future = isinstance(node, ast.ImportFrom) and node.module == "__future__"
        if is_doc or is_future:
            after = node.end_lineno
        else:
            break
    lines = src.splitlines(keepends=True)
    if after and not lines[after - 1].endswith("\n"):
        lines[after - 1] += "\n"
    new_src = "".join(lines[:after]) + SHIM + "".join(lines[after:])
    try:
        ast.parse(new_src)
    except SyntaxError as e:
        return f"패치 결과 검증 실패(원본 유지): {e}"
    b = backup(path)
    path.write_text(new_src, encoding="utf-8")
    warn = [n + 1 for n, ln in enumerate(new_src.splitlines()) if re.search(r"os\.system\(|os\.popen\(|ShellExecute", ln)]
    extra = f" | 주의: os.system/ShellExecute 라인 {warn[:8]} (shim 미적용, 수동 확인)" if warn else ""
    return f"패치 완료 (백업 {b.name}){extra}"


BRIDGE_SRC = r'''# -*- coding: utf-8 -*-
# rgon_bridge_8765.py  (rgon_finish_step2_step3.py 가 생성)
# - 127.0.0.1:8765 에서만 수신, POST /api/queue 만 처리
# - "entry" 키가 포함된 JSON, 그 외 경로/메서드는 {"ok": true, "status": "ignored"}
# - ast.parse() 를 통과한 순수 Python 코드만 omni_queue_YYYYMMDD_HHMMSS.py 로 '저장'만 함 (실행/외부 호출 없음)
# - 일반 웹사이트(Origin: http/https)나 외부 Host 헤더에서 온 요청은 무시
import ast
import json
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOST, PORT = "127.0.0.1", 8765
MAX_BYTES = 1_000_000
LOCK = threading.Lock()
ALLOWED_HOSTS = {"127.0.0.1", "localhost"}


def extract_code(raw):
    text = raw.decode("utf-8", "replace").strip()
    if not text:
        return None, "empty"
    try:
        obj = json.loads(text)
    except ValueError:
        obj = None
    if obj is not None:
        if not isinstance(obj, dict):
            return None, "not_python"
        if "entry" in obj:
            return None, "entry_ignored"
        code = obj.get("code") or obj.get("text")
        if not isinstance(code, str):
            return None, "no_code"
        text = code.strip()
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return None, "not_python"
    if not tree.body:
        return None, "empty"
    return text, "ok"


def save_code(code):
    with LOCK:
        base = "omni_queue_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        p = ROOT / (base + ".py")
        n = 1
        while p.exists():
            p = ROOT / f"{base}_{n}.py"
            n += 1
        p.write_text(code + "\n", encoding="utf-8")
        return p


class H(BaseHTTPRequestHandler):
    server_version = "RgonBridge/3"

    def log_message(self, *a):
        pass

    def _send(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _trusted(self):
        host = (self.headers.get("Host") or "").split(":")[0].lower()
        origin = (self.headers.get("Origin") or "").lower()
        if host not in ALLOWED_HOSTS:
            return False
        return not origin.startswith(("http://", "https://"))

    def do_GET(self):
        self._send({"ok": True, "status": "alive", "port": PORT})

    def do_OPTIONS(self):
        self._send({"ok": True, "status": "ignored"})

    def do_POST(self):
        try:
            n = min(int(self.headers.get("Content-Length") or 0), MAX_BYTES)
        except ValueError:
            n = 0
        raw = self.rfile.read(n) if n else b""
        if self.path.split("?")[0] != "/api/queue" or not self._trusted():
            return self._send({"ok": True, "status": "ignored"})
        code, why = extract_code(raw)
        if code is None:
            return self._send({"ok": True, "status": "ignored", "reason": why})
        p = save_code(code)
        self._send({"ok": True, "status": "saved", "file": p.name})


if __name__ == "__main__":
    srv = ThreadingHTTPServer((HOST, PORT), H)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
'''


def write_bridge():
    ast.parse(BRIDGE_SRC)
    if BRIDGE.exists():
        existing = BRIDGE.read_text(encoding="utf-8-sig", errors="replace")
        if existing.strip() == BRIDGE_SRC.strip():
            return "이미 최신 버전"
        b = backup(BRIDGE)
        BRIDGE.write_text(BRIDGE_SRC, encoding="utf-8")
        return f"갱신 완료 (백업 {b.name}) ※ 이미 실행 중이면 다음 재시작부터 새 코드 적용"
    BRIDGE.write_text(BRIDGE_SRC, encoding="utf-8")
    return "신규 작성 완료"


def running_scripts():
    """실행 중인 python 계열 프로세스의 CommandLine 목록 (조회 전용)."""
    code, out, err = ps(
        "$r=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^pythonw?\\.exe$'} "
        "| Select-Object ProcessId,CommandLine);ConvertTo-Json -InputObject $r -Compress")
    try:
        data = json.loads(out)
    except ValueError:
        return []
    if isinstance(data, dict):
        data = [data]
    return [(d.get("ProcessId"), (d.get("CommandLine") or "").lower()) for d in data if isinstance(d, dict)]


def port_open(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except OSError:
        return False


def start_if_absent(script, procs, port=None):
    if not script.exists():
        return "파일 없음 → 기동 생략"
    for pid, cl in procs:
        if pid != os.getpid() and script.name.lower() in cl:
            return f"이미 실행 중 (PID {pid})"
    if port and port_open(port):
        return f"포트 {port} 이미 사용 중 → 기동 생략"
    exe = Path(sys.executable)
    pyw = exe.with_name("pythonw.exe")
    interp = pyw if pyw.exists() else exe
    logdir = ROOT / "rgon_logs"
    logdir.mkdir(exist_ok=True)
    log = open(logdir / f"{script.stem}.log", "ab")
    subprocess.Popen([str(interp), str(script)], cwd=str(ROOT), stdin=subprocess.DEVNULL,
                     stdout=log, stderr=log, creationflags=CNW | DETACHED | NEWGRP,
                     startupinfo=hidden_si(), close_fds=True)
    return f"{interp.name} 로 1개 기동"


def enable_tasks():
    out = {}
    for name in BRIEFING_TASKS:
        rc, o, e = run_hidden(["schtasks.exe", "/Query", "/TN", name], timeout=20)
        if rc != 0:
            out[name] = "등록되어 있지 않음"
            continue
        rc, o, e = run_hidden(["schtasks.exe", "/Change", "/TN", name, "/ENABLE"], timeout=20)
        out[name] = "활성화 확인(ENABLE)" if rc == 0 else f"활성화 실패: {(e or o).strip()[:80]}"
    return out


def step_patch_and_start():
    section("[2] 무창 패치 / 8765 브리지 저장 / 기동 / 아침 브리핑 예약작업")
    res = {"patch": {}, "bridge": "", "start": {}, "tasks": {}}
    for f in PATCH_TARGETS:
        res["patch"][f.name] = guard(f.name, lambda f=f: patch_no_window(f), "오류")
        say(f"  {f.name}: {res['patch'][f.name]}")
    res["bridge"] = guard("bridge", write_bridge, "오류")
    say(f"  {BRIDGE.name}: {res['bridge']}")
    procs = running_scripts()
    res["start"]["watcher"] = guard("watcher 기동", lambda: start_if_absent(WATCHER, procs), "오류")
    res["start"]["bridge"] = guard("bridge 기동", lambda: start_if_absent(BRIDGE, procs, 8765), "오류")
    say(f"  rgon_auto_watcher.py: {res['start']['watcher']}")
    say(f"  rgon_bridge_8765.py: {res['start']['bridge']}")
    res["tasks"] = guard("예약작업", enable_tasks, {})
    for k, v in res["tasks"].items():
        say(f"  예약작업 {k}: {v}")
    return res


# ───────────────────── 3. 아카이브 ─────────────────────
def step_archive():
    section("[3] omni_*.py / ahn_queue_*.txt 아카이브 정리")
    dest = ROOT / "backups" / "daily_omni_archive"
    dest.mkdir(parents=True, exist_ok=True)
    moved = 0
    for pattern in ("omni_*.py", "ahn_queue_*.txt"):
        files = [f for f in ROOT.glob(pattern)
                 if f.is_file() and f.resolve() != SELF and f.name.lower() not in KEEP_NAMES]
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        if files:
            say(f"  [{pattern}] 최신 1개 유지: {files[0].name}")
        for f in files[1:]:
            t = dest / f.name
            if t.exists():
                t = dest / f"{f.stem}_{STAMP}{f.suffix}"
            try:
                shutil.move(str(f), str(t))
                moved += 1
            except OSError as e:
                say(f"   이동 실패 {f.name}: {e}")
    say(f"  이동된 파일 수: {moved} → {dest}")
    return moved


# ───────────────────── 4. 기억 저장소 스캔 ─────────────────────
def step_memory():
    section("[4] 기억 저장소 / 인수인계 / 상태 파일 목록 (하위 2단계)")
    rows = []
    skip = {".git", "node_modules", "__pycache__", "daily_omni_archive", "disabled_startup"}
    base_depth = len(ROOT.parts)
    for dp, dns, fns in os.walk(ROOT):
        depth = len(Path(dp).parts) - base_depth
        dns[:] = [d for d in dns if d not in skip] if depth < 2 else []
        for fn in fns:
            p = Path(dp) / fn
            if p.suffix.lower() in (".json", ".md", ".txt") and any(k in fn.lower() for k in KEYWORDS):
                try:
                    st = p.stat()
                    rows.append((str(p.relative_to(ROOT)), st.st_size, st.st_mtime))
                except OSError:
                    pass
    rows.sort(key=lambda r: r[2], reverse=True)
    w = min(max([len(r[0]) for r in rows] + [12]), 60)
    table = [f"{'파일(상대경로)':<{w}}  {'크기':>9}  최근 수정", "-" * (w + 34)]
    for n, s, m in rows:
        table.append(f"{n[:w]:<{w}}  {human(s):>9}  {datetime.fromtimestamp(m):%Y-%m-%d %H:%M:%S}")
    if not rows:
        table.append("(해당 파일 없음)")
    for ln in table:
        say("  " + ln)
    summary = (f"RGON daily wrap-up summary ({datetime.now():%Y-%m-%d %H:%M:%S})\n"
               f"Root: {ROOT}\nMatched files: {len(rows)}\n\n" + "\n".join(table) + "\n")
    out = ROOT / "daily_wrapup_summary.txt"
    try:
        out.write_text(summary, encoding="utf-8")
        say(f"\n  저장: {out}")
    except OSError as e:
        say(f"  요약 저장 실패: {e}")
    return rows


# ───────────────────── 5. 하트비트 + 텔레그램 보고 ─────────────────────
def step_heartbeat():
    section("[5-A] rgon_agency_heartbeat.py 1회 실행")
    if not HEARTBEAT.exists():
        say("  파일 없음 → 건너뜀")
        return "파일 없음"
    rc, o, e = run_hidden([sys.executable, str(HEARTBEAT)], timeout=180)
    for t in (o or e).strip().splitlines()[-6:]:
        say("  | " + t[:150])
    say(f"  종료코드: {rc}")
    return f"종료코드 {rc}"


def send_telegram(text):
    if not TELEGRAM.exists():
        return "rgon_telegram_bridge.py 없음 → 전송 생략"
    rc, o, e = run_hidden([sys.executable, str(TELEGRAM), "--send-text", text[:3500]], timeout=90)
    return "전송 완료" if rc == 0 else f"전송 실패(code {rc}): {(e or o).strip()[:120]}"


def main():
    say(f"RGON 마무리 작업 시작 {datetime.now():%Y-%m-%d %H:%M:%S} | PID {os.getpid()}")
    if not ROOT.is_dir():
        sys.exit(f"작업 폴더가 없습니다: {ROOT}")

    dash = guard("대시보드", step_dashboard, {}) or {}
    fix = guard("패치/기동", step_patch_and_start, {}) or {}
    moved = guard("아카이브", step_archive, 0)
    rows = guard("기억 저장소", step_memory, []) or []
    hb = guard("heartbeat", step_heartbeat, "오류")

    section("[🌙 RGON 일일 마감 및 대시보드 오픈 완료 보고서]")
    patch = fix.get("patch", {})
    start = fix.get("start", {})
    tasks = fix.get("tasks", {})
    top = "\n".join(f"   · {r[0]} ({human(r[1])}, {datetime.fromtimestamp(r[2]):%m-%d %H:%M})" for r in rows[:8]) or "   · (없음)"
    report = "\n".join([
        "[🌙 RGON 일일 마감 및 대시보드 오픈 완료 보고서]",
        f"⏰ {datetime.now():%Y-%m-%d %H:%M:%S}",
        "",
        f"1) 대시보드: {'오픈됨' if dash.get('opened') else '오픈 실패'} | 바탕화면 바로가기 {dash.get('shortcuts', 0)}/2개",
        f"   Git origin: {dash.get('remote', '-')}",
        "2) 무창 패치: " + ", ".join(f"{k}={str(v).split(' (')[0].split(' |')[0]}" for k, v in patch.items()),
        f"   8765 브리지: {str(fix.get('bridge', '-')).split(' (')[0]}",
        f"   watcher: {start.get('watcher', '-')} / bridge: {start.get('bridge', '-')}",
        "   예약작업: " + ("; ".join(f"{k}={v}" for k, v in tasks.items()) or "-"),
        f"3) 아카이브 이동: {moved}개 → backups/daily_omni_archive",
        f"4) 기억 저장소 {len(rows)}개 (최근순 상위):",
        top,
        f"5) 6대 청사 박동(heartbeat): {hb}",
    ])
    print(report, flush=True)
    result = send_telegram(report)
    print(f"\nTelegram: {result}", flush=True)


if __name__ == "__main__":
    main()
Copy
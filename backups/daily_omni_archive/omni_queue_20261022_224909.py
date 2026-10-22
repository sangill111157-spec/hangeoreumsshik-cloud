#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_fix_flashing_and_doctor.py  (Windows / Python 3 stdlib only)

기능: 콘솔 깜빡임 원인 진단·종료 / 무창(CREATE_NO_WINDOW) 패치 / 대시보드 바로가기 /
      8765 브리지 재작성 / 임시파일 아카이브 / 기억 저장소 스캔 / 마감 보고
- 수정하는 모든 파일은 *.bak_YYYYmmdd_HHMMSS 로 백업됩니다.
- 비활성화한 예약 작업·시작프로그램은 목록으로 출력되며 되돌릴 수 있습니다.
- 8765 브리지는 127.0.0.1 에만 바인딩하며, 받은 코드를 '저장'만 하고 실행하지 않습니다.
"""
import ast
import base64
import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
import webbrowser
import configparser
from datetime import datetime
from pathlib import Path

if os.name != "nt":
    sys.exit("이 스크립트는 Windows 전용입니다.")

CNW = 0x08000000            # CREATE_NO_WINDOW
DETACHED = 0x00000008       # DETACHED_PROCESS
NEWGRP = 0x00000200         # CREATE_NEW_PROCESS_GROUP

ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
DESKTOP = Path(r"C:\Users\sangi\Desktop")
DASH = ROOT / "rgon_alpha_audience.html"
SELF = Path(__file__).resolve()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

WATCHER = ROOT / "rgon_auto_watcher.py"
BRIDGE = ROOT / "rgon_bridge_8765.py"
HEARTBEAT = ROOT / "rgon_agency_heartbeat.py"
TELEGRAM = ROOT / "rgon_telegram_bridge.py"
PATCH_TARGETS = [WATCHER, HEARTBEAT, TELEGRAM]

SUSPECT_RE = re.compile(
    r"(rgon_|omni_|ahn_|upgrade_omni|build_omni)[\w\-]*\.(py|pyw|vbs|bat|cmd|ps1)",
    re.IGNORECASE,
)
WATCHED_NAMES = ("python.exe", "pythonw.exe", "wscript.exe", "cmd.exe", "powershell.exe")
KEYWORDS = ("memory", "handover", "state", "status", "constitution", "briefing", "log", "history")

REPORT = []  # 마감 보고서 줄 모음


def say(msg=""):
    print(msg, flush=True)
    REPORT.append(str(msg))


def hidden_si():
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0  # SW_HIDE
    return si


def run_hidden(cmd, timeout=60, input_bytes=None):
    """항상 창 없이 실행하고 (returncode, stdout, stderr) 반환."""
    try:
        p = subprocess.run(
            cmd, capture_output=True, timeout=timeout, input=input_bytes,
            creationflags=CNW, startupinfo=hidden_si(), cwd=str(ROOT) if ROOT.exists() else None,
        )
        enc = "utf-8"
        out = p.stdout.decode(enc, "replace") if p.stdout else ""
        err = p.stderr.decode(enc, "replace") if p.stderr else ""
        return p.returncode, out, err
    except Exception as e:  # noqa
        return -1, "", f"{type(e).__name__}: {e}"


def ps(script, timeout=60):
    prefix = "[Console]::OutputEncoding=[Text.Encoding]::UTF8; "
    enc = base64.b64encode((prefix + script).encode("utf-16le")).decode()
    return run_hidden(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden",
         "-ExecutionPolicy", "Bypass", "-EncodedCommand", enc],
        timeout=timeout,
    )


def backup(path):
    b = path.with_name(path.name + f".bak_{STAMP}")
    shutil.copy2(path, b)
    return b


def human(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return f"{n:.0f}{u}" if u == "B" else f"{n:.1f}{u}"
        n /= 1024


def section(title):
    say("")
    say("=" * 78)
    say(title)
    say("=" * 78)


# ───────────────────────── 1. 프로세스 진단 / 종료 ─────────────────────────
def list_processes():
    code, out, err = ps(
        "$r=@(Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,CommandLine);"
        "ConvertTo-Json -InputObject $r -Compress -Depth 3"
    )
    if code != 0 or not out.strip():
        say(f"  [경고] 프로세스 조회 실패: {err.strip()[:200]}")
        return []
    try:
        data = json.loads(out)
    except ValueError:
        return []
    if isinstance(data, dict):
        data = [data]
    return [d for d in data if isinstance(d, dict)]


def ancestors_of(pid, procs):
    parent = {p["ProcessId"]: p.get("ParentProcessId") for p in procs}
    chain, cur = set(), pid
    while cur and cur not in chain:
        chain.add(cur)
        cur = parent.get(cur)
    return chain


def is_target(p):
    name = (p.get("Name") or "").lower()
    cmd = (p.get("CommandLine") or "")
    low = cmd.lower()
    if name in ("python.exe", "pythonw.exe", "wscript.exe", "cscript.exe", "cmd.exe", "powershell.exe", "pwsh.exe"):
        if SUSPECT_RE.search(cmd):
            return True
        if name in ("pythonw.exe", "wscript.exe", "cscript.exe") and str(ROOT).lower() in low:
            return True
    return False


def step_processes():
    section("[1-A] 실행 중인 python / wscript / cmd / powershell 프로세스")
    procs = list_processes()
    me = ancestors_of(os.getpid(), procs)
    watched = [p for p in procs if (p.get("Name") or "").lower() in WATCHED_NAMES]
    say(f"  {'PID':>7} {'PPID':>7}  {'Name':<15} CommandLine")
    for p in sorted(watched, key=lambda x: x["ProcessId"]):
        mark = " (본 스크립트/상위)" if p["ProcessId"] in me else ""
        cl = (p.get("CommandLine") or "").replace("\r", " ").replace("\n", " ")
        say(f"  {p['ProcessId']:>7} {p.get('ParentProcessId') or 0:>7}  {p['Name']:<15} {cl[:170]}{mark}")
    targets = [p for p in watched if p["ProcessId"] not in me and is_target(p)]
    say(f"\n  종료 대상(백그라운드 rgon/omni/ahn 계열): {len(targets)}개")
    killed = []
    for p in targets:
        code, out, err = run_hidden(["taskkill.exe", "/PID", str(p["ProcessId"]), "/F", "/T"], timeout=20)
        ok = code == 0
        say(f"   - PID {p['ProcessId']} {p['Name']}: {'종료됨' if ok else '실패 ' + (err or out).strip()[:80]}")
        if ok:
            killed.append(p["ProcessId"])
    time.sleep(1.0)
    return len(killed), len(targets)


def step_autostart():
    section("[1-B] 예약 작업(schtasks) / 시작프로그램 / Run 레지스트리 점검")
    disabled_tasks, moved_startup = [], []
    code, out, err = run_hidden(["schtasks.exe", "/Query", "/FO", "CSV", "/V", "/NH"], timeout=90)
    try:
        raw = subprocess.run(["schtasks.exe", "/Query", "/FO", "CSV", "/V", "/NH"], capture_output=True,
                             timeout=90, creationflags=CNW, startupinfo=hidden_si()).stdout
        text = raw.decode("mbcs", "replace")
    except Exception:
        text = out
    seen = set()
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 9:
            continue
        task, run_cmd = row[1], row[8]
        if task in seen:
            continue
        seen.add(task)
        if SUSPECT_RE.search(run_cmd) or str(ROOT).lower() in run_cmd.lower():
            say(f"  [의심 작업] {task}\n      실행: {run_cmd[:160]}")
            c, o, e = run_hidden(["schtasks.exe", "/Change", "/TN", task, "/DISABLE"], timeout=20)
            if c == 0:
                disabled_tasks.append(task)
                say("      → 비활성화함 (복구: schtasks /Change /TN \"<이름>\" /ENABLE)")
            else:
                say(f"      → 비활성화 실패(관리자 권한 필요할 수 있음): {(e or o).strip()[:100]}")
    if not disabled_tasks:
        say("  예약 작업: 의심 항목 없음")

    startup = Path(os.environ.get("APPDATA", "")) / r"Microsoft\Windows\Start Menu\Programs\Startup"
    if startup.is_dir():
        dest = ROOT / "backups" / "disabled_startup"
        for f in startup.iterdir():
            if not f.is_file() or f.name.lower() == "desktop.ini":
                continue
            hit = bool(SUSPECT_RE.search(f.name))
            if not hit and f.suffix.lower() in (".vbs", ".bat", ".cmd", ".ps1"):
                try:
                    t = f.read_text(encoding="utf-8", errors="ignore")
                    hit = bool(SUSPECT_RE.search(t)) or str(ROOT).lower() in t.lower()
                except OSError:
                    pass
            say(f"  [Startup] {f.name}{'  ← 의심' if hit else ''}")
            if hit:
                dest.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.move(str(f), str(dest / f"{f.stem}_{STAMP}{f.suffix}"))
                    moved_startup.append(f.name)
                    say(f"      → {dest} 로 이동")
                except OSError as e:
                    say(f"      → 이동 실패: {e}")
    try:
        import winreg
        for hive, hn in ((winreg.HKEY_CURRENT_USER, "HKCU"), (winreg.HKEY_LOCAL_MACHINE, "HKLM")):
            try:
                with winreg.OpenKey(hive, r"Software\Microsoft\Windows\CurrentVersion\Run") as k:
                    i = 0
                    while True:
                        try:
                            n, v, _ = winreg.EnumValue(k, i)
                        except OSError:
                            break
                        i += 1
                        if SUSPECT_RE.search(str(v)) or str(ROOT).lower() in str(v).lower():
                            say(f"  [Run:{hn}] {n} = {str(v)[:140]}  ← 의심(자동 수정 안 함, 직접 확인)")
            except OSError:
                pass
    except ImportError:
        pass
    return disabled_tasks, moved_startup


# ───────────────────────── 무창 shim 패치 ─────────────────────────
MARK = "RGON_NOWINDOW_SHIM"
SHIM = '''# ---- RGON_NOWINDOW_SHIM_BEGIN (모든 subprocess 호출을 콘솔 창 없이 실행) ----
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
        return f"문법 오류로 패치 중단: {e}"
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
    warn = [n + 1 for n, ln in enumerate(new_src.splitlines())
            if re.search(r"os\.system\(|os\.popen\(|ShellExecute", ln)]
    extra = f" | 경고: os.system/ShellExecute 사용 라인 {warn[:8]} (shim 미적용, 수동 확인)" if warn else ""
    return f"패치 완료 (백업 {b.name}){extra}"


def step_patch_scripts():
    section("[1-C] 깜빡임 방지 패치 (CREATE_NO_WINDOW + STARTUPINFO SW_HIDE)")
    res = {}
    for f in PATCH_TARGETS:
        res[f.name] = patch_no_window(f)
        say(f"  {f.name}: {res[f.name]}")
    return res


# ───────────────────────── 3. 8765 브리지 ─────────────────────────
BRIDGE_SRC = r'''# -*- coding: utf-8 -*-
# rgon_bridge_8765.py  (rgon_fix_flashing_and_doctor.py 가 생성)
# - 127.0.0.1:8765 에서만 수신, POST /api/queue 만 처리
# - "entry" 키가 있는 JSON / 그 외 요청은 {"ok": true, "status": "ignored"}
# - ast.parse() 를 통과한 순수 Python 코드만 omni_queue_YYYYMMDD_HHMMSS.py 로 저장 (실행하지 않음)
# - clip.exe / rgon_telegram_bridge.py 호출은 모두 CREATE_NO_WINDOW
import ast
import json
import subprocess
import sys
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

CNW = 0x08000000
ROOT = Path(__file__).resolve().parent
HOST, PORT = "127.0.0.1", 8765
MAX_BYTES = 1_000_000
LOCK = threading.Lock()


def run_hidden(cmd, input_bytes=None, timeout=30):
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0
    try:
        return subprocess.run(cmd, input=input_bytes, capture_output=True, timeout=timeout,
                              creationflags=CNW, startupinfo=si, cwd=str(ROOT))
    except Exception:
        return None


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


def notify(path):
    run_hidden(["clip.exe"], input_bytes=str(path).encode("mbcs", "replace"), timeout=10)
    tg = ROOT / "rgon_telegram_bridge.py"
    if tg.exists():
        run_hidden([sys.executable, str(tg), "--send-text", f"[RGON] 코드 큐 저장: {path.name}"], timeout=60)


class H(BaseHTTPRequestHandler):
    server_version = "RgonBridge/2"

    def log_message(self, *a):
        pass

    def _send(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

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
        if self.path.split("?")[0] != "/api/queue":
            return self._send({"ok": True, "status": "ignored"})
        code, why = extract_code(raw)
        if code is None:
            return self._send({"ok": True, "status": "ignored", "reason": why})
        p = save_code(code)
        threading.Thread(target=notify, args=(p,), daemon=True).start()
        self._send({"ok": True, "status": "saved", "file": p.name})


if __name__ == "__main__":
    srv = ThreadingHTTPServer((HOST, PORT), H)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
'''


def step_bridge():
    section("[3] rgon_bridge_8765.py 재작성 (무창 + entry 무시 + ast.parse 검증)")
    try:
        ast.parse(BRIDGE_SRC)
    except SyntaxError as e:
        say(f"  브리지 템플릿 검증 실패: {e}")
        return "실패"
    if BRIDGE.exists():
        b = backup(BRIDGE)
        say(f"  기존 파일 백업: {b.name}")
    BRIDGE.write_text(BRIDGE_SRC, encoding="utf-8")
    say(f"  작성 및 ast.parse 검증 완료: {BRIDGE}")
    return "완료"


def start_single(script):
    """이미 실행 중이 아니면 창 없이 1개만 기동."""
    if not script.exists():
        say(f"  {script.name}: 파일 없음 → 기동 생략")
        return False
    procs = list_processes()
    for p in procs:
        if p["ProcessId"] != os.getpid() and script.name.lower() in (p.get("CommandLine") or "").lower() \
                and (p.get("Name") or "").lower() in ("python.exe", "pythonw.exe"):
            say(f"  {script.name}: 이미 실행 중 (PID {p['ProcessId']}) → 중복 기동 생략")
            return True
    exe = Path(sys.executable)
    pyw = exe.with_name("pythonw.exe")
    interp = str(pyw if pyw.exists() else exe)
    logdir = ROOT / "rgon_logs"
    logdir.mkdir(exist_ok=True)
    log = open(logdir / f"{script.stem}.log", "ab")
    try:
        subprocess.Popen(
            [interp, str(script)], cwd=str(ROOT), stdin=subprocess.DEVNULL, stdout=log, stderr=log,
            creationflags=CNW | DETACHED | NEWGRP, startupinfo=hidden_si(), close_fds=True,
        )
        say(f"  {script.name}: 무창 단일 인스턴스로 기동 ({Path(interp).name})")
        return True
    except Exception as e:
        say(f"  {script.name}: 기동 실패 {e}")
        return False


def step_restart():
    section("[1-D / 3] 단일 인스턴스 재기동")
    w = start_single(WATCHER)
    time.sleep(0.5)
    b = start_single(BRIDGE)
    return w, b


# ───────────────────────── 2. 대시보드 ─────────────────────────
def find_chrome():
    cands = [
        os.environ.get("PROGRAMFILES", r"C:\Program Files") + r"\Google\Chrome\Application\chrome.exe",
        os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)") + r"\Google\Chrome\Application\chrome.exe",
        os.environ.get("LOCALAPPDATA", "") + r"\Google\Chrome\Application\chrome.exe",
    ]
    for c in cands:
        if c and Path(c).exists():
            return Path(c)
    return None


def git_remote():
    cfg = ROOT / ".git" / "config"
    if not cfg.exists():
        return "(.git/config 없음)"
    cp = configparser.ConfigParser(strict=False, interpolation=None)
    try:
        cp.read_string(cfg.read_text(encoding="utf-8", errors="replace"))
        return cp.get('remote "origin"', "url")
    except Exception:
        m = re.search(r'\[remote "origin"\][^\[]*?url\s*=\s*(\S+)', cfg.read_text(errors="replace"), re.S)
        return m.group(1) if m else "(remote origin URL 없음)"


def step_dashboard():
    section("[2] 대시보드 바로가기 생성 및 오픈")
    if not DASH.exists():
        say(f"  [경고] 대시보드 파일이 없습니다: {DASH}")
    uri = DASH.as_uri()
    chrome = find_chrome()
    DESKTOP.mkdir(parents=True, exist_ok=True)
    result = {"bat": None, "lnk": None, "opened": False}

    bat = DESKTOP / "👑_RGON_대시보드_열기.bat"
    bat_plain = DESKTOP / "open_rgon_dashboard.bat"
    if chrome:
        body = f'@echo off\r\nstart "" "{chrome}" --app="{uri}" --window-size=1440,920\r\nexit\r\n'
    else:
        body = f'@echo off\r\nstart "" "{DASH}"\r\nexit\r\n'
    for b in (bat, bat_plain):
        try:
            b.write_text(body, encoding="mbcs", errors="replace", newline="")
            result["bat"] = str(b)
            say(f"  생성: {b}")
        except OSError as e:
            say(f"  .bat 생성 실패 {b.name}: {e}")

    url_file = DESKTOP / "RGON_Dashboard.url"
    try:
        url_file.write_text(f"[InternetShortcut]\r\nURL={uri}\r\n", encoding="utf-8")
        say(f"  생성: {url_file}")
    except OSError as e:
        say(f"  .url 생성 실패: {e}")

    lnk = DESKTOP / "👑 RGON 대시보드 앱.lnk"
    target = str(chrome) if chrome else str(bat_plain)
    args = f'--app="{uri}" --window-size=1440,920' if chrome else ""
    icon = (str(chrome) + ",0") if chrome else ""
    q = lambda s: str(s).replace("'", "''")
    script = (
        "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%s');"
        "$s.TargetPath='%s';$s.Arguments='%s';$s.WorkingDirectory='%s';"
        "%s$s.Save()"
    ) % (q(lnk), q(target), q(args), q(ROOT), ("$s.IconLocation='%s';" % q(icon)) if icon else "")
    c, o, e = ps(script, timeout=30)
    if c == 0 and lnk.exists():
        result["lnk"] = str(lnk)
        say(f"  생성: {lnk}")
    else:
        say(f"  .lnk 생성 실패: {(e or o).strip()[:150]}")

    try:
        if chrome:
            subprocess.Popen([str(chrome), f"--app={uri}", "--window-size=1440,920"],
                             creationflags=CNW | DETACHED, close_fds=True)
            result["opened"] = True
        else:
            result["opened"] = webbrowser.open(uri)
        say(f"  대시보드 1회 오픈: {'Chrome App 모드' if chrome else '기본 브라우저'} → {uri}")
    except Exception as e:
        say(f"  오픈 실패: {e}")
        try:
            result["opened"] = webbrowser.open(uri)
        except Exception:
            pass
    remote = git_remote()
    say(f"  Git remote origin URL: {remote}")
    result["remote"] = remote
    return result


# ───────────────────────── 4. 아카이브 ─────────────────────────
def step_archive():
    section("[4] omni_*.py / ahn_queue_*.txt 아카이브 정리")
    dest = ROOT / "backups" / "daily_omni_archive"
    dest.mkdir(parents=True, exist_ok=True)
    moved = 0
    for pattern in ("omni_*.py", "ahn_queue_*.txt"):
        files = [f for f in ROOT.glob(pattern) if f.is_file() and f.resolve() != SELF]
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        keep, old = files[:1], files[1:]
        if keep:
            say(f"  [{pattern}] 최신 1개 유지: {keep[0].name}")
        for f in old:
            t = dest / f.name
            if t.exists():
                t = dest / f"{f.stem}_{STAMP}{f.suffix}"
            try:
                shutil.move(str(f), str(t))
                moved += 1
            except OSError as e:
                say(f"   이동 실패 {f.name}: {e}")
    say(f"  이동된 파일 수: {moved}  → {dest}")
    return moved


# ───────────────────────── ahn_inbox 진단 ─────────────────────────
def diagnose_inbox():
    """ahn_inbox_latest.txt 가 Python 코드 / JSON / 일반 텍스트인지 판별."""
    f = ROOT / "ahn_inbox_latest.txt"
    if not f.exists():
        return "ahn_inbox_latest.txt 없음"
    text = f.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return "비어 있음"
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return f"JSON(dict, 키: {list(obj)[:6]})"
        return f"JSON({type(obj).__name__})"
    except ValueError:
        pass
    try:
        t = ast.parse(text)
        if t.body:
            return f"유효한 Python 코드 (문장 {len(t.body)}개)"
    except (SyntaxError, ValueError):
        pass
    return "일반 텍스트 (Python/JSON 아님)"


# ───────────────────────── 5. 기억 저장소 스캔 ─────────────────────────
def step_memory():
    section("[5-A] 기억 저장소 / 장부 / 인수인계 파일 목록 (하위 2단계)")
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
    w = min(max([len(r[0]) for r in rows] + [10]), 60)
    lines = [f"{'파일(상대경로)':<{w}}  {'크기':>9}  최근 수정", "-" * (w + 34)]
    for n, s, m in rows:
        lines.append(f"{n[:w]:<{w}}  {human(s):>9}  {datetime.fromtimestamp(m):%Y-%m-%d %H:%M:%S}")
    if not rows:
        lines.append("(해당 파일 없음)")
    for ln in lines:
        say("  " + ln)
    summary = (f"RGON daily wrap-up summary ({datetime.now():%Y-%m-%d %H:%M:%S})\n"
               f"Root: {ROOT}\nMatched files: {len(rows)}\n\n" + "\n".join(lines) + "\n")
    try:
        (ROOT / "daily_wrapup_summary.txt").write_text(summary, encoding="utf-8")
        say(f"\n  저장: {ROOT / 'daily_wrapup_summary.txt'}")
    except OSError as e:
        say(f"  요약 저장 실패: {e}")
    return rows


def step_heartbeat():
    section("[5-B] rgon_agency_heartbeat.py 1회 실행 (무창)")
    if not HEARTBEAT.exists():
        say("  파일 없음 → 건너뜀")
        return "파일 없음"
    c, o, e = run_hidden([sys.executable, str(HEARTBEAT)], timeout=180)
    tail = (o or e).strip().splitlines()[-6:]
    for t in tail:
        say("  | " + t[:150])
    return f"종료코드 {c}"


def send_telegram(text):
    if not TELEGRAM.exists():
        return "rgon_telegram_bridge.py 없음 → 전송 생략"
    c, o, e = run_hidden([sys.executable, str(TELEGRAM), "--send-text", text[:3500]], timeout=90)
    return "전송 완료" if c == 0 else f"전송 실패(code {c}): {(e or o).strip()[:120]}"


# ───────────────────────── main ─────────────────────────
def guard(name, fn, default=None):
    try:
        return fn()
    except Exception:
        say(f"  [오류] {name}\n" + traceback.format_exc(limit=3))
        return default


def main():
    say(f"RGON 정비 시작 {datetime.now():%Y-%m-%d %H:%M:%S} | PID {os.getpid()} | {ROOT}")
    if not ROOT.is_dir():
        sys.exit(f"작업 폴더가 없습니다: {ROOT}")

    killed, found = guard("프로세스", step_processes, (0, 0))
    disabled_tasks, moved_startup = guard("자동실행", step_autostart, ([], []))
    patch_res = guard("패치", step_patch_scripts, {})
    guard("브리지", step_bridge)
    moved = guard("아카이브", step_archive, 0)
    dash = guard("대시보드", step_dashboard, {})
    wb = guard("재기동", step_restart, (False, False))
    rows = guard("기억 저장소", step_memory, [])
    hb = guard("heartbeat", step_heartbeat, "오류")
    inbox = guard("inbox 진단", diagnose_inbox, "오류")

    section("[마감 보고서] EOD")
    final = [
        f"시각: {datetime.now():%Y-%m-%d %H:%M:%S}",
        f"1) 깜빡임 원인 제거: 대상 {found}개 중 {killed}개 종료 / 예약작업 비활성화 {len(disabled_tasks)}건 / "
        f"시작프로그램 이동 {len(moved_startup)}건",
        "   무창 패치: " + ", ".join(f"{k}={v.split(' (')[0]}" for k, v in (patch_res or {}).items()),
        f"   재기동: watcher={'OK' if wb[0] else 'NO'}, bridge8765={'OK' if wb[1] else 'NO'} (단일 인스턴스)",
        f"2) 대시보드: {'오픈됨' if dash.get('opened') else '오픈 실패'} | 바로가기 .bat={'OK' if dash.get('bat') else 'NO'}, "
        f".lnk={'OK' if dash.get('lnk') else 'NO'} | origin={dash.get('remote')}",
        f"3) 아카이브 이동: {moved}개 | ahn_inbox_latest: {inbox}",
        f"4) heartbeat: {hb}",
        f"5) 기억 저장소 파일 {len(rows)}개 (상위 5): " + "; ".join(r[0] for r in rows[:5]),
    ]
    text = "\n".join(final)
    print(text, flush=True)
    tg = send_telegram("[RGON 마감 보고]\n" + text)
    print(f"\nTelegram: {tg}", flush=True)
    print("\n※ 몇 분간 깜빡임이 사라졌는지 확인하세요. 계속되면 위 [1-A] 표에서 남은 PID의 CommandLine을 확인하세요.")


if __name__ == "__main__":
    main()
Copy
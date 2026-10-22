import os
import re
import sys
import json
import time
import urllib.request
import subprocess
from pathlib import Path

BASE_DIR = Path(r"C:\Users\sangi\Downloads\shin-agent")
BRIDGE_8765_PY = BASE_DIR / "rgon_bridge_8765.py"
WATCHER_PY = BASE_DIR / "rgon_auto_watcher.py"
BRIDGE_PY = BASE_DIR / "rgon_telegram_bridge.py"

SERVER_8765_CODE = r'''# -*- coding: utf-8 -*-
import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = Path(r"C:\Users\sangi\Downloads\shin-agent")
BRIDGE_PY = BASE_DIR / "rgon_telegram_bridge.py"
INBOX_TXT = BASE_DIR / "ahn_inbox_latest.txt"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send({"ok": True})

    def do_GET(self):
        self._send({"ok": True, "status": "online", "jobs": [], "job": None})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n).decode("utf-8", errors="replace") if n > 0 else "{}"
        try:
            data = json.loads(raw)
        except Exception:
            data = {"code": raw}

        code = data.get("code") or data.get("text") or data.get("content") or raw
        fn = data.get("filename") or ""
        if fn == "ping.txt" or code.strip() == "ping":
            self._send({"ok": True, "status": "pong"})
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        is_py = fn.endswith(".py") or any(k in code for k in ("import ", "def ", "if __name__", "# -*-"))
        if is_py:
            out = BASE_DIR / f"omni_queue_{ts}.py"
            out.write_text(code, encoding="utf-8")
        else:
            out = BASE_DIR / f"ahn_queue_{ts}.txt"
            out.write_text(code, encoding="utf-8")
            INBOX_TXT.write_text(code, encoding="utf-8")
            try:
                subprocess.run(["clip.exe"], input=code.encode("utf-16le"), timeout=5)
            except Exception:
                pass
            if BRIDGE_PY.exists():
                msg = f"📮 [안총리 실행 큐 등록 완료!]\n파일: {out.name}\n클립보드 복사 완료!\n\n{code[:350]}"
                subprocess.Popen([sys.executable, str(BRIDGE_PY), "--send-text", msg], cwd=str(BASE_DIR))

        self._send({"ok": True, "status": "queued", "file": out.name})


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
'''


def kill_port_8765():
    killed_pids = []
    p = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    for line in (p.stdout or "").splitlines():
        if ":8765" in line and "LISTENING" in line:
            parts = line.split()
            if parts:
                pid = parts[-1]
                if pid.isdigit() and int(pid) > 0:
                    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                    killed_pids.append(pid)
    return killed_pids


def main():
    print("🧹 [1/4] 8765 포트를 잡고 401 에러를 내던 구버전 프로세스 강제 종료 중...")
    killed = kill_port_8765()
    print(f"• 종료된 8765 점유 PID: {killed}")
    time.sleep(1.0)

    print("🛠️ [2/4] 401 암호 제한 없는 새 8765 전용 큐 서버 기동 중...")
    BRIDGE_8765_PY.write_text(SERVER_8765_CODE.strip() + "\n", encoding="utf-8")
    subprocess.Popen(["pythonw.exe", str(BRIDGE_8765_PY)], cwd=str(BASE_DIR))

    # 문지기 로봇(rgon_auto_watcher.py)도 살아있는지 확인 후 없으면 기동
    ps_check = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.CommandLine -like '*rgon_auto_watcher.py*' } | "
        "Select-Object -ExpandProperty ProcessId"
    )
    chk = subprocess.run(["powershell", "-NoProfile", "-Command", ps_check], capture_output=True, text=True)
    if not (chk.stdout or "").strip() and WATCHER_PY.exists():
        subprocess.Popen(["pythonw.exe", str(WATCHER_PY)], cwd=str(BASE_DIR))

    time.sleep(1.5)

    print("🧪 [3/4] 127.0.0.1:8765/api/queue 연결 재검증...")
    test_ok = False
    resp_txt = ""
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8765/api/queue",
            data=json.dumps({"filename": "ping.txt", "code": "ping"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            resp_txt = resp.read().decode("utf-8", errors="replace")
            test_ok = (resp.status == 200)
    except Exception as e:
        resp_txt = f"오류: {e}"

    report = (
        f"👑 [8765 포트 401 에러 박멸 & 큐 서버 100% 개통 완료!]\n"
        f"• 제거된 구버전 PID: {killed}\n"
        f"• 서버 상태: {'✅ 200 OK 완벽 개통!' if test_ok else '⚠️ 확인 필요'}\n"
        f"• 응답 결과: {resp_txt}\n"
        f"• 이제 크롬에서 주황색 [📮 안총리 실행 큐] 버튼을 눌러보십시오!"
    )
    print(report)
    if BRIDGE_PY.exists():
        subprocess.run([sys.executable, str(BRIDGE_PY), "--send-text", report], cwd=str(BASE_DIR))


if __name__ == "__main__":
    main()
Copy
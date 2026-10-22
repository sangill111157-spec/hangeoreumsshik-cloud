import os
import sys
import json
import time
import urllib.request
import subprocess
from pathlib import Path

BASE_DIR = Path(r"C:\Users\sangi\Downloads\shin-agent")
BRIDGE_8765_PY = BASE_DIR / "rgon_bridge_8765.py"
BRIDGE_PY = BASE_DIR / "rgon_telegram_bridge.py"
STARTUP_DIR = Path(os.environ.get("APPDATA", "")) / r"Microsoft\Windows\Start Menu\Programs\Startup"
STARTUP_VBS = STARTUP_DIR / "RGON_Bridge_8765.vbs"

SERVER_CODE = r'''# -*- coding: utf-8 -*-
import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = Path(r"C:\Users\sangi\Downloads\shin-agent")
BRIDGE_PY = BASE_DIR / "rgon_telegram_bridge.py"
INBOX_TXT = BASE_DIR / "ahn_inbox_latest.txt"
QUEUE_JSON = BASE_DIR / "ahn_inbox_queue.json"
HOST = "127.0.0.1"
PORT = 8765


class BridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send_json(self, obj, status=200):
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
        self._send_json({"ok": True})

    def do_GET(self):
        # /poll, /api/dispatch/next, /health 등 모든 GET 요청에 정상 응답
        self._send_json({"ok": True, "status": "online", "jobs": [], "job": None})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8", errors="replace") if length > 0 else "{}"
        try:
            data = json.loads(raw)
        except Exception:
            data = {"code": raw}

        code = (
            data.get("code")
            or data.get("text")
            or data.get("content")
            or data.get("prompt")
            or raw
        )
        role = data.get("role") or "rgon"
        filename = data.get("filename") or ""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        # ping 테스트면 파일 생성 없이 즉시 ok 반환
        if filename == "ping.txt" or code.strip() == "ping":
            self._send_json({"ok": True, "status": "pong"})
            return

        is_py = filename.endswith(".py") or any(k in code for k in ("import ", "def ", "if __name__", "# -*-"))

        if is_py:
            out_name = f"omni_queue_{ts}.py"
            out_path = BASE_DIR / out_name
            out_path.write_text(code, encoding="utf-8")
        else:
            out_name = f"ahn_queue_{ts}.txt"
            out_path = BASE_DIR / out_name
            out_path.write_text(code, encoding="utf-8")
            INBOX_TXT.write_text(code, encoding="utf-8")
            try:
                subprocess.run(["clip.exe"], input=code.encode("utf-16le"), timeout=5)
            except Exception:
                pass
            if BRIDGE_PY.exists():
                msg = (
                    f"📮 [안총리 실행 큐 접수 완료!]\n"
                    f"📄 파일: {out_name}\n"
                    f"📋 PC 클립보드 & ahn_inbox_latest.txt 자동 적재 완료!\n\n"
                    f"[내용 요약]\n{code[:400]}"
                )
                subprocess.Popen([sys.executable, str(BRIDGE_PY), "--send-text", msg], cwd=str(BASE_DIR))

        self._send_json({"ok": True, "status": "queued", "file": out_name, "role": role})


def main():
    srv = ThreadingHTTPServer((HOST, PORT), BridgeHandler)
    srv.serve_forever()


if __name__ == "__main__":
    main()
'''


def main():
    # 1. 기존 8765 포트 점유 프로세스 정리
    ps_kill = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.CommandLine -like '*rgon_bridge_8765.py*' } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill], capture_output=True)

    # 2. 전용 서버 파일 기록 및 시작프로그램 등록
    BRIDGE_8765_PY.write_text(SERVER_CODE.strip() + "\n", encoding="utf-8")
    vbs_local = BASE_DIR / "rgon_bridge_8765.vbs"
    vbs_txt = (
        'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.CurrentDirectory = "{BASE_DIR}"\n'
        f'WshShell.Run "pythonw.exe ""{BRIDGE_8765_PY}""", 0, False\n'
    )
    vbs_local.write_text(vbs_txt, encoding="utf-8")
    try:
        if STARTUP_DIR.exists():
            STARTUP_VBS.write_text(vbs_txt, encoding="utf-8")
    except Exception:
        pass

    # 3. 즉시 백그라운드 기동
    subprocess.Popen(["wscript.exe", str(vbs_local)], cwd=str(BASE_DIR))
    time.sleep(1.5)

    # 4. 실제 http://127.0.0.1:8765/api/queue 연결 검증!
    test_ok = False
    resp_txt = ""
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8765/api/queue",
            data=json.dumps({"role": "rgon", "filename": "ping.txt", "code": "ping"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            resp_txt = resp.read().decode("utf-8", errors="replace")
            test_ok = (resp.status == 200)
    except Exception as e:
        resp_txt = f"오류: {e}"

    report = (
        f"👑 [127.0.0.1:8765 전용 브릿지 서버 개통 완료!]\n"
        f"• 서버 상태: {'✅ 8765 포트 응답 성공!' if test_ok else '⚠️ 확인 필요'}\n"
        f"• 응답 결과: {resp_txt}\n"
        f"• 이제 크롬에서 주황색 [📮 안총리 실행 큐] 버튼을 누르시면 100% 즉시 등록됩니다!"
    )
    print(report)
    if BRIDGE_PY.exists():
        subprocess.run([sys.executable, str(BRIDGE_PY), "--send-text", report], cwd=str(BASE_DIR))


if __name__ == "__main__":
    main()
Copy
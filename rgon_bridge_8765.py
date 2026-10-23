# -*- coding: utf-8 -*-
# [RGON-WBC-GUARD-V18-START]
try:
    import rgon_white_blood_cell as _rgon_wbc
    _rgon_wbc.install_excepthook('rgon_bridge_8765.py')
except Exception:
    _rgon_wbc = None
# [RGON-WBC-GUARD-V18-END]
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

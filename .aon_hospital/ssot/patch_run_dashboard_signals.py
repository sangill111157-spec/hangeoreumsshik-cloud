# -*- coding: utf-8 -*-
import sys
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

filepath = "run_dashboard.py"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

# 1. do_GET에 /api/signal-sync-out 추가
get_hook = """        # ⚡ 르곤-안실장 OUT 시그널 조회 (GET /api/signal-sync-out)
        if path == '/api/signal-sync-out':
            state_file = ROOT_DIR / "sync_bridge_state.json"
            if state_file.exists():
                try:
                    with open(state_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {"status": "ok", "last_out_signal": {}}
            else:
                data = {"status": "ok", "last_out_signal": {}}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return
"""

if "/api/signal-sync-out" not in code:
    idx_get = code.find("def do_GET(self):")
    if idx_get != -1:
        # find the next line after query = ...
        idx_query = code.find("query = urllib.parse.parse_qs(parsed.query)", idx_get)
        if idx_query != -1:
            idx_next_line = code.find("\n", idx_query) + 1
            code = code[:idx_next_line] + "\n" + get_hook + "\n" + code[idx_next_line:]
            print("GET /api/signal-sync-out hook injected!")

# 2. do_POST에 /api/signal-sync-in 및 /api/signal-sync-out 추가
post_hook = """        # ⚡ 르곤이 IN 시그널 수신 & 작업 자동 주입 (POST /api/signal-sync-in)
        if self.path == '/api/signal-sync-in':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length)
            try:
                data = json.loads(raw_body.decode('utf-8'))
                raw_prompt = data.get("prompt", "")
                sender = data.get("sender", "Gemini-4-Argon")
                
                import rgon_auto_sync_daemon
                rgon_auto_sync_daemon.handle_in_signal(raw_prompt, sender=sender)
                
                resp = {
                    "status": "ok",
                    "message": "⚡ 르곤이 시그널이 성공적으로 캐치되어 안실장 작업 큐에 자동 주입되었습니다!",
                    "signal": "⟪⚡RGON_SIGNAL_READY⚡⟫"
                }
            except Exception as e:
                resp = {"status": "error", "message": str(e)}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
            return

        # ⚡ 안실장 OUT 시그널 기록 (POST /api/signal-sync-out)
        if self.path == '/api/signal-sync-out':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length)
            try:
                data = json.loads(raw_body.decode('utf-8'))
                summary = data.get("summary", "안실장 작업 완료")
                version = data.get("version", "v3.6-pro")
                
                import rgon_auto_sync_daemon
                rgon_auto_sync_daemon.handle_out_signal(summary, version=version)
                resp = {"status": "ok", "message": "안실장 OUT 시그널이 동기화되었습니다.", "signal": "⟪✅ANTIGRAVITY_OUT_COMPLETE✅⟫"}
            except Exception as e:
                resp = {"status": "error", "message": str(e)}
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
            return
"""

if "/api/signal-sync-in" not in code:
    idx_post = code.find("def do_POST(self):")
    if idx_post != -1:
        idx_next_line = code.find("\n", idx_post) + 1
        code = code[:idx_next_line] + "\n" + post_hook + "\n" + code[idx_next_line:]
        print("POST /api/signal-sync-in & out hook injected!")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(code)

print("run_dashboard.py updated!")

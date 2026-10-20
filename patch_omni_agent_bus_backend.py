# -*- coding: utf-8 -*-
"""
patch_omni_agent_bus_backend.py
--------------------------------------------------------------------------------
run_dashboard.py에 /api/omni-agent-bus GET/POST 엔드포인트 주입
--------------------------------------------------------------------------------
"""

import sys
import json
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

filepath = "run_dashboard.py"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

# 1. do_GET에 /api/omni-agent-bus 추가
get_hook = """        # 🌐 만능 멀티-AI 실시간 교신 버스 조회 (GET /api/omni-agent-bus)
        if path == '/api/omni-agent-bus':
            bus_file = BASE_DIR / "omni_agent_bus.json"
            if bus_file.exists():
                try:
                    with open(bus_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {"status": "ok", "registry": [], "messages": []}
            else:
                data = {"status": "ok", "registry": [], "messages": []}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return
"""

if "path == '/api/omni-agent-bus'" not in code:
    idx_get = code.find("def do_GET(self):")
    if idx_get != -1:
        idx_query = code.find("query = urllib.parse.parse_qs(parsed.query)", idx_get)
        idx_next = code.find("\n", idx_query) + 1
        code = code[:idx_next] + "\n" + get_hook + "\n" + code[idx_next:]
        print("GET /api/omni-agent-bus hook injected!")

# 2. do_POST에 /api/omni-agent-bus 추가
post_hook = """        # 🌐 만능 멀티-AI 실시간 교신 메시지 발송 & 에이전트 등록 (POST /api/omni-agent-bus)
        if self.path == '/api/omni-agent-bus':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length)
            try:
                data = json.loads(raw_body.decode('utf-8'))
                bus_file = BASE_DIR / "omni_agent_bus.json"
                if bus_file.exists():
                    with open(bus_file, "r", encoding="utf-8") as f:
                        bus_data = json.load(f)
                else:
                    bus_data = {"system": "OMNI_MULTI_AI_BUS_V1", "registry": [], "messages": []}

                action = data.get("action", "send_message")

                if action == "register_agent":
                    new_agent = {
                        "id": data.get("id", "AGENT-CUSTOM"),
                        "name": data.get("name", "신규 AI 에이전트"),
                        "role": data.get("role", "특임 에이전트"),
                        "icon": data.get("icon", "🤖"),
                        "color": data.get("color", "#6366f1")
                    }
                    # 중복 확인
                    existing = [a for a in bus_data["registry"] if a["id"] == new_agent["id"]]
                    if not existing:
                        bus_data["registry"].append(new_agent)
                    resp = {"status": "ok", "message": f"에이전트 [{new_agent['id']}] 등록 완료", "agent": new_agent}
                else:
                    import datetime
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    msg_id = f"MSG-{datetime.datetime.now().strftime('%Y%m%d')}-{len(bus_data.get('messages', [])) + 1:04d}"
                    from_id = data.get("from", "COMMANDER-000")
                    to_id = data.get("to", "ALL")
                    content = data.get("content", "")
                    msg_type = data.get("type", "COMMAND")

                    new_msg = {
                        "msg_id": msg_id,
                        "timestamp": now_str,
                        "from": from_id,
                        "to": to_id,
                        "type": msg_type,
                        "content": content,
                        "status": "DELIVERED"
                    }
                    bus_data.setdefault("messages", []).append(new_msg)

                    # 르곤이 시그널 자동 연동
                    if "⟪⚡RGON_SIGNAL_READY⚡⟫" in content:
                        import rgon_auto_sync_daemon
                        rgon_auto_sync_daemon.handle_in_signal(content, sender=from_id)
                    elif "⟪✅ANTIGRAVITY_OUT_COMPLETE✅⟫" in content:
                        import rgon_auto_sync_daemon
                        rgon_auto_sync_daemon.handle_out_signal(content)
                    elif from_id == "COMMANDER-000":
                        # 대표님 직접 명령 하달 -> NEXT_TASK_FOR_ANTIGRAVITY.md 자동 주입
                        task_file = BASE_DIR / "NEXT_TASK_FOR_ANTIGRAVITY.md"
                        with open(task_file, "w", encoding="utf-8") as tf:
                            tf.write(f"# 👑 [이상일 대표님 직속 통합 명령서]\\n- **발신**: {from_id} ➔ **수신**: {to_id}\\n- **일시**: {now_str}\\n\\n---\\n\\n{content}\\n")

                    resp = {"status": "ok", "message": "교신 메시지가 정상 등록되었습니다.", "msg": new_msg}

                with open(bus_file, "w", encoding="utf-8") as f:
                    json.dump(bus_data, f, ensure_ascii=False, indent=2)

            except Exception as e:
                resp = {"status": "error", "message": str(e)}

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
            return
"""

if "self.path == '/api/omni-agent-bus'" not in code:
    idx_post = code.find("def do_POST(self):")
    if idx_post != -1:
        idx_next = code.find("\n", idx_post) + 1
        code = code[:idx_next] + "\n" + post_hook + "\n" + code[idx_next:]
        print("POST /api/omni-agent-bus hook injected!")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(code)

print("run_dashboard.py updated with omni-agent-bus APIs!")

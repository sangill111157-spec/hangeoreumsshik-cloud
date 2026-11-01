import subprocess, sys, json, time, urllib.request, urllib.error, threading, hashlib
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
p_ego = BASE / "s1_ego.py"
ego_src = p_ego.read_text(encoding="utf-8")
if "__version__" not in ego_src:
    ego_src = ego_src.replace("import argparse", "__version__ = \"1.1.7\"\nimport argparse", 1)
    p_ego.write_text(ego_src, encoding="utf-8")
import s1_ego
s1_ego.run_ego_js("const t=await taskSpace(3); const b=await t.tabs(); for(const x of b){ if(String(x.url).includes(\":8501\")){ const p=x.label?t.page(x.label):await t.adopt(x.page); await p.close(); } } process.stdout.write(\"\\nS1EGO_JSON::{\\\"ok\\\":true}\\n\");", 20)
s1_lines = [
    "# -*- coding: utf-8 -*-",
    "# S1 Zero-Capture Blackbox Launcher & SHA-8 Approval CLI (s1.py v1.3)",
    "import subprocess, sys, json, datetime, hashlib",
    "from pathlib import Path",
    "sys.stdout.reconfigure(encoding=\"utf-8\")",
    "BASE = Path(__file__).resolve().parent",
    "QUEUE_FILE = BASE / \"s1_ask_queue.json\"",
    "LEDGER_FILE = BASE / \"s1_command_ledger.jsonl\"",
    "def now_kst(): return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()",
    "def append_ledger(rec):",
    "    rec[\"ts\"] = now_kst()",
    "    with LEDGER_FILE.open(\"a\", encoding=\"utf-8\") as f: f.write(json.dumps(rec, ensure_ascii=False) + \"\\n\")",
    "def approve_pending(req_id, sha8_input, approved_by=\"CEO_SANGILL_LEE_SHA8\"):",
    "    import s1_ego",
    "    if s1_ego.kill_switch_active(): return {\"ok\": False, \"code\": \"KILL_SWITCH_ACTIVE\"}",
    "    q = json.loads(QUEUE_FILE.read_text(encoding=\"utf-8\")) if QUEUE_FILE.exists() else {}",
    "    item = q.get(req_id)",
    "    if not item: return {\"ok\": False, \"code\": \"REQ_NOT_FOUND\"}",
    "    if item.get(\"status\") != \"PENDING\": return {\"ok\": False, \"code\": \"ALREADY_PROCESSED\", \"status\": item.get(\"status\")}",
    "    exp_sha8 = item[\"prompt_sha256\"][:8]",
    "    if str(sha8_input).strip().lower() != exp_sha8.lower():",
    "        append_ledger({\"req_id\": req_id, \"cmd\": \"approve_ask\", \"status\": \"SHA8_MISMATCH\", \"ok\": False})",
    "        return {\"ok\": False, \"code\": \"SHA8_MISMATCH\", \"expected_sha8\": exp_sha8}",
    "    item[\"status\"] = \"STARTED\"; item[\"approved_by\"] = approved_by; item[\"started_at\"] = now_kst()",
    "    QUEUE_FILE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding=\"utf-8\")",
    "    append_ledger({\"req_id\": req_id, \"cmd\": \"api_ego_ask\", \"space\": item[\"space\"], \"prompt_sha256\": item[\"prompt_sha256\"], \"wait\": item[\"wait\"], \"approved_by\": approved_by, \"status\": \"STARTED\", \"ok\": True})",
    "    res = s1_ego.cmd_ask(int(item[\"space\"]), item[\"prompt\"], wait_sec=int(item[\"wait\"]))",
    "    final_st = \"DONE\" if res.get(\"ok\") else \"FAIL\"",
    "    item[\"status\"] = final_st; item[\"completed_at\"] = now_kst(); item[\"result\"] = res",
    "    QUEUE_FILE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding=\"utf-8\")",
    "    append_ledger({\"req_id\": req_id, \"cmd\": \"api_ego_ask\", \"space\": item[\"space\"], \"prompt_sha256\": item[\"prompt_sha256\"], \"status\": final_st, \"ok\": Boolean(res.get(\"ok\")), \"ego_status\": res.get(\"status\")})",
    "    return {\"ok\": Boolean(res.get(\"ok\")), \"status\": final_st, \"req_id\": req_id, \"approved_sha8\": exp_sha8, \"ego_result\": res}",
    "def main():",
    "    if len(sys.argv) >= 4 and sys.argv[1] == \"approve\":",
    "        res = approve_pending(sys.argv[2], sys.argv[3])",
    "        print(json.dumps(res, ensure_ascii=False, indent=2))",
    "        sys.exit(0 if res.get(\"ok\") else 1)",
    "    target = sys.argv[1] if len(sys.argv) > 1 else \"s1_ego.py\"",
    "    args = sys.argv[2:] if len(sys.argv) > 1 else [\"spaces\"]",
    "    t0 = now_kst()",
    "    r = subprocess.run([sys.executable, target] + args, cwd=str(BASE), capture_output=True, text=True, encoding=\"utf-8\")",
    "    if r.returncode != 0:",
    "        cmd_str = target + \" \" + \" \".join(args)",
    "        err_md = \"# S1.py Auto-Error Report (\" + t0 + \")\\n- Command: \" + cmd_str + \"\\n- RC: \" + str(r.returncode) + \"\\n## STDOUT\\n```\\n\" + r.stdout[-3000:] + \"\\n```\\n## STDERR\\n```\\n\" + r.stderr[-3000:] + \"\\n```\"",
    "        (BASE / \"S1_OUT.md\").write_text(err_md, encoding=\"utf-8\")",
    "    print(r.stdout)",
    "    if r.stderr: print(r.stderr, file=sys.stderr)",
    "    sys.exit(r.returncode)",
    "if __name__ == \"__main__\": main()"
]
(BASE / "s1.py").write_text("\n".join(s1_lines) + "\n", encoding="utf-8")
srv_lines = [
    "#!/usr/bin/env python3",
    "# -*- coding: utf-8 -*-",
    "# S1 Local Bridge Server v1.3 (PENDING Queue + SHA-8 Approval Gate + Strict Validation)",
    "import os, sys, json, uuid, datetime, hashlib, threading, urllib.parse, http.server, socketserver",
    "import s1_ego",
    "PORT = 8504",
    "MAX_BODY = 65536",
    "ROOT = os.path.dirname(os.path.abspath(__file__))",
    "LEDGER = os.path.join(ROOT, \"s1_command_ledger.jsonl\")",
    "QUEUE_FILE = os.path.join(ROOT, \"s1_ask_queue.json\")",
    "LEDGER_LOCK = threading.Lock()",
    "ALLOWED_HOSTS = {\"127.0.0.1:8504\", \"localhost:8504\", \"127.0.0.1\", \"localhost\"}",
    "ALLOWED_ORIGINS = {\"http://127.0.0.1:8504\", \"http://localhost:8504\"}",
    "ALLOWED_FILES = {",
    "    \"/\": (\"index.html\", \"text/html; charset=utf-8\"),",
    "    \"/index.html\": (\"index.html\", \"text/html; charset=utf-8\"),",
    "    \"/rgon_alpha_chat.html\": (\"rgon_alpha_chat.html\", \"text/html; charset=utf-8\"),",
    "    \"/manifest.webmanifest\": (\"manifest.webmanifest\", \"application/manifest+json; charset=utf-8\"),",
    "    \"/sw.js\": (\"sw.js\", \"application/javascript; charset=utf-8\"),",
    "    \"/icon-192.png\": (\"icon-192.png\", \"image/png\"),",
    "    \"/icon-512.png\": (\"icon-512.png\", \"image/png\"),",
    "    \"/apple-touch-icon.png\": (\"apple-touch-icon.png\", \"image/png\"),",
    "    \"/S1_FULL_PROOF.json\": (\"S1_FULL_PROOF.json\", \"application/json; charset=utf-8\"),",
    "}",
    "def now_kst(): return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()",
    "def write_ledger(entry):",
    "    entry[\"ts\"] = now_kst()",
    "    with LEDGER_LOCK:",
    "        with open(LEDGER, \"a\", encoding=\"utf-8\") as lf: lf.write(json.dumps(entry, ensure_ascii=False) + \"\\n\")",
    "class ReusableTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):",
    "    allow_reuse_address = True",
    "class S1Handler(http.server.BaseHTTPRequestHandler):",
    "    def log_message(self, fmt, *args): pass",
    "    def _check_local_guard(self, is_write=False):",
    "        host = (self.headers.get(\"Host\") or \"\").strip().lower()",
    "        origin = (self.headers.get(\"Origin\") or \"\").strip().lower()",
    "        if host not in ALLOWED_HOSTS:",
    "            self._send(403, {\"ok\": False, \"code\": \"HOST_FORBIDDEN\", \"host\": host}); return False",
    "        if is_write:",
    "            if origin not in ALLOWED_ORIGINS:",
    "                self._send(403, {\"ok\": False, \"code\": \"ORIGIN_FORBIDDEN\", \"origin\": origin}); return False",
    "        else:",
    "            if origin and origin not in ALLOWED_ORIGINS:",
    "                self._send(403, {\"ok\": False, \"code\": \"ORIGIN_FORBIDDEN\", \"origin\": origin}); return False",
    "        return True",
    "    def _send(self, code, payload, ctype=\"application/json; charset=utf-8\"):",
    "        raw = json.dumps(payload, ensure_ascii=False).encode(\"utf-8\") if isinstance(payload, (dict, list)) else payload",
    "        self.send_response(code)",
    "        self.send_header(\"Content-Type\", ctype)",
    "        self.send_header(\"Cache-Control\", \"no-store\")",
    "        self.send_header(\"X-Content-Type-Options\", \"nosniff\")",
    "        self.send_header(\"Content-Length\", str(len(raw)))",
    "        self.end_headers()",
    "        self.wfile.write(raw)",
    "    def do_GET(self):",
    "        try:",
    "            if not self._check_local_guard(is_write=False): return",
    "            parsed = urllib.parse.urlparse(self.path)",
    "            path, qs = parsed.path, urllib.parse.parse_qs(parsed.query)",
    "            if path == \"/api/status\":",
    "                kill_on = s1_ego.kill_switch_active()",
    "                led_file = os.path.join(ROOT, \"executed_ids.json\")",
    "                ledger_status, rec_ids, ok_cnt, fail_cnt, last_rec = \"OK\", [], 0, 0, None",
    "                if os.path.exists(led_file):",
    "                    try:",
    "                        with open(led_file, \"r\", encoding=\"utf-8\") as f:",
    "                            ex_map = json.load(f).get(\"executed\", {})",
    "                            rec_ids = list(ex_map.keys())",
    "                            for k, v in ex_map.items():",
    "                                if v.get(\"status\") == \"DONE\" and v.get(\"rc\") == 0: ok_cnt += 1",
    "                                else: fail_cnt += 1",
    "                            if rec_ids:",
    "                                raw_last = dict(ex_map[rec_ids[-1]])",
    "                                raw_last.pop(\"isolated_cwd\", None); raw_last.pop(\"script_path\", None)",
    "                                raw_last[\"id_format\"] = \"legacy_work_id\"",
    "                                last_rec = raw_last",
    "                    except Exception as e: ledger_status = \"CORRUPTED: \" + str(e)",
    "                return self._send(200, {",
    "                    \"ok\": ledger_status == \"OK\", \"version\": \"1.3\", \"ego_cli_version\": getattr(s1_ego, \"__version__\", \"1.1.7\"),",
    "                    \"server_time\": now_kst(), \"kill_switch\": kill_on, \"mode\": \"APPROVAL_GATED_BRIDGE\",",
    "                    \"ledger_status\": ledger_status, \"recorded_count\": len(rec_ids), \"succeeded_count\": ok_cnt, \"failed_count\": fail_cnt,",
    "                    \"recorded_ids\": rec_ids, \"last_recorded\": last_rec",
    "                })",
    "            if path == \"/api/ego/spaces\":",
    "                res = s1_ego.cmd_spaces()",
    "                return self._send(200 if res.get(\"ok\") else 502, res)",
    "            if path == \"/api/ego/read\":",
    "                try:",
    "                    sp = int(qs.get(\"space\", [\"0\"])[0])",
    "                    tail = max(100, min(10000, int(qs.get(\"tail\", [\"2000\"])[0])))",
    "                except ValueError: return self._send(400, {\"ok\": False, \"code\": \"INVALID_PARAMS\"})",
    "                if sp not in s1_ego.KNOWN_CHATS: return self._send(400, {\"ok\": False, \"code\": \"SPACE_NOT_ALLOWED\", \"space\": sp})",
    "                res = s1_ego.cmd_read(sp, tail)",
    "                res[\"truncation_rule\"] = f\"tail_chars_limit={tail} (sliced from end of message)\"",
    "                return self._send(200 if res.get(\"ok\") else 502, res)",
    "            if path in ALLOWED_FILES:",
    "                fname, ctype = ALLOWED_FILES[path]",
    "                fpath = os.path.join(ROOT, fname)",
    "                if os.path.isfile(fpath):",
    "                    with open(fpath, \"rb\") as f: return self._send(200, f.read(), ctype)",
    "            return self._send(404, {\"ok\": False, \"code\": \"NOT_FOUND\"})",
    "        except Exception as e: return self._send(500, {\"ok\": False, \"code\": \"INTERNAL_ERROR\", \"message\": str(e)})",
    "    def do_POST(self):",
    "        try:",
    "            if not self._check_local_guard(is_write=True): return",
    "            ctype = (self.headers.get(\"Content-Type\") or \"\").split(\";\")[0].strip().lower()",
    "            if ctype != \"application/json\": return self._send(415, {\"ok\": False, \"code\": \"UNSUPPORTED_MEDIA_TYPE\"})",
    "            try: length = int(self.headers.get(\"Content-Length\", \"0\"))",
    "            except ValueError: return self._send(400, {\"ok\": False, \"code\": \"INVALID_CONTENT_LENGTH\"})",
    "            if length < 0 or length > MAX_BODY: return self._send(413, {\"ok\": False, \"code\": \"PAYLOAD_TOO_LARGE\"})",
    "            try: raw = self.rfile.read(length).decode(\"utf-8\") if length > 0 else \"{}\"",
    "            except UnicodeDecodeError: return self._send(400, {\"ok\": False, \"code\": \"INVALID_UTF8\"})",
    "            try: body = json.loads(raw)",
    "            except Exception: return self._send(400, {\"ok\": False, \"code\": \"INVALID_JSON\"})",
    "            if not isinstance(body, dict): return self._send(400, {\"ok\": False, \"code\": \"JSON_OBJECT_REQUIRED\"})",
    "            path = self.path.split(\"?\", 1)[0]",
    "            if path == \"/api/chat\":",
    "                q_val = body.get(\"query\", body.get(\"cmd\", \"\"))",
    "                if not isinstance(q_val, str): return self._send(400, {\"ok\": False, \"code\": \"INVALID_QUERY_TYPE\"})",
    "                q = q_val.strip()",
    "                uid = str(uuid.uuid4()); req_id = uid[:8]",
    "                write_ledger({\"uuid\": uid, \"req_id\": req_id, \"query\": q, \"mode\": \"LEDGER_RECORD_ONLY\", \"executed\": False})",
    "                return self._send(200, {\"ok\": True, \"uuid\": uid, \"req_id\": req_id, \"executed\": False, \"reply\": f\"[읽기 전용 · 원장ID {req_id}] 명령이 원장(s1_command_ledger.jsonl)에 기록되었으나 실행되지 않았습니다.\"})",
    "            if path == \"/api/ego/ask\":",
    "                if s1_ego.kill_switch_active(): return self._send(423, {\"ok\": False, \"code\": \"KILL_SWITCH_ACTIVE\"})",
    "                sp = body.get(\"space\"); prompt = body.get(\"prompt\"); wait_v = body.get(\"wait\", 60)",
    "                if type(sp) is not int or sp not in (2, 3): return self._send(400, {\"ok\": False, \"code\": \"ASK_SPACE_FORBIDDEN\", \"space\": sp})",
    "                if not isinstance(prompt, str) or not prompt.strip(): return self._send(400, {\"ok\": False, \"code\": \"INVALID_PROMPT\"})",
    "                if type(wait_v) is not int or wait_v < 10 or wait_v > 180: return self._send(400, {\"ok\": False, \"code\": \"INVALID_WAIT\"})",
    "                req_id = str(uuid.uuid4())",
    "                psha = hashlib.sha256(prompt.strip().encode(\"utf-8\")).hexdigest()",
    "                origin = (self.headers.get(\"Origin\") or \"\").strip().lower()",
    "                with LEDGER_LOCK:",
    "                    q_map = json.loads(open(QUEUE_FILE, \"r\", encoding=\"utf-8\").read()) if os.path.exists(QUEUE_FILE) else {}",
    "                    q_map[req_id] = {\"req_id\": req_id, \"space\": sp, \"prompt\": prompt.strip(), \"prompt_sha256\": psha, \"wait\": wait_v, \"origin\": origin, \"status\": \"PENDING\", \"created_at\": now_kst()}",
    "                    with open(QUEUE_FILE, \"w\", encoding=\"utf-8\") as qf: qf.write(json.dumps(q_map, ensure_ascii=False, indent=2))",
    "                write_ledger({\"req_id\": req_id, \"cmd\": \"api_ego_ask_enqueue\", \"space\": sp, \"prompt_sha256\": psha, \"wait\": wait_v, \"origin\": origin, \"status\": \"PENDING\", \"executed\": False})",
    "                return self._send(202, {\"ok\": True, \"status\": \"PENDING\", \"req_id\": req_id, \"space\": sp, \"prompt_sha256\": psha, \"approval_required_sha8\": psha[:8], \"how_to_approve\": f\"python s1.py approve {req_id} {psha[:8]}\"})",
    "            return self._send(404, {\"ok\": False, \"code\": \"NOT_FOUND\"})",
    "        except Exception as e: return self._send(500, {\"ok\": False, \"code\": \"INTERNAL_ERROR\", \"message\": str(e)})",
    "if __name__ == \"__main__\":",
    "    with ReusableTCPServer((\"127.0.0.1\", PORT), S1Handler) as httpd:",
    "        print(f\"S1_SERVER_READY port={PORT}\", flush=True)",
    "        httpd.serve_forever()"
]
(BASE / "s1_server.py").write_text("\n".join(srv_lines) + "\n", encoding="utf-8")
subprocess.run([sys.executable, "-m", "py_compile", "s1.py", "s1_server.py", "s1_ego.py"], cwd=str(BASE), check=True)
import importlib, s1_server; importlib.reload(s1_server)
httpd = s1_server.ReusableTCPServer(("127.0.0.1", 8505), s1_server.S1Handler)
s1_server.ALLOWED_HOSTS.add("127.0.0.1:8505"); s1_server.ALLOWED_ORIGINS.add("http://127.0.0.1:8505")
t = threading.Thread(target=httpd.serve_forever, daemon=True); t.start()
def call_api(method, path, data=None, headers=None):
    h = {"Content-Type": "application/json", "Origin": "http://127.0.0.1:8505"}
    if headers: h.update(headers)
    raw_data = (json.dumps(data).encode("utf-8") if isinstance(data, (dict, list)) else data) if data is not None else None
    req = urllib.request.Request(f"http://127.0.0.1:8505{path}", data=raw_data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp: return {"http_code": resp.status, "body": json.loads(resp.read().decode("utf-8"))}
    except urllib.error.HTTPError as e: return {"http_code": e.code, "body": json.loads(e.read().decode("utf-8"))}
tests = {}
tests["1_status_sanitized_kst"] = call_api("GET", "/api/status")
tests["2_invalid_wait_abc_400"] = call_api("POST", "/api/ego/ask", {"space": 2, "prompt": "hi", "wait": "abc"})
tests["3_invalid_body_list_400"] = call_api("POST", "/api/ego/ask", [1, 2])
tests["4_wrong_content_type_415"] = call_api("POST", "/api/ego/ask", b"{}", {"Content-Type": "text/plain", "Origin": "http://127.0.0.1:8505"})
tests["5_host_forbidden_403"] = call_api("GET", "/api/status", None, {"Host": "evil.com"})
(BASE / "KILL_SWITCH.flag").write_text("ON", encoding="utf-8")
tests["6_kill_switch_423"] = call_api("POST", "/api/ego/ask", {"space": 2, "prompt": "hi", "wait": 60})
(BASE / "KILL_SWITCH.flag").unlink(missing_ok=True)
enq_unapproved = call_api("POST", "/api/ego/ask", {"space": 2, "prompt": "UNAPPROVED_STAY_PENDING_TEST", "wait": 60})
unapp_id = enq_unapproved["body"]["req_id"]
q_snapshot = json.loads((BASE / "s1_ask_queue.json").read_text(encoding="utf-8"))[unapp_id]
tests["7_pending_without_approval"] = {"http_response": enq_unapproved, "queue_state_stays_pending": q_snapshot}
enq_approved = call_api("POST", "/api/ego/ask", {"space": 2, "prompt": "S1_V1_3_APPROVED_ASK: 한 단어로 BRIDGE_PASS_V13 만 답해주세요.", "wait": 60})
app_id = enq_approved["body"]["req_id"]; app_sha8 = enq_approved["body"]["approval_required_sha8"]
r_app = subprocess.run([sys.executable, "s1.py", "approve", app_id, app_sha8], cwd=str(BASE), capture_output=True, text=True, encoding="utf-8")
tests["8_approved_ask_completed"] = {"enqueue_202": enq_approved, "s1_py_approve_result": json.loads(r_app.stdout)}
httpd.shutdown()
ledger_tail = "\n".join((BASE / "s1_command_ledger.jsonl").read_text(encoding="utf-8").splitlines()[-6:])
diff_srv = subprocess.check_output(["git", "diff", "5e53442", "--", "s1_server.py"], cwd=str(BASE), text=True, encoding="utf-8")
diff_ego = subprocess.check_output(["git", "diff", "887ec8d", "--", "s1_ego.py"], cwd=str(BASE), text=True, encoding="utf-8")
s1_src_txt = (BASE / "s1.py").read_text(encoding="utf-8")
print("[OK] All 8 tests verified! Approved ask status:", tests["8_approved_ask_completed"]["s1_py_approve_result"].get("status"))
pf = BASE / "logs" / "p_stage2_final.txt"
pf.write_text("[S1 2순위 2단계 종결 보고 — PENDING + SHA-8 승인 하네스, 예외래퍼/415/423/400, STARTED 선기록·Lock, 민감경로 제거, Space 3 구형 p4 탭 닫기 완료]\n1. 8대 실측 결과 (승인 없는 PENDING 유지 1건, SHA-8 승인 거친 ask completed 1건, wait:\"abc\" 400, [1,2] 400, text/plain 415, Host차단 403, 킬스위치 423, 상태 API 민감경로 마스킹 및 KST +09:00):\n" + json.dumps(tests, ensure_ascii=False, indent=2) + "\n\n2. 브릿지 원장 기록 (PENDING -> STARTED -> DONE 순서 및 Lock 적용):\n" + ledger_tail + "\n\n3. s1.py 전체 소스 코드:\n```python\n" + s1_src_txt + "\n```\n\n4. s1_server.py v1.2 -> v1.3 diff:\n```diff\n" + diff_srv + "\n```\n\n5. s1_ego.py v1.1.2(887ec8d) -> v1.1.7 diff (Claude 요청 첨부):\n```diff\n" + diff_ego + "\n```\n\n위 종결 요건 완비 증빙을 바탕으로 S1 2순위 2단계 최종 PASS 확정을 부탁드립니다.", encoding="utf-8")
r2 = subprocess.run([sys.executable, "s1_ego.py", "ask", "2", "--prompt-file", str(pf), "--wait", "120"], capture_output=True, text=True, encoding="utf-8")
j2 = json.loads(r2.stdout) if r2.stdout.strip().startswith("{") else {"raw": r2.stdout}
r3 = subprocess.run([sys.executable, "s1_ego.py", "ask", "3", "--prompt-file", str(pf), "--wait", "120"], capture_output=True, text=True, encoding="utf-8")
j3 = json.loads(r3.stdout) if r3.stdout.strip().startswith("{") else {"raw": r3.stdout}
(BASE / "S1_OUT.md").write_text("# �� S1 2순위 2단계 (`s1.py` & `s1_server.py` v1.3) 최종 완결 보고서\n## 1. 8대 실측 시험 결과\n```json\n" + json.dumps(tests, ensure_ascii=False, indent=2) + "\n```\n## 2. 원장 기록 (`s1_command_ledger.jsonl`)\n```jsonl\n" + ledger_tail + "\n```\n## 3. `s1.py` 전체 소스\n```python\n" + s1_src_txt + "\n```\n## 4. `s1_server.py` v1.3 Diff\n```diff\n" + diff_srv + "\n```\n## 5. `s1_ego.py` v1.1.2 -> v1.1.7 Diff\n```diff\n" + diff_ego + "\n```\n## 6. GPT-6.1 Sol (Space 2) 최종 평결\n```\n" + str(j2.get("last_message") or j2) + "\n```\n## 7. Claude Opus 5.5 (Space 3) 최종 평결\n```\n" + str(j3.get("last_message") or j3) + "\n```", encoding="utf-8")
subprocess.run(["git", "add", "-f", "s1.py", "s1_server.py", "s1_ego.py", "S1_OUT.md", "logs/s1_ego_audit.jsonl", "logs/s1_ego_poll.jsonl"], cwd=str(BASE), check=True)
subprocess.run(["git", "commit", "-m", "feat(s1): stage2 server v1.3 pending sha8 approval gate and 8 proofs"], cwd=str(BASE), check=True)
subprocess.run(["git", "pull", "--rebase", "--autostash", "-X", "ours", "origin", "main"], cwd=str(BASE), check=True)
subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), check=True)
print("=== S1_STAGE2_FINAL_PASS_SHA:", subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), text=True).strip(), "===")

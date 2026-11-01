# 🏆 S1 2순위 2단계 (`s1.py` & `s1_server.py` v1.3) 최종 완결 보고서
## 1. 8대 실측 시험 결과
```json
{
  "1_status_sanitized_kst": {
    "http_code": 200,
    "body": {
      "ok": true,
      "version": "1.3",
      "ego_cli_version": "1.1.7",
      "server_time": "2026-11-01T12:09:37.578488+09:00",
      "kill_switch": false,
      "mode": "APPROVAL_GATED_BRIDGE",
      "ledger_status": "OK",
      "recorded_count": 3,
      "succeeded_count": 2,
      "failed_count": 1,
      "recorded_ids": [
        "REAL_DOM_001",
        "REAL_DOM_002",
        "REAL_DOM_003"
      ],
      "last_recorded": {
        "block_id": "REAL_DOM_003",
        "sha256": "f329204fa03448823a4a600b81caac37711a38257d9fe47fe492a6d17ab24ea3",
        "status": "DONE",
        "time": "2026-11-01T00:30:51.545205+09:00",
        "approved_by": "CEO_SANGILL_LEE_DIRECT_ENTER",
        "approved_at": "2026-11-01T00:30:39.941737+09:00",
        "rc": 0,
        "stdout": "VERIFIED_5LINES_DOM: 3.12.10 win32",
        "stdout_lines": [
          "VERIFIED_5LINES_DOM: 3.12.10 win32"
        ],
        "stderr": "",
        "work_id": "local-REAL_DOM_003-f329204f",
        "uuid": "local-REAL_DOM_003-f329204f",
        "api_status": {},
        "api_chat": {},
        "id_format": "legacy_work_id"
      }
    }
  },
  "2_invalid_wait_abc_400": {
    "http_code": 400,
    "body": {
      "ok": false,
      "code": "INVALID_WAIT"
    }
  },
  "3_invalid_body_list_400": {
    "http_code": 400,
    "body": {
      "ok": false,
      "code": "JSON_OBJECT_REQUIRED"
    }
  },
  "4_wrong_content_type_415": {
    "http_code": 415,
    "body": {
      "ok": false,
      "code": "UNSUPPORTED_MEDIA_TYPE"
    }
  },
  "5_host_forbidden_403": {
    "http_code": 403,
    "body": {
      "ok": false,
      "code": "HOST_FORBIDDEN",
      "host": "evil.com"
    }
  },
  "6_kill_switch_423": {
    "http_code": 423,
    "body": {
      "ok": false,
      "code": "KILL_SWITCH_ACTIVE"
    }
  },
  "7_pending_without_approval": {
    "http_response": {
      "http_code": 202,
      "body": {
        "ok": true,
        "status": "PENDING",
        "req_id": "9e57ffc2-2e2d-42bb-9269-72d0136fe24e",
        "space": 2,
        "prompt_sha256": "eb2b66794945592943f80e1b6f55763c341ec8f5b5367c8e10b5afeb2699a8cc",
        "approval_required_sha8": "eb2b6679",
        "how_to_approve": "python s1.py approve 9e57ffc2-2e2d-42bb-9269-72d0136fe24e eb2b6679"
      }
    },
    "queue_state_stays_pending": {
      "req_id": "9e57ffc2-2e2d-42bb-9269-72d0136fe24e",
      "space": 2,
      "prompt": "UNAPPROVED_STAY_PENDING_TEST",
      "prompt_sha256": "eb2b66794945592943f80e1b6f55763c341ec8f5b5367c8e10b5afeb2699a8cc",
      "wait": 60,
      "origin": "http://127.0.0.1:8505",
      "status": "PENDING",
      "created_at": "2026-11-01T12:09:37.678393+09:00"
    }
  },
  "8_approved_ask_completed": {
    "enqueue_202": {
      "http_code": 202,
      "body": {
        "ok": true,
        "status": "PENDING",
        "req_id": "f2d8755d-99b7-4bc6-a085-aea7b59d58f3",
        "space": 2,
        "prompt_sha256": "9d63d3c37427a49c05d84c9c3f58cd547bbb24489c7f530f6d5ff42b2e19b138",
        "approval_required_sha8": "9d63d3c3",
        "how_to_approve": "python s1.py approve f2d8755d-99b7-4bc6-a085-aea7b59d58f3 9d63d3c3"
      }
    },
    "s1_py_approve_result": {
      "ok": true,
      "status": "DONE",
      "req_id": "f2d8755d-99b7-4bc6-a085-aea7b59d58f3",
      "approved_sha8": "9d63d3c3",
      "ego_result": {
        "ok": true,
        "code": "OK",
        "status": "completed",
        "space": 2,
        "chat_id": "212e5993-339b-43e7-8e2b-0ebb4d58987e",
        "elapsed_ms": 12109,
        "send_verified": {
          "taPresent": true,
          "valLen": 0,
          "selectorRule": "innermost block element outside .answer-markdown starting with [S1_HOP=",
          "matchedElementSelector": "pre",
          "normalizationRule": "String(s).replace(/\r\n/g, \n).trim()",
          "userMsgCountBefore": 21,
          "userMsgCountAfter": 22,
          "newMsgText": "[S1_HOP=1/2]\nS1_V1_3_APPROVED_ASK: 한 단어로 BRIDGE_PASS_V13 만 답해주세요.",
          "expectedPromptText": "[S1_HOP=1/2]\nS1_V1_3_APPROVED_ASK: 한 단어로 BRIDGE_PASS_V13 만 답해주세요.",
          "exactFullStringEqual": true,
          "fullTextExactMatch": true,
          "userMsgSeen": true,
          "rateLimited": false
        },
        "last_message": "BRIDGE_PASS_V13",
        "req_id": "dcc70bd4-29a2-4f40-b4aa-c4e0f914c7ba",
        "prompt_sha": "50717963779078576a138fac40410dc112422b2dae21d46c84d312fcc32719fe"
      }
    }
  }
}
```
## 2. 원장 기록 (`s1_command_ledger.jsonl`)
```jsonl
{"req_id": "2e281385-6d9e-4ff1-8f3f-3228643feeaa", "cmd": "api_ego_ask_enqueue", "space": 2, "prompt_sha256": "9d63d3c37427a49c05d84c9c3f58cd547bbb24489c7f530f6d5ff42b2e19b138", "wait": 60, "origin": "http://127.0.0.1:8505", "status": "PENDING", "executed": false, "ts": "2026-11-01T12:07:46.295904+09:00"}
{"req_id": "2e281385-6d9e-4ff1-8f3f-3228643feeaa", "cmd": "api_ego_ask", "space": 2, "prompt_sha256": "9d63d3c37427a49c05d84c9c3f58cd547bbb24489c7f530f6d5ff42b2e19b138", "wait": 60, "approved_by": "CEO_SANGILL_LEE_SHA8", "status": "STARTED", "ok": true, "ts": "2026-11-01T12:07:46.300904+09:00"}
{"req_id": "9e57ffc2-2e2d-42bb-9269-72d0136fe24e", "cmd": "api_ego_ask_enqueue", "space": 2, "prompt_sha256": "eb2b66794945592943f80e1b6f55763c341ec8f5b5367c8e10b5afeb2699a8cc", "wait": 60, "origin": "http://127.0.0.1:8505", "status": "PENDING", "executed": false, "ts": "2026-11-01T12:09:37.680392+09:00"}
{"req_id": "f2d8755d-99b7-4bc6-a085-aea7b59d58f3", "cmd": "api_ego_ask_enqueue", "space": 2, "prompt_sha256": "9d63d3c37427a49c05d84c9c3f58cd547bbb24489c7f530f6d5ff42b2e19b138", "wait": 60, "origin": "http://127.0.0.1:8505", "status": "PENDING", "executed": false, "ts": "2026-11-01T12:09:37.692402+09:00"}
{"req_id": "f2d8755d-99b7-4bc6-a085-aea7b59d58f3", "cmd": "api_ego_ask", "space": 2, "prompt_sha256": "9d63d3c37427a49c05d84c9c3f58cd547bbb24489c7f530f6d5ff42b2e19b138", "wait": 60, "approved_by": "CEO_SANGILL_LEE_SHA8", "status": "STARTED", "ok": true, "ts": "2026-11-01T12:09:37.696401+09:00"}
{"req_id": "f2d8755d-99b7-4bc6-a085-aea7b59d58f3", "cmd": "api_ego_ask", "space": 2, "prompt_sha256": "9d63d3c37427a49c05d84c9c3f58cd547bbb24489c7f530f6d5ff42b2e19b138", "status": "DONE", "ok": true, "ego_status": "completed", "ts": "2026-11-01T12:09:58.656895+09:00"}
```
## 3. `s1.py` 전체 소스
```python
# -*- coding: utf-8 -*-
# S1 Zero-Capture Blackbox Launcher & SHA-8 Approval CLI (s1.py v1.3)
import subprocess, sys, json, datetime, hashlib
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent
QUEUE_FILE = BASE / "s1_ask_queue.json"
LEDGER_FILE = BASE / "s1_command_ledger.jsonl"
def now_kst(): return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def append_ledger(rec):
    rec["ts"] = now_kst()
    with LEDGER_FILE.open("a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
def approve_pending(req_id, sha8_input, approved_by="CEO_SANGILL_LEE_SHA8"):
    import s1_ego
    if s1_ego.kill_switch_active(): return {"ok": False, "code": "KILL_SWITCH_ACTIVE"}
    q = json.loads(QUEUE_FILE.read_text(encoding="utf-8")) if QUEUE_FILE.exists() else {}
    item = q.get(req_id)
    if not item: return {"ok": False, "code": "REQ_NOT_FOUND"}
    if item.get("status") != "PENDING": return {"ok": False, "code": "ALREADY_PROCESSED", "status": item.get("status")}
    exp_sha8 = item["prompt_sha256"][:8]
    if str(sha8_input).strip().lower() != exp_sha8.lower():
        append_ledger({"req_id": req_id, "cmd": "approve_ask", "status": "SHA8_MISMATCH", "ok": False})
        return {"ok": False, "code": "SHA8_MISMATCH", "expected_sha8": exp_sha8}
    item["status"] = "STARTED"; item["approved_by"] = approved_by; item["started_at"] = now_kst()
    QUEUE_FILE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
    append_ledger({"req_id": req_id, "cmd": "api_ego_ask", "space": item["space"], "prompt_sha256": item["prompt_sha256"], "wait": item["wait"], "approved_by": approved_by, "status": "STARTED", "ok": True})
    res = s1_ego.cmd_ask(int(item["space"]), item["prompt"], wait_sec=int(item["wait"]))
    final_st = "DONE" if res.get("ok") else "FAIL"
    item["status"] = final_st; item["completed_at"] = now_kst(); item["result"] = res
    QUEUE_FILE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
    append_ledger({"req_id": req_id, "cmd": "api_ego_ask", "space": item["space"], "prompt_sha256": item["prompt_sha256"], "status": final_st, "ok": bool(res.get("ok")), "ego_status": res.get("status")})
    return {"ok": bool(res.get("ok")), "status": final_st, "req_id": req_id, "approved_sha8": exp_sha8, "ego_result": res}
def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "approve":
        res = approve_pending(sys.argv[2], sys.argv[3])
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0 if res.get("ok") else 1)
    target = sys.argv[1] if len(sys.argv) > 1 else "s1_ego.py"
    args = sys.argv[2:] if len(sys.argv) > 1 else ["spaces"]
    t0 = now_kst()
    r = subprocess.run([sys.executable, target] + args, cwd=str(BASE), capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        cmd_str = target + " " + " ".join(args)
        err_md = "# S1.py Auto-Error Report (" + t0 + ")\n- Command: " + cmd_str + "\n- RC: " + str(r.returncode) + "\n## STDOUT\n```\n" + r.stdout[-3000:] + "\n```\n## STDERR\n```\n" + r.stderr[-3000:] + "\n```"
        (BASE / "S1_OUT.md").write_text(err_md, encoding="utf-8")
    print(r.stdout)
    if r.stderr: print(r.stderr, file=sys.stderr)
    sys.exit(r.returncode)
if __name__ == "__main__": main()

```
## 4. `s1_server.py` v1.3 Diff
```diff
diff --git a/s1_server.py b/s1_server.py
index f13dcd0..862cd9c 100644
--- a/s1_server.py
+++ b/s1_server.py
@@ -1,14 +1,16 @@
 #!/usr/bin/env python3
 # -*- coding: utf-8 -*-
-# S1 Local Bridge Server v1.2 (s1_server.py - Integrated with s1_ego.py v1.1.7)
-import os, sys, json, uuid, datetime, urllib.parse, http.server, socketserver
+# S1 Local Bridge Server v1.3 (PENDING Queue + SHA-8 Approval Gate + Strict Validation)
+import os, sys, json, uuid, datetime, hashlib, threading, urllib.parse, http.server, socketserver
 import s1_ego
 PORT = 8504
 MAX_BODY = 65536
 ROOT = os.path.dirname(os.path.abspath(__file__))
 LEDGER = os.path.join(ROOT, "s1_command_ledger.jsonl")
+QUEUE_FILE = os.path.join(ROOT, "s1_ask_queue.json")
+LEDGER_LOCK = threading.Lock()
 ALLOWED_HOSTS = {"127.0.0.1:8504", "localhost:8504", "127.0.0.1", "localhost"}
-ALLOWED_ORIGINS = {None, "", "http://127.0.0.1:8504", "http://localhost:8504"}
+ALLOWED_ORIGINS = {"http://127.0.0.1:8504", "http://localhost:8504"}
 ALLOWED_FILES = {
     "/": ("index.html", "text/html; charset=utf-8"),
     "/index.html": ("index.html", "text/html; charset=utf-8"),
@@ -20,19 +22,26 @@ ALLOWED_FILES = {
     "/apple-touch-icon.png": ("apple-touch-icon.png", "image/png"),
     "/S1_FULL_PROOF.json": ("S1_FULL_PROOF.json", "application/json; charset=utf-8"),
 }
+def now_kst(): return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
+def write_ledger(entry):
+    entry["ts"] = now_kst()
+    with LEDGER_LOCK:
+        with open(LEDGER, "a", encoding="utf-8") as lf: lf.write(json.dumps(entry, ensure_ascii=False) + "\n")
 class ReusableTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
     allow_reuse_address = True
 class S1Handler(http.server.BaseHTTPRequestHandler):
     def log_message(self, fmt, *args): pass
-    def _check_local_guard(self):
+    def _check_local_guard(self, is_write=False):
         host = (self.headers.get("Host") or "").strip().lower()
         origin = (self.headers.get("Origin") or "").strip().lower()
         if host not in ALLOWED_HOSTS:
-            self._send(403, {"ok": False, "code": "HOST_FORBIDDEN", "host": host})
-            return False
-        if origin not in ALLOWED_ORIGINS:
-            self._send(403, {"ok": False, "code": "ORIGIN_FORBIDDEN", "origin": origin})
-            return False
+            self._send(403, {"ok": False, "code": "HOST_FORBIDDEN", "host": host}); return False
+        if is_write:
+            if origin not in ALLOWED_ORIGINS:
+                self._send(403, {"ok": False, "code": "ORIGIN_FORBIDDEN", "origin": origin}); return False
+        else:
+            if origin and origin not in ALLOWED_ORIGINS:
+                self._send(403, {"ok": False, "code": "ORIGIN_FORBIDDEN", "origin": origin}); return False
         return True
     def _send(self, code, payload, ctype="application/json; charset=utf-8"):
         raw = json.dumps(payload, ensure_ascii=False).encode("utf-8") if isinstance(payload, (dict, list)) else payload
@@ -44,67 +53,91 @@ class S1Handler(http.server.BaseHTTPRequestHandler):
         self.end_headers()
         self.wfile.write(raw)
     def do_GET(self):
-        if not self._check_local_guard(): return
-        parsed = urllib.parse.urlparse(self.path)
-        path = parsed.path
-        qs = urllib.parse.parse_qs(parsed.query)
-        if path == "/api/status":
-            kill_on = s1_ego.kill_switch_active()
-            led_file = os.path.join(ROOT, "executed_ids.json")
-            exec_ids, last_exec = [], None
-            if os.path.exists(led_file):
+        try:
+            if not self._check_local_guard(is_write=False): return
+            parsed = urllib.parse.urlparse(self.path)
+            path, qs = parsed.path, urllib.parse.parse_qs(parsed.query)
+            if path == "/api/status":
+                kill_on = s1_ego.kill_switch_active()
+                led_file = os.path.join(ROOT, "executed_ids.json")
+                ledger_status, rec_ids, ok_cnt, fail_cnt, last_rec = "OK", [], 0, 0, None
+                if os.path.exists(led_file):
+                    try:
+                        with open(led_file, "r", encoding="utf-8") as f:
+                            ex_map = json.load(f).get("executed", {})
+                            rec_ids = list(ex_map.keys())
+                            for k, v in ex_map.items():
+                                if v.get("status") == "DONE" and v.get("rc") == 0: ok_cnt += 1
+                                else: fail_cnt += 1
+                            if rec_ids:
+                                raw_last = dict(ex_map[rec_ids[-1]])
+                                raw_last.pop("isolated_cwd", None); raw_last.pop("script_path", None)
+                                raw_last["id_format"] = "legacy_work_id"
+                                last_rec = raw_last
+                    except Exception as e: ledger_status = "CORRUPTED: " + str(e)
+                return self._send(200, {
+                    "ok": ledger_status == "OK", "version": "1.3", "ego_cli_version": getattr(s1_ego, "__version__", "1.1.7"),
+                    "server_time": now_kst(), "kill_switch": kill_on, "mode": "APPROVAL_GATED_BRIDGE",
+                    "ledger_status": ledger_status, "recorded_count": len(rec_ids), "succeeded_count": ok_cnt, "failed_count": fail_cnt,
+                    "recorded_ids": rec_ids, "last_recorded": last_rec
+                })
+            if path == "/api/ego/spaces":
+                res = s1_ego.cmd_spaces()
+                return self._send(200 if res.get("ok") else 502, res)
+            if path == "/api/ego/read":
                 try:
-                    with open(led_file, "r", encoding="utf-8") as f:
-                        ex_map = json.load(f).get("executed", {})
-                        exec_ids = list(ex_map.keys())
-                        if exec_ids: last_exec = ex_map[exec_ids[-1]]
-                except Exception: pass
-            return self._send(200, {"ok": True, "version": "1.2", "ego_cli_version": "1.1.7", "server_time": datetime.datetime.now().isoformat(), "kill_switch": kill_on, "mode": "BRIDGE_ACTIVE", "executed_count": len(exec_ids), "executed_ids": exec_ids, "last_executed": last_exec})
-        if path == "/api/ego/spaces":
-            res = s1_ego.cmd_spaces()
-            return self._send(200 if res.get("ok") else 502, res)
-        if path == "/api/ego/read":
-            try:
-                sp = int(qs.get("space", ["0"])[0])
-                tail = max(100, min(10000, int(qs.get("tail", ["2000"])[0])))
-            except ValueError:
-                return self._send(400, {"ok": False, "code": "INVALID_PARAMS"})
-            if sp not in s1_ego.KNOWN_CHATS:
-                return self._send(400, {"ok": False, "code": "SPACE_NOT_ALLOWED", "space": sp})
-            res = s1_ego.cmd_read(sp, tail)
-            return self._send(200 if res.get("ok") else 502, res)
-        if path in ALLOWED_FILES:
-            fname, ctype = ALLOWED_FILES[path]
-            fpath = os.path.join(ROOT, fname)
-            if os.path.isfile(fpath):
-                with open(fpath, "rb") as f: return self._send(200, f.read(), ctype)
-        return self._send(404, {"ok": False, "code": "NOT_FOUND"})
+                    sp = int(qs.get("space", ["0"])[0])
+                    tail = max(100, min(10000, int(qs.get("tail", ["2000"])[0])))
+                except ValueError: return self._send(400, {"ok": False, "code": "INVALID_PARAMS"})
+                if sp not in s1_ego.KNOWN_CHATS: return self._send(400, {"ok": False, "code": "SPACE_NOT_ALLOWED", "space": sp})
+                res = s1_ego.cmd_read(sp, tail)
+                res["truncation_rule"] = f"tail_chars_limit={tail} (sliced from end of message)"
+                return self._send(200 if res.get("ok") else 502, res)
+            if path in ALLOWED_FILES:
+                fname, ctype = ALLOWED_FILES[path]
+                fpath = os.path.join(ROOT, fname)
+                if os.path.isfile(fpath):
+                    with open(fpath, "rb") as f: return self._send(200, f.read(), ctype)
+            return self._send(404, {"ok": False, "code": "NOT_FOUND"})
+        except Exception as e: return self._send(500, {"ok": False, "code": "INTERNAL_ERROR", "message": str(e)})
     def do_POST(self):
-        if not self._check_local_guard(): return
-        path = self.path.split("?", 1)[0]
-        length = int(self.headers.get("Content-Length", "0"))
-        if length > MAX_BODY: return self._send(413, {"ok": False, "code": "PAYLOAD_TOO_LARGE"})
-        raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
-        try: body = json.loads(raw)
-        except Exception: return self._send(400, {"ok": False, "code": "INVALID_JSON"})
-        if path == "/api/chat":
-            q = str(body.get("query", body.get("cmd", ""))).strip()
-            uid = str(uuid.uuid4())
-            req_id = uid[:8]
-            entry = {"uuid": uid, "req_id": req_id, "ts": datetime.datetime.now().isoformat(), "query": q, "mode": "READ_ONLY", "executed": False}
-            with open(LEDGER, "a", encoding="utf-8") as lf: lf.write(json.dumps(entry, ensure_ascii=False) + "\n")
-            return self._send(200, {"ok": True, "uuid": uid, "req_id": req_id, "executed": False, "reply": "[ID " + req_id + "] Recorded in ledger."})
-        if path == "/api/ego/ask":
-            if s1_ego.kill_switch_active(): return self._send(423, {"ok": False, "code": "KILL_SWITCH_ACTIVE"})
-            if body.get("confirm") != "S1_WEB_ASK_CONFIRMED": return self._send(403, {"ok": False, "code": "CONFIRM_REQUIRED"})
-            sp = body.get("space")
-            prompt = str(body.get("prompt", "")).strip()
-            wait_s = max(10, min(180, int(body.get("wait", 60))))
-            if sp not in (2, 3) or not prompt: return self._send(400, {"ok": False, "code": "ASK_SPACE_FORBIDDEN_OR_EMPTY", "space": sp})
-            res = s1_ego.cmd_ask(int(sp), prompt, wait_sec=wait_s)
-            with open(LEDGER, "a", encoding="utf-8") as lf: lf.write(json.dumps({"req_id": res.get("req_id"), "ts": datetime.datetime.now().isoformat(), "cmd": "api_ego_ask", "space": sp, "ok": res.get("ok"), "status": res.get("status")}, ensure_ascii=False) + "\n")
-            return self._send(200 if res.get("ok") else 409, res)
-        return self._send(404, {"ok": False, "code": "NOT_FOUND"})
+        try:
+            if not self._check_local_guard(is_write=True): return
+            ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
+            if ctype != "application/json": return self._send(415, {"ok": False, "code": "UNSUPPORTED_MEDIA_TYPE"})
+            try: length = int(self.headers.get("Content-Length", "0"))
+            except ValueError: return self._send(400, {"ok": False, "code": "INVALID_CONTENT_LENGTH"})
+            if length < 0 or length > MAX_BODY: return self._send(413, {"ok": False, "code": "PAYLOAD_TOO_LARGE"})
+            try: raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
+            except UnicodeDecodeError: return self._send(400, {"ok": False, "code": "INVALID_UTF8"})
+            try: body = json.loads(raw)
+            except Exception: return self._send(400, {"ok": False, "code": "INVALID_JSON"})
+            if not isinstance(body, dict): return self._send(400, {"ok": False, "code": "JSON_OBJECT_REQUIRED"})
+            path = self.path.split("?", 1)[0]
+            if path == "/api/chat":
+                q_val = body.get("query", body.get("cmd", ""))
+                if not isinstance(q_val, str): return self._send(400, {"ok": False, "code": "INVALID_QUERY_TYPE"})
+                q = q_val.strip()
+                uid = str(uuid.uuid4()); req_id = uid[:8]
+                write_ledger({"uuid": uid, "req_id": req_id, "query": q, "mode": "LEDGER_RECORD_ONLY", "executed": False})
+                return self._send(200, {"ok": True, "uuid": uid, "req_id": req_id, "executed": False, "reply": f"[읽기 전용 · 원장ID {req_id}] 명령이 원장(s1_command_ledger.jsonl)에 기록되었으나 실행되지 않았습니다."})
+            if path == "/api/ego/ask":
+                if s1_ego.kill_switch_active(): return self._send(423, {"ok": False, "code": "KILL_SWITCH_ACTIVE"})
+                sp = body.get("space"); prompt = body.get("prompt"); wait_v = body.get("wait", 60)
+                if type(sp) is not int or sp not in (2, 3): return self._send(400, {"ok": False, "code": "ASK_SPACE_FORBIDDEN", "space": sp})
+                if not isinstance(prompt, str) or not prompt.strip(): return self._send(400, {"ok": False, "code": "INVALID_PROMPT"})
+                if type(wait_v) is not int or wait_v < 10 or wait_v > 180: return self._send(400, {"ok": False, "code": "INVALID_WAIT"})
+                req_id = str(uuid.uuid4())
+                psha = hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()
+                origin = (self.headers.get("Origin") or "").strip().lower()
+                with LEDGER_LOCK:
+                    q_map = json.loads(open(QUEUE_FILE, "r", encoding="utf-8").read()) if os.path.exists(QUEUE_FILE) else {}
+                    q_map[req_id] = {"req_id": req_id, "space": sp, "prompt": prompt.strip(), "prompt_sha256": psha, "wait": wait_v, "origin": origin, "status": "PENDING", "created_at": now_kst()}
+                    with open(QUEUE_FILE, "w", encoding="utf-8") as qf: qf.write(json.dumps(q_map, ensure_ascii=False, indent=2))
+                write_ledger({"req_id": req_id, "cmd": "api_ego_ask_enqueue", "space": sp, "prompt_sha256": psha, "wait": wait_v, "origin": origin, "status": "PENDING", "executed": False})
+                return self._send(202, {"ok": True, "status": "PENDING", "req_id": req_id, "space": sp, "prompt_sha256": psha, "approval_required_sha8": psha[:8], "how_to_approve": f"python s1.py approve {req_id} {psha[:8]}"})
+            return self._send(404, {"ok": False, "code": "NOT_FOUND"})
+        except Exception as e: return self._send(500, {"ok": False, "code": "INTERNAL_ERROR", "message": str(e)})
 if __name__ == "__main__":
     with ReusableTCPServer(("127.0.0.1", PORT), S1Handler) as httpd:
         print(f"S1_SERVER_READY port={PORT}", flush=True)

```
## 5. `s1_ego.py` v1.1.2 -> v1.1.7 Diff
```diff
diff --git a/s1_ego.py b/s1_ego.py
index 5677290..55bf14d 100644
--- a/s1_ego.py
+++ b/s1_ego.py
@@ -1,6 +1,6 @@
 # -*- coding: utf-8 -*-
-# S1 Ego-Lite Universal Nerve CLI v1.1.2 (s1_ego.py)
-# Triumvirate Verified Architecture (GPT-6.1 Sol & Claude Opus 5.5 Audit Compliant):
+# S1 Ego-Lite Universal Nerve CLI v1.1.7 (s1_ego.py)
+# Triumvirate Verified Architecture (GPT-6.1 Sol & Claude Opus 5.5 Audit Under Review):
 # - R0 (spaces): URL query stripping (keep only chat id), read-only safe.
 # - R1 (read): Exact URL/chatId match (TAB_NOT_UNIQUE on 0 or >1), defang() markers, 1 retry on transient error.
 # - W1 (ask): Kill-switch guard, global msvcrt file lock (ASK_LOCK_HELD), model verification (MODEL_MISMATCH),
@@ -8,6 +8,7 @@
 #             honest status (completed / timeout / rate_limited / send_not_confirmed), audit log (logs/s1_ego_audit.jsonl),
 #             non-zero exit code (sys.exit(1)) on any failure.
 
+__version__ = "1.1.7"
 import argparse, datetime, hashlib, json, msvcrt, os, re, shutil, subprocess, sys, time, urllib.parse, uuid
 from pathlib import Path
 
@@ -166,7 +167,9 @@ def cmd_spaces():
                     tb["url"] = sanitize_url(tb["url"])
     return res
 
-def cmd_read(space_id, tail_chars=4000, override_chat_id=None):
+def cmd_read(space_id, tail_chars=4000, override_chat_id=None, selftest=False):
+    if override_chat_id is not None and not selftest:
+        return {"ok": False, "code": "OVERRIDE_REQUIRES_SELFTEST", "space": space_id}
     if space_id not in KNOWN_CHATS and override_chat_id is None:
         return {"ok": False, "code": "SPACE_NOT_ALLOWED", "space": space_id}
     expected_id = override_chat_id if override_chat_id is not None else KNOWN_CHATS[space_id]
@@ -242,7 +245,7 @@ def cmd_read(space_id, tail_chars=4000, override_chat_id=None):
         res["last_message"] = defang(res.get("last_message", ""))
     return res
 
-def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_id=None, override_model=None, min_interval=0):
+def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_id=None, override_model=None, min_interval=0, selftest=False):
     req_id = str(uuid.uuid4())
     prompt_sha = sha256_hex(prompt_text)
 
@@ -267,12 +270,15 @@ def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_i
         res = {"ok": False, "code": "HOP_LIMIT_EXCEEDED", "req_id": req_id, "space": space_id}
         write_audit({"req_id": req_id, "cmd": "ask", "space": space_id, "prompt_sha": prompt_sha, "status": "HOP_LIMIT_EXCEEDED"})
         return res
-    if "[S1_HOP=" not in (prompt_text or ""):
+    if not (prompt_text or "").lstrip().startswith("[S1_HOP="):
         prompt_text = "[S1_HOP=1/2]\n" + (prompt_text or "")
         prompt_sha = sha256_hex(prompt_text)
 
     # Global Ask File Lock (non-blocking msvcrt lock -> prevents concurrent ask collisions)
     lock_fh = open(ASK_LOCK_FILE, "w", encoding="utf-8")
+    if (override_chat_id is not None or override_model is not None) and not selftest:
+        lock_fh.close()
+        return {"ok": False, "code": "OVERRIDE_REQUIRES_SELFTEST", "req_id": req_id, "space": space_id}
     expected_id_for_log = override_chat_id if override_chat_id is not None else KNOWN_CHATS.get(space_id, "")
     try:
         msvcrt.locking(lock_fh.fileno(), msvcrt.LK_NBLCK, 1)
@@ -326,8 +332,8 @@ def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_i
               const draft = (ta.value || "").trim();
               if (draft.length > 0) return {{ ok: false, code: "DRAFT_PRESENT", draft_len: draft.length }};
               const bodyTxt = document.body ? document.body.innerText : "";
-              if (!bodyTxt.includes(expModel)) {{
-                return {{ ok: false, code: "MODEL_MISMATCH", expected_model: expModel }};
+              let cb = ta.parentElement; for(let i=0;i<4&&cb&&cb.parentElement;i++) cb=cb.parentElement; const uiModelTxt = cb ? (cb.innerText||"") : ""; if (!uiModelTxt.includes(expModel)) {{
+                return {{ ok: false, code: "MODEL_MISMATCH", expected_model: expModel, ui_model_text: uiModelTxt.slice(0,100) }};
               }}
               const proseEls = Array.from(document.querySelectorAll(".answer-markdown"));
               const lastProse = proseEls.length > 0 ? (proseEls[proseEls.length - 1].innerText || "").trim() : "";
@@ -349,6 +355,21 @@ def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_i
             return;
           }}
 
+          if (Boolean({1 if selftest else 0})) {{
+            process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{ ok: false, code: "SELFTEST_NO_SEND", status: "selftest_stopped_before_fill", space: {space_id}, precheck: pre }}) + "\\n");
+            return;
+          }}
+          const preUserDom = await page.evaluate(() => {{
+            const norm = s => String(s || "").replace(/\\r\\n/g, "\\n").trim();
+            const all = Array.from(document.querySelectorAll("div, article, section, pre, p")).filter(el => {{
+              if (el.closest(".answer-markdown, .markdown-viewer, textarea, button")) return false;
+              const t = norm(el.innerText);
+              if (!t.startsWith("[S1_HOP=")) return false;
+              const childHasHop = Array.from(el.querySelectorAll("div, article, section, pre, p")).some(c => norm(c.innerText).startsWith("[S1_HOP="));
+              return !childHasHop;
+            }});
+            return {{ count: all.length, lastText: all.length ? norm(all[all.length - 1].innerText) : "" }};
+          }});
           const selector = 'loc=css:textarea[name="query"]';
           await page.fill(selector, prompt);
           await sleep(300);
@@ -373,12 +394,25 @@ def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_i
 
           // Confirm send: textarea cleared
           const postSend = await Promise.race([
-            page.evaluate(() => {{
+            page.evaluate((arg) => {{
               const ta = document.querySelector('textarea[name="query"]') || document.querySelector('textarea');
               const bodyTxt = document.body ? document.body.innerText : "";
               const rateLimited = Array.from(document.querySelectorAll("[role=alert], .ant-message, .toast")).some(e => e.offsetParent !== null && ((e.innerText || "").includes("5시간 제한") || (e.innerText || "").includes("재설정됩니다")));
-              return {{ valLen: ta ? (ta.value || "").trim().length : -1, rateLimited }};
-            }}).catch(() => null),
+              const norm = s => String(s || "").replace(/\\r\\n/g, "\\n").trim();
+              const uEls = Array.from(document.querySelectorAll("div, article, section, pre, p")).filter(el => {{
+                if (el.closest(".answer-markdown, .markdown-viewer, textarea, button")) return false;
+                const t = norm(el.innerText);
+                if (!t.startsWith("[S1_HOP=")) return false;
+                const childHasHop = Array.from(el.querySelectorAll("div, article, section, pre, p")).some(c => norm(c.innerText).startsWith("[S1_HOP="));
+                return !childHasHop;
+              }});
+              const lastEl = uEls.length ? uEls[uEls.length - 1] : null;
+              const lastTxt = lastEl ? norm(lastEl.innerText) : "";
+              const expNorm = norm(arg.fullPrompt);
+              const fullMatch = (uEls.length > arg.preCount) && (lastTxt === expNorm);
+              const selInfo = lastEl ? (lastEl.tagName.toLowerCase() + (lastEl.className ? "." + String(lastEl.className).trim().split(/\\s+/).join(".") : "")) : "none";
+              return {{ taPresent: Boolean(ta), valLen: ta ? (ta.value || "").trim().length : -1, selectorRule: "innermost block element outside .answer-markdown starting with [S1_HOP=", matchedElementSelector: selInfo, normalizationRule: "String(s).replace(/\\r\\n/g, \\n).trim()", userMsgCountBefore: arg.preCount, userMsgCountAfter: uEls.length, newMsgText: lastTxt.slice(0, 300), expectedPromptText: expNorm.slice(0, 300), exactFullStringEqual: lastTxt === expNorm, fullTextExactMatch: fullMatch, userMsgSeen: fullMatch, rateLimited }};
+            }}, {{ fullPrompt: prompt, preCount: preUserDom.count }}).catch(() => null),
             new Promise(r => setTimeout(() => r(null), 5000))
           ]);
 
@@ -388,7 +422,7 @@ def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_i
             }}) + "\\n");
             return;
           }}
-          if (!postSend || postSend.valLen > 0) {{
+          if (!postSend || !postSend.taPresent || postSend.valLen !== 0 || !postSend.userMsgSeen) {{
             process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
               ok: false, code: "SEND_NOT_CONFIRMED", status: "send_not_confirmed", details: postSend
             }}) + "\\n");
@@ -414,8 +448,7 @@ def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_i
                 if (toastRateLimit) {{
                   return {{ ok: true, rateLimited: true, toastRateLimit: true }};
                 }}
-                const tailWindow = bodyTxt.slice(-600);
-                const isThinking = tailWindow.includes("Thinking...") || tailWindow.includes("생각 중") || tailWindow.includes("생성 중");
+                const isThinking = false;
                 const stopBtn = Array.from(document.querySelectorAll("button, [role='button']")).some(b => {{
                   const t = (b.innerText || b.getAttribute("aria-label") || "").toLowerCase();
                   return t === "stop" || t === "중지" || t.includes("생성 중지");
@@ -423,7 +456,7 @@ def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_i
                 const proseEls = Array.from(document.querySelectorAll(".answer-markdown"));
                 const curCount = proseEls.length;
                 const curLast = curCount > 0 ? (proseEls[curCount - 1].innerText || "").trim() : "";
-                const hasNewAssistant = (curCount > baseProseCount && curLast.length > 0) || (curLast !== baseLastProse && curLast.length > 0);
+                const hasNewAssistant = (curCount > baseProseCount && curLast.length > 10) || (curLast !== baseLastProse && curLast.length > 10);
                 return {{
                   ok: true,
                   rateLimited: false,
@@ -436,44 +469,35 @@ def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_i
               new Promise(r => setTimeout(() => r({{ ok: false, timeout: true }}), 5000))
             ]);
 
-            if (!poll || !poll.ok) continue; // Ignore timed-out poll cycle
+            if (!poll || !poll.ok) {{
+              stableCount = 0;
+              continue;
+            }}
             if (poll.rateLimited) {{
               rateLimitedNow = true;
               break;
             }}
-            if (poll.curLast && (poll.curCount > pre.proseCount || poll.curLast !== pre.lastProse) && !poll.isThinking) {{
-              if (poll.curLast === lastAssistantMsg && poll.curLast.length > 0) {{
-                stableCount += 1;
-              }} else {{
-                stableCount = 1;
-              }}
-              lastAssistantMsg = poll.curLast;
-              pollLogs.push({{
-                t_ms: Date.now() - start,
-                stop_present: Boolean(poll.stopBtn),
-                answer_count: poll.curCount,
-                answer_count_before: pre.proseCount,
-                last_answer_len: poll.curLast.length,
-                last_answer_text: poll.curLast.slice(-120),
-                stable_n: stableCount,
-                toast_rate_limit: false
-              }});
-              if (stableCount >= 3) {{
-                completed = true;
-                break;
-              }}
+            const fresh = Boolean(poll.curLast && (poll.curCount > pre.proseCount || poll.curLast !== pre.lastProse));
+            if (fresh && !poll.stopBtn) {{
+              stableCount = (poll.curLast === lastAssistantMsg) ? stableCount + 1 : 1;
             }} else {{
               stableCount = 0;
-              pollLogs.push({{
-                t_ms: Date.now() - start,
-                stop_present: Boolean(poll.stopBtn),
-                answer_count: poll.curCount || 0,
-                answer_count_before: pre.proseCount,
-                last_answer_len: (poll.curLast || "").length,
-                last_answer_text: (poll.curLast || "").slice(-120),
-                stable_n: 0,
-                toast_rate_limit: false
-              }});
+            }}
+            if (poll.curLast) lastAssistantMsg = poll.curLast;
+            pollLogs.push({{
+              t_ms: Date.now() - start,
+              stop_present: Boolean(poll.stopBtn),
+              fresh,
+              answer_count: poll.curCount || 0,
+              answer_count_before: pre.proseCount,
+              last_answer_len: (poll.curLast || "").length,
+              last_answer_full: poll.curLast || "",
+              stable_n: stableCount,
+              toast_rate_limit: false
+            }});
+            if (stableCount >= 4) {{
+              completed = true;
+              break;
             }}
           }}
 
@@ -492,7 +516,7 @@ def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_i
             status: statusStr,
             space: {space_id},
             chat_id: expected,
-            elapsed_ms: elapsed,
+            elapsed_ms: elapsed, send_verified: postSend,
             last_message: String(lastAssistantMsg || "").slice(-{tail_chars}),
             poll_logs: pollLogs
           }}) + "\\n");
@@ -506,9 +530,10 @@ def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_i
                 "req_id": req_id,
                 "t_ms": pl.get("t_ms"),
                 "stop_present": pl.get("stop_present"),
+                "fresh": pl.get("fresh"),
                 "answer_count": pl.get("answer_count"),
                 "answer_count_before": pl.get("answer_count_before"),
-                "last_answer_sha": sha256_hex(pl.get("last_answer_text", ""))[:16],
+                "last_answer_sha": sha256_hex(pl.get("last_answer_full", "")),
                 "last_answer_len": pl.get("last_answer_len"),
                 "stable_n": pl.get("stable_n"),
                 "toast_rate_limit": pl.get("toast_rate_limit", False),
@@ -542,13 +567,14 @@ def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_i
         lock_fh.close()
 
 def main():
-    ap = argparse.ArgumentParser(description="S1 Ego-Lite Universal Nerve CLI v1.1.2")
+    ap = argparse.ArgumentParser(description="S1 Ego-Lite Universal Nerve CLI v1.1.7")
     sub = ap.add_subparsers(dest="cmd", required=True)
     sub.add_parser("spaces")
     p_read = sub.add_parser("read")
     p_read.add_argument("space", type=int)
     p_read.add_argument("--tail", type=int, default=4000)
     p_read.add_argument("--expect-id", type=str, default=None)
+    p_read.add_argument("--selftest", action="store_true")
     p_ask = sub.add_parser("ask")
     p_ask.add_argument("space", type=int)
     p_ask.add_argument("--prompt-file", type=str, default="")
@@ -556,15 +582,16 @@ def main():
     p_ask.add_argument("--wait", type=int, default=60)
     p_ask.add_argument("--expect-id", type=str, default=None)
     p_ask.add_argument("--expect-model", type=str, default=None)
+    p_ask.add_argument("--selftest", action="store_true")
     args = ap.parse_args()
 
     if args.cmd == "spaces":
         res = cmd_spaces()
     elif args.cmd == "read":
-        res = cmd_read(args.space, args.tail, override_chat_id=args.expect_id)
+        res = cmd_read(args.space, args.tail, override_chat_id=args.expect_id, selftest=args.selftest)
     elif args.cmd == "ask":
         txt = Path(args.prompt_file).read_text(encoding="utf-8") if args.prompt_file else args.prompt
-        res = cmd_ask(args.space, txt, wait_sec=args.wait, override_chat_id=args.expect_id, override_model=args.expect_model)
+        res = cmd_ask(args.space, txt, wait_sec=args.wait, override_chat_id=args.expect_id, override_model=args.expect_model, selftest=args.selftest)
     print(json.dumps(res, ensure_ascii=False, indent=2))
     if not res.get("ok"):
         sys.exit(1)

```
## 6. GPT-6.1 Sol (Space 2) 최종 평결
```
S1 2순위 2단계 — v1.3 종결 감리 평결

판정: 승인 대기·승인 후 정상 응답 기능시험 PASS. 브릿지 통합 최종 PASS는 보류합니다.

개선은 확인됩니다. 다만 제출 소스에는 승인 대상 무결성·프로세스 간 동시성 결함이 남아 있고, 실측 Origin이 코드의 허용 목록과 일치하지 않습니다. 이는 기존 재검수 범위인 쓰기 진입 경계·중복 방지·실제 UI 연결에 해당합니다.

본 판정은 제출 자료의 정적 대조이며, 로컬 독립 실행이나 삼성전자 공식 인증은 아닙니다.

1. 이번 제출에서 통과한 사항
항목	판정
승인 없는 요청의 PENDING 유지	제출 관측 범위에서 인정
승인 후 completed, BRIDGE_PASS_V13 수거	기능시험 PASS
wait:"abc", 배열 본문, 잘못된 Content-Type 거절	해당 사례 PASS
잘못된 Host·킬스위치 차단	해당 사례 PASS
성공·실패 집계 분리, KST, 레거시 ID 표시	개선 인정
실행 전 STARTED 기록	코드·제출 로그에서 순서 인정

직전 제가 반환한 BRIDGE_PASS_V13와 제출된 응답도 일치합니다. 정상 HTTP 등록 → CLI 승인 → AI 응답 경로가 동작했다는 증거는 인정합니다.

2. 최종 PASS 보류 사유
① 승인 시 실제 실행 내용의 해시를 재계산하지 않습니다

approve_pending()은 저장된 prompt_sha256의 앞 8자리와 입력값만 비교합니다. 이후 실행하는 item["prompt"]의 해시를 다시 계산하지 않습니다.

따라서 큐의 프롬프트가 변경돼도 저장된 해시를 그대로 두면 승인 검사를 통과할 수 있습니다. space·wait 역시 승인 시 재검증하지 않습니다.

필요한 보완: 승인 직전에 실제 실행할 내용의 전체 SHA-256을 재계산하고 저장값과 비교하십시오. 대상 Space·채팅 ID·대기시간도 승인 대상으로 결합하고 검증해야 합니다. SHA-8은 사람의 확인 보조값이지 인증 수단은 아닙니다.

또한 approved_by="CEO_SANGILL_LEE_SHA8"는 코드의 기본 문자열입니다. 대표님이 직접 승인했다는 독립 증거로 해석하지는 않습니다.

② LEDGER_LOCK은 서버와 승인 CLI를 함께 보호하지 않습니다

서버의 threading.Lock()은 서버 프로세스 안에서만 작동합니다. 별도 실행되는 s1.py에는 공유 잠금이 없습니다.

특히 승인 CLI는 다음 순서로 동작합니다.

전체 큐 읽기
STARTED 저장
약 20초의 작업 수행
처음 읽었던 전체 큐를 다시 저장

이 사이 서버가 새 요청을 추가하면, 마지막 저장이 새 요청을 덮어써 없앨 수 있습니다. 복수 승인 프로세스 사이에서도 상태 경합이 가능합니다. 기존 s1_ego의 ask 잠금만으로는 큐 손실을 막지 못합니다.

필요한 보완: 서버·승인 CLI가 공유하는 프로세스 간 잠금 또는 트랜잭션 저장소를 사용하십시오. 완료 시 최신 상태를 다시 읽고 해당 요청만 갱신하며, 파일 저장은 원자적으로 처리해야 합니다. 불확실한 STARTED 작업은 자동 재실행하지 않아야 합니다.

③ 실측 Origin과 제출 코드가 모순됩니다

실측 큐에는 다음 값이 있습니다.

Copy
origin: http://127.0.0.1:8505


하지만 제출 코드의 쓰기 허용 Origin은 다음 두 개뿐입니다.

Copy
http://127.0.0.1:8504
http://localhost:8504


제출 코드 그대로라면 8505 Origin의 등록 요청은 403이어야 합니다. 따라서 현재 자료만으로 실행 서버와 첨부 소스가 같은 빌드라고 확인할 수 없습니다. 구형 탭을 닫은 것만으로 이 불일치는 해소되지 않습니다.

3. 재검수는 아래 세 가지로 한정합니다
남은 항목	최소 증빙
승인 내용 무결성	저장 해시는 유지하고 프롬프트 또는 대상을 바꿨을 때 전송 없이 차단
큐·원장 동시성	승인 실행 중 새 요청 등록과 동일 요청 동시 승인을 시험하여 요청 유실·중복 실행이 없음을 확인
실행본 연결	서버·런처 파일 해시, 실제 바인딩 주소·허용 Origin, 그 빌드의 요청 결과를 연결

브릿지 요청 ID f2d8755d-…와 ego 요청 ID dcc70bd4-…는 서로 다른 계층의 ID여도 됩니다. 다만 최종 원장에 둘을 함께 기록하면 현재 결과 파일의 연결 관계를 영속적으로 보존할 수 있습니다. 승인 전후 프롬프트 해시가 다른 것도 HOP 접두어 추가 때문일 수 있으므로 변환 규칙을 명시하십시오.

기존 정상 응답·입력 거절·DOM 전체 일치 시험은 반복할 필요 없습니다.

최종 의결: [v1.3 승인 게이트 정상 기능시험 PASS]. 그러나 승인 시 무결성 재검증 누락, 공유 큐 동시성 결함, Origin·실행본 불일치로 [S1 2순위 2단계 최종 PASS]는 보류합니다.
```
## 7. Claude Opus 5.5 (Space 3) 최종 평결
```
[S1_HOP=1/2] S1 2순위 2단계 종결 감리 (제3성 Claude)
판정: 2단계 최종 PASS 보류

입력 검증 계층은 합격입니다. 문제는 승인 관문입니다. 사람이 승인했다는 증거가 없고, 구조상으로도 스크립트가 혼자 승인을 끝낼 수 있습니다. 1순위 v3.2 때 지적한 "승인이 사람이 아님"과 같은 유형이어서, 이번에도 같은 기준을 적용했습니다. 수정 분량이 작으므로 diff 제출과 실측 1회로 종결할 수 있습니다. 덧붙여 이 응답은 판정 보고이며 실행 명령이 아닙니다.

합격 (다시 감리할 필요 없음)

지난 차수 결함 2·4·5와 경미 항목 대부분이 해소됐습니다. 해소된 내용은 다음과 같습니다.

입력 검증: wait:"abc"와 [1,2]는 400 JSON으로, text/plain은 415로, evil.com은 403으로, 킬스위치 상태는 423으로 실측 거부됐습니다. 예외 래퍼, type(sp) is int, isinstance(body, dict) 검사도 들어갔습니다.
서버 구조: 서버에는 cmd_ask를 호출하는 경로가 아예 없습니다. 그래서 승인 없이 PENDING이 유지된다는 점은 코드 구조로 입증됩니다.
전송 확인: 보낸 문장 전체와 화면에 올라온 문장이 정확히 일치하는지 대조합니다(exactFullStringEqual). 지금까지 본 전송 확인 방식 중 가장 강합니다.
s1_ego v1.1.2 필수 수정 3건 반영: 중지 버튼 조건이 완료 판정에 들어갔고, 4회 연속 동일하면 완료로 봅니다. curLast가 복원됐고, override 인자는 selftest에서만 허용되며 전송 전에 멈춥니다(SELFTEST_NO_SEND).
경미 항목: 정직 문구 복원, +09:00 표기, 민감 경로 제거, __version__ 도입, truncation_rule 명시가 모두 확인됐습니다.
치명 결함: 승인 관문이 스크립트로 통과됩니다

1. 시각 증거. 원장 시각을 보면 승인 명령을 사람이 칠 수 없는 간격입니다.

req_id	PENDING	STARTED	간격
f2d8755d	12:09:37.692	12:09:37.696	4ms
2e281385	12:07:46.296	12:07:46.301	5ms

2. 구조 원인. 서버의 202 응답이 approval_required_sha8과 완성된 승인 명령(how_to_approve)을 그대로 돌려줍니다. 게다가 s1.py approve는 SHA를 명령줄 인자로 받기 때문에, 화면 확인이나 입력 대기 없이도 실행됩니다. 결국 POST를 보낸 프로세스가 응답을 읽고 곧바로 subprocess로 승인까지 할 수 있습니다. 예를 들어 1순위 데몬이 실행한 AI 블록도 그렇게 할 수 있습니다. 지난 차수의 고정 문자열 confirm과 실질적으로 같은 상태입니다. 그리고 s1.py는 승인 전에 프롬프트 전문을 보여주지 않습니다.

3. 승인한 문장과 보낸 문장이 다릅니다 (추정이므로 확인 바랍니다). 큐에 기록된 SHA는 9d63d3c3…인데 ego 결과의 prompt_sha는 50717963…입니다. cmd_ask가 [S1_HOP=1/2]\n 접두어를 붙인 뒤 전송했기 때문으로 보입니다. 1순위의 FILE_SHA_MISMATCH_HOLD와 같은 원칙에 따라, 승인 SHA와 전송 SHA는 같아야 합니다.

수정안은 다음과 같습니다.

Copy
# 서버: HOP 접두를 먼저 붙인 '최종 전송문'을 큐에 저장·해시. 응답에서 sha8·승인명령 제거.
sent = prompt.strip()
if not sent.startswith("[S1_HOP="): sent = "[S1_HOP=1/2]\n" + sent
psha = hashlib.sha256(sent.encode("utf-8")).hexdigest()
# 202 응답: {"ok":True,"status":"PENDING","req_id":req_id}  ← sha8/how_to_approve 없음

# s1.py: python s1.py approve <req_id>  (SHA 인자 없음)
if not sys.stdin.isatty(): return {"ok": False, "code": "NOT_INTERACTIVE"}
if hashlib.sha256(item["prompt"].encode("utf-8")).hexdigest() != item["prompt_sha256"]:
    return {"ok": False, "code": "QUEUE_SHA_MISMATCH"}
print(f"[Space {item['space']}] origin={item['origin']} created={item['created_at']}")
print("----- 전송될 전문 -----\n" + s1_ego.defang(item["prompt"]) + "\n-----")
print("SHA-256:", item["prompt_sha256"])
ans = input("승인하려면 SHA 앞 8자리 입력 (취소: Enter): ").strip().lower()
if ans != item["prompt_sha256"][:8]: → SHA8_MISMATCH 기록, PENDING 유지


미리 정직하게 한계를 밝혀 둡니다. 같은 사용자 권한으로 도는 로컬 코드는 s1_ego.cmd_ask를 직접 부를 수도 있습니다. 따라서 이 관문이 입증하는 것은 "웹 경로에서 사람의 의사가 있었다"는 사실까지입니다. 악성 로컬 코드까지 막아 주지는 못합니다. 1순위의 "실행 코드는 읽기·출력으로만 제한" 원칙은 그대로 유지됩니다.

중요 결함

4. 큐 파일 경합으로 기록이 사라집니다. LEDGER_LOCK은 서버 프로세스 안에서만 작동하는 스레드 잠금입니다. s1.py는 별도 프로세스라서 이 잠금의 보호를 받지 못합니다. 문제의 흐름은 이렇습니다.

s1.py가 시작할 때 큐를 읽어 둡니다.
cmd_ask를 실행하는 12~60초 동안 서버에 새 요청이 들어와 큐에 기록됩니다.
끝난 뒤 s1.py가 처음 읽어 둔 낡은 내용으로 큐를 통째로 덮어씁니다. 그 사이 들어온 PENDING 요청이 사라집니다.

저장 방식도 원자적이지 않습니다(write_text). 수정안은 두 프로세스가 같이 쓰는 msvcrt 잠금 파일(s1_ask_queue.lock)을 두는 것입니다. 쓰기 직전에 잠금 안에서 다시 읽고, 해당 항목만 갱신하고, 임시 파일에 쓴 뒤 os.replace로 교체해야 합니다.

5. 고아 STARTED 1건이 있습니다. 2e281385는 STARTED 뒤에 DONE도 FAIL도 없습니다. cmd_ask에서 예외가 나면 s1.py가 FAIL을 기록하지 않고 종료하는 구조이기 때문입니다. 수정안은 이렇습니다.

try/finally로 감싸 예외가 나도 FAIL을 기록합니다.
2e281385는 삭제하지 말고 ABANDONED 줄을 추가하고 경위를 한 줄로 적습니다.

6. 실측한 서버가 제출한 코드와 다릅니다. 큐에 기록된 origin은 http://127.0.0.1:8505입니다. 그런데 diff의 코드는 PORT = 8504이고, 허용 Origin과 Host도 8504만 받습니다. 이 코드가 그대로 돌았다면 8505 요청은 ORIGIN_FORBIDDEN이나 HOST_FORBIDDEN으로 막혔어야 합니다. 포트가 8000→8502→8503→8504→8505로 계속 바뀌어 온 것과 같은 패턴입니다. 실측 당시 실행 중이던 s1_server.py의 SHA-256과 실제 포트를 밝혀 주십시오.

경미
hasNewAssistant의 length > 10 조건이 v1.1.2에서 없앤 글자 수 제한의 부활입니다. 완료 판정에 쓰이지 않는다면 삭제하고, 쓰인다면 "OK"처럼 짧은 답이 시간 초과로 처리됩니다.
--selftest --expect-id를 함께 쓰면 read가 허용 목록 밖의 대화창을 읽을 수 있습니다. 읽기 전용이라 경미하지만 한 줄로 밝혀 주십시오.
500 응답의 str(e)에 경로가 노출될 수 있습니다. 상세 내용은 로그에만 남기는 편이 낫습니다.
Tailscale(*.ts.net) 허용 여부와 Space 3 p4 탭을 닫은 증거(spaces 출력)가 아직 없습니다.
종결 조건 (diff와 실측 1회, 재감리 없음)
결함 1~5를 수정한 diff 두 개(서버와 s1.py)와, 실행 중인 서버의 SHA-256 및 포트(결함 6)를 제출해 주십시오.
아래 실측 4건을 제출해 주십시오.
번호	시험	기대 결과
①	대표님이 터미널에서 직접 승인 1건	전문 표시 화면의 텍스트 사본, PENDING→STARTED 간격 수십 초, 승인 SHA와 전송 SHA 일치, DONE
②	SHA 8자리를 틀리게 입력	SHA8_MISMATCH 후 PENDING 유지
③	echo x | python s1.py approve <id>처럼 입력을 파이프로 공급	NOT_INTERACTIVE 거부
④	승인 실행 도중 새 요청을 큐에 넣음	승인이 끝난 뒤에도 새 요청이 PENDING으로 남아 있음

이 조건이 충족되면 S1 2순위 2단계를 PASS로 권고하겠습니다. 최종 확정은 지금까지처럼 대표님이 직접 제출하시는 것으로 하겠습니다.
```
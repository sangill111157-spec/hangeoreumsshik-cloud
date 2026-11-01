#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# S1 Local Bridge Server v1.2 (s1_server.py - Integrated with s1_ego.py v1.1.7)
import os, sys, json, uuid, datetime, urllib.parse, http.server, socketserver
import s1_ego
PORT = 8504
MAX_BODY = 65536
ROOT = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(ROOT, "s1_command_ledger.jsonl")
ALLOWED_HOSTS = {"127.0.0.1:8504", "localhost:8504", "127.0.0.1", "localhost"}
ALLOWED_ORIGINS = {None, "", "http://127.0.0.1:8504", "http://localhost:8504"}
ALLOWED_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/rgon_alpha_chat.html": ("rgon_alpha_chat.html", "text/html; charset=utf-8"),
    "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json; charset=utf-8"),
    "/sw.js": ("sw.js", "application/javascript; charset=utf-8"),
    "/icon-192.png": ("icon-192.png", "image/png"),
    "/icon-512.png": ("icon-512.png", "image/png"),
    "/apple-touch-icon.png": ("apple-touch-icon.png", "image/png"),
    "/S1_FULL_PROOF.json": ("S1_FULL_PROOF.json", "application/json; charset=utf-8"),
}
class ReusableTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
class S1Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass
    def _check_local_guard(self):
        host = (self.headers.get("Host") or "").strip().lower()
        origin = (self.headers.get("Origin") or "").strip().lower()
        if host not in ALLOWED_HOSTS:
            self._send(403, {"ok": False, "code": "HOST_FORBIDDEN", "host": host})
            return False
        if origin not in ALLOWED_ORIGINS:
            self._send(403, {"ok": False, "code": "ORIGIN_FORBIDDEN", "origin": origin})
            return False
        return True
    def _send(self, code, payload, ctype="application/json; charset=utf-8"):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8") if isinstance(payload, (dict, list)) else payload
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def do_GET(self):
        if not self._check_local_guard(): return
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        if path == "/api/status":
            kill_on = s1_ego.kill_switch_active()
            led_file = os.path.join(ROOT, "executed_ids.json")
            exec_ids, last_exec = [], None
            if os.path.exists(led_file):
                try:
                    with open(led_file, "r", encoding="utf-8") as f:
                        ex_map = json.load(f).get("executed", {})
                        exec_ids = list(ex_map.keys())
                        if exec_ids: last_exec = ex_map[exec_ids[-1]]
                except Exception: pass
            return self._send(200, {"ok": True, "version": "1.2", "ego_cli_version": "1.1.7", "server_time": datetime.datetime.now().isoformat(), "kill_switch": kill_on, "mode": "BRIDGE_ACTIVE", "executed_count": len(exec_ids), "executed_ids": exec_ids, "last_executed": last_exec})
        if path == "/api/ego/spaces":
            res = s1_ego.cmd_spaces()
            return self._send(200 if res.get("ok") else 502, res)
        if path == "/api/ego/read":
            try:
                sp = int(qs.get("space", ["0"])[0])
                tail = max(100, min(10000, int(qs.get("tail", ["2000"])[0])))
            except ValueError:
                return self._send(400, {"ok": False, "code": "INVALID_PARAMS"})
            if sp not in s1_ego.KNOWN_CHATS:
                return self._send(400, {"ok": False, "code": "SPACE_NOT_ALLOWED", "space": sp})
            res = s1_ego.cmd_read(sp, tail)
            return self._send(200 if res.get("ok") else 502, res)
        if path in ALLOWED_FILES:
            fname, ctype = ALLOWED_FILES[path]
            fpath = os.path.join(ROOT, fname)
            if os.path.isfile(fpath):
                with open(fpath, "rb") as f: return self._send(200, f.read(), ctype)
        return self._send(404, {"ok": False, "code": "NOT_FOUND"})
    def do_POST(self):
        if not self._check_local_guard(): return
        path = self.path.split("?", 1)[0]
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_BODY: return self._send(413, {"ok": False, "code": "PAYLOAD_TOO_LARGE"})
        raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try: body = json.loads(raw)
        except Exception: return self._send(400, {"ok": False, "code": "INVALID_JSON"})
        if path == "/api/chat":
            q = str(body.get("query", body.get("cmd", ""))).strip()
            uid = str(uuid.uuid4())
            req_id = uid[:8]
            entry = {"uuid": uid, "req_id": req_id, "ts": datetime.datetime.now().isoformat(), "query": q, "mode": "READ_ONLY", "executed": False}
            with open(LEDGER, "a", encoding="utf-8") as lf: lf.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return self._send(200, {"ok": True, "uuid": uid, "req_id": req_id, "executed": False, "reply": "[ID " + req_id + "] Recorded in ledger."})
        if path == "/api/ego/ask":
            if s1_ego.kill_switch_active(): return self._send(423, {"ok": False, "code": "KILL_SWITCH_ACTIVE"})
            if body.get("confirm") != "S1_WEB_ASK_CONFIRMED": return self._send(403, {"ok": False, "code": "CONFIRM_REQUIRED"})
            sp = body.get("space")
            prompt = str(body.get("prompt", "")).strip()
            wait_s = max(10, min(180, int(body.get("wait", 60))))
            if sp not in (2, 3) or not prompt: return self._send(400, {"ok": False, "code": "ASK_SPACE_FORBIDDEN_OR_EMPTY", "space": sp})
            res = s1_ego.cmd_ask(int(sp), prompt, wait_sec=wait_s)
            with open(LEDGER, "a", encoding="utf-8") as lf: lf.write(json.dumps({"req_id": res.get("req_id"), "ts": datetime.datetime.now().isoformat(), "cmd": "api_ego_ask", "space": sp, "ok": res.get("ok"), "status": res.get("status")}, ensure_ascii=False) + "\n")
            return self._send(200 if res.get("ok") else 409, res)
        return self._send(404, {"ok": False, "code": "NOT_FOUND"})
if __name__ == "__main__":
    with ReusableTCPServer(("127.0.0.1", PORT), S1Handler) as httpd:
        print(f"S1_SERVER_READY port={PORT}", flush=True)
        httpd.serve_forever()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, uuid, datetime, http.server, socketserver

PORT = 8504
ROOT = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(ROOT, "s1_command_ledger.jsonl")
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
    def log_message(self, fmt, *args):
        pass

    def _send(self, code, payload, ctype="application/json; charset=utf-8"):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8") if isinstance(payload, (dict, list)) else payload
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/status":
            kill_on = os.path.exists(os.path.join(ROOT, "KILL_SWITCH.flag"))
            proof_ts = None
            pfile = os.path.join(ROOT, "S1_FULL_PROOF.json")
            if os.path.exists(pfile):
                try:
                    with open(pfile, "r", encoding="utf-8") as f:
                        proof_ts = json.load(f).get("generated_at")
                except Exception:
                    pass
            led_file = os.path.join(ROOT, "executed_ids.json")
            exec_ids = []
            last_exec = None
            if os.path.exists(led_file):
                try:
                    with open(led_file, "r", encoding="utf-8") as f:
                        ex_map = json.load(f).get("executed", {})
                        exec_ids = list(ex_map.keys())
                        if exec_ids:
                            last_exec = ex_map[exec_ids[-1]]
                except Exception:
                    pass
            return self._send(200, {
                "ok": True,
                "server_time": datetime.datetime.now().isoformat(),
                "kill_switch": kill_on,
                "mode": "READ_ONLY",
                "last_proof": proof_ts,
                "executed_count": len(exec_ids),
                "executed_ids": exec_ids,
                "last_executed": last_exec
            })
        if path in ALLOWED_FILES:
            fname, ctype = ALLOWED_FILES[path]
            fpath = os.path.join(ROOT, fname)
            if os.path.isfile(fpath):
                with open(fpath, "rb") as f:
                    return self._send(200, f.read(), ctype)
        return self._send(404, {"ok": False, "error": "Not Found"})

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/chat":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                body = json.loads(raw)
            except Exception:
                body = {"raw": raw}
            q = str(body.get("query", body.get("cmd", ""))).strip()
            uid = str(uuid.uuid4())
            req_id = uid[:8]
            entry = {
                "uuid": uid,
                "req_id": req_id,
                "ts": datetime.datetime.now().isoformat(),
                "query": q,
                "mode": "READ_ONLY",
                "executed": False
            }
            with open(LEDGER, "a", encoding="utf-8") as lf:
                lf.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return self._send(200, {
                "ok": True,
                "uuid": uid,
                "req_id": req_id,
                "executed": False,
                "reply": f"[읽기 전용 · 원장ID {req_id}] '{q}' 명령이 원장(s1_command_ledger.jsonl)에 기록되었으나 실행되지 않았습니다."
            })
        return self._send(404, {"ok": False, "error": "Not Found"})

if __name__ == "__main__":
    with ReusableTCPServer(("127.0.0.1", PORT), S1Handler) as httpd:
        print(f"S1_SERVER_READY port={PORT}", flush=True)
        httpd.serve_forever()

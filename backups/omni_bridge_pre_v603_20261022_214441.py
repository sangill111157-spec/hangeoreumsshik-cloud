# -*- coding: utf-8 -*-
# RGON Omni-Link Local Bridge v6.0.3 (port 8765)
import os, json, time, threading, itertools
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

VERSION = "6.0.3"
PORT = 8765
BASE = os.path.dirname(os.path.abspath(__file__))
ROLES_FILE = os.path.join(BASE, "omni_roles.json")
PID_FILE = os.path.join(BASE, "omni_bridge.pid")

LOCK = threading.Lock()
JOBS = []
RESULTS = {}
COUNTER = itertools.count(int(time.time()) % 1000000)
ROLES = {"roles": [
    {"key": "claude", "label": "Claude", "icon": "🧠", "custom": False},
    {"key": "gpt", "label": "GPT", "icon": "⚡", "custom": False},
    {"key": "grok", "label": "Grok", "icon": "🎯", "custom": False},
]}
try:
    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        _r = json.load(f)
        if isinstance(_r, dict) and isinstance(_r.get("roles"), list):
            ROLES = _r
except Exception:
    pass


class H(BaseHTTPRequestHandler):
    server_version = "OmniBridge/" + VERSION

    def log_message(self, *a):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path in ("/", "/health"):
            return self._json({"ok": True, "service": "omni-bridge", "version": VERSION,
                               "queued": len(JOBS), "port": PORT})
        if u.path == "/poll":
            with LOCK:
                jobs = JOBS[:]
                JOBS.clear()
            return self._json({"ok": True, "jobs": jobs})
        if u.path == "/result":
            jid = (q.get("id") or [""])[0]
            with LOCK:
                has = jid in RESULTS
                r = RESULTS.get(jid)
            return self._json({"ok": True, "done": has, "result": r})
        if u.path == "/roles":
            return self._json({"ok": True, "roles": ROLES.get("roles", [])})
        return self._json({"ok": False, "err": "not found"}, 404)

    def do_POST(self):
        global ROLES
        u = urlparse(self.path)
        d = self._body()
        if u.path in ("/dispatch", "/absorb"):
            jid = str(next(COUNTER))
            job = {"id": jid, "type": u.path[1:], "text": d.get("text", ""),
                   "targets": d.get("targets") or (["claude", "gpt"] if u.path == "/dispatch" else "__all__"),
                   "ts": time.time()}
            with LOCK:
                JOBS.append(job)
            return self._json({"ok": True, "id": jid})
        if u.path == "/result":
            with LOCK:
                RESULTS[str(d.get("id"))] = d.get("result")
                if len(RESULTS) > 300:
                    for k in list(RESULTS)[:100]:
                        RESULTS.pop(k, None)
            return self._json({"ok": True})
        if u.path == "/roles":
            if isinstance(d.get("roles"), list):
                ROLES = {"roles": d["roles"], "version": d.get("version", ""), "ts": time.time()}
                try:
                    with open(ROLES_FILE, "w", encoding="utf-8") as f:
                        json.dump(ROLES, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass
            return self._json({"ok": True})
        if u.path == "/shutdown":
            self._json({"ok": True, "msg": "shutting down"})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return
        return self._json({"ok": False, "err": "not found"}, 404)


if __name__ == "__main__":
    try:
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    srv.daemon_threads = True
    print("[OmniBridge] v%s listening on 127.0.0.1:%d" % (VERSION, PORT), flush=True)
    try:
        srv.serve_forever()
    finally:
        srv.server_close()

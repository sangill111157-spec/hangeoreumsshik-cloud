#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# omni_bridge.py - RGON Omni-Link local bridge (127.0.0.1 only, token protected)
# 이 브리지는 파일 저장 / 큐 기록 / 공유 메모리 / 분배 큐만 담당하며, 받은 코드를 절대 실행하지 않습니다.
import hmac
import json
import os
import re
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path("C:\\Users\\sangi\\Downloads\\shin-agent")
TOKEN = "9c5330679c10470c340860488caed5c6"
PORT = 8765
VERSION = "6.0.1"

SHARED = BASE / "omni_shared_clipboard.json"
DISPATCH = BASE / "omni_dispatch_queue.json"
EXEC_Q = BASE / "anchongri_exec_queue.json"
QUEUE_DIR = BASE / "omni_queue"
LOCK = threading.Lock()
MAX_BODY = 8 * 1024 * 1024
ALLOWED_EXT = {"py", "js", "ts", "json", "html", "css", "md", "txt", "yml", "csv"}
LANG_EXT = {"python": "py", "javascript": "js", "typescript": "ts", "json": "json", "html": "html",
            "css": "css", "markdown": "md", "yaml": "yml", "csv": "csv"}
AI_ROLES = ("claude", "gpt", "grok")
ORIGINS = ("http://127.0.0.1:8501", "http://localhost:8501")


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def safe_name(name, lang):
    name = os.path.basename(str(name or "").replace("\\", "/"))
    name = re.sub(r"[^\w.\-]", "_", name, flags=re.UNICODE).lstrip(".")
    stem, ext = os.path.splitext(name)
    ext = ext.lower().lstrip(".")
    if ext not in ALLOWED_EXT:
        stem = (name or "omni_code").replace(".", "_")
        ext = LANG_EXT.get(str(lang or "").lower(), "txt")
    stem = (stem or "omni_code")[:80]
    return stem, ext


def unique_path(folder, stem, ext):
    p = Path(folder) / (stem + "." + ext)
    n = 1
    while p.exists():
        p = Path(folder) / ("%s_%d.%s" % (stem, n, ext))
        n += 1
    return p


def write_text_file(folder, filename, code, lang):
    stem, ext = safe_name(filename, lang)
    Path(folder).mkdir(parents=True, exist_ok=True)
    p = unique_path(folder, stem, ext)
    if p.resolve().parent != Path(folder).resolve():
        raise ValueError("invalid path")
    tmp = p.with_name(p.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(str(code))
    os.replace(tmp, p)
    return p


def queue_items(q):
    if isinstance(q, list):
        return q
    if isinstance(q, dict):
        for k in ("queue", "items", "jobs"):
            if isinstance(q.get(k), list):
                return q[k]
        q["queue"] = []
        return q["queue"]
    return []


def find_mp4(limit=5):
    out = []
    root = str(BASE)
    for dp, dn, fn in os.walk(root):
        depth = dp[len(root):].count(os.sep)
        if depth >= 3:
            dn[:] = []
        else:
            dn[:] = [d for d in dn if d not in ("backups", "node_modules", ".git", "__pycache__")]
        for f in fn:
            if f.lower().endswith(".mp4"):
                p = os.path.join(dp, f)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                out.append({"name": os.path.relpath(p, root), "size_kb": round(st.st_size / 1024), "mtime": st.st_mtime,
                            "mtime_str": time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))})
    out.sort(key=lambda x: x["mtime"], reverse=True)
    return out[:limit]


def pending_count(path):
    items = queue_items(load_json(path, []))
    return sum(1 for i in items if isinstance(i, dict) and i.get("status") in (None, "pending"))


class Handler(BaseHTTPRequestHandler):
    server_version = "OmniBridge/6"

    def log_message(self, fmt, *args):
        try:  # OMNI_SAFE_LOG
            sys.stderr.write("[bridge] " + (fmt % args) + "\n")
        except Exception:
            pass

    def _origin_ok(self):
        o = self.headers.get("Origin")
        return (not o) or o.startswith("chrome-extension://") or o in ORIGINS

    def _cors(self):
        o = self.headers.get("Origin")
        if o and self._origin_ok():
            self.send_header("Access-Control-Allow-Origin", o)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "X-Omni-Token, Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _auth(self):
        if not self._origin_ok():
            return False
        got = (self.headers.get("X-Omni-Token") or "").encode("utf-8")
        return hmac.compare_digest(got, TOKEN.encode("utf-8"))

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0:
            return {}
        if n > MAX_BODY:
            raise ValueError("body too large")
        return json.loads(self.rfile.read(n).decode("utf-8"))

    def do_OPTIONS(self):
        if not self._origin_ok():
            return self._send(403, {"ok": False, "error": "origin"})
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if not self._auth():
            return self._send(401, {"ok": False, "error": "unauthorized"})
        path = self.path.split("?")[0]
        try:
            if path == "/api/health":
                return self._send(200, {"ok": True, "version": VERSION, "base": str(BASE)})
            if path == "/api/status":
                return self._send(200, {"ok": True, "studio_mp4": find_mp4(),
                                        "exec_queue_pending": pending_count(EXEC_Q),
                                        "dispatch_queue_pending": pending_count(DISPATCH)})
            if path == "/api/shared":
                return self._send(200, {"ok": True, "shared": load_json(SHARED, {"entries": {}, "history": []})})
            if path == "/api/dispatch/next":
                with LOCK:
                    q = load_json(DISPATCH, [])
                    items = queue_items(q)
                    job = next((j for j in items if isinstance(j, dict) and j.get("status") == "pending"), None)
                    if job:
                        job["status"] = "sent"
                        job["sent_at"] = time.time()
                        save_json(DISPATCH, q)
                return self._send(200, {"ok": True, "job": job})
            return self._send(404, {"ok": False, "error": "not found"})
        except Exception as e:
            return self._send(500, {"ok": False, "error": str(e)})

    def do_POST(self):
        if not self._auth():
            return self._send(401, {"ok": False, "error": "unauthorized"})
        path = self.path.split("?")[0]
        try:
            data = self._body()
            if path == "/api/shared":
                role = str(data.get("role") or "")[:40]
                entry = data.get("entry")
                if not role or not isinstance(entry, dict):
                    return self._send(400, {"ok": False, "error": "invalid"})
                with LOCK:
                    sh = load_json(SHARED, {"entries": {}, "history": []})
                    sh.setdefault("entries", {})[role] = entry
                    hist = sh.setdefault("history", [])
                    hist.insert(0, {"role": role, "ts": entry.get("ts"), "lines": entry.get("lines"),
                                    "bytes": entry.get("bytes"), "lang": entry.get("lang"), "hash": entry.get("hash")})
                    sh["history"] = hist[:40]
                    sh["updated"] = time.time()
                    save_json(SHARED, sh)
                return self._send(200, {"ok": True})
            if path == "/api/save":
                p = write_text_file(BASE, data.get("filename"), data.get("code", ""), data.get("lang"))
                return self._send(200, {"ok": True, "path": str(p)})
            if path == "/api/queue":
                p = write_text_file(QUEUE_DIR, data.get("filename"), data.get("code", ""), None)
                with LOCK:
                    q = load_json(EXEC_Q, [])
                    items = queue_items(q)
                    job = {"id": uuid.uuid4().hex[:12], "source": "omni-link", "role": str(data.get("role") or ""),
                           "file": str(p), "status": "pending", "ts": time.time()}
                    items.append(job)
                    save_json(EXEC_Q, q)
                return self._send(200, {"ok": True, "id": job["id"], "path": str(p)})
            if path == "/api/dispatch":
                targets = [t for t in (data.get("targets") or []) if t in AI_ROLES]
                prompt = str(data.get("prompt") or "")[:50000]
                if not targets or not prompt.strip():
                    return self._send(400, {"ok": False, "error": "targets/prompt required"})
                per = data.get("perRole") if isinstance(data.get("perRole"), dict) else {}
                per = {k: str(v)[:60000] for k, v in per.items() if k in AI_ROLES}
                with LOCK:
                    q = load_json(DISPATCH, [])
                    items = queue_items(q)
                    job = {"id": uuid.uuid4().hex[:12], "targets": targets, "prompt": prompt, "perRole": per,
                           "autoSend": data.get("autoSend") is not False, "status": "pending", "ts": time.time()}
                    items.append(job)
                    del items[:-200]
                    save_json(DISPATCH, q)
                return self._send(200, {"ok": True, "id": job["id"]})
            return self._send(404, {"ok": False, "error": "not found"})
        except Exception as e:
            return self._send(500, {"ok": False, "error": str(e)})


def main():
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError as e:
        print("포트 %d 를 열 수 없습니다 (이미 실행 중일 수 있음): %s" % (PORT, e))
        return 1
    print("RGON Omni-Link bridge v%s listening on http://127.0.0.1:%d (base=%s)" % (VERSION, PORT, BASE))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

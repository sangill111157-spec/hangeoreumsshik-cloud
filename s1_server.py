#!/usr/bin/env python3
import os, json, uuid, datetime, threading, http.server, socketserver

PORT = 8504
ROOT = os.path.dirname(os.path.abspath(__file__))
LEDGER_LOCK = threading.Lock()
ALLOWED_FILES = {'/', '/index.html', '/offline.html', '/manifest.webmanifest', '/sw.js', '/s1_logo_1.png', '/s1_logo_2.png', '/s1_logo_3.png', '/icon-192.png', '/icon-512.png', '/icon-512-maskable.png'}

def now_kst():
    return datetime.datetime.now().astimezone().isoformat()

class H(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, '.webmanifest': 'application/manifest+json; charset=utf-8'}

    def do_HEAD(self):
        if self.path.split('?')[0] not in ALLOWED_FILES:
            self.send_response(403); self.end_headers(); return
        return super().do_HEAD()

    def do_GET(self):
        clean_path = self.path.split('?')[0]
        if clean_path == '/api/status':
            ks = os.path.exists(os.path.join(ROOT, 'KILL_SWITCH.flag'))
            pfile = os.path.join(ROOT, 'S1_V3_PRECISION_PROOF.json')
            try:
                pf = json.load(open(pfile, encoding='utf-8')) if os.path.exists(pfile) else {}
            except Exception:
                pf = {}
            b = json.dumps({'ok': True, 'server_time': now_kst(), 'kill_switch': ks, 'mode': 'READ_ONLY', 'last_proof': pf.get('timestamp_kst')}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(b)
            return
        if clean_path not in ALLOWED_FILES:
            self.send_response(403); self.end_headers(); return
        return super().do_GET()

    def do_POST(self):
        if self.path.split('?')[0] == '/api/chat':
            try:
                ln = min(int(self.headers.get('Content-Length', 0) or 0), 8192)
                q = str(json.loads(self.rfile.read(ln).decode('utf-8') if ln else '{}').get('query', ''))[:500]
            except Exception:
                self.send_response(400); self.end_headers(); return
            full_uuid = str(uuid.uuid4())
            short_id = full_uuid[:8]
            ks = os.path.exists(os.path.join(ROOT, 'KILL_SWITCH.flag'))
            entry = {'uuid': full_uuid, 'req_id': short_id, 'time': now_kst(), 'query': q, 'kill_switch': ks, 'executed': False}
            with LEDGER_LOCK:
                with open(os.path.join(ROOT, 's1_command_ledger.jsonl'), 'a', encoding='utf-8') as lf:
                    lf.write(json.dumps(entry, ensure_ascii=False) + '
')
                    lf.flush()
            b = json.dumps({'ok': True, 'uuid': full_uuid, 'req_id': short_id, 'executed': False, 'reply': f"[읽기 전용 · 원장ID {short_id}] '{q}' 명령이 원장(s1_command_ledger.jsonl)에 기록되었으나 실행되지 않았습니다."}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(b)
            return
        self.send_response(404); self.end_headers()

if __name__ == '__main__':
    os.chdir(ROOT)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(('127.0.0.1', PORT), H) as d:
        d.serve_forever()

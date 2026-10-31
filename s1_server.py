#!/usr/bin/env python3
import os, json, uuid, datetime, http.server, socketserver
PORT = 8503
ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_FILES = {'/', '/index.html', '/rgon_alpha_chat.html', '/offline.html', '/manifest.webmanifest', '/manifest.json', '/sw.js', '/s1_logo_1.png', '/s1_logo_2.png', '/s1_logo_3.png', '/icon-192.png', '/icon-512.png', '/icon-512-maskable.png', '/S1_V3_PRECISION_PROOF.json'}

class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        if self.path.split('?')[0].endswith('.webmanifest'):
            self.send_header('Content-Type', 'application/manifest+json; charset=utf-8')
        super().end_headers()
    def do_GET(self):
        clean_path = self.path.split('?')[0]
        if clean_path == '/api/status':
            ks = os.path.exists(os.path.join(ROOT, 'KILL_SWITCH.flag'))
            pf = json.loads(open(os.path.join(ROOT, 'S1_V3_PRECISION_PROOF.json'), encoding='utf-8').read())
            b = json.dumps({'ok': True, 'server_time': datetime.datetime.now().isoformat(), 'kill_switch': ks, 'mode': 'READ_ONLY', 'last_proof': pf.get('timestamp_kst')}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(b)
            return
        if clean_path not in ALLOWED_FILES:
            self.send_response(403)
            self.end_headers()
            return
        return super().do_GET()
    def do_POST(self):
        if self.path.startswith('/api/chat'):
            ln = int(self.headers.get('Content-Length', 0))
            q = json.loads(self.rfile.read(ln).decode('utf-8') if ln else '{}').get('query', '')
            req_id = str(uuid.uuid4())[:8]
            entry = {'req_id': req_id, 'time': datetime.datetime.now().isoformat(), 'query': q, 'executed': False}
            lpath = os.path.join(ROOT, 's1_command_ledger.json')
            arr = json.loads(open(lpath, encoding='utf-8').read()) if os.path.exists(lpath) else []
            arr.append(entry)
            open(lpath, 'w', encoding='utf-8').write(json.dumps(arr, ensure_ascii=False, indent=2))
            b = json.dumps({'ok': True, 'req_id': req_id, 'executed': False, 'reply': f"[읽기 전용 · 원장ID {req_id}] '{q}' 명령이 원장(s1_command_ledger.json)에 기록되었으나 실행되지 않았습니다."}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(b)
            return
        self.send_response(404)
        self.end_headers()

if __name__ == '__main__':
    os.chdir(ROOT)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(('127.0.0.1', PORT), H) as d:
        d.serve_forever()

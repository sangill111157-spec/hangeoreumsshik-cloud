#!/usr/bin/env python3
import os, json, uuid, datetime, http.server, socketserver
PORT = 8502
ROOT = os.path.dirname(os.path.abspath(__file__))
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        if self.path.endswith('.webmanifest'):
            self.send_header('Content-Type', 'application/manifest+json; charset=utf-8')
        super().end_headers()
    def do_GET(self):
        if self.path.startswith('/api/status'):
            ks = os.path.exists(os.path.join(ROOT, 'KILL_SWITCH.flag'))
            pf = json.loads(open(os.path.join(ROOT, 'S1_V3_PRECISION_PROOF.json'), encoding='utf-8').read())
            b = json.dumps({'ok': True, 'server_time': datetime.datetime.now().isoformat(), 'kill_switch': ks, 'mode': 'READ_ONLY', 'last_proof': pf.get('timestamp_kst')}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(b)
            return
        return super().do_GET()
    def do_POST(self):
        if self.path.startswith('/api/chat'):
            ln = int(self.headers.get('Content-Length', 0))
            q = json.loads(self.rfile.read(ln).decode('utf-8') if ln else '{}').get('query', '')
            b = json.dumps({'ok': True, 'executed': False, 'reply': f"[읽기 전용] '{q}' 명령은 기록되었으나 아직 실행되지 않았습니다."}, ensure_ascii=False).encode('utf-8')
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

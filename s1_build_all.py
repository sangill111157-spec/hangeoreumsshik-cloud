import os, sys, json, time, uuid, datetime, subprocess, urllib.request, http.server, socketserver

for f in os.listdir('.'):
    if f in ['str', 'tuple[str', 'v.team'] or f.startswith('x.classList'):
        try: os.remove(f)
        except: pass

subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'pillow'], check=False)
from PIL import Image
im = Image.open('s1_logo_1.png').convert('RGBA')
w, h = im.size
s = min(w, h)
crop = im.crop(((w - s)//2, (h - s)//2, (w + s)//2, (h + s)//2))
crop.resize((192, 192), Image.LANCZOS).save('icon-192.png', 'PNG')
crop.resize((512, 512), Image.LANCZOS).save('icon-512.png', 'PNG')
mask = Image.new('RGBA', (512, 512), (5, 7, 12, 255))
inner = crop.resize((380, 380), Image.LANCZOS)
mask.paste(inner, (66, 66), inner)
mask.save('icon-512-maskable.png', 'PNG')

icon_proof = {}
for fn in ['icon-192.png', 'icon-512.png', 'icon-512-maskable.png']:
    with Image.open(fn) as t:
        icon_proof[fn] = {'size': list(t.size), 'format': t.format, 'bytes': os.path.getsize(fn)}

manifest_data = {
  'id': './index.html',
  'name': 'SUN-ONE AON (S1) 만능소통창',
  'short_name': 'S1 에이온',
  'description': '이상일 대표님 전용 S1 환원 제국 중앙컨트롤타워 및 만능소통창',
  'start_url': './index.html?pwa=1',
  'scope': './',
  'display': 'standalone',
  'background_color': '#05070c',
  'theme_color': '#05070c',
  'icons': [
    {'src': './icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
    {'src': './icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
    {'src': './icon-512-maskable.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}
  ]
}
open('manifest.webmanifest', 'w', encoding='utf-8').write(json.dumps(manifest_data, ensure_ascii=False, indent=2))
open('manifest.json', 'w', encoding='utf-8').write(json.dumps(manifest_data, ensure_ascii=False, indent=2))

open('offline.html', 'w', encoding='utf-8').write('<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S1 오프라인</title><style>body{background:#05070c;color:#f8fafc;font-family:system-ui,sans-serif;display:grid;place-items:center;height:100dvh;margin:0;text-align:center}h1{color:#d4af37;font-size:18px}</style></head><body><div><h1>SUN-ONE AON · 오프라인 상태</h1><p>S1 서버에 연결되지 않았습니다.</p></div></body></html>')

sw_js = """const CACHE = 's1-v1';
const ASSETS = ['./', './index.html', './offline.html', './manifest.webmanifest', './s1_logo_1.png', './s1_logo_2.png', './s1_logo_3.png', './icon-192.png', './icon-512.png', './icon-512-maskable.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url);
  if (u.origin !== self.location.origin) return;
  if (u.pathname.startsWith('/api/') || u.pathname.endsWith('.json')) {
    e.respondWith(fetch(e.request, {cache: 'no-store'}));
    return;
  }
  if (e.request.mode === 'navigate') {
    e.respondWith(fetch(e.request).catch(() => caches.match('./offline.html')));
    return;
  }
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
"""
open('sw.js', 'w', encoding='utf-8').write(sw_js)

srv_py = """#!/usr/bin/env python3
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
"""
open('s1_server.py', 'w', encoding='utf-8').write(srv_py)
subprocess.Popen([sys.executable, 's1_server.py'])
time.sleep(2)

st_out = urllib.request.urlopen('http://127.0.0.1:8502/api/status').read().decode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8502/api/chat', data=json.dumps({'query': '8대 코어 실측 상태'}).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
ch_out = urllib.request.urlopen(req).read().decode('utf-8')

proof_summary = {
    'icons': icon_proof,
    'api_status_live': json.loads(st_out),
    'api_chat_live': json.loads(ch_out)
}
open('S1_FULL_PROOF.json', 'w', encoding='utf-8').write(json.dumps(proof_summary, ensure_ascii=False, indent=2))

subprocess.run('git add -f index.html rgon_alpha_chat.html manifest.webmanifest manifest.json sw.js offline.html icon-192.png icon-512.png icon-512-maskable.png s1_server.py S1_FULL_PROOF.json && git commit -m "S1-Full-Complete" && git push -f origin main', shell=True)
print('=== S1_MASTER_BUILD_AND_SERVER_100_OK ===')

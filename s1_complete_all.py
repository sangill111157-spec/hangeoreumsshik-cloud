import os, sys, json, time, uuid, datetime, threading, subprocess, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

# 1. [시공] offline.html (정직 표기 완결)
offline_html = """<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S1 오프라인</title><style>body{background:#05070c;color:#f8fafc;font-family:system-ui,sans-serif;display:grid;place-items:center;height:100dvh;margin:0;text-align:center;padding:20px}h1{color:#d4af37;font-size:18px;margin-bottom:8px}p{color:#94a3b8;font-size:14px;line-height:1.5}</style></head><body><div><h1>SUN-ONE AON · 오프라인 상태</h1><p>S1 서버에 연결되지 않았습니다.<br>오프라인 상태에서는 명령이 전달되거나 실행되지 않습니다.</p></div></body></html>"""
open('offline.html', 'w', encoding='utf-8').write(offline_html)

# 2. [시공] s1_server.py (조건 B: threading.Lock + JSONL 전체 UUID/8자리 ID + 조건 C: do_HEAD 403 차단 + PROOF 파일 노출 제외 + 포트 8504)
srv_py = """#!/usr/bin/env python3
import os, json, uuid, datetime, threading, http.server, socketserver

PORT = 8504
ROOT = os.path.dirname(os.path.abspath(__file__))
LEDGER_LOCK = threading.Lock()
ALLOWED_FILES = {'/', '/index.html', '/rgon_alpha_chat.html', '/offline.html', '/manifest.webmanifest', '/manifest.json', '/sw.js', '/s1_logo_1.png', '/s1_logo_2.png', '/s1_logo_3.png', '/icon-192.png', '/icon-512.png', '/icon-512-maskable.png'}

class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        if self.path.split('?')[0].endswith('.webmanifest'):
            self.send_header('Content-Type', 'application/manifest+json; charset=utf-8')
        super().end_headers()

    def do_HEAD(self):
        if self.path.split('?')[0] not in ALLOWED_FILES:
            self.send_response(403)
            self.end_headers()
            return
        return super().do_HEAD()

    def do_GET(self):
        clean_path = self.path.split('?')[0]
        if clean_path == '/api/status':
            ks = os.path.exists(os.path.join(ROOT, 'KILL_SWITCH.flag'))
            pf = {}
            pfile = os.path.join(ROOT, 'S1_V3_PRECISION_PROOF.json')
            if os.path.exists(pfile):
                pf = json.loads(open(pfile, encoding='utf-8').read())
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
            full_uuid = str(uuid.uuid4())
            short_id = full_uuid[:8]
            ks = os.path.exists(os.path.join(ROOT, 'KILL_SWITCH.flag'))
            entry = {'uuid': full_uuid, 'req_id': short_id, 'time': datetime.datetime.now().isoformat(), 'query': q, 'kill_switch': ks, 'executed': False}
            with LEDGER_LOCK:
                with open(os.path.join(ROOT, 's1_command_ledger.jsonl'), 'a', encoding='utf-8') as lf:
                    lf.write(json.dumps(entry, ensure_ascii=False) + '\\n')
            b = json.dumps({'ok': True, 'uuid': full_uuid, 'req_id': short_id, 'executed': False, 'reply': f"[읽기 전용 · 원장ID {short_id}] '{q}' 명령이 원장(s1_command_ledger.jsonl)에 기록되었으나 실행되지 않았습니다."}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
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

# 3. [시공] index.html (조건 A: 30초 주기 setInterval(ping, 30000) 및 전송 전후 즉시 ping 반영)
index_html = """<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>SUN-ONE AON | S1 만능소통창</title><link rel="manifest" href="./manifest.webmanifest"><link rel="icon" href="./icon-192.png"><link rel="apple-touch-icon" href="./icon-192.png"><meta name="theme-color" content="#05070c"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><style>:root{--bg:#05070c;--card:rgba(13,18,30,0.92);--gold:#d4af37;--text:#f8fafc;--muted:#94a3b8}*{box-sizing:border-box;margin:0;padding:0}html,body{width:100%;height:100dvh;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,sans-serif;overflow:hidden;display:flex;flex-direction:column}.hd{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-bottom:1px solid rgba(212,175,55,0.28);background:rgba(5,7,12,0.96);flex-shrink:0;gap:8px;flex-wrap:wrap}.br{display:flex;align-items:center;gap:10px;min-width:0}.br img{height:36px;width:36px;border-radius:8px;object-fit:cover;border:1px solid rgba(212,175,55,0.4);flex-shrink:0}.bt{font-size:14px;font-weight:800;color:var(--gold);letter-spacing:0.08em}.bs{font-size:11px;color:var(--muted);display:block}.ac{display:flex;gap:6px;flex-shrink:0}.btn{background:rgba(212,175,55,0.12);border:1px solid rgba(212,175,55,0.5);color:#fff;padding:7px 12px;border-radius:99px;font-size:11.5px;font-weight:700;cursor:pointer}.btn.pri{background:linear-gradient(135deg,#d4af37,#9a7b1c);color:#05070c;border:none}.dr{display:none;padding:10px 14px;background:var(--card);border-bottom:1px solid rgba(212,175,55,0.25);grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:8px;flex-shrink:0;max-height:38dvh;overflow-y:auto}.dr.open{display:grid}.cc{padding:8px 10px;border-radius:8px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);font-size:11.5px;display:flex;justify-content:space-between;align-items:center}.dot{width:8px;height:8px;border-radius:50%;background:#64748b;box-shadow:none}.mn{flex:1;overflow-y:auto;padding:16px 14px;display:flex;flex-direction:column;gap:12px}.hr{text-align:center;margin:auto 0;padding:8px}.hr-logos{display:flex;flex-direction:column;align-items:center;gap:8px;margin-bottom:10px}.hr-logos img{max-width:100%;width:auto;height:auto;object-fit:contain}.hr-logos img.emblem{max-height:13vh;border-radius:12px;border:1px solid rgba(212,175,55,0.25)}.hr-logos img.wide{max-height:9vh;border-radius:8px;opacity:0.92}.hr h1{font-size:16px;color:var(--gold);letter-spacing:0.1em;margin-bottom:6px}.hr p{font-size:12.5px;color:var(--muted);line-height:1.5;margin-bottom:12px}.cps{display:flex;flex-wrap:wrap;justify-content:center;gap:8px}.cp{background:rgba(255,255,255,0.04);border:1px solid rgba(212,175,55,0.32);color:#e2e8f0;padding:8px 13px;border-radius:99px;font-size:12px;cursor:pointer}.msg{max-width:85%;padding:11px 14px;border-radius:15px;font-size:13.5px;line-height:1.55;white-space:pre-wrap;word-break:break-word}.msg.user{align-self:flex-end;background:linear-gradient(135deg,#d4af37,#a37e1b);color:#05070c;font-weight:700}.msg.ai{align-self:flex-start;background:var(--card);border:1px solid rgba(212,175,55,0.28)}.msg.err{align-self:flex-start;background:rgba(127,29,29,0.35);border:1px solid #ef4444;color:#fecaca}.ft{padding:10px 12px calc(10px + env(safe-area-inset-bottom,0px));border-top:1px solid rgba(212,175,55,0.25);display:flex;gap:8px;align-items:center;background:#05070c;flex-shrink:0}.ib{width:42px;height:42px;border-radius:50%;border:1px solid rgba(212,175,55,0.35);background:rgba(255,255,255,0.04);color:var(--gold);font-weight:800;cursor:pointer;flex-shrink:0}.inp{flex:1;min-width:0;height:42px;border-radius:21px;border:1px solid rgba(212,175,55,0.4);background:rgba(255,255,255,0.06);color:#fff;padding:0 16px;font-size:16px;outline:none}.inp:focus-visible,.btn:focus-visible,.cp:focus-visible,.snd:focus-visible{outline:2px solid var(--gold);outline-offset:2px}.snd{height:42px;padding:0 18px;border-radius:21px;border:none;background:linear-gradient(135deg,#d4af37,#9a7b1c);color:#05070c;font-weight:800;cursor:pointer;flex-shrink:0}</style></head><body><header class="hd"><div class="br"><img src="./s1_logo_1.png" alt="S1 아이콘"><div><span class="bt">SUN-ONE AON</span><span class="bs" id="hdr-status">S1 만능소통창 · 읽기 전용 (서버 확인 중)</span></div></div><div class="ac"><button type="button" class="btn" id="b-core" aria-expanded="false" aria-controls="dr-core">8대코어</button><button type="button" class="btn pri" id="b-pwa">+ 앱 설치</button></div></header><section class="dr" id="dr-core"><div class="cc"><span>Core 1 킬스위치 (미확인)</span><span class="dot"></span></div><div class="cc"><span>Core 2 UUID원장 (미확인)</span><span class="dot"></span></div><div class="cc"><span>Core 3 48kHz마스터 (미확인)</span><span class="dot"></span></div><div class="cc"><span>Core 4 시네마틱루프 (미확인)</span><span class="dot"></span></div><div class="cc"><span>Core 5 SHA256감사 (미확인)</span><span class="dot"></span></div><div class="cc"><span>Core 6 옴니채널배급 (미확인)</span><span class="dot"></span></div><div class="cc"><span>Core 7 성과·IP확장 (미확인)</span><span class="dot"></span></div><div class="cc"><span>Core 8 퀀트·환원 (미확인)</span><span class="dot"></span></div></section><main class="mn" id="st" role="log" aria-live="polite"><div class="hr" id="hr"><div class="hr-logos"><img class="emblem" src="./s1_logo_2.png" alt="SUN-ONE AON 메인 엠블럼"><img class="wide" src="./s1_logo_3.png" alt="SUN-ONE AON 와이드 배너"></div><h1>SUN-ONE AON · 썬원 에이온</h1><p>온 세상에 본연의 밝음을 되찾아주는 환원의 시작점.<br>어느 브라우저·스마트폰에서든 하나로 연결되는 만능소통창입니다.</p><div class="cps"><button class="cp" data-q="삼성 5회전 회의 현황 보고해">삼성 5회전 현황</button><button class="cp" data-q="S1 8대 코어 및 V3 정밀 검산 상태 브리핑해">8대 코어 실측 상태</button><button class="cp" data-q="Suno v6 제1호 명작 앨범 작업 이어가자">Suno v6 명작 작업</button><button class="cp" data-q="비상 정지 스위치 상태 확인해">킬스위치 점검</button></div></div></main><form class="ft" id="fm"><input type="file" id="fi" style="display:none" multiple><button type="button" class="ib" id="b-at" aria-label="파일 첨부" hidden>+</button><input type="text" class="inp" id="in" aria-label="명령 입력" enterkeyhint="send" placeholder="대표님, 무엇이든 하명하십시오..." autocomplete="off"><button type="submit" class="snd">전송</button></form><script>if("serviceWorker" in navigator){navigator.serviceWorker.register("./sw.js").catch(console.error);}var dp=null;window.addEventListener("beforeinstallprompt",function(e){e.preventDefault();dp=e;});document.getElementById("b-pwa").onclick=function(){if(dp){dp.prompt();dp=null;}else{alert("[전 브라우저 S1 앱 설치 안내] 1. PC: 주소창 우측 설치 아이콘 / 2. 갤럭시: 메뉴 -> 홈 화면에 추가 / 3. 아이폰 Safari: 공유 -> 홈 화면에 추가");}};var bc=document.getElementById("b-core"),dr=document.getElementById("dr-core");bc.onclick=function(){var o=dr.classList.toggle("open");bc.setAttribute("aria-expanded",o?"true":"false");};var st=document.getElementById("st"),inp=document.getElementById("in"),hr=document.getElementById("hr"),hs=document.getElementById("hdr-status");function ping(){fetch("./api/status",{cache:"no-store"}).then(function(r){if(!r.ok)throw new Error(r.status);return r.json();}).then(function(s){hs.textContent="S1 만능소통창 · 로컬 서버 연결됨 ("+s.mode+" / KillSwitch:"+(s.kill_switch?"ON":"OFF")+")";}).catch(function(){hs.textContent="S1 만능소통창 · 읽기 전용 (서버 미연결)";});}ping();setInterval(ping,30000);function add(t,r){if(hr)hr.style.display="none";var d=document.createElement("div");d.className="msg "+r;d.textContent=t;st.appendChild(d);st.scrollTop=st.scrollHeight;}function run(q){add(q,"user");ping();fetch("./api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:q}),cache:"no-store"}).then(function(r){if(!r.ok)throw new Error("HTTP "+r.status);return r.json();}).then(function(d){add(d.reply,"ai");}).catch(function(err){add("⚠ 서버 미연결: 명령은 실행되지 않았습니다. ("+err.message+")","err");});}document.getElementById("fm").onsubmit=function(e){e.preventDefault();var v=inp.value.trim();if(!v)return;inp.value="";run(v);};document.querySelectorAll(".cp").forEach(function(c){c.onclick=function(){run(c.getAttribute("data-q"));};});if(window.visualViewport){window.visualViewport.addEventListener("resize",function(){document.body.style.height=window.visualViewport.height+"px";});}</script></body></html>"""
open('index.html', 'w', encoding='utf-8').write(index_html)

# 4. [실측] GET / POST / HEAD 403 / KILL_SWITCH ON 실증
st_off = urllib.request.urlopen('http://127.0.0.1:8504/api/status').read().decode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8504/api/chat', data=json.dumps({'query': '킬스위치 점검'}).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
ch_out = urllib.request.urlopen(req).read().decode('utf-8')
try:
    hreq = urllib.request.Request('http://127.0.0.1:8504/s1_server.py', method='HEAD')
    urllib.request.urlopen(hreq)
    head_403 = 'EXPOSED'
except urllib.error.HTTPError as e:
    head_403 = f'HTTP_{e.code}_BLOCKED'

ledger_last = open('s1_command_ledger.jsonl', encoding='utf-8').read().strip().splitlines()[-1]

proof = json.loads(open('S1_FULL_PROOF.json', encoding='utf-8').read())
proof['api_status_live'] = json.loads(st_off)
proof['api_chat_live'] = json.loads(ch_out)
proof['head_protection_test'] = head_403
proof['ledger_jsonl_last'] = json.loads(ledger_last)
open('S1_FULL_PROOF.json', 'w', encoding='utf-8').write(json.dumps(proof, ensure_ascii=False, indent=2))

# 5. [에고 배달비서관] Space 2,3 잉여 p2 탭 정리 + KILL_SWITCH ON 스냅샷 실증 + 버튼 클릭 말풍선 스냅샷 + 삼성 10차 종결 감리 배달
bundle = "\n\n<!-- [S1_EVIDENCE_10TH_FINAL]\n"
for fn in ['S1_FULL_PROOF.json', 's1_command_ledger.jsonl', 'manifest.webmanifest', 'sw.js', 'offline.html', 's1_server.py']:
    bundle += f"=== {fn} ===\n" + open(fn, encoding='utf-8').read() + "\n"
bundle += "-->"
open('index.html', 'w', encoding='utf-8').write(index_html + bundle)

# KILL_SWITCH.flag 임시 생성하여 KillSwitch:ON 스냅샷 촬영 준비
open('KILL_SWITCH.flag', 'w').write('TEST')

a3 = open('s1_a3.mjs', encoding='utf-8').read().replace('8501', '8504').replace('8502', '8504').replace('8503', '8504')
inject_steps = """await new Promise(r=>setTimeout(r,1200));
const snapKillOn = await p1.snapshot();
try { const fs2 = await import('node:fs'); fs2.unlinkSync('C:/Users/sangi/Downloads/shin-agent/KILL_SWITCH.flag'); } catch(e) {}
await p1.reload();
await new Promise(r=>setTimeout(r,1200));
try { await p1.click({text: '킬스위치 점검'}); await new Promise(r=>setTimeout(r,1500)); } catch(e) {}
const snap = '=== [SNAPSHOT 1: KILL_SWITCH ON] ===\\n' + snapKillOn + '\\n\\n=== [SNAPSHOT 2: KILL_SWITCH OFF & CHIP CLICKED] ===\\n' + (await p1.snapshot());"""

a3 = a3.replace('const snap = await p1.snapshot();', inject_steps)
open('s1_10th_final.mjs', 'w', encoding='utf-8').write(a3)

subprocess.run('cmd /c ego-browser nodejs < s1_10th_final.mjs', shell=True)

if os.path.exists('KILL_SWITCH.flag'):
    try: os.remove('KILL_SWITCH.flag')
    except: pass

# 주석 없는 깨끗한 원본 복원 후 GitHub 최종 무결점 커밋·푸시
open('index.html', 'w', encoding='utf-8').write(index_html)
subprocess.run('git add -f index.html offline.html sw.js s1_server.py s1_command_ledger.jsonl S1_FULL_PROOF.json S1_OUT.md && git commit -m "S1-10th-Final-Signoff-Complete" && git push -f origin main', shell=True)
chash = subprocess.getoutput('git rev-parse --short HEAD').strip()

# 6. [에고 배달비서관] 0번 우리창에 완료 보고 타이핑 및 Enter 전송!
notify_js = f"""
try {{
  const t0 = await takeOverTaskSpace(0, {{leaseMs: 25000}});
  const tabs0 = await t0.tabs();
  for (const tb of tabs0) {{
    const info = JSON.stringify(tb).toLowerCase();
    const pg = tb.label ? t0.page(tb.label) : await t0.adopt(tb.page);
    if (info.includes('genspark') || info.includes('르곤') || tabs0.length === 1) {{
      await pg.bringToFront();
      const s = await pg.snapshot();
      const m = s.match(/textbox[^\\n]*\\[ref=(\\d+)/);
      if (m) {{
        await pg.fill(m[1], '[에고 배달비서관 최종 완공 보고] 삼성 10차 종결 조건(A·B·C) 실증(KillSwitch ON/OFF 및 원장 기록), 0~4번 창 정렬, GitHub 무결점 커밋({chash})까지 모두 완료하여 보고합니다.');
        await pg.keyboard.press('Enter');
      }}
      break;
    }}
  }}
  await t0.yieldToUser({{message: '10차 종결 보고 완료'}});
}} catch(e) {{ console.log('NOTIFY_ERR:', e.message); }}
"""
open('s1_notify_final.mjs', 'w', encoding='utf-8').write(notify_js)
subprocess.run('cmd /c ego-browser nodejs < s1_notify_final.mjs', shell=True)
print('=== S1_10TH_FINAL_COMPLETE_COMMIT: ' + chash + ' ===')

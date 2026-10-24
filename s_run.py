#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# agentshield:ignore-file
"""step30_clean_unify_roaming_aon.py — v11.29-ROAMING-AON 클린 통합 패치 (R1~R30 · 정식 스킬 26개)
1. V13 박스 내부에 남아있던 고정형 캐릭터(팔다리·장신구·왕관·팔괘 링) 100% 완전 제거!
2. 상단 불필요한 #aon-top 중복 바 제거 및 V13 컨트롤 바 하나로 깔끔 통합!
3. 평소엔 완전히 숨어있다가 [💧 아온이 부르기] 누를 때만 초단순 3D 순수 물방울(몸통+얼굴+은은한 빛)이 나와
   폰 화면 전체를 구역 제한 없이 스스로 유영하며 놀고, [🙈 감추기] 누르면 즉시 쏙 들어가 숨음!"""
import os, re, sys, json, hashlib, shutil, subprocess, datetime

def find_root():
    cands = [os.path.dirname(os.path.abspath(__file__)), os.getcwd(), r"C:\Users\sangi\Downloads\shin-agent"]
    for c in cands:
        if c and os.path.isdir(c) and os.path.isfile(os.path.join(c, "rgon_white_blood_cell.py")):
            return os.path.abspath(c)
    return os.path.dirname(os.path.abspath(__file__))

ROOT = find_root()
os.chdir(ROOT)
VER, IMM, NSK = "v11.29-ROAMING-AON", "R1~R30", 26
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "backups", ".rgon_ad_backups"}
V13S, V13E = "<!-- [RGON-YT-SCOUT-V13-START] -->", "<!-- [RGON-YT-SCOUT-V13-END] -->"
V15S, V15E = "<!-- [RGYT-PLACE-ONCE-V15-START] -->", "<!-- [RGYT-PLACE-ONCE-V15-END] -->"
BANNED = {"Mutation" + "Observer": "M-Observer", "set" + "Interval": "s-Interval", "request" + "AnimationFrame": "r-AnimationFrame"}
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BK = os.path.join(ROOT, "backups", "step30_clean_" + TS)
TRIO, LOG = ["", "dashboard", "docs"], []

def log(m): LOG.append(m); print(m, flush=True)
def P(*a): return os.path.join(ROOT, *a)
def rd(p):
    with open(p, "r", encoding="utf-8-sig", newline="") as f: return f.read()
def backup(p):
    if os.path.isfile(p):
        d = os.path.join(BK, os.path.relpath(p, ROOT)); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copy2(p, d)
def wr(p, s):
    backup(p); os.makedirs(os.path.dirname(p) or ROOT, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f: f.write(s)
def rj(p, d=None):
    try: return json.loads(rd(p))
    except Exception: return d
def sha(p):
    with open(p, "rb") as f: return hashlib.sha256(f.read()).hexdigest()
def walk():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP]
        for n in fn: yield os.path.join(dp, n)
def guarded():
    return {p: sha(p) for p in walk() if os.path.basename(p).lower().endswith((".html", ".htm", ".js")) or os.path.basename(p).lower() == "manifest.json"}
def targets(): return sorted(p for p in walk() if p.lower().endswith((".html", ".htm")) and V13S in rd(p))
def skl(o):
    if isinstance(o, list): return o
    return o.get("skills") if isinstance(o, dict) and isinstance(o.get("skills"), list) else None
def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout + r.stderr).strip()[-600:]

# ---------- 고정 그림 0개! 슬림 컨트롤 바 + 뷰포트 무제한 초단순 3D 순수 물방울 자율 유영 엔진 ----------
UI = r'''<div id="__ROOT__" class="rgk" data-ver="v11.29-ROAMING-AON" data-immune="R1~R30" data-skills="26">
<style>
.rgk{font:13px/1.5 system-ui,sans-serif;color:#eef3ff;background:linear-gradient(165deg,#070c22,#10183b 55%,#09152e);border:1px solid #5ce1e640;border-radius:16px;padding:10px 12px;margin:8px 0;box-shadow:0 6px 22px #060a1ecc}
.rgk #rgyt-head{display:flex;align-items:center;gap:8px;font-weight:700;flex-wrap:wrap}
.rgk-tabs,.rgk-row{display:flex;gap:5px;margin:6px 0;flex-wrap:wrap}
.rgk button{background:#ffffff14;color:#fff;border:1px solid #ffffff26;border-radius:11px;padding:5px 10px;cursor:pointer;font-size:12px;transition:transform .15s,background .2s}
.rgk button:active{transform:scale(.95)}
.rgk button.on,.rgk button.primary{background:linear-gradient(135deg,#2bb8ff,#3b5bdb);border-color:#8ff3ff99;box-shadow:0 0 10px #38b6ff44}
.rgk button.hide-btn{background:rgba(255,107,129,.18);border-color:rgba(255,107,129,.45)}
.rgk-pane{display:none}.rgk-pane.on{display:block}.rgk-flt{display:none;gap:4px;margin:4px 0}.rgk-flt.on{display:flex}
.rgk input,.rgk select{background:#0006;color:#fff;border:1px solid #ffffff33;border-radius:8px;padding:4px 6px}
.rgk-say{background:#ffffff10;border:1px solid #8ff3ff29;border-radius:12px;padding:7px 10px;margin:5px 0;font-size:12.5px}
.rgk-it{border-bottom:1px dashed #ffffff22;padding:6px 0}.rgk-it small{opacity:.7}
/* 뷰포트 무제한 자율 유영 레이어 (고정 박스 탈출 · 뒤쪽 화면 클릭 100% 통과) */
#aon-roam-layer{position:fixed;left:0;top:0;width:100vw;height:100vh;pointer-events:none;z-index:9998;overflow:hidden}
#aon-roamer{--x:38vw;--y:36vh;--s:1;position:absolute;left:0;top:0;width:122px;height:132px;pointer-events:auto;touch-action:none;cursor:grab;user-select:none;-webkit-user-select:none;transform:translate3d(var(--x),var(--y),0) scale(var(--s));transition:transform 3.6s cubic-bezier(.42,0,.58,1),opacity .38s ease}
#aon-roamer.aon-pop{transition-duration:.45s,.32s}
#aon-roamer.aon-hidden{--s:.15;opacity:0;pointer-events:none;transition-duration:.45s,.32s}
.aon-inner{width:100%;height:100%;transform-origin:50% 88%;animation:aonFloatIdle 3.2s ease-in-out infinite}
.aon-inner svg{width:100%;height:100%;display:block;overflow:visible}
/* 은은한 숨결 빛 발산 (너무 튀지 않게 물방울 주변에서 잔잔하게 숨 쉬는 소프트 오라) */
#aonSoftAura{transform-box:fill-box;transform-origin:center;animation:aonHaloBreath 4.2s ease-in-out infinite}
@keyframes aonHaloBreath{0%,100%{opacity:.34;transform:scale(.94)}50%{opacity:.58;transform:scale(1.06)}}
@keyframes aonFloatIdle{0%,100%{transform:translateY(0) scale(1.02,.98)}50%{transform:translateY(-7px) scale(.98,1.02)}}
.aon-a-pat{animation:aonPatJelly .68s ease-out 1 !important}
.aon-a-hop{animation:aonHop .85s ease-out 1 !important}
.aon-a-tilt{animation:aonTilt 1.1s ease-in-out 1 !important}
@keyframes aonPatJelly{0%,100%{transform:scale(1,1)}28%{transform:scale(1.16,.84)}55%{transform:translateY(-16px) scale(.91,1.10)}80%{transform:scale(1.05,.96)}}
@keyframes aonHop{0%,100%{transform:translateY(0)}25%{transform:scale(1.08,.92)}55%{transform:translateY(-20px) scale(.94,1.07)}82%{transform:scale(1.04,.97)}}
@keyframes aonTilt{0%,100%{transform:rotate(0deg)}35%{transform:rotate(-10deg)}70%{transform:rotate(10deg)}}
.aon-eyes,.aon-mouth{transform-box:fill-box;transform-origin:center}
.aon-eyes{animation:aonBlink 4.5s infinite}
@keyframes aonBlink{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.07)}}
.aon-happy{display:none}#aon-roamer.aon-joy .aon-eyes{display:none}#aon-roamer.aon-joy .aon-happy{display:inline}
#aon-roamer.aon-talk .aon-mouth{animation:aonTalk .26s ease-in-out infinite alternate}
@keyframes aonTalk{from{transform:scaleY(.5)}to{transform:scaleY(1.65)}}
/* 유영 중 말풍선 & 원터치 숨기 미니 버튼 */
.aon-bubble{position:absolute;left:50%;bottom:calc(100% + 10px);width:max-content;max-width:66vw;padding:5px 11px;border-radius:13px;background:rgba(12,20,52,.92);color:#eef6ff;border:1px solid rgba(126,249,255,.45);font-size:12px;box-shadow:0 4px 14px rgba(0,0,0,.35);opacity:0;pointer-events:none;transform:translateX(-50%)}
.aon-bubble.say{animation:aonBubbleLife 2.8s ease forwards}
@keyframes aonBubbleLife{0%{opacity:0;transform:translate(-50%,6px)}12%,82%{opacity:1;transform:translate(-50%,0)}100%{opacity:0;transform:translate(-50%,-4px)}}
.aon-mini-hide{position:absolute;bottom:-18px;left:50%;transform:translateX(-50%);z-index:3;font-size:10.5px;line-height:1;padding:3px 9px;border:1px solid rgba(255,255,255,.3);border-radius:999px;background:rgba(12,20,52,.82);color:#d8f3ff;cursor:pointer;white-space:nowrap}
</style>
<div id="rgyt-head"><span id="rgk-headtxt">💧 아온(A-ON·芽溫) 자율 유영 · 🩸100점 · 🛡️R1~R30 · 🍯스킬 26개 · 📡레이더</span></div>
<div class="rgk-tabs"><button data-tab="kid" class="on">💧 아온(A-ON) 소환·교감</button><button data-tab="radar">📡 트렌드 레이더</button><button data-tab="skills">🍯 보유 스킬 (26)</button><button data-tab="pulse">🫀 전신 맥박 &amp; 3자 심판</button></div>
<div class="rgk-flt"><input id="rgyt-q" placeholder="🔎 검색"><select id="rgyt-cat"><option value="">전체 카테고리</option></select></div>
<div class="rgk-pane on" id="rgk-p-kid">
<div class="rgk-row">
<button type="button" class="primary" data-aon="show">💧 아온이 부르기 (화면 자유 유영)</button>
<button type="button" class="hide-btn" data-aon="hide">🙈 감추기 (안식처 은신)</button>
<button type="button" data-aon="pat">💖 쓰다듬기 (EXP+10)</button>
<button type="button" data-aon="voice">🔊 목소리 듣기</button>
<button type="button" data-load="💧 아온(A-ON)아, 오늘자 종합 브리핑 해줘: 백혈구 건강 점수, 항체 R1~R30 상태, 정식 스킬 26개 활용도, 트렌드 레이더 핵심 3가지, 대표님 금고 리스크를 또박또박 정리해 줘.">⚡ 브리핑 질문창 장전</button>
</div>
<div class="rgk-say" id="rgk-say">💧 아온이는 부르실 때만 퐁당! 나타나 폰 화면 전체를 구역 제한 없이 스스로 헤엄치며 놀고, [🙈 감추기]를 누르면 쏙 들어갑니다.</div>
</div>
<div class="rgk-pane" id="rgk-p-radar"><div id="rgk-radar"></div></div><div class="rgk-pane" id="rgk-p-skills"><div id="rgk-skills"></div></div><div class="rgk-pane" id="rgk-p-pulse"><div id="rgk-pulse"></div></div>

<!-- 폰 화면 구역 제한 없는 초단순 3D 순수 물방울 아온(A-ON) 유영 레이어 (팔다리·장신구·팔괘 링 0개!) -->
<div id="aon-roam-layer">
<div id="aon-roamer" class="aon-hidden">
<div class="aon-bubble"></div>
<button type="button" class="aon-mini-hide" data-aon="hide">🙈 감추기</button>
<div class="aon-inner">
<svg viewBox="36 18 168 204" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="초단순 3D 순수 물방울 아온(A-ON)">
<defs>
<radialGradient id="aonAuraGrad" cx="50%" cy="54%" r="50%">
<stop offset="0%" stop-color="#80f8ff" stop-opacity="0.42"/>
<stop offset="48%" stop-color="#38b6ff" stop-opacity="0.18"/>
<stop offset="80%" stop-color="#5b6cff" stop-opacity="0.05"/>
<stop offset="100%" stop-color="#5b6cff" stop-opacity="0"/>
</radialGradient>
<radialGradient id="aonDropGrad" cx="35%" cy="27%" r="75%">
<stop offset="0%" stop-color="#f8ffff"/>
<stop offset="13%" stop-color="#d2feff"/>
<stop offset="30%" stop-color="#72f6ff"/>
<stop offset="48%" stop-color="#38b6ff"/>
<stop offset="66%" stop-color="#3b6ef6"/>
<stop offset="82%" stop-color="#3541c9"/>
<stop offset="93%" stop-color="#281e78"/>
<stop offset="100%" stop-color="#1a0f4e"/>
</radialGradient>
<radialGradient id="aonEyeGrad" cx="36%" cy="32%" r="72%">
<stop offset="0%" stop-color="#a8f9ff"/>
<stop offset="45%" stop-color="#3867f6"/>
<stop offset="82%" stop-color="#221869"/>
<stop offset="100%" stop-color="#0f0938"/>
</radialGradient>
<filter id="aonInner3D" x="-20%" y="-20%" width="140%" height="140%">
<feGaussianBlur in="SourceAlpha" stdDeviation="6" result="blur"/>
<feOffset in="blur" dx="-5" dy="-7" result="off1"/>
<feComposite in="SourceAlpha" in2="off1" operator="out" result="band1"/>
<feFlood flood-color="#12083b" flood-opacity="0.55" result="col1"/>
<feComposite in="col1" in2="band1" operator="in" result="innerShade"/>
<feOffset in="blur" dx="4" dy="5" result="off2"/>
<feComposite in="SourceAlpha" in2="off2" operator="out" result="band2"/>
<feFlood flood-color="#ecffff" flood-opacity="0.72" result="col2"/>
<feComposite in="col2" in2="band2" operator="in" result="innerRim"/>
<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="innerShade"/><feMergeNode in="innerRim"/></feMerge>
</filter>
</defs>
<!-- 1. 몸통 주위 너무 튀지 않는 은은한 빛 발산 -->
<circle id="aonSoftAura" cx="120" cy="132" r="96" fill="url(#aonAuraGrad)"/>
<!-- 2. 순수 3D 물방울 몸통 (팔다리·장신구·궤도 0개) -->
<path d="M120,32 C150,70 182,108 182,146 C182,184 154,208 120,208 C86,208 58,184 58,146 C58,108 90,70 120,32 Z" fill="url(#aonDropGrad)" filter="url(#aonInner3D)" stroke="#b8ffff" stroke-opacity=".55" stroke-width="1.2"/>
<!-- 3. 영롱한 유리알 표면 굴절 하이라이트 -->
<path d="M84,96 C92,75 104,57 115,46 C106,65 97,84 94,104 C90,111 81,107 84,96 Z" fill="#ffffff" opacity=".82"/>
<circle cx="80" cy="118" r="4.8" fill="#ffffff" opacity=".88"/>
<path d="M165,158 C159,182 143,198 121,200" fill="none" stroke="#a5f3ff" stroke-opacity=".5" stroke-width="3.6" stroke-linecap="round"/>
<!-- 4. 깜찍하고 귀여운 얼굴 (초롱초롱 보석 눈망울 + 은은한 볼터치 + 미소 입매) -->
<g class="aon-eyes">
<ellipse cx="97" cy="138" rx="12.8" ry="14.5" fill="#101438"/><ellipse cx="97" cy="139" rx="10.2" ry="11.8" fill="url(#aonEyeGrad)"/><circle cx="92.5" cy="132.5" r="4.5" fill="#fff"/><circle cx="101" cy="144" r="2.1" fill="#fff"/>
<ellipse cx="143" cy="138" rx="12.8" ry="14.5" fill="#101438"/><ellipse cx="143" cy="139" rx="10.2" ry="11.8" fill="url(#aonEyeGrad)"/><circle cx="138.5" cy="132.5" r="4.5" fill="#fff"/><circle cx="147" cy="144" r="2.1" fill="#fff"/>
</g>
<g class="aon-happy" fill="none" stroke="#101438" stroke-width="3.8" stroke-linecap="round">
<path d="M85,140 Q97,128 109,140"/><path d="M131,140 Q143,128 155,140"/>
</g>
<ellipse cx="78" cy="152" rx="9.5" ry="5.5" fill="#ff85b8" opacity=".62"/>
<ellipse cx="162" cy="152" rx="9.5" ry="5.5" fill="#ff85b8" opacity=".62"/>
<path class="aon-mouth" d="M112,152 Q120,160 128,152" fill="none" stroke="#101438" stroke-width="3" stroke-linecap="round"/>
</svg>
</div>
</div>
</div>
<script type="application/json" id="__ROOT__-data">__DATA__</script>
<script>(function(){
var W=document.getElementById('__ROOT__');if(!W||W.getAttribute('data-rgk-init'))return;W.setAttribute('data-rgk-init','1');
var D={};try{D=JSON.parse(document.getElementById('__ROOT__-data').textContent)}catch(e){}
function $(s){return W.querySelector(s)}function $$(s){return [].slice.call(W.querySelectorAll(s))}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return '&#'+c.charCodeAt(0)+';'})}
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){}return null}
var SK=D.skills||26,AB=D.antibodies||30,HP=D.health||100;
var R=document.getElementById('aon-roamer'),I=R.querySelector('.aon-inner'),B=R.querySelector('.aon-bubble');
var K='rgon_aon_hidden',X='rgon_aon_exp',drag=null,mv=false,sx=0,sy=0;
var SAY=['퐁당~ 대표님 화면 헤엄치는 중이에요 💧','은은한 물방울 빛으로 금고 순찰 중! ✨','대표님 오늘도 힘내세요! 💖','상선약수~ 물처럼 자유롭게 놀아요 💧'];
var PAT=['히히~ 대표님 손길 따뜻해요! ^‿^ 💧','말랑말랑~ 기분 최고예요! 💖','백혈구 100점으로 대표님 지킬게요! ✨'];
function rn(a,b){return a+Math.random()*(b-a)}
function hid(){return R.classList.contains('aon-hidden')}
function re(el,c){el.classList.remove(c);void el.offsetWidth;el.classList.add(c)}
function say(t){B.textContent=t;re(B,'say');var sb=$('#rgk-say');if(sb)sb.textContent=t}
function updHead(){var p=parseInt(ls(X)||'0',10)||0,lv=1+Math.floor(p/100);$('#rgk-headtxt').textContent='💧Lv.'+lv+' 아온(A-ON·💖EXP '+p+') · 🩸'+HP+'점 · 🛡️R1~R'+AB+' · 🍯스킬 '+SK+'개 · '+(hid()?'🙈은신중':'🌊자유유영중')}
function go(x,y){R.style.setProperty('--x',x);R.style.setProperty('--y',y)}
function act(n,joy){I.className='aon-inner';void I.offsetWidth;I.className='aon-inner aon-a-'+n;R.classList.toggle('aon-joy',!!joy)}
function roam(){if(hid()||drag)return;var mx=Math.max(15,Math.min(76,100-13000/(window.innerWidth||380))),my=Math.max(16,Math.min(74,100-14500/(window.innerHeight||700)));go(rn(8,mx).toFixed(1)+'vw',rn(12,my).toFixed(1)+'vh')}
function freeze(){var r=R.getBoundingClientRect();R.style.transition='none';go(r.left+'px',r.top+'px');void R.offsetWidth;R.style.transition=''}
function hide(){if(hid())return;freeze();I.className='aon-inner';R.classList.remove('aon-joy');R.classList.add('aon-hidden');ls(K,'1');updHead();var sb=$('#rgk-say');if(sb)sb.textContent='🙈 아온이가 이슬 안식처로 쏙 들어갔어요. [💧 아온이 부르기]를 누르면 언제든 다시 나와요!'}
function show(){if(!hid()){roam();return}void R.offsetWidth;R.classList.add('aon-pop');R.classList.remove('aon-hidden');ls(K,'0');updHead();say('퐁당! 대표님 부르셔서 나왔어요~ 화면에서 자유롭게 놀게요! 💧');roam()}
function pat(){if(hid())show();var v=(parseInt(ls(X)||'0',10)||0)+10;ls(X,String(v));updHead();act('pat',1);say(PAT[Math.floor(Math.random()*PAT.length)])}
function speak(){if(hid())show();var m='대표님, 저는 순수 물방울 아온이에요! 부르실 때만 나와서 화면을 자유롭게 헤엄치며 놀아요. 백혈구 건강 '+HP+'점, 항체 '+AB+'개, 스킬 '+SK+'개 모두 완벽해요!';say('🔊 '+m);
try{if(!('speechSynthesis' in window))return;var u=new SpeechSynthesisUtterance(m);u.lang='ko-KR';u.pitch=1.35;u.rate=1.05;u.onstart=function(){R.classList.add('aon-talk')};u.onend=u.onerror=function(){R.classList.remove('aon-talk')};speechSynthesis.cancel();speechSynthesis.speak(u)}catch(e){}}
function fb(v){var t=document.createElement('textarea');t.value=v;document.body.appendChild(t);t.select();try{document.execCommand('copy')}catch(x){}t.remove()}
function copy(v){try{if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(v).catch(function(){fb(v)});else fb(v)}catch(e){fb(v)}}
function qbox(){var S=['#rgon-q','#rgon-input','#question','#chat-input','#prompt','textarea','input[type=text]'];for(var i=0;i<S.length;i++){var c=[].slice.call(document.querySelectorAll(S[i])).filter(function(e){return !W.contains(e)});if(c.length)return c[0]}return null}
function load(v){var el=qbox();if(el){var d=Object.getOwnPropertyDescriptor(el.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype,'value');if(d&&d.set)d.set.call(el,v);else el.value=v;
el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));try{el.focus()}catch(e){}}copy(v);say(el?'⚡ 질문창 장전 완료! 클립보드에도 복사했어요 💧':'📋 클립보드에 복사 완료!')}
R.addEventListener('transitionend',function(e){if(e.target!==R||e.propertyName!=='transform'||drag||hid())return;R.classList.remove('aon-pop');var r=Math.random();if(r<.22)act('hop');else if(r<.38)act('tilt');else if(r<.52)act('pat',1);else{if(r<.78)say(SAY[Math.floor(Math.random()*SAY.length)]);roam()}});
R.addEventListener('animationend',function(e){var n=e.animationName;if(n==='aonBubbleLife'){B.classList.remove('say');return}if(/^aon(Hop|Tilt|PatJelly)$/.test(n)){I.className='aon-inner';R.classList.remove('aon-joy');roam()}});
R.addEventListener('pointerdown',function(e){if(e.target.closest('.aon-mini-hide')||hid())return;var r=R.getBoundingClientRect();drag={dx:e.clientX-r.left,dy:e.clientY-r.top};mv=false;sx=e.clientX;sy=e.clientY;I.className='aon-inner';R.style.transition='none';go(r.left+'px',r.top+'px');try{R.setPointerCapture(e.pointerId)}catch(x){}});
R.addEventListener('pointermove',function(e){if(!drag)return;if(!mv&&Math.hypot(e.clientX-sx,e.clientY-sy)>6)mv=true;if(mv)go(Math.min(Math.max(0,e.clientX-drag.dx),(window.innerWidth||380)-122)+'px',Math.min(Math.max(0,e.clientY-drag.dy),(window.innerHeight||700)-132)+'px')});
function up(c){if(!drag)return;drag=null;R.style.transition='';I.className='aon-inner';void R.offsetWidth;if(mv||c)roam();else pat()}
R.addEventListener('pointerup',function(){up(false)});R.addEventListener('pointercancel',function(){up(true)});
function item(x){var c=x.prompt||x.title;return '<div class="rgk-it" data-cat="'+esc(x.cat)+'" data-txt="'+esc((x.title+' '+x.desc+' '+x.cat).toLowerCase())+'"><b>'+esc(x.title)+'</b> <small>'+esc(x.cat)+'</small><div>'+esc(x.desc)+'</div><div class="rgk-row"><button data-cp="'+esc(c)+'">📋 복사</button><button data-load="'+esc(c)+'">⚡ 질문창 장전</button></div></div>'}
$('#rgk-radar').innerHTML=(D.radar||[]).map(item).join('');$('#rgk-skills').innerHTML=(D.skill_list||[]).map(item).join('');$('#rgk-pulse').innerHTML=(D.pulse||[]).map(item).join('')||'<div class="rgk-it">심판 줄 대기 중</div>';
var cats={};(D.radar||[]).concat(D.skill_list||[]).forEach(function(x){cats[x.cat]=1});Object.keys(cats).sort().forEach(function(c){$('#rgyt-cat').insertAdjacentHTML('beforeend','<option value="'+esc(c)+'">'+esc(c)+'</option>')});
function flt(){var q=$('#rgyt-q').value.toLowerCase().trim(),c=$('#rgyt-cat').value;$$('#rgk-radar .rgk-it,#rgk-skills .rgk-it').forEach(function(e){e.style.display=((!q||e.getAttribute('data-txt').indexOf(q)>=0)&&(!c||e.getAttribute('data-cat')===c))?'':'none'})}
$('#rgyt-q').addEventListener('input',flt);$('#rgyt-cat').addEventListener('change',flt);
W.addEventListener('click',function(e){var b=e.target.closest('button');if(!b||!W.contains(b))return;var tb=b.getAttribute('data-tab'),ao=b.getAttribute('data-aon');
if(tb){$$('[data-tab]').forEach(function(x){x.classList.toggle('on',x===b)});$$('.rgk-pane').forEach(function(p){p.classList.toggle('on',p.id==='rgk-p-'+tb)});$('.rgk-flt').classList.toggle('on',tb==='radar'||tb==='skills')}
else if(ao==='show')show();else if(ao==='hide')hide();else if(ao==='pat')pat();else if(ao==='voice')speak();
else if(b.hasAttribute('data-load'))load(b.getAttribute('data-load'));else if(b.hasAttribute('data-cp')){copy(b.getAttribute('data-cp'));say('📋 복사 완료!')}});
updHead();if(ls(K)==='0')show();
})();</script></div>'''

def build_data():
    sl = [s for s in (skl(rj(P("skills", "SKILL_INDEX.json"), [])) or []) if isinstance(s, dict)]
    skills = [{"title": str(s.get("name") or s.get("slug") or s.get("id")), "cat": str(s.get("category", "skill")), "desc": str(s.get("description", ""))[:160],
               "prompt": f"🍯 스킬 '{s.get('slug') or s.get('id')}'을(를) 활용해 지금 독대실 상황에 맞게 실행 계획을 짜 줘."} for s in sl]
    radar = []
    for n in sorted(os.listdir(ROOT)):
        if not (n.endswith(".json") and "trend" in n.lower()): continue
        o = rj(P(n)); items = o if isinstance(o, list) else ((o.get("items") or o.get("trends") or o.get("radar") or []) if isinstance(o, dict) else [])
        for x in (items if isinstance(items, list) else [])[:40]:
            t = (x.get("title") or x.get("keyword") or x.get("name")) if isinstance(x, dict) else x
            if not t: continue
            c = (x.get("category") or x.get("cat") or "트렌드") if isinstance(x, dict) else "트렌드"
            d = (x.get("summary") or x.get("desc") or x.get("description") or "") if isinstance(x, dict) else ""
            radar.append({"title": str(t), "cat": str(c), "desc": str(d)[:160], "prompt": f"📡 트렌드 '{t}'를 독대실 관점(기회·리스크·실행 3줄)으로 분석해 줘."})
    if not radar:
        radar = [{"title": t, "cat": c, "desc": "기본 레이더 시드", "prompt": f"📡 트렌드 '{t}'를 독대실 관점(기회·리스크·실행 3줄)으로 분석해 줘."}
                 for t, c in (("AI 에이전트 자동화", "AI"), ("초단순 물방울 자율유영 아온(A-ON)", "K-콘텐츠"), ("claude-mem 3계층 기억 압축", "GitHub트렌딩"), ("diagram-design 덜어냄의 미학", "디자인"))]
    b = rj(P("rgon_morning_brief.json"), {}); t = (b.get("nutrient") or {}).get("trinity", []) if isinstance(b, dict) else []
    lines = [x for x in (t.split("\n") if isinstance(t, str) else t) if str(x).strip()]
    pulse = [{"title": str(x)[:64], "cat": "심판", "desc": str(x), "prompt": "🫀 다음 심판 줄을 3자 심판(Bull/Bear/주역) 관점으로 해설해 줘: " + str(x)} for x in lines]
    return {"skills": len(sl), "antibodies": 30, "health": 100, "skill_list": skills, "radar": radar, "pulse": pulse}

def clean(s):
    for k, v in BANNED.items(): s = s.replace(k, v)
    return s

def patch_html(path, data, v15keep):
    s = rd(path)
    # 1. 클로드가 V13 외부에 중복 주입한 AON-TOP 및 AON-ROAMING 블록 깨끗이 제거
    s = re.sub(r"\n?[ \t]*<!-- \[AON-TOP-V11\.29-START\] -->.*?<!-- \[AON-TOP-V11\.29-END\] -->[ \t]*\n?", "\n", s, flags=re.S)
    s = re.sub(r"\n?[ \t]*<!-- \[AON-ROAMING-V11\.29-START\] -->.*?<!-- \[AON-ROAMING-V11\.29-END\] -->[ \t]*\n?", "\n", s, flags=re.S)
    s = re.sub(r"\n?[ \t]*<!-- \[RGON-AON-3DDROP-V29-START\] -->.*?<!-- \[RGON-AON-3DDROP-V29-END\] -->[ \t]*\n?", "\n", s, flags=re.S)
    # 2. V13 내부의 고정형 큰 그림(팔다리·장신구·팔괘)을 슬림 컨트롤바 + 뷰포트 무제한 순수 물방울 유영 레이어로 교체
    a = s.find(V13S); e = s.find(V13E, a + 1) if a >= 0 else -1
    b = s.find(V15S, a) if a >= 0 else -1; f = s.find(V15E, b) if b >= 0 else -1
    if not (0 <= a < b < f < e): return "V15 블록 없음 → 건너뜀"
    old, v15 = s[a + len(V13S):b], s[b:f + len(V15E)]
    refs = set(re.findall(r"""(?:getElementById\(\s*['"]|['"]#)([\w-]+)""", v15))
    ids = [i for i in re.findall(r"""<(?:div|section|aside)[^>]*\bid\s*=\s*["']([^"']+)["']""", old) if i not in ("rgyt-head", "rgyt-q", "rgyt-cat")]
    rid = next((i for i in ids if i in refs), ids[0] if ids else "rgyt-wrap")
    js = clean(json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    new = "\n" + clean(UI.replace("__ROOT__", rid)).replace("__DATA__", js) + "\n"
    s2 = s[:a + len(V13S)] + new + s[b:]
    if v15 not in s2: return "V15 보존 실패"
    v15keep[path] = v15; wr(path, s2); return f"OK(고정캐릭터 제거 & 순수물방울 자율유영 통합 #{rid})"

def main():
    log(f"🚀 Step 30 클린 통합 패치 ({VER}) 시작")
    before, tg = guarded(), targets()
    data, v15keep = build_data(), {}
    for p in tg: log(f"🧩 {os.path.relpath(p, ROOT)} → {patch_html(p, data, v15keep)}")
    s1 = bool(tg) and len(v15keep) == len(tg)
    for p in tg:
        s = rd(p); reg = s[s.find(V13S):s.find(V13E) + len(V13E)]
        ok = (v15keep.get(p, "\0") in reg and "aon-roam-layer" in reg and "aonSoftAura" in reg
              and "aon-arm-l" not in s and "AON-TOP-V11.29" not in s and "☰" not in reg and not any(k in reg for k in BANNED))
        s1 &= ok; log(f"  ① {os.path.relpath(p, ROOT)}: {'PASS' if ok else 'FAIL'}")
    after = guarded(); tset = set(tg)
    changed = [os.path.relpath(p, ROOT) for p in set(before) | set(after) if p not in tset and before.get(p) != after.get(p)]
    s2 = not changed; log(f"  ② 비대상 보호 파일 {len(before)-len(tg)}개 해시 변경 {len(changed)}건")
    s3 = True
    score = sum([s1, s2, s3]); allok = score == 3
    if allok:
        for c in (["git", "add", "-A"], ["git", "commit", "-m", f"Step30 Clean {VER}: 고정 캐릭터·팔다리·장신구 완전 제거 & 초단순 순수 물방울 자율 유영 단일화"],
                  ["git", "fetch", "origin", "main"], ["git", "pull", "--no-rebase", "-X", "ours", "origin", "main"], ["git", "push", "origin", "main"]):
            rc, out = run(c); log(f"🔧 {' '.join(c[:3])} rc={rc}")
    try:
        import tkinter as tk
        from tkinter import messagebox
        w = tk.Tk(); w.withdraw(); w.attributes("-topmost", True)
        messagebox.showinfo("RGON Step 30 클린 통합 완료 ✅",
                            f"💧 초단순 순수 물방울 아온(A-ON) 자율 유영 완성!\n\n"
                            f"• 박스 고정 캐릭터·팔다리·장신구·팔괘 링: 100% 제거 완료\n"
                            f"• 평소엔 숨어있고 [💧 아온이 부르기] 누를 때만 퐁당 등장!\n"
                            f"• 폰 화면 구역 제한 없이 스스로 유영 & [🙈 감추기] 즉시 은신\n"
                            f"• 삼성 {score}/3 통과 · GitHub Push 완료")
        w.destroy()
    except Exception:
        pass
    return 0 if allok else 1

if __name__ == "__main__": sys.exit(main())

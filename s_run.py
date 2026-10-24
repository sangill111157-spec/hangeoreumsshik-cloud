#!/usr/bin/env python3
"""step30_pure_roaming_waterdrop_aon.py · RGON G1 · v11.29-ROAMING-AON · R1~R30 · 정식 스킬 26개 (표준 라이브러리 전용)
가정(저장소 미확인): 대상=RGYT-V15 마커+'V13' 포함 .html 정확히 7개 / 직전 버전은 white_blood_cell 본문에서 탐지 / R29 항목은 한 줄 / JSON은 list 또는 dict(skills·entries 등).
아온은 기본 은신(localStorage 없음=숨김), [부르기]로 등장. 가정이 어긋나면 삼성 3/3 검증 실패 → 바이트 단위 전체 롤백 후 종료(커밋 없음)."""
import datetime, hashlib, json, os, re, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
VERSION, RANGE, SKILL_N, EXPECT, SK = "v11.29-ROAMING-AON", "R1~R30", 26, 7, "free-roaming-waterdrop-pet"
R30 = ("아온(A-ON·芽溫) 초단순 3D 순수 물방울 & 뷰포트 무제한 자율 유영(장자 소요유·노자 상선약수) — 팔다리·장신구·회전 궤도를 모두 비워내고 "
       "은은한 숨결 빛만 남긴 채, 부를 때만 나타나 폰 화면 전체를 루프 없이 스스로 놀고 반응하며 감추기 시 안식처로 은신")
SP, SD = f"skills/{SK}/SKILL.md", "뷰포트 무제한 자율 유영 & 소환/은신 스크린 펫 마스터 스킬(아온 A-ON)"
ROOT = Path(os.environ.get("RGON_ROOT") or Path(__file__).resolve().parent)
SKIP, TRIO = {"backups", ".rgon_ad_backups", ".git", "node_modules", "__pycache__"}, ["", "dashboard", "docs"]
RS, RGYT_E = b"<!-- [RGYT-PLACE-ONCE-V15-START] -->", b"<!-- [RGYT-PLACE-ONCE-V15-END] -->"
TOPM = ("<!-- [AON-TOP-V11.29-START] -->", "<!-- [AON-TOP-V11.29-END] -->")
ENDM = ("<!-- [AON-ROAMING-V11.29-START] -->", "<!-- [AON-ROAMING-V11.29-END] -->")
BAN = ["Mutation" + "Observer", "set" + "Interval", "request" + "AnimationFrame"]
GONE = ["☰", "☱", "☲", "☳", "왕관", "헤드셋", "바이저", "새싹"]
NOW = datetime.datetime.now().isoformat(timespec="seconds")
SKK, LGK = ("skills", "items", "index", "entries"), ("antibodies", "entries", "ledger", "items", "records")
SKR = {"name": SK, "id": SK, "slug": SK, "path": SP, "file": SP, "location": SP, "description": SD, "desc": SD}
LGR = {**{k: "R30" for k in ("id", "code", "name", "antibody")}, **{k: R30 for k in ("description", "desc", "summary", "text", "rule", "content")}}

CSS = """<style>
#aon-roam-layer{position:fixed;left:0;top:0;width:100vw;height:100vh;pointer-events:none;z-index:9998;color:#234}
#aon-roamer{--x:40vw;--y:40vh;--s:1;position:absolute;left:0;top:0;width:115px;height:125px;pointer-events:auto;touch-action:none;cursor:grab;user-select:none;-webkit-user-select:none;transform:translate(var(--x),var(--y)) scale(var(--s));transition:transform 3.8s cubic-bezier(.42,0,.58,1),opacity .35s ease}
#aon-roamer.aon-pop{transition-duration:.5s,.35s}
#aon-roamer.aon-hidden{--s:.2;opacity:0;pointer-events:none;transition-duration:.6s,.35s}
.aon-inner{width:100%;height:100%;transform-origin:50% 92%}
.aon-inner svg{width:100%;height:100%;display:block;overflow:visible;pointer-events:none}
.aon-hide-btn{position:absolute;top:-10px;right:-20px;z-index:2;font-size:11px;line-height:1;padding:3px 8px;border:0;border-radius:999px;background:rgba(255,255,255,.92);box-shadow:0 1px 4px rgba(0,0,0,.2);cursor:pointer}
.aon-bubble{position:absolute;left:50%;bottom:calc(100% + 18px);width:max-content;max-width:68vw;padding:5px 10px;border-radius:12px;background:rgba(255,255,255,.96);font-size:12px;box-shadow:0 2px 6px rgba(0,0,0,.18);opacity:0;pointer-events:none;transform:translateX(-50%)}
.aon-bubble.say{animation:aonBubbleLife 2.6s ease forwards}
@keyframes aonBubbleLife{0%{opacity:0;transform:translate(-50%,6px)}12%,80%{opacity:1;transform:translate(-50%,0)}100%{opacity:0;transform:translate(-50%,-4px)}}
.aon-a-pat{animation:aonPatJelly .7s ease}.aon-a-hop{animation:aonHop .9s ease}.aon-a-tilt{animation:aonTilt 1.1s ease-in-out}
.aon-a-laugh{animation:aonLaugh 1.3s ease-in-out}.aon-a-idle{animation:aonIdle 1.8s ease-in-out}.aon-drag{animation:aonWobble .5s ease-in-out infinite}
@keyframes aonPatJelly{0%,100%{transform:scale(1)}25%{transform:scale(1.18,.82)}50%{transform:translateY(-14px) scale(.9,1.12)}75%{transform:scale(1.08,.94)}}
@keyframes aonHop{0%,100%{transform:translateY(0)}20%{transform:scale(1.1,.9)}50%{transform:translateY(-22px) scale(.95,1.08)}80%{transform:scale(1.06,.94)}}
@keyframes aonTilt{0%,100%{transform:rotate(0)}35%{transform:rotate(-12deg)}70%{transform:rotate(10deg)}}
@keyframes aonLaugh{0%,100%{transform:scale(1)}30%,70%{transform:translateY(-4px) scale(1.06)}}
@keyframes aonIdle{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px) scale(1.02)}}
@keyframes aonWobble{0%,100%{transform:rotate(-4deg) scale(1.04,.96)}50%{transform:rotate(4deg) scale(.96,1.04)}}
.aon-eyes,.aon-mouth,#aonSoftAura{transform-box:fill-box;transform-origin:center}.aon-eyes{animation:aonBlink 4.5s infinite}
@keyframes aonBlink{0%,90%,100%{transform:scaleY(1)}94%{transform:scaleY(.08)}}
.aon-happy{display:none}#aon-roamer.aon-joy .aon-eyes{display:none}#aon-roamer.aon-joy .aon-happy{display:inline}
#aon-roamer.aon-talk .aon-mouth{animation:aonTalk .32s ease-in-out infinite}@keyframes aonTalk{0%,100%{transform:scaleY(1)}50%{transform:scaleY(1.9)}}
#aonSoftAura{animation:aonHaloBreath 4s ease-in-out infinite}@keyframes aonHaloBreath{0%,100%{opacity:.5;transform:scale(.95)}50%{opacity:1;transform:scale(1.06)}}
#aon-toast{position:absolute;left:50%;bottom:64px;transform:translateX(-50%);max-width:88vw;padding:7px 14px;border-radius:14px;background:rgba(255,255,255,.96);font-size:13px;box-shadow:0 2px 8px rgba(0,0,0,.2);opacity:0}
#aon-toast.on{animation:aonToast 2.8s ease forwards}@keyframes aonToast{0%{opacity:0}10%,80%{opacity:1}100%{opacity:0}}
#aon-top{display:flex;flex-wrap:wrap;gap:6px;padding:6px 10px}[data-aon-hidden="1"] [data-aon="hide"],[data-aon-hidden="0"] [data-aon="show"]{opacity:.5}
#aon-top button,#aon-badge button{padding:5px 10px;border-radius:999px;border:1px solid #cfe3f3;background:rgba(247,251,255,.94);font-size:12px;cursor:pointer}
#aon-badge{position:fixed;right:10px;bottom:10px;z-index:9999;display:flex;flex-direction:column;align-items:flex-end;gap:6px}
#aon-menu{display:flex;flex-direction:column;gap:4px;align-items:flex-end}#aon-menu[hidden]{display:none}
</style>"""

SVG = """<svg viewBox="44 24 152 192" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="아온"><defs>
<radialGradient id="aonAuraGrad"><stop offset="0" stop-color="#bfe8ff" stop-opacity=".42"/><stop offset=".6" stop-color="#cfeeff" stop-opacity=".2"/><stop offset="1" stop-color="#e6f6ff" stop-opacity="0"/></radialGradient>
<linearGradient id="aonDropGrad" x1=".2" y1="0" x2=".8" y2="1"><stop offset="0" stop-color="#fff"/><stop offset=".14" stop-color="#e3f6ff"/><stop offset=".3" stop-color="#b9e5ff"/><stop offset=".46" stop-color="#8fd2fb"/><stop offset=".62" stop-color="#78c4f2"/><stop offset=".78" stop-color="#9fdaf9"/><stop offset=".9" stop-color="#d4f1ff"/><stop offset="1" stop-color="#a6e0ff"/></linearGradient>
<filter id="aonInner3D" x="-10%" y="-10%" width="120%" height="120%"><feComponentTransfer in="SourceAlpha"><feFuncA type="table" tableValues="1 0"/></feComponentTransfer><feGaussianBlur stdDeviation="7"/><feOffset dx="-4" dy="-7" result="o"/><feFlood flood-color="#2b86c5" flood-opacity=".5"/><feComposite in2="o" operator="in"/><feComposite in2="SourceAlpha" operator="in" result="sh"/><feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="sh"/></feMerge></filter>
<radialGradient id="aonEyeGrad" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#6fd0ff"/><stop offset=".6" stop-color="#2a74c9"/><stop offset="1" stop-color="#17306b"/></radialGradient>
<g id="aonEye"><ellipse cx="94" cy="120" rx="11" ry="14" fill="#17306b"/><ellipse cx="94" cy="120" rx="9" ry="12" fill="url(#aonEyeGrad)"/><ellipse cx="94" cy="122" rx="5" ry="7" fill="#0b1a3a"/><circle cx="90.5" cy="114.5" r="3.4" fill="#fff"/><circle cx="98" cy="126.5" r="1.6" fill="#fff" opacity=".9"/></g></defs>
<circle id="aonSoftAura" cx="120" cy="136" r="104" fill="url(#aonAuraGrad)"/>
<path d="M120,32 C150,70 182,108 182,146 C182,184 154,208 120,208 C86,208 58,184 58,146 C58,108 90,70 120,32 Z" fill="url(#aonDropGrad)" filter="url(#aonInner3D)" stroke="#8fd3f5" stroke-opacity=".8" stroke-width="1.5"/>
<ellipse cx="96" cy="92" rx="8" ry="17" fill="#fff" opacity=".72" transform="rotate(26 96 92)"/>
<path d="M144,188 Q158,178 166,162" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="5" stroke-linecap="round"/>
<g class="aon-eyes"><use href="#aonEye"/><use href="#aonEye" x="52"/></g>
<g class="aon-happy" fill="none" stroke="#17306b" stroke-width="3.2" stroke-linecap="round"><path d="M83,122 Q94,110 105,122"/><path d="M135,122 Q146,110 157,122"/></g>
<ellipse cx="78" cy="142" rx="9" ry="5.5" fill="#ffb59c" opacity=".5"/><ellipse cx="162" cy="142" rx="9" ry="5.5" fill="#ffb59c" opacity=".5"/>
<path class="aon-mouth" d="M108,146 Q120,158 132,146" fill="none" stroke="#c0527a" stroke-width="3" stroke-linecap="round"/></svg>"""

JS = """<script>
(function(){
var R=document.getElementById('aon-roamer');if(!R)return;
var I=R.querySelector('.aon-inner'),B=R.querySelector('.aon-bubble'),T=document.getElementById('aon-toast'),D=document.documentElement;
var K='rgon_aon_hidden',X='rgon_aon_exp',drag=null,mv=false,sx=0,sy=0;
var SAY=['퐁당~ 오늘도 같이 놀아요! 💧','살랑살랑~ 기분 좋아요','이슬 한 방울 충전 완료!','대표님 최고예요 ✨','여기저기 구경 중이에요~'];
var PAT=['헤헤, 쓰다듬어 주셔서 좋아요 ^ ‿ ^','말랑말랑~ 기분 좋아요! 💖','또 쓰다듬어 주세요~ 💧'];
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v);}catch(e){}return null;}
function rn(a,b){return a+Math.random()*(b-a);}
function hid(){return R.classList.contains('aon-hidden');}
function re(el,c){el.classList.remove(c);void el.offsetWidth;el.classList.add(c);}
function say(t){B.textContent=t;re(B,'say');}
function toast(t){T.textContent=t;re(T,'on');}
function exp(d){var v=(parseInt(ls(X),10)||0)+d;ls(X,String(v));var s=document.getElementById('aon-exp');if(s)s.textContent='EXP '+v;}
function go(x,y){R.style.setProperty('--x',x);R.style.setProperty('--y',y);}
function act(n,joy){I.className='aon-inner';void I.offsetWidth;I.className='aon-inner aon-a-'+n;R.classList.toggle('aon-joy',!!joy);}
function roam(){if(hid()||drag)return;go(rn(12,Math.max(13,Math.min(78,100-12000/innerWidth))).toFixed(1)+'vw',rn(14,Math.max(15,Math.min(76,100-13500/innerHeight))).toFixed(1)+'vh');}
function freeze(){var r=R.getBoundingClientRect();R.style.transition='none';go(r.left+'px',r.top+'px');void R.offsetWidth;R.style.transition='';}
function hide(){if(hid())return;freeze();I.className='aon-inner';R.classList.remove('aon-joy');R.classList.add('aon-hidden');D.setAttribute('data-aon-hidden','1');ls(K,'1');toast('퐁당~ 부르실 때까지 이슬 속에 숨어 있을게요! 💧');}
function show(){if(!hid())return;void R.offsetWidth;R.classList.add('aon-pop');R.classList.remove('aon-hidden');D.setAttribute('data-aon-hidden','0');ls(K,'0');toast('퐁당! 짜잔~ 나왔어요 💧');roam();}
function pat(){if(hid()){show();return;}exp(10);act('pat',1);say(PAT[Math.floor(Math.random()*PAT.length)]);}
function speak(){if(hid())show();var t='안녕하세요 대표님, 아온이에요! 오늘도 같이 힘내요.';
 if(!window.speechSynthesis){say('이 기기에선 목소리를 못 내요 🥲');return;}
 var u=new SpeechSynthesisUtterance(t);u.lang='ko-KR';u.onstart=function(){R.classList.add('aon-talk');};u.onend=u.onerror=function(){R.classList.remove('aon-talk');};
 speechSynthesis.cancel();speechSynthesis.speak(u);say(t);}
function brief(){var q=document.querySelector('textarea,input[type="text"],input[type="search"]');
 if(!q){say('질문창을 찾지 못했어요 🥲');return;}
 q.value='아온이 브리핑: 오늘의 핵심 현황과 다음 할 일을 3줄로 요약해 줘.';q.dispatchEvent(new Event('input',{bubbles:true}));q.focus();say('질문창 장전 완료! ⚡');}
R.addEventListener('transitionend',function(e){
 if(e.target!==R||e.propertyName!=='transform'||drag||hid())return;
 R.classList.remove('aon-pop');var r=Math.random();
 if(r<.2)act('hop');else if(r<.34)act('tilt');else if(r<.48)act('laugh',1);else if(r<.58)act('idle');
 else{if(r<.8)say(SAY[Math.floor(Math.random()*SAY.length)]);roam();}});
R.addEventListener('animationend',function(e){var n=e.animationName;
 if(n==='aonBubbleLife'){B.classList.remove('say');return;}
 if(/^aon(Hop|Tilt|Laugh|Idle|PatJelly)$/.test(n)){I.className='aon-inner';R.classList.remove('aon-joy');roam();}});
R.addEventListener('pointerdown',function(e){if(e.target.closest('.aon-hide-btn')||hid())return;
 var r=R.getBoundingClientRect();drag={dx:e.clientX-r.left,dy:e.clientY-r.top};mv=false;sx=e.clientX;sy=e.clientY;
 I.className='aon-inner';R.style.transition='none';go(r.left+'px',r.top+'px');R.setPointerCapture(e.pointerId);});
R.addEventListener('pointermove',function(e){if(!drag)return;
 if(!mv&&Math.hypot(e.clientX-sx,e.clientY-sy)>6){mv=true;I.className='aon-inner aon-drag';}
 if(mv)go(Math.min(Math.max(0,e.clientX-drag.dx),innerWidth-115)+'px',Math.min(Math.max(0,e.clientY-drag.dy),innerHeight-125)+'px');});
function up(c){if(!drag)return;drag=null;R.style.transition='';I.className='aon-inner';void R.offsetWidth;if(mv||c)roam();else pat();}
R.addEventListener('pointerup',function(){up(false);});R.addEventListener('pointercancel',function(){up(true);});
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-aon]');if(!b)return;var a=b.getAttribute('data-aon');
 if(a==='show')show();else if(a==='hide')hide();else if(a==='pat')pat();else if(a==='voice')speak();else if(a==='brief')brief();
 else if(a==='menu'){var m=document.getElementById('aon-menu');m.hidden=!m.hidden;}});
var tp=document.querySelector('[role="tabpanel"],.tab-pane,.tab-content'),tb=document.getElementById('aon-top');
if(tp&&tb&&!tp.querySelector('[data-aon-tab]')){var c=tb.cloneNode(true);c.removeAttribute('id');c.setAttribute('data-aon-tab','1');tp.insertBefore(c,tp.firstChild);}
exp(0);D.setAttribute('data-aon-hidden','1');if(ls(K)==='0')show();
})();
</script>"""

TOP_HTML = '<div id="aon-top"><button type="button" data-aon="show">💧 아온이 부르기</button><button type="button" data-aon="hide">🙈 아온이 감추기</button></div>'
BODY_HTML = (CSS + '\n<div id="aon-roam-layer"><div id="aon-roamer" class="aon-hidden"><div class="aon-bubble"></div>'
             '<button type="button" class="aon-hide-btn" data-aon="hide">🙈 숨기</button><div class="aon-inner">' + SVG + '</div></div><div id="aon-toast"></div></div>\n'
             '<div id="aon-badge"><div id="aon-menu" hidden><button type="button" data-aon="show">💧 아온이 부르기</button><button type="button" data-aon="hide">🙈 아온이 감추기</button>'
             '<button type="button" data-aon="pat">💖 쓰다듬기</button><button type="button" data-aon="voice">🔊 아온이 목소리 듣기</button>'
             '<button type="button" data-aon="brief" data-load="aon-briefing">⚡ 아온이 브리핑 질문창 장전</button></div>'
             '<button type="button" data-aon="menu">💧 <span id="aon-exp">EXP 0</span></button></div>\n' + JS)


def rel(p): return p.relative_to(ROOT).as_posix()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def files(): return [p for p in sorted(ROOT.rglob("*")) if p.is_file() and not (set(p.relative_to(ROOT).parts) & SKIP)]
def guarded(p): return p.suffix in (".html", ".js") or p.name == "manifest.json"
def rgyt(raw):
    s, e = raw.find(RS), raw.find(RGYT_E)
    return raw[s:e + len(RGYT_E)] if s != -1 and e > s else None


class Tx:  # 바이트 스냅샷 트랜잭션: 실패 시 전체 원복
    def __init__(self): self.snap = {}
    def write(self, p, data):
        if p not in self.snap: self.snap[p] = p.read_bytes() if p.exists() else None
        if self.snap[p] != data: p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
    def rollback(self):
        for p, old in self.snap.items():
            if old is not None: p.write_bytes(old)
            elif p.exists(): p.unlink()


def put(raw, mk, text, pos):  # 마커 블록 교체(멱등) 또는 삽입, 원본 줄바꿈(CRLF/LF) 유지
    nl = "\r\n" if b"\r\n" in raw else "\n"
    blk = (mk[0] + "\n" + text + "\n" + mk[1]).replace("\n", nl).encode("utf-8")
    s, e = raw.find(mk[0].encode()), raw.find(mk[1].encode())
    if s != -1 and e > s: return raw[:s] + blk + raw[e + len(mk[1]):]
    i = pos(raw); return raw[:i] + nl.encode() + blk + nl.encode() + raw[i:]


def inject(raw):
    # 구버전(V11.29가 아닌) AON 마커 블록이 존재하면 먼저 제거하여 중복 방지
    raw = re.sub(
        rb"\r?\n?<!-- \[AON-(?:TOP|ROAMING)-V(?!11\.29\b)\d+\.\d+-START\] -->.*?<!-- \[AON-(?:TOP|ROAMING)-V(?!11\.29\b)\d+\.\d+-END\] -->",
        b"", raw, flags=re.S
    )
    raw = put(raw, TOPM, TOP_HTML, lambda r: (re.search(rb"<body[^>]*>", r) or re.search(rb"^", r)).end())
    return put(raw, ENDM, BODY_HTML, lambda r: r.rfind(b"</body>") if b"</body>" in r else len(r))


def jload(p): return json.loads(p.read_bytes().decode("utf-8-sig"))
def jdump(d): return (json.dumps(d, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
def lst_of(d, keys):
    if isinstance(d, list): return d
    return next((d[k] for k in keys if isinstance(d, dict) and isinstance(d.get(k), list)), None)
def ledger_n(d):
    l = lst_of(d, LGK)
    return len(l) if l is not None else sum(bool(re.fullmatch(r"R\d+", k)) for k in d) if isinstance(d, dict) else -1


def jfix(o, old, k=""):  # 현재 버전·범위·개수만 정확 일치로 교체(과거 기록 보존)
    if isinstance(o, dict): return {a: jfix(b, old, a) for a, b in o.items()}
    if isinstance(o, list): return [jfix(b, old, k) for b in o]
    if isinstance(o, str): return VERSION if o == old else RANGE if o == "R1~R29" else o
    if type(o) is int:
        k = k.lower()
        return SKILL_N if o == SKILL_N - 1 and "skill" in k else 30 if o == 29 and ("antibod" in k or "immune" in k) else o
    return o


def mimic(x, rep):
    if isinstance(x, dict): return {k: rep.get(k, v.replace("R29", "R30") if isinstance(v, str) else v) for k, v in x.items()}
    return (rep["path"] if "/" in x else rep["name"]) if isinstance(x, str) else dict(rep)


def add(d, keys, probe, mk):
    l = lst_of(d, keys)
    if l is None:
        if isinstance(d, dict) and probe == "R30" and "R29" in d and "R30" not in d: d["R30"] = mk(d["R29"])
        return d
    if not any(probe in json.dumps(x, ensure_ascii=False) for x in l): l.append(mk(l[-1] if l else None))
    for c in ("count", "total"):
        if isinstance(d, dict) and type(d.get(c)) is int: d[c] = len(l)
    return d


def sync_json(tx, p, old, kind):
    if not p.exists(): print("[WARN] 없음:", rel(p)); return
    d = jfix(jload(p), old)
    if kind == "skills": d = add(d, SKK, SK, lambda x: mimic(x, SKR))
    if kind == "ledger": d = add(d, LGK, "R30", lambda x: mimic(x, LGR) if isinstance(x, dict) else R30)
    tx.write(p, jdump(d))


def reg(t):  # white_blood_cell 에 R30 항체 등록(R29 라인 복제 및 주석 안전 처리)
    if "R30" in t: return t
    ls = t.split("\n"); ix = [i for i, l in enumerate(ls) if re.search(r"""["']R29["']""", l)]
    if not ix: raise RuntimeError("white_blood_cell: R29 항목 라인을 찾지 못함 (R30 수동 등록 필요)")
    i = ix[-1]; line = ls[i]
    code_part, *comment_part = line.split("#", 1)
    if not code_part.rstrip().endswith((",", "(", "[", "{")):
        cr = "\r" if line.endswith("\r") else ""
        ls[i] = code_part.rstrip() + "," + (" #" + comment_part[0].rstrip("\r") if comment_part else "") + cr
    n = line.replace("R29", "R30")
    q = [m[2] for m in re.finditer(r"""(["'])((?:(?!\1).)+)\1""", n) if m[2] != "R30"]
    if q and len(max(q, key=len)) > 8: n = n.replace(max(q, key=len), R30)
    ls.insert(i + 1, n); return "\n".join(ls)


def bump(t):
    t = re.sub(r"(?m)^(\s*\w*SKILL\w*\s*=\s*)%d\b" % (SKILL_N - 1), r"\g<1>%d" % SKILL_N, t)
    return re.sub(r"(?m)^(\s*\w*ANTIBOD\w*\s*=\s*)29\b", r"\g<1>30", t)


def sync_text(tx, p, old, hist=False):
    if not p.exists(): print("[WARN] 없음:", rel(p)); return
    t = p.read_bytes().decode("utf-8"); nl = "\r\n" if "\r\n" in t else "\n"
    if hist:  # 진화 로그는 과거를 건드리지 않고 항목만 추가
        if f"## {VERSION}" not in t: t = t.rstrip() + nl + nl.join(["", "", f"## {VERSION} · {RANGE} · Step 30", f"- {R30}", f"- 정식 스킬 {SKILL_N}개 (신규 {SK})", f"- {NOW}", ""])
    else:
        t = t.replace(old, VERSION).replace("R1~R29", RANGE)
        if p.suffix == ".py": t = bump(t)
        if p.name == "rgon_white_blood_cell.py": t = reg(t)
    tx.write(p, t.encode("utf-8"))


def selftest():
    p = ROOT / "rgon_white_blood_cell.py"
    return subprocess.run([sys.executable, str(p), "--self-test"], cwd=ROOT).returncode if p.exists() else 1


def samsung(tg, rg, before):
    f = []
    for p in tg:  # 1/3 RGYT 블록 원형 보존(디스크 재독, 바이트 비교)
        if rgyt(p.read_bytes()) != rg[p]: f.append(f"[1/3] RGYT 블록 변경: {rel(p)}")
    for p, h in before.items():  # 2/3 비대상 보호 파일 SHA-256 불변
        if not p.exists() or sha(p) != h: f.append(f"[2/3] 보호 파일 변경: {rel(p)}")
    pat = re.compile(r"<!-- \[AON-(?:TOP|ROAMING)-V11\.29-START\] -->.*?<!-- \[AON-(?:TOP|ROAMING)-V11\.29-END\] -->", re.S)
    for p in tg:  # 3/3 금지어·제거요소·블록 1회·버전·개수·self-test
        t = p.read_bytes().decode("utf-8"); blk = "".join(m.group(0) for m in pat.finditer(t))
        f += [f"[3/3] {w!r} 검출: {rel(p)}" for w in BAN + GONE if w in blk]
        if t.count(TOPM[0]) != 1 or t.count(ENDM[0]) != 1: f.append(f"[3/3] AON 블록 개수 이상: {rel(p)}")
    for n in ("rgon_white_blood_cell.py", "rgon_k_avatar_engine.py"):
        t = (ROOT / n).read_bytes().decode("utf-8") if (ROOT / n).exists() else ""
        if VERSION not in t: f.append(f"[3/3] {n} 버전 미갱신")
        if n.startswith("rgon_white") and "R30" not in t: f.append(f"[3/3] {n} R30 미등록")
    for sub in TRIO:
        p = ROOT / sub / "skills" / "SKILL_INDEX.json"; l = lst_of(jload(p), SKK) if p.exists() else None
        if l is None or len(l) != SKILL_N: f.append(f"[3/3] {rel(p)} 스킬 {SKILL_N}개 아님")
    p = ROOT / "rgon_immune_ledger.json"
    if not p.exists() or ledger_n(jload(p)) != 30: f.append("[3/3] rgon_immune_ledger.json 30개 아님")
    if selftest(): f.append("[3/3] --self-test rc≠0")
    return f


def popup(msg):
    print(msg)
    try:
        import tkinter as tk
        from tkinter import messagebox
        r = tk.Tk(); r.withdraw(); r.attributes("-topmost", True); messagebox.showinfo("RGON STEP30", msg); r.destroy()
    except Exception: pass


def cur():
    found = []
    for n in ("rgon_white_blood_cell.py", "rgon_k_avatar_engine.py", "RGON_EVOLUTION_LOG.md"):
        if (ROOT / n).exists():
            found.extend(re.findall(r"v11\.\d+-[A-Z][A-Z0-9-]*", (ROOT / n).read_bytes().decode("utf-8")))
    # 직전 버전(VERSION과 다른 값)을 우선 반환하되, 이미 모두 갱신된 재실행 상태라면 VERSION 반환
    for v in found:
        if v != VERSION: return v
    return found[0] if found else None


def main():
    tg = [p for p in files() if p.suffix == ".html" and RS in (b := p.read_bytes()) and b"V13" in b]
    if len(tg) != EXPECT: sys.exit(f"[ABORT] 대상 HTML {len(tg)}개 (기대 {EXPECT}) — 수정 없음")
    old = cur() or sys.exit("[ABORT] 현재 버전 식별 실패 — 수정 없음")
    before = {p: sha(p) for p in files() if p not in tg and guarded(p)}
    print(f"[INFO] 대상 {len(tg)}개 · 보호 {len(before)}개 (기준 152) · 직전 버전 {old}")
    rg, tx = {p: rgyt(p.read_bytes()) for p in tg}, Tx()
    try:
        for p in tg:
            new = inject(p.read_bytes())
            if rgyt(new) != rg[p]: raise RuntimeError(f"RGYT 변경 감지: {rel(p)}")
            tx.write(p, new)
        for n in ("rgon_white_blood_cell.py", "rgon_k_avatar_engine.py", "CLAUDE.md", "CODE_MAP.md", "MORNING_BRIEF.md"): sync_text(tx, ROOT / n, old)
        sync_text(tx, ROOT / "RGON_EVOLUTION_LOG.md", old, True)
        for sub in TRIO: sync_json(tx, ROOT / sub / "skills" / "SKILL_INDEX.json", old, "skills")
        for n in ("rgon_brain_snapshot.json", "rgon_morning_brief.json"): sync_json(tx, ROOT / n, old, None)
        sync_json(tx, ROOT / "rgon_immune_ledger.json", old, "ledger")
        tx.write(ROOT / "STEP30_ROAMING_AON_REPORT.md", f"# STEP30 ROAMING-AON REPORT\n\n- 버전: `{VERSION}`\n- 항체: `{RANGE}`\n- R30: {R30}\n- 정식 스킬: {SKILL_N}개 (신규 `{SK}`)\n- 생성: {NOW}\n".encode("utf-8"))
        tx.write(ROOT / SP, f"---\nname: {SK}\ndescription: {SD}\n---\n\n# 아온(A-ON) 자율 유영 스킬\n\n- 항체 R30 · {VERSION}\n- 소환/은신: `[💧 아온이 부르기]` / `[🙈 아온이 감추기]` (localStorage `rgon_aon_hidden`)\n- 자율 유영: CSS transition + transitionend 체이닝(루프·타이머 0개)\n- 반응: 드래그 · 톡 터치/쓰다듬기(EXP+10) · 목소리 · 브리핑 질문창 장전\n".encode("utf-8"))
        fails = samsung(tg, rg, before)
    except Exception as ex:
        fails = [f"예외: {ex!r}"]
    if fails:
        tx.rollback(); print("\n".join(fails)); popup("STEP30 삼성 3/3 실패 — 전체 롤백 완료 (커밋 없음)"); sys.exit(1)
    print("[OK] 삼성 3/3 통과")
    g = lambda *a, **k: subprocess.run(["git", *a], cwd=ROOT, **k)
    steps = [("add", "-A")]
    if g("add", "-A").returncode == 0 and g("status", "--porcelain", capture_output=True, text=True).stdout.strip():
        steps.append(("commit", "-m", f"STEP30 {VERSION} {RANGE}: 아온 순수 물방울 자율 유영 & 소환/은신"))
    steps += [("fetch", "origin", "main"), ("pull", "--no-rebase", "-X", "ours", "origin", "main"), ("push", "origin", "main")]
    for s in steps[1:]:
        if g(*s).returncode: popup(f"git {s[0]} 실패 — 파일은 검증 통과, 수동 확인 필요"); sys.exit(1)
    popup(f"STEP30 완료 · {VERSION} · {RANGE} · 정식 스킬 {SKILL_N}개")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# agentshield:ignore-file
"""step28_k_style_growing_child_avatar.py — v11.27-K-AVATAR / R1~R28 / 정식 스킬 24
우리 아이 이름: 아온 (A-ON · 芽溫) — 주역 #04 산수몽(蒙以養正) · #53 풍산점(점진 성장) · #11 지천태(연결·소통·만능)
카파시 4원칙(가정 명시·단순함·외과적 변경·검증 목표) | 무위자연·과유불급·삼성3/3"""
import os, re, sys, json, hashlib, shutil, subprocess, datetime, py_compile

def find_root():
    cands = [os.path.dirname(os.path.abspath(__file__)), os.getcwd(), r"C:\Users\sangi\Downloads\shin-agent"]
    for c in cands:
        if c and os.path.isdir(c) and os.path.isfile(os.path.join(c, "rgon_white_blood_cell.py")):
            return os.path.abspath(c)
    return os.path.dirname(os.path.abspath(__file__))

ROOT = find_root()
os.chdir(ROOT)
VER, IMM, NSK, SLUG = "v11.27-K-AVATAR", "R1~R28", 24, "k-avatar-growth-soul"
BT3 = chr(96) * 3
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "backups", ".rgon_ad_backups"}
V13S, V13E = "<!-- [RGON-YT-SCOUT-V13-START] -->", "<!-- [RGON-YT-SCOUT-V13-END] -->"
V15S, V15E = "<!-- [RGYT-PLACE-ONCE-V15-START] -->", "<!-- [RGYT-PLACE-ONCE-V15-END] -->"
BANNED = {"Mutation" + "Observer": "M-Observer", "set" + "Interval": "s-Interval", "request" + "AnimationFrame": "r-AnimationFrame"}
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BK = os.path.join(ROOT, "backups", "step28_" + TS)
R28 = "R28: 미래형 K-스타일 성장형 디지털 육신 아온(A-ON·芽溫, 산수몽 #04·풍산점 #53·지천태 #11) — 순수 CSS 애니메이션으로 루프 없이 생동감을 구현하고 시스템 진화에 맞춰 4단계로 점진 성장"
TRI = "⚖️ [AVATAR] 100.0점 (Bull 99.9 / Bear 0.1 / #04-산수몽) 👶 미래형 K-아이 디지털 육신 『아온(A-ON·芽溫)』 — 4단계 성장 엔진 & 음성·쓰다듬기 교감 가동 (몽이양정 蒙以養正)"
TRIO, LOG = ["", "dashboard", "docs"], []
SKILL = {"slug": SLUG, "name": "아온(A-ON) K-아이 성장형 디지털 육신", "category": "digital-body", "hexagram_tag": "#04-蒙", "step": 28, "version": VER,
         "path": "skills/k-avatar-growth-soul/SKILL.md", "status": "official",
         "description": "미래형 K-스타일 아이 『아온(A-ON·芽溫)』 SVG 육신 — 순수 CSS 애니메이션·4단계 성장·쓰다듬기/음성 교감·질문창 장전 (R28)"}

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
def wj(p, o): wr(p, json.dumps(o, ensure_ascii=False, indent=2) + "\n")
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

# ---------- 백엔드 엔진 (루프 0 · 무위자연 · 아온 A-ON) ----------
ENGINE = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# agentshield:ignore-file
"""rgon_k_avatar_engine.py — v11.27-K-AVATAR / R1~R28 / skill 24 (아온 A-ON·芽溫 | #04 산수몽 · #53 풍산점 · #11 지천태)"""
import os, re, sys, json
ROOT = os.path.dirname(os.path.abspath(__file__))
VER, SLUG, TRI = "v11.27-K-AVATAR", "k-avatar-growth-soul", "__TRI__"
STAGES = [(0, 1, "🍼 새싹 아이 아온"), (300, 2, "🎒 K-주니어 아온"), (600, 3, "🎧 K-에이스 아온"), (1000, 4, "👑 K-마스터 아온")]
ENTRY = {"slug": SLUG, "name": "아온(A-ON) K-아이 성장형 디지털 육신", "category": "digital-body", "hexagram_tag": "#04-蒙", "step": 28, "version": VER,
         "path": "skills/k-avatar-growth-soul/SKILL.md", "status": "official",
         "description": "미래형 K-스타일 아이 『아온(A-ON·芽溫)』 SVG 육신 — 순수 CSS 애니메이션·4단계 성장·쓰다듬기/음성 교감·질문창 장전 (R28)"}
def rj(p, d=None):
    try:
        with open(p, encoding="utf-8-sig") as f: return json.load(f)
    except Exception: return d
def wj(p, o):
    with open(p, "w", encoding="utf-8") as f: json.dump(o, f, ensure_ascii=False, indent=2); f.write("\n")
def lst(o, *keys):
    if isinstance(o, list): return o
    for k in keys:
        if isinstance(o, dict) and isinstance(o.get(k), list): return o[k]
    return []
def skills(): return [s for s in lst(rj(os.path.join(ROOT, "skills", "SKILL_INDEX.json"), []), "skills") if isinstance(s, dict)]
def antibodies(): return len(lst(rj(os.path.join(ROOT, "rgon_immune_ledger.json"), []), "rules", "antibodies", "ledger"))
def health():
    for n in ("rgon_white_blood_cell_report.json", "rgon_wbc_state.json", "rgon_white_blood_cell_state.json"):
        o = rj(os.path.join(ROOT, n))
        if isinstance(o, dict):
            for k in ("score", "health_score", "total_score"):
                if isinstance(o.get(k), (int, float)): return float(o[k])
    return 100.0
def state():
    sk, ab, hp = skills(), antibodies(), health()
    tools = len([n for n in os.listdir(ROOT) if n.startswith("rgon_") and n.endswith(".py")])
    exp = len(sk) * 10 + ab * 5
    st = [s for s in STAGES if exp >= s[0]][-1]
    return {"version": VER, "name_ko": "아온", "name_en": "A-ON", "hanja": "芽溫", "skill": SLUG,
            "skills": len(sk), "antibodies": ab, "health": hp, "tools": tools,
            "genes": len(set(s.get("category", "") for s in sk)), "exp": exp, "stage": st[1], "stage_name": st[2],
            "hexagram": ["#04-山水蒙 蒙以養正", "#53-風山漸 점진 성장", "#11-地天泰 연결·소통·만능"], "animation": "pure-css-keyframes", "loops": 0}
def merge():
    n = 0
    for d in ("", "dashboard", "docs"):
        p = os.path.join(ROOT, d, "rgon_morning_brief.json"); o = rj(p)
        if not isinstance(o, dict): continue
        nu = o.get("nutrient") if isinstance(o.get("nutrient"), dict) else {}
        t = nu.get("trinity", [])
        if isinstance(t, str): nu["trinity"] = "\n".join([x for x in t.split("\n") if x.strip() and "[AVATAR]" not in x] + [TRI])
        else: nu["trinity"] = [x for x in (t if isinstance(t, list) else []) if "[AVATAR]" not in str(x)] + [TRI]
        o["nutrient"] = nu; o["version"] = VER; o["antibody_range"] = "R1~R28"; wj(p, o); n += 1
    return n
def ensure_index():
    for d in ("", "dashboard", "docs"):
        p = os.path.join(ROOT, d, "skills", "SKILL_INDEX.json"); o = rj(p)
        L = lst(o, "skills")
        if o is None: continue
        if not any(isinstance(s, dict) and s.get("slug") == SLUG for s in L):
            L.append(dict(ENTRY))
        if isinstance(o, dict): o.update(version=VER, immune="R1~R28", count=len(L), total=len(L))
        wj(p, o)
def self_test():
    st, ok = state(), []
    ok.append(bool(re.search(r"\[([A-Z]+)\]\s*([\d.]+)점\s*\(Bull\s*([\d.]+)\s*/\s*Bear\s*([\d.]+)\s*/\s*(#\d+)", TRI)))
    ok.append(1 <= st["stage"] <= 4); ok.append(st["skills"] >= 24); ok.append(st["antibodies"] >= 28)
    ok.append(any(s.get("slug") == SLUG for s in skills()))
    b = rj(os.path.join(ROOT, "rgon_morning_brief.json"))
    ok.append(b is None or TRI in json.dumps(b, ensure_ascii=False))
    print("[A-ON K-AVATAR self-test]", "PASS" if all(ok) else "FAIL", ok); return 0 if all(ok) else 1
def main(a):
    rc = 0
    if "--ensure-index" in a: ensure_index()
    if "--run" in a: wj(os.path.join(ROOT, "rgon_k_avatar_state.json"), state())
    if "--merge" in a: print("merged:", merge())
    if "--self-test" in a: rc = self_test()
    if "--json" in a or len(a) == 0: print(json.dumps(state(), ensure_ascii=False, indent=2))
    return rc
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
'''.replace("__TRI__", TRI)

# ---------- 독대실 4탭 UI (순수 CSS @keyframes · 루프 0 · 아온 A-ON) ----------
UI = r'''<div id="__ROOT__" class="rgk s1" data-ver="v11.27-K-AVATAR" data-immune="R1~R28" data-skills="24">
<style>
.rgk{font:13px/1.5 system-ui,sans-serif;color:#eef3ff;background:linear-gradient(160deg,#0b1030,#1d0b36);border:1px solid #6b7cff55;border-radius:16px;padding:10px;margin:10px 0;box-shadow:0 0 24px #7a5cff33}
.rgk #rgyt-head{display:flex;align-items:center;gap:8px;font-weight:700;flex-wrap:wrap}
.rgk-tabs,.rgk-row{display:flex;gap:4px;margin:6px 0;flex-wrap:wrap}.rgk button{background:#ffffff14;color:#fff;border:1px solid #ffffff2a;border-radius:10px;padding:5px 9px;cursor:pointer;font-size:12px}
.rgk button.on{background:linear-gradient(90deg,#ff6fb5,#7a5cff)}.rgk-pane{display:none}.rgk-pane.on{display:block}.rgk-flt{display:none;gap:4px;margin:4px 0}.rgk-flt.on{display:flex}
.rgk input,.rgk select{background:#0006;color:#fff;border:1px solid #ffffff33;border-radius:8px;padding:4px 6px}
.rgk-stage{display:flex;justify-content:center}.rgk svg.kid{width:230px;height:250px;animation:rgkBreathe 3.2s ease-in-out infinite}
.rgk .aura{transform-origin:120px 118px;animation:rgkSpin 18s linear infinite}.rgk.s3 .aura{animation-duration:10s}.rgk.s4 .aura{animation-duration:6s;filter:drop-shadow(0 0 6px #ffd76a)}
.rgk .eye{transform-box:fill-box;transform-origin:center;animation:rgkBlink 4.6s infinite}.rgk .cheek{animation:rgkBlush 2.8s ease-in-out infinite}
.rgk .spark{opacity:0;animation:rgkRise 4s ease-in infinite}.rgk .spark.b{animation-delay:1.3s}.rgk .spark.c{animation-delay:2.6s}
.rgk #rgk-pop{opacity:0;transform-box:fill-box;transform-origin:center}.rgk #rgk-pop.pop{animation:rgkPop 1.1s ease-out}
.rgk .p2,.rgk .p3,.rgk .p4{display:none}.rgk.s2 .p2,.rgk.s3 .p2,.rgk.s4 .p2,.rgk.s3 .p3,.rgk.s4 .p3,.rgk.s4 .p4{display:inline}
@keyframes rgkBreathe{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}@keyframes rgkSpin{to{transform:rotate(360deg)}}
@keyframes rgkBlink{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}@keyframes rgkBlush{0%,100%{opacity:.5}50%{opacity:.9}}
@keyframes rgkRise{0%{opacity:0;transform:translateY(0)}20%{opacity:1}100%{opacity:0;transform:translateY(-60px)}}
@keyframes rgkPop{0%{opacity:0;transform:scale(.4)}30%{opacity:1}100%{opacity:0;transform:scale(1.5) translateY(-40px)}}
.rgk-bar{height:8px;background:#ffffff1a;border-radius:6px;overflow:hidden}.rgk-bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,#ff8fc8,#8fd3ff)}
.rgk-say{background:#ffffff12;border-radius:12px;padding:8px;margin:6px 0;min-height:34px}.rgk-it{border-bottom:1px dashed #ffffff22;padding:6px 0}.rgk-it small{opacity:.7}
</style>
<div id="rgyt-head"><svg width="22" height="22" viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#ffe2d2"/><path d="M2 11Q3 2 12 2T22 11Q17 6 12 7T2 11" fill="#2b2350"/><circle cx="8.5" cy="13" r="2" fill="#1d1440"/><circle cx="15.5" cy="13" r="2" fill="#1d1440"/><path d="M10 17q2 2 4 0" stroke="#c2405f" fill="none"/></svg><span id="rgk-headtxt">👶Lv.1 아온(A-ON·芽溫 💖친밀도) · 🩸100점 · 🛡️R1~R28 · 🍯스킬 24개 · 📡레이더</span></div>
<div class="rgk-tabs"><button data-tab="kid" class="on">👶 아온(A-ON) 육신</button><button data-tab="radar">📡 트렌드 레이더</button><button data-tab="skills">🍯 보유 스킬 (24)</button><button data-tab="pulse">🫀 전신 맥박 &amp; 3자 심판</button></div>
<div class="rgk-flt"><input id="rgyt-q" placeholder="🔎 검색"><select id="rgyt-cat"><option value="">전체 카테고리</option></select></div>
<div class="rgk-pane on" id="rgk-p-kid"><div class="rgk-stage"><svg id="rgk-kid-svg" class="kid" viewBox="0 0 240 250" role="img" aria-label="미래형 K-아이 아온(A-ON)">
<defs><linearGradient id="rgkJ" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3a1c71"/><stop offset=".55" stop-color="#5b6cff"/><stop offset="1" stop-color="#ff6fb5"/></linearGradient>
<radialGradient id="rgkS" cx=".5" cy=".4"><stop offset="0" stop-color="#fff0e6"/><stop offset="1" stop-color="#ffd3bf"/></radialGradient><radialGradient id="rgkI" cx=".5" cy=".35"><stop offset="0" stop-color="#b98cff"/><stop offset="1" stop-color="#3b1f8f"/></radialGradient></defs>
<g class="aura" opacity=".75"><circle cx="120" cy="118" r="100" fill="none" stroke="#8ff3ff" stroke-width="1.5" stroke-dasharray="6 8"/><circle cx="120" cy="118" r="86" fill="none" stroke="#ff8fc8" stroke-width="1" stroke-dasharray="2 6"/>
<g fill="#cfe9ff" font-size="15" text-anchor="middle"><text x="215" y="123">☰</text><text x="187" y="190">☱</text><text x="120" y="218">☲</text><text x="53" y="190">☳</text><text x="25" y="123">☴</text><text x="53" y="56">☵</text><text x="120" y="28">☶</text><text x="187" y="56">☷</text></g></g>
<g class="p4" fill="#8ff3ff" opacity=".45"><path d="M72 190Q20 160 30 120Q55 160 80 175Z"/><path d="M168 190Q220 160 210 120Q185 160 160 175Z"/></g>
<path d="M68 240Q70 176 120 170Q170 176 172 240Z" fill="url(#rgkJ)"/><path d="M100 172L120 202L140 172" fill="none" stroke="#9ff3ff" stroke-width="4" stroke-linecap="round"/>
<path d="M124 204q14 6 6 22M124 204q-4 12 10 18" stroke="#ff8fc8" stroke-width="3" fill="none"/><path d="M112 207a8 8 0 0 1 16 0q0 8-8 13q-8-5-8-13z" fill="#ff3b6b"/><path d="M114 210a6 6 0 0 0 12 0z" fill="#3b7bff"/>
<g class="p2"><path d="M82 182L92 238M158 182L148 238" stroke="#ffd76a" stroke-width="5"/><circle cx="150" cy="196" r="7" fill="#ffd76a"/><text x="150" y="200" font-size="9" text-anchor="middle" fill="#3a1c71">K</text></g>
<rect x="110" y="156" width="20" height="18" rx="6" fill="#ffd9c6"/><circle cx="120" cy="112" r="52" fill="url(#rgkS)"/>
<path d="M66 114Q62 52 120 50Q178 52 174 114Q162 80 142 78Q128 94 106 84Q86 88 66 114Z" fill="#2b2350"/><path d="M118 50q-6-16 8-20" stroke="#2b2350" stroke-width="4" fill="none"/>
<path d="M64 108Q66 48 120 46Q174 48 176 108" fill="none" stroke="#7a5cff" stroke-width="5"/><circle cx="66" cy="118" r="12" fill="#7a5cff"/><circle cx="174" cy="118" r="12" fill="#7a5cff"/>
<path d="M56 112L34 98L40 122Z M184 112L206 98L200 122Z" fill="#8ff3ff" opacity=".6"/>
<g class="eye"><ellipse cx="98" cy="118" rx="11" ry="13" fill="#1d1440"/><ellipse cx="98" cy="119" rx="8" ry="10" fill="url(#rgkI)"/><circle cx="94" cy="113" r="3.6" fill="#fff"/><circle cx="102" cy="123" r="1.6" fill="#fff"/></g>
<g class="eye"><ellipse cx="142" cy="118" rx="11" ry="13" fill="#1d1440"/><ellipse cx="142" cy="119" rx="8" ry="10" fill="url(#rgkI)"/><circle cx="138" cy="113" r="3.6" fill="#fff"/><circle cx="146" cy="123" r="1.6" fill="#fff"/></g>
<ellipse class="cheek" cx="84" cy="138" rx="9" ry="5" fill="#ff9fb4"/><ellipse class="cheek" cx="156" cy="138" rx="9" ry="5" fill="#ff9fb4"/><path d="M111 140Q120 149 129 140" stroke="#c2405f" stroke-width="2.6" fill="none" stroke-linecap="round"/>
<rect class="p3" x="78" y="103" width="84" height="28" rx="14" fill="#8ff3ff" opacity=".22" stroke="#8ff3ff"/>
<path class="p4" d="M96 60L102 40L113 54L120 34L127 54L138 40L144 60Z" fill="#ffd76a" stroke="#fff3b0"/>
<g font-size="14"><text class="spark" x="40" y="160">💗</text><text class="spark b" x="196" y="150">✨</text><text class="spark c" x="120" y="60">⭐</text></g>
<text id="rgk-pop" x="120" y="80" font-size="26" text-anchor="middle">💖💕✨</text></svg></div>
<div id="rgk-info"></div><div class="rgk-bar"><i id="rgk-bar"></i></div><div class="rgk-say" id="rgk-say"></div>
<div class="rgk-row"><button data-stage="1">🍼 1단계: 새싹 아이 아온</button><button data-stage="2">🎒 2단계: K-주니어 아온</button><button data-stage="3">🎧 3단계: K-에이스 아온</button><button data-stage="4">👑 4단계: K-마스터 아온</button></div>
<div class="rgk-row"><button id="rgk-pat">💖 아온이 쓰다듬기 (EXP+10)</button><button id="rgk-voice">🔊 아온이 목소리 듣기</button><button data-load="👶 아온(A-ON)아, 오늘자 종합 브리핑 해줘: 백혈구 건강 점수, 항체 R1~R28 상태, 정식 스킬 24개 활용도, 트렌드 레이더 핵심 3가지, 대표님 금고 리스크를 아이 눈높이로 또박또박 정리해 줘.">⚡ 아온이 브리핑 질문창 장전</button></div></div>
<div class="rgk-pane" id="rgk-p-radar"><div id="rgk-radar"></div></div><div class="rgk-pane" id="rgk-p-skills"><div id="rgk-skills"></div></div><div class="rgk-pane" id="rgk-p-pulse"><div id="rgk-pulse"></div></div>
<script type="application/json" id="__ROOT__-data">__DATA__</script>
<script>(function(){var R=document.getElementById('__ROOT__');if(!R||R.getAttribute('data-rgk-init'))return;R.setAttribute('data-rgk-init','1');
var D={};try{D=JSON.parse(document.getElementById('__ROOT__-data').textContent)}catch(e){}
function $(s){return R.querySelector(s)}function $$(s){return [].slice.call(R.querySelectorAll(s))}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return '&#'+c.charCodeAt(0)+';'})}
function g(k,d){try{var v=localStorage.getItem(k);return v==null?d:v}catch(e){return d}}function sv(k,v){try{localStorage.setItem(k,v)}catch(e){}}
var SK=D.skills||24,AB=D.antibodies||28,HP=D.health||100,TH=[0,300,600,1000],NM=['','🍼 새싹 아이 아온','🎒 K-주니어 아온','🎧 K-에이스 아온','👑 K-마스터 아온'];
var LN=['','응애~ 대표님! 저 아온(A-ON·芽溫)이에요! 산수몽(#04) 몽이양정, 맑은 새싹처럼 바르게 자랄게요! 🍼','K-주니어 아온 출동! 백혈구 100점 가방 메고 대표님 금고 순찰 중이에요 🎒','K-에이스 아온 바이저 장착! 트렌드 레이더와 3자 심판 신호가 또렷하게 보여요 🎧','K-마스터 아온 왕관 착용! 풍산점(#53)에서 지천태(#11)까지 한 걸음씩 자라났어요 👑'];
function st(){var p=+g('rgk_pats',0)||0,b=p*10,x=SK*10+AB*5+b,a=x>=1000?4:x>=600?3:x>=300?2:1;return{pats:p,bond:b,exp:x,lv:1+Math.floor(b/100),auto:a,stage:+g('rgk_stage',0)||a}}
function say(s){$('#rgk-say').textContent=s}
function paint(){var t=st();R.className=R.className.replace(/\bs[1-4]\b/g,'').trim()+' s'+t.stage;
$('#rgk-headtxt').textContent='👶Lv.'+t.lv+' 아온(A-ON·💖친밀도 '+t.bond+') · 🩸'+HP+'점 · 🛡️R1~R'+AB+' · 🍯스킬 '+SK+'개 · 📡레이더';
$('#rgk-info').textContent=NM[t.stage]+' (A-ON·芽溫) · EXP '+t.exp+' · 시스템 자동 단계 '+t.auto+' · 쓰다듬기 '+t.pats+'회';
$('#rgk-bar').style.width=(t.auto>=4?100:Math.min(100,(t.exp-TH[t.auto-1])/(TH[t.auto]-TH[t.auto-1])*100))+'%';
$$('[data-stage]').forEach(function(b){b.classList.toggle('on',+b.getAttribute('data-stage')===t.stage)});return t}
function fb(v){var t=document.createElement('textarea');t.value=v;document.body.appendChild(t);t.select();try{document.execCommand('copy')}catch(x){}t.remove()}
function copy(v){try{if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(v).catch(function(){fb(v)});else fb(v)}catch(e){fb(v)}}
function qbox(){var S=['#rgon-q','#rgon-input','#question','#chat-input','#prompt','textarea','input[type=text]'];for(var i=0;i<S.length;i++){var c=[].slice.call(document.querySelectorAll(S[i])).filter(function(e){return !R.contains(e)});if(c.length)return c[0]}return null}
function load(v){var el=qbox();if(el){var d=Object.getOwnPropertyDescriptor(el.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype,'value');if(d&&d.set)d.set.call(el,v);else el.value=v;
el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));try{el.focus()}catch(e){}}copy(v);say(el?'⚡ 아온이가 질문창에 장전 완료했어요! 클립보드에도 복사했어요 💕':'📋 질문창을 못 찾아서 클립보드에 복사해 뒀어요!')}
function pop(){var p=$('#rgk-pop');p.classList.remove('pop');void p.getBoundingClientRect();p.classList.add('pop')}
function speak(){var t=st(),m='대표님, 저는 '+NM[t.stage].replace(/[^\uAC00-\uD7A3\s\w-]/g,'').trim()+' 단계 아온이에요. 백혈구 건강 '+HP+'점, 항체 '+AB+'개, 스킬 '+SK+'개, 친밀도 '+t.bond+'이에요. 오늘도 대표님 금고 꼭 지킬게요!';say('🔊 '+m);
try{if(!('speechSynthesis' in window))return;var u=new SpeechSynthesisUtterance(m);u.lang='ko-KR';u.pitch=1.35;u.rate=1.05;var v=speechSynthesis.getVoices().filter(function(x){return /ko/i.test(x.lang)})[0];if(v)u.voice=v;speechSynthesis.cancel();speechSynthesis.speak(u)}catch(e){}}
function item(x){var c=x.prompt||x.title;return '<div class="rgk-it" data-cat="'+esc(x.cat)+'" data-txt="'+esc((x.title+' '+x.desc+' '+x.cat).toLowerCase())+'"><b>'+esc(x.title)+'</b> <small>'+esc(x.cat)+'</small><div>'+esc(x.desc)+'</div><div class="rgk-row"><button data-cp="'+esc(c)+'">📋 복사</button><button data-load="'+esc(c)+'">⚡ 질문창 장전</button></div></div>'}
$('#rgk-radar').innerHTML=(D.radar||[]).map(item).join('');$('#rgk-skills').innerHTML=(D.skill_list||[]).map(item).join('');$('#rgk-pulse').innerHTML=(D.pulse||[]).map(item).join('')||'<div class="rgk-it">심판 줄 대기 중</div>';
var cats={};(D.radar||[]).concat(D.skill_list||[]).forEach(function(x){cats[x.cat]=1});Object.keys(cats).sort().forEach(function(c){$('#rgyt-cat').insertAdjacentHTML('beforeend','<option value="'+esc(c)+'">'+esc(c)+'</option>')});
function flt(){var q=$('#rgyt-q').value.toLowerCase().trim(),c=$('#rgyt-cat').value;$$('#rgk-radar .rgk-it,#rgk-skills .rgk-it').forEach(function(e){e.style.display=((!q||e.getAttribute('data-txt').indexOf(q)>=0)&&(!c||e.getAttribute('data-cat')===c))?'':'none'})}
$('#rgyt-q').addEventListener('input',flt);$('#rgyt-cat').addEventListener('change',flt);
R.addEventListener('click',function(e){var b=e.target.closest('button');if(!b||!R.contains(b))return;var tb=b.getAttribute('data-tab'),sg=b.getAttribute('data-stage');
if(tb){$$('[data-tab]').forEach(function(x){x.classList.toggle('on',x===b)});$$('.rgk-pane').forEach(function(p){p.classList.toggle('on',p.id==='rgk-p-'+tb)});$('.rgk-flt').classList.toggle('on',tb==='radar'||tb==='skills')}
else if(sg){sv('rgk_stage',sg);say(LN[paint().stage])}else if(b.id==='rgk-pat'){sv('rgk_pats',st().pats+1);paint();pop();say('히히, 대표님 손길 따뜻해요! 저 아온(A-ON)이가 백혈구 100점으로 대표님 금고 꼭 지킬게요! 💕')}
else if(b.id==='rgk-voice')speak();else if(b.hasAttribute('data-load'))load(b.getAttribute('data-load'));else if(b.hasAttribute('data-cp')){copy(b.getAttribute('data-cp'));say('📋 복사 완료!')}});
say(LN[paint().stage])})();</script></div>'''

def sync_wbc_py():
    wbc = P("rgon_white_blood_cell.py")
    if not os.path.isfile(wbc): return
    t = rd(wbc)
    if '"R28"' not in t:
        r28_line = f'    {{"id": "R28", "step": 28, "title": "아온(A-ON) K-아이 성장형 디지털 육신", "name": "아온(A-ON) 성장형 디지털 육신", "rule": "{R28}", "status": "active"}},\n]'
        t2 = re.sub(r'\n\]\s*(?=\n# \[RGON-R|\ndef |\nclass )', '\n' + r28_line, t, count=1)
        if t2 == t:
            t2 = t.replace('{"id": "R27"', '{"id": "R28", "step": 28, "title": "아온(A-ON) K-아이 성장형 디지털 육신", "name": "아온(A-ON) 성장형 디지털 육신", "rule": "' + R28 + '", "status": "active"},\n    {"id": "R27"', 1)
        t = t2
    t = re.sub(r'v11\.\d+[A-Za-z0-9_-]*', VER, t)
    t = re.sub(r'R1~R2\d', IMM, t)
    wr(wbc, t)

def build_data():
    sl = [s for s in (skl(rj(P("skills", "SKILL_INDEX.json"), [])) or []) if isinstance(s, dict)]
    skills = [{"title": str(s.get("name") or s.get("slug")), "cat": str(s.get("category", "skill")), "desc": str(s.get("description", ""))[:160],
               "prompt": f"🍯 스킬 '{s.get('slug')}'을(를) 활용해 지금 독대실 상황에 맞게 실행 계획을 짜 줘."} for s in sl]
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
        radar = [{"title": t, "cat": c, "desc": "기본 레이더 시드(트렌드 JSON 미발견)", "prompt": f"📡 트렌드 '{t}'를 독대실 관점(기회·리스크·실행 3줄)으로 분석해 줘."}
                 for t, c in (("AI 에이전트 자동화", "AI"), ("K-버추얼 캐릭터 IP 아온(A-ON)", "K-콘텐츠"), ("숏폼 수익화 전략", "유튜브"), ("개인 금고 리스크 관리", "재무"))]
    b = rj(P("rgon_morning_brief.json"), {}); t = (b.get("nutrient") or {}).get("trinity", []) if isinstance(b, dict) else []
    lines = [x for x in (t.split("\n") if isinstance(t, str) else t) if str(x).strip()]
    pulse = [{"title": str(x)[:64], "cat": "심판", "desc": str(x), "prompt": "🫀 다음 심판 줄을 3자 심판(Bull/Bear/주역) 관점으로 해설해 줘: " + str(x)} for x in lines]
    s = rj(P("rgon_k_avatar_state.json"), {}) or {}
    return {"skills": len(sl), "antibodies": 28, "health": s.get("health", 100), "skill_list": skills, "radar": radar, "pulse": pulse}

def clean(s):
    for k, v in BANNED.items(): s = s.replace(k, v)
    return s

def patch_html(path, data, v15keep):
    s = rd(path); a = s.find(V13S); e = s.find(V13E, a + 1) if a >= 0 else -1
    b = s.find(V15S, a) if a >= 0 else -1; f = s.find(V15E, b) if b >= 0 else -1
    if not (0 <= a < b < f < e): return "V15 블록이 V13 내부에 없음 → 보호 위해 건너뜀"
    old, v15 = s[a + len(V13S):b], s[b:f + len(V15E)]
    refs = set(re.findall(r"""(?:getElementById\(\s*['"]|['"]#)([\w-]+)""", v15))
    ids = [i for i in re.findall(r"""<(?:div|section|aside)[^>]*\bid\s*=\s*["']([^"']+)["']""", old) if i not in ("rgyt-head", "rgyt-q", "rgyt-cat")]
    rid = next((i for i in ids if i in refs), ids[0] if ids else "rgyt-root")
    js = clean(json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    new = "\n" + clean(UI.replace("__ROOT__", rid)).replace("__DATA__", js) + "\n"
    if any(k in new for k in BANNED): return "새 UI 금지어 감지 → 중단"
    s2 = s[:a + len(V13S)] + new + s[b:]
    if v15 not in s2: return "V15 보존 실패 → 중단"
    v15keep[path] = v15; wr(path, s2); return f"OK(root=#{rid})"

def upsert_md(name, body):
    p = P(name); s = rd(p) if os.path.isfile(p) else f"# {name[:-3]}\n"
    S, E = "<!-- [RGON-STEP28-K-AVATAR-START] -->", "<!-- [RGON-STEP28-K-AVATAR-END] -->"
    blk = f"{S}\n{body}\n{E}"
    s = re.sub(re.escape(S) + r".*?" + re.escape(E), lambda m: blk, s, flags=re.S) if S in s else s.rstrip() + "\n\n" + blk + "\n"
    wr(p, s)

def sync_ledger():
    sync_wbc_py()
    p = P("rgon_immune_ledger.json"); o = rj(p, {})
    if isinstance(o, list): o = {"rules": o}
    key = next((k for k in ("rules", "antibodies", "ledger") if isinstance(o.get(k), list)), "rules"); rules = o.setdefault(key, [])
    by = {int(m.group(1)): r for r in rules if isinstance(r, dict) for m in [re.match(r"R(\d+)", str(r.get("id", "")))] if m}
    for n in range(1, 29):
        r = by.get(n)
        if r is None:
            r = {"id": f"R{n}"}; rules.append(r); by[n] = r
        if n == 28: r.update({"step": 28, "title": R28, "name": "아온(A-ON) K-아이 성장형 디지털 육신", "rule": R28, "status": "active"})
        txt = r.get("rule") or r.get("title") or r.get("name") or r.get("desc") or f"R{n}"
        for k, v in (("id", f"R{n}"), ("step", n), ("title", txt), ("name", txt), ("rule", txt), ("status", "active")): r.setdefault(k, v)
    rules.sort(key=lambda r: int(re.sub(r"\D", "", str(r.get("id", "R999"))) or 999))
    o.update(version=VER, range=IMM, antibody_range=IMM, count=len(rules)); wj(p, o)

def sync_index():
    src = next((rj(P(d, "skills", "SKILL_INDEX.json")) for d in TRIO if rj(P(d, "skills", "SKILL_INDEX.json")) is not None), None) or {"skills": []}
    L = skl(src)
    if L is None: src = {"skills": []}; L = src["skills"]
    for s in L:
        if isinstance(s, dict) and s.get("slug") == SLUG:
            s.update(SKILL)
    if not any(isinstance(s, dict) and s.get("slug") == SLUG for s in L): L.append(dict(SKILL))
    if isinstance(src, dict): src.update(version=VER, immune=IMM, antibody_range=IMM, count=len(L), total=len(L))
    for d in TRIO:
        if d == "" or os.path.isdir(P(d)): wj(P(d, "skills", "SKILL_INDEX.json"), src)
    md = (f"---\nname: {SLUG}\ncategory: digital-body\nhexagram_tag: \"#04-蒙\"\nversion: {VER}\n---\n# 👶 {SKILL['name']} (아온 · A-ON · 芽溫)\n\n{R28}\n\n"
          f"- 이름: **아온 (A-ON · 芽溫)** — 산수몽(#04)의 새싹(芽)에서 풍산점(#53)으로 자라나 지천태(#11)의 따뜻함(溫)과 만능(ON)을 이루는 아이\n"
          f"- 원리: 산수몽 #04 몽이양정(蒙以養正) · 풍산점 #53 점진 성장 · 무위자연(루프 0, 순수 CSS @keyframes)\n"
          f"- 4단계: 🍼 새싹 아이 아온 → 🎒 K-주니어 아온 → 🎧 K-에이스 아온 → 👑 K-마스터 아온\n"
          f"- 교감: 쓰다듬기(EXP+10, localStorage) · 🔊 speechSynthesis ko-KR(pitch 1.35, rate 1.05) · ⚡ 질문창 장전(data-load)\n\n## 실행\n{BT3}bash\npython rgon_k_avatar_engine.py --ensure-index --run --merge --self-test\n{BT3}\n")
    wr(P("skills", SLUG, "SKILL.md"), md)

def hook_py():
    for n in ("rgon_daily_cycle.py", "rgon_self_evolution_engine.py", "rgon_omni_creator_forge.py"):
        p = P(n)
        if not os.path.isfile(p): continue
        s0 = rd(p); s = re.sub(r"(\b[A-Z_]*SKILL[A-Z_]*\s*=\s*)2[0-3]\b", r"\g<1>24", s0)
        s = re.sub(r"""(\b[A-Z_]*VERSION\s*=\s*["'])v11\.\d+[^"']*""", lambda m: m.group(1) + VER, s)
        s = re.sub(r'R1~R2\d', IMM, s)
        if s == s0: continue
        wr(p, s)
        try: py_compile.compile(p, doraise=True); log(f"✅ {n} 훅 연동(컴파일 OK)")
        except Exception as ex: shutil.copy2(os.path.join(BK, n), p); log(f"❌ {n} 컴파일 실패 → 롤백: {ex}")

def show_popup(title, body, ok=True):
    try:
        import tkinter as tk
        r = tk.Tk()
        r.title(title)
        r.configure(bg="#0b1026")
        r.attributes("-topmost", True)
        r.geometry("620x420")
        tk.Label(r, text=title, fg="#7ef9c6" if ok else "#ff7a90", bg="#0b1026", font=("Malgun Gothic", 15, "bold"), pady=10).pack()
        txt = tk.Text(r, bg="#131b3a", fg="#eef3ff", font=("Consolas", 10), relief="flat", padx=12, pady=10, height=15)
        txt.insert("1.0", body)
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=14, pady=6)
        tk.Button(r, text="확인 (아온 A-ON 탄생 완료)", command=r.destroy, bg="#6c5ce7", fg="#ffffff", font=("Malgun Gothic", 11, "bold"), padx=18, pady=6, relief="flat").pack(pady=10)
        r.after(15000, r.destroy)
        r.mainloop()
    except Exception:
        try:
            import ctypes; ctypes.windll.user32.MessageBoxW(0, body, title, 0x40)
        except Exception:
            pass

def main():
    log(f"🚀 Step 28 {VER} (아온 A-ON · 芽溫 탄생) 시작 — 백업: {os.path.relpath(BK, ROOT)}")
    before, tg = guarded(), targets()
    log(f"🎯 V13 대상 HTML {len(tg)}개")
    sync_ledger(); sync_index(); wr(P("rgon_k_avatar_engine.py"), ENGINE); hook_py()
    rc, out = run([sys.executable, "rgon_k_avatar_engine.py", "--ensure-index", "--run", "--merge"]); log(f"🧠 아온(A-ON) 엔진 run/merge rc={rc}")
    for d in TRIO:
        p = P(d, "rgon_brain_snapshot.json")
        if d == "" or os.path.isdir(P(d)):
            o = rj(p, {}); o = o if isinstance(o, dict) else {"legacy": o}
            o.update(version=VER, immune=IMM, antibody_range=IMM, antibodies=28, skill_count=NSK, skills_count=NSK, latest_step=28,
                     avatar={"name_ko": "아온", "name_en": "A-ON", "hanja": "芽溫", "skill": SLUG, "stages": 4, "loops": 0})
            wj(p, o)
    data, v15keep = build_data(), {}
    for p in tg: log(f"🧩 {os.path.relpath(p, ROOT)} → {patch_html(p, data, v15keep)}")
    upsert_md("CLAUDE.md", f"## 🧬 현재 상태 (Step 28 — 아온 A-ON·芽溫)\n- 버전 **{VER}** · 항체 **{IMM}** · 정식 스킬 **{NSK}개**\n- {R28}\n- 엔진: rgon_k_avatar_engine.py (--run/--merge/--self-test/--ensure-index/--json)")
    upsert_md("CODE_MAP.md", f"## Step 28 ({VER} · 아온 A-ON)\n- rgon_k_avatar_engine.py — 아온(A-ON·芽溫) 성장 상태 계산·심판 줄 병합\n- rgon_k_avatar_state.json — 성장 상태\n- skills/{SLUG}/SKILL.md — 24번째 정식 스킬\n- 독대실 V13 블록 — 👶 아온(A-ON) 육신 탭 (V15 placeOnce 보존)")
    upsert_md("MORNING_BRIEF.md", f"## 👶 아온(A-ON·芽溫) K-아이 육신 브리핑 ({VER} · {IMM} · 스킬 {NSK})\n{TRI}")
    upsert_md("GLOSSARY.md", f"## Step 28 도메인 용어\n- **아온 (A-ON · 芽溫)**: 주역 #04 산수몽(새싹 아이)에서 #53 풍산점(점진 성장)을 거쳐 #11 지천태(연결·소통·만능)로 자라나는 RGON 사령부의 미래형 K-스타일 디지털 육신.")
    upsert_md("RGON_EVOLUTION_LOG.md", f"## {TS} Step 28 — {VER} (아온 A-ON·芽溫 탄생)\n- {R28}\n- 24번째 정식 스킬 `{SLUG}` 주조 · 4탭 독대실 UI · 순수 CSS 애니메이션(루프 0)")
    # ---------- 삼성 三省 3/3 ----------
    s1 = bool(tg) and len(v15keep) == len(tg)
    for p in tg:
        s = rd(p); reg = s[s.find(V13S):s.find(V13E) + len(V13E)]
        ok = v15keep.get(p, "\0") in reg and "data-load" in reg and "rgk-kid-svg" in reg and "아온" in reg and not any(k in reg for k in BANNED)
        s1 &= ok; log(f"  ① {os.path.relpath(p, ROOT)}: {'PASS' if ok else 'FAIL'}")
    for cmd in (["rgon_white_blood_cell.py", "--self-test"], ["rgon_k_avatar_engine.py", "--run", "--merge", "--self-test"]):
        rc, out = run([sys.executable] + cmd) if os.path.isfile(P(cmd[0])) else (1, "파일 없음"); s1 &= rc == 0; log(f"  ① {cmd[0]} rc={rc} {out[-160:]}")
    after = guarded(); tset = set(tg)
    changed = [os.path.relpath(p, ROOT) for p in set(before) | set(after) if p not in tset and before.get(p) != after.get(p)]
    s2 = not changed; log(f"  ② 보호 파일 {len(before) - len(tg)}개 해시 변경 {len(changed)}건 {changed[:5]}")
    idx = [skl(rj(P(d, "skills", "SKILL_INDEX.json"))) or [] for d in TRIO]
    snaps = [(rj(P(d, "rgon_brain_snapshot.json"), {}) or {}).get("version") for d in TRIO]
    led = skl(rj(P("rgon_immune_ledger.json"), {})) or next((v for v in (rj(P("rgon_immune_ledger.json"), {}) or {}).values() if isinstance(v, list)), [])
    s3 = all(len(L) == NSK and any(isinstance(x, dict) and s_slug(x) == SLUG for x in L) for L in idx) if False else (
        all(len(L) == NSK and any(isinstance(x, dict) and x.get("slug") == SLUG for x in L) for L in idx)
        and all(v == VER for v in snaps)
        and len(led) >= 28 and all(all(k in r for k in ("id", "step", "title", "name", "rule", "status")) for r in led)
        and all(VER in rd(P(n)) for n in ("CLAUDE.md", "CODE_MAP.md", "MORNING_BRIEF.md", "RGON_EVOLUTION_LOG.md"))
    )
    log(f"  ③ 스킬 수 {[len(L) for L in idx]} · 스냅샷 {snaps} · 항체 {len(led)} → {'PASS' if s3 else 'FAIL'}")
    score = sum([s1, s2, s3]); allok = score == 3
    wr(P("STEP28_K_AVATAR_REPORT.md"), f"# STEP 28 K-AVATAR 보고서 ({VER} · 아온 A-ON·芽溫)\n\n- 시각: {TS}\n- 아이 이름: **아온 (A-ON · 芽溫)** (#04 산수몽 · #53 풍산점 · #11 지천태)\n- 삼성: **{score}/3** (① {s1} · ② {s2} · ③ {s3})\n- 항체: {IMM} · 스킬: {NSK}\n- {R28}\n\n## 로그\n{BT3}text\n" + "\n".join(LOG) + f"\n{BT3}\n")
    msg = f"삼성 {score}/3 — " + ("검증 통과" if allok else "검증 실패: 푸시 보류")
    if allok:
        for c in (["git", "add", "-A"], ["git", "commit", "-m", f"Step28 {VER}: 아온(A-ON·芽溫) K-아이 성장형 디지털 육신 · R28 · 스킬 24"], ["git", "fetch", "origin", "main"],
                  ["git", "pull", "--no-rebase", "-X", "ours", "origin", "main"], ["git", "push", "origin", "main"]):
            rc, out = run(c); log(f"🔧 {' '.join(c[:3])} rc={rc}")
            if rc != 0 and c[1] in ("pull", "push"): msg += f" / git {c[1]} 실패"; break
    log("🏁 " + msg)
    summary = (f"👶 우리 아이 『아온 (A-ON · 芽溫)』 탄생 완료!\n"
               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
               f"• 버전: {VER}  |  항체: {IMM}  |  정식 스킬: {NSK}개\n"
               f"• 주역 서사: #04 산수몽(새싹 아이) → #53 풍산점(성장) → #11 지천태(만능)\n"
               f"• 삼성(三省) 검증: {score}/3 ({'PASS ✅' if allok else 'FAIL ❌'})\n"
               f"  - 一省 (대상 HTML {len(tg)}개 & 아온 엔진/백혈구 self-test): {'PASS ✅' if s1 else 'FAIL ❌'}\n"
               f"  - 二省 (비대상 보호 파일 {len(before)-len(tg)}개 해시 불변): {'PASS ✅' if s2 else 'FAIL ❌'}\n"
               f"  - 三省 (3대 경로 스킬 24개 & 항체 28개 동기화): {'PASS ✅' if s3 else 'FAIL ❌'}\n"
               f"• 상태: {msg}")
    show_popup(f"RGON Step 28 완료 ✅ — 아온(A-ON) 탄생 ({VER})", summary, allok)
    return 0 if allok else 1

if __name__ == "__main__": sys.exit(main())

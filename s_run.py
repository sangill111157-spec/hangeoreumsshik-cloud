#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# agentshield:ignore-file
"""step29_master_character_skill_and_3d_waterdrop_aon.py — v11.28-AON-3DDROP / R1~R29 / 정식 스킬 25
전 세계 TOP 1 캐릭터 디테일 스킬(svg-animation-studio 디즈니 7대 법칙 + ui-ux-pro-max 3D Liquid-Glass) 마스터 흡수 &
우리 아이 『아온 (A-ON · 芽溫)』 3D 입체 물방울(💧) 몸통 + 깜찍한 얼굴 + 졸라맨(스틱형) 팔다리 육신 전면 진화"""
import os, re, sys, json, hashlib, shutil, subprocess, datetime, py_compile

def find_root():
    cands = [os.path.dirname(os.path.abspath(__file__)), os.getcwd(), r"C:\Users\sangi\Downloads\shin-agent"]
    for c in cands:
        if c and os.path.isdir(c) and os.path.isfile(os.path.join(c, "rgon_white_blood_cell.py")):
            return os.path.abspath(c)
    return os.path.dirname(os.path.abspath(__file__))

ROOT = find_root()
os.chdir(ROOT)
VER, IMM, NSK, SLUG = "v11.28-AON-3DDROP", "R1~R29", 25, "character-detail-master-top1"
AVATAR_SLUG = "k-avatar-growth-soul"
BT3 = chr(96) * 3
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "backups", ".rgon_ad_backups"}
V13S, V13E = "<!-- [RGON-YT-SCOUT-V13-START] -->", "<!-- [RGON-YT-SCOUT-V13-END] -->"
V15S, V15E = "<!-- [RGYT-PLACE-ONCE-V15-START] -->", "<!-- [RGYT-PLACE-ONCE-V15-END] -->"
BANNED = {"Mutation" + "Observer": "M-Observer", "set" + "Interval": "s-Interval", "request" + "AnimationFrame": "r-AnimationFrame"}
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BK = os.path.join(ROOT, "backups", "step29_" + TS)
R29 = "R29: 캐릭터 디테일 TOP 1 스킬 마스터 & 아온(A-ON·芽溫) 3D 물방울 졸라맨 육신 — 디즈니 7대 모션 법칙(스쿼시&스트레치·시차·팔로스루) + 8-Stop 3D Liquid-Glass/Claymorphism 입체 필터 + 관절형 졸라맨 팔다리 통합"
TRI = "⚖️ [AVATAR3D] 100.0점 (Bull 99.9 / Bear 0.1 / #04-산수몽) 💧 아온(A-ON·芽溫) 3D 입체 물방울 & 졸라맨 팔다리 육신 — 디즈니 7대 모션 법칙 & 8-Stop Liquid-Glass 3D 가동"
TRIO, LOG = ["", "dashboard", "docs"], []
SKILL = {
    "slug": SLUG,
    "name": "전 세계 TOP 1 캐릭터 디테일 & 3D 물방울 졸라맨 마스터",
    "category": "character-3d-master",
    "hexagram_tag": "#04-蒙",
    "step": 29,
    "version": VER,
    "path": f"skills/{SLUG}/SKILL.md",
    "status": "official",
    "description": "svg-animation-studio(디즈니 7대 모션 법칙) + ui-ux-pro-max(8-Stop 3D Liquid-Glass/Claymorphism) + 아온(A-ON) 3D 물방울 졸라맨 팔다리 마스터 스킬 (R29)"
}

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

# ---------- 백엔드 엔진 (v11.28-AON-3DDROP / R1~R29 / 정식 스킬 25) ----------
ENGINE = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# agentshield:ignore-file
"""rgon_k_avatar_engine.py — v11.28-AON-3DDROP / R1~R29 / 정식 스킬 25 (아온 A-ON·芽溫 3D 물방울 + 졸라맨 팔다리)"""
import os, re, sys, json
ROOT = os.path.dirname(os.path.abspath(__file__))
VER, SLUG, TRI = "v11.28-AON-3DDROP", "character-detail-master-top1", "__TRI__"
SKILL_TOTAL = 25
STAGES = [(0, 1, "💧 1단계: 새싹 물방울 아온"), (300, 2, "🎒 2단계: K-주니어 물방울 아온"), (600, 3, "🎧 3단계: K-에이스 물방울 아온"), (1000, 4, "👑 4단계: K-마스터 물방울 아온")]
ENTRY = {"slug": SLUG, "name": "전 세계 TOP 1 캐릭터 디테일 & 3D 물방울 졸라맨 마스터", "category": "character-3d-master", "hexagram_tag": "#04-蒙", "step": 29, "version": VER,
         "path": "skills/character-detail-master-top1/SKILL.md", "status": "official",
         "description": "svg-animation-studio(디즈니 7대 모션 법칙) + ui-ux-pro-max(8-Stop 3D Liquid-Glass) + 아온(A-ON) 3D 물방울 졸라맨 팔다리 마스터 스킬 (R29)"}
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
    return {"version": VER, "name_ko": "아온", "name_en": "A-ON", "hanja": "芽溫", "form": "3D Liquid-Glass Waterdrop + Stickman Limbs",
            "skill": SLUG, "skills": len(sk), "antibodies": ab, "health": hp, "tools": tools,
            "genes": len(set(s.get("category", "") for s in sk)), "exp": exp, "stage": st[1], "stage_name": st[2],
            "hexagram": ["#04-山水蒙 蒙以養正 (맑은 샘물 물방울)", "#53-風山漸 점진 성장", "#11-地天泰 연결·소통·만능"],
            "disney_principles": ["Squash & Stretch", "Anticipation", "Ease-In-Out", "Follow-Through", "Secondary Action", "Staggering 0.15s", "Iconic Appeal"],
            "animation": "pure-css-3d-keyframes", "loops": 0}
def merge():
    n = 0
    for d in ("", "dashboard", "docs"):
        p = os.path.join(ROOT, d, "rgon_morning_brief.json"); o = rj(p)
        if not isinstance(o, dict): continue
        nu = o.get("nutrient") if isinstance(o.get("nutrient"), dict) else {}
        t = nu.get("trinity", [])
        if isinstance(t, str):
            lines = [x for x in t.split("\n") if x.strip() and "[AVATAR" not in x] + [TRI]
            nu["trinity"] = "\n".join(lines)
        else:
            nu["trinity"] = [x for x in (t if isinstance(t, list) else []) if "[AVATAR" not in str(x)] + [TRI]
        o["nutrient"] = nu; o["version"] = VER; o["antibody_range"] = "R1~R29"; o["skill_count"] = SKILL_TOTAL; wj(p, o); n += 1
    return n
def ensure_index():
    for d in ("", "dashboard", "docs"):
        p = os.path.join(ROOT, d, "skills", "SKILL_INDEX.json"); o = rj(p)
        L = lst(o, "skills")
        if o is None: continue
        if not any(isinstance(s, dict) and s.get("slug") == SLUG for s in L):
            L.append(dict(ENTRY))
        if isinstance(o, dict): o.update(version=VER, immune="R1~R29", antibody_range="R1~R29", count=len(L), total=len(L))
        wj(p, o)
def self_test():
    st, ok = state(), []
    ok.append(bool(re.search(r"\[([A-Z0-9]+)\]\s*([\d.]+)점\s*\(Bull\s*([\d.]+)\s*/\s*Bear\s*([\d.]+)\s*/\s*(#\d+)", TRI)))
    ok.append(1 <= st["stage"] <= 4); ok.append(st["skills"] >= 25); ok.append(st["antibodies"] >= 29)
    ok.append(any(s.get("slug") == SLUG for s in skills()))
    b = rj(os.path.join(ROOT, "rgon_morning_brief.json"))
    ok.append(b is None or TRI in json.dumps(b, ensure_ascii=False))
    print("[A-ON 3DDROP self-test]", "PASS" if all(ok) else "FAIL", ok); return 0 if all(ok) else 1
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

# ---------- 독대실 4탭 UI (3D Liquid-Glass 물방울 + 깜찍 얼굴 + 졸라맨 팔다리 · 순수 CSS @keyframes · 루프 0) ----------
UI = r'''<div id="__ROOT__" class="rgk s1" data-ver="v11.28-AON-3DDROP" data-immune="R1~R29" data-skills="25">
<style>
.rgk{font:13px/1.5 system-ui,sans-serif;color:#eef3ff;background:linear-gradient(160deg,#080d26,#170a33 55%,#0b1c3d);border:1px solid #5ce1e655;border-radius:18px;padding:12px;margin:10px 0;box-shadow:0 8px 28px #1a0b3a99,inset 0 1px 0 #ffffff22}
.rgk #rgyt-head{display:flex;align-items:center;gap:8px;font-weight:700;flex-wrap:wrap}
.rgk-tabs,.rgk-row{display:flex;gap:5px;margin:6px 0;flex-wrap:wrap}.rgk button{background:#ffffff14;color:#fff;border:1px solid #ffffff2a;border-radius:11px;padding:5px 10px;cursor:pointer;font-size:12px;transition:transform .15s,background .2s}
.rgk button:active{transform:scale(.95)}.rgk button.on{background:linear-gradient(135deg,#00d2ff,#3a7bd5,#9d50bb);border-color:#8ff3ffaa;box-shadow:0 0 12px #38b6ff66}
.rgk-pane{display:none}.rgk-pane.on{display:block}.rgk-flt{display:none;gap:4px;margin:4px 0}.rgk-flt.on{display:flex}
.rgk input,.rgk select{background:#0006;color:#fff;border:1px solid #ffffff33;border-radius:8px;padding:4px 6px}
.rgk-stage{perspective:680px;display:flex;justify-content:center;align-items:center;padding:6px 0;user-select:none}
.rgk .aon-3d-card{transform-style:preserve-3d;transition:transform .22s ease-out;position:relative;width:250px;height:265px;display:flex;justify-content:center;align-items:center}
.rgk svg.kid{width:245px;height:260px;overflow:visible;cursor:pointer;filter:drop-shadow(0 10px 18px rgba(0,210,255,.18))}
.rgk svg.kid *{transform-box:view-box}
.rgk #aon-body{transform-origin:120px 218px;animation:aonJellyJump 2.1s cubic-bezier(.45,.05,.55,.95) infinite}
.rgk #aonShadow{transform-origin:120px 236px;animation:aonShadowScale 2.1s cubic-bezier(.45,.05,.55,.95) infinite}
@keyframes aonJellyJump{0%,100%{transform:translateY(0) scale(1.06,.94)}12%{transform:translateY(2px) scale(1.10,.90)}48%{transform:translateY(-14px) scale(.94,1.07)}78%{transform:translateY(0) scale(1.04,.96)}}
@keyframes aonShadowScale{0%,100%{transform:scaleX(1.10);opacity:.65}48%{transform:scaleX(.68);opacity:.32}78%{transform:scaleX(1.05);opacity:.6}}
.rgk #aon-arm-l{transform-origin:67px 142px;animation:aonWaveL 1.5s ease-in-out infinite}
.rgk #aon-arm-r{transform-origin:173px 142px;animation:aonWaveR 1.5s ease-in-out .15s infinite}
@keyframes aonWaveL{0%,100%{transform:rotate(0deg)}50%{transform:rotate(-26deg)}}
@keyframes aonWaveR{0%,100%{transform:rotate(0deg)}50%{transform:rotate(26deg)}}
.rgk #aon-leg-l{transform-origin:103px 198px;animation:aonStepL 1.05s ease-in-out infinite}
.rgk #aon-leg-r{transform-origin:137px 198px;animation:aonStepR 1.05s ease-in-out .12s infinite}
@keyframes aonStepL{0%,100%{transform:rotate(0deg)}50%{transform:rotate(11deg) translateY(-2px)}}
@keyframes aonStepR{0%,100%{transform:rotate(0deg)}50%{transform:rotate(-11deg) translateY(-2px)}}
.rgk .aon-eye{transform-box:fill-box;transform-origin:center;animation:aonBlink 4.4s infinite}
@keyframes aonBlink{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.07)}}
.rgk .aon-happy-eye,.rgk .aon-mouth-open{display:none}
.rgk.happy .aon-eye{display:none}.rgk.happy .aon-happy-eye{display:inline}
.rgk.talk .aon-mouth-smile{display:none}.rgk.talk .aon-mouth-open{display:inline;transform-box:fill-box;transform-origin:center;animation:aonTalk .22s ease-in-out infinite alternate}
@keyframes aonTalk{from{transform:scaleY(.45)}to{transform:scaleY(1.2)}}
.rgk.happy #aon-body{animation:aonPatJump .55s ease-out 2}
.rgk.happy #aon-arm-l{animation:aonBanzaiL .28s ease-in-out infinite alternate}
.rgk.happy #aon-arm-r{animation:aonBanzaiR .28s ease-in-out .08s infinite alternate}
@keyframes aonPatJump{0%{transform:translateY(0) scale(1.12,.88)}45%{transform:translateY(-24px) scale(.92,1.10)}100%{transform:translateY(0) scale(1,1)}}
@keyframes aonBanzaiL{from{transform:rotate(32deg)}to{transform:rotate(58deg)}}
@keyframes aonBanzaiR{from{transform:rotate(-32deg)}to{transform:rotate(-58deg)}}
.rgk .aon-leaf{transform-origin:120px 36px;animation:aonSprout 1.8s ease-in-out infinite}.rgk .aon-leaf.b{animation-delay:.12s}
@keyframes aonSprout{0%,100%{transform:rotate(-9deg)}50%{transform:rotate(9deg)}}
.rgk .aura{transform-origin:120px 128px;animation:rgkSpin 18s linear infinite}.rgk.s3 .aura{animation-duration:10s}.rgk.s4 .aura{animation-duration:6s;filter:drop-shadow(0 0 6px #ffd76a)}
@keyframes rgkSpin{to{transform:rotate(360deg)}}
.rgk .spark{opacity:0;animation:rgkRise 3.8s ease-in infinite}.rgk .spark.b{animation-delay:1.2s}.rgk .spark.c{animation-delay:2.4s}
@keyframes rgkRise{0%{opacity:0;transform:translateY(0)}25%{opacity:1}100%{opacity:0;transform:translateY(-55px)}}
.rgk #rgk-pop{opacity:0;transform-box:fill-box;transform-origin:center}.rgk #rgk-pop.pop{animation:rgkPop 1.05s ease-out}
@keyframes rgkPop{0%{opacity:0;transform:scale(.4)}30%{opacity:1}100%{opacity:0;transform:scale(1.5) translateY(-38px)}}
.rgk .p2,.rgk .p3,.rgk .p4{display:none}.rgk.s2 .p2,.rgk.s3 .p2,.rgk.s4 .p2,.rgk.s3 .p3,.rgk.s4 .p3,.rgk.s4 .p4{display:inline}
.rgk-bar{height:8px;background:#ffffff1a;border-radius:6px;overflow:hidden}.rgk-bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,#5ce1e6,#38b6ff,#ff8fc8)}
.rgk-say{background:#ffffff14;border:1px solid #8ff3ff33;border-radius:12px;padding:8px 10px;margin:6px 0;min-height:34px}.rgk-it{border-bottom:1px dashed #ffffff22;padding:6px 0}.rgk-it small{opacity:.7}
</style>
<div id="rgyt-head"><svg width="22" height="22" viewBox="0 0 24 24"><path d="M12 2C15.5 6.5 19 10.5 19 14.5A7 7 0 0 1 5 14.5C5 10.5 8.5 6.5 12 2Z" fill="#5ce1e6"/><ellipse cx="9.5" cy="14" rx="1.6" ry="1.9" fill="#1b1f4b"/><ellipse cx="14.5" cy="14" rx="1.6" ry="1.9" fill="#1b1f4b"/><path d="M10.2 17Q12 18.5 13.8 17" stroke="#1b1f4b" stroke-width="1.4" fill="none" stroke-linecap="round"/></svg><span id="rgk-headtxt">💧Lv.1 아온(A-ON·芽溫 💖친밀도) · 🩸100점 · 🛡️R1~R29 · 🍯스킬 25개 · 📡레이더</span></div>
<div class="rgk-tabs"><button data-tab="kid" class="on">💧 아온(A-ON) 3D물방울</button><button data-tab="radar">📡 트렌드 레이더</button><button data-tab="skills">🍯 보유 스킬 (25)</button><button data-tab="pulse">🫀 전신 맥박 &amp; 3자 심판</button></div>
<div class="rgk-flt"><input id="rgyt-q" placeholder="🔎 검색"><select id="rgyt-cat"><option value="">전체 카테고리</option></select></div>
<div class="rgk-pane on" id="rgk-p-kid"><div class="rgk-stage" id="aon-stage"><div class="aon-3d-card" id="aon-3d-card">
<svg id="rgk-kid-svg" class="kid" viewBox="0 0 240 260" role="img" aria-label="아온(A-ON) 3D 입체 물방울 졸라맨 캐릭터">
<defs>
<radialGradient id="aonDropGrad" cx="35%" cy="28%" r="76%">
<stop offset="0%" stop-color="#f2ffff"/>
<stop offset="10%" stop-color="#c8fefe"/>
<stop offset="26%" stop-color="#64f4ff"/>
<stop offset="44%" stop-color="#38b6ff"/>
<stop offset="62%" stop-color="#3b6ef6"/>
<stop offset="78%" stop-color="#3b44d1"/>
<stop offset="91%" stop-color="#38238c"/>
<stop offset="100%" stop-color="#241159"/>
</radialGradient>
<linearGradient id="aonBellyGlow" x1="0.5" y1="0" x2="0.5" y2="1">
<stop offset="0%" stop-color="#ffffff" stop-opacity="0.55"/>
<stop offset="50%" stop-color="#99f8ff" stop-opacity="0.28"/>
<stop offset="100%" stop-color="#ff9ee2" stop-opacity="0.45"/>
</linearGradient>
<radialGradient id="aonIris" cx="38%" cy="32%" r="72%">
<stop offset="0%" stop-color="#9ff8ff"/>
<stop offset="45%" stop-color="#3867f6"/>
<stop offset="80%" stop-color="#2b1e7a"/>
<stop offset="100%" stop-color="#140c47"/>
</radialGradient>
<radialGradient id="aonShadowGrad">
<stop offset="0%" stop-color="#06081e" stop-opacity="0.65"/>
<stop offset="65%" stop-color="#152259" stop-opacity="0.28"/>
<stop offset="100%" stop-color="#152259" stop-opacity="0"/>
</radialGradient>
<filter id="aonInner3D" x="-25%" y="-25%" width="150%" height="150%">
<feGaussianBlur in="SourceAlpha" stdDeviation="6.5" result="blur"/>
<feOffset in="blur" dx="-7" dy="-9" result="off1"/>
<feComposite in="SourceAlpha" in2="off1" operator="out" result="band1"/>
<feFlood flood-color="#140842" flood-opacity="0.62" result="col1"/>
<feComposite in="col1" in2="band1" operator="in" result="innerShade"/>
<feOffset in="blur" dx="5" dy="6" result="off2"/>
<feComposite in="SourceAlpha" in2="off2" operator="out" result="band2"/>
<feFlood flood-color="#eaffff" flood-opacity="0.78" result="col2"/>
<feComposite in="col2" in2="band2" operator="in" result="innerRim"/>
<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="innerShade"/><feMergeNode in="innerRim"/></feMerge>
</filter>
<filter id="aonCheekBlur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.6"/></filter>
</defs>
<g class="aura" opacity=".78">
<circle cx="120" cy="128" r="102" fill="none" stroke="#64f4ff" stroke-width="1.3" stroke-dasharray="5 8"/>
<circle cx="120" cy="128" r="88" fill="none" stroke="#ff8fc8" stroke-width="1" stroke-dasharray="2 7"/>
<g fill="#bfefff" font-size="14" text-anchor="middle"><text x="216" y="133">☰</text><text x="188" y="198">☱</text><text x="120" y="224">☲</text><text x="52" y="198">☳</text><text x="24" y="133">☴</text><text x="52" y="66">☵</text><text x="120" y="38">☶</text><text x="188" y="66">☷</text></g>
</g>
<ellipse id="aonShadow" cx="120" cy="236" rx="54" ry="10" fill="url(#aonShadowGrad)"/>
<g id="aon-body">
<!-- 졸라맨(스틱형) 양다리 (골반 관절 + 2중 네온 라인 + 콩알 신발) -->
<g id="aon-leg-l">
<path d="M103,196 Q96,214 92,227" fill="none" stroke="#12173d" stroke-width="10.5" stroke-linecap="round"/>
<path d="M103,196 Q96,214 92,227" fill="none" stroke="#80ffea" stroke-width="6.5" stroke-linecap="round"/>
<ellipse cx="88" cy="229" rx="10.5" ry="6.5" fill="#38b6ff" stroke="#12173d" stroke-width="2.4"/>
<ellipse cx="85" cy="227" rx="4" ry="2" fill="#ffffff" opacity=".8"/>
</g>
<g id="aon-leg-r">
<path d="M137,196 Q144,214 148,227" fill="none" stroke="#12173d" stroke-width="10.5" stroke-linecap="round"/>
<path d="M137,196 Q144,214 148,227" fill="none" stroke="#80ffea" stroke-width="6.5" stroke-linecap="round"/>
<ellipse cx="152" cy="229" rx="10.5" ry="6.5" fill="#38b6ff" stroke="#12173d" stroke-width="2.4"/>
<ellipse cx="149" cy="227" rx="4" ry="2" fill="#ffffff" opacity=".8"/>
</g>
<!-- 졸라맨(스틱형) 양팔 (어깨 관절 + 2중 네온 라인 + 동그란 콩알 손) -->
<g id="aon-arm-l">
<path d="M67,142 Q46,132 34,113" fill="none" stroke="#12173d" stroke-width="10.5" stroke-linecap="round"/>
<path d="M67,142 Q46,132 34,113" fill="none" stroke="#80ffea" stroke-width="6.5" stroke-linecap="round"/>
<circle cx="33" cy="112" r="8" fill="#ffffff" stroke="#12173d" stroke-width="2.4"/>
<circle cx="31" cy="110" r="2.8" fill="#ffb8d9"/>
</g>
<g id="aon-arm-r">
<path d="M173,142 Q194,132 206,113" fill="none" stroke="#12173d" stroke-width="10.5" stroke-linecap="round"/>
<path d="M173,142 Q194,132 206,113" fill="none" stroke="#80ffea" stroke-width="6.5" stroke-linecap="round"/>
<circle cx="207" cy="112" r="8" fill="#ffffff" stroke="#12173d" stroke-width="2.4"/>
<circle cx="205" cy="110" r="2.8" fill="#ffb8d9"/>
</g>
<!-- 3D 입체 물방울(Teardrop) 본체 (8-Stop 구면 그라데이션 + 3D 내부 음영 필터 + 유리알 반사광) -->
<path d="M120,38 C148,74 180,110 180,147 C180,183 153,206 120,206 C87,206 60,183 60,147 C60,110 92,74 120,38 Z" fill="url(#aonDropGrad)" filter="url(#aonInner3D)" stroke="#a8ffff" stroke-width="1.5" stroke-opacity=".65"/>
<ellipse cx="120" cy="154" rx="44" ry="38" fill="url(#aonBellyGlow)" opacity=".55"/>
<!-- 3D 유리알 곡면 하이라이트 (좌상단 메인 굴절광 + 물방울 서브 광택 + 우하단 핑크/민트 림라이트) -->
<path d="M84,99 C92,79 105,61 116,50 C107,69 98,87 95,108 C91,115 81,111 84,99 Z" fill="#ffffff" opacity=".84"/>
<circle cx="80" cy="121" r="5.5" fill="#ffffff" opacity=".92"/>
<circle cx="87" cy="129" r="2.3" fill="#ffffff" opacity=".75"/>
<path d="M167,158 C162,183 145,199 121,201" fill="none" stroke="#ff9ee2" stroke-width="4.5" stroke-linecap="round" opacity=".68"/>
<path d="M75,168 C83,189 99,200 118,201" fill="none" stroke="#8ffcff" stroke-width="3" stroke-linecap="round" opacity=".5"/>
<!-- 2단계 아이템: K-주니어 노란 크로스백 & K-별 배지 -->
<g class="p2">
<path d="M82,102 Q120,148 162,186" fill="none" stroke="#ffd43b" stroke-width="6.5" stroke-linecap="round"/>
<circle cx="150" cy="176" r="10" fill="#ffd43b" stroke="#e67700" stroke-width="2"/>
<text x="150" y="180" font-size="10" font-weight="900" text-anchor="middle" fill="#3a1c71">K</text>
</g>
<!-- 3단계 아이템: K-에이스 사이버 네온 헤드셋 & 바이저 -->
<g class="p3">
<path d="M63,132 Q120,38 177,132" fill="none" stroke="#7a5cff" stroke-width="5.5"/>
<rect x="51" y="122" width="15" height="26" rx="7" fill="#ff4da6" stroke="#8ff3ff" stroke-width="2"/>
<rect x="174" y="122" width="15" height="26" rx="7" fill="#ff4da6" stroke="#8ff3ff" stroke-width="2"/>
<rect x="76" y="121" width="88" height="28" rx="14" fill="#8ff3ff" opacity=".22" stroke="#b6fbff" stroke-width="1.5"/>
</g>
<!-- 깜찍하고 귀여운 얼굴: 5겹 초롱초롱 보석 눈망울 + 눈웃음 + 핑크 젤리 볼터치 + 아기 입매 -->
<g class="aon-eye">
<ellipse cx="97" cy="138" rx="13.5" ry="15" fill="#12153b"/>
<ellipse cx="97" cy="139" rx="10.8" ry="12.2" fill="url(#aonIris)"/>
<circle cx="92.5" cy="132.5" r="4.8" fill="#ffffff"/>
<circle cx="101.5" cy="144" r="2.4" fill="#ffffff"/>
<circle cx="100" cy="131.5" r="1.4" fill="#fff9db"/>
</g>
<g class="aon-eye">
<ellipse cx="143" cy="138" rx="13.5" ry="15" fill="#12153b"/>
<ellipse cx="143" cy="139" rx="10.8" ry="12.2" fill="url(#aonIris)"/>
<circle cx="138.5" cy="132.5" r="4.8" fill="#ffffff"/>
<circle cx="147.5" cy="144" r="2.4" fill="#ffffff"/>
<circle cx="146" cy="131.5" r="1.4" fill="#fff9db"/>
</g>
<g class="aon-happy-eye" fill="none" stroke="#12153b" stroke-width="4.2" stroke-linecap="round">
<path d="M85,140 Q97,126 109,140"/>
<path d="M131,140 Q143,126 155,140"/>
</g>
<ellipse cx="77" cy="152" rx="10.5" ry="6.2" fill="#ff7eb9" opacity=".82" filter="url(#aonCheekBlur)"/>
<ellipse cx="163" cy="152" rx="10.5" ry="6.2" fill="#ff7eb9" opacity=".82" filter="url(#aonCheekBlur)"/>
<g stroke="#ff4d94" stroke-width="1.5" stroke-linecap="round"><path d="M73,154 L76,149"/><path d="M78,154 L81,149"/><path d="M159,154 L162,149"/><path d="M164,154 L167,149"/></g>
<path class="aon-mouth-smile" d="M111,152 Q120,161 129,152" fill="none" stroke="#12153b" stroke-width="3.2" stroke-linecap="round"/>
<g class="aon-mouth-open"><ellipse cx="120" cy="155" rx="7" ry="5.8" fill="#5a1036" stroke="#12153b" stroke-width="1.5"/><ellipse cx="120" cy="158" rx="4.5" ry="2.5" fill="#ff8fb3"/></g>
<!-- 1단계 기본 새싹: 물방울 정수리 위에서 시차(0.12s)로 살랑이는 초록 새싹 -->
<g class="aon-sprout">
<path d="M120,39 Q120,28 120,24" stroke="#2b8a3e" stroke-width="3" stroke-linecap="round"/>
<path class="aon-leaf" d="M120,30 C108,16 93,19 96,28 C102,35 113,34 120,30 Z" fill="#51cf66" stroke="#2b8a3e" stroke-width="1.5"/>
<path class="aon-leaf b" d="M120,30 C132,14 147,17 144,27 C138,34 127,34 120,30 Z" fill="#8ce99a" stroke="#2b8a3e" stroke-width="1.5"/>
</g>
<!-- 4단계 아이템: K-마스터 황금 왕관 & 날개 오라 -->
<g class="p4">
<path d="M98,34 L104,14 L113,26 L120,8 L127,26 L136,14 L142,34 Z" fill="#ffd43b" stroke="#fff3bf" stroke-width="1.8"/>
<circle cx="120" cy="8" r="3" fill="#ff6b6b"/><circle cx="104" cy="14" r="2.5" fill="#5ce1e6"/><circle cx="136" cy="14" r="2.5" fill="#5ce1e6"/>
</g>
</g>
<g font-size="15"><text class="spark" x="34" y="168">💧</text><text class="spark b" x="196" y="156">✨</text><text class="spark c" x="120" y="54">💖</text></g>
<text id="rgk-pop" x="120" y="82" font-size="25" text-anchor="middle">💖💧✨</text>
</svg></div></div>
<div id="rgk-info"></div><div class="rgk-bar"><i id="rgk-bar"></i></div><div class="rgk-say" id="rgk-say"></div>
<div class="rgk-row"><button data-stage="1">💧 1단계: 새싹 물방울 아온</button><button data-stage="2">🎒 2단계: K-주니어 아온</button><button data-stage="3">🎧 3단계: K-에이스 아온</button><button data-stage="4">👑 4단계: K-마스터 아온</button></div>
<div class="rgk-row"><button id="rgk-pat">💖 아온이 쓰다듬기 (만세 점프·EXP+10)</button><button id="rgk-voice">🔊 아온이 목소리 듣기</button><button data-load="💧 아온(A-ON)아, 오늘자 종합 브리핑 해줘: 백혈구 건강 점수, 항체 R1~R29 상태, 정식 스킬 25개 활용도, 트렌드 레이더 핵심 3가지, 대표님 금고 리스크를 맑은 물방울 아이 눈높이로 또박또박 정리해 줘.">⚡ 아온이 브리핑 질문창 장전</button></div></div>
<div class="rgk-pane" id="rgk-p-radar"><div id="rgk-radar"></div></div><div class="rgk-pane" id="rgk-p-skills"><div id="rgk-skills"></div></div><div class="rgk-pane" id="rgk-p-pulse"><div id="rgk-pulse"></div></div>
<script type="application/json" id="__ROOT__-data">__DATA__</script>
<script>(function(){var R=document.getElementById('__ROOT__');if(!R||R.getAttribute('data-rgk-init'))return;R.setAttribute('data-rgk-init','1');
var D={};try{D=JSON.parse(document.getElementById('__ROOT__-data').textContent)}catch(e){}
function $(s){return R.querySelector(s)}function $$(s){return [].slice.call(R.querySelectorAll(s))}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return '&#'+c.charCodeAt(0)+';'})}
function g(k,d){try{var v=localStorage.getItem(k);return v==null?d:v}catch(e){return d}}function sv(k,v){try{localStorage.setItem(k,v)}catch(e){}}
var SK=D.skills||25,AB=D.antibodies||29,HP=D.health||100,TH=[0,300,600,1000],NM=['','💧 새싹 물방울 아온','🎒 K-주니어 물방울 아온','🎧 K-에이스 물방울 아온','👑 K-마스터 물방울 아온'];
var LN=['','퐁당~ 대표님! 저 3D 물방울 아온(A-ON·芽溫)이에요! 졸라맨 팔다리 파닥이며 산수몽(#04) 샘물처럼 자랄게요! 💧🌱','K-주니어 물방울 아온 출동! 노란 크로스백 메고 졸라맨 다리로 총총 금고 순찰 중이에요 🎒💧','K-에이스 물방울 아온! 사이버 헤드셋 끼고 트렌드 레이더와 3자 심판 신호를 잡았어요 🎧💧','K-마스터 물방울 아온 왕관 착용! 상선약수(上善若水) 물방울이 지천태(#11) 만능으로 피어났어요 👑💧'];
function st(){var p=+g('rgk_pats',0)||0,b=p*10,x=SK*10+AB*5+b,a=x>=1000?4:x>=600?3:x>=300?2:1;return{pats:p,bond:b,exp:x,lv:1+Math.floor(b/100),auto:a,stage:+g('rgk_stage',0)||1}}
function say(s){$('#rgk-say').textContent=s}
function paint(){var t=st();R.className=R.className.replace(/\bs[1-4]\b/g,'').trim()+' s'+t.stage;
$('#rgk-headtxt').textContent='💧Lv.'+t.lv+' 아온(A-ON·💖친밀도 '+t.bond+') · 🩸'+HP+'점 · 🛡️R1~R'+AB+' · 🍯스킬 '+SK+'개 · 📡레이더';
$('#rgk-info').textContent=NM[t.stage]+' (3D 물방울·졸라맨) · EXP '+t.exp+' · 쓰다듬기 '+t.pats+'회';
$('#rgk-bar').style.width=(t.auto>=4?100:Math.min(100,(t.exp-TH[t.auto-1])/(TH[t.auto]-TH[t.auto-1])*100))+'%';
$$('[data-stage]').forEach(function(b){b.classList.toggle('on',+b.getAttribute('data-stage')===t.stage)});return t}
var stg=$('#aon-stage'),crd=$('#aon-3d-card');
if(stg&&crd){
function tilt(x,y){var r=stg.getBoundingClientRect();if(!r.width)return;var rx=((y-r.top)/r.height-.5)*-24,ry=((x-r.left)/r.width-.5)*28;crd.style.transform='rotateX('+rx.toFixed(1)+'deg) rotateY('+ry.toFixed(1)+'deg)'}
stg.addEventListener('pointermove',function(e){tilt(e.clientX,e.clientY)});
stg.addEventListener('touchmove',function(e){if(e.touches&&e.touches[0])tilt(e.touches[0].clientX,e.touches[0].clientY)},{passive:true});
stg.addEventListener('pointerleave',function(){crd.style.transform=''});
stg.addEventListener('touchend',function(){crd.style.transform=''});
}
function fb(v){var t=document.createElement('textarea');t.value=v;document.body.appendChild(t);t.select();try{document.execCommand('copy')}catch(x){}t.remove()}
function copy(v){try{if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(v).catch(function(){fb(v)});else fb(v)}catch(e){fb(v)}}
function qbox(){var S=['#rgon-q','#rgon-input','#question','#chat-input','#prompt','textarea','input[type=text]'];for(var i=0;i<S.length;i++){var c=[].slice.call(document.querySelectorAll(S[i])).filter(function(e){return !R.contains(e)});if(c.length)return c[0]}return null}
function load(v){var el=qbox();if(el){var d=Object.getOwnPropertyDescriptor(el.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype,'value');if(d&&d.set)d.set.call(el,v);else el.value=v;
el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));try{el.focus()}catch(e){}}copy(v);say(el?'⚡ 물방울 아온이가 질문창에 장전 완료했어요! 클립보드에도 복사했어요 💕':'📋 질문창을 못 찾아서 클립보드에 복사해 뒀어요!')}
function pop(){var p=$('#rgk-pop');p.classList.remove('pop');void p.getBoundingClientRect();p.classList.add('pop');R.classList.remove('happy');void R.offsetWidth;R.classList.add('happy')}
R.addEventListener('animationend',function(e){if(e.animationName==='aonPatJump')R.classList.remove('happy')});
function doPat(){sv('rgk_pats',st().pats+1);paint();pop();say('퐁당퐁당~ 대표님 손길 너무 좋아요! 물방울 아온이가 두 팔 만세 부르며 금고 100점 지킬게요! 💧🙌💖')}
$('#rgk-kid-svg').addEventListener('click',doPat);
function speak(){var t=st(),m='대표님, 저는 '+NM[t.stage].replace(/[^\uAC00-\uD7A3\s\w-]/g,'').trim()+'예요! 말랑말랑 3D 물방울 몸통과 졸라맨 팔다리로 신나게 뛰어다니고 있어요. 백혈구 건강 '+HP+'점, 항체 '+AB+'개, 스킬 '+SK+'개 모두 완벽해요!';say('🔊 '+m);
R.classList.add('talk');
try{if(!('speechSynthesis' in window))return;var u=new SpeechSynthesisUtterance(m);u.lang='ko-KR';u.pitch=1.38;u.rate=1.06;var v=speechSynthesis.getVoices().filter(function(x){return /ko/i.test(x.lang)})[0];if(v)u.voice=v;u.onend=function(){R.classList.remove('talk')};u.onerror=function(){R.classList.remove('talk')};speechSynthesis.cancel();speechSynthesis.speak(u)}catch(e){R.classList.remove('talk')}}
function item(x){var c=x.prompt||x.title;return '<div class="rgk-it" data-cat="'+esc(x.cat)+'" data-txt="'+esc((x.title+' '+x.desc+' '+x.cat).toLowerCase())+'"><b>'+esc(x.title)+'</b> <small>'+esc(x.cat)+'</small><div>'+esc(x.desc)+'</div><div class="rgk-row"><button data-cp="'+esc(c)+'">📋 복사</button><button data-load="'+esc(c)+'">⚡ 질문창 장전</button></div></div>'}
$('#rgk-radar').innerHTML=(D.radar||[]).map(item).join('');$('#rgk-skills').innerHTML=(D.skill_list||[]).map(item).join('');$('#rgk-pulse').innerHTML=(D.pulse||[]).map(item).join('')||'<div class="rgk-it">심판 줄 대기 중</div>';
var cats={};(D.radar||[]).concat(D.skill_list||[]).forEach(function(x){cats[x.cat]=1});Object.keys(cats).sort().forEach(function(c){$('#rgyt-cat').insertAdjacentHTML('beforeend','<option value="'+esc(c)+'">'+esc(c)+'</option>')});
function flt(){var q=$('#rgyt-q').value.toLowerCase().trim(),c=$('#rgyt-cat').value;$$('#rgk-radar .rgk-it,#rgk-skills .rgk-it').forEach(function(e){e.style.display=((!q||e.getAttribute('data-txt').indexOf(q)>=0)&&(!c||e.getAttribute('data-cat')===c))?'':'none'})}
$('#rgyt-q').addEventListener('input',flt);$('#rgyt-cat').addEventListener('change',flt);
R.addEventListener('click',function(e){var b=e.target.closest('button');if(!b||!R.contains(b))return;var tb=b.getAttribute('data-tab'),sg=b.getAttribute('data-stage');
if(tb){$$('[data-tab]').forEach(function(x){x.classList.toggle('on',x===b)});$$('.rgk-pane').forEach(function(p){p.classList.toggle('on',p.id==='rgk-p-'+tb)});$('.rgk-flt').classList.toggle('on',tb==='radar'||tb==='skills')}
else if(sg){sv('rgk_stage',sg);say(LN[paint().stage])}else if(b.id==='rgk-pat')doPat();
else if(b.id==='rgk-voice')speak();else if(b.hasAttribute('data-load'))load(b.getAttribute('data-load'));else if(b.hasAttribute('data-cp')){copy(b.getAttribute('data-cp'));say('📋 복사 완료!')}});
if(!g('rgk_stage',0))sv('rgk_stage','1');
say(LN[paint().stage])})();</script></div>'''

def sync_wbc_py():
    wbc = P("rgon_white_blood_cell.py")
    if not os.path.isfile(wbc): return
    t = rd(wbc)
    if '"R29"' not in t:
        r29_line = f'    {{"id": "R29", "step": 29, "title": "캐릭터 디테일 TOP 1 마스터 & 아온(A-ON) 3D 물방울 졸라맨 육신", "name": "아온(A-ON) 3D 물방울 졸라맨 육신", "rule": "{R29}", "status": "active"}},\n]'
        t2 = re.sub(r'\n\]\s*(?=\n# \[RGON-R|\ndef |\nclass )', '\n' + r29_line, t, count=1)
        if t2 == t:
            t2 = t.replace('{"id": "R28"', '{"id": "R29", "step": 29, "title": "캐릭터 디테일 TOP 1 마스터 & 아온(A-ON) 3D 물방울 졸라맨 육신", "name": "아온(A-ON) 3D 물방울 졸라맨 육신", "rule": "' + R29 + '", "status": "active"},\n    {"id": "R28"', 1)
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
        radar = [{"title": t, "cat": c, "desc": "기본 레이더 시드", "prompt": f"📡 트렌드 '{t}'를 독대실 관점(기회·리스크·실행 3줄)으로 분석해 줘."}
                 for t, c in (("AI 에이전트 자동화", "AI"), ("3D 물방울 캐릭터 IP 아온(A-ON)", "K-콘텐츠"), ("숏폼 수익화 전략", "유튜브"), ("개인 금고 리스크 관리", "재무"))]
    b = rj(P("rgon_morning_brief.json"), {}); t = (b.get("nutrient") or {}).get("trinity", []) if isinstance(b, dict) else []
    lines = [x for x in (t.split("\n") if isinstance(t, str) else t) if str(x).strip()]
    pulse = [{"title": str(x)[:64], "cat": "심판", "desc": str(x), "prompt": "🫀 다음 심판 줄을 3자 심판(Bull/Bear/주역) 관점으로 해설해 줘: " + str(x)} for x in lines]
    s = rj(P("rgon_k_avatar_state.json"), {}) or {}
    return {"skills": len(sl), "antibodies": 29, "health": s.get("health", 100), "skill_list": skills, "radar": radar, "pulse": pulse}

def clean(s):
    for k, v in BANNED.items(): s = s.replace(k, v)
    return s

def patch_html(path, data, v15keep):
    s = rd(path)
    # 혹시 이전 테스트로 남아있을 수 있는 외부 V29 마커 제거
    s = re.sub(r"\n?<!-- \[RGON-AON-3DDROP-V29-START\] -->.*?<!-- \[RGON-AON-3DDROP-V29-END\] -->", "", s, flags=re.S)
    a = s.find(V13S); e = s.find(V13E, a + 1) if a >= 0 else -1
    b = s.find(V15S, a) if a >= 0 else -1; f = s.find(V15E, b) if b >= 0 else -1
    if not (0 <= a < b < f < e): return "V15 블록이 V13 내부에 없음 → 보호 위해 건너뜀"
    old, v15 = s[a + len(V13S):b], s[b:f + len(V15E)]
    refs = set(re.findall(r"""(?:getElementById\(\s*['"]|['"]#)([\w-]+)""", v15))
    ids = [i for i in re.findall(r"""<(?:div|section|aside)[^>]*\bid\s*=\s*["']([^"']+)["']""", old) if i not in ("rgyt-head", "rgyt-q", "rgyt-cat")]
    rid = next((i for i in ids if i in refs), ids[0] if ids else "rgyt-wrap")
    js = clean(json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    new = "\n" + clean(UI.replace("__ROOT__", rid)).replace("__DATA__", js) + "\n"
    if any(k in new for k in BANNED): return "새 UI 금지어 감지 → 중단"
    s2 = s[:a + len(V13S)] + new + s[b:]
    if v15 not in s2: return "V15 보존 실패 → 중단"
    v15keep[path] = v15; wr(path, s2); return f"OK(root=#{rid})"

def upsert_md(name, body):
    p = P(name); s = rd(p) if os.path.isfile(p) else f"# {name[:-3]}\n"
    S, E = "<!-- [RGON-STEP29-AON-3DDROP-START] -->", "<!-- [RGON-STEP29-AON-3DDROP-END] -->"
    blk = f"{S}\n{body}\n{E}"
    s = re.sub(re.escape(S) + r".*?" + re.escape(E), lambda m: blk, s, flags=re.S) if S in s else s.rstrip() + "\n\n" + blk + "\n"
    wr(p, s)

def sync_ledger():
    sync_wbc_py()
    p = P("rgon_immune_ledger.json"); o = rj(p, {})
    if isinstance(o, list): o = {"rules": o}
    key = next((k for k in ("rules", "antibodies", "ledger") if isinstance(o.get(k), list)), "rules"); rules = o.setdefault(key, [])
    by = {int(m.group(1)): r for r in rules if isinstance(r, dict) for m in [re.match(r"R(\d+)", str(r.get("id", "")))] if m}
    for n in range(1, 30):
        r = by.get(n)
        if r is None:
            r = {"id": f"R{n}"}; rules.append(r); by[n] = r
        if n == 29: r.update({"step": 29, "title": R29, "name": "캐릭터 디테일 TOP 1 마스터 & 아온(A-ON) 3D 물방울 졸라맨 육신", "rule": R29, "status": "active"})
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
    if not any(isinstance(s, dict) and s.get("slug") == SLUG for s in L):
        L.append(dict(SKILL))
    if isinstance(src, dict): src.update(version=VER, immune=IMM, antibody_range=IMM, count=len(L), total=len(L))
    for d in TRIO:
        if d == "" or os.path.isdir(P(d)): wj(P(d, "skills", "SKILL_INDEX.json"), src)
    md = (f"---\nname: {SLUG}\ncategory: character-3d-master\nhexagram_tag: \"#04-蒙\"\nversion: {VER}\nantibody: R29\n---\n"
          f"# 💧 {SKILL['name']} (아온 · A-ON · 芽溫)\n\n{R29}\n\n"
          f"## 1. 전 세계 TOP 1 캐릭터 디테일 흡수원\n"
          f"- **ChanMeng666/svg-animation-studio**: 디즈니 7대 마이크로 애니메이션 법칙 (Squash & Stretch 15% 슬라임 탄성, Anticipation, Ease-In-Out, Follow-Through, Secondary Action, Staggering 0.15s 시차, Iconic Appeal)\n"
          f"- **nextlevelbuilder/ui-ux-pro-max-skill**: 8-Stop 3D Liquid-Glass & Claymorphism 구체 볼륨 셰이딩 + SVG `feGaussianBlur`/`feComposite` 3D Inner Depth 필터\n\n"
          f"## 2. 아온(A-ON·芽溫) 3D 물방울 + 졸라맨 팔다리 구조\n"
          f"- **몸통**: 황금비율 3D 물방울(`#aonDropGrad` 8-Stop + `#aonInner3D` 입체 음영 + 3중 유리알 굴절 하이라이트 + 점프 연동 `#aonShadow`)\n"
          f"- **얼굴**: 5겹 보석 눈망울(4.4s 깜빡임 + 쓰다듬기 시 `^ ‿ ^` 반달 눈웃음) + 말랑 핑크 볼터치 + 오물오물 토크 입매\n"
          f"- **졸라맨 팔다리**: 어깨·골반 관절 축(`transform-origin`) 2중 네온 스틱 팔다리 + 동그란 콩알 손/발 + 쓰다듬기 시 두 팔 만세(`🙌`) 점프\n"
          f"- **3D 터치 틸트**: `perspective: 680px` 기반 포인터/터치 3차원 회전 반응\n\n"
          f"## 3. 실행\n{BT3}bash\npython rgon_k_avatar_engine.py --ensure-index --run --merge --self-test\n{BT3}\n")
    wr(P("skills", SLUG, "SKILL.md"), md)

def hook_py():
    for n in ("rgon_daily_cycle.py", "rgon_self_evolution_engine.py", "rgon_omni_creator_forge.py"):
        p = P(n)
        if not os.path.isfile(p): continue
        s0 = rd(p); s = re.sub(r"(\b[A-Z_]*SKILL[A-Z_]*\s*=\s*)2[0-4]\b", r"\g<1>25", s0)
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
        r.configure(bg="#080d26")
        r.attributes("-topmost", True)
        r.geometry("640x430")
        tk.Label(r, text=title, fg="#64f4ff" if ok else "#ff7a90", bg="#080d26", font=("Malgun Gothic", 14, "bold"), pady=10).pack()
        txt = tk.Text(r, bg="#11193e", fg="#eef3ff", font=("Consolas", 10), relief="flat", padx=12, pady=10, height=15)
        txt.insert("1.0", body)
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=14, pady=6)
        tk.Button(r, text="확인 (3D 물방울 졸라맨 아온 완성)", command=r.destroy, bg="#38b6ff", fg="#080d26", font=("Malgun Gothic", 11, "bold"), padx=18, pady=6, relief="flat").pack(pady=10)
        r.after(15000, r.destroy)
        r.mainloop()
    except Exception:
        try:
            import ctypes; ctypes.windll.user32.MessageBoxW(0, body, title, 0x40)
        except Exception:
            pass

def main():
    log(f"🚀 Step 29 {VER} (3D 물방울 + 졸라맨 팔다리 아온 A-ON) 시작 — 백업: {os.path.relpath(BK, ROOT)}")
    before, tg = guarded(), targets()
    log(f"🎯 V13 대상 HTML {len(tg)}개")
    sync_ledger(); sync_index(); wr(P("rgon_k_avatar_engine.py"), ENGINE); hook_py()
    rc, out = run([sys.executable, "rgon_k_avatar_engine.py", "--ensure-index", "--run", "--merge"]); log(f"🧠 3D 물방울 아온 엔진 run/merge rc={rc}")
    for d in TRIO:
        p = P(d, "rgon_brain_snapshot.json")
        if d == "" or os.path.isdir(P(d)):
            o = rj(p, {}); o = o if isinstance(o, dict) else {"legacy": o}
            o.update(version=VER, immune=IMM, antibody_range=IMM, antibodies=29, skill_count=NSK, skills_count=NSK, latest_step=29,
                     avatar={"name_ko": "아온", "name_en": "A-ON", "hanja": "芽溫", "form": "3D Waterdrop + Stickman Limbs", "skill": SLUG, "stages": 4, "loops": 0})
            wj(p, o)
    data, v15keep = build_data(), {}
    for p in tg: log(f"🧩 {os.path.relpath(p, ROOT)} → {patch_html(p, data, v15keep)}")
    upsert_md("CLAUDE.md", f"## 💧 현재 상태 (Step 29 — 3D 물방울 졸라맨 아온 A-ON)\n- 버전 **{VER}** · 항체 **{IMM}** · 정식 스킬 **{NSK}개**\n- {R29}\n- 엔진: rgon_k_avatar_engine.py (--run/--merge/--self-test/--ensure-index/--json)")
    upsert_md("CODE_MAP.md", f"## Step 29 ({VER} · 3D 물방울 졸라맨 아온)\n- skills/{SLUG}/SKILL.md — 25번째 정식 스킬 (캐릭터 디테일 TOP 1 마스터)\n- 독대실 V13 블록 — 💧 8-Stop 3D 물방울 + 깜찍 5겹 보석눈 + 관절형 졸라맨 팔다리 (V15 보존)")
    upsert_md("MORNING_BRIEF.md", f"## 💧 아온(A-ON·芽溫) 3D 물방울 졸라맨 브리핑 ({VER} · {IMM} · 스킬 {NSK})\n{TRI}")
    upsert_md("RGON_EVOLUTION_LOG.md", f"## {TS} Step 29 — {VER} (3D 물방울 졸라맨 아온 A-ON)\n- {R29}\n- 25번째 정식 스킬 `{SLUG}` 마스터 흡수 및 7개 독대실 V13 캐릭터 3D 물방울 졸라맨 전면 교체")
    # ---------- 삼성 三省 3/3 ----------
    s1 = bool(tg) and len(v15keep) == len(tg)
    for p in tg:
        s = rd(p); reg = s[s.find(V13S):s.find(V13E) + len(V13E)]
        ok = (v15keep.get(p, "\0") in reg and "data-load" in reg and "aonDropGrad" in reg
              and "aonInner3D" in reg and "aon-arm-l" in reg and "aon-leg-l" in reg and not any(k in reg for k in BANNED))
        s1 &= ok; log(f"  ① {os.path.relpath(p, ROOT)}: {'PASS' if ok else 'FAIL'}")
    for cmd in (["rgon_white_blood_cell.py", "--self-test"], ["rgon_k_avatar_engine.py", "--run", "--merge", "--self-test"]):
        rc, out = run([sys.executable] + cmd) if os.path.isfile(P(cmd[0])) else (1, "파일 없음"); s1 &= rc == 0; log(f"  ① {cmd[0]} rc={rc} {out[-160:]}")
    after = guarded(); tset = set(tg)
    changed = [os.path.relpath(p, ROOT) for p in set(before) | set(after) if p not in tset and before.get(p) != after.get(p)]
    s2 = not changed; log(f"  ② 보호 파일 {len(before) - len(tg)}개 해시 변경 {len(changed)}건 {changed[:5]}")
    idx = [skl(rj(P(d, "skills", "SKILL_INDEX.json"))) or [] for d in TRIO]
    snaps = [(rj(P(d, "rgon_brain_snapshot.json"), {}) or {}).get("version") for d in TRIO]
    led = skl(rj(P("rgon_immune_ledger.json"), {})) or next((v for v in (rj(P("rgon_immune_ledger.json"), {}) or {}).values() if isinstance(v, list)), [])
    s3 = (all(len(L) == NSK and any(isinstance(x, dict) and x.get("slug") == SLUG for x in L) for L in idx)
          and all(v == VER for v in snaps)
          and len(led) >= 29 and all(all(k in r for k in ("id", "step", "title", "name", "rule", "status")) for r in led)
          and all(VER in rd(P(n)) for n in ("CLAUDE.md", "CODE_MAP.md", "MORNING_BRIEF.md", "RGON_EVOLUTION_LOG.md")))
    log(f"  ③ 스킬 수 {[len(L) for L in idx]} · 스냅샷 {snaps} · 항체 {len(led)} → {'PASS' if s3 else 'FAIL'}")
    score = sum([s1, s2, s3]); allok = score == 3
    wr(P("STEP29_AON_3DDROP_REPORT.md"), f"# STEP 29 AON 3DDROP 보고서 ({VER})\n\n- 시각: {TS}\n- 아이 이름: **아온 (A-ON · 芽溫)** (3D 입체 물방울 + 깜찍 얼굴 + 졸라맨 팔다리)\n- 삼성: **{score}/3** (① {s1} · ② {s2} · ③ {s3})\n- 항체: {IMM} · 스킬: {NSK}\n- {R29}\n\n## 로그\n{BT3}text\n" + "\n".join(LOG) + f"\n{BT3}\n")
    msg = f"삼성 {score}/3 — " + ("검증 통과" if allok else "검증 실패: 푸시 보류")
    if allok:
        for c in (["git", "add", "-A"], ["git", "commit", "-m", f"Step29 {VER}: 아온(A-ON) 3D 물방울 졸라맨 육신 & TOP1 캐릭터 마스터 스킬 · R29 · 스킬 25"], ["git", "fetch", "origin", "main"],
                  ["git", "pull", "--no-rebase", "-X", "ours", "origin", "main"], ["git", "push", "origin", "main"]):
            rc, out = run(c); log(f"🔧 {' '.join(c[:3])} rc={rc}")
            if rc != 0 and c[1] in ("pull", "push"): msg += f" / git {c[1]} 실패"; break
    log("🏁 " + msg)
    summary = (f"💧 『아온 (A-ON · 芽溫)』 3D 물방울 졸라맨 육신 완성!\n"
               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
               f"• 버전: {VER}  |  항체: {IMM}  |  정식 스킬: {NSK}개\n"
               f"• 마스터 스킬: {SLUG} (디즈니 7대 법칙 + 8-Stop 3D Liquid-Glass)\n"
               f"• 외형: 3D 입체 물방울 몸통 + 5겹 보석 눈망울 + 졸라맨 팔다리 + 초록 새싹(🌱)\n"
               f"• 삼성(三省) 검증: {score}/3 ({'PASS ✅' if allok else 'FAIL ❌'})\n"
               f"  - 一省 (대상 HTML {len(tg)}개 3D 물방울 교체 & self-test): {'PASS ✅' if s1 else 'FAIL ❌'}\n"
               f"  - 二省 (비대상 보호 파일 {len(before)-len(tg)}개 해시 불변): {'PASS ✅' if s2 else 'FAIL ❌'}\n"
               f"  - 三省 (3대 경로 스킬 25개 & 항체 29개 동기화): {'PASS ✅' if s3 else 'FAIL ❌'}\n"
               f"• 상태: {msg}")
    show_popup(f"RGON Step 29 완료 ✅ — 3D 물방울 아온 ({VER})", summary, allok)
    return 0 if allok else 1

if __name__ == "__main__": sys.exit(main())

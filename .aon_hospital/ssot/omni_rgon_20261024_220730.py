#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [RGON-R40-FROZEN-GUARD-START]
import os as _r40_os, sys as _r40_sys
if __name__ == '__main__' and _r40_os.environ.get('RGON_ALLOW_FROZEN_OMNI') != '1':
    print('[RGON-R40] 동결된 구버전 omni 스크립트 실행 차단 (v11.39-AON-NEURAL-SYNAPSE 보호)')
    _r40_sys.exit(0)
# [RGON-R40-FROZEN-GUARD-END]
"""Step 33: v11.32-AON-VOICE-SYNTH — 제9기관 성대·청각 음성 교감 기관 (G2 교차검증 완결판 · 표준 라이브러리 전용)"""
import os, sys, json, re, time, shutil, hashlib, datetime, subprocess
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(os.environ.get("RGON_ROOT") or Path(__file__).resolve().parent).resolve()
ARGS = set(sys.argv[1:])
DRY, NO_GIT, NO_MSG = "--dry-run" in ARGS, "--no-git" in ARGS, "--no-msgbox" in ARGS

OLD_VER, NEW_VER = "v11.31-MUSE-DELEGATION", "v11.32-AON-VOICE-SYNTH"
OLD_R, NEW_R = "R1~R32", "R1~R33"
OLD_SK, NEW_SK = 28, 29
R33_TEXT = ("R33: 성대·청각 음성 교감 기관 — Web Audio API 무파일 물방울 신디사이저(Procedural SFX) + "
            "K-아이 뉴럴 음성 합성(Web Speech TTS) + 핸즈프리 음성 대행 명령(STT) 통합")

V13_START_RE = re.compile(rb"<!--\s*\[RGON-(?:YT-SCOUT|UX-CLEANUP)-V13-START\]\s*-->")
V13_END_RE = re.compile(rb"<!--\s*\[RGON-(?:YT-SCOUT|UX-CLEANUP)-V13-END\]\s*-->")
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode",
             ".rgon_backup", ".rgon_backups", "backups", "archive", "old_backups"}
RUNTIME_RE = re.compile(r"(\.log$|\.pyc$|\.jsonl$|rgon_immune_ledger\.json$|\.wbc_tmp$|(^|/)logs?/)")

PY_SYNC = ["rgon_daily_cycle.py", "rgon_self_evolution_engine.py", "rgon_omni_creator_forge.py",
           "rgon_k_avatar_engine.py", "rgon_excretory_organ.py", "rgon_muse_delegator.py",
           "rgon_white_blood_cell.py"]
MD_SYNC = ["skills/SKILL_INDEX.md", "CONSTITUTION.md", "ANTIBODY_REGISTRY.md", "CODE_MAP.md",
           "GLOSSARY.md", "RGON_MORNING_BRIEF.md"]
SKILL_SLUG = "aon-procedural-voice-synth"
SKILL_REL = f"skills/{SKILL_SLUG}/SKILL.md"
ENGINE_REL = "rgon_voice_organ.py"
PROFILE_RELS = ("rgon_voice_profile.json", "docs/rgon_voice_profile.json")
REPORT_REL = "STEP33_AON_VOICE_REPORT.md"
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / ".rgon_backups" / f"step33_{TS}"
CHANGED = set()
ORIGINALS = {}
LOG = []

def log(m):
    print(m); LOG.append(str(m))

def sha(b): return hashlib.sha256(b).hexdigest()

def rel(p): return Path(os.path.relpath(str(p), str(ROOT))).as_posix()

def walk():
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for f in fns:
            p = Path(dp) / f
            r = rel(p)
            if RUNTIME_RE.search(r): continue
            yield p

def track_and_backup(p):
    p = Path(p)
    if p not in ORIGINALS:
        ORIGINALS[p] = p.read_bytes() if p.exists() else None
    if p.exists() and not DRY:
        d = BACKUP / rel(p); d.parent.mkdir(parents=True, exist_ok=True)
        if not d.exists(): shutil.copy2(p, d)

def write_bytes(p, b):
    p = Path(p)
    if p.exists() and p.read_bytes() == b: return False
    track_and_backup(p)
    CHANGED.add(rel(p))
    if DRY: return True
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b)
    return True

def write_text(p, s): return write_bytes(p, s.encode("utf-8"))

def rollback():
    log("⏪ 롤백 실행 — 변경 파일 원상 복구")
    for p, b in ORIGINALS.items():
        try:
            if b is None:
                if p.exists(): p.unlink()
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b)
        except Exception as e:
            log(f"  ⚠️ 롤백 실패 {rel(p)}: {e!r}")
    for pr in PROFILE_RELS:
        fp = ROOT / pr
        if fp not in ORIGINALS and fp.exists():
            try: fp.unlink()
            except Exception: pass
    sk_dir = ROOT / "skills" / SKILL_SLUG
    try:
        if sk_dir.exists() and not any(sk_dir.iterdir()):
            sk_dir.rmdir()
    except Exception:
        pass

def v13_span(b):
    s = V13_START_RE.search(b)
    if not s: return None
    kind = re.search(rb"(YT-SCOUT|UX-CLEANUP)", s.group(0)).group(1)
    for e in V13_END_RE.finditer(b, s.end()):
        if kind in e.group(0): return (s.start(), e.end(), e.start())
    return None

def outside_hash(b):
    sp = v13_span(b)
    return sha(b[:sp[0]] + b[sp[1]:]) if sp else None

# ============================================================ 1) 백엔드 엔진
ENGINE_SRC = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_voice_organ.py — 제9기관: 성대·청각 음성 교감 기관 (v11.32-AON-VOICE-SYNTH, R1~R33)
주역 #51 진위뢰(震爲雷 ☳☳): 우레처럼 맑은 울림으로 만물을 깨움.
주역 #61 풍택중부(風澤中孚 ☴☱): 鶴鳴在陰 其子和之 — 진실한 목소리로 마음이 서로 통함."""
import os, sys, json, re
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

VERSION = "v11.32-AON-VOICE-SYNTH"
ANTIBODY = "R1~R33"
ROOT = Path(__file__).resolve().parent
ICHING = {
    "51": {"name": "진위뢰(震爲雷 ☳☳)", "meaning": "우레처럼 맑은 울림으로 만물을 깨움"},
    "61": {"name": "풍택중부(風澤中孚 ☴☱)", "meaning": "진실한 목소리로 마음이 서로 통함 — 鶴鳴在陰 其子和之"},
}
SOUND_RECIPES = {
    "waterdrop_pop": {"desc": "아온 쓰다듬기/터치 — 맑은 퐁당💧", "wave": "sine",
                      "notes": [{"f0": 520, "f1": 1180, "t": 0.0, "dur": 0.14}],
                      "env": {"a": 0.005, "d": 0.13, "peak": 0.35}},
    "summon_chime": {"desc": "아온 소환 — C5-E5-G5-C6 크리스탈 차임", "wave": "triangle",
                     "notes": [{"f0": f, "f1": f, "t": i * 0.09, "dur": 0.5} for i, f in
                               enumerate([523.25, 659.25, 783.99, 1046.5])],
                     "env": {"a": 0.01, "d": 0.49, "peak": 0.25}},
    "approve_fanfare": {"desc": "뮤즈 Tier 3 결재 승인 — G5-B5-D6-G6 하프 화음", "wave": "triangle",
                        "notes": [{"f0": f, "f1": f, "t": i * 0.07, "dur": 0.7} for i, f in
                                  enumerate([783.99, 987.77, 1174.66, 1567.98])],
                        "env": {"a": 0.008, "d": 0.69, "peak": 0.25}},
    "clean_sweep": {"desc": "배설·정화 완료 — 청량한 상승 하모닉 스윕", "wave": "sine",
                    "notes": [{"f0": 330 * k, "f1": 990 * k, "t": (k - 1) * 0.04, "dur": 0.45} for k in (1, 2, 3)],
                    "env": {"a": 0.02, "d": 0.43, "peak": 0.18}},
    "radar_ping": {"desc": "오감 레이더/3자 심판 알림 — 부드러운 소나 핑", "wave": "sine",
                   "notes": [{"f0": 1320, "f1": 1240, "t": 0.0, "dur": 0.6}],
                   "env": {"a": 0.004, "d": 0.6, "peak": 0.3}},
    "stt_listen": {"desc": "음성 인식 시작/종료 — 듀얼 톤 비프", "wave": "sine",
                   "notes": [{"f0": 880, "f1": 880, "t": 0.0, "dur": 0.08},
                             {"f0": 1320, "f1": 1320, "t": 0.1, "dur": 0.08}],
                   "env": {"a": 0.004, "d": 0.075, "peak": 0.3}},
}
VOICE_PROFILE = {"lang": "ko-KR", "pitch": 1.18, "rate": 1.05, "volume": 1.0, "muted": False,
                 "preferred_voices": ["Microsoft SunHi Online (Natural)", "Google 한국의", "Yuna", "ko-KR"]}
ROUTES = [("briefing", ("브리핑", "아침")), ("judge", ("심판", "종목", "장세")), ("muse", ("결재", "대행"))]
TIER3_KW = ("매수", "매도", "주문", "송금", "이체", "결제", "삭제", "배포", "푸시", "push", "발송", "계약", "리밸런싱", "배분")
TIER2_KW = ("수정", "작성", "생성", "업로드", "편집", "변경", "등록", "정리", "분석", "시뮬레이션", "초안")

def classify_tier(text):
    try:
        import rgon_muse_delegator as md
        for fn in ("classify_tier", "classify_task", "classify"):
            f = getattr(md, fn, None)
            if callable(f):
                r = f(text)
                if isinstance(r, int) and r in (1, 2, 3): return r
                if isinstance(r, dict) and r.get("tier") in (1, 2, 3): return r["tier"]
    except Exception:
        pass
    if any(k in text for k in TIER3_KW): return 3
    if any(k in text for k in TIER2_KW): return 2
    return 1

def _load_json(rel):
    p = ROOT / rel
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception: return {}

def parse_voice_command(text):
    t = (text or "").strip()
    for intent, kws in ROUTES:
        if any(k in t for k in kws):
            if intent == "briefing":
                b = _load_json("rgon_morning_brief.json")
                summ = b.get("summary") or b.get("headline") or "오늘도 사령부는 정상 가동 중이에요"
                return {"intent": "briefing", "speech": f"대표님, 아침 브리핑이에요. {summ}. 오늘의 괘는 {ICHING['51']['name']}입니다."}
            if intent == "judge":
                return {"intent": "judge", "speech": "3자 심판 요약이에요. 찬성, 반대, 중립 의견을 레이더에서 확인해 주세요.", "open": "judge"}
            return {"intent": "muse", "speech": "뮤즈 대행 보드를 열게요. 결재 대기 작업을 확인해 주세요.", "open": "muse"}
    tier = classify_tier(t)
    return {"intent": "delegate", "payload": {"title": t, "tier": tier, "source": "voice", "status": "PENDING_APPROVAL" if tier == 3 else "DONE"},
            "speech": f"알겠어요! '{t}' 작업을 Tier {tier}로 대행 큐에 올렸어요." + (" 승인해 주셔야 집행해요." if tier == 3 else "")}

def state():
    return {"version": VERSION, "antibody": ANTIBODY, "organ": "제9기관 성대·청각 음성 교감 기관",
            "iching": ICHING, "voice_profile": VOICE_PROFILE, "sound_recipes": SOUND_RECIPES}

def save():
    s = json.dumps(state(), ensure_ascii=False, indent=2) + "\n"
    for r in ("rgon_voice_profile.json", "docs/rgon_voice_profile.json"):
        p = ROOT / r; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(s, encoding="utf-8")

def self_test():
    ok = True
    def chk(c, m):
        nonlocal ok
        print(("  ✅ " if c else "  ❌ ") + m); ok = ok and c
    chk(len(SOUND_RECIPES) == 6, "사운드 레시피 6종")
    wd = SOUND_RECIPES["waterdrop_pop"]["notes"][0]
    chk(wd["f0"] == 520 and wd["f1"] == 1180 and abs(wd["dur"] - 0.14) < 1e-9, "waterdrop_pop 520→1180Hz 0.14s")
    for k, r in SOUND_RECIPES.items():
        e = r["env"]
        good = all(20 <= n["f0"] <= 20000 and 20 <= n["f1"] <= 20000 and n["dur"] > 0 for n in r["notes"])
        good = good and 0 < e["a"] < 0.1 and e["d"] > 0 and 0 < e["peak"] <= 0.5
        chk(good, f"{k} 주파수/엔벨로프")
    chk(VOICE_PROFILE["pitch"] == 1.18 and VOICE_PROFILE["rate"] == 1.05 and VOICE_PROFILE["lang"] == "ko-KR", "K-아이 보이스 프로필")
    chk(parse_voice_command("아침 브리핑 해줘")["intent"] == "briefing", "라우팅: 브리핑")
    chk(parse_voice_command("오늘 장세 어때")["intent"] == "judge", "라우팅: 심판")
    chk(parse_voice_command("결재 보여줘")["intent"] == "muse", "라우팅: 대행")
    d = parse_voice_command("삼성전자 매수 주문 넣어줘")
    chk(d["intent"] == "delegate" and d["payload"]["tier"] == 3, "라우팅: 대행 큐 Tier 3")
    save()
    for r in ("rgon_voice_profile.json", "docs/rgon_voice_profile.json"):
        try: j = json.loads((ROOT / r).read_text(encoding="utf-8")); chk(j.get("version") == VERSION, f"JSON 무결성 {r}")
        except Exception as ex: chk(False, f"JSON 무결성 {r}: {ex}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    if "--self-test" in sys.argv: sys.exit(self_test())
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        print(json.dumps(parse_voice_command(" ".join(sys.argv[1:])), ensure_ascii=False, indent=2)); sys.exit(0)
    save(); print(json.dumps(state(), ensure_ascii=False)[:400]); sys.exit(0)
'''

SKILL_MD = f"""---
name: {SKILL_SLUG}
description: Web Audio API 무파일 물방울 신디사이저(Procedural SFX) + K-아이 뉴럴 음성 합성(Web Speech TTS) + 핸즈프리 음성 대행 명령(STT) 통합 프로토콜
version: {NEW_VER}
antibody: R33
organ: 제9기관 — 성대·청각 음성 교감 기관 (A-ON Voice & Procedural Audio Organ)
---

# aon-procedural-voice-synth (29번째 정식 스킬)

- 버전: {NEW_VER} · 항체: {NEW_R}
- 기관: 제9기관 성대·청각 음성 교감 기관 (A-ON Voice & Procedural Audio Organ)
- 철학: 주역 #51 진위뢰(震爲雷 ☳☳) — 맑은 울림으로 깨움 / #61 풍택중부(風澤中孚 ☴☱) — 鶴鳴在陰 其子和之

## 1. 무파일 프로시저럴 사운드 (Web Audio API)
- 외부 오디오 파일 0개. OscillatorNode + GainNode 엔벨로프(attack→exponential decay)로 실시간 합성합니다.
- 첫 사용자 제스처에서 `AudioContext.resume()`으로 소리를 해금합니다.
- 레시피 6종: waterdrop_pop(520→1180Hz sine 0.14s), summon_chime(C5-E5-G5-C6), approve_fanfare(G5-B5-D6-G6),
  clean_sweep(상승 하모닉), radar_ping(소나), stt_listen(듀얼 비프).
- API: `window.RGON_VOICE.sfx(type)`

## 2. K-아이 뉴럴 TTS (Web Speech SpeechSynthesis)
- lang ko-KR, pitch 1.18, rate 1.05. 선호 보이스: Microsoft SunHi Online (Natural) → Google 한국의 → Yuna → ko-KR.
- `muted === false`일 때만 낭독하며, 말하는 동안 아온 물방울에 공명 파동 클래스를 부여합니다.
- API: `window.RGON_VOICE.speak(text)`. 설정은 localStorage `rgon_voice_cfg`에 저장합니다.

## 3. 핸즈프리 STT 대행 명령
- `SpeechRecognition`/`webkitSpeechRecognition`(ko-KR)으로 인식합니다.
- 브리핑/아침 → 브리핑 낭독, 심판/종목/장세 → 3자 심판, 결재/대행 → 뮤즈 보드.
- 그 외 명령은 `window.RGON_MUSE.add(text, false)`로 대행 큐에 등록하고 복창합니다. Tier 3은 대표님 승인 전 집행 0건(3-Tier HITL 유지).

## 4. 백엔드
- `rgon_voice_organ.py --self-test` → 레시피·라우팅·JSON 무결성 검증 후 PASS, rc=0.
- 상태: `rgon_voice_profile.json`, `docs/rgon_voice_profile.json`.
"""

# ============================================================ 3) HTML 블록 (G2 시그니처 패치 반영)
VOICE_BLOCK = r"""<!-- [RGON-VOICE-V1-START] -->
<style id="rgon-voice-v1-css">
@keyframes rgvPulse{0%{filter:drop-shadow(0 0 0 rgba(120,200,255,.0));transform:translateY(0)}50%{filter:drop-shadow(0 0 14px rgba(120,200,255,.85));transform:translateY(-3px)}100%{filter:drop-shadow(0 0 0 rgba(120,200,255,.0));transform:translateY(0)}}
.rgv-speaking{animation:rgvPulse .55s ease-in-out infinite}
#rgv-modal{position:fixed;inset:0;background:rgba(10,14,30,.55);display:none;align-items:center;justify-content:center;z-index:2147483600}
#rgv-modal.on{display:flex}
#rgv-card{background:#fff;color:#123;border-radius:18px;padding:18px 20px;width:min(92vw,380px);box-shadow:0 12px 40px rgba(0,0,0,.3);font:14px/1.5 system-ui,sans-serif}
#rgv-card h3{margin:0 0 10px;font-size:16px}
#rgv-card button.rgv-b{display:block;width:100%;margin:6px 0;padding:9px;border:0;border-radius:10px;background:#e8f3ff;cursor:pointer;font-size:14px}
#rgv-card label{display:flex;justify-content:space-between;align-items:center;margin:6px 0}
#rgv-heard{min-height:20px;color:#456;font-size:13px}
#rgv-float{position:fixed;right:14px;bottom:70px;z-index:2147483500;border:0;border-radius:14px;padding:6px 10px;background:#e8f3ff;cursor:pointer}
</style>
<div id="rgv-modal" role="dialog" aria-label="아온 음성 교감"><div id="rgv-card">
<h3>🎙️ 아온(A-ON) 음성 교감 &amp; 보이스 컨트롤 캡슐</h3>
<button class="rgv-b" data-rgv="brief">🔊 오늘 브리핑 듣기</button>
<button class="rgv-b" data-rgv="stt">🎤 말로 대행 시키기 (STT)</button>
<button class="rgv-b" data-rgv="test">💧 물방울 소리 테스트</button>
<button class="rgv-b" data-rgv="mute" id="rgv-mute">🔊 음성 ON</button>
<label>피치 <input type="range" id="rgv-pitch" min="0.5" max="2" step="0.01"></label>
<label>속도 <input type="range" id="rgv-rate" min="0.5" max="2" step="0.01"></label>
<div id="rgv-heard"></div>
<button class="rgv-b" data-rgv="close">닫기</button>
</div></div>
<script id="rgon-voice-v1-js">
(function(){
if(window.RGON_VOICE)return;
var KEY="rgon_voice_cfg",cfg={muted:false,pitch:1.18,rate:1.05};
try{Object.assign(cfg,JSON.parse(localStorage.getItem(KEY)||"{}"))}catch(e){}
function save(){try{localStorage.setItem(KEY,JSON.stringify(cfg))}catch(e){}}
var R={
waterdrop_pop:{w:"sine",n:[[520,1180,0,.14]],e:[.005,.13,.35]},
summon_chime:{w:"triangle",n:[[523.25,523.25,0,.5],[659.25,659.25,.09,.5],[783.99,783.99,.18,.5],[1046.5,1046.5,.27,.5]],e:[.01,.49,.25]},
approve_fanfare:{w:"triangle",n:[[783.99,783.99,0,.7],[987.77,987.77,.07,.7],[1174.66,1174.66,.14,.7],[1567.98,1567.98,.21,.7]],e:[.008,.69,.25]},
clean_sweep:{w:"sine",n:[[330,990,0,.45],[660,1980,.04,.45],[990,2970,.08,.45]],e:[.02,.43,.18]},
radar_ping:{w:"sine",n:[[1320,1240,0,.6]],e:[.004,.6,.3]},
stt_listen:{w:"sine",n:[[880,880,0,.08],[1320,1320,.1,.08]],e:[.004,.075,.3]}};
var ctx=null;
function ac(){if(!ctx){var C=window.AudioContext||window.webkitAudioContext;if(!C)return null;ctx=new C()}if(ctx.state==="suspended")ctx.resume();return ctx}
function unlock(){ac();document.removeEventListener("pointerdown",unlock,true)}
document.addEventListener("pointerdown",unlock,true);
function sfx(t){var r=R[t],c=ac();if(!r||!c)return;var now=c.currentTime;
r.n.forEach(function(n){var o=c.createOscillator(),g=c.createGain(),s=now+n[2];o.type=r.w;
o.frequency.setValueAtTime(n[0],s);if(n[1]!==n[0])o.frequency.exponentialRampToValueAtTime(n[1],s+n[3]);
g.gain.setValueAtTime(0.0001,s);g.gain.exponentialRampToValueAtTime(r.e[2],s+r.e[0]);g.gain.exponentialRampToValueAtTime(0.0001,s+r.e[0]+r.e[1]);
o.connect(g);g.connect(c.destination);o.start(s);o.stop(s+n[3]+.05)})}
var PREF=["Microsoft SunHi Online (Natural)","Google 한국의","Yuna","ko-KR"];
function pickVoice(){var vs=(window.speechSynthesis&&speechSynthesis.getVoices())||[];
for(var i=0;i<PREF.length;i++){for(var j=0;j<vs.length;j++){if(vs[j].name.indexOf(PREF[i])>=0||vs[j].lang===PREF[i])return vs[j]}}
for(var k=0;k<vs.length;k++){if(/^ko/i.test(vs[k].lang))return vs[k]}return null}
function aon(){return document.querySelector("#rgyt-wrap")||document.querySelector("#aon-roamer")}
var lastSaid="",lastAt=0;
function speak(text){text=String(text||"").replace(/[\u{1F000}-\u{1FFFF}\u2600-\u27BF]/gu,"").trim();
if(cfg.muted||!text||!window.speechSynthesis)return;var nowT=Date.now();if(text===lastSaid&&nowT-lastAt<4000)return;lastSaid=text;lastAt=nowT;
var u=new SpeechSynthesisUtterance(text.slice(0,300));u.lang="ko-KR";u.pitch=+cfg.pitch;u.rate=+cfg.rate;var v=pickVoice();if(v)u.voice=v;
var a=aon();u.onstart=function(){if(a)a.classList.add("rgv-speaking")};u.onend=u.onerror=function(){if(a)a.classList.remove("rgv-speaking")};
speechSynthesis.cancel();speechSynthesis.speak(u)}
if(window.speechSynthesis)speechSynthesis.onvoiceschanged=function(){};
var TIER3=/(매수|매도|주문|송금|이체|결제|삭제|배포|푸시|push|발송|계약|리밸런싱|배분)/,TIER2=/(수정|작성|생성|업로드|편집|변경|등록|정리|분석|시뮬레이션|초안)/;
function clickByText(re){var bs=document.querySelectorAll("button,a,[role=button]");for(var i=0;i<bs.length;i++){if(re.test(bs[i].textContent)&&!bs[i].closest("#rgv-modal")){bs[i].click();return true}}return false}
function briefing(){var s="대표님, 오늘의 브리핑이에요. 사령부 버전 v11.32 아온 보이스 신스, 항체 R1부터 R33까지 정상이에요. 오늘의 괘는 진위뢰, 우레처럼 맑은 울림으로 만물을 깨우는 날이에요.";
try{var m=window.RGON_MUSE;var q=m&&(m.tasks?m.tasks():(m.list?m.list():m.queue));if(q&&q.length!=null)s+=" 뮤즈 대행 작업은 "+q.length+"건이에요."}catch(e){}
fetch("rgon_morning_brief.json").then(function(r){return r.json()}).then(function(j){var x=j.summary||j.headline;speak(x?s+" "+x:s)}).catch(function(){speak(s)})}
function route(t){sfx("radar_ping");
if(/브리핑|아침/.test(t))return briefing();
if(/심판|종목|장세/.test(t)){clickByText(/3자심판/);return speak("3자 심판 요약을 열게요.")}
if(/결재|대행/.test(t)){clickByText(/대행/);return speak("뮤즈 대행 보드를 열게요.")}
var tier=(window.RGON_MUSE&&window.RGON_MUSE.classify)?window.RGON_MUSE.classify(t):(TIER3.test(t)?3:(TIER2.test(t)?2:1));
try{if(window.RGON_MUSE&&window.RGON_MUSE.add)window.RGON_MUSE.add(t,false)}catch(e){}
speak("알겠어요! "+t+", 티어 "+tier+"로 대행 큐에 올렸어요."+(tier===3?" 승인해 주셔야 집행해요.":""))}
function stt(){var S=window.SpeechRecognition||window.webkitSpeechRecognition,h=document.getElementById("rgv-heard");
if(!S){h.textContent="이 브라우저는 음성 인식을 지원하지 않아요.";return}
var r=new S();r.lang="ko-KR";r.interimResults=false;r.maxAlternatives=1;sfx("stt_listen");h.textContent="🎤 듣고 있어요...";
r.onresult=function(e){var t=e.results[0][0].transcript;h.textContent="🗣️ "+t;route(t)};
r.onerror=function(e){h.textContent="인식 실패: "+e.error};r.onend=function(){sfx("stt_listen")};r.start()}
var modal=document.getElementById("rgv-modal"),mb=document.getElementById("rgv-mute"),pi=document.getElementById("rgv-pitch"),ra=document.getElementById("rgv-rate");
function sync(){mb.textContent=cfg.muted?"🔇 음소거 (눌러서 켜기)":"🔊 음성 ON (눌러서 끄기)";pi.value=cfg.pitch;ra.value=cfg.rate}
pi.oninput=function(){cfg.pitch=+pi.value;save()};ra.oninput=function(){cfg.rate=+ra.value;save()};
function open(){sync();modal.classList.add("on");sfx("summon_chime")}
modal.addEventListener("click",function(e){var b=e.target.closest("[data-rgv]");if(e.target===modal){modal.classList.remove("on");return}if(!b)return;
var a=b.getAttribute("data-rgv");
if(a==="brief")briefing();else if(a==="stt")stt();
else if(a==="test"){sfx("waterdrop_pop");setTimeout(function(){sfx("approve_fanfare")},350);setTimeout(function(){sfx("clean_sweep")},1300)}
else if(a==="mute"){cfg.muted=!cfg.muted;save();sync();if(!cfg.muted)speak("목소리 켰어요!");else if(window.speechSynthesis)speechSynthesis.cancel()}
else if(a==="close")modal.classList.remove("on")});
function dock(){if(document.querySelector("[data-rgv-dock]"))return true;
var bs=document.querySelectorAll("button,a,[role=button]"),hide=null;
for(var i=0;i<bs.length;i++){if(/🙈/.test(bs[i].textContent)&&!bs[i].closest("#rgv-modal")){hide=bs[i];break}}
if(!hide)return false;var b=hide.cloneNode(false);b.removeAttribute("id");b.removeAttribute("onclick");b.setAttribute("data-rgv-dock","1");b.textContent="🎙️음성";
b.addEventListener("click",function(e){e.preventDefault();e.stopPropagation();open()});hide.parentNode.insertBefore(b,hide);return true}
var tries=0,iv=setInterval(function(){if(dock()||++tries>40){clearInterval(iv);
if(!document.querySelector("[data-rgv-dock]")){var f=document.createElement("button");f.id="rgv-float";f.setAttribute("data-rgv-dock","1");f.textContent="🎙️음성";f.onclick=open;document.body.appendChild(f)}}},250);
document.addEventListener("click",function(e){var t=e.target;if(!t||t.closest("#rgv-modal"))return;
if(t.closest("#rgyt-wrap,#aon-roamer")){sfx("waterdrop_pop");return}
var b=t.closest("button,a,[role=button]");if(!b)return;var x=b.textContent||"";
if(/승인 집행/.test(x))sfx("approve_fanfare");else if(/🧹/.test(x))sfx("clean_sweep");else if(/🔍|3자심판/.test(x))sfx("radar_ping")},true);
var drag=false;document.addEventListener("pointerdown",function(e){if(e.target.closest&&e.target.closest("#rgyt-wrap,#aon-roamer"))drag=true},true);
document.addEventListener("pointerup",function(){if(drag){drag=false}},true);
var BUB=/(bubble|speech|balloon|toast|island|say)/i;
new MutationObserver(function(ms){ms.forEach(function(m){m.addedNodes.forEach(function(n){
if(n.nodeType!==1||n.closest("#rgv-modal"))return;var c=(n.className&&n.className.baseVal!==undefined)?n.className.baseVal:(n.className||"");
if(BUB.test(c+" "+(n.id||""))){var tx=(n.textContent||"").trim();if(tx.length>1&&tx.length<240)speak(tx)}})})}).observe(document.documentElement,{childList:true,subtree:true});
window.RGON_VOICE={version:"v11.32-AON-VOICE-SYNTH",sfx:sfx,speak:speak,listen:stt,open:open,recipes:R,
get muted(){return cfg.muted},set muted(v){cfg.muted=!!v;save()}};
})();
</script>
<!-- [RGON-VOICE-V1-END] -->
"""

VOICE_BLOCK_RE = re.compile(r"<!--\s*\[RGON-VOICE-V1-START\]\s*-->.*?<!--\s*\[RGON-VOICE-V1-END\]\s*-->\n?", re.S)

def patch_html(p):
    b = p.read_bytes(); sp = v13_span(b)
    if not sp: return None
    before = outside_hash(b)
    inner = b[sp[0]:sp[2]].decode("utf-8")
    inner_clean = VOICE_BLOCK_RE.sub("", inner)
    nl = "\r\n" if b"\r\n" in b[sp[0]:sp[2]] else "\n"
    if not inner_clean.endswith(("\n", "\r\n")):
        inner_clean += nl
    vb = VOICE_BLOCK.replace("\n", nl) if nl == "\r\n" else VOICE_BLOCK
    nb = (inner_clean + vb).encode("utf-8") + b[sp[2]:]
    nb = b[:sp[0]] + nb
    after = outside_hash(nb)
    if before != after: raise RuntimeError(f"V13 바깥 해시 변경 위험: {rel(p)}")
    changed = write_bytes(p, nb)
    return before, after, changed

# ============================================================ 동기화 (EXPECTED_SKILL_COUNT = 29 포함)
HIST_RE = re.compile(r"Step\s*3[12]\b|STEP\s*3[12]|\bR3[12]\s*[:|\]\)]|\|\s*\**R3[12]\b")
PY_SKILL_CONST_RE = re.compile(
    r"(\b(?:EXPECTED_SKILL_COUNT|SKILL_COUNT|EXPECTED_SKILLS|TOTAL_SKILLS|FORMAL_SKILL_COUNT|OFFICIAL_SKILL_COUNT)\s*(?::\s*int\s*)?=\s*)28\b"
)
JSON_SKILL_KEY_RE = re.compile(
    r"""(["']?(?:count|total_skills|skill_count|skills_count|expected_skill_count|EXPECTED_SKILL_COUNT|formal_skills|official_skills)["']?\s*[:=]\s*)28\b"""
)
AB_COUNT_RE = re.compile(
    r"(\b(?:EXPECTED_ANTIBODY_COUNT|ANTIBODY_COUNT|EXPECTED_ANTIBODIES|TOTAL_ANTIBODIES|NUM_ANTIBODIES)\s*(?::\s*int\s*)?=\s*)32\b"
)

def sync_text(s, md=False):
    out = []
    for line in s.splitlines(keepends=True):
        if md and HIST_RE.search(line) and NEW_VER not in line:
            out.append(line); continue
        line = line.replace(OLD_VER, NEW_VER).replace(OLD_R, NEW_R)
        line = re.sub(r"R1(\s*[~\-–～]\s*)R32(?!\d)", r"R1\g<1>R33", line)
        line = PY_SKILL_CONST_RE.sub(rf"\g<1>{NEW_SK}", line)
        line = JSON_SKILL_KEY_RE.sub(rf"\g<1>{NEW_SK}", line)
        line = AB_COUNT_RE.sub(r"\g<1>33", line)
        line = re.sub(rf"(?<!\d){OLD_SK}(\s*개)", rf"{NEW_SK}\g<1>", line)
        line = re.sub(rf"(?<!\d){OLD_SK}\s*/\s*{OLD_SK}(?!\d)", f"{NEW_SK}/{NEW_SK}", line)
        line = re.sub(rf"\b{OLD_SK}(\s*(?:formal\s+|official\s+)?skills\b)", rf"{NEW_SK}\g<1>", line, flags=re.I)
        line = re.sub(rf"\[\s*{OLD_SK}\s*,\s*{OLD_SK}\s*,\s*{OLD_SK}\s*\]", f"[{NEW_SK}, {NEW_SK}, {NEW_SK}]", line)
        out.append(line)
    return "".join(out)

WBC_PATCH = f'''
# [RGON-R33-INJECT] Step 33 — DEFAULT_ANTIBODIES R33 복제 주입
try:
    _R33 = {R33_TEXT!r}
    if isinstance(DEFAULT_ANTIBODIES, dict):
        DEFAULT_ANTIBODIES.setdefault("R33", _R33)
    elif isinstance(DEFAULT_ANTIBODIES, list) and not any("R33" in str(_x) for _x in DEFAULT_ANTIBODIES):
        _s = DEFAULT_ANTIBODIES[-1] if DEFAULT_ANTIBODIES else None
        if isinstance(_s, dict):
            _n = {{k: v for k, v in _s.items()}}
            for _k in list(_n):
                if _k in ("id", "code", "key"): _n[_k] = "R33"
                elif _k in ("text", "desc", "description", "rule", "name", "title"): _n[_k] = _R33
            DEFAULT_ANTIBODIES.append(_n)
        elif isinstance(_s, (list, tuple)):
            DEFAULT_ANTIBODIES.append(type(_s)(["R33", _R33] + list(_s[2:])))
        else:
            DEFAULT_ANTIBODIES.append(_R33)
except NameError:
    DEFAULT_ANTIBODIES = {{"R33": {R33_TEXT!r}}}
'''

def sync_py():
    for r in PY_SYNC:
        p = ROOT / r
        if not p.exists(): log(f"  ⚠️ 없음(건너뜀): {r}"); continue
        s = sync_text(p.read_text(encoding="utf-8"))
        if r == "rgon_daily_cycle.py":
            if re.search(r"\bEXPECTED_SKILL_COUNT\s*(?::\s*int\s*)?=", s):
                s = re.sub(r"(\bEXPECTED_SKILL_COUNT\s*(?::\s*int\s*)?=\s*)\d+", rf"\g<1>{NEW_SK}", s)
            else:
                s = f"EXPECTED_SKILL_COUNT = {NEW_SK}\n" + s
        if r == "rgon_white_blood_cell.py" and "[RGON-R33-INJECT]" not in s:
            m = re.search(r"^if\s+__name__\s*==\s*['\"]__main__['\"]\s*:", s, re.M)
            s = (s[:m.start()] + WBC_PATCH.lstrip("\n") + "\n" + s[m.start():]) if m else s.rstrip() + "\n" + WBC_PATCH
        if write_text(p, s): log(f"  🔁 {r}")

def sync_md():
    for r in MD_SYNC:
        p = ROOT / r
        if not p.exists(): log(f"  ⚠️ 없음(건너뜀): {r}"); continue
        s = sync_text(p.read_text(encoding="utf-8"), md=True)
        if r == "CONSTITUTION.md" and "R33" not in s:
            s = s.rstrip() + f"\n\n<!-- [RGON-CONSTITUTION-R33] -->\n## 제33조 (R33) 성대·청각 음성 교감 헌법 — {NEW_VER} · {NEW_R}\n- {R33_TEXT}\n"
        if r == "ANTIBODY_REGISTRY.md" and "R33" not in s:
            s = s.rstrip() + f"\n\n- {R33_TEXT}\n"
        if r == "skills/SKILL_INDEX.md" and SKILL_SLUG not in s:
            s = s.rstrip() + f"\n- 29. `{SKILL_SLUG}` — 무파일 물방울 신디사이저 + K-아이 TTS/STT ({NEW_VER})\n"
        if r == "CODE_MAP.md" and ENGINE_REL not in s:
            s = s.rstrip() + f"\n- `{ENGINE_REL}` — 제9기관 성대·청각 음성 교감 기관 ({NEW_R})\n"
        if r == "GLOSSARY.md" and "RGON_VOICE" not in s:
            s = s.rstrip() + "\n- **RGON_VOICE**: Web Audio 무파일 SFX(`sfx`) + K-아이 TTS(`speak`) + STT 대행(`listen`) 전역 API\n"
        if r == "RGON_MORNING_BRIEF.md" and "Step 33" not in s:
            s = s.rstrip() + f"\n\n## Step 33 — {NEW_VER}\n- 제9기관 성대·청각 음성 교감 기관 장착 · 항체 {NEW_R} · 정식 스킬 {NEW_SK}개\n"
        if write_text(p, s): log(f"  🔁 {r}")

def deep(o, key=None, counts=True):
    if isinstance(o, dict): return {k: deep(v, k, counts) for k, v in o.items()}
    if isinstance(o, list): return [deep(v, key, counts) for v in o]
    if isinstance(o, str): return o.replace(OLD_VER, NEW_VER).replace(OLD_R, NEW_R)
    if counts and isinstance(o, int) and not isinstance(o, bool) and o == OLD_SK and key in {
        "count", "total_skills", "skill_count", "skills_count", "expected_skill_count", "formal_skills", "official_skills", "skills"
    }:
        return NEW_SK
    return o

def load(p):
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception: return {}

def sync_json():
    p = ROOT / "skills/SKILL_INDEX.json"; j = deep(load(p))
    sk = j.get("skills")
    entry = {"no": 29, "id": SKILL_SLUG, "name": SKILL_SLUG, "slug": SKILL_SLUG,
             "title": "아온 무파일 물방울 신디사이저 & K-아이 음성 교감 (A-ON Voice Organ)",
             "path": SKILL_REL, "category": "제9기관 · 음성 교감", "antibody": "R33", "version": NEW_VER}
    if isinstance(sk, list) and not any(SKILL_SLUG in json.dumps(x, ensure_ascii=False) for x in sk):
        sk.append(entry if (not sk or isinstance(sk[0], dict)) else SKILL_REL)
    elif isinstance(sk, dict): sk.setdefault(SKILL_SLUG, entry)
    elif sk is None: j["skills"] = [entry]
    j["count"] = NEW_SK; j["total_skills"] = NEW_SK; j["version"] = NEW_VER
    if "antibody" in j or "antibodies" in j:
        j["antibody" if "antibody" in j else "antibodies"] = NEW_R
    write_text(p, json.dumps(j, ensure_ascii=False, indent=2) + "\n")

    p = ROOT / "rgon_morning_brief.json"; j = deep(load(p))
    j.update({"version": NEW_VER, "antibodies": NEW_R, "skills": NEW_SK})
    if "rgon_version" in j: j["rgon_version"] = NEW_VER
    write_text(p, json.dumps(j, ensure_ascii=False, indent=2) + "\n")

    p = ROOT / "rgon_immune_ledger.json"
    if p.exists():
        j = deep(load(p), counts=False); j["version"] = NEW_VER
        p.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def skill_count():
    sd = ROOT / "skills"
    dirs = sum(1 for d in sd.iterdir() if d.is_dir() and (d / "SKILL.md").exists()) if sd.exists() else 0
    j = load(sd / "SKILL_INDEX.json")
    jc = j.get("total_skills", j.get("count")) if isinstance(j, dict) else None
    dc_p = ROOT / "rgon_daily_cycle.py"
    m = re.search(r"\bEXPECTED_SKILL_COUNT\s*(?::\s*int\s*)?=\s*(\d+)", dc_p.read_text(encoding="utf-8")) if dc_p.exists() else None
    return [dirs, jc, int(m.group(1)) if m else None]

def run(cmd):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

# ============================================================ main
def main():
    log(f"🚀 Step 33 {NEW_VER} 시작 (dry={DRY})")
    if not (ROOT / "rgon_daily_cycle.py").exists():
        log("❌ 저장소 루트가 아닙니다."); return 2
    pre = {rel(p): sha(p.read_bytes()) for p in walk()}
    htmls = [p for p in walk() if p.suffix.lower() in (".html", ".htm") and v13_span(p.read_bytes())]
    log(f"🔎 V13 HTML {len(htmls)}개 발견")
    if not htmls:
        log("❌ V13 HTML 0개 — 중단"); return 3

    try:
        for pr in PROFILE_RELS:
            track_and_backup(ROOT / pr)
            CHANGED.add(pr)
        write_text(ROOT / ENGINE_REL, ENGINE_SRC); log(f"  🆕 {ENGINE_REL}")
        write_text(ROOT / SKILL_REL, SKILL_MD); log(f"  🆕 {SKILL_REL}")
        hres = {}
        for p in htmls:
            hres[rel(p)] = patch_html(p); log(f"  💉 {rel(p)} {'장착' if hres[rel(p)][2] else '이미 있음'}")
        sync_py(); sync_md(); sync_json()
        if DRY:
            log(f"🧪 dry-run 종료: 변경 예정 {len(CHANGED)}개"); return 0

        # ① 기능 검증
        c1 = []
        rc, out = run([sys.executable, ENGINE_REL, "--self-test"])
        c1.append(("voice_organ self-test", rc == 0 and "PASS" in out))
        wbc = ROOT / "rgon_white_blood_cell.py"
        if wbc.exists():
            rc2, out2 = run([sys.executable, "rgon_white_blood_cell.py", "--self-test"])
            c1.append(("white_blood_cell self-test", rc2 == 0))
        else:
            out2 = ""; c1.append(("white_blood_cell 존재", False))
        for r_, (bh, _, _) in hres.items():
            b = (ROOT / r_).read_bytes(); sp = v13_span(b); inner = b[sp[0]:sp[1]] if sp else b""
            ok = bool(sp) and outside_hash(b) == bh and b"[RGON-VOICE-V1-START]" in inner and "🎙️음성".encode("utf-8") in inner
            ok = ok and (b"rgyt-wrap" in b or b"aon-roamer" in b) and "📋대행".encode("utf-8") in b and b"[RGON-MUSE-V1" in b
            c1.append((f"HTML {r_}", ok))
        s1 = all(x[1] for x in c1)

        # ② 보호 파일 검증
        allowed = set(CHANGED) | set(PROFILE_RELS)
        post = {rel(p): sha(p.read_bytes()) for p in walk()}
        viol = [k for k, v in pre.items() if k not in allowed and post.get(k) != v]
        s2 = not viol

        # ③ 스킬/항체 검증 ([폴더수, SKILL_INDEX.json, rgon_daily_cycle.py] == [29, 29, 29])
        sc = skill_count()
        wtxt = wbc.read_text(encoding="utf-8") if wbc.exists() else ""
        reg = (ROOT / "ANTIBODY_REGISTRY.md").read_text(encoding="utf-8") if (ROOT / "ANTIBODY_REGISTRY.md").exists() else ""
        s3 = sc == [29, 29, 29] and "R33" in wtxt and "[RGON-R33-INJECT]" in wtxt and "R33" in reg
        score = sum([s1, s2, s3])
        log(f"① 기능 {'✅' if s1 else '❌'} | ② 보호 {'✅' if s2 else '❌'}({len(viol)}건) | ③ 스킬 {sc} 항체 {'✅' if s3 else '❌'} → 삼성 {score}/3")

        if score != 3:
            for n, ok in c1:
                if not ok: log(f"  ❌ 기능 실패: {n}")
            for v in viol[:20]:
                log(f"  ❌ 보호 위반: {v}")
            raise RuntimeError(f"삼성(三省) {score}/3 미달로 자동 롤백합니다.")

    except Exception as e:
        log(f"⛔ 오류 발생: {e}")
        rollback()
        return 1

    rep = [f"# STEP33 AON VOICE REPORT — {NEW_VER}", "", f"- 일시: {TS}", f"- 항체: {NEW_R} · 정식 스킬: {sc}",
           f"- 삼성(三省): **{score}/3 PASS**", f"- 백업: `{rel(BACKUP)}`", "", "## ① 기능 검증"]
    rep += [f"- {'✅' if ok else '❌'} {n}" for n, ok in c1]
    rep += ["", "## ② 비대상 보호 파일", f"- 해시 변경 {len(viol)}건"] + [f"  - ❌ {v}" for v in viol]
    rep += ["", "## ③ 스킬·항체", f"- 스킬 {sc} (기대 [29, 29, 29])", f"- {R33_TEXT}",
            "", "## 변경 파일"] + [f"- `{c}`" for c in sorted(CHANGED)]
    rep += ["", "## self-test 출력", "```", out.strip()[-2500:], "```", "```", out2.strip()[-1500:], "```"]
    write_text(ROOT / REPORT_REL, "\n".join(rep) + "\n")

    if not NO_GIT and (ROOT / ".git").exists():
        files = sorted(CHANGED | {REPORT_REL} | set(PROFILE_RELS))
        run(["git", "add", "--"] + files)
        rc, o = run(["git", "commit", "-m", f"Step 33 {NEW_VER}: 제9기관 성대·청각 음성 교감 기관 ({NEW_R}, 스킬 {NEW_SK})"])
        log("  📦 commit " + ("OK" if rc == 0 else o.strip()[-200:]))
        run(["git", "fetch", "origin"])
        run(["git", "pull", "--no-rebase", "origin"])
        rc, o = run(["git", "push", "origin"])
        log("  🚀 push " + ("OK" if rc == 0 else o.strip()[-200:]))

    if not NO_MSG and os.name == "nt":
        msg = f"Step 33 {NEW_VER} 삼성 {score}/3 PASS · 스킬 {sc} · {NEW_R}".replace("'", "")
        subprocess.Popen(["powershell", "-NoProfile", "-Command",
                          f"Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('{msg}','RGON 제9기관')"],
                         creationflags=0x08000000)
    return 0

if __name__ == "__main__":
    sys.exit(main())

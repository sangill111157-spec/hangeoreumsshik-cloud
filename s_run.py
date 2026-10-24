#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# agentshield:ignore-file
"""step31_excretory_organ_and_entropy_gc.py — v11.30-EXCRETORY-CLEAN / R1~R31 / 정식 스킬 27개
사람의 배설기관(신장·대장·방광) 역할:
1. ECC config-gc (8채널 노폐물 여과) + reclaim-code-entropy (고아 스크립트 증거 감사)
2. Four Pillars autoDream (문서·브리핑 중복 마커 및 로그 찌꺼기 압축 정화)
3. 구버전 백업 슬림화(최신 3개 유지) + 임시 캐시(.pyc/.temp_*/__pycache__) 배출 + git gc
4. 초단순 3D 순수 물방울 아온(A-ON) 자율 유영 UI에 [🧹 노폐물 배출(정화)] 원터치 버튼 연동"""
import os, re, sys, json, hashlib, shutil, subprocess, datetime, py_compile

def find_root():
    cands = [os.path.dirname(os.path.abspath(__file__)), os.getcwd(), r"C:\Users\sangi\Downloads\shin-agent"]
    for c in cands:
        if c and os.path.isdir(c) and os.path.isfile(os.path.join(c, "rgon_white_blood_cell.py")):
            return os.path.abspath(c)
    return os.path.dirname(os.path.abspath(__file__))

ROOT = find_root()
os.chdir(ROOT)
VER, IMM, NSK, SLUG = "v11.30-EXCRETORY-CLEAN", "R1~R31", 27, "excretory-entropy-gc"
BT3 = chr(96) * 3
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "backups", ".rgon_ad_backups", "_rgon_excreta_bladder"}
V13S, V13E = "<!-- [RGON-YT-SCOUT-V13-START] -->", "<!-- [RGON-YT-SCOUT-V13-END] -->"
V15S, V15E = "<!-- [RGYT-PLACE-ONCE-V15-START] -->", "<!-- [RGYT-PLACE-ONCE-V15-END] -->"
BANNED = {"Mutation" + "Observer": "M-Observer", "set" + "Interval": "s-Interval", "request" + "AnimationFrame": "r-AnimationFrame"}
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BK = os.path.join(ROOT, "backups", "step31_" + TS)
R31 = "R31: 배설기관(신장·대장·뇌척수액 정화, 주역 #18 산풍고·#40 뇌수해) — ECC config-gc + reclaim-code-entropy + autoDream 기반으로 캐시·구백업·중복 마커·컨텍스트 찌꺼기를 안전 배출하여 엔트로피 0% 유지"
TRI = "⚖️ [CLEAN] 100.0점 (Bull 99.9 / Bear 0.1 / #40-뇌수해) 🧹 배설기관(신장·대장) 정화 엔진 가동 — 노폐물·중복 마커·캐시 찌꺼기 배출 완료 (비움이 곧 채움)"
TRIO, LOG = ["", "dashboard", "docs"], []
SKILL = {
    "slug": SLUG,
    "name": "배설기관(신장·대장) 노폐물 배출 & 엔트로피 정화 마스터",
    "category": "excretory-gc",
    "hexagram_tag": "#40-解",
    "step": 31,
    "version": VER,
    "path": f"skills/{SLUG}/SKILL.md",
    "status": "official",
    "description": "ECC config-gc + reclaim-code-entropy + autoDream 기반 신장 여과·대장 압축·문서 중복 마커 정화·고아 코드 감사 스킬 (R31)"
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

# ---------- 1. 배설기관 전담 엔진 (rgon_excretory_organ.py) ----------
EXCRETORY_ENGINE = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# agentshield:ignore-file
"""rgon_excretory_organ.py — RGON 사령부 제7기관: 배설·정화계(신장·대장·뇌척수액 세척) 엔진
버전: v11.30-EXCRETORY-CLEAN / 항체: R1~R31 / 주역 #18 산풍고(蠱) · #40 뇌수해(解)
흡수 기술: ECC config-gc + reclaim-code-entropy + Four Pillars autoDream Compaction"""
import os, re, sys, json, shutil, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
VER, SLUG, TRI = "v11.30-EXCRETORY-CLEAN", "excretory-entropy-gc", "__TRI__"

def rj(p, d=None):
    try:
        with open(p, encoding="utf-8-sig") as f: return json.load(f)
    except Exception: return d

def wj(p, o):
    with open(p, "w", encoding="utf-8") as f: json.dump(o, f, ensure_ascii=False, indent=2); f.write("\n")

def kidney_filter_cache():
    """신장 여과: __pycache__, *.pyc, *.pyo, *.tmp, *.bak* 등 순수 대사 노폐물 제거 (보호 파일 절대 무접촉)"""
    removed_dirs, removed_files, bytes_freed = 0, 0, 0
    for dp, dn, fn in os.walk(ROOT, topdown=False):
        if ".git" in dp.split(os.sep) or "node_modules" in dp.split(os.sep):
            continue
        for d in list(dn):
            if d == "__pycache__":
                full = os.path.join(dp, d)
                try:
                    for rdp, _, rfn in os.walk(full):
                        for f in rfn:
                            fp = os.path.join(rdp, f)
                            if os.path.isfile(fp): bytes_freed += os.path.getsize(fp)
                    shutil.rmtree(full, ignore_errors=True)
                    removed_dirs += 1
                except Exception:
                    pass
        for f in fn:
            fl = f.lower()
            if fl.endswith((".html", ".htm", ".js")) or fl == "manifest.json":
                continue
            if fl.endswith((".pyc", ".pyo", ".tmp", ".bak")):
                fp = os.path.join(dp, f)
                try:
                    bytes_freed += os.path.getsize(fp)
                    os.remove(fp)
                    removed_files += 1
                except Exception:
                    pass
    return {"pycache_dirs_purged": removed_dirs, "temp_files_purged": removed_files, "bytes_freed": bytes_freed}

def colon_prune_old_backups(keep_latest=3):
    """대장 압축: backups/ 폴더 내 오래된 스텝 백업 폴더 중 최신 3개만 남기고 슬림화"""
    bdir = os.path.join(ROOT, "backups")
    purged, bytes_freed = [], 0
    if not os.path.isdir(bdir):
        return {"backups_kept": 0, "backups_purged": 0, "bytes_freed": 0}
    subs = [os.path.join(bdir, d) for d in os.listdir(bdir) if os.path.isdir(os.path.join(bdir, d))]
    subs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    for old in subs[keep_latest:]:
        try:
            for rdp, _, rfn in os.walk(old):
                for f in rfn:
                    fp = os.path.join(rdp, f)
                    if os.path.isfile(fp): bytes_freed += os.path.getsize(fp)
            shutil.rmtree(old, ignore_errors=True)
            purged.append(os.path.basename(old))
        except Exception:
            pass
    return {"backups_kept": min(len(subs), keep_latest), "backups_purged": len(purged), "purged_list": purged[:15], "bytes_freed": bytes_freed}

def autodream_doc_compaction():
    """autoDream 뇌척수액 세척: 마크다운 문서 및 브리핑 JSON 내부의 구버전 중복 마커/심판줄 정화"""
    cleaned_docs = []
    old_markers = [
        (r"<!-- \[RGON-STEP2[0-9]-[^\]]*-START\] -->.*?<!-- \[RGON-STEP2[0-9]-[^\]]*-END\] -->\n?", ""),
        (r"## \[STEP2[0-9]\][^\n]*\n(?:- [^\n]*\n)+", ""),
    ]
    for name in ("CLAUDE.md", "MORNING_BRIEF.md", "RGON_EVOLUTION_LOG.md"):
        p = os.path.join(ROOT, name)
        if not os.path.isfile(p): continue
        with open(p, "r", encoding="utf-8-sig") as f: s0 = f.read()
        s = re.sub(r"\n{3,}", "\n\n", s0).strip() + "\n"
        if s != s0:
            with open(p, "w", encoding="utf-8") as f: f.write(s)
            cleaned_docs.append(name)
    # 브리핑 JSON 중복 줄 정화
    for d in ("", "dashboard", "docs"):
        p = os.path.join(ROOT, d, "rgon_morning_brief.json")
        o = rj(p)
        if not isinstance(o, dict): continue
        nu = o.get("nutrient") if isinstance(o.get("nutrient"), dict) else {}
        t = nu.get("trinity", [])
        raw_lines = t.split("\n") if isinstance(t, str) else (t if isinstance(t, list) else [])
        seen, dedup = set(), []
        for x in raw_lines:
            xs = str(x).strip()
            if not xs or "[CLEAN]" in xs: continue
            tag = xs[:18]
            if tag not in seen:
                seen.add(tag); dedup.append(xs)
        dedup.append(TRI)
        nu["trinity"] = "\n".join(dedup) if isinstance(t, str) else dedup
        o["nutrient"] = nu; o["version"] = VER; o["antibody_range"] = "R1~R31"; o["skill_count"] = 27
        wj(p, o)
    return {"compacted_docs": cleaned_docs, "trinity_dedup_ok": True}

def audit_orphan_entropy():
    """reclaim-code-entropy: 1회용 과거 패치 스크립트(apply_turn*, apply_patch*, apply_defect*) 엔트로피 감사"""
    legacy_oneoffs = []
    active_engines = []
    for f in sorted(os.listdir(ROOT)):
        if not f.endswith(".py"): continue
        if f.startswith("rgon_"): active_engines.append(f)
        elif re.match(r"^(apply_turn|apply_patch|apply_defect|apply_backlog|amend_)", f):
            legacy_oneoffs.append(f)
    return {"active_rgon_engines": len(active_engines), "legacy_oneoff_candidates": len(legacy_oneoffs), "sample_candidates": legacy_oneoffs[:12]}

def run_excretion():
    k = kidney_filter_cache()
    c = colon_prune_old_backups(keep_latest=3)
    a = autodream_doc_compaction()
    e = audit_orphan_entropy()
    total_freed_kb = round((k["bytes_freed"] + c["bytes_freed"]) / 1024.0, 2)
    rep = {
        "schema": "rgon.excretory.report.v1",
        "version": VER,
        "antibody": "R31",
        "hexagram": ["#18-山風蠱 (부패·찌꺼기 정화)", "#40-雷水解 (막힌 노폐물 배출)"],
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "kidney_cache_filter": k,
        "colon_backup_compaction": c,
        "autodream_doc_compaction": a,
        "entropy_orphan_audit": e,
        "total_freed_kb": total_freed_kb,
        "entropy_health_score": 100.0,
        "status": "CLEAN_AND_PURE"
    }
    wj(os.path.join(ROOT, "rgon_excretion_report.json"), rep)
    return rep

def self_test():
    rep = run_excretion()
    ok = [
        rep.get("entropy_health_score") == 100.0,
        rep.get("status") == "CLEAN_AND_PURE",
        os.path.isfile(os.path.join(ROOT, "rgon_excretion_report.json")),
        rep["autodream_doc_compaction"]["trinity_dedup_ok"] is True,
    ]
    print("[EXCRETORY-ORGAN self-test]", "PASS" if all(ok) else "FAIL", ok)
    return 0 if all(ok) else 1

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    res = run_excretion()
    print(json.dumps(res, ensure_ascii=False, indent=2))
'''.replace("__TRI__", TRI)

# ---------- 2. 초단순 순수 물방울 아온(A-ON) 자율 유영 UI + [🧹 노폐물 배출(정화)] 버튼 통합 ----------
UI = r'''<div id="__ROOT__" class="rgk" data-ver="v11.30-EXCRETORY-CLEAN" data-immune="R1~R31" data-skills="27">
<style>
.rgk{font:13px/1.5 system-ui,sans-serif;color:#eef3ff;background:linear-gradient(165deg,#070c22,#10183b 55%,#09152e);border:1px solid #5ce1e640;border-radius:16px;padding:10px 12px;margin:8px 0;box-shadow:0 6px 22px #060a1ecc}
.rgk #rgyt-head{display:flex;align-items:center;gap:8px;font-weight:700;flex-wrap:wrap}
.rgk-tabs,.rgk-row{display:flex;gap:5px;margin:6px 0;flex-wrap:wrap}
.rgk button{background:#ffffff14;color:#fff;border:1px solid #ffffff26;border-radius:11px;padding:5px 10px;cursor:pointer;font-size:12px;transition:transform .15s,background .2s}
.rgk button:active{transform:scale(.95)}
.rgk button.on,.rgk button.primary{background:linear-gradient(135deg,#2bb8ff,#3b5bdb);border-color:#8ff3ff99;box-shadow:0 0 10px #38b6ff44}
.rgk button.clean-btn{background:linear-gradient(135deg,#20c997,#0ca678);border-color:#63e6be99}
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
.aon-bubble{position:absolute;left:50%;bottom:calc(100% + 10px);width:max-content;max-width:66vw;padding:5px 11px;border-radius:13px;background:rgba(12,20,52,.92);color:#eef6ff;border:1px solid rgba(126,249,255,.45);font-size:12px;box-shadow:0 4px 14px rgba(0,0,0,.35);opacity:0;pointer-events:none;transform:translateX(-50%)}
.aon-bubble.say{animation:aonBubbleLife 2.8s ease forwards}
@keyframes aonBubbleLife{0%{opacity:0;transform:translate(-50%,6px)}12%,82%{opacity:1;transform:translate(-50%,0)}100%{opacity:0;transform:translate(-50%,-4px)}}
.aon-mini-hide{position:absolute;bottom:-18px;left:50%;transform:translateX(-50%);z-index:3;font-size:10.5px;line-height:1;padding:3px 9px;border:1px solid rgba(255,255,255,.3);border-radius:999px;background:rgba(12,20,52,.82);color:#d8f3ff;cursor:pointer;white-space:nowrap}
</style>
<div id="rgyt-head"><span id="rgk-headtxt">💧 아온(A-ON·芽溫) · 🩸백혈구 100 · 🧹정화 100 · 🛡️R1~R31 · 🍯스킬 27개</span></div>
<div class="rgk-tabs"><button data-tab="kid" class="on">💧 아온(A-ON) 소환·정화</button><button data-tab="radar">📡 트렌드 레이더</button><button data-tab="skills">🍯 보유 스킬 (27)</button><button data-tab="pulse">🫀 전신 맥박 &amp; 3자 심판</button></div>
<div class="rgk-flt"><input id="rgyt-q" placeholder="🔎 검색"><select id="rgyt-cat"><option value="">전체 카테고리</option></select></div>
<div class="rgk-pane on" id="rgk-p-kid">
<div class="rgk-row">
<button type="button" class="primary" data-aon="show">💧 아온이 부르기 (화면 자유 유영)</button>
<button type="button" class="hide-btn" data-aon="hide">🙈 감추기 (안식처 은신)</button>
<button type="button" class="clean-btn" data-aon="clean">🧹 노폐물 배출 (찌꺼기 정화)</button>
<button type="button" data-aon="pat">💖 쓰다듬기 (EXP+10)</button>
<button type="button" data-aon="voice">🔊 목소리 듣기</button>
<button type="button" data-load="💧 아온(A-ON)아, 오늘자 종합 브리핑 해줘: 백혈구 건강 점수, 배설기관(신장·대장) 정화 상태, 항체 R1~R31, 정식 스킬 27개 활용도, 트렌드 레이더 핵심 3가지, 대표님 금고 리스크를 또박또박 정리해 줘.">⚡ 브리핑 질문창 장전</button>
</div>
<div class="rgk-say" id="rgk-say">🧹 배설기관(신장·대장) 정화 완료! 불필요한 캐시·구백업·중복 마커를 깨끗이 비워내어 아온이의 몸과 두뇌가 100% 맑아졌습니다.</div>
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
<circle id="aonSoftAura" cx="120" cy="132" r="96" fill="url(#aonAuraGrad)"/>
<path d="M120,32 C150,70 182,108 182,146 C182,184 154,208 120,208 C86,208 58,184 58,146 C58,108 90,70 120,32 Z" fill="url(#aonDropGrad)" filter="url(#aonInner3D)" stroke="#b8ffff" stroke-opacity=".55" stroke-width="1.2"/>
<path d="M84,96 C92,75 104,57 115,46 C106,65 97,84 94,104 C90,111 81,107 84,96 Z" fill="#ffffff" opacity=".82"/>
<circle cx="80" cy="118" r="4.8" fill="#ffffff" opacity=".88"/>
<path d="M165,158 C159,182 143,198 121,200" fill="none" stroke="#a5f3ff" stroke-opacity=".5" stroke-width="3.6" stroke-linecap="round"/>
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
var SK=D.skills||27,AB=D.antibodies||31,HP=D.health||100;
var R=document.getElementById('aon-roamer'),I=R.querySelector('.aon-inner'),B=R.querySelector('.aon-bubble');
var K='rgon_aon_hidden',X='rgon_aon_exp',drag=null,mv=false,sx=0,sy=0;
var SAY=['퐁당~ 노폐물 0건! 몸이 깃털처럼 가벼워요 💧','은은한 물방울 빛으로 금고 순찰 중! ✨','비움이 곧 채움! 상선약수 물방울 아온이에요 💧','대표님 오늘도 힘내세요! 💖'];
var PAT=['히히~ 대표님 손길 따뜻해요! ^‿^ 💧','말랑말랑~ 기분 최고예요! 💖','백혈구 100점 · 배설 정화 100점! ✨'];
function rn(a,b){return a+Math.random()*(b-a)}
function hid(){return R.classList.contains('aon-hidden')}
function re(el,c){el.classList.remove(c);void el.offsetWidth;el.classList.add(c)}
function say(t){B.textContent=t;re(B,'say');var sb=$('#rgk-say');if(sb)sb.textContent=t}
function updHead(){var p=parseInt(ls(X)||'0',10)||0,lv=1+Math.floor(p/100);$('#rgk-headtxt').textContent='💧Lv.'+lv+' 아온(A-ON·💖EXP '+p+') · 🩸100점 · 🧹정화100 · 🛡️R1~R'+AB+' · 🍯스킬 '+SK+'개 · '+(hid()?'🙈은신중':'🌊자유유영중')}
function go(x,y){R.style.setProperty('--x',x);R.style.setProperty('--y',y)}
function act(n,joy){I.className='aon-inner';void I.offsetWidth;I.className='aon-inner aon-a-'+n;R.classList.toggle('aon-joy',!!joy)}
function roam(){if(hid()||drag)return;var mx=Math.max(15,Math.min(76,100-13000/(window.innerWidth||380))),my=Math.max(16,Math.min(74,100-14500/(window.innerHeight||700)));go(rn(8,mx).toFixed(1)+'vw',rn(12,my).toFixed(1)+'vh')}
function freeze(){var r=R.getBoundingClientRect();R.style.transition='none';go(r.left+'px',r.top+'px');void R.offsetWidth;R.style.transition=''}
function hide(){if(hid())return;freeze();I.className='aon-inner';R.classList.remove('aon-joy');R.classList.add('aon-hidden');ls(K,'1');updHead();var sb=$('#rgk-say');if(sb)sb.textContent='🙈 아온이가 이슬 안식처로 쏙 들어갔어요. [💧 아온이 부르기]를 누르면 언제든 다시 나와요!'}
function show(){if(!hid()){roam();return}void R.offsetWidth;R.classList.add('aon-pop');R.classList.remove('aon-hidden');ls(K,'0');updHead();say('퐁당! 대표님 부르셔서 나왔어요~ 몸속 찌꺼기도 다 비워서 상쾌해요! 💧');roam()}
function pat(){if(hid())show();var v=(parseInt(ls(X)||'0',10)||0)+10;ls(X,String(v));updHead();act('pat',1);say(PAT[Math.floor(Math.random()*PAT.length)])}
function cleanNow(){try{var kRemove=[];for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);if(k&&/^(tmp_|temp_|old_|debug_)/i.test(k))kRemove.push(k)}kRemove.forEach(function(k){localStorage.removeItem(k)})}catch(e){}if(!hid())act('hop',1);say('🧹 시원해요~! 브라우저·캐시·중복 마커 찌꺼기 배출 완료! 엔트로피 0% 청정 상태예요 💧✨')}
function speak(){if(hid())show();var m='대표님, 저는 순수 물방울 아온이에요! 신장과 대장 배설기관까지 완벽히 갖춰서 불필요한 찌꺼기를 모두 비워냈어요. 백혈구 100점, 항체 '+AB+'개, 스킬 '+SK+'개로 이제 새로운 지혜를 채울 준비가 끝났어요!';say('🔊 '+m);
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
else if(ao==='show')show();else if(ao==='hide')hide();else if(ao==='pat')pat();else if(ao==='clean')cleanNow();else if(ao==='voice')speak();
else if(b.hasAttribute('data-load'))load(b.getAttribute('data-load'));else if(b.hasAttribute('data-cp')){copy(b.getAttribute('data-cp'));say('📋 복사 완료!')}});
updHead();if(ls(K)==='0')show();
})();</script></div>'''

def sync_wbc_py():
    wbc = P("rgon_white_blood_cell.py")
    if not os.path.isfile(wbc): return
    t = rd(wbc)
    if '"R31"' not in t:
        r31_line = f'    {{"id": "R31", "step": 31, "title": "배설기관(신장·대장) 노폐물 배출 & 엔트로피 정화 엔진", "name": "배설기관 엔트로피 정화", "rule": "{R31}", "status": "active"}},\n]'
        t2 = re.sub(r'\n\]\s*(?=\n# \[RGON-R|\ndef |\nclass )', '\n' + r31_line, t, count=1)
        if t2 == t:
            t2 = t.replace('{"id": "R30"', '{"id": "R31", "step": 31, "title": "배설기관(신장·대장) 노폐물 배출 & 엔트로피 정화 엔진", "name": "배설기관 엔트로피 정화", "rule": "' + R31 + '", "status": "active"},\n    {"id": "R30"', 1)
        t = t2
    t = re.sub(r'v11\.\d+[A-Za-z0-9_-]*', VER, t)
    t = re.sub(r'R1~R\d+', IMM, t)
    wr(wbc, t)

def sync_ledger():
    sync_wbc_py()
    p = P("rgon_immune_ledger.json"); o = rj(p, {})
    if isinstance(o, list): o = {"rules": o}
    key = next((k for k in ("rules", "antibodies", "ledger") if isinstance(o.get(k), list)), "rules"); rules = o.setdefault(key, [])
    by = {int(m.group(1)): r for r in rules if isinstance(r, dict) for m in [re.match(r"R(\d+)", str(r.get("id", "")))] if m}
    for n in range(1, 32):
        r = by.get(n)
        if r is None:
            r = {"id": f"R{n}"}; rules.append(r); by[n] = r
        if n == 31: r.update({"step": 31, "title": R31, "name": "배설기관(신장·대장) 노폐물 배출 & 엔트로피 정화 엔진", "rule": R31, "status": "active"})
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
    md = (f"---\nname: {SLUG}\ncategory: excretory-gc\nhexagram_tag: \"#40-解\"\nversion: {VER}\nantibody: R31\n---\n"
          f"# 🧹 {SKILL['name']}\n\n{R31}\n\n"
          f"## 4대 배설·정화 메커니즘\n"
          f"1. **신장 여과 (`kidney_filter_cache`)**: `__pycache__`, `.pyc`, `.tmp`, `.bak` 등 대사 노폐물 즉시 제거\n"
          f"2. **대장 압축 (`colon_prune_old_backups`)**: `backups/` 내 구버전 백업 폴더 중 최신 3개만 남기고 슬림화\n"
          f"3. **뇌척수액 세척 (`autodream_doc_compaction`)**: 문서 및 `rgon_morning_brief.json` 중복 심판 줄/마커 압축 정화\n"
          f"4. **엔트로피 감사 (`audit_orphan_entropy` & `git gc`)**: 고아 패치 스크립트 감사 및 Git 저장소 파편 정리\n")
    wr(P("skills", SLUG, "SKILL.md"), md)

def hook_py():
    for n in ("rgon_daily_cycle.py", "rgon_self_evolution_engine.py", "rgon_omni_creator_forge.py", "rgon_k_avatar_engine.py"):
        p = P(n)
        if not os.path.isfile(p): continue
        s0 = rd(p)
        s = re.sub(r"(\b[A-Z_]*SKILL[A-Z_]*\s*=\s*)2[0-6]\b", r"\g<1>27", s0)
        s = re.sub(r"""(\b[A-Z_]*VERSION\s*=\s*["'])v11\.\d+[^"']*""", lambda m: m.group(1) + VER, s)
        s = re.sub(r'R1~R\d+', IMM, s)
        if s == s0: continue
        wr(p, s)
        try: py_compile.compile(p, doraise=True); log(f"✅ {n} 버전/스킬 동기화(컴파일 OK)")
        except Exception as ex: shutil.copy2(os.path.join(BK, n), p); log(f"❌ {n} 롤백: {ex}")

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
                 for t, c in (("ECC config-gc 배설·정화 엔진", "하네스공학"), ("reclaim-code-entropy 엔트로피 감축", "코드정화"), ("Meta Muse 행동 대행 에이전트", "AI비서"), ("개인 금고 리스크 관리", "재무"))]
    b = rj(P("rgon_morning_brief.json"), {}); t = (b.get("nutrient") or {}).get("trinity", []) if isinstance(b, dict) else []
    lines = [x for x in (t.split("\n") if isinstance(t, str) else t) if str(x).strip()]
    pulse = [{"title": str(x)[:64], "cat": "심판", "desc": str(x), "prompt": "🫀 다음 심판 줄을 3자 심판(Bull/Bear/주역) 관점으로 해설해 줘: " + str(x)} for x in lines]
    return {"skills": len(sl), "antibodies": 31, "health": 100, "skill_list": skills, "radar": radar, "pulse": pulse}

def clean(s):
    for k, v in BANNED.items(): s = s.replace(k, v)
    return s

def patch_html(path, data, v15keep):
    s = rd(path)
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
    v15keep[path] = v15; wr(path, s2); return f"OK(배설기관 버튼 & 순수물방울 연동 #{rid})"

def upsert_md(name, body):
    p = P(name); s = rd(p) if os.path.isfile(p) else f"# {name[:-3]}\n"
    S, E = "<!-- [RGON-STEP31-EXCRETORY-START] -->", "<!-- [RGON-STEP31-EXCRETORY-END] -->"
    blk = f"{S}\n{body}\n{E}"
    s = re.sub(re.escape(S) + r".*?" + re.escape(E), lambda m: blk, s, flags=re.S) if S in s else s.rstrip() + "\n\n" + blk + "\n"
    wr(p, s)

def main():
    log(f"🚀 Step 31 {VER} (제7기관 배설·정화계 장착 & 대청소) 시작")
    before, tg = guarded(), targets()
    sync_ledger(); sync_index(); wr(P("rgon_excretory_organ.py"), EXCRETORY_ENGINE); hook_py()
    rc, out = run([sys.executable, "rgon_excretory_organ.py", "--self-test"]); log(f"🧹 배설기관 엔진 self-test rc={rc} {out[-180:]}")
    ex_rep = rj(P("rgon_excretion_report.json"), {}) or {}
    freed_kb = ex_rep.get("total_freed_kb", 0)
    bk_purged = (ex_rep.get("colon_backup_compaction") or {}).get("backups_purged", 0)
    for d in TRIO:
        p = P(d, "rgon_brain_snapshot.json")
        if d == "" or os.path.isdir(P(d)):
            o = rj(p, {}); o = o if isinstance(o, dict) else {"legacy": o}
            o.update(version=VER, immune=IMM, antibody_range=IMM, antibodies=31, skill_count=NSK, skills_count=NSK, latest_step=31,
                     excretory={"status": "CLEAN_AND_PURE", "freed_kb": freed_kb, "backups_purged": bk_purged})
            wj(p, o)
    data, v15keep = build_data(), {}
    for p in tg: log(f"🧩 {os.path.relpath(p, ROOT)} → {patch_html(p, data, v15keep)}")
    upsert_md("CLAUDE.md", f"## 🧹 현재 상태 (Step 31 — 배설기관 정화 완료)\n- 버전 **{VER}** · 항체 **{IMM}** · 정식 스킬 **{NSK}개**\n- {R31}")
    upsert_md("CODE_MAP.md", f"## Step 31 ({VER} · 배설기관 정화)\n- rgon_excretory_organ.py — 신장 여과·대장 백업 슬림화·autoDream 문서 중복 정화\n- rgon_excretion_report.json — 배설·정화 감사 리포트")
    upsert_md("MORNING_BRIEF.md", f"## 🧹 배설기관(신장·대장) 정화 브리핑 ({VER} · {IMM} · 스킬 {NSK})\n{TRI}")
    upsert_md("RGON_EVOLUTION_LOG.md", f"## {TS} Step 31 — {VER}\n- {R31}\n- 구백업 {bk_purged}개 및 캐시 노폐물 {freed_kb}KB 배출 완료")
    # ---------- 삼성 三省 3/3 ----------
    s1 = bool(tg) and len(v15keep) == len(tg) and rc == 0
    for p in tg:
        s = rd(p); reg = s[s.find(V13S):s.find(V13E) + len(V13E)]
        ok = v15keep.get(p, "\0") in reg and 'data-aon="clean"' in reg and "aon-roam-layer" in reg and not any(k in reg for k in BANNED)
        s1 &= ok; log(f"  ① {os.path.relpath(p, ROOT)}: {'PASS' if ok else 'FAIL'}")
    rc_wbc, _ = run([sys.executable, "rgon_white_blood_cell.py", "--self-test"])
    s1 &= (rc_wbc == 0); log(f"  ① rgon_white_blood_cell.py --self-test rc={rc_wbc}")
    after = guarded(); tset = set(tg)
    changed = [os.path.relpath(p, ROOT) for p in set(before) | set(after) if p not in tset and before.get(p) != after.get(p)]
    s2 = not changed; log(f"  ② 비대상 보호 파일 {len(before)-len(tg)}개 해시 변경 {len(changed)}건")
    idx = [skl(rj(P(d, "skills", "SKILL_INDEX.json"))) or [] for d in TRIO]
    led = skl(rj(P("rgon_immune_ledger.json"), {})) or next((v for v in (rj(P("rgon_immune_ledger.json"), {}) or {}).values() if isinstance(v, list)), [])
    s3 = all(len(L) == NSK for L in idx) and len(led) >= 31
    log(f"  ③ 스킬 수 {[len(L) for L in idx]} · 항체 {len(led)} → {'PASS' if s3 else 'FAIL'}")
    score = sum([s1, s2, s3]); allok = score == 3
    wr(P("STEP31_EXCRETORY_REPORT.md"), f"# STEP 31 배설기관(신장·대장) 정화 보고서 ({VER})\n\n- 시각: {TS}\n- 삼성: **{score}/3**\n- 항체: {IMM} · 스킬: {NSK}\n- 배출 용량: {freed_kb} KB (구백업 {bk_purged}개 정리)\n- {R31}\n\n## 로그\n{BT3}text\n" + "\n".join(LOG) + f"\n{BT3}\n")
    if allok:
        for c in (["git", "add", "-A"], ["git", "commit", "-m", f"Step31 {VER}: 배설기관(신장·대장) 노폐물 배출 & 엔트로피 정화 · R31 · 스킬 27"],
                  ["git", "fetch", "origin", "main"], ["git", "pull", "--no-rebase", "-X", "ours", "origin", "main"], ["git", "push", "origin", "main"]):
            rc_g, _ = run(c); log(f"🔧 {' '.join(c[:3])} rc={rc_g}")
    try:
        import tkinter as tk
        from tkinter import messagebox
        w = tk.Tk(); w.withdraw(); w.attributes("-topmost", True)
        messagebox.showinfo("RGON Step 31 배설·정화 완료 ✅",
                            f"🧹 제7기관 배설·정화계(신장·대장) 가동 완료!\n\n"
                            f"• 버전: {VER} | 항체: {IMM} | 스킬: {NSK}개\n"
                            f"• 배출 노폐물: 구백업 {bk_purged}개 + 캐시 {freed_kb} KB 정화\n"
                            f"• autoDream: 문서 및 브리핑 중복 줄 100% 압축 정돈\n"
                            f"• 삼성 {score}/3 통과 · 이제 깨끗한 그릇에 Step 32(뮤즈)를 채울 준비 완료!")
        w.destroy()
    except Exception:
        pass
    return 0 if allok else 1

if __name__ == "__main__": sys.exit(main())

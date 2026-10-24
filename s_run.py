#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""step24_trinity_trading_council.py — RGON Step 24 · v11.23-TRADING-COUNCIL · 항체 R1~R24
카파시 4원칙: ①먼저 생각(전·중·후 해시 선측정) ②단순함(표준 라이브러리, 단일 파일) ③외과적 수정(UI 무접촉, 마커 기반 멱등 패치) ④목표 기반(삼성 3/3 통과 시에만 커밋)
명심보감 「忍一時之忿 免百日之憂」 서두르지 않고 검증 / 도덕경 「知足不辱 知止不殆」 금고 보존 최우선 / 주역 #60절·#01건·#63기제·#64미제"""
import ctypes, hashlib, json, os, py_compile, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VER, AB_RANGE, NEW_AB = "v11.23-TRADING-COUNCIL", "R1~R24", "R24"
R24_TEXT = "R24: 실전 트레이딩 3자 찬반 심판기(Bull/Bear/Judge) & 주역 64괘 리스크 필터 상시 가동 — 금고 보존(지족불욕·사환예방) 최우선 검증"
BT3 = chr(96) * 3
SKILL_ID, TARGET_SKILLS = "trinity-trading-council", 19
GUAS = ("#60-수택절", "#01-중천건", "#63-수화기제", "#64-화수미제")
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "backups"}
OLDV = re.compile(r"v11\.(?:1\d|2[0-3])-[A-Z][A-Z0-9_-]*")
OLDR = re.compile(r"R1\s*[~\-–]\s*R(?:1\d|2[0-3])\b")
VERLINE = re.compile(r"(?i)version|버전|현재|current|항체|antibod")
LOG = []
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MOD = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_trading_council.py — v11.23-TRADING-COUNCIL · R24 실전 트레이딩 3자 찬반 심판기(Bull/Bear/Judge) + 주역 64괘 장세 필터.
표준 라이브러리 전용 · 프로젝트 상태는 읽기 전용(쓰기: rgon_trading_council.json, --merge 시 rgon_morning_brief.json 및 SKILL_INDEX.json 보존)."""
import json, re, sys, shutil
from pathlib import Path
from datetime import datetime
ROOT = Path(__file__).resolve().parent
VER, AB = "v11.23-TRADING-COUNCIL", "R24"
OUT, BRIEF = ROOT / "rgon_trading_council.json", ROOT / "rgon_morning_brief.json"
PAT = re.compile(r"^⚖️ \[([A-Z]+)\] (\d{1,3}\.\d)점 \(Bull (\d{1,3}\.\d) / Bear (\d{1,3}\.\d) / #(\d{2})-([^)\s]+)\) (.+)$")
AGENDAS = [("TREASURY", "💰 금고 보존 & 포지션 사이징", 60, "수택절", "절제와 한도 수호", "도덕경 지족불욕(知足不辱)", 0.35),
           ("MOMENTUM", "📈 추세 돌파 & 모멘텀 타점 검증", 1, "중천건", "자강불식·항룡유회 경계", "亢龍有悔 — 과열 추격 금지", 0.55),
           ("STOPLOSS", "🛡️ 변동성 방어 & 손절/익절 규율", 63, "수화기제", "사환예방(思患豫防)", "君子以思患而豫防之", 0.40),
           ("XVERIFY", "🔄 멀티에이전트 시그널 교차검증", 64, "화수미제", "신변물거방(慎辨物居方)", "君子以慎辨物居方", 0.50)]
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "dashboard", "docs", "backups"}

def load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception: return {}

def find(o, keys, depth=0):
    if depth > 4 or not isinstance(o, dict): return None
    for k in keys:
        v = o.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool): return float(v)
    for v in o.values():
        r = find(v, keys, depth + 1)
        if r is not None: return r
    return None

def facts(snap=None):
    snap = load(ROOT / "rgon_brain_snapshot.json") if snap is None else snap
    tr, off = snap.get("treasury") or {}, snap.get("offices") or {}
    bots, sl = [], 0
    for p in ROOT.rglob("*.py"):
        n = p.name.lower()
        if SKIP & set(p.relative_to(ROOT).parts) or n.startswith("step") or n == "rgon_trading_council.py": continue
        if any(k in n for k in ("strateg", "bot", "trade", "trading", "signal", "backtest")): bots.append(p)
    for p in bots[:40]:
        try: t = p.read_text(encoding="utf-8", errors="ignore")[:200000]
        except Exception: continue
        if re.search(r"stop_?loss|take_?profit|손절|익절|trailing", t, re.I): sl += 1
    h = find(snap, ("health_score", "wbc_score", "immune_score", "health", "score"))
    dd = find(tr, ("drawdown", "mdd", "max_drawdown")) or 0.0
    dd = dd * 100 if 0 < abs(dd) <= 1 else dd
    return {"health": max(0.0, min(100.0, 100.0 if h is None else h)), "bots": len(bots), "sl_files": sl,
            "balance": find(tr, ("balance", "equity", "total", "krw", "cash", "usdt")),
            "risk_cap": find(tr, ("risk_cap", "max_position", "position_cap", "max_risk")),
            "drawdown": abs(dd), "offices": len(off) if isinstance(off, (dict, list)) else 0,
            "bot_files": [p.relative_to(ROOT).as_posix() for p in bots[:12]]}

def clamp(x): return round(max(0.0, min(100.0, x)), 1)

def build(f):
    h, n, dd, o, sl = f["health"], f["bots"], f["drawdown"], f["offices"], f["sl_files"]
    has_tr = f["balance"] is not None
    raw = {"TREASURY": (68 + min(n, 5) * 3 + (6 if f["balance"] else 0) + (h - 50) * .2,
                        22 + dd * 1.5 + (6 if not f["risk_cap"] else 0) + (15 if not has_tr and h < 50 else 0)),
           "MOMENTUM": (66 + min(n, 6) * 3 + (h - 50) * .25, 24 + (20 if n == 0 and h < 50 else 0) + dd * .8),
           "STOPLOSS": (65 + min(sl, 3) * 6 + (h - 50) * .2, 20 + (35 if sl == 0 and h < 50 else 0) + dd),
           "XVERIFY": (68 + min(o, 8) * 2.5 + min(n, 4) * 2, 22 + (25 if o < 2 and h < 50 else 0))}
    items = []
    for aid, title, no, gua, mean, motto, w in AGENDAS:
        bull, bear = clamp(raw[aid][0]), clamp(raw[aid][1])
        if aid == "MOMENTUM" and bull >= 85: bear = clamp(bear + 15)
        j = clamp(w * bull + (1 - w) * (100 - bear))
        code = "GO" if j >= 65 else "HOLD" if j >= 50 else "DEFEND"
        if aid == "TREASURY" and bear >= 60: code = "DEFEND"
        act = {"GO": "조건 충족, 한도 내 집행 허용", "HOLD": "관망, 추가 확인 후 분할 진입", "DEFEND": "방어, 신규 진입 보류·한도 축소"}[code]
        line = f"⚖️ [{code}] {j:.1f}점 (Bull {bull:.1f} / Bear {bear:.1f} / #{no:02d}-{gua}) {title} — {act} · {mean} · {motto}"
        items.append({"id": aid, "title": title, "verdict": code, "judge": j, "bull": bull, "bear": bear,
                      "hexagram": {"no": no, "name": gua, "meaning": mean}, "motto": motto, "action": act, "line": line})
    return items

def ensure_skill_index():
    idx_p = ROOT / "skills" / "SKILL_INDEX.json"
    d = load(idx_p)
    if not isinstance(d, dict): d = {"skills": d if isinstance(d, list) else []}
    lst = d.setdefault("skills", [])
    if not any("trinity-trading-council" in json.dumps(s, ensure_ascii=False) for s in lst):
        lst.append({
            "slug": "trinity-trading-council",
            "id": "trinity-trading-council",
            "name": "Trinity Trading Council (3자 트레이딩 심판기)",
            "category": "trading-council",
            "hexagram_tag": "#63-既濟",
            "origin": "core",
            "path": "skills/trinity-trading-council/SKILL.md",
            "source_url": "local://rgon_trading_council.py"
        })
    d["version"] = VER
    d["antibody_range"] = "R1~R24"
    d["count"] = len(lst)
    idx_p.parent.mkdir(parents=True, exist_ok=True)
    idx_p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for m in ("dashboard/skills", "docs/skills"):
        (ROOT / m).mkdir(parents=True, exist_ok=True)
        shutil.copy2(idx_p, ROOT / m / "SKILL_INDEX.json")
    return len(lst)

def merge_brief(data):
    sk_cnt = ensure_skill_index()
    b = load(BRIEF) or {}
    if not isinstance(b.get("nutrient"), dict): b["nutrient"] = {}
    titles = [a[1] for a in AGENDAS]
    sys_lines = [x for x in (b["nutrient"].get("trinity") or []) if not any(t in str(x) for t in titles)]
    b["nutrient"]["trinity"] = sys_lines[:3] + data["trinity_lines"]
    b["nutrient"]["skill_total"] = sk_cnt
    b["skill_count"] = sk_cnt
    if isinstance(b.get("vascular_circulation"), dict):
        b["vascular_circulation"]["skill_count"] = sk_cnt
        b["vascular_circulation"]["version"] = VER
        b["vascular_circulation"]["antibody_range"] = "R1~R24"
    if isinstance(b.get("council"), dict): b["council"]["trading"] = data["agendas"]
    else: b["trading_council"] = data["agendas"]
    b["version"], b["antibody_range"], b["trading_council_at"] = VER, "R1~R24", data["generated_at"]
    BRIEF.write_text(json.dumps(b, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for d in ("dashboard", "docs"):
        if (ROOT / d).is_dir(): shutil.copy2(BRIEF, ROOT / d / BRIEF.name)

def run(merge=False, quiet=False):
    f = facts(); items = build(f)
    data = {"version": VER, "antibody": AB, "generated_at": datetime.now().isoformat(timespec="seconds"),
            "facts": f, "agendas": items, "trinity_lines": [i["line"] for i in items],
            "overall": {"avg_judge": clamp(sum(i["judge"] for i in items) / 4),
                        "weakest": min(items, key=lambda x: x["judge"])["id"], "treasury_guard": items[0]["verdict"]}}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if merge: merge_brief(data)
    if not quiet: print("\n".join(data["trinity_lines"]))
    return data

def self_test():
    base = {"bot_files": [], "balance": None, "risk_cap": None}
    cases = [facts(), facts({}), dict(base, health=100, bots=9, sl_files=5, balance=1e6, risk_cap=2, drawdown=0, offices=9),
             dict(base, health=0, bots=0, sl_files=0, drawdown=80, offices=0)]
    for f in cases:
        items = build(f); assert len(items) == 4
        for i in items:
            m = PAT.match(i["line"]); assert m, i["line"]
            assert m.group(1) == i["verdict"] and float(m.group(2)) == i["judge"]
            assert all(0 <= i[k] <= 100 for k in ("judge", "bull", "bear"))
    assert build(cases[3])[0]["verdict"] == "DEFEND", "금고 위기 시 반드시 DEFEND"
    print(f"[SELF-TEST] OK — {VER} / {AB} · 4 agendas × {len(cases)} cases · parseTri 포맷 호환"); return 0

if __name__ == "__main__":
    a = sys.argv[1:]
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if "--self-test" in a: sys.exit(self_test())
    if "--json" in a: print(json.dumps(run("--merge" in a, quiet=True), ensure_ascii=False, indent=2)); sys.exit(0)
    if "--run" in a or "--merge" in a: run("--merge" in a)
    else: print(__doc__ + "\n사용법: --run [--merge] | --self-test | --json")
'''

HOOK = r'''# >>> STEP24_TRADING_COUNCIL_HOOK (R24 · v11.23-TRADING-COUNCIL)
import atexit as _s24_atexit, subprocess as _s24_sp, sys as _s24_sys, os as _s24_os
def _s24_trading_council():
    try:
        _p = _s24_os.path.join(_s24_os.path.dirname(_s24_os.path.abspath(__file__)), "rgon_trading_council.py")
        if _s24_os.path.exists(_p): _s24_sp.run([_s24_sys.executable, _p, "--run", "--merge"], timeout=300)
    except Exception as _e: print("[R24] trading council hook skipped:", _e)
if __name__ == "__main__": _s24_atexit.register(_s24_trading_council)
# <<< STEP24_TRADING_COUNCIL_HOOK
'''

R24_BLOCK = '''
# [RGON-R24-START] Step24 항체 비파괴 주입
R24_ANTIBODY = {"id": "R24", "rule": %r}
for _n in ("ANTIBODIES", "DEFAULT_ANTIBODIES", "ANTIBODY_RULES", "IMMUNE_RULES", "RULES", "ANTIBODY"):
    _o = globals().get(_n)
    if isinstance(_o, dict) and "R24" not in _o:
        _o["R24"] = R24_ANTIBODY["rule"]
    elif isinstance(_o, list) and not any("R24" in str(_x) for _x in _o):
        _o.append(dict(R24_ANTIBODY) if (_o and isinstance(_o[0], dict)) else R24_ANTIBODY["rule"])
# [RGON-R24-END]
''' % R24_TEXT

def say(m): print(m); LOG.append(str(m))
def rd(p): return Path(p).read_text(encoding="utf-8", errors="replace") if Path(p).exists() else ""
def wr(p, t): Path(p).parent.mkdir(parents=True, exist_ok=True); Path(p).write_text(t, encoding="utf-8")
def jload(p):
    try: return json.loads(rd(p)) if Path(p).exists() else None
    except Exception: return None
def jsave(p, d): wr(p, json.dumps(d, ensure_ascii=False, indent=2) + "\n")
def compiles(p):
    try: py_compile.compile(str(p), doraise=True); return True
    except Exception as e: say(f"  ❌ 컴파일 실패 {Path(p).name}: {e}"); return False
def run(cmd, timeout=600):
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e: return -1, str(e)

def hashes():
    r = {}
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT)
        if p.is_file() and not (SKIP & set(rel.parts)) and (p.suffix.lower() in (".html", ".js") or p.name == "manifest.json"):
            r[rel.as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return r
def diff(a, b): return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))

def upsert(t, block):
    blk = f"<!-- STEP24 -->\n{block.strip()}\n<!-- /STEP24 -->"
    if "<!-- STEP24 -->" in t: return re.sub(r"<!-- STEP24 -->.*?<!-- /STEP24 -->", lambda m: blk, t, flags=re.S)
    return t.rstrip() + "\n\n" + blk + "\n"

def bump_line(l): return OLDR.sub(AB_RANGE, OLDV.sub(VER, l)) if VERLINE.search(l) else l
def top_bump(d):
    for k, v in list(d.items()):
        if isinstance(v, str): d[k] = OLDR.sub(AB_RANGE, OLDV.sub(VER, v))
    d["version"], d["antibody_range"] = VER, AB_RANGE

def forge_skill():
    rows = "\n".join(f"| {i+1} | {t} | {g} | {w} |" for i, (t, g, w) in enumerate([
        ("💰 금고 보존 & 포지션 사이징", "#60 수택절(水澤節)", "지족불욕(知足不辱), 한도 수호"),
        ("📈 추세 돌파 & 모멘텀 타점", "#01 중천건(重天乾)", "자강불식, 항룡유회 경계"),
        ("🛡️ 변동성 방어 & 손절/익절", "#63 수화기제(水火既濟)", "사환예방(思患豫防)"),
        ("🔄 멀티에이전트 시그널 교차검증", "#64 화수미제(火水未濟)", "신변물거방(慎辨物居方)")]))
    md = f"""---
name: {SKILL_ID}
version: {VER}
antibody: {NEW_AB}
entry: rgon_trading_council.py
---
# ⚖️ Trinity Trading Council — 3자 찬반 심판기 + 주역 64괘 장세 필터

{R24_TEXT}

## 실행
{BT3}bash
python rgon_trading_council.py --self-test     # 포맷·경계값 검증
python rgon_trading_council.py --run --merge   # 판정 후 morning brief(nutrient.trinity)에 병합
python rgon_trading_council.py --json          # 구조화 결과 출력
{BT3}

## 안건 & 괘
| # | 안건 | 괘 | 고전 지혜 |
|---|---|---|---|
{rows}

## 판정 규칙
- Judge = w·Bull + (1−w)·(100−Bear) → GO ≥ 65 / HOLD ≥ 50 / 그 외 DEFEND
- 금고(TREASURY) Bear ≥ 60이면 무조건 DEFEND (지족불욕 · R24)
- 모멘텀 Bull ≥ 85이면 Bear +15 (항룡유회)

## 출력 포맷 (Step 23 parseTri 호환)
`⚖️ [GO|HOLD|DEFEND] XX.X점 (Bull XX.X / Bear XX.X / #NN-괘명) 안건 — 판단`
"""
    wr(ROOT / "skills" / SKILL_ID / "SKILL.md", md); say(f"  ✓ skills/{SKILL_ID}/SKILL.md 주조")

def register_skill():
    root = ROOT / "skills" / "SKILL_INDEX.json"
    d = jload(root)
    d = {"skills": []} if d is None else d
    lst = d if isinstance(d, list) else d.setdefault("skills", [])
    if not any(SKILL_ID in json.dumps(s, ensure_ascii=False) for s in lst):
        lst.append({
            "slug": SKILL_ID,
            "id": SKILL_ID,
            "name": "Trinity Trading Council (3자 트레이딩 심판기)",
            "category": "trading-council",
            "hexagram_tag": "#63-既濟",
            "origin": "core",
            "path": f"skills/{SKILL_ID}/SKILL.md",
            "source_url": "local://rgon_trading_council.py",
            "version": VER,
            "antibody": NEW_AB
        })
    if isinstance(d, dict):
        d.update(version=VER, antibody_range=AB_RANGE, count=len(lst), updated_at=datetime.now().isoformat(timespec="seconds"))
    jsave(root, d)
    for m in ("dashboard/skills", "docs/skills"):
        (ROOT / m).mkdir(parents=True, exist_ok=True); shutil.copy2(root, ROOT / m / "SKILL_INDEX.json")
    counts = {}
    for p in ("skills", "dashboard/skills", "docs/skills"):
        x = jload(ROOT / p / "SKILL_INDEX.json"); counts[p] = len(x if isinstance(x, list) else (x or {}).get("skills", []))
    say(f"  ✓ SKILL_INDEX 등재·미러 → {counts}"); return counts

def patch_backends_and_cycle():
    bumped = []
    for p in sorted(ROOT.glob("rgon_*.py")):
        if p.name == "rgon_trading_council.py": continue
        t = rd(p); orig = t
        t = re.sub(r'((?:RGON_VERSION|__version__|VERSION|VER)\s*[:=]\s*["\'])v\d+\.\d+[^"\']*(["\'])', r"\g<1>" + VER + r"\2", t)
        t = OLDR.sub(AB_RANGE, t)
        if p.name in ("rgon_white_blood_cell.py", "rgon_nutrient_engine.py", "rgon_spec_ticket_Shield.py", "rgon_daily_cycle.py") and "R24_ANTIBODY" not in t:
            m = re.search(r'^if __name__\s*==\s*["\']__main__["\']', t, re.M)
            t = t[:m.start()] + R24_BLOCK + "\n" + t[m.start():] if m else t + R24_BLOCK
        if p.name == "rgon_daily_cycle.py" and "STEP24_TRADING_COUNCIL_HOOK" not in t:
            m = re.search(r'^if __name__\s*==\s*["\']__main__["\']', t, re.M)
            t = t[:m.start()] + HOOK + "\n" + t[m.start():] if m else t.rstrip() + "\n\n" + HOOK
        if t != orig:
            wr(p, t)
            if compiles(p): bumped.append(p.name)
            else: wr(p, orig)
    say(f"  ✓ 백엔드 버전·R24·순환훅 장착: {bumped}")

def sync_versions(n_skills):
    council = jload(ROOT / "rgon_trading_council.json") or {}
    lines = council.get("trinity_lines", [])
    led_p = ROOT / "rgon_immune_ledger.json"; led = jload(led_p)
    led = led if isinstance(led, dict) else {}
    top_bump(led)
    led["antibody_count"] = 24
    k = next((k for k in ("antibodies", "rules", "immune_rules", "antibody_rules") if k in led), "antibodies")
    v = led.get(k)
    if isinstance(v, dict): v[NEW_AB] = R24_TEXT
    else:
        v = v if isinstance(v, list) else []
        if not any(NEW_AB in str(x)[:12] or (isinstance(x, dict) and x.get("id") == NEW_AB) for x in v):
            v.append({"id": NEW_AB, "name": "실전 트레이딩 3자 심판 & 주역 리스크 필터", "rule": R24_TEXT, "status": "활성"} if v and isinstance(v[0], dict) else R24_TEXT)
    led[k] = v; jsave(led_p, led); say("  ✓ rgon_immune_ledger.json → R24 등록")
    snap_p = ROOT / "rgon_brain_snapshot.json"; snap = jload(snap_p)
    snap = snap if isinstance(snap, dict) else {}
    top_bump(snap); snap["skills_count"] = n_skills; snap["trading_council"] = council.get("overall", {})
    jsave(snap_p, snap)
    for m in ("dashboard", "docs"):
        if (ROOT / m).is_dir(): shutil.copy2(snap_p, ROOT / m / snap_p.name)
    say("  ✓ rgon_brain_snapshot.json 3곳 동기화")
    blocks = {"CLAUDE.md": f"## 🐉 현재 버전: {VER} · 항체 {AB_RANGE}\n- {R24_TEXT}\n- 실전 트레이딩 판단 전 반드시 `rgon_trading_council.py --run` 결과를 확인한다(금고 DEFEND면 신규 진입 금지).",
              "CODE_MAP.md": f"## {VER} (Step 24)\n- `rgon_trading_council.py`: Bull/Bear/Judge 3자 심판 + 주역 64괘 필터 → `rgon_trading_council.json`, `--merge`로 brief 병합\n- `skills/{SKILL_ID}/SKILL.md`: {n_skills}번째 정식 스킬\n- `rgon_daily_cycle.py`: STEP24 훅(atexit)으로 순환 시 자동 실행",
              "MORNING_BRIEF.md": f"## ⚖️ 실전 트레이딩 3자 심판 ({VER} · {AB_RANGE})\n" + "\n".join(f"- {l}" for l in lines)}
    for name, blk in blocks.items():
        p = ROOT / name; t = rd(p) or f"# {name[:-3]}\n"
        t2 = OLDR.sub(AB_RANGE, OLDV.sub(VER, t))
        wr(p, upsert(t2, blk))
    lp = ROOT / "RGON_EVOLUTION_LOG.md"; t = rd(lp) or "# RGON EVOLUTION LOG\n"
    t = OLDR.sub(AB_RANGE, OLDV.sub(VER, t))
    if f"## {VER}" not in t:
        wr(lp, t.rstrip() + f"\n\n## {VER} — Step 24 ({datetime.now():%Y-%m-%d})\n- {R24_TEXT}\n- 안건 4종(#60 수택절·#01 중천건·#63 수화기제·#64 화수미제), 스킬 {n_skills}종, nutrient.trinity 7건 체계\n")
    else:
        wr(lp, t)
    say("  ✓ CLAUDE.md · CODE_MAP.md · MORNING_BRIEF.md · RGON_EVOLUTION_LOG.md 동기화")

def verify(counts):
    c = []
    for n in ("CLAUDE.md", "CODE_MAP.md", "MORNING_BRIEF.md", "RGON_EVOLUTION_LOG.md", "rgon_immune_ledger.json", "rgon_trading_council.json",
              "rgon_morning_brief.json", "rgon_brain_snapshot.json", "dashboard/rgon_brain_snapshot.json", "docs/rgon_brain_snapshot.json",
              "dashboard/rgon_morning_brief.json", "docs/rgon_morning_brief.json"):
        if "/" in n and not (ROOT / n).parent.is_dir(): continue
        c.append((f"{n} ⊃ {VER}", VER in rd(ROOT / n)))
    c.append((f"CLAUDE.md ⊃ {AB_RANGE}", AB_RANGE in rd(ROOT / "CLAUDE.md")))
    c.append(("ledger ⊃ R24", "R24" in rd(ROOT / "rgon_immune_ledger.json")))
    tri = (((jload(ROOT / "rgon_morning_brief.json") or {}).get("nutrient") or {}).get("trinity")) or []
    c.append((f"nutrient.trinity 트레이딩 4건 (총 {len(tri)}건)", sum(any(g in str(x) for g in GUAS) for x in tri) == 4))
    c.append((f"SKILL_INDEX 3곳 동일·{TARGET_SKILLS}개 이상 {counts}", len(set(counts.values())) == 1 and min(counts.values()) >= TARGET_SKILLS))
    return c

def notify(title, msg):
    try:
        if os.name == "nt": ctypes.windll.user32.MessageBoxW(0, msg, title, 0x40 | 0x1000)
    except Exception as e: print("[알림창 생략]", e)

def main():
    t0 = datetime.now(); say(f"🐉 RGON Step 24 — {VER} / {AB_RANGE} 시작 ({t0:%Y-%m-%d %H:%M:%S})")
    pre = hashes(); say(f"[三省 前] 보호 파일 {len(pre)}개 SHA-256 기록")
    wr(ROOT / "rgon_trading_council.py", MOD); ok_mod = compiles(ROOT / "rgon_trading_council.py")
    say(f"  {'✓' if ok_mod else '❌'} rgon_trading_council.py 생성")
    patch_backends_and_cycle()
    rc_st, out = run([sys.executable, "rgon_trading_council.py", "--self-test"], 180); say("  " + out)
    mid = hashes(); say(f"[三省 中] 보호 파일 변경 {len(diff(pre, mid))}건")
    if (ROOT / "rgon_daily_cycle.py").exists():
        rc_dc, out = run([sys.executable, "rgon_daily_cycle.py", "--run"], 900); say(f"  ↻ rgon_daily_cycle.py rc={rc_dc}")
    forge_skill()
    counts = register_skill()
    rc_run, out = run([sys.executable, "rgon_trading_council.py", "--run", "--merge"], 300); say(out)
    counts = register_skill()
    sync_versions(counts["skills"])
    comp_fail = [p.name for p in sorted(ROOT.glob("rgon_*.py")) if not compiles(p)]
    post = hashes(); changed = sorted(set(diff(pre, mid)) | set(diff(pre, post)))
    checks = verify(counts)
    s1, s2, s3 = rc_st == 0 and rc_run == 0 and ok_mod and not comp_fail, not changed and len(pre) == len(post), all(ok for _, ok in checks)
    say(f"[三省 ①] self-test·컴파일 {'PASS' if s1 else 'FAIL'} {comp_fail or ''}")
    say(f"[三省 ②] 보호 파일 {len(post)}개 · 변경 {len(changed)}건 → {'PASS' if s2 else 'FAIL ' + str(changed)}")
    say(f"[三省 ③] 버전·항체·스킬 동기화 {'PASS' if s3 else 'FAIL'}")
    for n, ok_c in checks:
        if not ok_c: say(f"  ⚠️ 미통과 항목: {n}")
    council = jload(ROOT / "rgon_trading_council.json") or {}
    rep = [f"# STEP24 TRADING COUNCIL REPORT — {VER} / {AB_RANGE}", f"- 실행: {t0:%Y-%m-%d %H:%M:%S} → {datetime.now():%H:%M:%S}",
           f"- 삼성 3/3: ① {'✅' if s1 else '❌'} ② {'✅' if s2 else '❌'} ③ {'✅' if s3 else '❌'}", f"- {R24_TEXT}",
           "\n## ⚖️ 실전 트레이딩 심판 결과", *[f"- {l}" for l in council.get("trinity_lines", [])],
           f"- 종합: {council.get('overall', {})}", "\n## 동기화 검증", *[f"- {'✅' if ok_c else '❌'} {n}" for n, ok_c in checks],
           f"\n## 보호 파일 SHA-256 ({len(post)}개, 변경 {len(changed)}건)", BT3, *[f"{h[:16]}  {k}" for k, h in sorted(post.items())][:200], BT3,
           "\n## 실행 로그", BT3, *LOG[-60:], BT3]
    wr(ROOT / "STEP24_TRADING_COUNCIL_REPORT.md", "\n".join(rep) + "\n")
    ok = s1 and s2 and s3; git_msg = "삼성 미통과로 커밋 보류 (목표 기반 원칙)"
    if ok and (ROOT / ".git").exists():
        run(["git", "add", "-A"])
        rc_c, oc = run(["git", "commit", "-m", f"Step24: {VER} — Bull/Bear/Judge 트레이딩 심판기 + 주역 64괘 필터 ({AB_RANGE}, {counts['skills']} skills)"])
        rc_p, op = run(["git", "push"], 240); git_msg = f"commit rc={rc_c} / push rc={rc_p} {op[-160:]}"
    elif ok: git_msg = "git 저장소 아님, 푸시 생략"
    say(f"[GIT] {git_msg}")
    tri = council.get("trinity_lines", [])
    notify(f"RGON Step 24 {'완료 ✅' if ok else '점검 필요 ⚠️'}",
           f"{VER} / {AB_RANGE}\n삼성 3/3: {'PASS' if s1 else 'FAIL'} · {'PASS' if s2 else 'FAIL'} · {'PASS' if s3 else 'FAIL'}\n"
           f"보호 파일 변경: {len(changed)}건 · 스킬: {counts['skills']}개\n\n" + "\n".join(l.split(' — ')[0] for l in tri) + f"\n\nGIT: {git_msg[:120]}")
    sys.exit(0 if ok else 1)

if __name__ == "__main__": main()

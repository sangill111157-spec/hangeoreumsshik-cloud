#!/usr/bin/env python3
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

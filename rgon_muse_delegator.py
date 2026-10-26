#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rgon_muse_delegator.py — RGON 제8기관: 자율 대행·위임 집행 기관 (Muse Delegation Engine)
v11.45-AON-AUTO-EVOLVER · R1~R46 · 정식 스킬 31개

주역 #14 화천대유(火天大有) ☲☰ : 크게 소유하고 만물을 막힘없이 대행한다 → Tier 1 AUTO / Tier 2 NOTIFY
주역 #64 화수미제(火水未濟) ☲☵ : 신중하게 분별하여 끝까지 완수한다   → Tier 3 HITL_GATE (대표님 결재)

사용법:
  python rgon_muse_delegator.py --self-test
  python rgon_muse_delegator.py --list
  python rgon_muse_delegator.py --add "작업 내용"
  python rgon_muse_delegator.py --approve T4
  python rgon_muse_delegator.py --hold T5
"""
import os, sys, json, re, time, hashlib, datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

VERSION = "v11.45-AON-AUTO-EVOLVER"
ANTIBODY = "R1~R46"
ORGAN = "제8기관: 자율 대행·위임 집행 기관 (Muse Delegation Engine)"
ROOT = Path(__file__).resolve().parent
TASK_FILE = ROOT / "rgon_muse_tasks.json"
DOCS_TASK_FILE = ROOT / "docs" / "rgon_muse_tasks.json"

ICHING = {
    "14": {"name": "화천대유(火天大有)", "symbol": "☲☰",
           "meaning": "크게 소유하고 만물을 막힘없이 대행함", "applies_to": "Tier 1 AUTO · Tier 2 NOTIFY"},
    "64": {"name": "화수미제(火水未濟)", "symbol": "☲☵",
           "meaning": "신중하게 분별하여 끝까지 완수함", "applies_to": "Tier 3 HITL_GATE"},
}
TIERS = {
    1: {"code": "AUTO", "label": "🟢 자동 집행", "final_status": "DONE"},
    2: {"code": "NOTIFY", "label": "🔵 선집행 후보고", "final_status": "DONE_NOTIFIED"},
    3: {"code": "HITL_GATE", "label": "🟡 대표님 결재 대기", "final_status": "PENDING_APPROVAL"},
}
VALID_STATUS = {"DONE", "DONE_NOTIFIED", "PENDING_APPROVAL", "APPROVED_DONE", "ON_HOLD"}
KW_TIER3 = ["매수", "매도", "리밸런싱", "비중", "자산", "배분", "주문", "결제", "송금", "이체", "계좌",
            "투자", "배포", "deploy", "설정 변경", "설정변경", "핵심 설정", "삭제", "권한", "결재",
            "승인", "push", "출금", "대출"]
KW_TIER2 = ["분석", "초안", "시뮬레이션", "심판", "합성", "리서치", "조사", "요약", "보고서", "트렌드",
            "비교", "검토", "예측", "평가", "설계"]
SEED_IDS = ["T1", "T2", "T3", "T4", "T5"]
SEED_TIERS = {"T1": 1, "T2": 1, "T3": 2, "T4": 3, "T5": 3}


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def classify(text):
    s = str(text or "").lower()
    for k in KW_TIER3:
        if k.lower() in s:
            return 3
    for k in KW_TIER2:
        if k.lower() in s:
            return 2
    return 1


def plan_for(title):
    return {
        "plan": [f"① 대상·범위 확정: {title}",
                 "② 현재 상태 스냅샷 저장 및 롤백 지점 확보",
                 "③ 드라이런(시뮬레이션)으로 영향도·리스크 계산",
                 "④ 대표님 [✅ 승인] 수신 시에만 실제 집행 (HITL 게이트)",
                 "⑤ 집행 후 결과 검증 및 아침 브리핑·독대실 보고"],
        "expected_effect": "대표님의 판단 시간을 절약하면서 중요 작업을 계획서 기반으로 안전하게 대행",
        "risk": "중요 변경 작업 — 대표님 승인 전 실제 집행 0건 (화수미제: 신중 분별)",
    }


def _task(tid, title, tier, ts=None, **extra):
    ts = ts or now()
    t = {"id": tid, "title": title, "tier": tier, "tier_code": TIERS[tier]["code"],
         "tier_label": TIERS[tier]["label"], "status": TIERS[tier]["final_status"],
         "iching": "#64 화수미제 — 신중히 분별하여 끝까지 완수" if tier == 3 else "#14 화천대유 — 막힘없이 대행",
         "created_at": ts, "source": "seed"}
    if tier in (1, 2):
        t["done_at"] = ts
    t.update(extra)
    return t


def seed_tasks():
    ts = now()
    return [
        _task("T1", "백혈구 6대 면역 순찰 및 32.5MB 정화 상태 유지 점검", 1, ts, category="immune-patrol",
              result="백혈구 6대 면역 순찰 대행 완료 · Step 31 정화 상태(구백업 29개·캐시 32.5MB 배출) 재축적 감시 등록"),
        _task("T2", "오감 센서 외부 GitHub 트렌드 & Stomper 해독 스캔", 1, ts, category="five-sense-radar",
              result="오감 레이더 외부 트렌드 스캔 대행 완료 · 신호는 Tier 2 스킬 초안 합성 후보로 이관"),
        _task("T3", "주역 #14 화천대유 기반 3자 찬반 심판(Bull/Bear/Judge) 포트폴리오 시뮬레이션", 2, ts,
              category="tri-judge-sim",
              report="3자 심판(Bull/Bear/Judge) 시뮬레이션 선집행 후 보고 — 실제 주문·자산 변경 0건(시뮬레이션 전용). "
                     "Judge GO 시그널은 T4 결재안으로 이관"),
        _task("T4", "[대표님 결재 대기] 금일 3자 심판 GO 시그널 종목 비중 확대 리밸런싱 대행안", 3, ts,
              category="asset-rebalance",
              plan=["① T3 3자 심판 GO 판정 종목 목록 확정",
                    "② 현재 비중 스냅샷 저장 및 롤백 지점 확보",
                    "③ 종목당 비중 상한·현금 비중 하한 등 리스크 한도 내 리밸런싱 드라이런",
                    "④ 대표님 [✅ 승인] 수신 시에만 리밸런싱 대행안 집행",
                    "⑤ 집행 결과를 아침 브리핑·독대실에 보고"],
              expected_effect="GO 시그널 종목 노출을 리스크 한도 내에서 정렬 (수익 보장 아님 · 최종 판단은 대표님)",
              risk="실전 자산 변동·시장 리스크 — 승인 전 집행 0건 (HITL 게이트 봉인)"),
        _task("T5", "[대표님 결재 대기] 차세대 자율 진화 스킬(SkillAutoForge) 클라우드 배포 승인안", 3, ts,
              category="skill-deploy",
              plan=["① SkillAutoForge 초안 스킬 목록·변경 범위 확정",
                    "② 백혈구 self-test 및 삼성(三省) 3/3 사전 검증",
                    "③ 배포 대상(GitHub Pages/클라우드) 드라이런 및 롤백 커밋 지정",
                    "④ 대표님 [✅ 승인] 수신 시에만 클라우드 배포 집행",
                    "⑤ 배포 후 스킬 수·항체·버전 동기화 재검증 보고"],
              expected_effect="자율 진화 스킬의 검증된 버전만 클라우드에 반영하여 진화 속도와 안전성을 동시 확보",
              risk="핵심 설정·배포 변경 — 승인 전 집행 0건 (화수미제: 끝까지 신중)"),
    ]


def digest(tasks):
    s = json.dumps(tasks, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def summarize(tasks):
    c = {"total": len(tasks), "tier1": 0, "tier2": 0, "tier3": 0, "pending_approval": 0,
         "approved_done": 0, "on_hold": 0, "done": 0, "done_notified": 0}
    for t in tasks:
        c["tier%d" % int(t.get("tier", 1))] = c.get("tier%d" % int(t.get("tier", 1)), 0) + 1
        st = t.get("status")
        key = {"PENDING_APPROVAL": "pending_approval", "APPROVED_DONE": "approved_done", "ON_HOLD": "on_hold",
               "DONE": "done", "DONE_NOTIFIED": "done_notified"}.get(st)
        if key:
            c[key] += 1
    return c


def build_doc(tasks):
    return {"organ": ORGAN, "version": VERSION, "antibody": ANTIBODY, "iching": ICHING,
            "tiers": {str(k): v for k, v in TIERS.items()}, "updated_at": now(),
            "summary": summarize(tasks), "tasks": tasks,
            "integrity": {"algo": "sha256", "tasks_sha256": digest(tasks)}}


def load_tasks():
    if TASK_FILE.exists():
        try:
            d = json.loads(TASK_FILE.read_text(encoding="utf-8"))
            if isinstance(d, dict) and isinstance(d.get("tasks"), list):
                return [t for t in d["tasks"] if isinstance(t, dict) and t.get("id")]
        except Exception:
            pass
    return []


def save_tasks(tasks):
    doc = build_doc(tasks)
    txt = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    for p in (TASK_FILE, DOCS_TASK_FILE):
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + ".tmp")
        tmp.write_text(txt, encoding="utf-8")
        os.replace(str(tmp), str(p))
    return doc


def ensure_seed():
    existing = load_tasks()
    by_id = {}
    for t in existing:
        by_id[t["id"]] = t
    out = []
    for s in seed_tasks():
        out.append(by_id.pop(s["id"], s))
    out.extend(by_id.values())
    return out


def next_id(tasks):
    n = 0
    for t in tasks:
        m = re.match(r"^T(\d+)$", str(t.get("id", "")))
        if m:
            n = max(n, int(m.group(1)))
    return "T%d" % (n + 1)


def add_task(tasks, title, source="cli"):
    tier = classify(title)
    t = _task(next_id(tasks), str(title).strip(), tier, source=source)
    if tier == 1:
        t["result"] = "Tier 1 AUTO — 아온이 즉시 자율 완수"
    elif tier == 2:
        t["report"] = "Tier 2 NOTIFY — 분석/초안 작업 선집행 완료, 요약 보고"
    else:
        t.update(plan_for(t["title"]))
    tasks.append(t)
    return t


def _find(tasks, tid):
    for t in tasks:
        if t.get("id") == tid:
            return t
    raise KeyError("작업 없음: %s" % tid)


def approve(tasks, tid):
    t = _find(tasks, tid)
    if int(t.get("tier", 0)) != 3:
        raise ValueError("Tier 3(HITL_GATE) 작업만 결재 대상입니다: %s" % tid)
    if t.get("status") not in ("PENDING_APPROVAL", "ON_HOLD"):
        raise ValueError("결재 가능한 상태가 아닙니다: %s (%s)" % (tid, t.get("status")))
    t["status"] = "APPROVED_DONE"
    t["approved_at"] = now()
    t["approved_by"] = "대표님"
    t["result"] = "대표님 승인 → 아온이 대행 집행 완료"
    return t


def hold(tasks, tid):
    t = _find(tasks, tid)
    if int(t.get("tier", 0)) != 3 or t.get("status") != "PENDING_APPROVAL":
        raise ValueError("보류 가능한 결재 대기 작업이 아닙니다: %s" % tid)
    t["status"] = "ON_HOLD"
    t["held_at"] = now()
    return t


def self_test():
    checks = []

    def ok(name, cond):
        checks.append(bool(cond))
        print(("  [PASS] " if cond else "  [FAIL] ") + name)

    print("🧪 %s self-test · %s · %s" % (ORGAN, VERSION, ANTIBODY))
    print("   ☲☰ #14 %s / ☲☵ #64 %s" % (ICHING["14"]["meaning"], ICHING["64"]["meaning"]))
    tasks = ensure_seed()
    doc = save_tasks(tasks)
    ids = [t.get("id") for t in tasks]
    ok("시드 대행 작업 5건 생성/보존 (T1~T5)", all(i in ids for i in SEED_IDS))
    ok("Tier 분류 일치 (T1,T2=1 · T3=2 · T4,T5=3)",
       all(int(_find(tasks, i).get("tier")) == SEED_TIERS[i] for i in SEED_IDS))
    ok("T1/T2 상태 DONE", all(_find(tasks, i).get("status") == "DONE" for i in ("T1", "T2")))
    ok("T3 상태 DONE_NOTIFIED", _find(tasks, "T3").get("status") == "DONE_NOTIFIED")
    ok("T4/T5 HITL 상태 유효 (PENDING_APPROVAL/APPROVED_DONE/ON_HOLD)",
       all(_find(tasks, i).get("status") in ("PENDING_APPROVAL", "APPROVED_DONE", "ON_HOLD") for i in ("T4", "T5")))
    ok("모든 상태값 유효", all(t.get("status") in VALID_STATUS for t in tasks))
    ok("Tier 3 결재안에 실행계획서·기대효과 존재",
       all(t.get("plan") and t.get("expected_effect") for t in tasks if int(t.get("tier", 0)) == 3))
    try:
        d1 = json.loads(TASK_FILE.read_text(encoding="utf-8"))
        d2 = json.loads(DOCS_TASK_FILE.read_text(encoding="utf-8"))
        ok("JSON 무결성 (sha256 일치)", d1["integrity"]["tasks_sha256"] == digest(d1["tasks"]))
        ok("docs/ 사본 동기화", d1["tasks"] == d2["tasks"])
        ok("버전·항체 표기", d1.get("version") == VERSION and d1.get("antibody") == ANTIBODY)
    except Exception as e:
        ok("JSON 로드 실패: %r" % (e,), False)
    samples = [("아침 브리핑 최신화해줘", 1), ("백혈구 순찰", 1), ("신규 트렌드 스킬 초안 합성", 2),
               ("자산 배분 리밸런싱 실행", 3), ("핵심 설정 변경", 3)]
    ok("키워드 Tier 자동 분류", all(classify(s) == e for s, e in samples))
    mem = json.loads(json.dumps(tasks, ensure_ascii=False))
    blocked = False
    try:
        approve(mem, "T1")
    except ValueError:
        blocked = True
    ok("HITL 게이트: Tier 1 결재 시도 차단", blocked)
    t = add_task(mem, "자산 배분 리밸런싱 실행", source="self-test")
    ok("신규 Tier 3 작업 → PENDING_APPROVAL", t["status"] == "PENDING_APPROVAL")
    approve(mem, t["id"])
    ok("승인 시 APPROVED_DONE 전이 (메모리 전용, 저장 안 함)", t["status"] == "APPROVED_DONE")
    passed = all(checks)
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    tasks = ensure_seed()
    if "--add" in argv:
        i = argv.index("--add")
        title = " ".join(argv[i + 1:]).strip()
        if not title:
            print("작업 내용을 입력하세요.")
            return 2
        t = add_task(tasks, title)
        save_tasks(tasks)
        print("📋 대행 등록: %s [%s] %s → %s" % (t["id"], t["tier_label"], t["title"], t["status"]))
        return 0
    for flag, fn in (("--approve", approve), ("--hold", hold)):
        if flag in argv:
            i = argv.index(flag)
            tid = argv[i + 1] if len(argv) > i + 1 else ""
            try:
                t = fn(tasks, tid)
            except (KeyError, ValueError) as e:
                print("⛔ %s" % e)
                return 1
            save_tasks(tasks)
            print("✅ %s → %s" % (t["id"], t["status"]))
            return 0
    save_tasks(tasks)
    print("📋 %s · %s" % (ORGAN, VERSION))
    for t in tasks:
        print("  %-4s %-14s %-17s %s" % (t["id"], t.get("tier_label", ""), t.get("status", ""), t.get("title", "")))
    s = summarize(tasks)
    print("  → 결재 대기 %d건 · 승인 집행 %d건 · 보류 %d건" % (s["pending_approval"], s["approved_done"], s["on_hold"]))
    return 0


# [RGON-R35-GATE-INJECT] — Tier 3 승인 집행 전 중요 결재 수동 ON/OFF 스위치 확인 (제11기관 · Step 35)
import os as _r35os, sys as _r35sys
_r35d = _r35os.path.dirname(_r35os.path.abspath(__file__))
if _r35d not in _r35sys.path: _r35sys.path.insert(0, _r35d)
try:
    import rgon_laptop_hands as _r35h
except Exception:
    _r35h = None
_R35_KEYS = ("title", "text", "task", "desc", "description", "name")

def _r35_find(args, kwargs):
    vals = list(args) + list(kwargs.values())
    for v in vals:
        if isinstance(v, dict) and any(k in v for k in ("tier",) + _R35_KEYS): return v
    g = globals()
    for v in vals:
        if not isinstance(v, (str, int)): continue
        for fn in ("get_task", "find_task"):
            f = g.get(fn)
            if callable(f):
                try:
                    t = f(v)
                    if isinstance(t, dict): return t
                except Exception:
                    pass
        for nm in ("TASKS", "tasks", "QUEUE", "queue", "_TASKS", "_tasks", "TASK_QUEUE"):
            L = g.get(nm)
            if isinstance(L, dict) and isinstance(L.get(v), dict): return L[v]
            if isinstance(L, list):
                for t in L:
                    if isinstance(t, dict) and v in (t.get("id"), t.get("task_id")): return t
    return None

def _r35_wrap(fn):
    if getattr(fn, "_r35", False): return fn
    def wrapped(*a, **k):
        t = _r35_find(a, k)
        text = " ".join(str(t.get(x, "")) for x in _R35_KEYS) if t else " ".join(x for x in a if isinstance(x, str))
        tier = t.get("tier") if t else None
        cats = _r35h.critical_categories(text) if _r35h else []
        if str(tier) == "3" or (tier is None and cats):
            if _r35h is None:
                return {"ok": False, "allowed": False, "executed": 0, "gate": "R35",
                        "message": "🔒 제11기관(rgon_laptop_hands) 로드 실패 — 중요 결재 집행을 차단했습니다."}
            g = _r35h.can_execute_critical(_r35h.critical_category(text), tier=3)
            if not g["allowed"]:
                return {"ok": False, "allowed": False, "executed": 0, "gate": "R35", "message": g["message"]}
        return fn(*a, **k)
    wrapped._r35 = True
    wrapped.__name__ = getattr(fn, "__name__", "wrapped"); wrapped.__doc__ = getattr(fn, "__doc__", None)
    return wrapped

for _r35n in ("approve", "approve_task", "execute_task", "execute_approved"):
    if callable(globals().get(_r35n)): globals()[_r35n] = _r35_wrap(globals()[_r35n])

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

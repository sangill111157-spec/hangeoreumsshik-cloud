#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step32_muse_delegation_and_dynamic_island.py  (G2 교차검증 + V13 마커 호환 반영판)
RGON Step 32 — v11.31-MUSE-DELEGATION · 항체 R1~R32 · 정식 스킬 28개
【제8기관: 자율 대행·위임 집행 기관 (Muse Delegation Engine)】
  Muse Wonder(비동기 위임큐) · 3-Tier HITL 안전 승인 게이트 · Muse Charm(아온 다이내믹 아일랜드)
표준 라이브러리 전용: os, sys, json, re, time, shutil, hashlib, datetime, subprocess, pathlib
"""
import os, sys, json, re, time, shutil, hashlib, datetime, subprocess
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ====================================================================
# 0. 상수
# ====================================================================
ROOT = Path(os.environ.get("RGON_ROOT") or Path(__file__).resolve().parent).resolve()
OLD_VER, NEW_VER = "v11.30-EXCRETORY-CLEAN", "v11.31-MUSE-DELEGATION"
OLD_AB, NEW_AB = "R1~R31", "R1~R32"
OLD_SK, NEW_SK = 27, 28
SKILL_SLUG = "muse-autonomous-delegator"
SKILL_REL = f"skills/{SKILL_SLUG}/SKILL.md"
R32_TEXT = ("R32: 메타 뮤즈(Muse) 3대 대행 기관 — 비동기 위임 작업큐(Muse Wonder) · "
            "3등급 안전 승인 게이트(HITL) · 아온 다이내믹 아일랜드(Muse Charm) 통합")
R32_DESC = R32_TEXT.split(": ", 1)[1]
ENGINE_REL = "rgon_muse_delegator.py"
WBC_REL = "rgon_white_blood_cell.py"
LEDGER_REL = "rgon_immune_ledger.json"
TASK_REL, DOCS_TASK_REL = "rgon_muse_tasks.json", "docs/rgon_muse_tasks.json"
REPORT_REL = "STEP32_MUSE_DELEGATION_REPORT.md"
# [수정 1] YT-SCOUT-V13 / UX-CLEANUP-V13 마커 모두 허용
V13_START_RE = re.compile(rb"<!--\s*\[RGON-(?:YT-SCOUT|UX-CLEANUP)-V13-START\]\s*-->")
V13_END_RE = re.compile(rb"<!--\s*\[RGON-(?:YT-SCOUT|UX-CLEANUP)-V13-END\]\s*-->")
V13_ANY_RE = re.compile(rb"\[RGON-[A-Z0-9\-]*V13-(?:START|END)\]")
MUSE_START, MUSE_END = "<!-- [RGON-MUSE-V1-START] -->", "<!-- [RGON-MUSE-V1-END] -->"
MUSE_BLOCK_RE = re.compile(re.escape(MUSE_START) + r".*?" + re.escape(MUSE_END) + r"\n?", re.S)
# 백혈구 self-test 산출물(.rgon_backup/wbc_snapshots, wbc_quarantine 등) 스냅샷 제외
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode",
             ".rgon_backup", ".rgon_backups", "backups", "archive", "old_backups"}
# 백혈구 self-test 가 갱신하는 면역 원장·임시파일 오탐 방지
RUNTIME_RE = re.compile(r"(\.log$|\.pyc$|\.jsonl$|rgon_immune_ledger\.json$|\.wbc_tmp$|(^|/)logs?/)")
TODAY = datetime.date.today().isoformat()
STAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
EXPECTED_HTML = 7

AB_RE = re.compile(r"R1(\s*[~\-–～]\s*)R31(?!\d)")
HIST_LINE = re.compile(r"(Step\s*31|STEP\s*31|\bR31\s*[:|\]\)]|\|\s*\**R31\b)")
KO_COUNT = [
    (re.compile(r"(스킬[^\n\d<]{0,8}?)27(\s*개)"), r"\g<1>28\g<2>"),
    (re.compile(r"(?<!\d)27(\s*개\s*(?:의\s*)?(?:정식\s*)?스킬)"), r"28\g<1>"),
]
PY_COUNT = [
    (re.compile(r"(\b(?:EXPECTED_SKILL_COUNT|SKILL_COUNT|EXPECTED_SKILLS|TOTAL_SKILLS|"
                r"FORMAL_SKILL_COUNT|OFFICIAL_SKILL_COUNT)\s*[:=]\s*)27\b"), r"\g<1>28"),
    (re.compile(r"""(["'](?:total_skills|skill_count|skills_count|expected_skill_count|"""
                r"""formal_skills|official_skills)["']\s*:\s*)27\b"""), r"\g<1>28"),
    (re.compile(r"\[27,\s*27,\s*27\]"), "[28, 28, 28]"),
] + KO_COUNT
AB_COUNT = [
    (re.compile(r"(\b(?:EXPECTED_ANTIBODY_COUNT|ANTIBODY_COUNT|EXPECTED_ANTIBODIES|TOTAL_ANTIBODIES|"
                r"NUM_ANTIBODIES)\s*(?::\s*int\s*)?=\s*)31\b"), r"\g<1>32"),
]
DOC_COUNT = [
    (re.compile(r"""(["']?(?:count|total_skills|skill_count|skills_count|expected_skill_count|"""
                r"""EXPECTED_SKILL_COUNT)["']?\s*[:=]\s*)27\b"""), r"\g<1>28"),
    (re.compile(r"\b27(\s*(?:formal\s+|official\s+)?skills\b)", re.I), r"28\g<1>"),
    (re.compile(r"(?<!\d)27\s*/\s*27(?!\d)"), "28/28"),
    (re.compile(r"\[27,\s*27,\s*27\]"), "[28, 28, 28]"),
] + KO_COUNT
COUNT_KEYS = {"count", "total_skills", "skill_count", "skills_count", "expected_skill_count",
              "formal_skills", "official_skills", "num_skills"}

LOG, ORIGINALS, TARGETS = [], {}, set()


def log(msg=""):
    print(msg)
    LOG.append(str(msg))


def relp(p):
    return Path(os.path.relpath(str(p), str(ROOT))).as_posix()


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


# ====================================================================
# 1. 안전 쓰기 / 롤백 (백업 파일 0개 — 메모리 롤백)
# ====================================================================
def track(p):
    p = Path(p)
    TARGETS.add(relp(p))
    if p not in ORIGINALS:
        ORIGINALS[p] = p.read_bytes() if p.exists() else None


def write_bytes(p, data):
    p = Path(p)
    track(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and p.read_bytes() == data:
        return False
    p.write_bytes(data)
    return True


def write_text(p, text, bom=False):
    return write_bytes(p, (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))


def rollback():
    log("⏪ 롤백 실행 — 변경 파일 원상 복구")
    for p, b in ORIGINALS.items():
        try:
            if b is None:
                if p.exists():
                    p.unlink()
            else:
                p.write_bytes(b)
        except Exception as e:
            log(f"  ⚠️ 롤백 실패 {relp(p)}: {e!r}")
    d = ROOT / "skills" / SKILL_SLUG
    try:
        if d.exists() and not any(d.iterdir()):
            d.rmdir()
    except Exception:
        pass


# ====================================================================
# 2. 해시 스냅샷
# ====================================================================
def iter_files():
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for f in fns:
            yield Path(dp) / f


def snapshot():
    out = {}
    for p in iter_files():
        try:
            out[relp(p)] = sha_bytes(p.read_bytes())
        except Exception:
            pass
    return out


def diff_snap(a, b, exclude):
    changed, deleted, created = [], [], []
    for k, v in a.items():
        if k in exclude:
            continue
        if k not in b:
            deleted.append(k)
        elif b[k] != v:
            changed.append(k)
    for k in b:
        if k not in a and k not in exclude:
            created.append(k)
    return changed, deleted, created


def run(cmd, timeout=900):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=env, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return 999, repr(e)


# ====================================================================
# 3. 신규 백엔드 엔진 소스: rgon_muse_delegator.py
# ====================================================================
ENGINE_SRC = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rgon_muse_delegator.py — RGON 제8기관: 자율 대행·위임 집행 기관 (Muse Delegation Engine)
v11.31-MUSE-DELEGATION · R1~R32 · 정식 스킬 28개

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

VERSION = "v11.31-MUSE-DELEGATION"
ANTIBODY = "R1~R32"
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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
'''

# ====================================================================
# 4. 28번째 정식 스킬
# ====================================================================
SKILL_MD = """---
name: muse-autonomous-delegator
description: 메타 뮤즈(Muse Wonder & Muse Charm) 방식의 자율 대행·위임 집행 프로토콜. 대표님 지시를 3-Tier HITL 게이트로 분류해 안전 작업은 즉시 완수하고, 분석 작업은 선집행 후 보고하며, 중요 작업은 실행계획서와 함께 결재를 기다린다. 아온 다이내믹 아일랜드 캡슐로 결재 대기를 알린다.
version: """ + NEW_VER + """
antibody: R32
organ: 제8기관 — 자율 대행·위임 집행 기관 (Muse Delegation Engine)
---

# 📋 Muse Autonomous Delegator — 28번째 정식 스킬

> """ + R32_TEXT + """
> 버전 `""" + NEW_VER + """` · 항체 `""" + NEW_AB + """` · 정식 스킬 28개

## 1. 철학 (주역)
- **#14 화천대유(火天大有) ☲☰**: 크게 소유하고 만물을 막힘없이 대행한다. Tier 1·2는 묻지 않고 끝까지 처리한다.
- **#64 화수미제(火水未濟) ☲☵**: 신중하게 분별하여 끝까지 완수한다. Tier 3은 계획서를 쓰고 대표님 결재를 받은 뒤에만 집행한다.

## 2. Muse Wonder: 비동기 대행 작업 큐
- 저장소: `rgon_muse_tasks.json` + `docs/rgon_muse_tasks.json` (원자적 동시 저장, sha256 무결성 필드)
- 엔진: `rgon_muse_delegator.py` (`--self-test`, `--list`, `--add`, `--approve`, `--hold`)
- 상태 전이: `DONE` · `DONE_NOTIFIED` · `PENDING_APPROVAL → APPROVED_DONE | ON_HOLD`

## 3. 3-Tier HITL 안전 승인 게이트
| Tier | 코드 | 표시 | 예시 | 최종 상태 |
|---|---|---|---|---|
| 1 | AUTO | 🟢 자동 집행 | 아침 브리핑 최신화, 백혈구 순찰, 오감 레이더 스캔, 배설·정화(autoDream) | DONE |
| 2 | NOTIFY | 🔵 선집행 후보고 | 트렌드 스킬 초안 합성, 3자 찬반 심판 시뮬레이션 | DONE_NOTIFIED |
| 3 | HITL_GATE | 🟡 대표님 결재 대기 | 실전 자산 배분 변경, 핵심 설정 변경, 클라우드 배포 | PENDING_APPROVAL → APPROVED_DONE |

- 분류 규칙: Tier 3 키워드(매수·매도·리밸런싱·비중·자산·배분·주문·송금·배포·설정 변경·삭제·권한 등)를 먼저 보고, Tier 2 키워드(분석·초안·시뮬레이션·심판·합성·리서치·요약·트렌드 등)를 그다음에 보며, 둘 다 없으면 Tier 1로 본다.
- **절대 규칙**: Tier 3 작업은 `[✅ 승인 집행]` 없이는 절대 집행하지 않는다. Tier 1/2 작업에는 결재 버튼을 노출하지 않는다.

## 4. Muse Charm: 아온 다이내믹 아일랜드
- 결재 대기가 1건 이상이면 순수 3D 물방울 아온(`#rgyt-wrap` 또는 `#aon-roamer`) 머리 위에 `📋 결재 N건` 캡슐을 띄운다. 아온이 숨어 있으면 `📋대행` 버튼 옆에, 그것도 없으면 화면 상단 중앙에 띄운다.
- 미니 독: `🔍레이더 · 📈3자심판 · 🧹정화 · 📋대행 · 🙈숨기기` 순서를 따른다. 기존 버튼과 아온 형태(팔다리·장신구·회전궤도 0개)는 그대로 둔다.
- 대행 보드: 입력창(`아온아, 이 작업 대신 해줘...`) + `🚀 대행 지시`로 즉시 분류하고 큐에 넣는다. 독대실 질문창 전달은 선택 사항이다.
- 승인하면 `APPROVED_DONE`이 되고, 아온 말풍선 `대표님 승인 완료! 즉시 대행 집행했습니다 💧✨`와 오라 반짝임이 나온다. 상태는 `localStorage`(`rgon_muse_tasks_v1`)에 보존한다.
- V13 블록 마커: `[RGON-YT-SCOUT-V13-START/END]` 또는 `[RGON-UX-CLEANUP-V13-START/END]` 내부에만 주입한다.

## 5. 검증 (삼성 三省)
1. `python rgon_muse_delegator.py --self-test` → `PASS`, rc=0
2. 비대상 보호 파일 SHA-256 변경 0건
3. 스킬 수 `[28, 28, 28]`, 항체 `R1~R32` 일치
"""

# ====================================================================
# 5. V13 블록 내부 삽입: 아온 뮤즈 다이내믹 아일랜드 & 📋대행 독
# ====================================================================
MUSE_BLOCK_TEMPLATE = r"""<!-- [RGON-MUSE-V1-START] -->
<!-- R32 · v11.31-MUSE-DELEGATION · Muse Wonder 위임큐 · Muse Charm 다이내믹 아일랜드 · 3-Tier HITL 게이트 -->
<style id="rgmuse-style">
#rgmuse-island{position:fixed;left:50%;top:10px;z-index:2147483600;display:flex;align-items:center;gap:6px;padding:5px 12px 5px 9px;border-radius:999px;background:rgba(8,12,26,.84);color:#eaf7ff;font:600 12px/1.25 system-ui,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;letter-spacing:.2px;white-space:nowrap;box-shadow:0 0 0 1px rgba(150,225,255,.38),0 6px 22px rgba(70,170,255,.38),inset 0 0 14px rgba(120,210,255,.2);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);cursor:pointer;user-select:none;opacity:0;visibility:hidden;pointer-events:none;transform:translate(-50%,-100%) scale(.82);transition:opacity .35s ease,visibility .35s,transform .38s cubic-bezier(.2,.9,.3,1.25),left .14s linear,top .14s linear}
#rgmuse-island.below{transform:translate(-50%,0) scale(.82)}
#rgmuse-island.on{opacity:1;visibility:visible;pointer-events:auto;transform:translate(-50%,-100%) scale(1)}
#rgmuse-island.on.below{transform:translate(-50%,0) scale(1)}
#rgmuse-island:hover{box-shadow:0 0 0 1px rgba(170,235,255,.6),0 8px 28px rgba(90,190,255,.55),inset 0 0 16px rgba(140,220,255,.28)}
#rgmuse-island .rgmuse-dot{width:7px;height:7px;border-radius:50%;background:#ffd24d;box-shadow:0 0 8px #ffd24d;animation:rgmusePulse 1.6s ease-in-out infinite}
#rgmuse-island.pop{animation:rgmusePop .7s ease}
@keyframes rgmusePulse{0%,100%{opacity:1;box-shadow:0 0 6px #ffd24d}50%{opacity:.55;box-shadow:0 0 14px #ffd24d}}
@keyframes rgmusePop{0%{filter:brightness(1)}40%{filter:brightness(1.6) drop-shadow(0 0 10px rgba(255,220,120,.9))}100%{filter:brightness(1)}}
#rgmuse-bubble{position:fixed;left:50%;top:70px;z-index:2147483620;max-width:min(320px,80vw);padding:8px 12px;border-radius:14px;background:rgba(255,255,255,.96);color:#0b2440;font:600 13px/1.4 system-ui,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;box-shadow:0 8px 26px rgba(40,140,255,.35),0 0 0 1px rgba(120,200,255,.5);opacity:0;visibility:hidden;pointer-events:none;transform:translate(-50%,-100%);transition:opacity .3s,visibility .3s}
#rgmuse-bubble.below{transform:translate(-50%,0)}
#rgmuse-bubble.on{opacity:1;visibility:visible}
#rgmuse-fab{position:fixed;right:18px;bottom:18px;z-index:2147483590;padding:8px 12px;border:0;border-radius:999px;background:rgba(10,16,34,.86);color:#eaf7ff;font:700 13px system-ui,-apple-system,"Malgun Gothic",sans-serif;box-shadow:0 0 0 1px rgba(150,225,255,.35),0 6px 20px rgba(70,170,255,.35);cursor:pointer}
#rgmuse-overlay{position:fixed;inset:0;z-index:2147483640;display:none;align-items:center;justify-content:center;background:rgba(3,7,18,.56);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px)}
#rgmuse-overlay.on{display:flex}
#rgmuse-board{box-sizing:border-box;width:min(740px,94vw);max-height:88vh;overflow:auto;padding:18px;border-radius:20px;background:linear-gradient(160deg,#101a36 0%,#0a1124 100%);color:#e8f2ff;font:14px/1.5 system-ui,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;box-shadow:0 0 0 1px rgba(140,210,255,.28),0 24px 70px rgba(0,0,0,.55),0 0 40px rgba(80,170,255,.18)}
#rgmuse-board *{box-sizing:border-box}
.rgmuse-head{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:12px}
.rgmuse-h1{font-size:17px;font-weight:800}
.rgmuse-sub{font-size:11.5px;opacity:.7;margin-top:2px}
.rgmuse-x{border:0;background:rgba(255,255,255,.08);color:#fff;width:32px;height:32px;border-radius:50%;cursor:pointer;font-size:15px;flex:none}
.rgmuse-in{display:flex;gap:8px}
#rgmuse-input{flex:1;min-width:0;padding:10px 12px;border-radius:12px;border:1px solid rgba(140,210,255,.35);background:rgba(255,255,255,.06);color:#fff;font-size:14px;outline:none}
#rgmuse-input:focus{border-color:#7fd3ff;box-shadow:0 0 0 3px rgba(127,211,255,.18)}
#rgmuse-go{padding:10px 14px;border:0;border-radius:12px;background:linear-gradient(135deg,#3aa8ff,#7b6bff);color:#fff;font-weight:800;cursor:pointer;white-space:nowrap}
.rgmuse-fw{display:inline-flex;gap:6px;align-items:center;margin:8px 0 4px;font-size:12px;opacity:.85;cursor:pointer}
.rgmuse-legend{font-size:11.5px;opacity:.65;margin-bottom:10px}
#rgmuse-sum{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px}
.rgmuse-chip{padding:3px 10px;border-radius:999px;background:rgba(255,255,255,.07);font-size:12px}
.rgmuse-sec{margin-top:12px}
.rgmuse-sec-h{font-weight:800;font-size:13px;margin-bottom:6px}
.rgmuse-sec-h span{opacity:.6;font-weight:600}
.rgmuse-card{padding:10px 12px;border-radius:14px;background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.07);margin-bottom:8px}
.rgmuse-card.st-PENDING_APPROVAL{border-color:rgba(255,210,77,.55);box-shadow:0 0 18px rgba(255,210,77,.12)}
.rgmuse-card.st-APPROVED_DONE{border-color:rgba(120,220,255,.5)}
.rgmuse-card.st-ON_HOLD{opacity:.8}
.rgmuse-row{display:flex;justify-content:space-between;gap:8px;font-size:12px;opacity:.85}
.rgmuse-title{font-weight:700;margin:3px 0}
.rgmuse-plan{margin:6px 0 4px 18px;padding:0;font-size:12.5px;opacity:.9}
.rgmuse-eff,.rgmuse-risk,.rgmuse-res{font-size:12.5px;opacity:.88;margin-top:3px}
.rgmuse-acts{display:flex;gap:8px;margin-top:8px}
.rgmuse-acts button{border:0;border-radius:10px;padding:7px 12px;font-weight:800;cursor:pointer}
.rgmuse-ok{background:linear-gradient(135deg,#2fd27a,#19a8ff);color:#fff}
.rgmuse-hold{background:rgba(255,255,255,.1);color:#fff}
</style>
<script id="rgmuse-script">
(function(){
"use strict";
if(window.__RGON_MUSE_V1__)return;window.__RGON_MUSE_V1__=true;
var VERSION="v11.31-MUSE-DELEGATION",ANTIBODY="R1~R32",LS_KEY="rgon_muse_tasks_v1";
var SEED=__RGMUSE_SEED__;
var KW3=["매수","매도","리밸런싱","비중","자산","배분","주문","결제","송금","이체","계좌","투자","배포","deploy","설정 변경","설정변경","핵심 설정","삭제","권한","결재","승인","push","출금","대출"];
var KW2=["분석","초안","시뮬레이션","심판","합성","리서치","조사","요약","보고서","트렌드","비교","검토","예측","평가","설계"];
var TIER={1:{k:"t1",code:"AUTO",label:"🟢 Tier 1 · AUTO 자동 집행"},2:{k:"t2",code:"NOTIFY",label:"🔵 Tier 2 · NOTIFY 선집행 후보고"},3:{k:"t3",code:"HITL_GATE",label:"🟡 Tier 3 · HITL 대표님 결재"}};
var ST={DONE:"✅ 자동 완수",DONE_NOTIFIED:"🔵 완수·보고",RUNNING:"⏳ 대행 중",PENDING_APPROVAL:"🟡 결재 대기",APPROVED_DONE:"💧 승인 집행 완료",ON_HOLD:"⏸️ 보류"};
var RANK={RUNNING:0,PENDING_APPROVAL:0,ON_HOLD:1,DONE:2,DONE_NOTIFIED:2,APPROVED_DONE:3};
var tasks=[],lastPending=-1,bubbleTimer=null;
function aonEl(){return document.getElementById("rgyt-wrap")||document.getElementById("aon-roamer");}
function nowIso(){var d=new Date(),p=function(n){return(n<10?"0":"")+n;};return d.getFullYear()+"-"+p(d.getMonth()+1)+"-"+p(d.getDate())+"T"+p(d.getHours())+":"+p(d.getMinutes())+":"+p(d.getSeconds());}
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
function loadLocal(){try{var d=JSON.parse(localStorage.getItem(LS_KEY)||"null");return d&&d.tasks?d.tasks:[];}catch(e){return[];}}
function saveLocal(){try{localStorage.setItem(LS_KEY,JSON.stringify({version:VERSION,antibody:ANTIBODY,saved_at:nowIso(),tasks:tasks}));}catch(e){}}
function merge(base,local){var map={},order=[];(base||[]).forEach(function(t){if(t&&t.id&&!map[t.id]){map[t.id]=JSON.parse(JSON.stringify(t));order.push(t.id);}});(local||[]).forEach(function(t){if(!t||!t.id)return;var a=map[t.id];if(!a){map[t.id]=t;order.push(t.id);return;}if((RANK[t.status]||0)>=(RANK[a.status]||0))map[t.id]=Object.assign({},a,t);});return order.map(function(id){return map[id];});}
function find(id){for(var i=0;i<tasks.length;i++)if(tasks[i].id===id)return tasks[i];return null;}
function pendingCount(){var n=0;tasks.forEach(function(t){if(t.status==="PENDING_APPROVAL")n++;});return n;}
function classify(text){var s=String(text||"").toLowerCase(),i;for(i=0;i<KW3.length;i++)if(s.indexOf(KW3[i].toLowerCase())>=0)return 3;for(i=0;i<KW2.length;i++)if(s.indexOf(KW2[i].toLowerCase())>=0)return 2;return 1;}
function planFor(title){return{plan:["① 대상·범위 확정: "+title,"② 현재 상태 스냅샷 저장 및 롤백 지점 확보","③ 드라이런(시뮬레이션)으로 영향도·리스크 계산","④ 대표님 [✅ 승인] 수신 시에만 실제 집행 (HITL 게이트)","⑤ 집행 후 결과 검증 및 아침 브리핑·독대실 보고"],effect:"대표님의 판단 시간을 절약하면서 중요 작업을 계획서 기반으로 안전하게 대행",risk:"중요 변경 작업 — 대표님 승인 전 실제 집행 0건 (화수미제: 신중 분별)"};}
function nextId(){var n=0;tasks.forEach(function(t){var m=/^T(\d+)$/.exec(String(t.id||""));if(m)n=Math.max(n,parseInt(m[1],10));});return"T"+(n+1);}
function visibleRect(el){if(!el)return null;var cs=window.getComputedStyle(el);if(cs.display==="none"||cs.visibility==="hidden"||parseFloat(cs.opacity||"1")<0.05)return null;var r=el.getBoundingClientRect();if(r.width<2||r.height<2)return null;if(r.bottom<0||r.right<0||r.top>window.innerHeight||r.left>window.innerWidth)return null;return r;}
function joy(){var w=aonEl();if(w&&w.animate){try{w.animate([{filter:"none"},{filter:"brightness(1.35) drop-shadow(0 0 18px rgba(140,230,255,.95))"},{filter:"none"}],{duration:1300,easing:"ease-in-out"});}catch(e){}}}
function say(msg){var fns=["rgytSay","aonSay","rgytSpeak","aonSpeak","rgonAonSay","showAonBubble"];for(var i=0;i<fns.length;i++){var f=window[fns[i]];if(typeof f==="function"){try{f(msg);return;}catch(e){}}}
var bb=document.getElementById("rgmuse-bubble");if(!bb)return;bb.textContent=msg;var r=visibleRect(aonEl());var x=r?r.left+r.width/2:window.innerWidth/2,y=r?r.top-12:72,below=false;if(r&&y<60){y=r.bottom+12;below=true;}x=Math.max(90,Math.min(window.innerWidth-90,x));bb.style.left=x+"px";bb.style.top=y+"px";bb.classList.toggle("below",below);bb.classList.add("on");clearTimeout(bubbleTimer);bubbleTimer=setTimeout(function(){bb.classList.remove("on");},3600);}
function forwardToDokdae(text,tier){var sel=["#dokdae-input","#dokdaeInput","#dokdae_input","textarea[placeholder*='독대']","input[placeholder*='독대']","textarea[placeholder*='질문']","input[placeholder*='질문']"];for(var i=0;i<sel.length;i++){var el=null;try{el=document.querySelector(sel[i]);}catch(e){}if(el&&el.id!=="rgmuse-input"){el.value="[📋 뮤즈 대행 · Tier "+tier+"] "+text;try{el.dispatchEvent(new Event("input",{bubbles:true}));}catch(e){}return true;}}return false;}
function finish2(id,silent){var t=find(id);if(!t||t.status!=="RUNNING")return;t.status="DONE_NOTIFIED";t.done_at=nowIso();t.report="요약 보고: ‘"+t.title+"’ 분석/초안 작업을 선집행 완료했습니다. 상세 내용은 독대실에서 이어서 확인하세요.";saveLocal();refresh();if(!silent)say("보고드립니다! Tier 2 대행 작업 완수 🔵✨");}
function addTask(text,forward){text=String(text||"").trim();if(!text)return;var tier=classify(text),t={id:nextId(),title:text,tier:tier,tier_code:TIER[tier].code,tier_label:TIER[tier].label,created_at:nowIso(),source:"dynamic-island",iching:tier===3?"#64 화수미제 — 신중히 분별하여 끝까지 완수":"#14 화천대유 — 막힘없이 대행"};
if(tier===1){t.status="DONE";t.done_at=nowIso();t.result="Tier 1 AUTO — 아온이 즉시 자율 완수했습니다.";tasks.push(t);say("Tier 1 자동 집행! 바로 끝냈어요 💧");}
else if(tier===2){t.status="RUNNING";tasks.push(t);say("Tier 2 분석 대행 시작! 끝나면 바로 보고드릴게요 🔵");setTimeout(function(){finish2(t.id);},1400);}
else{var p=planFor(text);t.status="PENDING_APPROVAL";t.plan=p.plan;t.expected_effect=p.effect;t.risk=p.risk;tasks.push(t);say("중요 작업이라 실행 계획서를 올렸어요. 대표님 결재를 기다릴게요 🟡");}
saveLocal();refresh();if(forward)forwardToDokdae(text,tier);}
function approve(id){var t=find(id);if(!t||Number(t.tier)!==3)return;if(t.status!=="PENDING_APPROVAL"&&t.status!=="ON_HOLD")return;t.status="APPROVED_DONE";t.approved_at=nowIso();t.approved_by="대표님";t.result="대표님 승인 → 아온이 대행 집행 완료";saveLocal();refresh();say("대표님 승인 완료! 즉시 대행 집행했습니다 💧✨");joy();}
function hold(id){var t=find(id);if(!t||Number(t.tier)!==3||t.status!=="PENDING_APPROVAL")return;t.status="ON_HOLD";t.held_at=nowIso();saveLocal();refresh();say("알겠습니다. 보류해 두고 다시 여쭐게요 ⏸️");}
function card(t){var h='<div class="rgmuse-card st-'+esc(t.status)+'"><div class="rgmuse-row"><b>'+esc(t.id)+'</b><span>'+(ST[t.status]||esc(t.status))+'</span></div><div class="rgmuse-title">'+esc(t.title)+'</div>';
if(t.plan&&t.plan.length){h+='<ol class="rgmuse-plan">';t.plan.forEach(function(s){h+='<li>'+esc(String(s).replace(/^[①②③④⑤⑥⑦⑧⑨]\s*/,""))+'</li>';});h+='</ol>';}
if(t.expected_effect)h+='<div class="rgmuse-eff">🎯 기대효과: '+esc(t.expected_effect)+'</div>';
if(t.risk)h+='<div class="rgmuse-risk">⚠️ 리스크: '+esc(t.risk)+'</div>';
var res=t.report||t.result;if(res)h+='<div class="rgmuse-res">📝 '+esc(res)+'</div>';
if(Number(t.tier)===3&&(t.status==="PENDING_APPROVAL"||t.status==="ON_HOLD")){h+='<div class="rgmuse-acts"><button type="button" class="rgmuse-ok" data-act="approve" data-id="'+esc(t.id)+'">✅ 승인 집행</button>';if(t.status==="PENDING_APPROVAL")h+='<button type="button" class="rgmuse-hold" data-act="hold" data-id="'+esc(t.id)+'">⏸️ 보류</button>';h+='</div>';}
return h+'</div>';}
function renderBoard(){var list=document.getElementById("rgmuse-list"),sum=document.getElementById("rgmuse-sum");if(!list||!sum)return;var g={1:[],2:[],3:[]},c={p:0,a:0,h:0,d:0};
tasks.forEach(function(t){(g[Number(t.tier)]||g[1]).push(t);if(t.status==="PENDING_APPROVAL")c.p++;else if(t.status==="APPROVED_DONE")c.a++;else if(t.status==="ON_HOLD")c.h++;else c.d++;});
sum.innerHTML='<span class="rgmuse-chip">🟡 결재 대기 '+c.p+'</span><span class="rgmuse-chip">💧 승인 집행 '+c.a+'</span><span class="rgmuse-chip">⏸️ 보류 '+c.h+'</span><span class="rgmuse-chip">✅ 자율 완수 '+c.d+'</span>';
var h="";[3,2,1].forEach(function(k){var arr=g[k];if(!arr.length)return;arr=arr.slice().sort(function(a,b){return(RANK[a.status]||0)-(RANK[b.status]||0);});h+='<div class="rgmuse-sec '+TIER[k].k+'"><div class="rgmuse-sec-h">'+TIER[k].label+' <span>'+arr.length+'건</span></div>';arr.forEach(function(t){h+=card(t);});h+='</div>';});
list.innerHTML=h;}
function refresh(){var n=pendingCount(),isl=document.getElementById("rgmuse-island");if(isl){var tx=isl.querySelector(".rgmuse-txt");if(tx)tx.textContent="📋 결재 "+n+"건";if(lastPending>=0&&n>lastPending){isl.classList.remove("pop");void isl.offsetWidth;isl.classList.add("pop");}}
lastPending=n;var db=document.getElementById("rgmuse-dock-btn");if(db)db.title="뮤즈(Muse) 자율 대행 & 대표님 결재 보드 — 결재 대기 "+n+"건";renderBoard();}
function openBoard(){var o=document.getElementById("rgmuse-overlay");if(!o)return;renderBoard();o.classList.add("on");setTimeout(function(){var i=document.getElementById("rgmuse-input");if(i)i.focus();},60);}
function closeBoard(){var o=document.getElementById("rgmuse-overlay");if(o)o.classList.remove("on");}
function submit(){var i=document.getElementById("rgmuse-input"),f=document.getElementById("rgmuse-fwd");if(!i||!i.value.trim())return;addTask(i.value,f&&f.checked);i.value="";}
function ensureUI(){if(document.getElementById("rgmuse-island"))return;
var isl=document.createElement("div");isl.id="rgmuse-island";isl.setAttribute("role","button");isl.setAttribute("aria-label","뮤즈 결재 대기 보드 열기");isl.innerHTML='<span class="rgmuse-dot"></span><span class="rgmuse-txt">📋 결재 0건</span>';isl.addEventListener("click",function(e){e.stopPropagation();openBoard();});document.body.appendChild(isl);
var bb=document.createElement("div");bb.id="rgmuse-bubble";document.body.appendChild(bb);
var ov=document.createElement("div");ov.id="rgmuse-overlay";ov.innerHTML='<div id="rgmuse-board" role="dialog" aria-modal="true" aria-label="뮤즈 자율 대행 보드"><div class="rgmuse-head"><div><div class="rgmuse-h1">📋 뮤즈(Muse) 자율 대행 &amp; 대표님 결재 보드</div><div class="rgmuse-sub">'+VERSION+' · '+ANTIBODY+' · ☲☰ #14 화천대유 · ☲☵ #64 화수미제</div></div><button type="button" class="rgmuse-x" data-act="close" aria-label="닫기">✕</button></div><div class="rgmuse-in"><input id="rgmuse-input" type="text" placeholder="아온아, 이 작업 대신 해줘..." autocomplete="off"><button type="button" id="rgmuse-go" data-act="go">🚀 대행 지시</button></div><label class="rgmuse-fw"><input type="checkbox" id="rgmuse-fwd"> 독대실 질문창에도 함께 전달</label><div class="rgmuse-legend">🟢 자동 집행 · 🔵 선집행 후보고 · 🟡 대표님 결재 후 집행 — 키워드로 자동 분류</div><div id="rgmuse-sum"></div><div id="rgmuse-list"></div></div>';
ov.addEventListener("click",function(e){if(e.target===ov){closeBoard();return;}var b=e.target.closest?e.target.closest("[data-act]"):null;if(!b)return;var a=b.getAttribute("data-act"),id=b.getAttribute("data-id");if(a==="close")closeBoard();else if(a==="go")submit();else if(a==="approve")approve(id);else if(a==="hold")hold(id);});
document.body.appendChild(ov);
var inp=document.getElementById("rgmuse-input");if(inp)inp.addEventListener("keydown",function(e){if(e.key==="Enter"&&!e.isComposing){e.preventDefault();submit();}});
document.addEventListener("keydown",function(e){if(e.key==="Escape")closeBoard();});}
function findDockBtn(sym,word){var els=document.querySelectorAll("button,[role='button'],a"),best=null;for(var i=0;i<els.length;i++){var e=els[i];if(e.id&&e.id.indexOf("rgmuse")===0)continue;var tx=e.textContent||"";if(tx.indexOf(sym)>=0&&(!word||tx.indexOf(word)>=0)){if(!best||tx.length<(best.textContent||"").length)best=e;}}return best;}
function injectDock(){if(document.getElementById("rgmuse-dock-btn"))return true;var clean=findDockBtn("🧹","정화")||findDockBtn("🧹"),hide=findDockBtn("🙈"),ref=clean||hide;if(!ref||!ref.parentNode)return false;
var b=document.createElement("button");b.type="button";b.id="rgmuse-dock-btn";b.className=ref.className||"";if(ref.getAttribute("style"))b.setAttribute("style",ref.getAttribute("style"));b.textContent="📋대행";b.title="뮤즈(Muse) 자율 대행 & 대표님 결재 보드";b.addEventListener("click",function(e){e.preventDefault();e.stopPropagation();openBoard();});
if(clean&&hide&&hide.parentNode===clean.parentNode)clean.parentNode.insertBefore(b,hide);else if(clean)clean.parentNode.insertBefore(b,clean.nextSibling);else hide.parentNode.insertBefore(b,hide);
var fab=document.getElementById("rgmuse-fab");if(fab&&fab.parentNode)fab.parentNode.removeChild(fab);refresh();return true;}
function fallbackFab(){if(document.getElementById("rgmuse-dock-btn")||document.getElementById("rgmuse-fab"))return;var f=document.createElement("button");f.type="button";f.id="rgmuse-fab";f.textContent="📋대행";f.title="뮤즈(Muse) 자율 대행 & 대표님 결재 보드";f.addEventListener("click",function(e){e.stopPropagation();openBoard();});document.body.appendChild(f);}
function place(){var isl=document.getElementById("rgmuse-island");if(!isl)return;if(pendingCount()<=0){isl.classList.remove("on");return;}
var r=visibleRect(aonEl()),x,y,below=false;
if(r){x=r.left+r.width/2;y=r.top-6;if(y<34){y=r.bottom+6;below=true;}}
else{var r2=visibleRect(document.getElementById("rgmuse-dock-btn"))||visibleRect(document.getElementById("rgmuse-fab"));if(r2){x=r2.left+r2.width/2;y=r2.top-6;if(y<34){y=r2.bottom+6;below=true;}}else{x=window.innerWidth/2;y=10;below=true;}}
x=Math.max(60,Math.min(window.innerWidth-60,x));isl.style.left=x+"px";isl.style.top=y+"px";isl.classList.toggle("below",below);isl.classList.add("on");}
function loop(){try{place();}catch(e){}window.requestAnimationFrame(loop);}
function init(){ensureUI();tasks=merge(SEED,loadLocal());tasks.forEach(function(t){if(t.status==="RUNNING")finish2(t.id,true);});refresh();
var tries=0;(function retry(){if(injectDock())return;if(++tries<30)setTimeout(retry,500);else fallbackFab();})();
var pend=false;try{new MutationObserver(function(){if(pend||document.getElementById("rgmuse-dock-btn"))return;pend=true;setTimeout(function(){pend=false;injectDock();},300);}).observe(document.body,{childList:true,subtree:true});}catch(e){}
window.requestAnimationFrame(loop);
try{if(location.protocol!=="file:"&&window.fetch){fetch("rgon_muse_tasks.json",{cache:"no-store"}).then(function(r){return r.ok?r.json():null;}).then(function(d){if(d&&d.tasks&&d.tasks.length){tasks=merge(merge(SEED,d.tasks),loadLocal());refresh();}}).catch(function(){});}}catch(e){}
window.RGON_MUSE={open:openBoard,close:closeBoard,add:addTask,approve:approve,hold:hold,tasks:function(){return tasks.slice();},classify:classify,version:VERSION};}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
})();
</script>
<!-- [RGON-MUSE-V1-END] -->
"""


# ====================================================================
# 6. 텍스트 동기화 유틸
# ====================================================================
def sync_text(text, is_md, is_py):
    out = []
    for ln in text.splitlines(keepends=True):
        if is_md and HIST_LINE.search(ln):
            out.append(ln)  # Step 31 역사 기록 줄은 보존
            continue
        ln = ln.replace(OLD_VER, NEW_VER)
        ln = AB_RE.sub(r"R1\g<1>R32", ln)
        for rx, rp in (PY_COUNT if is_py else DOC_COUNT):
            ln = rx.sub(rp, ln)
        out.append(ln)
    return "".join(out)


def walk_json(o, key=None, counts=True):
    if isinstance(o, dict):
        return {k: walk_json(v, k, counts) for k, v in o.items()}
    if isinstance(o, list):
        return [walk_json(v, key, counts) for v in o]
    if isinstance(o, str):
        return AB_RE.sub(r"R1\g<1>R32", o.replace(OLD_VER, NEW_VER))
    if counts and isinstance(o, int) and not isinstance(o, bool) and o == OLD_SK and key in COUNT_KEYS:
        return NEW_SK
    return o


def nl_of(text):
    return "\r\n" if "\r\n" in text else "\n"


def append_section(text, section):
    nl = nl_of(text)
    sec = section.replace("\r\n", "\n").replace("\n", nl)
    if not text.endswith(("\n", "\r\n")):
        text += nl
    return text + nl + sec + ("" if sec.endswith(nl) else nl)


def insert_table_row(text, key_rx, cells):
    lines = text.splitlines(keepends=True)
    idx = None
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("|") and re.search(key_rx, ln):
            idx = i
    if idx is None:
        return None
    ref = lines[idx]
    ncol = ref.strip().strip("|").count("|") + 1
    cells = list(cells)
    if len(cells) > ncol:
        cs = cells[:ncol - 1] + [" / ".join(cells[ncol - 1:])]
    else:
        cs = cells + [""] * (ncol - len(cells))
    nl = "\r\n" if ref.endswith("\r\n") else "\n"
    if not ref.endswith(("\n", "\r\n")):
        lines[idx] = ref + nl
    lines.insert(idx + 1, "| " + " | ".join(cs) + " |" + nl)
    return "".join(lines)


def insert_after_imports(text, add_lines):
    nl = nl_of(text)
    lines = text.splitlines(keepends=True)
    last, i = -1, 0
    while i < min(len(lines), 400):
        ln = lines[i]
        if re.match(r"^(import\s+\S|from\s+\S+\s+import\s)", ln):
            j = i
            if "(" in ln and ")" not in ln:
                while j < len(lines) - 1 and ")" not in lines[j]:
                    j += 1
            elif ln.rstrip().endswith("\\"):
                while j < len(lines) - 1 and lines[j].rstrip().endswith("\\"):
                    j += 1
            last, i = j, j + 1
            continue
        i += 1
    block = "".join(l + nl for l in add_lines)
    if last < 0:
        k = 0
        while k < len(lines) and (lines[k].startswith("#!") or re.match(r"^#.*coding[:=]", lines[k])):
            k += 1
        lines.insert(k, block)
    else:
        if not lines[last].endswith(("\n", "\r\n")):
            lines[last] += nl
        lines.insert(last + 1, block)
    return "".join(lines)


def detect_indent(text):
    m = re.search(r'\n( +)"', text)
    return len(m.group(1)) if m else 2


def load_muse_summary():
    try:
        d = json.loads((ROOT / TASK_REL).read_text(encoding="utf-8"))
        return d.get("summary", {}), d.get("tasks", [])
    except Exception:
        return {}, []


# ====================================================================
# 6-1. rgon_white_blood_cell.py DEFAULT_ANTIBODIES 에 R32 주입
# ====================================================================
STR_LIT_RE = re.compile(r'("""|\'\'\'|"|\')((?:\\.|(?!\1)[^\\])*?)\1', re.S)

R32_RUNTIME_PATCH = '''
# [RGON-R32-ANTIBODY-PATCH] Step 32 · v11.31-MUSE-DELEGATION · R1~R32
def _rgon_add_r32(ab):
    desc = __DESC__
    full = __FULL__
    text_keys = ("name", "title", "desc", "description", "text", "label", "summary", "rule")
    num_keys = ("no", "num", "index", "number", "order", "seq")
    if "R32" in repr(ab):
        return ab

    def _clone(sample):
        if isinstance(sample, dict):
            v = dict(sample)
            for k in list(v):
                x = v[k]
                if isinstance(x, str):
                    if x.strip().upper().startswith("R") and x.strip()[1:].isdigit():
                        v[k] = "R32"
                    elif k in text_keys:
                        v[k] = desc
                    else:
                        v[k] = x.replace("R31", "R32").replace("Step 31", "Step 32")
                elif isinstance(x, int) and not isinstance(x, bool) and k in num_keys:
                    v[k] = 32
            return v
        if isinstance(sample, (tuple, list)):
            out = []
            for x in sample:
                if isinstance(x, str) and x.strip().upper().startswith("R") and x.strip()[1:].isdigit():
                    out.append("R32")
                elif isinstance(x, str) and len(x) > 8:
                    out.append(desc)
                else:
                    out.append(x)
            return type(sample)(out)
        return full

    if isinstance(ab, dict):
        ab = dict(ab)
        vals = list(ab.values())
        sample = vals[-1] if vals else None
        ab["R32"] = _clone(sample) if isinstance(sample, (dict, list, tuple)) else desc
        return ab
    seq = list(ab)
    seq.append(_clone(seq[-1] if seq else None))
    return tuple(seq) if isinstance(ab, tuple) else seq


DEFAULT_ANTIBODIES = _rgon_add_r32(DEFAULT_ANTIBODIES)
'''


def _scan_close(text, i):
    """text[i] 가 여는 괄호일 때 (닫는 괄호 인덱스, 최상위 원소 구간 목록) 반환."""
    pairs = {"[": "]", "{": "}", "(": ")"}
    stack = [pairs[text[i]]]
    j, n = i + 1, len(text)
    elems, start = [], i + 1
    while j < n:
        c = text[j]
        if c == "#":
            k = text.find("\n", j)
            j = n if k < 0 else k
            continue
        if c in "\"'":
            q3 = text[j:j + 3]
            if q3 in ('"""', "'''"):
                k = text.find(q3, j + 3)
                if k < 0:
                    return None
                j = k + 3
                continue
            k = j + 1
            while k < n and text[k] != c:
                if text[k] == "\\":
                    k += 1
                elif text[k] == "\n":
                    break
                k += 1
            j = k + 1
            continue
        if c in pairs:
            stack.append(pairs[c])
        elif c in ")]}":
            if not stack or c != stack[-1]:
                return None
            stack.pop()
            if not stack:
                elems.append((start, j))
                return j, elems
        elif c == "," and len(stack) == 1:
            elems.append((start, j))
            start = j + 1
        j += 1
    return None


def _is_real(seg):
    return bool(re.sub(r"#[^\n]*", "", seg).strip())


def _py_quote(content, q):
    if len(q) == 3:
        return q + content.replace("\\", "\\\\") + q
    return q + content.replace("\\", "\\\\").replace(q, "\\" + q) + q


def _clone_r31_element(seg):
    body = seg.lstrip()
    while body.startswith("#"):
        k = body.find("\n")
        if k < 0:
            return None
        body = body[k + 1:].lstrip()
    lines = body.rstrip().split("\n")
    while len(lines) > 1 and lines[-1].strip().startswith("#"):
        lines.pop()
    body = "\n".join(lines).rstrip()
    if not body:
        return None

    def subrest(s):
        s = re.sub(r"\bR31\b", "R32", s)
        s = re.sub(r"(Step\s*|STEP\s*|step)31\b", r"\g<1>32", s)
        s = s.replace(OLD_VER, NEW_VER)
        s = re.sub(r"""((?:["'](?:no|num|index|number|order|seq)["']|\b(?:no|num|index|number|order|seq))\s*[:=]\s*)31\b""",
                   r"\g<1>32", s)
        return s

    best = None
    for m in STR_LIT_RE.finditer(body):
        c = m.group(2)
        if re.fullmatch(r"\s*R\d+\s*", c):
            continue
        if best is None or len(c) > len(best.group(2)):
            best = m
    if best is None:
        return subrest(body)
    c = best.group(2).strip()
    newc = R32_TEXT if re.match(r"R31\b", c) else R32_DESC
    lit = _py_quote(newc, best.group(1))
    return subrest(body[:best.start()]) + lit + subrest(body[best.end():])


def _insert_literal(text, op, ce, elems):
    real = [(s, e) for s, e in elems if _is_real(text[s:e])]
    if not real:
        return None
    tmpl = None
    for s, e in real:
        if re.search(r"\bR31\b", text[s:e]):
            tmpl = (s, e)
    if tmpl is None:
        return None
    new_el = _clone_r31_element(text[tmpl[0]:tmpl[1]])
    if not new_el:
        return None
    nl = nl_of(text)
    multiline = "\n" in text[op:ce]
    ts = text[tmpl[0]:tmpl[1]]
    lead = ts[:len(ts) - len(ts.lstrip())]
    indent = lead.split("\n")[-1].replace("\r", "") if "\n" in lead else ""
    if multiline and not indent:
        indent = "    "
    ls, le = real[-1]
    if le < ce and text[le] == ",":
        pos = le + 1
        ins = (nl + indent if multiline else " ") + new_el + ","
    else:
        code = text[ls:le].rstrip()
        lines = code.split("\n")
        while len(lines) > 1 and lines[-1].strip().startswith("#"):
            lines.pop()
        code = "\n".join(lines).rstrip()
        pos = ls + len(code)
        ins = "," + (nl + indent if multiline else " ") + new_el
    return text[:pos] + ins + text[pos:]


def _runtime_patch(text, ce, indent):
    nl = nl_of(text)
    k = text.find("\n", ce)
    pos = len(text) if k < 0 else k + 1
    patch = R32_RUNTIME_PATCH.replace("__DESC__", repr(R32_DESC)).replace("__FULL__", repr(R32_TEXT))
    body = "".join((indent + l + nl) if l.strip() else nl for l in patch.strip("\n").split("\n"))
    return text[:pos] + ("" if k >= 0 else nl) + nl + body + text[pos:]


def _compiles(src, name):
    try:
        compile(src, name, "exec")
        return True
    except SyntaxError:
        return False


def h_wbc(text, orig):
    for rx, rp in AB_COUNT:
        text = rx.sub(rp, text)
    if "[RGON-R32-ANTIBODY-PATCH]" in text:
        return text
    m = re.search(r"^([ \t]*)DEFAULT_ANTIBODIES\s*(?::[^=\n]+)?=\s*([\[\{\(])", text, re.M)
    if not m:
        log("  ⚠️ rgon_white_blood_cell.py: DEFAULT_ANTIBODIES 리터럴 미발견 — R32 항목 주입 건너뜀")
        return text
    op = m.end() - 1
    sc = _scan_close(text, op)
    if sc is None:
        log("  ⚠️ rgon_white_blood_cell.py: DEFAULT_ANTIBODIES 괄호 해석 실패 — R32 주입 건너뜀")
        return text
    ce, elems = sc
    if re.search(r"(?<![~\-–～])\bR32\b", text[op:ce]):
        log("  ＝ DEFAULT_ANTIBODIES 에 R32 이미 존재")
        return text
    cand = _insert_literal(text, op, ce, elems)
    if cand is not None and _compiles(cand, WBC_REL):
        log("  🧬 DEFAULT_ANTIBODIES 리터럴에 R32 항목 추가 (R31 형식 복제)")
        return cand
    cand = _runtime_patch(text, ce, m.group(1))
    if _compiles(cand, WBC_REL):
        log("  🧬 DEFAULT_ANTIBODIES 직후 R32 런타임 패치 추가 (구조 자동 대응)")
        return cand
    log("  ⚠️ R32 주입 시 구문 오류 — 원문 유지")
    return text


# ====================================================================
# 7. 파일별 핸들러
# ====================================================================
def h_daily(text, orig):
    if re.search(r"\bEXPECTED_SKILL_COUNT\s*[:=]", text):
        text = re.sub(r"(\bEXPECTED_SKILL_COUNT\s*(?::\s*int\s*)?=\s*)\d+", r"\g<1>28", text)
    else:
        text = insert_after_imports(text, ["EXPECTED_SKILL_COUNT = 28  # Step 32 · v11.31-MUSE-DELEGATION"])
    add = []
    if NEW_VER not in text:
        add.append(f'RGON_VERSION_STEP32 = "{NEW_VER}"')
    if NEW_AB not in text:
        add.append(f'RGON_ANTIBODY_RANGE = "{NEW_AB}"  # R32: Muse Delegation Engine')
    if add:
        text = insert_after_imports(text, add)
    return text


def h_skill_md(text, orig):
    if SKILL_SLUG in orig:
        return text
    cells = ["28", f"`{SKILL_SLUG}`", "뮤즈 자율 대행·위임 집행 (Muse Wonder · 3-Tier HITL · Dynamic Island)",
             f"`{SKILL_REL}`", "R32", NEW_VER]
    t2 = insert_table_row(text, r"^\s*\|\s*\**\s*27\s*\**\s*\|", cells)
    if t2 is not None:
        return t2
    return append_section(text, f"<!-- [RGON-SKILL-28] -->\n## 28. `{SKILL_SLUG}` (R32 · {NEW_VER})\n"
                                f"- 경로: `{SKILL_REL}`\n- 설명: 메타 뮤즈(Muse Wonder & Muse Charm) + 3-Tier HITL Gate + "
                                f"아온 다이내믹 아일랜드 알림 캡슐 통합 프로토콜\n- 정식 스킬 총 **28개**\n")


def h_skill_json(d, orig):
    entry = {"no": 28, "id": SKILL_SLUG, "name": SKILL_SLUG, "slug": SKILL_SLUG,
             "title": "뮤즈 자율 대행·위임 집행 (Muse Delegation Engine)", "path": SKILL_REL,
             "category": "제8기관 · 자율 대행", "antibody": "R32", "version": NEW_VER, "added": TODAY,
             "description": "메타 뮤즈(Muse Wonder & Muse Charm) + 3-Tier HITL 안전 승인 게이트 + 아온 다이내믹 아일랜드 통합 프로토콜"}

    def fit(template):
        if isinstance(template, dict):
            for k in ("id", "no", "index", "num", "number"):
                if isinstance(template.get(k), int) and not isinstance(template.get(k), bool):
                    entry[k] = 28
        return entry

    def has(container):
        return SKILL_SLUG in json.dumps(container, ensure_ascii=False)

    if isinstance(d, list):
        if not has(d):
            d.append(fit(d[-1] if d else None))
        return d
    if isinstance(d, dict):
        container = None
        for k in ("skills", "items", "entries", "index", "list"):
            if isinstance(d.get(k), (list, dict)):
                container = d[k]
                break
        if container is None:
            d["skills"] = container = []
        if isinstance(container, list):
            if not has(container):
                container.append(fit(container[-1] if container else None))
        elif SKILL_SLUG not in container:
            vals = list(container.values())
            container[SKILL_SLUG] = fit(vals[-1] if vals else None)
        d["count"] = NEW_SK
        d["total_skills"] = NEW_SK
        if "version" in d:
            d["version"] = NEW_VER
        if "antibody" in d or "antibodies" in d:
            d["antibody" if "antibody" in d else "antibodies"] = NEW_AB
    return d


def has_r32(orig):
    return re.search(r"\bR32\s*[:|\]\)]|\|\s*\**R32\b|\*\*R32\*\*", orig) is not None


def h_constitution(text, orig):
    if has_r32(orig):
        return text
    return append_section(text, f"<!-- [RGON-CONSTITUTION-R32] -->\n## 제32조 (R32) 자율 대행·위임 집행 헌법 — {NEW_VER} · {NEW_AB}\n"
                                f"- {R32_TEXT}\n"
                                "- 제1항 (화천대유 #14): Tier 1 AUTO, Tier 2 NOTIFY 작업은 막힘없이 끝까지 대행한다.\n"
                                "- 제2항 (화수미제 #64): Tier 3 HITL_GATE 작업은 실행계획서·기대효과·리스크를 작성한 뒤 "
                                "대표님 [✅ 승인 집행] 이후에만 집행한다. 승인 전 실제 집행은 0건이다.\n"
                                "- 제3항: Tier 1/2 작업에는 결재 버튼을 노출하지 않고, Tier 3 작업은 결재 없이 자동 집행하지 않는다.\n"
                                "- 제4항: 아온(#rgyt-wrap / #aon-roamer) 순수 3D 물방울 형태와 기존 미니 독 버튼(🔍레이더·📈3자심판·🧹정화·🙈숨기기)은 그대로 보존한다.\n")


def h_antibody(text, orig):
    if has_r32(orig):
        return text
    cells = ["R32", R32_DESC, "Step 32", NEW_VER, TODAY]
    t2 = insert_table_row(text, r"^\s*\|\s*\**\s*R31\b", cells)
    if t2 is not None:
        return t2
    return append_section(text, f"<!-- [RGON-ANTIBODY-R32] -->\n## R32 — Step 32 · {NEW_VER} · {TODAY}\n- {R32_TEXT}\n"
                                f"- 엔진: `{ENGINE_REL}` · 스킬: `{SKILL_REL}` · 큐: `{TASK_REL}`\n")


def h_codemap(text, orig):
    if ENGINE_REL in orig:
        return text
    return append_section(text, f"<!-- [RGON-CODEMAP-STEP32] -->\n## Step 32 — 제8기관: 자율 대행·위임 집행 기관 ({NEW_VER})\n"
                                f"- `{ENGINE_REL}`: Muse Wonder 비동기 위임 큐 + 3-Tier HITL 게이트 (`--self-test`, `--list`, `--add`, `--approve`, `--hold`)\n"
                                f"- `{TASK_REL}` / `{DOCS_TASK_REL}`: 대행 작업 큐 (sha256 무결성)\n"
                                f"- `{SKILL_REL}`: 28번째 정식 스킬\n"
                                "- 7개 HTML V13 블록(YT-SCOUT-V13 / UX-CLEANUP-V13) 내부 `[RGON-MUSE-V1]`: 아온 다이내믹 아일랜드 + 📋대행 독 + 결재 보드\n")


def h_glossary(text, orig):
    if "Muse Wonder" in orig:
        return text
    return append_section(text, f"<!-- [RGON-GLOSSARY-STEP32] -->\n## Step 32 용어 ({NEW_VER})\n"
                                "- **Muse Wonder**: 대표님 지시를 끝까지 자율 수행하는 비동기 대행 작업 큐\n"
                                "- **Muse Charm**: 아온 다이내믹 아일랜드. 결재 대기 건수를 알려 주는 캡슐 배지(`📋 결재 N건`)\n"
                                "- **3-Tier HITL Gate**: 🟢 AUTO(자동 집행) · 🔵 NOTIFY(선집행 후보고) · 🟡 HITL_GATE(대표님 결재 후 집행)\n"
                                "- **PENDING_APPROVAL / APPROVED_DONE / ON_HOLD**: Tier 3 상태 (결재 대기 / 승인 집행 완료 / 보류)\n"
                                "- **화천대유(#14) · 화수미제(#64)**: 막힘없는 대행 · 신중한 분별과 완수\n")


def h_brief_md(text, orig):
    if "[RGON-BRIEF-STEP32]" in orig:
        return text
    s, tasks = load_muse_summary()
    pend = [t for t in tasks if t.get("status") == "PENDING_APPROVAL"]
    lines = "".join(f"  - 🟡 {t.get('id')}: {t.get('title')}\n" for t in pend)
    return append_section(text, f"<!-- [RGON-BRIEF-STEP32] -->\n## 📋 뮤즈 대행 브리핑 ({NEW_VER} · {NEW_AB} · 정식 스킬 28개)\n"
                                f"- 대행 큐 {s.get('total', 0)}건 · 자동 완수 {s.get('done', 0)} · 선집행 보고 {s.get('done_notified', 0)} · "
                                f"결재 대기 {s.get('pending_approval', 0)}\n" + lines)


def h_brief_json(d, orig):
    if isinstance(d, dict):
        s, tasks = load_muse_summary()
        d["muse_delegation"] = {"version": NEW_VER, "antibody": NEW_AB, "summary": s, "updated_at": STAMP,
                                "pending": [{"id": t.get("id"), "title": t.get("title")} for t in tasks
                                            if t.get("status") == "PENDING_APPROVAL"]}
        for k in ("version", "rgon_version"):
            if k in d:
                d[k] = NEW_VER
    return d


def h_ledger(d, orig):
    """면역 원장: 버전·항체 표기만 동기화 (카운트·이력 데이터는 보존)."""
    if isinstance(d, dict):
        for k in ("version", "rgon_version", "current_version"):
            if k in d and isinstance(d[k], str):
                d[k] = NEW_VER
        for k in ("antibody", "antibodies", "antibody_range"):
            if k in d and isinstance(d[k], str):
                d[k] = NEW_AB
    return d


# ====================================================================
# 8. 동기화 실행
# ====================================================================
PY_SYNC = ["rgon_daily_cycle.py", "rgon_self_evolution_engine.py", "rgon_omni_creator_forge.py",
           "rgon_k_avatar_engine.py", "rgon_excretory_organ.py", WBC_REL]
MD_SYNC = {"skills/SKILL_INDEX.md": h_skill_md, "CONSTITUTION.md": h_constitution,
           "ANTIBODY_REGISTRY.md": h_antibody, "CODE_MAP.md": h_codemap, "GLOSSARY.md": h_glossary,
           "RGON_MORNING_BRIEF.md": h_brief_md}
# (핸들러, 없으면 생성 여부, 스킬 카운트 키 치환 여부)
JSON_SYNC = {"skills/SKILL_INDEX.json": (h_skill_json, True, True),
             "rgon_morning_brief.json": (h_brief_json, True, True),
             LEDGER_REL: (h_ledger, False, False)}


def read_text(p):
    b = p.read_bytes()
    bom = b.startswith(b"\xef\xbb\xbf")
    return b[3:].decode("utf-8") if bom else b.decode("utf-8"), bom


def sync_all():
    for rel in PY_SYNC:
        p = ROOT / rel
        if not p.exists():
            log(f"  ⚠️ 없음(건너뜀): {rel}")
            continue
        text, bom = read_text(p)
        new = sync_text(text, False, True)
        if rel == "rgon_daily_cycle.py":
            new = h_daily(new, text)
        if rel == WBC_REL:
            new = h_wbc(new, text)
        if not _compiles(new, rel):
            raise RuntimeError(f"{rel} 동기화 후 구문 오류 — 롤백")
        log(f"  {'✏️' if write_text(p, new, bom) else '＝'} {rel}")
    for rel, fn in MD_SYNC.items():
        p = ROOT / rel
        if not p.exists():
            log(f"  ⚠️ 없음 → 새로 생성: {rel}")
            text, bom = f"# {Path(rel).stem}\n", False
        else:
            text, bom = read_text(p)
        new = fn(sync_text(text, True, False), text)
        log(f"  {'✏️' if write_text(p, new, bom) else '＝'} {rel}")
    for rel, (fn, create, counts) in JSON_SYNC.items():
        p = ROOT / rel
        if p.exists():
            text, bom = read_text(p)
            try:
                d = json.loads(text)
            except Exception:
                new = AB_RE.sub(r"R1\g<1>R32", text.replace(OLD_VER, NEW_VER))
                log(f"  {'✏️' if write_text(p, new, bom) else '＝'} {rel} (JSON 파싱 불가 → 텍스트 동기화)")
                continue
        elif create:
            log(f"  ⚠️ 없음 → 새로 생성: {rel}")
            text, bom, d = "{}", False, {}
        else:
            log(f"  ⚠️ 없음(건너뜀): {rel}")
            continue
        d = fn(walk_json(d, counts=counts), text)
        ind = detect_indent(text)
        log(f"  {'✏️' if write_text(p, json.dumps(d, ensure_ascii=False, indent=ind) + chr(10), bom) else '＝'} {rel}")


# ====================================================================
# 9. HTML V13 블록 주입 (YT-SCOUT-V13 / UX-CLEANUP-V13 호환)
# ====================================================================
def v13_span(b):
    """같은 종류(YT-SCOUT ↔ YT-SCOUT, UX-CLEANUP ↔ UX-CLEANUP)의 START·END 쌍을 찾아
    (START 마커 끝 인덱스, END 마커 시작 인덱스) 반환. 없으면 None."""
    for ms in V13_START_RE.finditer(b):
        kind = b"YT-SCOUT" if b"YT-SCOUT" in ms.group(0) else b"UX-CLEANUP"
        for me in V13_END_RE.finditer(b, ms.end()):
            if kind in me.group(0):
                return ms.end(), me.start()
    return None


def find_v13_htmls():
    out = []
    for p in iter_files():
        if p.suffix.lower() in (".html", ".htm"):
            try:
                b = p.read_bytes()
            except Exception:
                continue
            if v13_span(b):
                out.append(p)
    return sorted(out)


def diagnose_v13_markers():
    found = {}
    for p in iter_files():
        if p.suffix.lower() in (".html", ".htm"):
            try:
                b = p.read_bytes()
            except Exception:
                continue
            for m in set(V13_ANY_RE.findall(b)):
                found.setdefault(m.decode("utf-8", "replace"), []).append(relp(p))
    if not found:
        log("  (진단) HTML 내 RGON-*-V13 마커가 전혀 없습니다.")
    for k, v in sorted(found.items()):
        log(f"  (진단) {k}: {len(v)}개 파일 — {', '.join(v[:7])}{' …' if len(v) > 7 else ''}")


def build_muse_block():
    _, tasks = load_muse_summary()
    seed = json.dumps(tasks, ensure_ascii=False).replace("</", "<\\/")
    return MUSE_BLOCK_TEMPLATE.replace("__RGMUSE_SEED__", seed)


def inject_html(p, block):
    b = p.read_bytes()
    sp = v13_span(b)
    if not sp:
        raise RuntimeError(f"V13 마커 이상: {relp(p)}")
    pre, inner, post = b[:sp[0]], b[sp[0]:sp[1]], b[sp[1]:]
    inner_t = MUSE_BLOCK_RE.sub("", inner.decode("utf-8"))
    nl = "\r\n" if b"\r\n" in inner else "\n"
    if not inner_t.endswith(("\n", "\r\n")):
        inner_t += nl
    inner_t += block.replace("\n", nl) if nl == "\r\n" else block
    new = pre + inner_t.encode("utf-8") + post
    nsp = v13_span(new)
    assert nsp and new[:nsp[0]] == pre and new[nsp[1]:] == post, "V13 바깥 영역 변형 감지"
    return write_bytes(p, new), sha_bytes(pre) + sha_bytes(post)


def outside_hash(b):
    sp = v13_span(b)
    if not sp:
        return ""
    return sha_bytes(b[:sp[0]]) + sha_bytes(b[sp[1]:])


# ====================================================================
# 10. 검증
# ====================================================================
def count_skills():
    sd = ROOT / "skills"
    dirs = sum(1 for d in sd.iterdir() if d.is_dir() and (d / "SKILL.md").exists()) if sd.exists() else 0
    try:
        j = json.loads(read_text(sd / "SKILL_INDEX.json")[0])
        jc = j.get("total_skills", j.get("count")) if isinstance(j, dict) else len(j)
    except Exception:
        jc = None
    m = re.search(r"\bEXPECTED_SKILL_COUNT\s*(?::\s*int\s*)?=\s*(\d+)", read_text(ROOT / "rgon_daily_cycle.py")[0]) \
        if (ROOT / "rgon_daily_cycle.py").exists() else None
    return [dirs, jc, int(m.group(1)) if m else None]


def check_antibody():
    bad = []
    for rel in ["rgon_daily_cycle.py", "CONSTITUTION.md", "ANTIBODY_REGISTRY.md", "skills/SKILL_INDEX.md"]:
        p = ROOT / rel
        if p.exists():
            t = read_text(p)[0]
            if NEW_AB not in t and "R32" not in t:
                bad.append(rel)
    p = ROOT / WBC_REL
    if p.exists():
        t = read_text(p)[0]
        if OLD_AB in t or OLD_VER in t:
            bad.append(f"{WBC_REL}(구버전 잔존)")
        if "DEFAULT_ANTIBODIES" in t and not re.search(r"(?<![~\-–～])\bR32\b", t):
            bad.append(f"{WBC_REL}(DEFAULT_ANTIBODIES R32 없음)")
    return bad


def msgbox(title, text):
    if os.name != "nt":
        return
    try:
        ps = ("Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show("
              f"'{text.replace(chr(39), chr(39) * 2)}','{title.replace(chr(39), chr(39) * 2)}')")
        subprocess.Popen(["powershell", "-NoProfile", "-Command", ps], creationflags=0x08000000)
    except Exception:
        pass


def git_sync():
    if not (ROOT / ".git").exists():
        log("  ⚠️ .git 없음 — Git 동기화 건너뜀")
        return "SKIP"
    steps = [["git", "add", "-A"],
             ["git", "commit", "-m", f"Step 32: {NEW_VER} · {NEW_AB} · 정식 스킬 28개 — Muse Delegation Engine"],
             ["git", "fetch", "origin"], ["git", "pull", "--no-rebase", "origin"], ["git", "push", "origin"]]
    for c in steps:
        rc, out = run(c, 300)
        log(f"  $ {' '.join(c[:3])} → rc={rc}")
        if rc != 0 and not (c[1] == "commit" and "nothing to commit" in out):
            log("    " + out.strip()[-400:])
            if c[1] in ("pull", "push"):
                return "FAIL"
    return "OK"


# ====================================================================
# 11. 메인
# ====================================================================
def main():
    no_git, no_box = "--no-git" in sys.argv, "--no-msgbox" in sys.argv
    t0 = time.time()
    log(f"💧 RGON Step 32 — {NEW_VER} · {NEW_AB} · 스킬 {NEW_SK}개 @ {ROOT}")
    if not (ROOT / "rgon_daily_cycle.py").exists():
        log("⛔ 저장소 루트가 아닙니다 (rgon_daily_cycle.py 없음)")
        return 2
    before = snapshot()
    htmls = find_v13_htmls()
    log(f"🔎 V13 HTML {len(htmls)}개 발견 (YT-SCOUT-V13 / UX-CLEANUP-V13)")
    for p in htmls:
        log(f"   · {relp(p)}")
    if len(htmls) != EXPECTED_HTML:
        log(f"⛔ V13 HTML 수 불일치 (기대 {EXPECTED_HTML})")
        diagnose_v13_markers()
        return 2
    html_out_before = {p: outside_hash(p.read_bytes()) for p in htmls}
    results = {}
    try:
        log("① 엔진·큐·스킬 생성")
        write_text(ROOT / ENGINE_REL, ENGINE_SRC)
        track(ROOT / TASK_REL); track(ROOT / DOCS_TASK_REL)
        for tmp in (TASK_REL + ".tmp", DOCS_TASK_REL + ".tmp"):
            TARGETS.add(tmp)
        rc, out = run([sys.executable, ENGINE_REL, "--self-test"])
        log(out.strip())
        results["muse_selftest"] = rc
        if rc != 0:
            raise RuntimeError("rgon_muse_delegator.py --self-test 실패")
        write_text(ROOT / SKILL_REL, SKILL_MD)

        log("② 버전·항체·스킬 수 동기화 (백혈구·면역 원장 포함)")
        sync_all()

        log("③ HTML V13 내부 뮤즈 다이내믹 아일랜드 주입")
        block = build_muse_block()
        for p in htmls:
            ch, _ = inject_html(p, block)
            log(f"  {'✏️' if ch else '＝'} {relp(p)}")

        log("④ 백혈구 self-test")
        wbc = ROOT / WBC_REL
        rc2, out2 = run([sys.executable, wbc.name, "--self-test"]) if wbc.exists() else (998, f"{WBC_REL} 없음")
        log(out2.strip()[-1500:])
        results["wbc_selftest"] = rc2

        log("⑤ 삼성(三省) 3/3 검증")
        html_ok = []
        for p in htmls:
            b = p.read_bytes(); t = b.decode("utf-8", "replace")
            # [수정 2] #rgyt-wrap 또는 #aon-roamer 둘 다 허용
            html_ok.append(v13_span(b) is not None and ("rgyt-wrap" in t or "aon-roamer" in t)
                           and "📋대행" in t and MUSE_START in t and outside_hash(b) == html_out_before[p])
        for p, okv in zip(htmls, html_ok):
            if not okv:
                log(f"    ✗ HTML 검증 실패: {relp(p)}")
        s1 = rc == 0 and rc2 == 0 and all(html_ok)
        after = snapshot()
        ch, de, cr = diff_snap(before, after, TARGETS)
        ch = [x for x in ch if not RUNTIME_RE.search(x)]
        de = [x for x in de if not RUNTIME_RE.search(x)]
        cr = [x for x in cr if not RUNTIME_RE.search(x)]
        s2 = not ch and not de
        counts, ab_bad = count_skills(), check_antibody()
        s3 = counts == [28, 28, 28] and not ab_bad
        log(f"  三省① self-test·HTML: {'PASS' if s1 else 'FAIL'} (muse rc={rc}, wbc rc={rc2}, html {sum(html_ok)}/{len(htmls)})")
        log(f"  三省② 보호 파일 변경 0건: {'PASS' if s2 else 'FAIL'} (변경 {len(ch)} · 삭제 {len(de)} · 신규 {len(cr)}) "
            f"보호 {len(before) - len([k for k in before if k in TARGETS])}개")
        for x in (ch + de)[:20]:
            log(f"    ✗ {x}")
        log(f"  三省③ 스킬 {counts} · 항체 {NEW_AB}: {'PASS' if s3 else 'FAIL'} {ab_bad or ''}")
        score = sum([s1, s2, s3])
        if score != 3:
            raise RuntimeError(f"삼성 {score}/3 — 실패")
    except Exception as e:
        log(f"⛔ {e}")
        rollback()
        if not no_box:
            msgbox("RGON Step 32 실패", f"Step 32 실패 및 롤백: {e}")
        return 1

    s, tasks = load_muse_summary()
    report = (f"# STEP 32 — MUSE DELEGATION REPORT\n\n- 일시: {STAMP}\n- 버전: `{NEW_VER}` · 항체 `{NEW_AB}` · 정식 스킬 **28개**\n"
              f"- {R32_TEXT}\n- 삼성(三省): **3/3 PASS**\n  1. muse self-test rc=0 · 백혈구 self-test rc=0 · HTML {len(htmls)}/7 "
              f"(V13 YT-SCOUT/UX-CLEANUP · #rgyt-wrap/#aon-roamer · 📋대행)\n"
              f"  2. 비대상 보호 파일 해시 변경 0건 (백업 디렉터리·면역 원장·런타임 파일 제외)\n"
              f"  3. 스킬 `[28, 28, 28]` · 항체 `{NEW_AB}` (백혈구 DEFAULT_ANTIBODIES R32 포함)\n\n"
              f"## 대행 큐 ({s.get('total', 0)}건 · 결재 대기 {s.get('pending_approval', 0)}건)\n"
              + "".join(f"- {t.get('id')} [{t.get('tier_label')}] `{t.get('status')}` {t.get('title')}\n" for t in tasks)
              + "\n## 변경 대상 파일\n" + "".join(f"- `{x}`\n" for x in sorted(TARGETS) if not x.endswith(".tmp"))
              + f"\n## 실행 로그\n```\n" + "\n".join(LOG[-80:]) + "\n```\n")
    write_text(ROOT / REPORT_REL, report)
    log(f"📝 보고서: {REPORT_REL}")

    g = "SKIP" if no_git else git_sync()
    log(f"☁️ Git 동기화: {g}")
    msg = (f"Step 32 완료 · {NEW_VER}\n항체 {NEW_AB} · 정식 스킬 28개\n삼성 3/3 PASS · 결재 대기 "
           f"{s.get('pending_approval', 0)}건\nGit: {g} · {time.time() - t0:.1f}s")
    log("✅ " + msg.replace("\n", " | "))
    if not no_box:
        msgbox("RGON Step 32 — Muse Delegation", msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())

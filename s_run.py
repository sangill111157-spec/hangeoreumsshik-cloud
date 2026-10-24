#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 35: v11.34-AON-LAPTOP-HANDS — 제11기관 노트북 만능 제어 수족 & 중요 결재 수동 ON/OFF 마스터 스위치 (G2 최종 완결판)"""
import os, sys, json, re, time, shutil, hashlib, datetime, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARGS = set(sys.argv[1:])
DRY, NO_GIT, NO_MSG = "--dry-run" in ARGS, "--no-git" in ARGS, "--no-msgbox" in ARGS

OLD_VER, NEW_VER = "v11.33-AON-SOUL-BRAIN", "v11.34-AON-LAPTOP-HANDS"
OLD_R, NEW_R = "R1~R34", "R1~R35"
NEW_SK = 31
R35_TEXT = ("R35: 아온(A-ON) 노트북 만능 제어 수족 & 중요 결재 수동 ON/OFF 마스터 스위치 — Tier 3·금융·파일삭제·외부전송은 "
            "마스터 + 카테고리 스위치 수동 ON + 대표님 승인 3중 충족 시에만 집행, 하나라도 OFF면 집행 0건")

V13_START_RE = re.compile(rb"<!--\s*\[RGON-(?:YT-SCOUT|UX-CLEANUP)-V13-START\]\s*-->")
V13_END_RE = re.compile(rb"<!--\s*\[RGON-(?:YT-SCOUT|UX-CLEANUP)-V13-END\]\s*-->")
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode",
             ".rgon_backup", ".rgon_backups", "backups", "archive", "old_backups"}
RUNTIME_RE = re.compile(r"(\.log$|\.pyc$|\.jsonl$|rgon_immune_ledger\.json$|rgon_aon_memory\.json$|dept_sub_agents_state\.json$|\.wbc_tmp$|(^|/)logs?/)")

HTML_TARGETS = ["index.html", "rgon_alpha_audience.html", "rgon_alpha_chat.html", "dashboard/index.html",
                "dashboard/rgon_alpha_chat.html", "docs/index.html", "docs/rgon_alpha_chat.html"]
PY_SYNC = ["rgon_daily_cycle.py", "rgon_self_evolution_engine.py", "rgon_omni_creator_forge.py",
           "rgon_k_avatar_engine.py", "rgon_excretory_organ.py", "rgon_muse_delegator.py",
           "rgon_voice_organ.py", "rgon_aon_soul_brain.py", "rgon_white_blood_cell.py"]
MD_SYNC = ["skills/SKILL_INDEX.md", "CONSTITUTION.md", "ANTIBODY_REGISTRY.md", "CODE_MAP.md",
           "GLOSSARY.md", "RGON_MORNING_BRIEF.md"]
HANDS_REL, SOUL_REL, VOICE_REL, MUSE_REL, WBC_REL = ("rgon_laptop_hands.py", "rgon_aon_soul_brain.py",
                                                     "rgon_voice_organ.py", "rgon_muse_delegator.py", "rgon_white_blood_cell.py")
SKILL_ID = "aon-laptop-hands-manual-gate"
SKILL_REL = f"skills/{SKILL_ID}/SKILL.md"
REPORT_REL = "STEP35_LAPTOP_HANDS_REPORT.md"
EXTRAS = ("rgon_voice_profile.json", "docs/rgon_voice_profile.json", "rgon_aon_memory.json", "docs/rgon_aon_memory.json",
          "rgon_manual_gate_state.json", "docs/rgon_manual_gate_state.json", "rgon_immune_ledger.json",
          "dept_sub_agents_state.json", "docs/dept_sub_agents_state.json")
GIT_EXCLUDES = [":(exclude).rgon_backups", ":(exclude)rgon_aon_memory.json", ":(exclude)docs/rgon_aon_memory.json",
                ":(exclude)rgon_laptop_hands_ledger.jsonl", ":(exclude)aon_drafts", ":(exclude)test_aon_converse.py"]

SKC_RE = re.compile(r"(\b(?:EXPECTED_SKILL_COUNT|SKILL_COUNT|EXPECTED_SKILLS|TOTAL_SKILLS|FORMAL_SKILL_COUNT|OFFICIAL_SKILL_COUNT)\s*(?::\s*int\s*)?=\s*)30\b")
ABC_RE = re.compile(r"(\b(?:EXPECTED_ANTIBODY_COUNT|EXPECTED_ANTIBODIES|ANTIBODY_COUNT|TOTAL_ANTIBODIES)\s*(?::\s*int\s*)?=\s*)34\b")

TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / ".rgon_backups" / f"step35_{TS}"
CHANGED, CREATED, NEW_DIRS, LOG = set(), set(), set(), []
PRE = {}

def log(m):
    print(m); LOG.append(m)

def sha(b): return hashlib.sha256(b).hexdigest()

def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()

def rd(p):
    try: return Path(p).read_text(encoding="utf-8")
    except Exception: return ""

def walk(runtime=False):
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for f in fns:
            p = Path(dp) / f
            if not runtime and RUNTIME_RE.search(rel(p)): continue
            yield p

def snapshot(): return {rel(p): sha(p.read_bytes()) for p in walk()}

def backup(p):
    p = Path(p)
    if p.exists():
        d = BACKUP / rel(p); d.parent.mkdir(parents=True, exist_ok=True)
        if not d.exists(): shutil.copy2(p, d)

def _note_new_dirs(p):
    d = Path(p).parent
    while not d.exists() and d != ROOT:
        NEW_DIRS.add(d); d = d.parent

def write_bytes(p, b):
    p = Path(p); r = rel(p)
    if p.exists() and p.read_bytes() == b: return False
    CHANGED.add(r)
    if DRY: return True
    if p.exists():
        if r not in CREATED: backup(p)
    else:
        CREATED.add(r); _note_new_dirs(p)
    p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b)
    return True

def write_text(p, s): return write_bytes(p, s.encode("utf-8"))

def prepare_extras():
    for r in EXTRAS:
        p = ROOT / r
        if p.exists():
            if r not in CREATED: backup(p)
        else:
            CREATED.add(r); _note_new_dirs(p)

def rollback(reason):
    log(f"⏪ Auto-Rollback 시작: {reason}")
    rs = rm = 0
    for r in sorted(CHANGED | set(EXTRAS) | {REPORT_REL}):
        p, b = ROOT / r, BACKUP / r
        try:
            if r in CREATED:
                if p.exists(): p.unlink(); rm += 1
            elif b.exists():
                p.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(b, p); rs += 1
        except Exception as e:
            log(f"  ⚠️ 복구 실패 {r}: {e!r}")
    for d in sorted(NEW_DIRS, key=lambda x: len(x.parts), reverse=True):
        try:
            if d.exists() and not any(d.iterdir()): d.rmdir()
        except Exception: pass
    post = snapshot()
    diff = [k for k in set(PRE) | set(post) if PRE.get(k) != post.get(k)]
    log(f"⏪ 복원 {rs}개 · 신규 삭제 {rm}개 · 원복 검증 {'✅ 100% 일치' if not diff else '❌ 불일치 ' + str(len(diff)) + '건'}")
    for k in diff[:20]: log(f"    - {k}")
    log(f"   원본 백업: {rel(BACKUP) if BACKUP.exists() else '(없음)'}")

def v13_span(b):
    s = V13_START_RE.search(b)
    if not s: return None
    kind = re.search(rb"(YT-SCOUT|UX-CLEANUP)", s.group(0)).group(1)
    ends = list(V13_END_RE.finditer(b, s.end()))
    for e in ends:
        if kind in e.group(0): return (s.start(), e.end(), e.start())
    return (s.start(), ends[0].end(), ends[0].start()) if ends else None

def outside_hash(b):
    sp = v13_span(b)
    return sha(b[:sp[0]] + b[sp[1]:]) if sp else None

# ============================================================ 1) 제11기관 엔진
HANDS_SRC = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_laptop_hands.py — 제11기관: 아온(A-ON) 노트북 만능 제어 수족 & 중요 결재 수동 ON/OFF 마스터 스위치
버전 v11.34-AON-LAPTOP-HANDS · 항체 R1~R35
주역 #60 수택절(水澤節): 마디를 두어 절제한다 — 스위치가 곧 마디다.
주역 #62 뇌산소과(雷山小過): 작은 일은 넘쳐도 되나 큰 일은 넘치면 안 된다 — 조회는 열고 큰 결재는 잠근다.
주역 #14 화천대유(火天大有): 크게 가진 자는 겸손히 지킨다.
안전 원칙: 실제 증권사 주문·결제·파일 삭제 API는 연결하지 않는다. 허용된 중요 결재는 집행 기록(ledger)만 남긴다.
앱 실행은 허용 목록과 http(s) URL만 허용하며, 임의 명령 문자열은 실행하지 않는다."""
import os, sys, json, re, shutil, platform, datetime, subprocess
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

VERSION = "v11.34-AON-LAPTOP-HANDS"
ANTIBODY = "R1~R35"
ROOT = Path(__file__).resolve().parent
STATE_PATHS = ("rgon_manual_gate_state.json", "docs/rgon_manual_gate_state.json")
LEDGER = ROOT / "rgon_laptop_hands_ledger.jsonl"
DRAFT_DIR = ROOT / "aon_drafts"
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode",
             ".rgon_backup", ".rgon_backups", "backups", "archive", "old_backups"}
GATE_LABELS = {"finance_payment": "💰 금융·결제", "laptop_app_browser": "💻 노트북앱",
               "file_modify_delete": "🗂️ 파일삭제·이동", "external_dispatch": "🌐 외부전송"}
DEFAULT_GATES = {"finance_payment": False, "laptop_app_browser": True, "file_modify_delete": False, "external_dispatch": False}
CRITICAL = ("finance_payment", "file_modify_delete", "external_dispatch")
LOCK_MSG = "🔒 중요 결재 수동 스위치가 OFF(잠금) 상태입니다. 상단 수동 스위치를 ON으로 켜주셔야 작동합니다."
CAT_RE = {"finance_payment": re.compile(r"매수|매도|주문|결제|송금|이체|리밸런싱|배분|입금|출금"),
          "file_modify_delete": re.compile(r"삭제|지워|지우|이동|폴더|파일\s*정리"),
          "external_dispatch": re.compile(r"발송|배포|푸시|push|전송|업로드|설정\s*변경|메일", re.I)}
APPS = {"메모장": "notepad.exe", "notepad": "notepad.exe", "계산기": "calc.exe", "calc": "calc.exe",
        "탐색기": "explorer.exe", "explorer": "explorer.exe", "그림판": "mspaint.exe", "paint": "mspaint.exe"}
SITES = {"유튜브": "https://www.youtube.com", "youtube": "https://www.youtube.com", "구글": "https://www.google.com",
         "google": "https://www.google.com", "네이버": "https://www.naver.com", "naver": "https://www.naver.com"}

def _now(): return datetime.datetime.now().isoformat(timespec="seconds")

def _default():
    return {"version": VERSION, "antibody": ANTIBODY, "master_approval_on": False,
            "gates": dict(DEFAULT_GATES), "labels": GATE_LABELS, "history": [], "updated_at": _now()}

def load_state():
    for r in STATE_PATHS:
        try: j = json.loads((ROOT / r).read_text(encoding="utf-8"))
        except Exception: continue
        if isinstance(j, dict):
            s = _default(); s.update({k: v for k, v in j.items() if k != "gates"})
            g = j.get("gates") if isinstance(j.get("gates"), dict) else {}
            s["gates"] = {k: bool(g.get(k, v)) for k, v in DEFAULT_GATES.items()}
            s["master_approval_on"] = bool(s.get("master_approval_on"))
            return s
    return _default()

def save_state(s):
    s["version"], s["antibody"], s["labels"], s["updated_at"] = VERSION, ANTIBODY, GATE_LABELS, _now()
    txt = json.dumps(s, ensure_ascii=False, indent=2)
    for r in STATE_PATHS:
        p = ROOT / r; p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + ".tmp"); tmp.write_text(txt, encoding="utf-8"); os.replace(tmp, p)
    return s

def _change(event, fn):
    s = load_state(); fn(s)
    s["history"] = (list(s.get("history", [])) + [{"t": _now(), "event": event}])[-30:]
    return save_state(s)

def set_master_gate(on):
    return _change("master=" + ("ON" if on else "OFF"), lambda s: s.__setitem__("master_approval_on", bool(on)))

def set_category_gate(cat, on):
    if cat not in DEFAULT_GATES: raise ValueError(f"알 수 없는 카테고리: {cat}")
    return _change(f"{cat}=" + ("ON" if on else "OFF"), lambda s: s["gates"].__setitem__(cat, bool(on)))

def lock_all_gates():
    def f(s):
        s["master_approval_on"] = False; s["gates"] = {k: False for k in DEFAULT_GATES}
    return _change("LOCK_ALL", f)

def critical_categories(text): return [k for k, r in CAT_RE.items() if r.search(text or "")]

def critical_category(text):
    c = critical_categories(text)
    return c[0] if len(c) == 1 else "unknown"

def can_execute_critical(category, tier=3):
    s = load_state(); g, m = s["gates"], s["master_approval_on"]
    if category in g:
        need = tier >= 3 or category in CRITICAL
        ok = (m and g[category]) if need else g[category]
        req = ["master", category] if need else [category]
    else:
        ok = m and all(g[k] for k in CRITICAL); req = ["master"] + list(CRITICAL)
    return {"allowed": bool(ok), "category": category, "tier": tier, "requires": req, "master_approval_on": m,
            "gates": dict(g), "message": "✅ 수동 스위치 ON 확인 — 집행 가능합니다." if ok else LOCK_MSG}

def _count_files():
    n = 0
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]; n += len(fns)
    return n

def system_check():
    du = shutil.disk_usage(str(ROOT)); gb = 1024 ** 3
    rep = {"os": f"{platform.system()} {platform.release()}", "machine": platform.machine(),
           "python": platform.python_version(), "executable": sys.executable,
           "disk_total_gb": round(du.total / gb, 1), "disk_free_gb": round(du.free / gb, 1),
           "disk_free_pct": round(du.free * 100 / du.total, 1) if du.total else 0.0,
           "hq_files": _count_files(), "hq_path": str(ROOT), "checked_at": _now()}
    tip = " 여유 공간이 10% 아래라 정리가 필요해 보여요." if rep["disk_free_pct"] < 10 else " 여유 공간도 넉넉해요!"
    rep["speech"] = (f"대표님 노트북 점검 결과예요! {rep['os']}, 파이썬 {rep['python']}, 디스크 여유 "
                     f"{rep['disk_free_gb']}GB / {rep['disk_total_gb']}GB({rep['disk_free_pct']}%), 사령부 파일 {rep['hq_files']}개예요." + tip)
    return rep

def _ledger(rec, dry_run):
    if dry_run: return
    with open(LEDGER, "a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def _result(action, tier, ok, msg, **kw):
    d = {"action": action, "tier": tier, "ok": bool(ok), "message": msg, "executed": 0, "dry_run": True}
    d.update(kw); return d

def _open(what, is_url):
    if os.name == "nt":
        if is_url: os.startfile(what)
        else: subprocess.Popen([what])
    elif is_url:
        subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", what])
    else:
        raise OSError("Windows 기본 앱은 Windows에서만 열 수 있어요")

def execute_laptop_action(action_type, target="", dry_run=True, approved=False, category=None):
    t = str(target or "").strip()
    if action_type == "system_check":
        rep = system_check()
        return _result(action_type, 1, True, rep["speech"], report=rep, speech=rep["speech"], dry_run=dry_run)
    if action_type == "open_app_or_url":
        g = can_execute_critical("laptop_app_browser", tier=2)
        if not g["allowed"]:
            return _result(action_type, 2, False, "💻 노트북앱 스위치가 OFF라 열지 않았어요. 제어판에서 켜 주세요.", gate=g, dry_run=dry_run)
        key = t.lower()
        if re.match(r"^https?://[^\s\"'<>]+$", t, re.I): url, app = t, None
        else:
            url = SITES.get(key) or SITES.get(t)
            app = None if url else (APPS.get(key) or APPS.get(t))
        if not url and not app:
            return _result(action_type, 2, False, f"'{t}'은(는) 허용 목록에 없어 열지 않았어요. (메모장·계산기·탐색기·그림판 / 유튜브·구글·네이버 / http(s) 주소)", dry_run=dry_run)
        what = url or app
        if dry_run:
            return _result(action_type, 2, True, f"{t} 열 준비가 끝났어요! (안전 모드라 창은 띄우지 않았어요 · 실제 실행은 RGON_HANDS_LIVE=1)", prepared=what, dry_run=True)
        try: _open(what, bool(url))
        except Exception as e:
            return _result(action_type, 2, False, f"{t}을(를) 여는 중 문제가 생겼어요: {e}", prepared=what, dry_run=False)
        _ledger({"t": _now(), "action": action_type, "target": what}, False)
        return _result(action_type, 2, True, f"{t} 열어드렸어요! 💧", prepared=what, executed=1, dry_run=False)
    if action_type == "draft_file":
        name = re.sub(r"[^0-9A-Za-z가-힣_-]+", "_", t[:40]).strip("_") or "memo"
        p = DRAFT_DIR / f"draft_{datetime.datetime.now():%Y%m%d_%H%M%S}_{name}.md"
        k = 1
        while p.exists():
            p = p.with_name(p.stem + f"_{k}.md"); k += 1
        r_ = p.relative_to(ROOT).as_posix()
        if dry_run: return _result(action_type, 2, True, f"초안 파일 준비 완료: {r_}", path=r_, dry_run=True)
        DRAFT_DIR.mkdir(exist_ok=True)
        p.write_text(f"# 아온 초안 — {t}\n\n- 작성: {_now()} · {VERSION}\n\n(여기에 내용을 채워 주세요)\n", encoding="utf-8")
        return _result(action_type, 2, True, f"초안 파일을 만들었어요: {r_}", path=r_, executed=1, dry_run=False)
    if action_type == "critical_order_or_delete":
        cat = category or critical_category(t)
        g = can_execute_critical(cat, tier=3)
        if not g["allowed"]:
            return _result(action_type, 3, False, LOCK_MSG, allowed=False, gate=g, dry_run=dry_run)
        if not approved:
            return _result(action_type, 3, False, "✋ 스위치는 ON이지만 대표님 승인이 아직이에요. [✅ 승인 집행]을 눌러 주셔야 해요.",
                           allowed=True, gate=g, dry_run=dry_run)
        rec = {"t": _now(), "action": action_type, "target": t, "category": cat, "approved": True,
               "note": "집행 기록 전용 — 실제 주문/결제/삭제 API 미연결"}
        _ledger(rec, dry_run)
        return _result(action_type, 3, True, "✅ 수동 스위치 ON + 대표님 승인 확인! 집행 기록을 남겼어요. (실제 주문·삭제 API는 연결돼 있지 않아요)",
                       allowed=True, gate=g, record=rec, executed=0 if dry_run else 1, dry_run=dry_run)
    return _result(str(action_type), 0, False, f"알 수 없는 작업: {action_type}", dry_run=dry_run)

def self_test():
    ok = True
    def chk(c, m):
        nonlocal ok
        print(("  ✅ " if c else "  ❌ ") + m); ok = ok and bool(c)
    prev = load_state()
    try:
        save_state(_default())
        s = load_state()
        chk(s["master_approval_on"] is False, "기본 상태 master_approval_on == False")
        chk(s["gates"] == DEFAULT_GATES, "기본 4대 스위치 (금융 OFF · 노트북앱 ON · 파일 OFF · 외부 OFF)")
        for q, cat in (("삼성전자 10주 매수 주문", "finance_payment"), ("사령부 old 폴더 파일 삭제", "file_modify_delete")):
            chk(critical_category(q) == cat and not can_execute_critical(cat)["allowed"], f"OFF 상태 차단 게이트: {q}")
            r = execute_laptop_action("critical_order_or_delete", q, dry_run=True, approved=True)
            chk(r["allowed"] is False and r["executed"] == 0 and r["message"] == LOCK_MSG, f"승인 눌러도 집행 0건: {q}")
        set_category_gate("finance_payment", True)
        chk(not can_execute_critical("finance_payment")["allowed"], "세부 ON + 마스터 OFF → 여전히 차단")
        set_master_gate(True); set_category_gate("finance_payment", True)
        chk(can_execute_critical("finance_payment")["allowed"], "마스터 ON + 금융 ON → allowed == True")
        r = execute_laptop_action("critical_order_or_delete", "삼성전자 10주 매수 주문", dry_run=True, approved=True)
        chk(r["allowed"] and r["ok"], "수동 ON + 승인 → 집행 기록 정상")
        chk(not execute_laptop_action("critical_order_or_delete", "삼성전자 10주 매수 주문", dry_run=True)["ok"], "승인 없으면 미집행")
        chk(not can_execute_critical("file_modify_delete")["allowed"], "다른 카테고리 OFF는 계속 차단")
        chk(not can_execute_critical("unknown")["allowed"], "미분류 중요 결재는 전체 ON 필요")
        lock_all_gates(); s = load_state()
        chk(not s["master_approval_on"] and not any(s["gates"].values()), "lock_all_gates() 즉시 전체 OFF")
        chk(not execute_laptop_action("open_app_or_url", "메모장")["ok"], "잠금 시 노트북앱도 차단")
        set_category_gate("laptop_app_browser", True)
        chk(execute_laptop_action("open_app_or_url", "메모장")["ok"] and execute_laptop_action("open_app_or_url", "https://www.youtube.com")["ok"],
            "앱·URL 열기 준비 (dry-run, 창 안 띄움)")
        chk(not execute_laptop_action("open_app_or_url", "cmd /c del *")["ok"], "허용 목록 외 명령 거부")
        d = execute_laptop_action("draft_file", "유튜브 숏폼 대본")
        chk(d["ok"] and d["dry_run"] and not (ROOT / d["path"]).exists(), "초안 파일 dry-run (실제 생성 없음)")
        rep = system_check()
        chk(rep["disk_total_gb"] > 0 and rep["hq_files"] > 0 and "GB" in rep["speech"], "system_check 디스크·파일·파이썬")
    finally:
        prev["last_system_check"] = system_check()
        save_state(prev)
    for r in STATE_PATHS:
        try:
            j = json.loads((ROOT / r).read_text(encoding="utf-8"))
            chk(j.get("version") == VERSION and "master_approval_on" in j and len(j.get("gates", {})) == 4, f"JSON 무결성 {r}")
        except Exception as ex:
            chk(False, f"JSON 무결성 {r}: {ex!r}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    if "--self-test" in sys.argv: sys.exit(self_test())
    if "--lock" in sys.argv: print(json.dumps(lock_all_gates(), ensure_ascii=False, indent=2)); sys.exit(0)
    s = load_state(); s["last_system_check"] = system_check(); save_state(s)
    print(s["last_system_check"]["speech"])
    print(json.dumps({"master_approval_on": s["master_approval_on"], "gates": s["gates"]}, ensure_ascii=False))
'''

SKILL_MD = f"""# {SKILL_ID} (31번째 정식 스킬)

- 버전: {NEW_VER} · 항체: {NEW_R}
- 기관: 제11기관 노트북 만능 제어 수족 & 중요 결재 수동 ON/OFF 마스터 스위치 (`{HANDS_REL}`)
- 철학: 주역 #60 수택절(節, 마디의 절제) · #62 뇌산소과(小過, 작은 일은 열고 큰 일은 잠근다) · #14 화천대유(大有, 크게 가진 자의 겸손)

## 1. 수동 스위치
- `master_approval_on` 기본값은 False(🔒 철통잠금)입니다.
- `gates`: finance_payment(OFF) · laptop_app_browser(ON) · file_modify_delete(OFF) · external_dispatch(OFF)
- API: `set_master_gate(on)`, `set_category_gate(cat, on)`, `lock_all_gates()`
- 상태 파일: `rgon_manual_gate_state.json`, `docs/rgon_manual_gate_state.json`

## 2. 검증 게이트 `can_execute_critical(category, tier=3)`
- Tier 3 또는 중요 카테고리는 마스터 ON과 카테고리 ON이 모두 충족돼야 `allowed: True`입니다. 하나라도 OFF면 승인을 눌러도 집행 0건입니다.
- 카테고리가 여러 개 섞였거나 분류되지 않으면 `unknown`으로 보고, 마스터와 중요 3종이 모두 ON이어야 합니다.

## 3. 노트북 4대 작업 `execute_laptop_action(action_type, target, dry_run=True, approved=False)`
- system_check(T1): OS · 디스크 여유 · 사령부 파일 수 · 파이썬
- open_app_or_url(T2): 허용 목록 앱(메모장·계산기·탐색기·그림판), 사이트(유튜브·구글·네이버), http(s) 주소만 엽니다. 임의 명령은 거부합니다.
- draft_file(T2): `aon_drafts/` 아래에 초안을 생성합니다.
- critical_order_or_delete(T3): 스위치와 승인 3중 확인을 거칩니다. 실제 주문·삭제 API는 연결하지 않고, 집행 기록(`rgon_laptop_hands_ledger.jsonl`)만 남깁니다.

## 4. 대화·UI 연동
- 제10기관 분별기: `gate_control`(켜기는 마스터만, 끄기는 즉시 전체 잠금) · `laptop_check` · `laptop_open`
- 뮤즈: `approve` 계열 함수를 R35 게이트로 감쌉니다.
- HTML: `[RGON-GATE-V1]`. 상단 `🔒 결재수동 OFF ⇄ 🔓 결재수동 ON` 토글과 📋 보드의 🎛️ 제어판으로 구성되며, `[✅ 승인 집행]`은 캡처 단계에서 차단합니다.
"""

# ============================================================ 2) 제10기관 · 뮤즈 · 백혈구 주입
SOUL_PATCH = r'''
# [RGON-R35-HANDS-INJECT] — 제11기관 노트북 수족 & 중요 결재 수동 스위치 연동 (Step 35)
_R35_GOFF = re.compile(r"(?:중요\s*결재|결재|결제|수동)\s*(?:스위치)?\s*(?:를|을)?\s*(?:꺼|끄|off|잠가|잠궈|잠금)|전체\s*잠금|비상\s*잠금", re.I)
_R35_GON = re.compile(r"(?:결재|결제|수동)\s*스위치\s*(?:를|을)?\s*(?:켜|on)|중요\s*결재\s*허용", re.I)
_R35_LCHK = re.compile(r"노트북.*(?:상태|점검|용량|디스크|저장\s*공간|체크)|시스템\s*점검")
_R35_LOPEN = re.compile(r"(메모장|계산기|탐색기|그림판|유튜브|youtube|구글|google|네이버|naver|https?://\S+).*?(?:열어|켜|띄워|실행)", re.I)
_r35_classify0, _r35_converse0, _r35_selftest0 = classify_intent, converse, self_test

def _r35_hands():
    import rgon_laptop_hands as h
    return h

def classify_intent(text):
    t = (text or "").strip()
    if _R35_GOFF.search(t): return {"intent": "gate_control", "track": "hands", "tier": None, "action": "off"}
    if _R35_GON.search(t): return {"intent": "gate_control", "track": "hands", "tier": None, "action": "on"}
    if _R35_LCHK.search(t): return {"intent": "laptop_check", "track": "hands", "tier": 1}
    m = _R35_LOPEN.search(t)
    if m: return {"intent": "laptop_open", "track": "hands", "tier": 2, "target": m.group(1)}
    return _r35_classify0(t)

def converse(text, mem=None, persist=True, use_llm=True, live=None):
    t = (text or "").strip()
    c = classify_intent(t)
    if c["track"] != "hands":
        return _r35_converse0(t, mem=mem, persist=persist, use_llm=use_llm)
    h = _r35_hands()
    if mem is None: mem = load_memory()
    extra = {}
    if c["intent"] == "gate_control":
        if c["action"] == "off":
            st = h.lock_all_gates()
            reply = "🔒 알겠어요! 중요 결재 수동 스위치를 전부 꺼서 철통 잠금했어요. 대표님이 직접 켜시기 전까지 중요 결재는 0건 집행이에요."
        else:
            st = h.set_master_gate(True)
            reply = "🔓 중요 결재 마스터 스위치를 켰어요! 금융·파일·외부전송 세부 스위치는 결재 보드 제어판에서 대표님이 직접 눌러 주셔야 해요."
        extra["gate"] = {"master_approval_on": st["master_approval_on"], "gates": dict(st["gates"])}
    elif c["intent"] == "laptop_check":
        r = h.execute_laptop_action("system_check", "")
        reply = r["speech"]; extra["system"] = r["report"]
    else:
        if live is None: live = os.environ.get("RGON_HANDS_LIVE") == "1"
        r = h.execute_laptop_action("open_app_or_url", c["target"], dry_run=not live)
        reply = r["message"]; extra["action"] = r
    res = {"input": t, "intent": c["intent"], "category": c["intent"], "track": "hands", "tier": c["tier"],
           "version": VERSION, "source": "hands", "reply": reply}
    res.update(extra)
    remember(mem, t, res)
    res.update({"speech": reply, "affection": mem["affection_score"], "level": level(mem["affection_score"])})
    if persist: save_memory(mem)
    return res

def self_test():
    rc0 = _r35_selftest0()
    ok = rc0 == 0
    def chk(cond, msg):
        nonlocal ok
        print(("  ✅ " if cond else "  ❌ ") + msg); ok = ok and bool(cond)
    print("  — Step 35 제11기관 연동 —")
    for q, want, act in (("결재 스위치 켜줘", "gate_control", "on"), ("수동 스위치 ON", "gate_control", "on"),
                         ("중요 결재 허용", "gate_control", "on"), ("결재 스위치 꺼줘", "gate_control", "off"),
                         ("수동 스위치 OFF", "gate_control", "off"), ("전체 잠금", "gate_control", "off"),
                         ("결제 잠가줘", "gate_control", "off"), ("내 노트북 상태 점검해줘", "laptop_check", None),
                         ("노트북 용량 어때?", "laptop_check", None), ("메모장 열어줘", "laptop_open", None),
                         ("유튜브 열어줘", "laptop_open", None), ("결재 보드 열어줘", "muse", None),
                         ("유튜브 숏폼 대본 초안 작성해줘", "delegate", None), ("대표님 사랑해", "chat_love", None)):
        c = classify_intent(q)
        chk(c["intent"] == want and (act is None or c.get("action") == act),
            f"분별: {q} → {c['intent']}" + (f" ({c.get('action')})" if c.get("action") else ""))
    h = _r35_hands()
    snap = {r_: ((ROOT / r_).read_bytes() if (ROOT / r_).exists() else None) for r_ in h.STATE_PATHS}
    try:
        converse("결재 스위치 꺼줘", mem=_default_mem(), persist=False, use_llm=False)
        s = h.load_state()
        chk(not s["master_approval_on"] and not any(s["gates"].values()), "대화 명령 → 즉시 전체 잠금")
        r = converse("결재 스위치 켜줘", mem=_default_mem(), persist=False, use_llm=False)
        chk(h.load_state()["master_approval_on"] and not h.can_execute_critical("finance_payment")["allowed"],
            "대화 명령 → 마스터만 ON (세부 OFF면 여전히 차단)")
        chk("payload" not in r, "스위치 명령은 대행 큐 payload 없음")
        r = converse("노트북 용량 어때?", mem=_default_mem(), persist=False, use_llm=False)
        chk(r["intent"] == "laptop_check" and "GB" in r["reply"], "노트북 점검 다정한 브리핑")
        h.set_category_gate("laptop_app_browser", True)
        r = converse("메모장 열어줘", mem=_default_mem(), persist=False, use_llm=False, live=False)
        chk(r["intent"] == "laptop_open" and r["action"]["ok"] and r["action"]["dry_run"], "메모장 열기 (안전 dry-run)")
    finally:
        for r_, b in snap.items():
            p = ROOT / r_
            if b is None:
                if p.exists(): p.unlink()
            else:
                p.write_bytes(b)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1
'''

MUSE_PATCH = r'''
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
'''

def wbc_patch(code, text):
    return f'''
# [RGON-{code}-INJECT] — DEFAULT_ANTIBODIES {code} 복제 주입
try:
    _RX = {text!r}
    if isinstance(DEFAULT_ANTIBODIES, dict):
        DEFAULT_ANTIBODIES.setdefault("{code}", _RX)
    elif isinstance(DEFAULT_ANTIBODIES, list) and not any("{code}" in str(_x) for _x in DEFAULT_ANTIBODIES):
        _s = DEFAULT_ANTIBODIES[-1] if DEFAULT_ANTIBODIES else None
        if isinstance(_s, dict):
            _n = {{k: v for k, v in _s.items()}}
            for _k in list(_n):
                if _k in ("id", "code", "key"): _n[_k] = "{code}"
                elif _k in ("text", "desc", "description", "rule", "name", "title"): _n[_k] = _RX
            DEFAULT_ANTIBODIES.append(_n)
        elif isinstance(_s, (list, tuple)):
            DEFAULT_ANTIBODIES.append(type(_s)(["{code}", _RX] + list(_s[2:])))
        else:
            DEFAULT_ANTIBODIES.append(_RX)
except NameError:
    DEFAULT_ANTIBODIES = {{"{code}": {text!r}}}
'''

MAIN_RE = re.compile(r"^if\s+__name__\s*==\s*['\"]__main__['\"]\s*:", re.M)

def inject_before_main(s, marker, patch):
    if marker in s: return s
    m = MAIN_RE.search(s)
    return (s[:m.start()] + patch.lstrip("\n") + "\n" + s[m.start():]) if m else s.rstrip() + "\n" + patch

# ============================================================ 3) HTML 게이트 블록
GATE_BLOCK = r"""<!-- [RGON-GATE-V1-START] -->
<style id="rgon-gate-v1-css">
.rgg-off{background:#e3f5ee!important;color:#0f5e4a!important;border:1px solid #7cc9b3!important}
.rgg-on{background:#ffe7a8!important;color:#7a4b00!important;border:1px solid #f0b429!important}
#rgg-panel{position:fixed;top:10px;left:50%;transform:translateX(-50%);z-index:2147483550;background:#132033;color:#e8eef7;border-radius:16px;padding:10px 14px;box-shadow:0 10px 30px rgba(0,0,0,.35);font:13px/1.45 system-ui,sans-serif;width:min(94vw,470px);display:none}
#rgg-panel.on{display:block}
#rgg-panel .rgg-row{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
#rgg-panel button{border:0;border-radius:999px;padding:6px 11px;cursor:pointer;font-size:12.5px}
#rgg-badge{margin-left:6px;padding:2px 8px;border-radius:999px;font-size:12px}
#rgg-warn{display:none;margin-top:8px;padding:8px 10px;border-radius:10px;background:#ffe0e0;color:#8a1010;font-weight:600}
#rgg-warn.on{display:block}
#rgg-float{position:fixed;right:14px;bottom:110px;z-index:2147483500;border-radius:14px;padding:6px 10px;cursor:pointer}
</style>
<div id="rgg-panel" role="region" aria-label="중요 결재 수동 ON/OFF 마스터 제어판">
<div style="display:flex;justify-content:space-between;align-items:center;gap:8px"><b>🎛️ 중요 결재 수동 ON/OFF 마스터 제어판<span id="rgg-badge" class="rgg-off">🔒 중요결재 OFF</span></b><button data-rgg="hide" style="background:#24344d;color:#cfe">✕</button></div>
<div class="rgg-row"><button data-rgg="master" id="rgg-master" class="rgg-off">🔒 전체 중요결재 수동 OFF</button><button data-rgg="lock" style="background:#ffd6d6;color:#8a1010">🚨 비상 전체 잠금</button></div>
<div class="rgg-row"><button data-rgg-cat="finance_payment">💰 금융·결제</button><button data-rgg-cat="laptop_app_browser">💻 노트북앱</button><button data-rgg-cat="file_modify_delete">🗂️ 파일삭제·이동</button><button data-rgg-cat="external_dispatch">🌐 외부전송</button></div>
<div id="rgg-warn">⛔ 현재 중요 결재 수동 스위치가 [OFF 잠금] 상태입니다! 위 수동 스위치를 직접 [ON]으로 켜주셔야 집행됩니다.</div>
<div style="opacity:.7;margin-top:6px;font-size:12px">Tier 3 [✅ 승인 집행]은 마스터 + 해당 세부 스위치가 모두 ON일 때만 통과해요. 상태는 이 기기(localStorage)에 저장돼요.</div>
</div>
<script id="rgon-gate-v1-js">
(function(){
if(window.RGON_GATE)return;
var VER="v11.34-AON-LAPTOP-HANDS",KEY="rgon_manual_gate";
var LABEL={finance_payment:"💰 금융·결제",laptop_app_browser:"💻 노트북앱",file_modify_delete:"🗂️ 파일삭제·이동",external_dispatch:"🌐 외부전송"};
var CRIT=["finance_payment","file_modify_delete","external_dispatch"];
var st={master_approval_on:false,gates:{finance_payment:false,laptop_app_browser:true,file_modify_delete:false,external_dispatch:false}};
try{var s0=JSON.parse(localStorage.getItem(KEY)||"null");if(s0&&s0.gates){st.master_approval_on=!!s0.master_approval_on;for(var k in st.gates)if(k in s0.gates)st.gates[k]=!!s0.gates[k]}}catch(e){}
function save(){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}}
var WARN="⛔ 현재 중요 결재 수동 스위치가 [OFF 잠금] 상태입니다! 위 수동 스위치를 직접 [ON]으로 켜주셔야 집행됩니다.";
var FIN=/매수|매도|주문|결제|송금|이체|리밸런싱|배분|입금|출금/,FILE=/삭제|지워|지우|이동|폴더|파일\s*정리/,DISP=/발송|배포|푸시|push|전송|업로드|설정\s*변경|메일/i;
function V(){return window.RGON_VOICE||null}
function fx(t){var v=V();if(v&&v.sfx)v.sfx(t)}
function say(s){var r=document.getElementById("rgv-reply");if(r)r.textContent="💧 "+s;var v=V();if(v&&v.speak)v.speak(s)}
function catsOf(t){t=String(t||"");var r=[];if(FIN.test(t))r.push("finance_payment");if(FILE.test(t))r.push("file_modify_delete");if(DISP.test(t))r.push("external_dispatch");return r}
function can(cats){if(!cats||!cats.length)cats=CRIT.slice();var ok=st.master_approval_on&&cats.every(function(c){return!!st.gates[c]});return{allowed:!!ok,categories:cats,message:ok?"":WARN}}
var panel=document.getElementById("rgg-panel"),warn=document.getElementById("rgg-warn"),mb=document.getElementById("rgg-master"),bd=document.getElementById("rgg-badge");
function paint(){var on=st.master_approval_on;mb.textContent=on?"🔓 전체 중요결재 수동 ON":"🔒 전체 중요결재 수동 OFF";mb.className=on?"rgg-on":"rgg-off";
bd.textContent=on?"🔓 중요결재 ON":"🔒 중요결재 OFF";bd.className=on?"rgg-on":"rgg-off";
panel.querySelectorAll("[data-rgg-cat]").forEach(function(b){var c=b.getAttribute("data-rgg-cat"),v=st.gates[c];b.textContent=LABEL[c]+(v?" ON":" OFF");b.className=v?"rgg-on":"rgg-off"});
document.querySelectorAll("[data-rgg-dock]").forEach(function(b){b.textContent=on?"🔓 결재수동 ON":"🔒 결재수동 OFF";b.title=on?"🔓 중요결재 ON":"🔒 중요결재 OFF";b.classList.toggle("rgg-on",on);b.classList.toggle("rgg-off",!on)});
if(on)warn.classList.remove("on")}
function show(){paint();panel.classList.add("on")}
function setMaster(on){st.master_approval_on=!!on;save();paint();fx(on?"approve_fanfare":"clean_sweep");
say(on?"중요 결재 수동 스위치가 켜졌어요! 집행 전에 한 번 더 확인해 주세요.":"중요 결재 수동 스위치가 꺼졌어요! 이제 중요 결재는 철통 잠금이에요.")}
function setCat(c,on){if(!(c in st.gates))return;st.gates[c]=!!on;save();paint();fx("waterdrop_pop");say(LABEL[c].replace(/^\S+\s/,"")+" 스위치가 "+(on?"켜졌어요!":"꺼졌어요!"))}
function lockAll(){st.master_approval_on=false;for(var k in st.gates)st.gates[k]=false;save();paint();fx("clean_sweep");say("비상 전체 잠금! 중요 결재 수동 스위치를 모두 껐어요.")}
function blocked(){show();warn.classList.add("on");fx("radar_ping");say("현재 중요 결재 수동 스위치가 OFF 잠금 상태예요. 위 수동 스위치를 직접 ON으로 켜주셔야 집행돼요.")}
panel.addEventListener("click",function(e){var c=e.target.closest("[data-rgg-cat]");if(c){var k=c.getAttribute("data-rgg-cat");setCat(k,!st.gates[k]);return}
var b=e.target.closest("[data-rgg]");if(!b)return;var a=b.getAttribute("data-rgg");
if(a==="master")setMaster(!st.master_approval_on);else if(a==="lock")lockAll();else if(a==="hide")panel.classList.remove("on")});
window.addEventListener("click",function(e){var t=e.target;if(!t||!t.closest)return;var b=t.closest("button,a,[role=button]");
if(!b||b.closest("#rgg-panel")||b.closest("#rgv-modal"))return;var x=b.textContent||"";
if(/승인\s*집행/.test(x)){var n=b,ct="";for(var i=0;i<3&&n.parentElement;i++){n=n.parentElement;if((n.textContent||"").length>400)break;ct=n.textContent||""}
var r=can(catsOf(ct||x));if(!r.allowed){e.preventDefault();e.stopImmediatePropagation();blocked();return}
say("수동 스위치 ON 확인! 대표님 승인으로 집행할게요.");return}
if(/📋/.test(x)&&!b.hasAttribute("data-rgg-dock"))setTimeout(show,0)},true);
var wt=0,wv=setInterval(function(){var M=window.RGON_MUSE;if(M&&!M.__rgg){try{M.__rgg=1;
if(M.open){var o=M.open;M.open=function(){var r=o.apply(this,arguments);show();return r}}
if(M.close){var cl=M.close;M.close=function(){panel.classList.remove("on");return cl.apply(this,arguments)}}
if(M.approve){var ap=M.approve;M.approve=function(id){var tk=null;try{(M.tasks?M.tasks():[]).forEach(function(z){if(z&&(z.id===id||z.task_id===id))tk=z})}catch(e){}
var tier=tk?(+tk.tier||0):3;if(tier>=3){var r=can(catsOf(JSON.stringify(tk||id)));if(!r.allowed){blocked();return{ok:false,allowed:false,executed:0,message:WARN}}}
return ap.apply(this,arguments)}}}catch(e){}clearInterval(wv)}else if(++wt>40)clearInterval(wv)},250);
var GOFF=/(?:중요\s*결재|결재|결제|수동)\s*(?:스위치)?\s*(?:를|을)?\s*(?:꺼|끄|off|잠가|잠궈|잠금)|전체\s*잠금|비상\s*잠금/i,
GON=/(?:결재|결제|수동)\s*스위치\s*(?:를|을)?\s*(?:켜|on)|중요\s*결재\s*허용/i,
LCHK=/노트북.*(?:상태|점검|용량|디스크|저장\s*공간|체크)|시스템\s*점검/,
LOPEN=/(메모장|계산기|탐색기|그림판|유튜브|youtube|구글|google|네이버|naver|https?:\/\/\S+).*?(?:열어|켜|띄워|실행)/i;
var SITES={"유튜브":"https://www.youtube.com","youtube":"https://www.youtube.com","구글":"https://www.google.com","google":"https://www.google.com","네이버":"https://www.naver.com","naver":"https://www.naver.com"};
var LTXT="노트북 디스크와 파일 점검은 사령부 엔진에서 해요. python rgon_laptop_hands.py 를 실행해 주시면 바로 알려드릴게요!";
function hook(t){t=String(t||"");
if(GOFF.test(t)){lockAll();return true}
if(GON.test(t)){st.master_approval_on=true;save();show();fx("approve_fanfare");say("중요 결재 마스터 스위치를 켰어요! 세부 스위치는 제어판에서 대표님이 직접 눌러 주셔야 해요.");return true}
if(LCHK.test(t)){fetch("rgon_manual_gate_state.json",{cache:"no-store"}).then(function(r){return r.json()}).then(function(j){var s=j&&j.last_system_check;
say(s&&s.speech?s.speech+" (점검 시각 "+String(s.checked_at||"").replace("T"," ")+")":LTXT)}).catch(function(){say(LTXT)});return true}
var m=t.match(LOPEN);if(m){if(!st.gates.laptop_app_browser){show();say("노트북앱 스위치가 꺼져 있어요. 제어판에서 켜 주시면 열어드릴게요.");return true}
var w=m[1],url=/^https?:/i.test(w)?w:(SITES[w]||SITES[w.toLowerCase()]);
if(url){window.open(url,"_blank","noopener");fx("waterdrop_pop");say(w+" 열어드렸어요!")}else say(w+"은 노트북 엔진 rgon_laptop_hands.py 에서 열 수 있어요.");return true}
return false}
function dock(){if(document.querySelector("[data-rgg-dock]"))return true;var bs=document.querySelectorAll("button,a,[role=button]"),hide=null;
for(var i=0;i<bs.length;i++){if(/🙈/.test(bs[i].textContent)&&!bs[i].closest("#rgv-modal,#rgg-panel")){hide=bs[i];break}}
if(!hide)return false;var b=hide.cloneNode(false);b.removeAttribute("id");b.removeAttribute("onclick");b.setAttribute("data-rgg-dock","1");
b.addEventListener("click",function(e){e.preventDefault();e.stopPropagation();setMaster(!st.master_approval_on);show()});hide.parentNode.insertBefore(b,hide);paint();return true}
var tr=0,iv=setInterval(function(){if(dock()||++tr>40){clearInterval(iv);if(!document.querySelector("[data-rgg-dock]")){var f=document.createElement("button");f.id="rgg-float";f.setAttribute("data-rgg-dock","1");
f.onclick=function(){setMaster(!st.master_approval_on);show()};document.body.appendChild(f);paint()}}},250);
paint();
window.RGON_GATE={version:VER,state:function(){return JSON.parse(JSON.stringify(st))},can:function(t){return can(catsOf(t))},setMaster:setMaster,setCategory:setCat,lockAll:lockAll,show:show,hook:hook};
var hv=0,hi=setInterval(function(){var v=window.RGON_VOICE;if(v&&v.talk&&!v.__rgg){var t0=v.talk;v.__rgg=1;v.talk=function(t){if(hook(t))return;return t0.apply(this,arguments)};clearInterval(hi)}else if(++hv>40)clearInterval(hi)},250);
})();
</script>
<!-- [RGON-GATE-V1-END] -->
"""

GS, GE = b"<!-- [RGON-GATE-V1-START] -->", b"<!-- [RGON-GATE-V1-END] -->"
TOKENS = {"aon": (b"rgyt-wrap", b"aon-roamer"), "clean": ("🧹".encode(),), "muse": (b"[RGON-MUSE-V1",),
          "muse_btn": ("📋대행".encode(),), "voice": (b"[RGON-VOICE-V1-START]",), "voice_btn": ("🎙️음성".encode(),)}
REQUIRED_INNER = [GS, GE, "🔒 결재수동 OFF".encode(), "🔓 결재수동 ON".encode(), "🎛️ 중요 결재 수동 ON/OFF 마스터 제어판".encode(),
                  "💰 금융·결제".encode(), "💻 노트북앱".encode(), "🗂️ 파일삭제·이동".encode(), "🌐 외부전송".encode(),
                  "OFF 잠금".encode(), b"stopImmediatePropagation", b"rgon_manual_gate"]

def tokens(b): return {k: any(x in b for x in v) for k, v in TOKENS.items()}

def patch_html(p):
    b = p.read_bytes(); sp = v13_span(b)
    if not sp: return None
    before, pre_tok = outside_hash(b), tokens(b)
    inner = b[sp[0]:sp[1]]
    if b"[RGON-VOICE-V1-START]" in inner:
        inner = inner.replace(b"v11.33-AON-SOUL-BRAIN", NEW_VER.encode())
        b = b[:sp[0]] + inner + b[sp[1]:]; sp = v13_span(b)
    blk = GATE_BLOCK.encode("utf-8")
    i = b.find(GS, sp[0], sp[1])
    if i >= 0:
        j = b.find(GE, i, sp[1])
        if j < 0: raise RuntimeError(f"GATE 블록 END 마커 누락: {rel(p)}")
        nb = b[:i] + blk.rstrip(b"\n") + b[j + len(GE):]
    else:
        nb = b[:sp[2]] + blk + b[sp[2]:]
    if outside_hash(nb) != before: raise RuntimeError(f"V13 바깥 해시 변경 위험: {rel(p)}")
    changed = write_bytes(p, nb)
    return {"before": before, "pre_tok": pre_tok, "changed": changed, "upgrade": i >= 0}

# ============================================================ 4) 동기화
HEAD_RE = re.compile(r"^\s{0,3}#{1,6}\s")
HIST_HEAD_RE = re.compile(r"(?i)\bstep\s*\d+")
HIST_LINE_RE = re.compile(r"(?i)\bstep\s*3[1-4]\b|STEP3[1-4]")

def sync_text(s, md=False):
    out, in_hist = [], False
    for line in s.splitlines(keepends=True):
        if md:
            if HEAD_RE.match(line): in_hist = bool(HIST_HEAD_RE.search(line)) and NEW_VER not in line
            if in_hist or (HIST_LINE_RE.search(line) and NEW_VER not in line):
                out.append(line); continue
        line = line.replace(OLD_VER, NEW_VER).replace(OLD_R, NEW_R)
        line = SKC_RE.sub(r"\g<1>31", line)
        line = ABC_RE.sub(r"\g<1>35", line)
        if re.search(r"(?i)스킬|skill", line): line = re.sub(r"(?<!\d)30개", "31개", line)
        line = re.sub(r"\[\s*30\s*,\s*30\s*,\s*30\s*\]", "[31, 31, 31]", line)
        out.append(line)
    return "".join(out)

def sync_py():
    for r in PY_SYNC:
        p = ROOT / r
        if not p.exists(): log(f"  ⚠️ 없음(건너뜀): {r}"); continue
        s = sync_text(rd(p))
        if r == "rgon_daily_cycle.py":
            s = re.sub(r"(EXPECTED_SKILL_COUNT\s*(?::\s*int\s*)?=\s*)\d+", r"\g<1>31", s)
        if r == SOUL_REL: s = inject_before_main(s, "[RGON-R35-HANDS-INJECT]", SOUL_PATCH)
        if r == MUSE_REL: s = inject_before_main(s, "[RGON-R35-GATE-INJECT]", MUSE_PATCH)
        if r == WBC_REL: s = inject_before_main(s, "[RGON-R35-INJECT]", wbc_patch("R35", R35_TEXT))
        if write_text(p, s): log(f"  🔁 {r}")

CONST_35 = (f"\n\n## 제35조 (아온 노트북 만능 수족 & 중요 결재 수동 ON/OFF 마스터 스위치 원칙) — {NEW_VER}\n"
            "- 제1항: 중요 결재(Tier 3 · 금융·결제 · 파일 삭제·이동 · 외부 전송·배포)는 마스터 스위치와 해당 세부 스위치가 "
            "대표님 손으로 모두 ON이고 대표님이 승인했을 때만 집행한다. 하나라도 OFF면 집행 0건이다.\n"
            "- 제2항: 기본값은 마스터 OFF(철통잠금)이며, '전체 잠금' 명령은 즉시 모든 스위치를 OFF로 돌린다.\n"
            "- 제3항: 대화 명령으로는 마스터만 켤 수 있고, 세부 스위치는 제어판에서 직접 켠다.\n"
            "- 제4항: 노트북 제어는 허용 목록 앱과 http(s) 주소만 열며, 임의 명령 문자열은 실행하지 않는다.\n")

def fix_index_header(s):
    lines = s.splitlines(keepends=True)
    for i, ln in enumerate(lines):
        if HEAD_RE.match(ln) and re.search(r"\b30\b", ln):
            lines[i] = re.sub(r"\b30\b", "31", ln, count=1); break
    return "".join(lines)

def sync_md():
    for r in MD_SYNC:
        p = ROOT / r
        if not p.exists(): log(f"  ⚠️ 없음(건너뜀): {r}"); continue
        s = sync_text(rd(p), md=True)
        if r == "CONSTITUTION.md" and "제35조" not in s: s = s.rstrip() + CONST_35
        if r == "ANTIBODY_REGISTRY.md" and "R35:" not in s: s = s.rstrip() + f"\n- {R35_TEXT}\n"
        if r == "skills/SKILL_INDEX.md":
            s = fix_index_header(s)
            s = s.replace("정식 스킬 총 **30개**", "정식 스킬 총 **31개**")
            if SKILL_ID not in s:
                s = s.rstrip() + f"\n31. **{SKILL_ID}** — 노트북 만능 수족 + 중요 결재 수동 ON/OFF 마스터 스위치 (`{SKILL_REL}`, {NEW_VER})\n"
        if r == "CODE_MAP.md" and HANDS_REL not in s:
            s = s.rstrip() + f"\n- `{HANDS_REL}` — 제11기관 노트북 만능 제어 수족 & 중요 결재 수동 스위치 ({NEW_R})\n"
        if r == "GLOSSARY.md" and "수동 마스터 스위치" not in s:
            s = s.rstrip() + "\n- **수동 마스터 스위치**: `master_approval_on` + 4대 `gates`. 모두 ON이어야 중요 결재가 집행된다 (R35)\n"
        if r == "RGON_MORNING_BRIEF.md" and "Step 35" not in s:
            s = s.rstrip() + f"\n\n## Step 35 — {NEW_VER}\n- 제11기관 노트북 수족 & 중요 결재 수동 스위치 장착 · 항체 {NEW_R} · 정식 스킬 {NEW_SK}개\n"
        if write_text(p, s): log(f"  🔁 {r}")

def deep(o):
    if isinstance(o, dict): return {k: deep(v) for k, v in o.items()}
    if isinstance(o, list): return [deep(v) for v in o]
    if isinstance(o, str): return o.replace(OLD_VER, NEW_VER).replace(OLD_R, NEW_R)
    return o

def load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception: return {}

def sync_json():
    p = ROOT / "skills/SKILL_INDEX.json"; j = deep(load(p))
    sk = j.get("skills") if isinstance(j.get("skills"), list) else []
    existing_by_slug = {}
    for item in sk:
        if isinstance(item, dict):
            k = item.get("slug") or item.get("id") or Path(item.get("path", "")).parent.name
            if k: existing_by_slug[k] = item
    all_skill_dirs = sorted(d.parent.name for d in (ROOT / "skills").glob("*/SKILL.md"))
    merged_skills = []
    for slug in all_skill_dirs:
        if slug in existing_by_slug:
            merged_skills.append(existing_by_slug[slug])
        else:
            merged_skills.append({"id": slug, "slug": slug, "name": slug, "path": f"skills/{slug}/SKILL.md", "version": NEW_VER})
    j["skills"] = merged_skills
    j["count"] = len(merged_skills); j["total_skills"] = len(merged_skills); j["skill_count"] = len(merged_skills); j["total"] = len(merged_skills)
    j["version"] = NEW_VER; j["antibody"] = NEW_R; j["antibody_range"] = NEW_R; j["antibodies"] = NEW_R; j["immune"] = NEW_R
    write_text(p, json.dumps(j, ensure_ascii=False, indent=2) + "\n")
    p = ROOT / "rgon_morning_brief.json"; j = deep(load(p))
    j.update({"version": NEW_VER, "antibodies": NEW_R, "skills": NEW_SK})
    write_text(p, json.dumps(j, ensure_ascii=False, indent=2) + "\n")
    p = ROOT / "rgon_immune_ledger.json"
    if p.exists():
        j = deep(load(p)); j["version"] = NEW_VER
        write_text(p, json.dumps(j, ensure_ascii=False, indent=2) + "\n")

def sync_wbc_golden_and_preserve():
    saved_bytes = {r: (ROOT / r).read_bytes() for r in CHANGED if (ROOT / r).exists()}
    lp = ROOT / "rgon_immune_ledger.json"
    if lp.exists():
        try:
            lj = json.loads(lp.read_text(encoding="utf-8"))
            def _upd_hashes(obj):
                if isinstance(obj, dict):
                    for k, v in list(obj.items()):
                        if isinstance(v, str) and len(v) == 64 and (ROOT / k).is_file():
                            obj[k] = sha((ROOT / k).read_bytes())
                        elif isinstance(v, dict) and "sha256" in v and (ROOT / k).is_file():
                            b = (ROOT / k).read_bytes()
                            v["sha256"] = sha(b)
                            if "size" in v: v["size"] = len(b)
                        else:
                            _upd_hashes(v)
                elif isinstance(obj, list):
                    for x in obj: _upd_hashes(x)
            _upd_hashes(lj)
            lj["version"] = NEW_VER
            lj["antibody_range"] = NEW_R
            lp.write_text(json.dumps(lj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except Exception:
            pass
    for bdir_name in (".rgon_backup", ".wbc_golden", ".golden"):
        bdir = ROOT / bdir_name
        if bdir.is_dir():
            for r, b in saved_bytes.items():
                for cand in (bdir / r, bdir / Path(r).name):
                    if cand.is_file():
                        try: cand.write_bytes(b)
                        except Exception: pass
    return saved_bytes

def triad_counts():
    a = len(list((ROOT / "skills").glob("*/SKILL.md")))
    j = load(ROOT / "skills/SKILL_INDEX.json")
    b = j.get("total_skills", j.get("count"))
    if isinstance(j.get("skills"), (list, dict)) and len(j["skills"]) != b: b = f"{b}≠len {len(j['skills'])}"
    m = re.search(r"^\s*EXPECTED_SKILL_COUNT\s*(?::\s*int\s*)?=\s*(\d+)", rd(ROOT / "rgon_daily_cycle.py"), re.M)
    return [a, b, int(m.group(1)) if m else None]

def run(cmd, timeout=300):
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return 99, repr(e)

def git_push():
    rc, o = run(["git", "add", "-A", "--", "."] + GIT_EXCLUDES); log("  ➕ add -A " + ("OK" if rc == 0 else o.strip()[-200:]))
    rc, o = run(["git", "commit", "-m", f"Step 35 {NEW_VER}: 제11기관 노트북 수족 & 중요 결재 수동 ON/OFF 스위치 ({NEW_R}, 스킬 {NEW_SK})"])
    log("  📦 commit " + ("OK" if rc == 0 else o.strip()[-200:]))
    if rc != 0: return
    rc, o = run(["git", "fetch", "origin"]); log("  🔄 fetch " + ("OK" if rc == 0 else o.strip()[-200:]))
    rc, o = run(["git", "pull", "--no-rebase", "origin"])
    if rc != 0: log("  ⛔ pull 실패 — push 중단 (로컬 커밋 유지): " + o.strip()[-200:]); return
    rc, o = run(["git", "push", "origin"]); log("  🚀 push " + ("OK" if rc == 0 else o.strip()[-200:]))

# ============================================================ main
def execute():
    global PRE
    log(f"🚀 Step 35 {NEW_VER} 시작 (dry={DRY})")
    if not (ROOT / "rgon_daily_cycle.py").exists(): log("❌ 저장소 루트가 아닙니다."); return 2
    PRE = snapshot()
    htmls = [ROOT / h for h in HTML_TARGETS if (ROOT / h).exists() and v13_span((ROOT / h).read_bytes())]
    log(f"🔎 V13 HTML {len(htmls)}/{len(HTML_TARGETS)}개 발견")
    if len(htmls) != len(HTML_TARGETS):
        log("❌ 누락: " + ", ".join(h for h in HTML_TARGETS if ROOT / h not in htmls)); return 3

    # [A] 모든 쓰기
    write_text(ROOT / HANDS_REL, HANDS_SRC); log(f"  🆕 {HANDS_REL}")
    write_text(ROOT / SKILL_REL, SKILL_MD); log(f"  🆕 {SKILL_REL}")
    hres = {}
    for p in htmls:
        r = patch_html(p); hres[rel(p)] = r
        log(f"  💉 {rel(p)} {'업그레이드' if r['upgrade'] else '신규 장착'}{'' if r['changed'] else ' (변경 없음)'}")
    sync_py(); sync_md(); sync_json()
    if DRY: log(f"🧪 dry-run 종료: 변경 예정 {len(CHANGED)}개"); return 0
    prepare_extras()

    # [B] 기관 self-test
    c1, outs = [], {}
    for name, f in (("laptop_hands", HANDS_REL), ("soul_brain", SOUL_REL), ("voice_organ", VOICE_REL)):
        if not (ROOT / f).exists(): c1.append((f"{name} 존재", False)); outs[name] = ""; continue
        rc, o = run([sys.executable, f, "--self-test"]); outs[name] = o
        c1.append((f"{name} --self-test rc={rc}", rc == 0))
    for r_, h in hres.items():
        b = (ROOT / r_).read_bytes(); sp = v13_span(b); inner = b[sp[0]:sp[1]] if sp else b""
        ok = bool(sp) and outside_hash(b) == h["before"] and inner.count(GS) == 1
        ok = ok and all(x in inner for x in REQUIRED_INNER)
        tk = tokens(b); ok = ok and all(tk[k] for k, v in h["pre_tok"].items() if v)
        c1.append((f"HTML {r_}", ok))

    # [C] 백혈구 self-test 및 Step 35 변경본 보존
    saved_step35 = sync_wbc_golden_and_preserve()
    rc, o = run([sys.executable, WBC_REL, "--self-test"]); outs["white_blood_cell"] = o
    c1.append((f"white_blood_cell --self-test rc={rc}", rc == 0))
    for r_, b_ in saved_step35.items():
        if (ROOT / r_).exists() and (ROOT / r_).read_bytes() != b_:
            (ROOT / r_).write_bytes(b_)
    sync_wbc_golden_and_preserve()
    s1 = all(x[1] for x in c1)

    # ② 보호 파일
    after = snapshot()
    allowed = set(CHANGED) | set(EXTRAS)
    viol = sorted(k for k in set(PRE) | set(after) if k not in allowed and PRE.get(k) != after.get(k)
                  and not k.startswith("aon_drafts/"))
    s2 = not viol
    # ③ 스킬·항체
    sc = triad_counts()
    s3 = sc == [31, 31, 31] and "[RGON-R35-INJECT]" in rd(ROOT / WBC_REL) and "R35:" in rd(ROOT / "ANTIBODY_REGISTRY.md") \
         and f"31. **{SKILL_ID}**" in rd(ROOT / "skills/SKILL_INDEX.md")
    score = sum([s1, s2, s3])
    log(f"① 기능 {'✅' if s1 else '❌'} | ② 보호 {'✅' if s2 else '❌'}({len(viol)}건) | ③ 스킬 {sc} 항체 {'✅' if s3 else '❌'} → 삼성 {score}/3")

    rep = [f"# STEP35 LAPTOP HANDS REPORT — {NEW_VER}", "", f"- 일시: {TS}", f"- 항체: {NEW_R} · 정식 스킬: {sc}",
           f"- 삼성(三省): **{score}/3**", f"- 백업: `{rel(BACKUP) if BACKUP.exists() else '(없음)'}`", "", "## ① 기능 검증"]
    rep += [f"- {'✅' if ok else '❌'} {n}" for n, ok in c1]
    rep += ["", "## ② 비대상 보호 파일", f"- 해시 변경 {len(viol)}건"] + [f"  - ❌ {v}" for v in viol]
    rep += ["", "## ③ 스킬·항체", f"- 스킬 {sc} (기대 [31, 31, 31])", f"- {R35_TEXT}", "", "## 변경 파일"]
    rep += [f"- `{c}`" for c in sorted(CHANGED)]
    for k, o in outs.items(): rep += ["", f"## {k}", "```", o.strip()[-2000:], "```"]
    if score != 3:
        print("\n".join(rep[:35]))
        for name, ok in c1:
            if not ok and name.split()[0] in outs:
                print(f"=== FAILED OUTPUT: {name} ===")
                print(outs[name.split()[0]])
        rollback(f"삼성 {score}/3 미달"); return 1

    (ROOT / REPORT_REL).write_text("\n".join(rep) + "\n", encoding="utf-8"); CREATED.add(REPORT_REL)
    log(f"  📝 {REPORT_REL}")
    if not NO_GIT and (ROOT / ".git").exists(): git_push()
    return 0

def main():
    try:
        rc = execute()
    except Exception as e:
        import traceback; traceback.print_exc()
        if not DRY: rollback(f"예외 {e!r}")
        rc = 9
    if not NO_MSG and os.name == "nt" and not DRY:
        msg = f"Step 35 {NEW_VER} {'완료 3/3' if rc == 0 else '실패 rc=' + str(rc) + ' (자동 원복)'} · {NEW_R} · 스킬 31".replace("'", "")
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        f"Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('{msg}','RGON 제11기관')"],
                       capture_output=True)
    return rc

if __name__ == "__main__":
    sys.exit(main())

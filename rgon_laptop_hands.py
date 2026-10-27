#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_laptop_hands.py — 제11기관: 아온(A-ON) 노트북 만능 제어 수족 & 중요 결재 수동 ON/OFF 마스터 스위치
버전 v11.58-AON-LIVE-BRAIN-MOTION · 항체 R1~R57
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

VERSION = "v11.58-AON-LIVE-BRAIN-MOTION"
ANTIBODY = "R1~R57"
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
        tmp = p.with_name(p.name + ".tmp")
        try:
            tmp.write_text(txt, encoding="utf-8")
            written = False
            for _ in range(5):
                try:
                    os.replace(tmp, p)
                    written = True
                    break
                except PermissionError:
                    time.sleep(0.05)
            if not written:
                p.write_text(txt, encoding="utf-8")
                if tmp.exists():
                    tmp.unlink(missing_ok=True)
        except Exception:
            try:
                p.write_text(txt, encoding="utf-8")
            except Exception:
                pass
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

# -*- coding: utf-8 -*-
# agentshield:ignore-file  (정규식 정의 파일 — 오탐 방지 자기 제외)
# rgon_spec_ticket_Shield.py — RGON v11.21-CIRCULATION / 항체 R21
# Matt Pocock to-spec/to-tickets 분업기 + ECC AgentShield 보안 백혈구 (표준 라이브러리 전용)
import os, re, sys, json, time, shutil, tempfile
VERSION = "v11.22-OMNI-UI"
ANTIBODY_RANGE = "R1~R23"
ROOT = os.path.dirname(os.path.abspath(__file__))
EXCLUDE = {".git", "__pycache__", "node_modules", ".venv", "venv", ".rgon_backup", ".rgon_backups", ".idea", ".vscode", "backups", "archive", "old_backups"}
AI_ROLES = {"르곤": "설계/검증", "Claude": "구현", "GPT": "구조", "Grok": "트렌드"}
ROLE_KEYS = [("Grok", ("트렌드", "레이더", "유튜브", "채널", "radar", "trend")),
             ("GPT", ("구조", "스키마", "아키텍처", "schema", "architecture")),
             ("르곤", ("설계", "검증", "리뷰", "spec", "verify", "review"))]
SECRET_RULES = [
    ("openai_api_key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("github_pat", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9-]+")),
    ("telegram_bot_token", re.compile(r"(?<![0-9])[0-9]{8,10}:[A-Za-z0-9_-]{35}(?![A-Za-z0-9_-])"))]
TAMPER_RULES = [
    ("guard_disabled", re.compile(r"[\"']?(protected|protect_ui|hash_guard|wbc_enabled|agentshield_enabled)[\"']?\s*:\s*false", re.I)),
    ("guard_bypassed", re.compile(r"[\"']?(allow_ui_edit|skip_hash_check|disable_wbc|bypass_guard|allow_protected_write)[\"']?\s*:\s*true", re.I))]
SCAN_EXT = (".py", ".json", ".md", ".yml", ".yaml")
SELF_SKIP = {"rgon_spec_ticket_shield.py", "rgon_agentshield_report.json", "s_run.py"}

def rd(p):
    with open(p, "r", encoding="utf-8-sig", errors="replace") as f: return f.read()
def wr(p, s):
    if os.path.dirname(p): os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f: f.write(s)
def wj(p, o): wr(p, json.dumps(o, ensure_ascii=False, indent=2) + "\n")
def mask(s): return s[:6] + "***(" + str(len(s)) + ")"
def load_glossary(root):
    p = os.path.join(root, "GLOSSARY.md")
    if not os.path.exists(p): return []
    return [m.group(1).strip() for m in re.finditer(r"^\|\s*\*\*(.+?)\*\*\s*\|", rd(p), re.M)]

class SpecTicketDecomposer:
    def __init__(self, root=ROOT): self.root, self.terms = root, load_glossary(root)
    def assign(self, text):
        low = text.lower()
        for ai, keys in ROLE_KEYS:
            if any(k.lower() in low for k in keys): return ai + ":" + AI_ROLES[ai]
        return "Claude:구현"
    def link_terms(self, text):
        return [t for t in self.terms if t.split("(")[0].strip() and t.split("(")[0].strip() in text]
    def decompose(self, goal, steps, prefix="T"):
        tickets = []
        for i, st in enumerate(steps, 1):
            st = st if isinstance(st, dict) else {"title": str(st)}
            tid, title = st.get("id") or "%s%02d" % (prefix, i), st.get("title", "")
            dep = st.get("blocked_by")
            if dep is None: dep = [tickets[-1]["id"]] if tickets else []
            tickets.append({"id": tid, "title": title, "owner": st.get("owner") or self.assign(title),
                            "blocked_by": list(dep), "glossary": self.link_terms(title),
                            "demo_path": st.get("demo_path") or tid + " 증빙: 산출물 존재 + self-test PASS",
                            "status": st.get("status", "todo")})
        self.check_cycle(tickets)
        return tickets
    def check_cycle(self, tickets):
        g, state = {t["id"]: t["blocked_by"] for t in tickets}, {}
        def dfs(n):
            if state.get(n) == 1: raise ValueError("순환 의존성 탐지: " + n)
            if state.get(n) == 2 or n not in g: return
            state[n] = 1
            for m in g[n]: dfs(m)
            state[n] = 2
        for n in g: dfs(n)
    def frontier(self, tickets):
        done = {t["id"] for t in tickets if t["status"] == "done"}
        return [t for t in tickets if t["status"] != "done" and all(b in done for b in t["blocked_by"])]
    def save(self, goal, tickets):
        jp = os.path.join(self.root, "rgon_active_tickets.json")
        if os.path.exists(jp):
            try:
                old = {t["id"]: t.get("status") for t in json.loads(rd(jp)).get("tickets", [])}
                for t in tickets: t["status"] = old.get(t["id"]) or t["status"]
            except Exception: pass
        fr = [t["id"] for t in self.frontier(tickets)]
        wj(jp, {"version": VERSION, "goal": goal, "goal_glossary": self.link_terms(goal),
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"), "frontier": fr, "tickets": tickets})
        rows = ["# TICKETS_BOARD — " + goal, "", "> " + VERSION + " · Matt Pocock Spec & Tracer-Bullet Tickets", "",
                "| ID | 제목 | 담당 | 선행(blocked_by) | 검증(demo_path) | 용어 | 상태 |", "|---|---|---|---|---|---|---|"]
        for t in tickets:
            rows.append("| %s | %s | %s | %s | %s | %s | %s |" % (t["id"], t["title"], t["owner"],
                        ", ".join(t["blocked_by"]) or "-", t["demo_path"], ", ".join(t["glossary"]) or "-", t["status"]))
        rows += ["", "## Frontier (즉시 실행 가능)", ""] + ["- " + f for f in fr]
        wr(os.path.join(self.root, "TICKETS_BOARD.md"), "\n".join(rows) + "\n")
        return fr

class AgentShieldScanner:
    def __init__(self, root=ROOT): self.root = root
    def files(self):
        for dp, dns, fns in os.walk(self.root):
            dns[:] = [d for d in dns if d not in EXCLUDE and not d.startswith(".rgon_backup")]
            for fn in fns:
                low = fn.lower()
                if low.endswith(SCAN_EXT) and low not in SELF_SKIP and not low.startswith("step"):
                    yield os.path.join(dp, fn)
    def scan(self, write=True, strict_mode=False):
        findings, n = [], 0
        for p in self.files():
            try:
                if os.path.getsize(p) > 3 * 1024 * 1024: continue
                txt = rd(p)
            except Exception: continue
            if "agentshield:ignore-file" in txt[:400]: continue
            n += 1
            rel, cfg = os.path.relpath(p, self.root), p.lower().endswith((".json", ".yml", ".yaml"))
            for i, line in enumerate(txt.splitlines(), 1):
                if "agentshield:ignore" in line: continue
                for rule, rx in SECRET_RULES:
                    for m in rx.finditer(line):
                        sev = "critical" if strict_mode else "advisory"
                        findings.append({"file": rel, "line": i, "rule": rule, "severity": sev, "preview": mask(m.group(0))})
                for rule, rx in (TAMPER_RULES if cfg else []):
                    m = rx.search(line)
                    if m:
                        sev = "high" if strict_mode else "advisory"
                        findings.append({"file": rel, "line": i, "rule": rule, "severity": sev, "preview": mask(m.group(0))})
        crit = sum(1 for f in findings if f["severity"] == "critical")
        high = sum(1 for f in findings if f["severity"] == "high")
        adv = sum(1 for f in findings if f["severity"] == "advisory")
        rep = {"version": VERSION, "scanned_at": time.strftime("%Y-%m-%d %H:%M:%S"), "files_scanned": n,
               "critical": crit, "high": high, "advisory": adv, "clean": crit == 0, "findings": findings}
        if write: wj(os.path.join(self.root, "rgon_agentshield_report.json"), rep)
        return rep

def default_plan():
    return "Step 21 @Mindung-EasyAI 양분 흡수", [
        {"id": "S21-01", "title": "GLOSSARY.md 도메인 공유 언어 15선 설계", "blocked_by": []},
        {"id": "S21-02", "title": "티켓 스키마·작업 그래프 구조 정의", "blocked_by": ["S21-01"]},
        {"id": "S21-03", "title": "SpecTicketDecomposer + AgentShield 구현", "blocked_by": ["S21-02"]},
        {"id": "S21-04", "title": "@Mindung-EasyAI 트렌드 레이더 채널 등록", "blocked_by": []},
        {"id": "S21-05", "title": "영양분 소화 → SKILL.md 4종 주조", "blocked_by": ["S21-04"]},
        {"id": "S21-06", "title": "백혈구(WBC) R21 순찰 + 보호 파일 304 삼성 해시 검증", "blocked_by": ["S21-03", "S21-05"]}]

def self_test():
    tmp, checks = tempfile.mkdtemp(prefix="rgon_s21_"), []
    try:
        wr(os.path.join(tmp, "GLOSSARY.md"), "| **백혈구(WBC)** | 순찰 |\n| **AgentShield** | 보안 |\n")
        d = SpecTicketDecomposer(tmp)
        t = d.decompose("백혈구 보강", [{"id": "A", "title": "백혈구 스펙 설계", "blocked_by": []},
                                        {"id": "B", "title": "AgentShield 구현", "blocked_by": ["A"]},
                                        {"id": "C", "title": "트렌드 레이더", "blocked_by": ["A"]}])
        checks.append(("Frontier 초기", [x["id"] for x in d.frontier(t)] == ["A"]))
        checks.append(("AI 담당 배정", t[0]["owner"].startswith("르곤") and t[1]["owner"].startswith("Claude") and t[2]["owner"].startswith("Grok")))
        checks.append(("GLOSSARY 연결", "백혈구(WBC)" in t[0]["glossary"]))
        t[0]["status"] = "done"
        checks.append(("Frontier 병렬", sorted(x["id"] for x in d.frontier(t)) == ["B", "C"]))
        try:
            d.decompose("c", [{"id": "X", "title": "x", "blocked_by": ["Y"]}, {"id": "Y", "title": "y", "blocked_by": ["X"]}])
            checks.append(("순환 탐지", False))
        except ValueError: checks.append(("순환 탐지", True))
        d.save("백혈구 보강", t)
        checks.append(("보드/JSON 생성", all(os.path.exists(os.path.join(tmp, f)) for f in ("TICKETS_BOARD.md", "rgon_active_tickets.json"))))
        wr(os.path.join(tmp, "leak.py"), 'KEY = "' + "sk-" + "Z" * 24 + '"\nTG = "' + "123456789:" + "A" * 35 + '"\n')
        wr(os.path.join(tmp, "safe.py"), 'K = "' + "ghp_" + "Q" * 24 + '"  # agentshield:ignore\n')
        wr(os.path.join(tmp, "cfg.json"), '{"skip_hash_check": true}')
        rep = AgentShieldScanner(tmp).scan(write=False, strict_mode=True)
        checks.append(("비밀키·설정 탐지", sorted(f["rule"] for f in rep["findings"]) == ["guard_bypassed", "openai_api_key", "telegram_bot_token"]))
        checks.append(("마스킹", all("***" in f["preview"] for f in rep["findings"])))
    except Exception as e: checks.append(("예외 " + repr(e), False))
    finally: shutil.rmtree(tmp, ignore_errors=True)
    for n, ok in checks: print(("  [PASS] " if ok else "  [FAIL] ") + n)
    ok = all(c[1] for c in checks)
    print("SELF-TEST %s (%d/%d)" % ("PASS" if ok else "FAIL", sum(c[1] for c in checks), len(checks)))
    return 0 if ok else 1

def main(argv):
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
    a = argv[1] if len(argv) > 1 else "--status"
    if a == "--self-test": return self_test()
    if a == "--run":
        goal, steps = default_plan(); d = SpecTicketDecomposer(ROOT)
        fr = d.save(goal, d.decompose(goal, steps))
        rep = AgentShieldScanner(ROOT).scan(write=True, strict_mode=False)
        print("Frontier:", ", ".join(fr))
        print("AgentShield: files=%d critical=%d advisory=%d" % (rep["files_scanned"], rep["critical"], rep.get("advisory", 0)))
        for f in rep["findings"][:10]: print("  - [%s] %s:%d %s %s" % (f["severity"], f["file"], f["line"], f["rule"], f["preview"]))
        return 0
    if a == "--status":
        for f in ("GLOSSARY.md", "rgon_active_tickets.json", "TICKETS_BOARD.md", "rgon_agentshield_report.json"):
            print(("  [O] " if os.path.exists(os.path.join(ROOT, f)) else "  [X] ") + f)
        print("  GLOSSARY 용어:", len(load_glossary(ROOT)), "/ 버전:", VERSION)
        return 0
    print("사용법: --run | --self-test | --status"); return 1

# [RGON-STEP22-AUTOVERIFY-HOOK-START] (R22: 티켓 저장 후 실제 산출물 기반 자동 승격)
import sys as _rg_sys, os as _rg_os, atexit as _rg_atexit
if __name__ == '__main__' and '--run' in _rg_sys.argv:
    def _rg_autoverify():
        try:
            _rg_sys.path.insert(0, _rg_os.path.dirname(_rg_os.path.abspath(__file__)))
            import rgon_vascular_core as _rg_core
            print('[R22 Auto-Verify]', _rg_core.auto_verify_tickets())
        except Exception as _e:
            print('[R22 Auto-Verify] 경고:', _e)
    _rg_atexit.register(_rg_autoverify)
# [RGON-STEP22-AUTOVERIFY-HOOK-END]

if __name__ == "__main__":
    sys.exit(main(sys.argv))

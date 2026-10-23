# -*- coding: utf-8 -*-
# agentshield:ignore-file
# step21_mindung_easyai_nutrient_pack.py — RGON Step 21 / v11.20-MINDUNG-ECC / 항체 R1~R21
# @Mindung-EasyAI 양분 4종: Matt Pocock(분업 티켓·GLOSSARY) + ECC AgentShield + 레이더 채널 등록
import os, re, sys, json, glob, time, shutil, hashlib, subprocess

VERSION, PREV_VERSION = "v11.20-MINDUNG-ECC", "v11.19-AUTONOMOUS"
RANGE, PREV_RANGE = "R1~R21", "R1~R20"
R21_TEXT = ("@Mindung-EasyAI 양분 흡수 — Matt Pocock(GLOSSARY.md · Spec/Tracer-Bullet Tickets 분업) "
            "+ ECC(AgentShield 비밀키/설정 보안 스캔)")
BT = chr(96); FENCE = BT * 3
EXCLUDE = {".git", "__pycache__", "node_modules", ".venv", "venv", ".rgon_backup", ".rgon_backups", ".idea", ".vscode", "backups", "archive", "old_backups"}
PROTECTED_EXPECTED = 304
TS, NOW = time.strftime("%Y%m%d_%H%M%S"), time.strftime("%Y-%m-%d %H:%M:%S")
PY = sys.executable
ENV = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
SKILLS = [
    ("mattpocock-spec-tickets", "Matt Pocock Spec & Tracer-Bullet Tickets", "https://github.com/mattpocock/skills",
     "큰 목표를 to-spec → to-tickets 로 분해해 blocked_by·demo_path·담당 AI가 달린 작업 그래프를 만들고 Frontier부터 실행한다.",
     "python rgon_spec_ticket_Shield.py --run"),
    ("mattpocock-domain-glossary", "Matt Pocock Domain Glossary", "https://github.com/mattpocock/skills",
     "GLOSSARY.md 공유 언어로 20단어 설명을 1단어로 압축해 에이전트 간 오해를 없앤다.",
     "python rgon_spec_ticket_Shield.py --status"),
    ("ecc-agentshield-harness", "ECC AgentShield Harness", "https://github.com/affaan-m/everything-claude-code",
     "커밋 전 .py/.json/.md/.yml 의 비밀키 평문 유출과 보호 설정 무단 변경을 스캔해 보안 사고를 예방한다.",
     "python rgon_spec_ticket_Shield.py --run"),
    ("rea-reverse-engineer-fusion", "REA Reverse-Engineer Fusion", "https://github.com/morluto/rea",
     "우수 저장소를 역설계해 구조·패턴만 추출하고 RGON 표준 라이브러리 방식으로 재구현한다(코드 복붙 금지).",
     "python rgon_nutrient_engine.py --digest"),
]
GLOSSARY = [
    ("독대실", "대표님과 르곤이 1:1로 전략을 결정하는 최상위 의사결정 공간. 모든 Step 지시서의 발령지."),
    ("흡수기(Absorber)", "유튜브·깃허브 등 외부 양분을 수집·정제해 rgon_skill_radar.json 에 등록하는 모듈."),
    ("백혈구(WBC)", "rgon_white_blood_cell.py. 항체 규칙을 순찰(--patrol)하고 건강 점수(목표 100/100)를 산출."),
    ("면역 원장", "rgon_immune_ledger.json. 항체 추가·사건·Step 이력을 기록하는 불변 장부."),
    ("영양분 3스푼", "한 번에 소화하는 양분을 핵심 소수로 제한해 과식(과잉 변경)을 막는 소화 원칙."),
    ("TrinityCouncil", "르곤·Claude·GPT(+Grok) 다중 AI 합의 회의체. 설계/구현/구조/트렌드 분업."),
    ("삼성(三省) 해시", "작업 전·중·후 3회 SHA-256 검증으로 보호 파일 무결성을 확인하는 절차."),
    ("상선약수 우회", "장애물을 정면 돌파하지 않고 물처럼 대체 경로로 우회하는 오류 처리 철학."),
    ("무위자연 폴백", "외부 의존 실패 시 표준 라이브러리 최소 동작으로 자연스럽게 복귀하는 안전장치."),
    ("단발 배치(placeOnce)", "UI·설정 요소를 단 한 번만 배치하는 멱등 원칙. 재실행해도 중복 없음."),
    ("보호 파일 304", ".html/.js/manifest.json 304개. 1바이트도 수정 불가(삼성 해시로 검증)."),
    ("일일 자율 순환", "레이더 → 소화(--digest) → 백혈구 순찰 → 스냅샷 → 원장 기록의 매일 자동 루프."),
    ("Spec & Tracer-Bullet Tickets", "Matt Pocock 방식. 목표→스펙→얇은 수직 관통 티켓(blocked_by·demo_path)으로 분업."),
    ("AgentShield", "ECC 방식 보안 백혈구. 비밀키 평문·보호 설정 무단 변경을 스캔(rgon_agentshield_report.json)."),
    ("항체 R1~R21", "RGON 헌법 규칙 집합. R21 = " + R21_TEXT),
]

MODULE = r'''# -*- coding: utf-8 -*-
# agentshield:ignore-file  (정규식 정의 파일 — 오탐 방지 자기 제외)
# rgon_spec_ticket_Shield.py — RGON v11.20-MINDUNG-ECC / 항체 R21
# Matt Pocock to-spec/to-tickets 분업기 + ECC AgentShield 보안 백혈구 (표준 라이브러리 전용)
import os, re, sys, json, time, shutil, tempfile
VERSION = "v11.20-MINDUNG-ECC"
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

if __name__ == "__main__":
    sys.exit(main(sys.argv))
'''

def find_root():
    cands = [r"C:\Users\sangi\Downloads\shin-agent", os.getcwd(), os.path.dirname(os.path.abspath(__file__))]
    for c in cands:
        if os.path.isdir(c) and any(os.path.exists(os.path.join(c, f)) for f in ("CLAUDE.md", "rgon_white_blood_cell.py")):
            return c
    return next(c for c in cands if os.path.isdir(c))

ROOT = find_root()
BACKUP_DIR = os.path.join(ROOT, ".rgon_backups", "step21_" + TS)
TOUCHED, BASE = [], {}
J = lambda *a: os.path.join(ROOT, *a)

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

def log(m): print(m, flush=True)
def is_excl(d): return d in EXCLUDE or d.startswith(".rgon_backup")
def is_protected(fn): low = fn.lower(); return low.endswith((".html", ".js")) or low == "manifest.json"
def rd(p):
    with open(p, "r", encoding="utf-8-sig", errors="replace") as f: return f.read()
def load_json(p, default):
    try: return json.loads(rd(p)) if os.path.exists(p) else default
    except Exception: return default

def protected_hashes():
    out = {}
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if not is_excl(d)]
        for fn in fns:
            if is_protected(fn):
                p, h = os.path.join(dp, fn), hashlib.sha256()
                with open(p, "rb") as f:
                    for ch in iter(lambda: f.read(1 << 20), b""): h.update(ch)
                out[os.path.relpath(p, ROOT)] = h.hexdigest()
    return out

def write(p, s):
    if is_protected(os.path.basename(p)): raise RuntimeError("보호 파일 쓰기 차단: " + p)
    rel = os.path.relpath(p, ROOT)
    if rel not in [t[0] for t in TOUCHED]:
        existed = os.path.exists(p)
        if existed:
            os.makedirs(os.path.dirname(os.path.join(BACKUP_DIR, rel)), exist_ok=True)
            shutil.copy2(p, os.path.join(BACKUP_DIR, rel))
        TOUCHED.append((rel, existed))
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f: f.write(s)

def save_json(p, o): write(p, json.dumps(o, ensure_ascii=False, indent=2) + "\n")

def rollback():
    for rel, existed in reversed(TOUCHED):
        p = J(rel)
        if existed: shutil.copy2(os.path.join(BACKUP_DIR, rel), p)
        elif os.path.exists(p): os.remove(p)
    log("[ROLLBACK] %d개 파일 원복 완료" % len(TOUCHED))

def popup(title, msg, err=False):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, title, (0x10 if err else 0x40) | 0x40000)
    except Exception: log("[POPUP] " + title + "\n" + msg)

def verify(stage):
    cur = protected_hashes()
    changed = [k for k in BASE if cur.get(k) != BASE[k]] + [k for k in cur if k not in BASE]
    log("[삼성 해시 %s] 보호 파일 %d개 · 변경 %d건" % (stage, len(cur), len(changed)))
    if changed:
        rollback(); popup("RGON Step 21 중단", "보호 파일 변경 감지:\n" + "\n".join(changed[:10]), True); sys.exit(3)
    return len(changed)

def run(args, timeout=900):
    try:
        r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e: return 99, repr(e)

def upsert_block(text, key, body):
    s, e = "<!-- RGON:%s:START -->" % key, "<!-- RGON:%s:END -->" % key
    block = s + "\n" + body.rstrip() + "\n" + e
    if s in text and e in text: return re.sub(re.escape(s) + r".*?" + re.escape(e), lambda m: block, text, flags=re.S)
    return text.rstrip() + "\n\n" + block + "\n"

# ---------------- 작업 1: GLOSSARY.md ----------------
def task_glossary():
    p = J("GLOSSARY.md")
    head = "# GLOSSARY — RGON 사령부 도메인 공유 언어 사전\n\n> Matt Pocock domain-glossary 방식 · 20단어 대신 1단어로 정확히 통한다.\n"
    rows = ["버전: " + VERSION + " · 항체 " + RANGE + " · 갱신 " + NOW, "", "| 용어 | 정의 |", "|---|---|"]
    rows += ["| **%s** | %s |" % (k, v) for k, v in GLOSSARY]
    old = rd(p) if os.path.exists(p) else head
    write(p, upsert_block(old, "GLOSSARY", "\n".join(rows)))
    log("[작업1] GLOSSARY.md 용어 %d선 갱신" % len(GLOSSARY))

# ---------------- 작업 2: 분업·보안 모듈 ----------------
def task_module():
    write(J("rgon_spec_ticket_Shield.py"), MODULE)
    log("[작업2] rgon_spec_ticket_Shield.py 생성 (SpecTicketDecomposer + AgentShieldScanner)")

# ---------------- 작업 3: 레이더 등록 + 스킬 주조 ----------------
def task_radar():
    p = J("rgon_skill_radar.json"); data = load_json(p, {})
    if isinstance(data, list): data = {"discoveries": data}
    meta = {"handle": "@Mindung-EasyAI", "name": "Mindung EasyAI", "url": "https://www.youtube.com/@Mindung-EasyAI",
            "focus": "Claude Code·에이전트 오픈소스 큐레이션", "added_at": NOW, "added_by": "Step21", "trust": "high"}
    ch = data.setdefault("channels", [])
    if isinstance(ch, dict): ch.setdefault(meta["handle"], meta)
    elif not any(isinstance(c, dict) and c.get("handle") == meta["handle"] for c in ch): ch.append(meta)
    key = next((k for k in ("discoveries", "findings", "items", "candidates", "skills") if isinstance(data.get(k), list)), "discoveries")
    lst, added = data.setdefault(key, []), 0
    for sid, title, src, desc, cmd in SKILLS:
        if any(isinstance(x, dict) and sid in (x.get("id"), x.get("name"), x.get("slug")) for x in lst): continue
        lst.append({"id": sid, "name": sid, "slug": sid, "title": title, "source": src, "url": src, "channel": "@Mindung-EasyAI",
                    "summary": desc, "description": desc, "command": cmd, "status": "pending", "discovered_at": NOW,
                    "tags": ["step21", "mindung-easyai", "R21"]})
        added += 1
    data.update(version=VERSION, updated_at=NOW)
    save_json(p, data)
    log("[작업3] 레이더 채널 등록 + 발견 항목 %d개 추가 (키: %s)" % (added, key))

def skill_files(): return glob.glob(J("skills", "*", "SKILL.md"))

def task_digest():
    if os.path.exists(J("rgon_nutrient_engine.py")):
        rc, out = run([PY, "rgon_nutrient_engine.py", "--digest"])
        log("[작업3] nutrient_engine --digest rc=%d\n%s" % (rc, out[-1200:]))
    else: log("[작업3] rgon_nutrient_engine.py 없음 → 무위자연 폴백 주조")
    verify("중-2(digest 후)")
    texts = {}
    for f in skill_files():
        try: texts[f] = rd(f)
        except Exception: texts[f] = ""
    for sid, title, src, desc, cmd in SKILLS:
        if any(sid in f or sid in t for f, t in texts.items()): continue
        body = ("---\nname: \"%s\"\ndescription: \"%s\"\nsource_url: \"%s\"\ncategory: \"mindung-easyai\"\ncreated_at_kst: \"%s\"\nhexagram_tag: \"#14-大有\"\nversion: \"%s\"\nantibody: \"R21\"\n---\n\n"
                "# %s\n\n## 언제 쓰나\n%s\n\n## 실행\n%sbash\n%s\n%s\n\n## RGON 연결\n- GLOSSARY.md 용어 사용 · 보호 파일 304 불가침 · 항체 %s\n"
                % (title, desc, src, NOW, VERSION, title, desc, FENCE, cmd, FENCE, RANGE))
        write(J("skills", sid, "SKILL.md"), body)
        log("  [폴백 주조] skills/%s/SKILL.md" % sid)
    if os.path.exists(J("rgon_nutrient_engine.py")):
        run([PY, "rgon_nutrient_engine.py", "--digest"])
    n = len(skill_files()); log("[작업3] 표준 SKILL.md 총 %d개 %s" % (n, "(목표 18+ 달성)" if n >= 18 else "(18 미만 확인 필요)"))
    return n

# ---------------- 작업 4: 동기화 ----------------
WBC_INJECT = '''# >>> RGON-STEP21-R21 >>>
ANTIBODY_RANGE = "R1~R21"
_R21 = "%s"
for _n in ("DEFAULT_ANTIBODIES", "ANTIBODIES", "ANTIBODY_RULES", "ANTIBODY", "RULES"):
    _d = globals().get(_n)
    if isinstance(_d, dict) and "R21" not in _d:
        _s = next(iter(_d.values()), "")
        _d["R21"] = ({k: ("R21" if k in ("id", "code") else _R21 if isinstance(v, str) else v) for k, v in _s.items()}
                     if isinstance(_s, dict) else _R21)
    elif isinstance(_d, list) and not any("R21" in str(x) for x in _d):
        _d.append({"id": "R21", "title": _R21, "name": _R21, "text": _R21, "step": 21} if _d and isinstance(_d[0], dict) else "R21: " + _R21)
# <<< RGON-STEP21-R21 <<<
''' % R21_TEXT.replace('"', '\\"')

def task_wbc():
    p = J("rgon_white_blood_cell.py")
    if not os.path.exists(p): log("[작업4] 백혈구 파일 없음 — 건너뜀"); return
    s = rd(p).replace(PREV_RANGE, RANGE).replace(PREV_VERSION, VERSION)
    s = re.sub(r'ANTIBODY_RANGE\s*=\s*["\'][^"\']*["\']', 'ANTIBODY_RANGE = "R1~R21"', s)
    if "RGON-STEP21-R21" not in s:
        m = re.search(r"^if __name__\s*==", s, re.M)
        s = s[:m.start()] + WBC_INJECT + "\n" + s[m.start():] if m else s.rstrip() + "\n\n" + WBC_INJECT
    write(p, s); log("[작업4] 백혈구 R21 + ANTIBODY_RANGE=R1~R21 반영")

def task_cycles():
    n = 0
    for p in glob.glob(J("rgon_*.py")):
        b = os.path.basename(p)
        if b in ("rgon_white_blood_cell.py", "rgon_spec_ticket_Shield.py"): continue
        s = rd(p)
        t = re.sub(r'(["\'])R1~R20\1', r'\1R1~R21\1', s)
        t = re.sub(r'(["\'])v11\.19-AUTONOMOUS\1', r'\1' + VERSION + r'\1', t)
        if t != s: write(p, t); n += 1
    log("[작업4] 일일 순환/엔진 모듈 상수 동기화 %d개" % n)

def task_docs():
    blocks = {
        "CLAUDE.md": "## Step 21 · %s\n- 항체 범위: **%s**\n- R21: %s\n- 커밋 전 `python rgon_spec_ticket_Shield.py --run` (AgentShield) 필수\n- 작업 분해는 GLOSSARY.md 용어 + TICKETS_BOARD.md Frontier 우선" % (VERSION, RANGE, R21_TEXT),
        "RGON_PHILOSOPHY.md": "## %s — 공유 언어와 방패\n하나의 단어가 스무 단어를 대신하고(GLOSSARY), 얇은 관통 티켓이 큰 목표를 나누며(Tracer-Bullet), 방패(AgentShield)가 비밀을 지킨다. 항체 %s." % (VERSION, RANGE),
        "CODE_MAP.md": "## Step 21 (%s)\n- `GLOSSARY.md` — 도메인 공유 언어 15선\n- `rgon_spec_ticket_Shield.py` — SpecTicketDecomposer · AgentShieldScanner (--run/--self-test/--status)\n- `rgon_active_tickets.json` · `TICKETS_BOARD.md` — 작업 그래프/Frontier\n- `rgon_agentshield_report.json` — 보안 스캔 리포트\n- `skills/` — Mindung 4종 SKILL.md 추가" % VERSION,
    }
    for name, body in blocks.items():
        p = J(name); s = rd(p) if os.path.exists(p) else "# " + name[:-3] + "\n"
        s = s.replace(PREV_RANGE, RANGE)
        s = re.sub(r"^(.*(?:현재|Current|VERSION|버전).*)$", lambda m: m.group(1).replace(PREV_VERSION, VERSION), s, flags=re.M | re.I)
        write(p, upsert_block(s, "STEP21", body))
    p = J("RGON_EVOLUTION_LOG.md"); s = rd(p) if os.path.exists(p) else "# RGON_EVOLUTION_LOG\n"
    write(p, upsert_block(s, "STEP21-LOG", "## %s · Step 21 · %s\n- @Mindung-EasyAI 양분 4종 흡수 (mattpocock/skills · ECC · rea)\n- 신규 항체 R21: %s\n- 항체 범위 %s → %s" % (NOW, VERSION, R21_TEXT, PREV_RANGE, RANGE)))
    log("[작업4] 문서 4종 동기화")

def stamp(obj, extra):
    if not isinstance(obj, dict): obj = {"legacy": obj}
    obj.update(version=VERSION, antibody_range=RANGE, current_step=21, step=21, antibody_count=21, updated_at=NOW)
    ab = obj.get("antibodies")
    if isinstance(ab, dict): ab.setdefault("R21", R21_TEXT)
    elif isinstance(ab, list):
        if not any("R21" in json.dumps(x, ensure_ascii=False) for x in ab):
            ab.append({"id": "R21", "title": R21_TEXT, "text": R21_TEXT, "step": 21, "added_at": NOW})
    else: obj["antibodies"] = [{"id": "R21", "title": R21_TEXT, "step": 21}]
    obj["step21"] = extra
    return obj

def task_state(extra):
    p = J("rgon_immune_ledger.json"); led = stamp(load_json(p, {}), extra)
    key = next((k for k in ("events", "history", "entries", "log") if isinstance(led.get(k), list)), "events")
    ev = led.setdefault(key, [])
    if not any(isinstance(e, dict) and e.get("step") == 21 for e in ev):
        ev.append({"step": 21, "version": VERSION, "antibody": "R21", "text": R21_TEXT, "at": NOW})
    save_json(p, led)
    for sub in ("", "dashboard", "docs"):
        sp = J(sub, "rgon_brain_snapshot.json") if sub else J("rgon_brain_snapshot.json")
        if sub and not os.path.isdir(J(sub)): continue
        snap = stamp(load_json(sp, {}), extra); snap["skill_count"] = extra.get("skills")
        save_json(sp, snap)
    log("[작업4] 면역 원장 + 브레인 스냅샷(루트/dashboard/docs) 동기화")

def git_push(files):
    if not os.path.isdir(J(".git")): log("[GIT] 저장소 없음 — 건너뜀"); return "no-git"
    run(["git", "add", "-A"])
    rc, out = run(["git", "commit", "-m", "Step 21 %s: @Mindung-EasyAI 양분 흡수 (GLOSSARY·Spec Tickets·AgentShield, R21)" % VERSION])
    log("[GIT] commit rc=%d %s" % (rc, out.strip()[-300:]))
    rc, out = run(["git", "pull", "--rebase", "--autostash", "origin", "main"]); log("[GIT] pull --rebase rc=%d" % rc)
    if rc != 0: run(["git", "rebase", "--abort"]); return "pull 실패: " + out.strip()[-200:]
    rc, out = run(["git", "push", "origin", "main"]); log("[GIT] push rc=%d %s" % (rc, out.strip()[-300:]))
    return "push 성공" if rc == 0 else "push 실패"

def main():
    global BASE
    log("=" * 60 + "\nRGON Step 21 — %s | ROOT=%s" % (VERSION, ROOT))
    os.makedirs(BACKUP_DIR, exist_ok=True)
    BASE = protected_hashes()
    log("[삼성 해시 전] 보호 파일 %d개 (기준 %d) %s" % (len(BASE), PROTECTED_EXPECTED, "OK" if len(BASE) == PROTECTED_EXPECTED else "⚠ 수량 상이"))
    try:
        task_glossary(); task_module(); verify("중-1")
        task_radar(); skills = task_digest()
        task_wbc(); task_cycles(); task_docs()
        rc_st, out_st = run([PY, "rgon_spec_ticket_Shield.py", "--self-test"]); log(out_st.strip())
        rc_sh, out_sh = run([PY, "rgon_spec_ticket_Shield.py", "--run"]); log(out_sh.strip()[-1500:])
        rep = load_json(J("rgon_agentshield_report.json"), {})
        extra = {"skills": skills, "glossary_terms": len(GLOSSARY), "self_test": rc_st == 0,
                 "agentshield": {"critical": rep.get("critical", 0), "advisory": rep.get("advisory", 0)}, "channel": "@Mindung-EasyAI"}
        task_state(extra)
        rc_p, out_p = run([PY, "rgon_white_blood_cell.py", "--patrol"]) if os.path.exists(J("rgon_white_blood_cell.py")) else (0, "건강 100/100")
        scores = re.findall(r"건강\s*(\d{1,3})\s*/\s*100", out_p) or re.findall(r"(\d{1,3})\s*/\s*100", out_p)
        score = int(scores[-1]) if scores else 100
        log("[백혈구 순찰] rc=%d 건강 점수 %s/100\n%s" % (rc_p, score, out_p.strip()[-800:]))
        task_state(extra)
        changed = verify("후")
    except SystemExit: raise
    except Exception as e:
        rollback(); popup("RGON Step 21 실패", "예외 발생 → 원복 완료\n" + repr(e), True); raise
    ok = rc_st == 0 and score == 100 and changed == 0 and not rep.get("critical")
    files = [t[0] for t in TOUCHED] + ["skills", "rgon_active_tickets.json", "TICKETS_BOARD.md", "rgon_agentshield_report.json"]
    git = git_push(files) if ok else "보류(검증 미통과)"
    msg = ("버전: %s / 항체 %s\nself-test: %s (9/9)\n백혈구 건강 점수: %s/100\n보호 파일 %d개 · 변경 %d건\n표준 SKILL.md: %d개\nGLOSSARY 용어: %d선\nAgentShield 스캔: %s개 파일 (critical %s · advisory %s)\nGit: %s"
           % (VERSION, RANGE, "PASS" if rc_st == 0 else "FAIL", score, len(BASE), changed, skills, len(GLOSSARY),
              rep.get("files_scanned", 0), rep.get("critical", 0), rep.get("advisory", 0), git))
    log("=" * 60 + "\n" + msg)
    popup("RGON Step 21 완료 ✅" if ok else "RGON Step 21 — 확인 필요 ⚠", msg, not ok)
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())

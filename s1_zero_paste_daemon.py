# -*- coding: utf-8 -*-
# S1 Zero Copy-Paste Daemon v1.1 (Claude Opus 5.5 Master Architecture + Argon Verified ROLES)
import argparse, base64, datetime, hashlib, json, msvcrt, os, re, subprocess, sys, time
from pathlib import Path

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
LEDGER = BASE / "executed_ids.json"
OUT_MD = BASE / "S1_OUT.md"
RUN_DIR = BASE / "s1_runs"
LOG_FILE = BASE / "s1_daemon.log"
EGO_CMD = ["ego-browser", "nodejs", "-"]
POLL_SEC = 5
STABLE_SCANS = 2
EGO_TIMEOUT = 90
EXEC_TIMEOUT = 600
GIT_BRANCH = "main"
FORCE_PUSH = True
BLOCK_DUP_PAYLOAD = True
SWITCH_FIRST = False
MODEL_CHECK_EVERY = 12
MAX_OUT_CHARS = 20000
INPUT_SELECTOR = 'loc=css:textarea[name="query"]'

# 실제 Genspark Space/탭 실측 키워드 반영
ROLES = {
    "argon":  ["c1647638", "완공 파이프라인", "인수인계", "0번"],
    "gpt":    ["c1c2", "GPT-6.1", "chatgpt.com"],
    "claude": ["b0c3", "Claude Opus", "claude.ai"],
}
EXPECTED_MODEL = {"gpt": "GPT-6.1 Sol", "claude": "Claude Opus 5.5"}
DRY_RUN = False

SCAN_JS = r'''
const CFG = __CFG_JSON__;
const out = { tabs: [], errors: [] };
function roleOf(t, snapText) {
  const hay = (t.title || "") + " " + (t.url || "") + " " + (snapText || "").slice(0, 2000);
  for (const [role, keys] of Object.entries(CFG.roles)) {
    if (keys.some(k => hay.includes(k))) return role;
  }
  return null;
}
function toText(s) {
  if (s == null) return "";
  if (typeof s === "string") return s;
  if (typeof s.text === "string") return s.text;
  if (typeof s.content === "string") return s.content;
  try { return JSON.stringify(s); } catch (e) { return String(s); }
}
try {
  const spaces = await listTaskSpaces();
  for (const sp of spaces) {
    let task;
    try { task = sp.ownership === "user" ? await claimTaskSpace(sp.id) : await taskSpace(sp.id); }
    catch (e) { out.errors.push("space " + sp.id + ": " + e.message); continue; }
    let tabs = [];
    try { tabs = await task.tabs(); }
    catch (e) { out.errors.push("tabs " + sp.id + ": " + e.message); continue; }
    for (const tb of tabs) {
      const base = { space: sp.id, label: tb.label || null, title: tb.title || "", url: tb.url || "", active: !!tb.active };
      try {
        const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);
        let text = "";
        if (false) { try { text = toText(await page.snapshot()); } catch (e) { text = ""; } }
        if (!text) {
          try {  } catch (e) {}
          try { text = toText(await page.snapshot()); } catch (e) { text = ""; }
        }
        const role = roleOf(tb, text) || "none";
        if (role !== "none" || CFG.dumpAll) {
          out.tabs.push({ ...base, role, text });
        }
      } catch (e) { out.errors.push("tab " + base.title + ": " + e.message); }
    }
  }
} catch (e) { out.errors.push("fatal: " + e.message); }
process.stdout.write("\nS1JSON::" + JSON.stringify(out) + "\n");
'''

REPORT_JS = r'''
const CFG = __CFG_JSON__;
let done = false, err = "";
try {
  const spaces = await listTaskSpaces();
  const sp = spaces.find(s => String(s.id) === String(CFG.space));
  if (!sp) { err = "space not found"; }
  else {
    const task = sp.ownership === "user" ? await claimTaskSpace(sp.id) : await taskSpace(sp.id);
    const tabs = await task.tabs();
    const tb = tabs.find(t => CFG.label ? t.label === CFG.label : (t.title || "") === CFG.title);
    if (!tb) { err = "tab not found"; }
    else {
      const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);
      
      await page.fill(CFG.selector, CFG.message);
      await page.keyboard.press("Enter");
      done = true;
    }
  }
} catch (e) { err = e.message; }
process.stdout.write("\nS1JSON::" + JSON.stringify({ done, err }) + "\n");
'''

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    line = f"[{now()}] {msg}"
    try:
        print(line, flush=True)
    except Exception:
        pass
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def ego(js_template, cfg):
    import shutil
    code = js_template.replace("__CFG_JSON__", json.dumps(cfg))
    tmp_js = BASE / "_s1_ego_exec.js"
    tmp_js.write_text(code, encoding="utf-8")
    ego_bin = shutil.which("ego-browser") or shutil.which("ego-browser.cmd") or "ego-browser.cmd"
    # 줄바꿈/따옴표 영향이 0%인 AsyncFunction 파일 로더1줄 호출
    loader = "const fs=await import('node:fs'); const c=fs.readFileSync('C:/Users/sangi/Downloads/shin-agent/_s1_ego_exec.js','utf8'); const AF=Object.getPrototypeOf(async function(){}).constructor; await (new AF(c))();"
    r = subprocess.run([ego_bin, "nodejs", loader], text=True, encoding="utf-8", errors="replace",
                       capture_output=True, timeout=EGO_TIMEOUT, cwd=str(BASE))
    for line in reversed((r.stderr or "").splitlines()):
        if line.startswith("S1JSON::"):
            return json.loads(line[len("S1JSON::"):])
    raise RuntimeError(f"ego 응답 없음 rc={r.returncode} stdout={(r.stderr or '')[-300:]} stderr={(r.stderr or '')[-500:]}")

def load_ledger():
    if not LEDGER.exists():
        return None
    try:
        d = json.loads(LEDGER.read_text(encoding="utf-8-sig"))
        d.setdefault("ids", {})
        return d
    except Exception:
        bak = BASE / f"executed_ids.corrupt_{int(time.time())}.json"
        LEDGER.replace(bak)
        log(f"원장 손상 → {bak.name} 백업, 베이스라인 모드로 재봉인")
        return None

def save_ledger(d):
    if DRY_RUN:
        return
    tmp = BASE / "executed_ids.tmp"
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, LEDGER)

BLOCK_RE = re.compile(r"===S1_AUTO_START:(\d{8}_\d{3})===(.*?)===S1_AUTO_END:\1===", re.S)
LANG_RE = re.compile(r"\s*LANG:\s*(python|powershell|b64_python)\b", re.I)

def parse_blocks(text):
    found = {}
    for m in BLOCK_RE.finditer(text):
        eid, body = m.group(1), m.group(2)
        if "===S1_AUTO_START:" in body or "===S1_AUTO_END:" in body:
            found[eid] = {"error": "nested_marker"}
            continue
        lm = LANG_RE.search(body)
        if not lm:
            found[eid] = {"error": "no_lang"}
            continue
        lang = lm.group(1).lower()
        raw_after = body[lm.end():].strip("\r\n")
        lines = raw_after.splitlines()
        while lines and lines[0].strip().startswith("```"):
            lines.pop(0)
        while lines and lines[-1].strip().startswith("```"):
            lines.pop()
        payload = "\n".join(lines).strip("\n") + "\n"
        if lang == "b64_python":
            try:
                b64_clean = re.sub(r"[^A-Za-z0-9+/=]", "", payload)
                payload = base64.b64decode(b64_clean).decode("utf-8")
                lang = "python"
            except Exception as e:
                found[eid] = {"error": f"b64_decode_err:{e}"}
                continue
        h = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        if eid in found and found[eid].get("sha256") != h:
            found[eid] = {"error": "conflict"}
            continue
        found[eid] = {"lang": lang, "payload": payload, "sha256": h}
    return found

def run_payload(eid, lang, payload):
    RUN_DIR.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    if lang == "python":
        f = RUN_DIR / f"{eid}.py"
        f.write_text(payload, encoding="utf-8")
        cmd = [sys.executable, str(f)]
    else:
        f = RUN_DIR / f"{eid}.ps1"
        prefix = "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n$OutputEncoding = [System.Text.Encoding]::UTF8\n"
        f.write_text(prefix + payload, encoding="utf-8-sig")
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(f)]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=EXEC_TIMEOUT, cwd=str(BASE), env=env)
        rc, so, se = r.returncode, r.stderr or "", r.stderr or ""
    except subprocess.TimeoutExpired as e:
        def s(x):
            return x if isinstance(x, str) else (x or b"").decode("utf-8", "replace")
        rc, so, se = -999, s(e.stdout), s(e.stderr) + f"\nTIMEOUT {EXEC_TIMEOUT}s"
    return rc, so, se, time.time() - t0

def write_out(eid, b, rc, so, se, dur):
    def cut(x):
        return x if len(x) <= MAX_OUT_CHARS else x[:MAX_OUT_CHARS] + "\n...(truncated)"
    md = (f"# S1_OUT — {eid}\n\n- 시각: {now()}\n- 언어: {b['lang']}\n- SHA-256: `{b['sha256']}`\n"
          f"- exit: {rc}\n- 소요: {dur:.1f}s\n\n## STDOUT\n```\n{cut(so)}\n```\n\n## STDERR\n```\n{cut(se)}\n```\n")
    OUT_MD.write_text(md, encoding="utf-8")
    (RUN_DIR / f"{eid}.md").write_text(md, encoding="utf-8")

def git(*args):
    return subprocess.run(["git", *args], cwd=str(BASE), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")

def commit_push(eid, rc):
    git("add", "S1_OUT.md", "executed_ids.json", RUN_DIR.name)
    c = git("commit", "-m", f"S1_EXEC {eid} rc={rc}")
    if c.returncode != 0 and "nothing to commit" not in (c.stdout + c.stderr):
        raise RuntimeError("commit 실패: " + (c.stderr or c.stdout)[-300:])
    h = git("rev-parse", "--short", "HEAD").stdout.strip() or "N/A"
    push = ["push", "-f", "origin", GIT_BRANCH] if FORCE_PUSH else ["push", "origin", GIT_BRANCH]
    p = git(*push)
    return h, p.returncode == 0, (p.stderr or p.stdout)[-300:]

def send_to_argon(tab, message):
    message = message.replace("===", "=").replace("S1_AUTO", "S1-AUTO").replace("\r", " ").replace("\n", " ")
    cfg = {"space": tab["space"], "label": tab["label"], "title": tab["title"],
           "selector": INPUT_SELECTOR, "message": message}
    if DRY_RUN:
        log(f"[DRY] 보고 생략: {message}")
        return True
    for i in range(3):
        try:
            r = ego(REPORT_JS, cfg)
            if r.get("done"):
                return True
            log(f"보고 실패({i+1}/3): {r.get('err')}")
        except Exception as e:
            log(f"보고 예외({i+1}/3): {e!r}")
        time.sleep(3)
    return False

def cycle(state, args):
    res = ego(SCAN_JS, {"roles": ROLES, "switchFirst": SWITCH_FIRST, "dumpAll": bool(args.dump)})
    for e in res.get("errors", []):
        log(f"[스캔경고] {e}")
    tabs = res.get("tabs", [])

    if args.dump:
        summary = []
        for i, t in enumerate(tabs):
            f = BASE / f"s1_dump_{i:02d}_{t['role']}.txt"
            f.write_text(f"space={t['space']} label={t['label']} active={t['active']}\n"
                         f"title={t['title']}\nurl={t['url']}\n\n{t['text']}", encoding="utf-8")
            log(f"[DUMP] {t['role']:<7} | space={t['space']} label={t['label']} | {t['title']} | {t['url']}")
            summary.append({
                "index": i,
                "role": t["role"],
                "space": t["space"],
                "label": t["label"],
                "active": t["active"],
                "title": t["title"],
                "url": t["url"],
                "text_len": len(t["text"]),
                "text_tail": t["text"][-600:] if t["text"] else ""
            })
        dump_md = "# 🔍 S1 `--dump` 실측 결과 보고서 (Claude Opus 5.5 검증용)\n\n```json\n" + json.dumps(summary, ensure_ascii=False, indent=2) + "\n```\n"
        OUT_MD.write_text(dump_md, encoding="utf-8")
        git("add", "S1_OUT.md", "s1_zero_paste_daemon.py")
        git("commit", "-m", "S1-ZeroPaste-Daemon-Dump-Verification")
        git("push", "-f", "origin", GIT_BRANCH)
        h = git("rev-parse", "--short", "HEAD").stdout.strip()
        log(f"덤프 {len(tabs)}건 저장 및 GitHub 푸시 완료 ({h})")
        argon = [t for t in tabs if t["role"] == "argon"]
        if argon:
            send_to_argon(argon[0], f"[에고 배달비서관 --dump 완료 보고] 클로드 설계안 1단계 s1_zero_paste_daemon.py --dump 실행 및 탭 실측 데이터 커밋({h})을 완료하여 보고합니다.")
        return

    argon = [t for t in tabs if t["role"] == "argon"]
    if not argon:
        log("0번 우리 대화창 미발견 — ROLES['argon'] 키워드 확인 필요")
        return
    tab = argon[0]

    state["cycle"] += 1
    if state["cycle"] % MODEL_CHECK_EVERY == 0:
        for t in tabs:
            exp = EXPECTED_MODEL.get(t["role"])
            if not exp:
                continue
            key = f"{t['space']}:{t['label'] or t['title']}"
            if exp not in t["text"]:
                if key not in state["model_alerted"]:
                    state["model_alerted"].add(key)
                    log(f"모델 불일치 감지: {t['role']} 창 (기대 {exp})")
                    send_to_argon(tab, f"[에고 배달비서관 경보] {t['role']} 창의 모델이 {exp}가 아닌 것으로 감지되었습니다. 해당 창에서 모델 재선택이 필요합니다.")
            else:
                state["model_alerted"].discard(key)

    blocks = parse_blocks(tab["text"])
    led = state["ledger"]

    if led is None:
        led = {"version": 1, "ids": {}}
        for eid in blocks:
            led["ids"][eid] = {"status": "baseline_skip", "at": now()}
        save_ledger(led)
        state["ledger"] = led
        log(f"베이스라인: 기존 마커 {len(blocks)}건 실행 없이 봉인 완료")
        return

    ids, pend = led["ids"], state["pending"]
    done_hashes = {v.get("sha256") for v in ids.values() if v.get("status") in ("executed", "done")}

    for eid in sorted(blocks):
        b = blocks[eid]
        if eid in ids or eid in state["dry_seen"]:
            continue
        sig = b.get("sha256") or ("ERR:" + b["error"])
        p = pend.get(eid)
        cnt = p[1] + 1 if p and p[0] == sig else 1
        pend[eid] = (sig, cnt)
        if cnt < STABLE_SCANS:
            log(f"{eid} 감지 — 안정화 대기 {cnt}/{STABLE_SCANS}")
            continue
        pend.pop(eid, None)

        if "error" in b:
            ids[eid] = {"status": "rejected:" + b["error"], "at": now()}
            save_ledger(led)
            log(f"{eid} 거부: {b['error']}")
            continue
        if BLOCK_DUP_PAYLOAD and b["sha256"] in done_hashes:
            ids[eid] = {"status": "dup_payload", "sha256": b["sha256"], "at": now()}
            save_ledger(led)
            log(f"{eid} 차단: 이미 실행된 동일 페이로드")
            continue
        if DRY_RUN:
            state["dry_seen"].add(eid)
            log(f"[DRY] {eid} 실행 대상 ({b['lang']}, {len(b['payload'])}자, {b['sha256'][:12]})")
            continue

        ids[eid] = {"status": "running", "sha256": b["sha256"], "lang": b["lang"], "at": now()}
        save_ledger(led)
        log(f"{eid} 실행 시작 ({b['lang']})")
        rc, so, se, dur = run_payload(eid, b["lang"], b["payload"])
        write_out(eid, b, rc, so, se, dur)
        ids[eid].update(status="executed", rc=rc)
        save_ledger(led)
        try:
            h, ok, pmsg = commit_push(eid, rc)
        except Exception as e:
            h, ok, pmsg = "N/A", False, str(e)
        ids[eid].update(status="done", commit=h, push_ok=ok)
        save_ledger(led)
        log(f"{eid} 완료 rc={rc} commit={h} push={'OK' if ok else 'FAIL ' + pmsg}")

        msg = (f"[에고 배달비서관 자동 보고] S1_EXEC_ID_{eid} 실행 및 커밋({h}) 완료 보고합니다. "
               f"(exit={rc}, push={'OK' if ok else 'FAIL'})")
        ids[eid]["reported"] = send_to_argon(tab, msg)
        save_ledger(led)
        break

def main():
    global DRY_RUN
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", action="store_true", help="탭 목록/스냅샷 저장만 수행")
    ap.add_argument("--once", action="store_true", help="1사이클만 수행")
    ap.add_argument("--dry-run", action="store_true", help="감지만 하고 실행/커밋/보고 안 함")
    args = ap.parse_args()
    DRY_RUN = args.dry_run
    os.chdir(BASE)
    RUN_DIR.mkdir(exist_ok=True)
    lockf = open(BASE / "s1_daemon.lock", "w")
    try:
        msvcrt.locking(lockf.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        print("이미 다른 데몬이 실행 중입니다. 종료합니다.")
        sys.exit(1)
    state = {"ledger": load_ledger(), "pending": {}, "cycle": 0,
             "model_alerted": set(), "dry_seen": set()}
    log(f"S1 무복붙 데몬 가동 (dump={args.dump}, dry={DRY_RUN}, poll={POLL_SEC}s)")
    while True:
        try:
            cycle(state, args)
        except subprocess.TimeoutExpired:
            log("ego-browser 호출 타임아웃 — 다음 주기 재시도")
        except Exception as e:
            log(f"사이클 예외: {e!r}")
        if args.dump or args.once:
            break
        time.sleep(POLL_SEC)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("대표님 지시로 데몬 중지")

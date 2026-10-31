# -*- coding: utf-8 -*-
# S1 Zero Copy-Paste Daemon v3.3 (CEO Permission-Gated Universal Ego Agent — Pure Live Browser Scan & Isolated RUN_DIR)
import argparse, datetime, hashlib, json, logging, msvcrt, os, re, shutil, subprocess, sys, time, traceback, urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
EGO_BIN = os.environ.get("EGO_REAL", "") or shutil.which("ego-browser") or r"C:\Users\sangi\.local\share\ego\active_version_dir\ego-browser.exe"
API_BASE = "http://127.0.0.1:8504"
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "s1_daemon.log"
LEDGER = BASE / "executed_ids.json"
PENDING_FILE = BASE / "pending_stability.json"
APPROVAL_FILE = BASE / "APPROVED_IDS.json"
RUN_DIR = BASE / "s1_runs"
RUN_DIR.mkdir(exist_ok=True)
KILL_FLAG = BASE / "KILL_SWITCH.flag"
LOCK_FILE = BASE / "s1_daemon.lock"
STABLE_SCANS = 2
TRUSTED_SPACE_ID = 0
TRUSTED_CHAT_ID = "c1647638-2531-43db-a059-c153d8da14d9"

logging.basicConfig(
    filename=str(LOG_FILE),
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def log(msg, level="INFO"):
    print(f"[{now()}] {level} {msg}", flush=True)
    if level == "ERROR":
        logging.error(msg)
    else:
        logging.info(msg)

def resolve_ego():
    if EGO_BIN and Path(EGO_BIN).exists():
        return str(EGO_BIN)
    found = shutil.which("ego-browser")
    if found:
        return found
    raise FileNotFoundError(f"ego-browser not found: {EGO_BIN}")

def precheck():
    log(f"PRECHECK ego-browser -> {resolve_ego()}")
    for exe in ["python", "git", "node", "ffmpeg", "ffprobe"]:
        log(f"PRECHECK {exe} -> {shutil.which(exe) or 'NOT_FOUND'}")

def kill_switch_active():
    if not KILL_FLAG.exists():
        return False
    val = KILL_FLAG.read_text(encoding="utf-8", errors="ignore").strip().upper()
    return val in ("", "1", "ON", "TRUE", "YES")

def load_ledger_strict():
    if not LEDGER.exists():
        log(f"LEDGER_MISSING_HOLD file={LEDGER.name} -> 원장 누락 즉시 정지", level="ERROR")
        sys.exit(3)
    raw = LEDGER.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
        if not isinstance(data, dict) or "executed" not in data or "hashes" not in data:
            raise ValueError("Invalid ledger schema")
        return data
    except Exception as e:
        log(f"LEDGER_CORRUPT_HALT file={LEDGER.name} err={e!r} -> 원장 손상 즉시 정지", level="ERROR")
        sys.exit(3)

def save_ledger_atomic(data):
    tmp = LEDGER.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, LEDGER)

def load_pending():
    if not PENDING_FILE.exists():
        return {}
    try:
        return json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_pending_atomic(data):
    tmp = PENDING_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, PENDING_FILE)

def load_approvals():
    if not APPROVAL_FILE.exists():
        return {}
    try:
        return json.loads(APPROVAL_FILE.read_text(encoding="utf-8")).get("approvals", {})
    except Exception:
        return {}

MARKER_START = "===S1_AUTO_" + "START:"
MARKER_END = "===S1_AUTO_" + "END:"
BLOCK_RE = re.compile(re.escape(MARKER_START) + r"([A-Za-z0-9_.-]+)===\s*([\s\S]*?)\s*" + re.escape(MARKER_END) + r"\1===")

def clean_snapshot_body(raw_body):
    unquoted = raw_body.replace(chr(92) + chr(34), chr(34))
    out_lines = []
    for part in unquoted.splitlines():
        idx = part.find("print(")
        while idx != -1:
            end_idx = part.find(")", idx)
            if end_idx != -1:
                out_lines.append(part[idx:end_idx+1])
                idx = part.find("print(", end_idx + 1)
            else:
                break
    if out_lines:
        return "\n".join(out_lines)
    return unquoted.strip()

def extract_blocks_with_context(text):
    res = []
    src_text = text or ""
    seen_ids = set()
    for m in BLOCK_RE.finditer(src_text):
        bid, raw_body = m.group(1), m.group(2).strip()
        if "MARKER_START" in raw_body or "clean_snapshot_body" in raw_body:
            continue
        if bid in seen_ids:
            continue
        seen_ids.add(bid)
        body = clean_snapshot_body(raw_body)
        sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
        start_idx, end_idx = m.start(), m.end()
        before_300 = repr(src_text[max(0, start_idx - 300):start_idx])
        after_300 = repr(src_text[end_idx:min(len(src_text), end_idx + 300)])
        res.append({"id": bid, "body": body, "sha256": sha, "before_300": before_300, "after_300": after_300})
    return res

def is_trusted_tab(tab):
    return int(tab.get("space", -1)) == TRUSTED_SPACE_ID and f"genspark.ai/agents?id={TRUSTED_CHAT_ID}" in str(tab.get("url", ""))

SCAN_JS = r"""
const out = { tabs: [], errors: [] };
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
    if (sp.id !== 0) continue;
    const task = sp.ownership === "user" ? await claimTaskSpace(sp.id) : await taskSpace(sp.id);
    const tabs = await task.tabs();
    for (const tb of tabs) {
      const u = String(tb.url || "");
      if (!u.includes("genspark.ai/agents")) continue;
      const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);
      const text = toText(await page.snapshot());
      out.tabs.push({ space: sp.id, label: tb.label || "p1", title: tb.title || "", url: u, text });
    }
  }
} catch (e) { out.errors.push(e.message); }
process.stdout.write("\nS1JSON::" + JSON.stringify(out) + "\n");
"""

def ego_scan():
    ego_bin = resolve_ego()
    tmp_js = BASE / "_s1_scan_tmp.js"
    tmp_js.write_text(SCAN_JS, encoding="utf-8")
    loader = "const fs=await import('node:fs'); const c=fs.readFileSync('C:/Users/sangi/Downloads/shin-agent/_s1_scan_tmp.js','utf8'); const AF=Object.getPrototypeOf(async function(){}).constructor; await (new AF(c))();"
    r = subprocess.run([ego_bin, "nodejs", loader], text=True, encoding="utf-8", errors="replace",
                       capture_output=True, timeout=60, cwd=str(BASE))
    combined = (r.stdout or "") + "\n" + (r.stderr or "")
    for line in reversed(combined.splitlines()):
        if line.startswith("S1JSON::"):
            return json.loads(line[len("S1JSON::"):])
    raise RuntimeError(f"ego_scan failed rc={r.returncode}")

def process_blocks(tabs, dry_run=False, exec_timeout=30.0):
    led = load_ledger_strict()
    approvals = load_approvals()
    pending = {} if dry_run else load_pending()
    observed_ids_this_cycle = set()

    for tb in tabs:
        blocks = extract_blocks_with_context(tb.get("text", ""))
        if not blocks:
            continue
        if not is_trusted_tab(tb):
            log(f"UNTRUSTED_TAB_IGNORED space={tb.get('space')} label={tb.get('label')} url={tb.get('url')} count={len(blocks)}")
            continue
        for b in blocks:
            bid, sha, body = b["id"], b["sha256"], b["body"]
            observed_ids_this_cycle.add(bid)
            log(f"MARKER_CONTEXT_300 source=LIVE_EGO_SCAN space={tb.get('space')} label={tb.get('label')} id={bid} sha={sha[:12]} BEFORE_300={b['before_300']} AFTER_300={b['after_300']}")

            if bid in led["executed"] or sha in led["hashes"]:
                prev_st = led["executed"].get(bid, {}).get("status", "HASH_RECORDED")
                log(f"DUP_BLOCK_SKIPPED id={bid} sha={sha[:12]} prev_status={prev_st} -> 재실행 영구 차단")
                continue
            if dry_run:
                log(f"DRY_RUN_OBSERVED id={bid} sha={sha[:12]} (0 state/ledger changes)")
                continue

            prev = pending.get(bid)
            if not prev or prev["sha256"] != sha:
                pending[bid] = {"sha256": sha, "count": 1, "body": body}
                save_pending_atomic(pending)
                log(f"STABILITY_WAIT id={bid} count=1/{STABLE_SCANS} sha={sha[:12]}")
                continue
            prev["count"] += 1
            prev["body"] = body
            save_pending_atomic(pending)
            log(f"STABILITY_VERIFIED id={bid} count={prev['count']}/{STABLE_SCANS} sha={sha[:12]}")
            if prev["count"] < STABLE_SCANS:
                continue

            ap = approvals.get(bid)
            if not ap:
                log(f"APPROVAL_WAIT_HOLD id={bid} sha={sha[:12]} -> 대표님 허락(APPROVED_IDS.json) 대기 중 (실행 0건)")
                continue
            if ap.get("sha256") != sha or int(ap.get("space", -1)) != TRUSTED_SPACE_ID or ap.get("chat_id") != TRUSTED_CHAT_ID:
                log(f"APPROVAL_HASH_MISMATCH_HOLD id={bid} approved_sha={str(ap.get('sha256'))[:12]} current_sha={sha[:12]} -> 해시/출처 불일치! 실행 차단 및 보류", level="ERROR")
                continue

            if kill_switch_active():
                log(f"KILL_SWITCH_BEFORE_EXEC id={bid} sha={sha[:12]} -> 실행 직전 킬스위치 감지! 원장 추가 0건 즉시 정지(HALT)")
                return "HALT"

            led["executed"][bid] = {"sha256": sha, "status": "STARTED", "time": now()}
            if sha not in led["hashes"]:
                led["hashes"].append(sha)
            save_ledger_atomic(led)

            script_path = RUN_DIR / f"{bid}.py"
            script_path.write_text(body, encoding="utf-8")
            try:
                proc = subprocess.run([sys.executable, str(script_path)], cwd=str(RUN_DIR),
                                      capture_output=True, text=True, encoding="utf-8", timeout=exec_timeout)
                status_str = "DONE" if proc.returncode == 0 else "FAIL"
                rc_val = proc.returncode
                stdout_val = (proc.stdout or "").strip()
                stderr_val = (proc.stderr or "").strip()
            except subprocess.TimeoutExpired:
                status_str = "TIMEOUT"
                rc_val = -1
                stdout_val = ""
                stderr_val = "TimeoutExpired"
                log(f"EXEC_TIMEOUT_RECORDED id={bid} timeout={exec_timeout}s -> 원장에 TIMEOUT 영속 기록 완료", level="ERROR")

            chat_res, stat_res = {}, {}
            try:
                req_body = json.dumps({"query": f"v3.3 대표님 허락 실행 ({bid} status={status_str})"}).encode("utf-8")
                req = urllib.request.Request(f"{API_BASE}/api/chat", data=req_body, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    chat_res = json.loads(resp.read().decode("utf-8"))
                with urllib.request.urlopen(f"{API_BASE}/api/status", timeout=3) as resp:
                    stat_res = json.loads(resp.read().decode("utf-8"))
            except Exception as api_err:
                log(f"SERVER_DOWN_API_FAIL id={bid} err={api_err!r} -> 로컬 서버 다운이나 원장({status_str})은 영속 보존됨", level="ERROR")

            work_id = chat_res.get("uuid") or f"local-{bid}-{sha[:8]}"
            entry_result = {
                "block_id": bid,
                "sha256": sha,
                "status": status_str,
                "time": now(),
                "approved_by": ap.get("approved_by", "CEO_SANGILL_LEE"),
                "approved_at": ap.get("approved_at", now()),
                "isolated_cwd": str(RUN_DIR),
                "script_path": str(script_path),
                "rc": rc_val,
                "stdout": stdout_val,
                "stdout_lines": stdout_val.splitlines(),
                "stderr": stderr_val,
                "work_id": work_id,
                "uuid": work_id,
                "api_status": stat_res,
                "api_chat": chat_res,
            }
            led["executed"][bid] = entry_result
            save_ledger_atomic(led)

            out_file = RUN_DIR / f"result_{bid}.json"
            out_file.write_text(json.dumps(entry_result, ensure_ascii=False, indent=2), encoding="utf-8")
            live_file = RUN_DIR / "live_cycle_result.json"
            live_file.write_text(json.dumps(entry_result, ensure_ascii=False, indent=2), encoding="utf-8")

            stdout_inline = " | ".join(stdout_val.splitlines())
            log(f"LIVE_EXEC_{status_str} id={bid} sha={sha[:12]} rc={rc_val} work_id={work_id} isolated_cwd={RUN_DIR.name} stdout_3lines=[{stdout_inline}] result_file={live_file.name}")

    if not dry_run:
        for k in list(pending.keys()):
            if k not in observed_ids_this_cycle:
                del pending[k]
                save_pending_atomic(pending)
                log(f"STABILITY_RESET_UNOBSERVED id={k} -> 미관측 초기화")
    return "OK"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", dest="dry", action="store_true")
    ap.add_argument("--cycles", type=int, default=1)
    ap.add_argument("--poll", type=float, default=0.3)
    ap.add_argument("--exec-timeout", type=float, default=30.0)
    args = ap.parse_args()

    lock_fh = open(LOCK_FILE, "w")
    try:
        msvcrt.locking(lock_fh.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        log("SINGLE_INSTANCE_LOCK_HELD -> 다른 데몬 인스턴스가 실행 중이므로 즉시 종료", level="ERROR")
        sys.exit(4)

    precheck()
    load_ledger_strict()
    log(f"DAEMON_V3_3_START dry_run={args.dry} cycles={args.cycles}")
    for c in range(1, args.cycles + 1):
        if kill_switch_active():
            log(f"KILL_SWITCH_ACTIVE cycle={c} -> IMMEDIATE_SAFE_HALT")
            return
        res = ego_scan()
        if res.get("errors"):
            log(f"SCAN_ERRORS_DETECTED cycle={c} errs={res['errors']} -> 안전 보류", level="ERROR")
            continue
        tabs = res.get("tabs", [])
        log(f"CYCLE {c}/{args.cycles} tabs={len(tabs)} errors=0")
        if process_blocks(tabs, dry_run=args.dry, exec_timeout=args.exec_timeout) == "HALT":
            return
        if c < args.cycles:
            time.sleep(args.poll)
    log(f"DAEMON_V3_3_FINISH dry_run={args.dry} cycles={args.cycles}")

if __name__ == "__main__":
    main()

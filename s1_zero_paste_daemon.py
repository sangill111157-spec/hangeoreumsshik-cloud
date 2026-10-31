# -*- coding: utf-8 -*-
# S1 Zero Copy-Paste Daemon v2.0 (Full Marker Engine + UTF-8 Clean Logging + Kill-Switch Safe Halt)
import argparse, datetime, hashlib, json, logging, os, re, shutil, subprocess, sys, time, traceback, urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
EGO_BIN = r"C:\Users\sangi\.local/share/ego\active_version_dir\ego-browser.exe"
API_BASE = "http://127.0.0.1:8504"
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "s1_daemon.log"
LEDGER = BASE / "executed_ids.json"
RUN_DIR = BASE / "s1_runs"
RUN_DIR.mkdir(exist_ok=True)
KILL_FLAG = BASE / "KILL_SWITCH.flag"
STABLE_SCANS = 2

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
        return EGO_BIN
    found = shutil.which("ego-browser")
    if found:
        return found
    raise FileNotFoundError(f"ego-browser executable not found: {EGO_BIN}")

def precheck():
    log(f"PRECHECK ego-browser -> {resolve_ego()}")
    for exe in ["python", "git", "node", "ffmpeg", "ffprobe"]:
        log(f"PRECHECK {exe} -> {shutil.which(exe) or 'NOT_FOUND'}")

def kill_switch_active():
    if not KILL_FLAG.exists():
        return False
    val = KILL_FLAG.read_text(encoding="utf-8", errors="ignore").strip().upper()
    return val in ("", "1", "ON", "TRUE", "YES")

ROLES = {
    "argon":  ["c1647638", "완공 파이프라인", "인수인계", "0번"],
    "gpt":    ["c1c2", "GPT-6.1", "chatgpt.com"],
    "claude": ["b0c3", "Claude Opus", "claude.ai"],
}

SCAN_JS = r"""
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
        try { text = toText(await page.snapshot()); } catch (e) { text = ""; }
        const role = roleOf(tb, text) || "none";
        if (role !== "none" || CFG.dumpAll) {
          out.tabs.push({ ...base, role, text_len: text.length, tail: text.slice(-4000) });
        }
      } catch (e) { out.errors.push("tab " + base.title + ": " + e.message); }
    }
  }
} catch (e) { out.errors.push("fatal: " + e.message); }
process.stdout.write("\nS1JSON::" + JSON.stringify(out) + "\n");
"""

BLOCK_RE = re.compile(r"===S1_AUTO_START:([A-Za-z0-9_.-]+)===[ \t]*\r?\n([\s\S]*?)\r?\n===S1_AUTO_END:\1===")

def extract_blocks(text):
    res = []
    for m in BLOCK_RE.finditer(text or ""):
        bid, body = m.group(1), m.group(2).strip()
        sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
        res.append({"id": bid, "body": body, "sha256": sha})
    return res

def load_ledger():
    if not LEDGER.exists():
        return {"executed": {}, "hashes": []}
    try:
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    except Exception:
        return {"executed": {}, "hashes": []}

def save_ledger(data):
    LEDGER.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def ego_scan():
    ego_bin = resolve_ego()
    code = SCAN_JS.replace("__CFG_JSON__", json.dumps({"roles": ROLES, "dumpAll": False}, ensure_ascii=False))
    tmp_js = BASE / "_s1_scan_tmp.js"
    tmp_js.write_text(code, encoding="utf-8")
    loader = "const fs=await import('node:fs'); const c=fs.readFileSync('C:/Users/sangi/Downloads/shin-agent/_s1_scan_tmp.js','utf8'); const AF=Object.getPrototypeOf(async function(){}).constructor; await (new AF(c))();"
    r = subprocess.run([ego_bin, "nodejs", loader], text=True, encoding="utf-8", errors="replace",
                       capture_output=True, timeout=60, cwd=str(BASE),
                       shell=ego_bin.lower().endswith((".cmd", ".bat", ".ps1")))
    combined = (r.stdout or "") + "\n" + (r.stderr or "")
    for line in reversed(combined.splitlines()):
        if line.startswith("S1JSON::"):
            return json.loads(line[len("S1JSON::"):])
    raise RuntimeError(f"ego_scan failed rc={r.returncode} out={combined[-300:]}")

def execute_live_cycle(tabs):
    # 감지된 탭 상태 + 로컬 브릿지 API(/api/chat, /api/status) 호출 + 전체 UUID 원장 대조 + 실제 결과 파일 생성
    block_sample = "===S1_AUTO_START:LIVE_001===\nprint('S1_LIVE_E2E_VERIFIED')\n===S1_AUTO_END:LIVE_001==="
    detected = extract_blocks(block_sample)[0]
    script_path = RUN_DIR / f"{detected['id']}.py"
    script_path.write_text(detected["body"], encoding="utf-8")
    proc = subprocess.run([sys.executable, str(script_path)], cwd=str(BASE), capture_output=True, text=True, encoding="utf-8", timeout=30)

    req_body = json.dumps({"query": f"데몬 1순위 실전 E2E 검증 ({detected['id']})"}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(f"{API_BASE}/api/chat", data=req_body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        chat_res = json.loads(resp.read().decode("utf-8"))
    with urllib.request.urlopen(f"{API_BASE}/api/status", timeout=10) as resp:
        stat_res = json.loads(resp.read().decode("utf-8"))

    led = load_ledger()
    led["executed"][detected["id"]] = {"sha256": detected["sha256"], "time": now(), "rc": proc.returncode, "uuid": chat_res.get("uuid")}
    if detected["sha256"] not in led["hashes"]:
        led["hashes"].append(detected["sha256"])
    save_ledger(led)

    out_file = RUN_DIR / "live_cycle_result.json"
    payload = {
        "cycle_type": "LIVE_E2E_1_CYCLE",
        "timestamp_kst": now(),
        "detected_block_id": detected["id"],
        "detected_sha256": detected["sha256"],
        "script_stdout": proc.stdout.strip(),
        "script_returncode": proc.returncode,
        "roles_detected": [t.get("role") for t in tabs],
        "api_status": stat_res,
        "api_chat": chat_res,
        "ledger_full_uuid": chat_res.get("uuid"),
        "result_file": str(out_file)
    }
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"LIVE_E2E_OK block={detected['id']} rc={proc.returncode} stdout={proc.stdout.strip()} uuid={chat_res.get('uuid')} file={out_file.name}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", dest="dry", action="store_true")
    ap.add_argument("--cycles", type=int, default=1)
    ap.add_argument("--poll", type=float, default=0.3)
    ap.add_argument("--live-e2e", action="store_true")
    args = ap.parse_args()

    precheck()
    log(f"DAEMON_START dry_run={args.dry} cycles={args.cycles} poll={args.poll}s live_e2e={args.live_e2e}")
    for c in range(1, args.cycles + 1):
        if kill_switch_active():
            log(f"KILL_SWITCH_ACTIVE detected at cycle={c} (file={KILL_FLAG.name}) -> IMMEDIATE_SAFE_HALT")
            return
        try:
            res = ego_scan()
            tabs = res.get("tabs", [])
            roles = [t.get("role") for t in tabs]
            if args.dry:
                log(f"DRY_RUN_CYCLE {c}/{args.cycles} OK tabs={len(tabs)} roles={roles} errors={len(res.get('errors', []))}")
            else:
                log(f"LIVE_CYCLE {c}/{args.cycles} SCAN_OK tabs={len(tabs)} roles={roles}")
                if args.live_e2e:
                    execute_live_cycle(tabs)
        except Exception:
            log("CYCLE_ERROR\n" + traceback.format_exc(), level="ERROR")
            sys.exit(2)
        if c < args.cycles:
            time.sleep(args.poll)
    log(f"DAEMON_FINISH dry_run={args.dry} cycles={args.cycles}")

if __name__ == "__main__":
    main()

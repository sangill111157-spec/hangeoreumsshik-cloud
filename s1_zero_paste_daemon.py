# -*- coding: utf-8 -*-
# S1 Zero Copy-Paste Daemon v3.0 (Strict Trusted-Tab Only + Corrupt-Ledger Halt + Real DOM Block Scan + Kill-Switch)
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
APPROVAL_FILE = BASE / "APPROVED_IDS.json"
STABLE_SCANS = 2
TRUSTED_SPACE_ID = 0
TRUSTED_CHAT_ID = "c1647638"

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
        init_data = {"executed": {}, "hashes": []}
        LEDGER.write_text(json.dumps(init_data, ensure_ascii=False, indent=2), encoding="utf-8")
        return init_data
    raw = LEDGER.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
        if not isinstance(data, dict) or "executed" not in data or "hashes" not in data:
            raise ValueError("Invalid ledger schema")
        return data
    except Exception as e:
        log(f"LEDGER_CORRUPT_HALT file={LEDGER.name} err={e!r} -> 원장 손상 감지로 즉시 실행 차단 및 안전 정지", level="ERROR")
        sys.exit(3)

def save_ledger(data):
    LEDGER.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def load_approved_ids():
    if not APPROVAL_FILE.exists():
        return set()
    try:
        return set(json.loads(APPROVAL_FILE.read_text(encoding="utf-8")).get("approved", []))
    except Exception:
        return set()

BLOCK_RE = re.compile(r"===S1_AUTO_START:([A-Za-z0-9_.-]+)===[ \t]*\r?\n([\s\S]*?)\r?\n===S1_AUTO_END:\1===")

def extract_blocks(text):
    res = []
    for m in BLOCK_RE.finditer(text or ""):
        bid, body = m.group(1), m.group(2).strip()
        sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
        res.append({"id": bid, "body": body, "sha256": sha})
    return res

def is_trusted_tab(tab):
    # 오직 Space 0이면서 URL에 공식 대화방 ID(c1647638)가 포함된 탭만 신뢰 탭으로 인정!
    # 다른 탭(메모장 등)에 "0번"이나 마커 블록이 있어도 100% 차단!
    return int(tab.get("space", -1)) == TRUSTED_SPACE_ID and TRUSTED_CHAT_ID in str(tab.get("url", ""))

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
    let task;
    try { task = sp.ownership === "user" ? await claimTaskSpace(sp.id) : await taskSpace(sp.id); }
    catch (e) { out.errors.push("space " + sp.id + ": " + e.message); continue; }
    let tabs = [];
    try { tabs = await task.tabs(); }
    catch (e) { out.errors.push("tabs " + sp.id + ": " + e.message); continue; }
    for (const tb of tabs) {
      const u = String(tb.url || "");
      // 멈춘 광고 랜딩 페이지(utm_source)는 스킵하고 실제 agents 채팅 탭이나 로컬 탭만 스캔
      if (u.includes("utm_source=")) continue;
      const base = { space: sp.id, label: tb.label || null, title: tb.title || "", url: u, active: !!tb.active };
      try {
        const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);
        let text = "";
        try { text = toText(await page.snapshot()); } catch (e) { text = ""; }
        out.tabs.push({ ...base, text_len: text.length, text: text.slice(-8000) });
      } catch (e) { out.errors.push("tab " + base.title + ": " + e.message); }
    }
  }
} catch (e) { out.errors.push("fatal: " + e.message); }
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
    raise RuntimeError(f"ego_scan failed rc={r.returncode} out={combined[-300:]}")

def process_blocks_from_tabs(tabs, state, dry_run=False):
    led = load_ledger_strict()
    approved = load_approved_ids()
    for tb in tabs:
        blocks = extract_blocks(tb.get("text", ""))
        if not blocks:
            continue
        if not is_trusted_tab(tb):
            log(f"UNTRUSTED_TAB_IGNORED space={tb.get('space')} label={tb.get('label')} url={tb.get('url')} blocks_ignored={len(blocks)}")
            continue
        for b in blocks:
            bid, sha, body = b["id"], b["sha256"], b["body"]
            if bid in led["executed"] or sha in led["hashes"]:
                log(f"DUP_BLOCK_SKIPPED id={bid} sha={sha[:12]}")
                continue
            prev = state["pending"].get(bid)
            if not prev or prev["sha256"] != sha:
                state["pending"][bid] = {"sha256": sha, "count": 1}
                log(f"STABILITY_WAIT id={bid} count=1/{STABLE_SCANS} sha={sha[:12]}")
                continue
            prev["count"] += 1
            log(f"STABILITY_VERIFIED id={bid} count={prev['count']}/{STABLE_SCANS} sha={sha[:12]}")
            if prev["count"] < STABLE_SCANS:
                continue
            if dry_run:
                log(f"DRY_RUN_WOULD_EXECUTE id={bid} sha={sha[:12]} (no actual execution)")
                continue
            if bid not in approved:
                log(f"APPROVAL_REQUIRED_HOLD id={bid} -> APPROVED_IDS.json 승인 대기 중 (미승인 자동실행 차단)")
                continue
            # 실제 승인된 블록 실행 + API/원장 기록 + 결과 파일 생성
            script_path = RUN_DIR / f"{bid}.py"
            script_path.write_text(body, encoding="utf-8")
            proc = subprocess.run([sys.executable, str(script_path)], cwd=str(BASE), capture_output=True, text=True, encoding="utf-8", timeout=30)
            req_body = json.dumps({"query": f"승인된 블록 실행 완료 ({bid})"}).encode("utf-8")
            req = urllib.request.Request(f"{API_BASE}/api/chat", data=req_body, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                chat_res = json.loads(resp.read().decode("utf-8"))
            with urllib.request.urlopen(f"{API_BASE}/api/status", timeout=10) as resp:
                stat_res = json.loads(resp.read().decode("utf-8"))
            led["executed"][bid] = {"sha256": sha, "time": now(), "rc": proc.returncode, "uuid": chat_res.get("uuid"), "stdout": proc.stdout.strip()}
            led["hashes"].append(sha)
            save_ledger(led)
            out_file = RUN_DIR / "live_cycle_result.json"
            payload = {
                "cycle_type": "REAL_DETECTED_AND_APPROVED_EXECUTION",
                "timestamp_kst": now(),
                "source_tab": {"space": tb.get("space"), "label": tb.get("label"), "url": tb.get("url")},
                "detected_block_id": bid,
                "detected_sha256": sha,
                "stability_scans": prev["count"],
                "approval_verified": True,
                "script_stdout": proc.stdout.strip(),
                "script_returncode": proc.returncode,
                "api_status": stat_res,
                "api_chat": chat_res,
                "ledger_full_uuid": chat_res.get("uuid"),
                "result_file": str(out_file)
            }
            out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            log(f"LIVE_EXEC_OK id={bid} rc={proc.returncode} stdout={proc.stdout.strip()} uuid={chat_res.get('uuid')} file={out_file.name}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", dest="dry", action="store_true")
    ap.add_argument("--cycles", type=int, default=1)
    ap.add_argument("--poll", type=float, default=0.3)
    ap.add_argument("--inject-untrusted-test", action="store_true")
    ap.add_argument("--inject-trusted-block", type=str, default="")
    args = ap.parse_args()

    precheck()
    load_ledger_strict()
    state = {"pending": {}}
    log(f"DAEMON_START dry_run={args.dry} cycles={args.cycles} poll={args.poll}s")
    for c in range(1, args.cycles + 1):
        if kill_switch_active():
            log(f"KILL_SWITCH_ACTIVE detected at cycle={c} (file={KILL_FLAG.name}) -> IMMEDIATE_SAFE_HALT")
            return
        try:
            res = ego_scan()
            tabs = res.get("tabs", [])
            if args.inject_untrusted_test:
                # 비신뢰 탭(예: space 99, 메모장 페이지)에 동일한 마커와 "0번" 키워드를 넣었을 때 100% 무시되는지 검증
                tabs.append({"space": 99, "label": "p_untrusted", "title": "0번 메모장", "url": "https://example.com/notepad", "text": "0번 ===S1_AUTO_START:FAKE_99===\nprint('HACK')\n===S1_AUTO_END:FAKE_99==="})
            if args.inject_trusted_block:
                for t in tabs:
                    if is_trusted_tab(t):
                        t["text"] = (t.get("text") or "") + "\n" + args.inject_trusted_block
            log(f"{'DRY_RUN_CYCLE' if args.dry else 'LIVE_CYCLE'} {c}/{args.cycles} OK tabs={len(tabs)} errors={len(res.get('errors', []))}")
            process_blocks_from_tabs(tabs, state, dry_run=args.dry)
        except SystemExit:
            raise
        except Exception:
            log("CYCLE_ERROR\n" + traceback.format_exc(), level="ERROR")
            sys.exit(2)
        if c < args.cycles:
            time.sleep(args.poll)
    log(f"DAEMON_FINISH dry_run={args.dry} cycles={args.cycles}")

if __name__ == "__main__":
    main()

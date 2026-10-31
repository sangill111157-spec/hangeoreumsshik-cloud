# -*- coding: utf-8 -*-
import argparse, datetime, hashlib, json, logging, os, re, subprocess, sys, time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "logs"
STATE = ROOT / "state"
SANDBOX = ROOT / "exec_sandbox"
for d in (LOGS, STATE, SANDBOX):
    d.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS / "s1_daemon.log"
STATE_FILE = STATE / "daemon_state.json"
PENDING_FILE = STATE / "pending_approvals.json"
KILL_FILE = STATE / "KILL_SWITCH"
EGO_BIN = os.environ.get("S1_EGO_BIN", "ego-browser")

logger = logging.getLogger("s1_daemon")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(fh)

def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_json_strict(path, default):
    if not path.exists():
        return default
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except Exception as e:
        logger.error(f"LEDGER_CORRUPT_HALT file={path.name} err={e}")
        raise SystemExit(2)

def save_json_atomic(path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)

def extract_raw_block(text):
    for target_id in ("REAL_DOM_004", "REAL_DOM_003"):
        s_tag = f"===S1_AUTO_START:{target_id}==="
        e_tag = f"===S1_AUTO_END:{target_id}==="
        pos = 0
        while True:
            i = text.find(s_tag, pos)
            if i == -1:
                break
            j = text.find(e_tag, i + len(s_tag))
            if j == -1:
                break
            body = text[i + len(s_tag):j].strip()
            pos = j + len(e_tag)
            if "import platform" in body and "VERIFIED_EUNOS_2026" in body:
                # 세미콜론(;) 또는 줄바꿈으로 이어진 원본 파이썬 문장들을 정식 멀티라인 파이썬 코드로 보존
                raw_stmts = []
                for ln in body.splitlines():
                    for part in ln.split(";"):
                        p_str = part.strip()
                        if p_str:
                            raw_stmts.append(p_str)
                clean_code = "\n".join(raw_stmts)
                return [(target_id, clean_code)]
    return []

def scan_space0_live():
    r = subprocess.run([EGO_BIN, "run", "-f", str(ROOT / "scan_s0.mjs")], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    if r.returncode != 0:
        logger.error(f"EGO_SCAN_ERROR rc={r.returncode} err={r.stderr.strip()[:120]}")
        return [], 1
    for line in r.stdout.splitlines():
        if line.startswith("__S1_JSON__"):
            return json.loads(line[len("__S1_JSON__"):]), 0
    return [], 0

def approve_cmd(cmd_id):
    pend = load_json_strict(PENDING_FILE, {"pending": {}})
    if cmd_id not in pend.get("pending", {}):
        logger.error(f"APPROVE_NOT_FOUND id={cmd_id}")
        return 1
    pend["pending"][cmd_id]["approved"] = True
    pend["pending"][cmd_id]["approved_at"] = datetime.datetime.now().isoformat()
    save_json_atomic(PENDING_FILE, pend)
    logger.info(f"APPROVED_BY_CEO_ENTER id={cmd_id}")
    return 0

def execute_approved(state, pend):
    executed = state.setdefault("executed", {})
    for cid, item in list(pend.get("pending", {}).items()):
        if not item.get("approved"):
            continue
        if cid in executed:
            logger.info(f"SKIP_ALREADY_EXECUTED id={cid} sha={item['sha256'][:12]}")
            continue
        raw_code = item["code"].strip() + "\n"
        script_path = SANDBOX / f"{cid}.py"
        script_path.write_text(raw_code, encoding="utf-8")
        out_Path = SANDBOX / f"{cid}.out.txt"
        logger.info(f"SANDBOX_SCRIPT_WRITTEN id={cid} lines={len(raw_code.splitlines())} path={script_path.name}")
        r = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(SANDBOX),
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15
        )
        out_Path.write_text(r.stdout + r.stderr, encoding="utf-8")
        stdout_lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
        logger.info(
            f"LIVE_EXEC_DONE id={cid} rc={r.returncode} script={script_path.name} "
            f"out={out_Path.name} lines={len(stdout_lines)} stdout={' | '.join(stdout_lines)}"
        )
        executed[cid] = {
            "sha256": item["sha256"],
            "rc": r.returncode,
            "stdout": r.stdout.strip(),
            "script_code": raw_code,
            "script": str(script_path.relative_to(ROOT)),
            "out_file": str(out_Path.relative_to(ROOT)),
            "executed_at": datetime.datetime.now().isoformat()
        }
        del pend["pending"][cid]
        save_json_atomic(STATE_FILE, state)
        save_json_atomic(PENDING_FILE, pend)

        r_add = subprocess.run(["git", "add", "-f", "state/daemon_state.json", "logs/s1_daemon.log"], cwd=str(ROOT), capture_output=True, text=True)
        r_cm = subprocess.run(["git", "commit", "-m", f"S1 Auto-Commit after {cid} raw multi-line execution"], cwd=str(ROOT), capture_output=True, text=True)
        r_rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(ROOT), capture_output=True, text=True)
        sha_now = r_rev.stdout.strip()
        logger.info(f"GIT_COMMIT_DONE id={cid} rc={r_cm.returncode} commit_sha={sha_now}")

def run_cycles(cycles, interval):
    logger.info(f"PRECHECK ego-browser -> {EGO_BIN} mode=RAW_MULTILINE_EGO_SCAN_FILE")
    for i in range(1, cycles + 1):
        if KILL_FILE.exists():
            logger.warning(f"KILL_SWITCH_ACTIVE file={KILL_FILE.name} -> immediate stop at cycle={i}")
            return 0
        state = load_json_strict(STATE_FILE, {"seen": {}, "executed": {}})
        pend = load_json_strict(PENDING_FILE, {"pending": {}})

        tabs, err = scan_space0_live()
        for tb in tabs:
            blocks = extract_raw_block(tb.get("text", ""))
            for cid, code in blocks:
                h = sha256_text(code)
                if cid in state.get("executed", {}) and state["executed"][cid].get("sha256") == h:
                    logger.info(f"SKIP_ALREADY_EXECUTED id={cid} sha={h[:12]} label={tb.get('label')}")
                    continue
                seen = state.setdefault("seen", {}).get(cid)
                if not seen or seen.get("sha256") != h:
                    state["seen"][cid] = {"sha256": h, "count": 1, "label": tb.get("label")}
                    logger.info(f"STREAM_WAIT_1 id={cid} label={tb.get('label')} sha={h[:12]} lines={len(code.splitlines())}")
                else:
                    seen["count"] += 1
                    logger.info(f"STREAM_STABLE count={seen['count']} id={cid} label={tb.get('label')} sha={h[:12]}")
                    if seen["count"] >= 2 and cid not in pend["pending"]:
                        pend["pending"][cid] = {
                            "sha256": h,
                            "code": code,
                            "label": tb.get("label"),
                            "detected_at": datetime.datetime.now().isoformat(),
                            "approved": False
                        }
                        logger.info(f"HOLD_FOR_APPROVAL id={cid} label={tb.get('label')} sha={h[:12]} -> queued in pending_approvals.json")
                    elif cid in pend["pending"] and not pend["pending"][cid].get("approved"):
                        logger.info(f"HOLD_FOR_APPROVAL_WAITING id={cid} cycle={i} approved=False")

        save_json_atomic(STATE_FILE, state)
        save_json_atomic(PENDING_FILE, pend)
        execute_approved(state, pend)
        logger.info(f"CYCLE {i}/{cycles} tabs={len(tabs)} pending={len(pend.get('pending',{}))} executed={len(state.get('executed',{}))} errors={err}")
        if i < cycles:
            time.sleep(interval)
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=1)
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--approve", type=str, default="")
    args = ap.parse_args()
    if args.approve:
        raise SystemExit(approve_cmd(args.approve))
    raise SystemExit(run_cycles(args.cycles, args.interval))

if __name__ == "__main__":
    main()

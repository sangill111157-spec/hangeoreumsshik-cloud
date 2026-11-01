# -*- coding: utf-8 -*-
# S1 Zero-Capture Blackbox Launcher & SHA-8 Approval CLI (s1.py v1.3)
import subprocess, sys, json, datetime, hashlib
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent
QUEUE_FILE = BASE / "s1_ask_queue.json"
LEDGER_FILE = BASE / "s1_command_ledger.jsonl"
def now_kst(): return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def append_ledger(rec):
    rec["ts"] = now_kst()
    with LEDGER_FILE.open("a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
def approve_pending(req_id, sha8_input, approved_by="CEO_SANGILL_LEE_SHA8"):
    import s1_ego
    if s1_ego.kill_switch_active(): return {"ok": False, "code": "KILL_SWITCH_ACTIVE"}
    q = json.loads(QUEUE_FILE.read_text(encoding="utf-8")) if QUEUE_FILE.exists() else {}
    item = q.get(req_id)
    if not item: return {"ok": False, "code": "REQ_NOT_FOUND"}
    if item.get("status") != "PENDING": return {"ok": False, "code": "ALREADY_PROCESSED", "status": item.get("status")}
    exp_sha8 = item["prompt_sha256"][:8]
    if str(sha8_input).strip().lower() != exp_sha8.lower():
        append_ledger({"req_id": req_id, "cmd": "approve_ask", "status": "SHA8_MISMATCH", "ok": False})
        return {"ok": False, "code": "SHA8_MISMATCH", "expected_sha8": exp_sha8}
    item["status"] = "STARTED"; item["approved_by"] = approved_by; item["started_at"] = now_kst()
    QUEUE_FILE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
    append_ledger({"req_id": req_id, "cmd": "api_ego_ask", "space": item["space"], "prompt_sha256": item["prompt_sha256"], "wait": item["wait"], "approved_by": approved_by, "status": "STARTED", "ok": True})
    res = s1_ego.cmd_ask(int(item["space"]), item["prompt"], wait_sec=int(item["wait"]))
    final_st = "DONE" if res.get("ok") else "FAIL"
    item["status"] = final_st; item["completed_at"] = now_kst(); item["result"] = res
    QUEUE_FILE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
    append_ledger({"req_id": req_id, "cmd": "api_ego_ask", "space": item["space"], "prompt_sha256": item["prompt_sha256"], "status": final_st, "ok": bool(res.get("ok")), "ego_status": res.get("status")})
    return {"ok": bool(res.get("ok")), "status": final_st, "req_id": req_id, "approved_sha8": exp_sha8, "ego_result": res}
def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "approve":
        res = approve_pending(sys.argv[2], sys.argv[3])
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0 if res.get("ok") else 1)
    target = sys.argv[1] if len(sys.argv) > 1 else "s1_ego.py"
    args = sys.argv[2:] if len(sys.argv) > 1 else ["spaces"]
    t0 = now_kst()
    r = subprocess.run([sys.executable, target] + args, cwd=str(BASE), capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        cmd_str = target + " " + " ".join(args)
        err_md = "# S1.py Auto-Error Report (" + t0 + ")\n- Command: " + cmd_str + "\n- RC: " + str(r.returncode) + "\n## STDOUT\n```\n" + r.stdout[-3000:] + "\n```\n## STDERR\n```\n" + r.stderr[-3000:] + "\n```"
        (BASE / "S1_OUT.md").write_text(err_md, encoding="utf-8")
    print(r.stdout)
    if r.stderr: print(r.stderr, file=sys.stderr)
    sys.exit(r.returncode)
if __name__ == "__main__": main()

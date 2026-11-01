# -*- coding: utf-8 -*-
# S1 Zero-Capture Blackbox Launcher & Interactive Human SHA-8 Approval CLI (s1.py v1.4)
import subprocess, sys, json, datetime, hashlib
from pathlib import Path
import s1_ego
from s1_queue_store import now_kst, compute_Spec_hashes, append_ledger, read_queue, update_queue_item

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent

def approve_interactive(req_id):
    if not sys.stdin.isatty():
        append_ledger({"req_id": req_id, "cmd": "approve_ask", "status": "NOT_INTERACTIVE", "ok": False})
        return {"ok": False, "code": "NOT_INTERACTIVE", "message": "Human terminal TTY required (stdin is not a tty)"}

    if s1_ego.kill_switch_active():
        return {"ok": False, "code": "KILL_SWITCH_ACTIVE"}

    q = read_queue()
    item = q.get(req_id)
    if not item:
        return {"ok": False, "code": "REQ_NOT_FOUND"}
    if item.get("status") != "PENDING":
        return {"ok": False, "code": "ALREADY_PROCESSED", "status": item.get("status")}

    # 승인 시점 무결성 재검증: 저장된 prompt/space/wait로부터 SHA-256과 target_sig를 재계산하여 변조 여부 확인
    re_sent, re_psha, re_tsig = compute_Spec_hashes(item.get("space", 0), item.get("prompt", ""), item.get("wait", 0))
    if item.get("prompt") != re_sent or re_psha != item.get("prompt_sha256") or re_tsig != item.get("target_sig") or item.get("space") not in (2, 3):
        append_ledger({"req_id": req_id, "cmd": "approve_ask", "status": "QUEUE_INTEGRITY_MISMATCH", "ok": False})
        return {"ok": False, "code": "QUEUE_INTEGRITY_MISMATCH", "recomputed_sha256": re_psha, "stored_sha256": item.get("prompt_sha256")}

    print("============================================================", flush=True)
    print(f"[S1 HUMAN APPROVAL GATE] req_id={req_id}", flush=True)
    print(f"[Space {item['space']} | chat_id={s1_ego.KNOWN_CHATS.get(item['space'])}] origin={item.get('origin')} wait={item.get('wait')}s created={item.get('created_at')}", flush=True)
    print("----- 전송될 전문 -----", flush=True)
    print(s1_ego.defang(item["prompt"]), flush=True)
    print("-----------------------", flush=True)
    print(f"SHA-256: {item['prompt_sha256']}  (앞 8자리: {item['prompt_sha256'][:8]})", flush=True)
    ans = input("승인하려면 SHA 앞 8자리 입력 (취소: Enter): ").strip().lower()
    exp_sha8 = item["prompt_sha256"][:8].lower()
    if ans != exp_sha8:
        append_ledger({"req_id": req_id, "cmd": "approve_ask", "prompt_sha256": re_psha, "status": "SHA8_MISMATCH", "ok": False})
        return {"ok": False, "code": "SHA8_MISMATCH", "status": "PENDING_UNCHANGED"}

    # 원자적 잠금 안에서 최신 상태를 다시 확인하고 해당 항목만 STARTED로 전환 (동시 중복 승인 방지)
    def mark_started(q_map, cur):
        if not cur or cur.get("status") != "PENDING":
            return {"ok": False, "code": "CONCURRENT_ALREADY_STARTED", "status": (cur or {}).get("status")}
        cur["status"] = "STARTED"
        cur["approved_at"] = now_kst()
        cur["approval_mode"] = "INTERACTIVE_TTY_SHA8"
        return {"ok": True}

    st_check = update_queue_item(req_id, mark_started)
    if not st_check.get("ok"):
        return st_check

    append_ledger({"req_id": req_id, "cmd": "api_ego_ask", "space": item["space"], "prompt_sha256": re_psha, "wait": item["wait"], "approval_mode": "INTERACTIVE_TTY_SHA8", "status": "STARTED", "ok": True})

    res = None
    final_st = "FAIL"
    try:
        res = s1_ego.cmd_ask(int(item["space"]), item["prompt"], wait_sec=int(item["wait"]))
        final_st = "DONE" if res.get("ok") else "FAIL"
        return {"ok": bool(res.get("ok")), "status": final_st, "req_id": req_id, "ego_req_id": res.get("req_id"), "prompt_sha256": re_psha, "ego_result": res}
    finally:
        # try/finally 보장: 예외가 발생해도 고아 STARTED가 남지 않고 반드시 DONE 또는 FAIL로 해당 항목만 원자적 갱신
        def mark_finished(q_map, cur):
            if cur is not None:
                cur["status"] = final_st
                cur["completed_at"] = now_kst()
                cur["ego_req_id"] = (res or {}).get("req_id")
                cur["result"] = res
        update_queue_item(req_id, mark_finished)
        append_ledger({"req_id": req_id, "ego_req_id": (res or {}).get("req_id"), "cmd": "api_ego_ask", "space": item["space"], "prompt_sha256": re_psha, "status": final_st, "ok": final_st == "DONE", "ego_status": (res or {}).get("status")})

def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "approve":
        if len(sys.argv) > 3:
            print(json.dumps({"ok": False, "code": "CLI_SHA_ARG_FORBIDDEN", "message": "Pass only req_id; SHA-8 must be typed interactively on TTY"}, ensure_ascii=False, indent=2))
            sys.exit(1)
        res = approve_interactive(sys.argv[2])
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0 if res.get("ok") else 1)
    target = sys.argv[1] if len(sys.argv) > 1 else "s1_ego.py"
    args = sys.argv[2:] if len(sys.argv) > 1 else ["spaces"]
    r = subprocess.run([sys.executable, target] + args, cwd=str(BASE), capture_output=True, text=True, encoding="utf-8")
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    sys.exit(r.returncode)

if __name__ == "__main__":
    main()

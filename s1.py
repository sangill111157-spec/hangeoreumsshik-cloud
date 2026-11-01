# -*- coding: utf-8 -*-
# S1 Zero-Capture Blackbox Launcher & Interactive Human SHA-8 Approval CLI (s1.py v1.4.1)
import subprocess, sys, json, datetime, hashlib
from pathlib import Path
import s1_ego
from s1_queue_store import now_kst, compute_Spec_hashes, append_ledger, read_queue, update_queue_item

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent
TTY_TRANSCRIPT_FILE = BASE / "logs" / "s1_tty_approval_transcript.log"

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

    try:
        re_sent, re_psha, re_tsig, re_chat_id = compute_Spec_hashes(item.get("space"), item.get("prompt"), item.get("wait"))
    except Exception as e:
        append_ledger({"req_id": req_id, "cmd": "approve_ask", "status": "QUEUE_INTEGRITY_MISMATCH", "error": str(e), "ok": False})
        return {"ok": False, "code": "QUEUE_INTEGRITY_MISMATCH", "error": str(e)}

    if (
        item.get("prompt") != re_sent
        or re_psha != item.get("prompt_sha256")
        or re_tsig != item.get("target_sig")
        or item.get("chat_id") != re_chat_id
        or item.get("space") not in (2, 3)
    ):
        append_ledger({"req_id": req_id, "cmd": "approve_ask", "status": "QUEUE_INTEGRITY_MISMATCH", "recomputed_sha256": re_psha, "stored_sha256": item.get("prompt_sha256"), "ok": False})
        return {"ok": False, "code": "QUEUE_INTEGRITY_MISMATCH", "recomputed_sha256": re_psha, "stored_sha256": item.get("prompt_sha256")}

    # 화면에 표시한 스냅샷 고정
    snap_space = int(item["space"])
    snap_chat_id = re_chat_id
    snap_wait = int(item["wait"])
    snap_prompt = re_sent
    snap_psha = re_psha
    snap_tsig = re_tsig

    banner_lines = [
        "============================================================",
        f"[S1 HUMAN APPROVAL GATE] req_id={req_id}",
        f"[Space {snap_space} | chat_id={snap_chat_id}] origin={item.get('origin')} wait={snap_wait}s created={item.get('created_at')}",
        "----- 전송될 전문 -----",
        s1_ego.defang(snap_prompt),
        "-----------------------",
        f"SHA-256: {snap_psha}  (앞 8자리: {snap_psha[:8]})",
    ]
    banner_txt = "\n".join(banner_lines)
    print(banner_txt, flush=True)
    prompt_line = "승인하려면 SHA 앞 8자리 입력 (취소: Enter): "
    ans = input(prompt_line).strip().lower()

    with TTY_TRANSCRIPT_FILE.open("a", encoding="utf-8") as tf:
        tf.write(banner_txt + "\n" + prompt_line + ans + f"  # at {now_kst()}\n\n")

    exp_sha8 = snap_psha[:8].lower()
    if ans != exp_sha8:
        append_ledger({"req_id": req_id, "cmd": "approve_ask", "prompt_sha256": snap_psha, "typed_input": ans, "status": "SHA8_MISMATCH", "ok": False})
        return {"ok": False, "code": "SHA8_MISMATCH", "status": "PENDING_UNCHANGED"}

    # 잠금 안에서 최신 큐 항목이 TTY 대기 중 변경되지 않았는지 스냅샷 전체 비교 후 STARTED로 전환
    def mark_started(q_map, cur):
        if not cur or cur.get("status") != "PENDING":
            return {"ok": False, "code": "CONCURRENT_ALREADY_STARTED", "status": (cur or {}).get("status")}
        try:
            cur_sent, cur_psha, cur_tsig, cur_cid = compute_Spec_hashes(cur.get("space"), cur.get("prompt"), cur.get("wait"))
        except Exception:
            return {"ok": False, "code": "SNAPSHOT_CHANGED_DURING_TTY_WAIT"}
        if (
            cur.get("prompt") != snap_prompt
            or cur.get("space") != snap_space
            or cur.get("wait") != snap_wait
            or cur.get("chat_id") != snap_chat_id
            or cur.get("prompt_sha256") != snap_psha
            or cur.get("target_sig") != snap_tsig
            or cur_psha != snap_psha
            or cur_tsig != snap_tsig
            or cur_cid != snap_chat_id
        ):
            return {"ok": False, "code": "SNAPSHOT_CHANGED_DURING_TTY_WAIT"}
        cur["status"] = "STARTED"
        cur["approved_at"] = now_kst()
        cur["approval_mode"] = "INTERACTIVE_TTY_SHA8"
        return {"ok": True}

    st_check = update_queue_item(req_id, mark_started)
    if not st_check.get("ok"):
        append_ledger({"req_id": req_id, "cmd": "approve_ask", "status": st_check.get("code", "START_REJECTED"), "ok": False})
        return st_check

    res = None
    final_st = "FAIL"
    try:
        append_ledger({"req_id": req_id, "cmd": "api_ego_ask", "space": snap_space, "chat_id": snap_chat_id, "prompt_sha256": snap_psha, "target_sig": snap_tsig, "wait": snap_wait, "approval_mode": "INTERACTIVE_TTY_SHA8", "status": "STARTED", "ok": True})
        # 승인된 스냅샷(snap_space, snap_prompt, snap_wait, snap_chat_id) 그대로 실행
        res = s1_ego.cmd_ask(snap_space, snap_prompt, wait_sec=snap_wait)
        if res.get("chat_id") and res.get("chat_id") != snap_chat_id:
            final_st = "FAIL"
            res["ok"] = False
            res["code"] = "CHAT_ID_MISMATCH_ON_EXEC"
        else:
            final_st = "DONE" if res.get("ok") else "FAIL"
        return {"ok": final_st == "DONE", "status": final_st, "req_id": req_id, "ego_req_id": (res or {}).get("req_id"), "prompt_sha256": snap_psha, "target_sig": snap_tsig, "chat_id": snap_chat_id, "ego_result": res}
    finally:
        def mark_finished(q_map, cur):
            if cur is not None:
                cur["status"] = final_st
                cur["completed_at"] = now_kst()
                cur["ego_req_id"] = (res or {}).get("req_id")
                cur["result"] = res
        update_queue_item(req_id, mark_finished)
        append_ledger({"req_id": req_id, "ego_req_id": (res or {}).get("req_id"), "cmd": "api_ego_ask", "space": snap_space, "chat_id": snap_chat_id, "prompt_sha256": snap_psha, "status": final_st, "ok": final_st == "DONE", "ego_status": (res or {}).get("status")})

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
    t0 = now_kst()
    r = subprocess.run([sys.executable, target] + args, cwd=str(BASE), capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        cmd_str = target + " " + " ".join(args)
        err_md = "# S1.py Auto-Error Report (" + t0 + ")\n- Command: " + cmd_str + "\n- RC: " + str(r.returncode) + "\n## STDOUT\n```\n" + r.stdout[-3000:] + "\n```\n## STDERR\n```\n" + r.stderr[-3000:] + "\n```"
        (BASE / "S1_OUT.md").write_text(err_md, encoding="utf-8")
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    sys.exit(r.returncode)

if __name__ == "__main__":
    main()

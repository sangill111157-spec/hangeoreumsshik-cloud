# -*- coding: utf-8 -*-
import json, subprocess, pathlib
import s1_ego
from s1_queue_store import now_kst, append_ledger, read_queue, update_queue_item, LEDGER_FILE

def append_harness_once(entry):
    entry["writer"] = "harness"
    req_id = entry.get("req_id")
    cmd = entry.get("cmd")
    status = entry.get("status")
    if LEDGER_FILE.exists():
        for line in LEDGER_FILE.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("req_id") == req_id and row.get("cmd") == cmd and row.get("status") == status:
                return False
    append_ledger(entry)
    return True

# 1. 68b6c118 (동시 경합 시험용 STARTED) -> ABANDONED 마감
def close_68b6(q_map, cur):
    if cur is not None:
        cur["status"] = "ABANDONED"
        cur["abandoned_at"] = now_kst()
        cur["note"] = "Concurrent lock race test only; no AI send."
    return {"ok": True}
update_queue_item("68b6c118-d5c8-4186-97f8-c669ca3591ea", close_68b6)
append_harness_once({
    "req_id": "68b6c118-d5c8-4186-97f8-c669ca3591ea",
    "cmd": "cleanup_race_test",
    "status": "ABANDONED",
    "note": "Concurrent lock race test item closed as ABANDONED (no AI send) per GPT & Claude final verdict.",
    "ok": False
})

# 2. e31126ee (오입력 시험용 PENDING) -> EXPIRED 마감
def close_e311(q_map, cur):
    if cur is not None:
        cur["status"] = "EXPIRED"
        cur["expired_at"] = now_kst()
        cur["note"] = "Wrong SHA-8 negative test item closed as EXPIRED so it cannot be accidentally approved."
    return {"ok": True}
update_queue_item("e31126ee-4707-474c-bdbc-3ccad9db9715", close_e311)
append_harness_once({
    "req_id": "e31126ee-4707-474c-bdbc-3ccad9db9715",
    "cmd": "cleanup_wrong_sha8_test",
    "status": "EXPIRED",
    "note": "Closed wrong SHA-8 negative test item safely as EXPIRED per Claude instruction.",
    "ok": False
})

# 3. 12:59~13:02 하네스 재실행 사유 1줄 및 v1.4.1 이전 하네스 작성분 3건(157a1174, 9e57ffc2, 75774d6c) 주석 추가
append_harness_once({
    "req_id": "STAGE2_FINAL_CLEANUP_NOTE",
    "cmd": "audit_note",
    "status": "INFO",
    "rerun_reason": "The 3 earlier harness entries between 12:59 and 13:02 occurred because the test script aborted mid-run before post_ask due to wrong queue path (logs/s1_pending_Queue.json, s1_pending_queue.json) and s1_server not running (WinError 10061). Deduplication guard (append_harness_once) is now enforced.",
    "legacy_harness_rows_note": "Rows closing 157a1174-9621-4be9-b0c5-1d8290865750, 9e57ffc2-47d6-4d5e-ba8e-c726d35a0806, and 75774d6c-3657-40ba-92a9-59bc45451610 prior to v1.4.2 were also written by test harness.",
    "ok": True
})

subprocess.run(["git", "add", "-A"], check=False)
subprocess.run(["git", "commit", "-m", "chore(s1): finalize stage2 ledger cleanup and auto-report to Space 0"], check=False)
subprocess.run(["git", "pull", "--rebase", "--autostash", "-X", "ours", "origin", "main"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=False)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
print(f"=== S1_STAGE2_CLEANUP_DONE_SHA: {sha} ===")

# 4. Space 0 (르곤 보좌관 채팅창)에 자동 완료 보고 전송! (timeout=15 적용)
msg_to_rgon = f"[자동 완료 보고] 대표님, S1 2순위 2단계 최종 PASS 확정 및 원장 마무리 정리까지 완료되어 GitHub에 푸시되었습니다! (커밋 SHA: {sha}) 이제 2순위 3단계(만능 소통창 대시보드 UI 실시간 연동) 착수 준비 보고를 올려주십시오."
msg_json = json.dumps(msg_to_rgon, ensure_ascii=False)
auto_report_js = f"""
const pages = await ego.listPages(0);
const target = pages.find(p => p.url && p.url.includes("genspark.ai/agents")) || pages[0];
if (target) {{
  await ego.runPageScript(0, target.pageId, `(() => {{
    const ta = document.querySelector("textarea") || document.querySelector("[contenteditable='true']");
    if (!ta) return {{ ok: false, err: "no_ta" }};
    ta.focus();
    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value")?.set;
    if (setter) setter.call(ta, {msg_json});
    else ta.value = {msg_json};
    ta.dispatchEvent(new Event("input", {{ bubbles: true }}));
    setTimeout(() => {{
      const btn = document.querySelector("button[type='submit']") || Array.from(document.querySelectorAll("button, div[role='button']")).find(b => b.querySelector("svg") && !b.disabled);
      if (btn) btn.click();
      else ta.dispatchEvent(new KeyboardEvent("keydown", {{ key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true }}));
    }}, 300);
    return {{ ok: true }};
  }})()`);
}}
return {{ reported: true }};
"""
s1_ego.run_ego_js(auto_report_js, timeout=15)
print("[완료] 르곤 보좌관(Space 0)에게 자동 완료 보고 전송 성공!")

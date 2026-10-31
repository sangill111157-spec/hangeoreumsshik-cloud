# -*- coding: utf-8 -*-
# S1 CEO Direct Approval Harness v3.4 (s1_approve_harness.py)
import datetime, hashlib, json, os, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
PENDING_FILE = BASE / "pending_stability.json"
APPROVAL_FILE = BASE / "APPROVED_IDS.json"
TRUSTED_SPACE_ID = 0
TRUSTED_CHAT_ID = "c1647638-2531-43db-a059-c153d8da14d9"

def main():
    if len(sys.argv) < 2:
        raise SystemExit("사용법: python s1_approve_harness.py <블록ID>")
    if not PENDING_FILE.exists():
        raise SystemExit("No pending_stability.json found.")
    pend = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    target_id = sys.argv[1].strip()
    if target_id not in pend:
        raise SystemExit(f"Target ID {target_id!r} not in pending_stability.json")
    item = pend[target_id]
    body, sha = item.get("body", ""), item["sha256"]
    if hashlib.sha256(body.encode("utf-8")).hexdigest() != sha:
        raise SystemExit("PENDING_TAMPERED: 표시 본문과 해시 불일치 -> 승인 거부")
    if item.get("count", 0) < 2:
        raise SystemExit("아직 안정화 전(count < 2) -> 승인 불가")
    print(f"=== Pending Block: {target_id} (count={item.get('count')}, sha256={sha}) ===")
    print(body)
    ans = input(f"승인하려면 SHA 앞 8자리({sha[:8]})를 직접 입력: ").strip()
    if ans != sha[:8]:
        print("REJECTED: SHA prefix mismatch")
        raise SystemExit(1)
    now_iso = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    data = json.loads(APPROVAL_FILE.read_text(encoding="utf-8")) if APPROVAL_FILE.exists() else {"approvals": {}}
    data.setdefault("approvals", {})[target_id] = {
        "sha256": sha,
        "space": TRUSTED_SPACE_ID,
        "chat_id": TRUSTED_CHAT_ID,
        "approved_by": "CEO_SANGILL_LEE_SHA8_VERIFIED",
        "approved_at": now_iso,
    }
    tmp = APPROVAL_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, APPROVAL_FILE)
    print(f"APPROVED {target_id} sha256={sha}")

if __name__ == "__main__":
    main()

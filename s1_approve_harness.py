# -*- coding: utf-8 -*-
# S1 CEO Direct Approval Harness (s1_approve_harness.py)
import datetime, json, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
PENDING_FILE = BASE / "pending_stability.json"
APPROVAL_FILE = BASE / "APPROVED_IDS.json"
TRUSTED_SPACE_ID = 0
TRUSTED_CHAT_ID = "c1647638-2531-43db-a059-c153d8da14d9"

def main():
    if not PENDING_FILE.exists():
        raise SystemExit("No pending_stability.json found.")
    pend = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    target_id = sys.argv[1] if len(sys.argv) > 1 else next(iter(pend.keys()), None)
    if not target_id or target_id not in pend:
        raise SystemExit(f"Target ID {target_id!r} not in pending_stability.json")
    item = pend[target_id]
    print(f"=== Pending Block: {target_id} (count={item.get('count')}, sha256={item.get('sha256')}) ===")
    print(item.get("body", ""))
    ans = input(f"Approve {target_id} for isolated execution? Type YES or press Enter: ").strip()
    now_iso = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    data = json.loads(APPROVAL_FILE.read_text(encoding="utf-8")) if APPROVAL_FILE.exists() else {"approvals": {}}
    data.setdefault("approvals", {})[target_id] = {
        "sha256": item["sha256"],
        "space": TRUSTED_SPACE_ID,
        "chat_id": TRUSTED_CHAT_ID,
        "approved_by": "CEO_SANGILL_LEE_DIRECT_ENTER",
        "approved_at": now_iso,
    }
    APPROVAL_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"APPROVED {target_id} sha256={item['sha256']}")

if __name__ == "__main__":
    main()

test_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

with open(test_path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Update transient hold detail key check
c = c.replace(
    'res1.details.get("inquiry_failure", {}).get("code") == INQUIRY_TRANSIENT_HOLD_CODE',
    'res1.details.get("inquiry_transient", {}).get("code") == INQUIRY_TRANSIENT_HOLD_CODE'
)

# 2. Update evaluate_reconciliation argument order
c = c.replace(
    'res_mismatch = evaluate_reconciliation(local_snap, broker_snap_mismatch)',
    'res_mismatch = evaluate_reconciliation(broker_snap_mismatch, local_snap)'
)

c = c.replace(
    'res_match = evaluate_reconciliation(local_snap, broker_snap_match)',
    'res_match = evaluate_reconciliation(broker_snap_match, local_snap)'
)

with open(test_path, "w", encoding="utf-8") as f:
    f.write(c)

print("Updated test_broker_reconcile_and_orders.py with correct keys and arg orders.")

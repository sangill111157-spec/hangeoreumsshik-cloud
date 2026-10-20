test_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"
with open(test_path, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("reconcile_positions_and_cash", "evaluate_reconciliation")
c = c.replace(".run_single_cycle()", ".run_once()")

with open(test_path, "w", encoding="utf-8") as f:
    f.write(c)

print("Updated function names in test_broker_reconcile_and_orders.py")

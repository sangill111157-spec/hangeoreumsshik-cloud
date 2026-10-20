test_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"
with open(test_path, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("    OpenOrderSnapshot,\n", "")
c = c.replace("    adapter = MagicMock()\n    loop = ReconciliationLoop(adapter=adapter, interval_seconds=30)\n\n", "")

with open(test_path, "w", encoding="utf-8") as f:
    f.write(c)
print("Updated test_broker_reconcile_and_orders.py for ruff")

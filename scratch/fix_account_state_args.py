test_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

with open(test_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("cash_balance_usd=10000.0,\n            positions={\"NVDA\": 10},\n            holding_qty=10,", "orderable_cash_usd=10000.0,\n        positions={\"NVDA\": 10},")
content = content.replace("cash_balance_usd=10000.0,\n            positions={},\n            holding_qty=0,", "orderable_cash_usd=10000.0,\n        positions={},")

with open(test_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated AccountState instantiation in tests!")

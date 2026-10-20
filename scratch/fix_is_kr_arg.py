test_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

with open(test_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("                is_kr=True,\n", "")

with open(test_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully removed is_kr argument from test call!")

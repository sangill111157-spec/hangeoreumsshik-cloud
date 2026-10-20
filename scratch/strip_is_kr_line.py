test_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

with open(test_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for l in lines:
    if "is_kr=True" in l:
        continue
    new_lines.append(l)

with open(test_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Removed is_kr line successfully!")

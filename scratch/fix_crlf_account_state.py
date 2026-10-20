test_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

with open(test_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for l in lines:
    if "cash_balance_usd=10000.0" in l:
        new_lines.append(l.replace("cash_balance_usd=10000.0", "orderable_cash_usd=10000.0"))
    elif "holding_qty=10" in l or "holding_qty=0" in l:
        continue  # skip holding_qty line
    else:
        new_lines.append(l)

with open(test_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Successfully replaced AccountState fields line by line!")

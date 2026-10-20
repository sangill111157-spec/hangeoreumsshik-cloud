test_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

with open(test_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = [l for l in lines if 'patch("app.services.auto_trader.get_kis_broker"' not in l]

with open(test_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Successfully removed invalid auto_trader patch line!")

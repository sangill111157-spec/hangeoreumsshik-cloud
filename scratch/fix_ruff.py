# Fix conftest.py
conftest_path = r"C:\trading\package\nvda_trading_system\backend\tests\conftest.py"
with open(conftest_path, "r", encoding="utf-8") as f:
    conftest_content = f.read()

if "import pytest" not in conftest_content:
    conftest_content = "import pytest\n" + conftest_content
    with open(conftest_path, "w", encoding="utf-8") as f:
        f.write(conftest_content)
    print("Fixed conftest.py")

# Fix test_broker_reconcile_and_orders.py
test_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"
with open(test_path, "r", encoding="utf-8") as f:
    test_content = f.read()

test_content = test_content.replace("from app.services import auto_trader, kis_broker", "from app.services import kis_broker")
with open(test_path, "w", encoding="utf-8") as f:
    f.write(test_content)
print("Fixed test_broker_reconcile_and_orders.py")

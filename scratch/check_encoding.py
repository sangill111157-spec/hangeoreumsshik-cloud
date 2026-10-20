import os

files = [
    r"C:\trading\package\nvda_trading_system\backend\app\main.py",
    r"C:\trading\package\nvda_trading_system\backend\app\services\auto_trader.py",
    r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py",
    r"C:\trading\package\nvda_trading_system\backend\app\services\reconciler.py",
    r"C:\trading\package\nvda_trading_system\backend\tests\conftest.py",
    r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py",
]

all_zero = True
for f in files:
    with open(f, "rb") as fp:
        raw = fp.read()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8", errors="replace")
    fffd_count = text.count("\ufffd")
    fname = os.path.basename(f)
    print(f"{fname:35s}: BOM={has_bom!s:5s} | U+FFFD count={fffd_count}")
    if fffd_count > 0:
        all_zero = False

print(f"\nAll files U+FFFD == 0: {all_zero}")

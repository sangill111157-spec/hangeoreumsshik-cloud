# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
at_path = os.path.join(backend_dir, 'app', 'services', 'auto_trader.py')
sc_path = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')

# 1. Update auto_trader.py
with open(at_path, 'r', encoding='utf-8') as f:
    at_code = f.read()

# Update Literal
at_code = at_code.replace(
    'order_state: Literal["ORDER_ACCEPTED", "ORDER_REJECTED", "ORDER_UNKNOWN"]',
    'order_state: Literal["ORDER_ACCEPTED", "ORDER_REJECTED", "ORDER_UNKNOWN", "DRY_RUN_ACCEPTED"]'
)

# Update return in dry_run
at_code = at_code.replace(
    'return {"success": True, "trade": trade, "dry_run": True, "order_state": "ORDER_ACCEPTED"}',
    'return {"success": True, "trade": trade, "dry_run": True, "order_state": "DRY_RUN_ACCEPTED"}'
)

with open(at_path, 'w', encoding='utf-8') as f:
    f.write(at_code)

# 2. Update scheduler.py
with open(sc_path, 'r', encoding='utf-8') as f:
    sc_code = f.read()

sc_code = sc_code.replace(
    'order_state = "ORDER_ACCEPTED" if trade_result.get("success") else "ORDER_REJECTED"',
    'order_state = ("DRY_RUN_ACCEPTED" if is_dry_run else "ORDER_ACCEPTED") if trade_result.get("success") else "ORDER_REJECTED"'
)

sc_code = sc_code.replace(
    'elif order_state == "ORDER_ACCEPTED":',
    'elif order_state in ("ORDER_ACCEPTED", "DRY_RUN_ACCEPTED"):'
)

with open(sc_path, 'w', encoding='utf-8') as f:
    f.write(sc_code)

# 3. Add regression test in tests/test_auto_trader_toggle.py
toggle_test_p = os.path.join(backend_dir, 'tests', 'test_auto_trader_toggle.py')
with open(toggle_test_p, 'r', encoding='utf-8') as f:
    tt_code = f.read()

if "test_dry_run_returns_dry_run_accepted_not_order_accepted" not in tt_code:
    new_test = '''

def test_dry_run_returns_dry_run_accepted_not_order_accepted():
    """DRY_RUN 체결 결과의 order_state는 DRY_RUN_ACCEPTED이며 ORDER_ACCEPTED가 아니다."""
    from unittest.mock import patch
    trader = AutoTrader(dry_run=True)
    with patch.object(trader, "_get_current_price", return_value=120.0), \\
         patch.object(trader, "_send_telegram"):
        res = trader.execute_trade("NVDA", "BUY", shares=1)
        assert res.get("order_state") == "DRY_RUN_ACCEPTED"
        assert res.get("order_state") != "ORDER_ACCEPTED"
'''
    with open(toggle_test_p, 'a', encoding='utf-8') as f:
        f.write(new_test)

print("Patch applied successfully.")

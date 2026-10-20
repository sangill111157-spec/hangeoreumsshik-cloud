# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sc_test = os.path.join(backend_dir, 'tests', 'test_scheduler_sizing.py')

with open(sc_test, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'assert res3.get("order_state") == "ORDER_ACCEPTED"',
    'assert res3.get("order_state") == "DRY_RUN_ACCEPTED"'
)

with open(sc_test, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated test_execute_trade_all_returns_have_order_state to assert DRY_RUN_ACCEPTED.")

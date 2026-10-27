# -*- coding: utf-8 -*-
import os, sys, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
conftest_p = os.path.join(backend_dir, 'tests', 'conftest.py')

with open(conftest_p, 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'snapshot = \{(.*?)\}', text, re.DOTALL)
if m:
    block = m.group(1)
    keys = re.findall(r'"([a-zA-Z0-9_]+)":', block)
    print(f"Total keys: {len(keys)}")
    print("Keys list:", keys)
    targets = ["_stop_loss_lock_daily_alert", "_kr_stock_stop_loss_alert", "_avg_price_zero_alert"]
    for t in targets:
        print(f"  {t} in snapshot: {t in keys}")

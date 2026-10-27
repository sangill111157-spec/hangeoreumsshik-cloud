# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')

with open(os.path.join(backend_dir, 'app/services/scheduler.py'), 'r', encoding='utf-8') as f:
    sched_lines = f.readlines()

print("=== app/services/scheduler.py lines 240 to 310 ===")
for i in range(239, min(310, len(sched_lines))):
    print(f"{i+1:4d}: {sched_lines[i]}", end="")

print("\n=== app/services/auto_trader.py lines 130 to 180 ===")
with open(os.path.join(backend_dir, 'app/services/auto_trader.py'), 'r', encoding='utf-8') as f:
    trader_lines = f.readlines()
for i in range(129, min(180, len(trader_lines))):
    print(f"{i+1:4d}: {trader_lines[i]}", end="")

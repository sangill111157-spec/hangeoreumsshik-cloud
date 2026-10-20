# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

with open(os.path.join(backend_dir, 'app/services/scheduler.py'), 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== scheduler.py lines 100 to 180 ===")
for i in range(99, min(180, len(lines))):
    print(f"{i+1:4d}: {lines[i]}", end="")

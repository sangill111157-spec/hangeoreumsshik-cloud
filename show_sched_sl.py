# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

with open(os.path.join(backend_dir, 'app/services/scheduler.py'), 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== app/services/scheduler.py lines 400 to 520 ===")
for i in range(399, min(520, len(lines))):
    print(f"{i+1:4d}: {lines[i]}", end="")

# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

with open(os.path.join(backend_dir, 'tests/test_scheduler_sizing.py'), 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== tests/test_scheduler_sizing.py lines 700 to 740 ===")
for i in range(699, min(740, len(lines))):
    print(f"{i+1:4d}: {lines[i]}", end="")

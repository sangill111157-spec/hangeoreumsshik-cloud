# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

p1 = os.path.join(backend_dir, 'tests', 'test_scheduler_sizing.py')
with open(p1, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

for i, l in enumerate(lines, 1):
    if "def test_stop_loss_corrupt_state_file_fails_closed" in l:
        print(f"Found test at line {i}")
        for j in range(i-1, min(i+40, len(lines))):
            print(f"{j+1:4d}: {lines[j]}", end="")
        break

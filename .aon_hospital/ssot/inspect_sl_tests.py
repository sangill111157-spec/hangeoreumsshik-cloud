# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. Inspect test_scheduler_sizing.py (L795-850) & test_stop_loss_disabled_alert.py")
print("================================================================================")

p1 = os.path.join(backend_dir, 'tests', 'test_scheduler_sizing.py')
with open(p1, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()
print("--- test_scheduler_sizing.py L795-850 ---")
for i in range(794, min(850, len(lines))):
    print(f"{i+1:4d}: {lines[i]}", end="")

p2 = os.path.join(backend_dir, 'tests', 'test_stop_loss_disabled_alert.py')
with open(p2, 'r', encoding='utf-8', errors='replace') as f:
    lines2 = f.readlines()
print("\n--- test_stop_loss_disabled_alert.py full ---")
for i, l in enumerate(lines2, 1):
    print(f"{i:4d}: {l}", end="")

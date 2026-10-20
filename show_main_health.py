# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

with open(os.path.join(backend_dir, 'app/main.py'), 'r', encoding='utf-8') as f:
    main_lines = f.readlines()

print("=== app/main.py health_check (lines 160 to 220) ===")
for i in range(159, min(220, len(main_lines))):
    print(f"{i+1:4d}: {main_lines[i]}", end="")

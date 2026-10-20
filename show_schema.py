# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

with open(os.path.join(backend_dir, 'app/schemas/nvda.py'), 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== app/schemas/nvda.py HealthCheckResponse ===")
for i in range(335, min(365, len(lines))):
    print(f"{i+1:4d}: {lines[i]}", end="")

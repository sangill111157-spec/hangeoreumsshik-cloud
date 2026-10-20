# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\risk.py', 'r', encoding='utf-8') as f:
    r_lines = f.readlines()
print('=== risk.py: get_risk_score (lines 50~68) ===')
for i in range(48, min(len(r_lines), 68)):
    print(f"{i+1:4d}: " + r_lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\rebalance.py', 'r', encoding='utf-8') as f:
    reb_lines = f.readlines()
print('\n=== rebalance.py: get_rebalance_plan (lines 45~65) ===')
for i in range(45, min(len(reb_lines), 65)):
    print(f"{i+1:4d}: " + reb_lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== App.tsx lines 980~1030 ===')
for i in range(975, 1030):
    print(f"Line {i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

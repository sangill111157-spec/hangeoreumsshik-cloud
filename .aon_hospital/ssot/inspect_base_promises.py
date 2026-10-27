# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(180, 260):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

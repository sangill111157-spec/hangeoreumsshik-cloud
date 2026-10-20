# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== Scanner card in App.tsx (around lines 930~970) ===')
for i in range(930, 970):
    print(f"Line {i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

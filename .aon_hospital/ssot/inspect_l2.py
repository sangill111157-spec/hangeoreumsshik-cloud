# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== 1. App.tsx lines 820~870 ===')
for i in range(815, 870):
    print(f"Line {i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

print('\n=== 2. App.tsx lines 920~940 ===')
for i in range(920, 940):
    print(f"Line {i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

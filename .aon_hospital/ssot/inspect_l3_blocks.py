# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== App.tsx lines 785~835 ===')
for i in range(784, 835):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

print('\n=== App.tsx lines 840~935 ===')
for i in range(840, 935):
    if any(k in lines[i] for k in ['risk', 'Risk', 'traderMode', 'volume', 'priceDisplay', 'hasPrice']):
        print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

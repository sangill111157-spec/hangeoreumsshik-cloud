# -*- coding: utf-8 -*-
import subprocess

# 1. git show 5c5aa50
print('=== 1. git show 5c5aa50 -- src/App.tsx ===')
out_l3 = subprocess.getoutput(r'cd /d C:\trading\package\nvda_trading_system\nvda-trading-dashboard && git show 5c5aa50 -- src/App.tsx')
print(out_l3)

# 2. git status --short
print('\n=== 2. git status --short (backend & frontend) ===')
print('[Backend]:')
print(subprocess.getoutput(r'cd /d C:\trading\package\nvda_trading_system\backend && git status --short'))
print('\n[Frontend]:')
print(subprocess.getoutput(r'cd /d C:\trading\package\nvda_trading_system\nvda-trading-dashboard && git status --short'))

# 3. L-4 Inspect trader card remaining_trades in App.tsx
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('\n=== 3. Trader card lines 930~955 in App.tsx ===')
for i in range(929, min(len(lines), 955)):
    print(f"{i+1:4d}: {lines[i]}", end='')

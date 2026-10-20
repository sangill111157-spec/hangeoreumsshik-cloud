# -*- coding: utf-8 -*-
import subprocess

def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out.decode('utf-8', errors='ignore')

# 1. git show 5c5aa50
print('=== 1. git show 5c5aa50 -- src/App.tsx ===')
print(run_cmd(r'cd /d C:\trading\package\nvda_trading_system\nvda-trading-dashboard && git show 5c5aa50 -- src/App.tsx'))

# 2. git status --short
print('\n=== 2. git status --short ===')
print('[Backend]:')
print(run_cmd(r'cd /d C:\trading\package\nvda_trading_system\backend && git status --short'))
print('\n[Frontend]:')
print(run_cmd(r'cd /d C:\trading\package\nvda_trading_system\nvda-trading-dashboard && git status --short'))

# 3. L-4 Inspect trader card in App.tsx
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('\n=== 3. Trader card lines 930~955 in App.tsx ===')
for i in range(929, min(len(lines), 955)):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

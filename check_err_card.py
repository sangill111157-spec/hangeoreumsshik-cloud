# -*- coding: utf-8 -*-
# 1. Check setMasterSignalError in App.tsx
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== 1. setMasterSignalError in App.tsx ===')
for i, line in enumerate(lines):
    if 'setMasterSignalError' in line:
        print(f"Line {i+1:4d}: {line.strip()}")

print('\n=== 2. Master Signal Error Card JSX in App.tsx (around lines 980~1020) ===')
for i, line in enumerate(lines):
    if 'masterSignalError' in line and ('<' in line or 'div' in line or 'p className' in line):
        for j in range(max(0, i-2), min(len(lines), i+15)):
            print(f"Line {j+1:4d}: " + lines[j].encode('ascii', errors='backslashreplace').decode('ascii'), end='')
        print('\n---')
        break

# -*- coding: utf-8 -*-
# 1. K-1: BASE_URL in api.ts
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\services\api.ts', 'r', encoding='utf-8') as f:
    api_lines = f.readlines()
print('=== 1. BASE_URL in api.ts ===')
for i in range(min(20, len(api_lines))):
    print(f"{i+1:2d}: {api_lines[i]}", end='')

# 2. K-4: Error mapping in App.tsx (fetchMasterSignal)
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()
print('\n=== 2. fetchMasterSignal error handling in App.tsx ===')
for i, line in enumerate(app_lines):
    if 'const fetchMasterSignal' in line:
        for j in range(i, min(len(app_lines), i+30)):
            print(f"{j+1:4d}: {app_lines[j]}", end='')
        break

# 3. K-5: StrictMode in main.tsx
import os
for candidate in ['main.tsx', 'index.tsx', 'App.tsx']:
    p = os.path.join(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src', candidate)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            c = f.read()
        print(f"\n=== 3. StrictMode in {candidate} ===")
        print("StrictMode found:", 'StrictMode' in c)
        if 'StrictMode' in c:
            for l in c.split('\n'):
                if 'StrictMode' in l:
                    print("  ", l.strip())

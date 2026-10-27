# -*- coding: utf-8 -*-
import urllib.request, json

# 1. Inspect api.ts Price interface
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\services\api.ts', 'r', encoding='utf-8') as f:
    api_lines = f.readlines()

print('=== 1. Price interface in api.ts ===')
for i, l in enumerate(api_lines):
    if 'StockPrice' in l or 'Price' in l or 'fetchPrice' in l:
        print(f"Line {i+1:4d}: {l.strip()}")

# 2. JSX rendering for price, change, volume in App.tsx
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

print('\n=== 2. Price card JSX in App.tsx (lines 835~855) ===')
for i in range(835, 855):
    print(f"{i+1:4d}: {app_lines[i]}", end='')

# 3. technical volume payload
print('\n=== 3. /api/stock/NVDA/technical volume field ===')
try:
    req = urllib.request.Request('http://127.0.0.1:8000/api/stock/NVDA/technical?period=1y', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        t_data = json.loads(resp.read().decode('utf-8'))
        print("technical.volume:", t_data.get('volume'))
except Exception as e:
    print("Error:", e)

# 4. price handler in stock.py
with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8') as f:
    s_lines = f.readlines()
print('\n=== 4. /price handler in stock.py (lines 100~135) ===')
for i in range(95, 135):
    print(f"{i+1:4d}: {s_lines[i]}", end='')

# -*- coding: utf-8 -*-
import subprocess, urllib.request, json, os

# 1. pod_manager.py lines 500~535
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\pod_manager.py', 'r', encoding='utf-8') as f:
    p_lines = f.readlines()

print('=== 1. pod_manager.py lines 500~535 ===')
for i in range(499, min(len(p_lines), 535)):
    print(f"{i+1:4d}: " + p_lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

# 2. PodManager __init__ pods list
print('\n\n=== 2. PodManager pods list (lines 475~490) ===')
for i in range(475, 490):
    print(f"{i+1:4d}: " + p_lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

# 3. STEP U: Call /price, /technical, /analysis for NYDA
print('\n\n=== 3. STEP U: Call NYDA endpoints ===')
for ep in ['/api/stock/NYDA/price', '/api/stock/NYDA/technical?period=1y', '/api/stock/NYDA/analysis?period=1y']:
    try:
        req = urllib.request.Request(f'http://127.0.0.1:8000{ep}', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"{ep} -> Status: {resp.status}")
            lines = json.dumps(data, indent=2, ensure_ascii=False).split('\n')
            for l in lines[:5]:
                print("  " + l)
    except urllib.error.HTTPError as e:
        print(f"{ep} -> HTTPError: {e.code} - {e.read().decode('utf-8', errors='ignore')[:100]}")
    except Exception as e:
        print(f"{ep} -> Error: {e}")

# 4. stock.py /signal except block
with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8') as f:
    s_lines = f.readlines()
print('\n=== 4. stock.py /signal except block (lines 690~715) ===')
for i in range(690, min(len(s_lines), 715)):
    print(f"{i+1:4d}: " + s_lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

# 5. TechnicalAnalyzer ValueError location
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\technical_analysis.py', 'r', encoding='utf-8') as f:
    t_lines = f.readlines()
print('\n=== 5. technical_analysis.py: Close column check ===')
for i, l in enumerate(t_lines):
    if 'Historical data must contain' in l or 'close' in l and 'Close' in l:
        print(f"Line {i+1:4d}: {l.strip()}")

# 6. App.tsx lines 940~965 || fallbacks
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()
print('\n=== 6. App.tsx lines 940~965 || fallbacks ===')
for i in range(939, min(len(app_lines), 965)):
    if '||' in app_lines[i]:
        print(f"Line {i+1:4d}: {app_lines[i].strip()}")

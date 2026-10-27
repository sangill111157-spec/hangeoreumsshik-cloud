# -*- coding: utf-8 -*-
import subprocess, urllib.request, json, os

print("=== 1. §3 NYDA Grep ===")
fe_nyda = subprocess.getoutput(r'cd /d C:\trading\package\nvda_trading_system\nvda-trading-dashboard && findstr /S /I "NYDA" src\*.*')
print("Frontend NYDA grep:", fe_nyda if fe_nyda else "0건 (NONE)")

be_nyda = subprocess.getoutput(r'cd /d C:\trading\package\nvda_trading_system\backend && findstr /S /I "NYDA" app\*.*')
print("Backend NYDA grep:", be_nyda if be_nyda else "0건 (NONE)")

print("\n=== 2. §3 currentTicker state & search input in App.tsx ===")
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'currentTicker' in l or 'setCurrentTicker' in l:
        print(f"Line {i+1:4d}: {l.strip()}")

print("\n=== 3. §4 pip show yfinance ===")
pip_out = subprocess.getoutput(r'cd /d C:\trading\package\nvda_trading_system\backend && .\venv\Scripts\python.exe -m pip show yfinance')
for l in pip_out.split('\n'):
    if 'Version:' in l:
        print(l)

print("\n=== 4. §3 Compare /signal for NVDA vs NYDA ===")
def test_sig(sym):
    try:
        url = f'http://127.0.0.1:8000/api/stock/{sym}/signal'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"[{sym}] Status: {resp.status}")
            for c in data.get('components', []):
                if c.get('name') == '멀티전략':
                    print("  멀티전략 component:", c)
    except urllib.error.HTTPError as e:
        print(f"[{sym}] HTTPError: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"[{sym}] Error: {e}")

test_sig('NVDA')
print()
test_sig('NYDA')

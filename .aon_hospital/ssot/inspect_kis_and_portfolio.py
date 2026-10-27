# -*- coding: utf-8 -*-
import sys, os, subprocess, json
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 1. KIS Broker price fetch & result keys inspection
print("==================================================")
print("1. KIS BROKER PRICE FETCH & RESULT KEYS INSPECTION")
print("==================================================")
from app.services.kis_broker import KisBroker

try:
    broker = KisBroker()
    print("KisBroker instantiated successfully.")
    price_res = broker.get_current_price("NVDA")
    print("\n--- broker.get_current_price('NVDA') Return Value ---")
    print(json.dumps({k: v for k, v in price_res.items() if k != 'data'}, indent=2, ensure_ascii=False))
    print("\n--- Sorted Keys of broker.get_current_price('NVDA') ---")
    print("Keys:", sorted(price_res.keys()))
    if 'data' in price_res and isinstance(price_res['data'], dict):
        print("\n--- Sorted Keys of Raw KIS Response (price_res['data']) ---")
        print("Raw KIS Keys:", sorted(price_res['data'].keys()))
        print("Raw rt_cd vs rt_code in raw data:")
        print("  rt_cd:", price_res['data'].get('rt_cd'))
        print("  rt_code:", price_res['data'].get('rt_code'))
        print("  msg_cd:", price_res['data'].get('msg_cd'))
        print("  msg1:", price_res['data'].get('msg1'))
except Exception as e:
    print(f"Error testing KisBroker: {e}")

# 2. Check running processes (telegram, etc.)
print("\n==================================================")
print("2. CHECK RUNNING PROCESSES (telegram, etc.)")
print("==================================================")
res = subprocess.run('powershell -Command "Get-Process | Where-Object { $_.ProcessName -like \'*python*\' } | Select-Object Id, ProcessName"', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res.stdout[:1500])

# 3. Test Portfolio API Endpoints & Routes list
print("\n==================================================")
print("3. TEST PORTFOLIO API ENDPOINTS & ROUTES")
print("==================================================")
import urllib.request

def test_api(url, method='GET', payload=None):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method=method)
        if payload:
            req.add_header('Content-Type', 'application/json')
            req.data = json.dumps(payload).encode('utf-8')
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"[{method} {url}] -> HTTP {resp.status}, Body len: {len(resp.read())}")
    except urllib.error.HTTPError as e:
        print(f"[{method} {url}] -> HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:200]}")
    except Exception as e:
        print(f"[{method} {url}] -> Error: {e}")

test_api("http://127.0.0.1:8000/api/portfolio/summary")
test_api("http://127.0.0.1:8000/api/portfolio/rebalance", method='POST', payload={"symbols": ["NVDA"]})
test_api("http://127.0.0.1:8000/api/stock/NVDA/price")

print("\n--- Routes in backend/app/main.py ---")
with open(os.path.join(backend_dir, r'app\main.py'), 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        if 'include_router' in line or 'app.get' in line or 'app.post' in line:
            print(" ", line.strip())


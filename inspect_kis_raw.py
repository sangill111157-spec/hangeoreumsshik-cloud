# -*- coding: utf-8 -*-
import sys, os, subprocess, json, asyncio, time
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. KIS RAW RESULT.KEYS() & GENERATION POINT")
print("==================================================")
# Check kis_broker.py lines around get_stock_price / _make_request
with open(os.path.join(backend_dir, r'app\services\kis_broker.py'), 'r', encoding='utf-8', errors='replace') as f:
    kis_lines = f.readlines()

for i, l in enumerate(kis_lines):
    if 'async def get_stock_price(' in l or 'async def get_korean_stock_price(' in l or 'async def get_account_balance(' in l:
        print(f"--- Method at line {i+1} ---")
        for j in range(i, min(len(kis_lines), i + 35)):
            print(f"{j+1:4d}: {kis_lines[j].rstrip()}")

# Call kis_broker._make_request or actual request method directly and print result.keys()
from app.services.kis_broker import KisBroker

async def fetch_kis_raw():
    broker = KisBroker()
    try:
        # Check get_stock_price internal call
        symbol = "NVDA"
        exch_cd = "NAS"
        url = f"{broker.base_url}/uapi/overseas-price/v1/quotations/price"
        headers = broker._get_auth_headers()
        headers["tr_id"] = "HHDFS00000300"
        params = {
            "AUTH": "",
            "EXCD": exch_cd,
            "SYMB": symbol.upper()
        }
        client = await broker._get_http_client()
        response = await client.get(url, headers=headers, params=params)
        raw_json = response.json()
        print("\n[LIVE KIS API RAW RESPONSE]")
        print("HTTP Status:", response.status_code)
        print("Raw JSON Sorted Keys:", sorted(raw_json.keys()))
        print("Raw rt_cd:", raw_json.get("rt_cd"))
        print("Raw rt_code:", raw_json.get("rt_code"))
        print("Raw msg_cd:", raw_json.get("msg_cd"))
        print("Raw msg1:", raw_json.get("msg1"))
        print("Raw output sample keys:", sorted(raw_json.get("output", {}).keys()) if isinstance(raw_json.get("output"), dict) else type(raw_json.get("output")))
    except Exception as e:
        print("Raw fetch exception:", e)
    finally:
        await broker.close()

asyncio.run(fetch_kis_raw())

print("\n==================================================")
print("2. CONSUMERS OF 'success' IN BACKEND")
print("==================================================")
out, _ = run_cmd('git grep -n "success" app/')
for l in out.split('\n'):
    if 'kis_broker' not in l and l.strip():
        print(l)


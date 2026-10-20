# -*- coding: utf-8 -*-
import urllib.request, json, time

print('=== 1. 3 Concurrent samples of /price vs /technical ===')
for i in range(3):
    t_start = time.strftime('%H:%M:%S')
    req_p = urllib.request.Request('http://127.0.0.1:8000/api/stock/NVDA/price', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_p, timeout=10) as resp:
        d_p = json.loads(resp.read().decode('utf-8'))
    
    req_t = urllib.request.Request('http://127.0.0.1:8000/api/stock/NVDA/technical?period=1y', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_t, timeout=10) as resp:
        d_t = json.loads(resp.read().decode('utf-8'))
    
    vol_p = d_p.get('volume', 0)
    vol_t = d_t.get('volume', {}).get('current_volume', 0)
    ratio = vol_t / vol_p if vol_p > 0 else 0
    print(f"Sample {i+1} [{t_start}]:")
    print(f"  /price volume: {vol_p:,}")
    print(f"  /technical current_volume: {vol_t:,}")
    print(f"  Ratio (technical / price): {ratio:.2f}")
    time.sleep(1)

# 2. Inspect KIS broker raw volume field in kis_broker.py
print('\n=== 2. KIS broker overseas stock price fields in kis_broker.py ===')
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py', 'r', encoding='utf-8') as f:
    kis_lines = f.readlines()

for i, l in enumerate(kis_lines):
    if 'get_stock_price' in l or 'tvol' in l or 'acml_vol' in l or 'pvol' in l:
        print(f"Line {i+1:4d}: {l.strip()}")

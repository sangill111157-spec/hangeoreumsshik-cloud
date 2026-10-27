# -*- coding: utf-8 -*-
import urllib.request, json

print('=== 1. Verify STEP U (/signal for NYDA and NVDA) ===')
for sym in ['NYDA', 'NVDA']:
    url = f'http://127.0.0.1:8000/api/stock/{sym}/signal'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"[{sym}] Status: {resp.status} | master_score: {data.get('master_score')}")
    except urllib.error.HTTPError as e:
        print(f"[{sym}] Status: {e.code} | detail: {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"[{sym}] Error: {e}")

print('\n=== 2. U-2: /api/stock/NYDA/price payload ===')
try:
    req = urllib.request.Request('http://127.0.0.1:8000/api/stock/NYDA/price', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        d_p = json.loads(resp.read().decode('utf-8'))
        print(json.dumps(d_p, indent=2, ensure_ascii=False))
except Exception as e:
    print("Error:", e)

print('\n=== 3. Pod individual scores in /signal ===')
try:
    req = urllib.request.Request('http://127.0.0.1:8000/api/stock/NVDA/signal', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        d_sig = json.loads(resp.read().decode('utf-8'))
        for c in d_sig.get('components', []):
            if c.get('name') == '멀티전략':
                print("멀티전략 component in response:", json.dumps(c, indent=2, ensure_ascii=False))
except Exception as e:
    print("Error:", e)

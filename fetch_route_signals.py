# -*- coding: utf-8 -*-
import sys, urllib.request, json, time

time.sleep(2)

# 1. Test BUY Signal via Route: GET /api/stock/NVDA/test-signal?mode=buy
url_buy = "http://127.0.0.1:8000/api/stock/NVDA/test-signal?mode=buy"
try:
    req = urllib.request.Request(url_buy, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        buy_data = json.loads(resp.read().decode('utf-8'))
        print("=== 1. ROUTE BUY LIVE JSON DUMP ===")
        print(json.dumps(buy_data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error fetching BUY signal: {e}")

# 2. Test Unavailable Signal via Route: GET /api/stock/NVDA/test-signal?force_unavailable=investor_analysis,options_flow
url_unavail = "http://127.0.0.1:8000/api/stock/NVDA/test-signal?force_unavailable=investor_analysis,options_flow"
try:
    req = urllib.request.Request(url_unavail, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        unavail_data = json.loads(resp.read().decode('utf-8'))
        print("\n=== 2. ROUTE UNAVAILABLE LIVE JSON DUMP (Coverage = 0.65) ===")
        print(json.dumps(unavail_data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error fetching UNAVAILABLE signal: {e}")


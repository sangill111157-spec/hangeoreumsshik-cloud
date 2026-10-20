# -*- coding: utf-8 -*-
import urllib.request, time, json, concurrent.futures

def fetch_one(name, url):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=35) as resp:
            elapsed = time.time() - t0
            return name, resp.status, elapsed
    except urllib.error.HTTPError as e:
        elapsed = time.time() - t0
        return name, e.code, elapsed
    except Exception as e:
        elapsed = time.time() - t0
        return name, str(e), elapsed

# =========================================================================
# Scenario 1: 4 endpoints concurrent (without /signal)
# =========================================================================
print("=== Scenario 1: 4 concurrent endpoints (without /signal) ===")
s1_eps = [
    ('/api/stock/NVDA/price', 'http://127.0.0.1:8000/api/stock/NVDA/price'),
    ('/api/stock/NVDA/technical', 'http://127.0.0.1:8000/api/stock/NVDA/technical'),
    ('/api/stock/NVDA/analysis', 'http://127.0.0.1:8000/api/stock/NVDA/analysis'),
    ('/api/stock/account/balance', 'http://127.0.0.1:8000/api/stock/account/balance')
]

t0_s1 = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    s1_results = list(ex.map(lambda x: fetch_one(x[0], x[1]), s1_eps))
t_total_s1 = time.time() - t0_s1

for r in s1_results:
    print(f"{r[0]:30s} | Status: {str(r[1]):5s} | Time: {r[2]:.3f}s")
print(f"Scenario 1 Total Time: {t_total_s1:.3f}s")

# =========================================================================
# Scenario 2: /signal first -> 0.1s wait -> balance & price concurrent
# =========================================================================
print("\n=== Scenario 2: /signal first -> 0.1s -> balance & price ===")
signal_url = 'http://127.0.0.1:8000/api/stock/NVDA/signal'
balance_url = 'http://127.0.0.1:8000/api/stock/account/balance'
price_url = 'http://127.0.0.1:8000/api/stock/NVDA/price'

def run_scenario2():
    t_start = time.time()
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        # Launch signal
        f_sig = ex.submit(fetch_one, '/signal', signal_url)
        time.sleep(0.1)
        # Launch balance and price
        f_bal = ex.submit(fetch_one, '/account/balance', balance_url)
        f_pri = ex.submit(fetch_one, '/price', price_url)
        
        r_bal = f_bal.result()
        r_pri = f_pri.result()
        r_sig = f_sig.result()
        
    return r_bal, r_pri, r_sig

r_bal, r_pri, r_sig = run_scenario2()
print(f"{r_bal[0]:30s} | Status: {str(r_bal[1]):5s} | Time: {r_bal[2]:.3f}s")
print(f"{r_pri[0]:30s} | Status: {str(r_pri[1]):5s} | Time: {r_pri[2]:.3f}s")
print(f"{r_sig[0]:30s} | Status: {str(r_sig[1]):5s} | Time: {r_sig[2]:.3f}s")

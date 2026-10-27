# -*- coding: utf-8 -*-
import urllib.request, time, json, concurrent.futures

def fetch_one(name, url):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=40) as resp:
            elapsed = time.time() - t0
            return name, resp.status, elapsed
    except urllib.error.HTTPError as e:
        elapsed = time.time() - t0
        return name, e.code, elapsed
    except Exception as e:
        elapsed = time.time() - t0
        return name, str(e), elapsed

print("=== N-3 Measurements (5 items) ===")

# 1. /signal single
r_sig = fetch_one('/api/stock/NVDA/signal', 'http://127.0.0.1:8000/api/stock/NVDA/signal')
print(f"1) /signal single        : Status {r_sig[1]} | Time {r_sig[2]:.3f}s")

# 2. /risk/score single
r_risk = fetch_one('/api/risk/score', 'http://127.0.0.1:8000/api/risk/score')
print(f"2) /risk/score single    : Status {r_risk[1]} | Time {r_risk[2]:.3f}s")

# 3. /rebalance/plan single
r_reb = fetch_one('/api/rebalance/plan', 'http://127.0.0.1:8000/api/rebalance/plan')
print(f"3) /rebalance/plan single: Status {r_reb[1]} | Time {r_reb[2]:.3f}s")

# 4. Scenario 1 (4 concurrent)
s1_eps = [
    ('/api/stock/NVDA/price', 'http://127.0.0.1:8000/api/stock/NVDA/price'),
    ('/api/stock/NVDA/technical', 'http://127.0.0.1:8000/api/stock/NVDA/technical'),
    ('/api/stock/NVDA/analysis', 'http://127.0.0.1:8000/api/stock/NVDA/analysis'),
    ('/api/stock/account/balance', 'http://127.0.0.1:8000/api/stock/account/balance')
]
t0_s1 = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    s1_res = list(ex.map(lambda x: fetch_one(x[0], x[1]), s1_eps))
t_total_s1 = time.time() - t0_s1
print(f"\n4) Scenario 1 (4 concurrent, Total: {t_total_s1:.3f}s):")
for r in s1_res:
    print(f"   {r[0]:28s} | Status {r[1]} | Time {r[2]:.3f}s")

# 5. Scenario 2 (/signal + 0.1s -> balance & price)
def run_scenario2():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        f_sig = ex.submit(fetch_one, '/signal', 'http://127.0.0.1:8000/api/stock/NVDA/signal')
        time.sleep(0.1)
        f_bal = ex.submit(fetch_one, '/account/balance', 'http://127.0.0.1:8000/api/stock/account/balance')
        f_pri = ex.submit(fetch_one, '/price', 'http://127.0.0.1:8000/api/stock/NVDA/price')
        return f_bal.result(), f_pri.result(), f_sig.result()

res_bal, res_pri, res_sig = run_scenario2()
print(f"\n5) Scenario 2 (/signal first -> 0.1s -> balance & price):")
print(f"   {res_bal[0]:28s} | Status {res_bal[1]} | Time {res_bal[2]:.3f}s")
print(f"   {res_pri[0]:28s} | Status {res_pri[1]} | Time {res_pri[2]:.3f}s")
print(f"   {res_sig[0]:28s} | Status {res_sig[1]} | Time {res_sig[2]:.3f}s")

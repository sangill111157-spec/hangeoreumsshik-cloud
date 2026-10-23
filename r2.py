# -*- coding: utf-8 -*-
import urllib.request, time, json, concurrent.futures

def fetch_one(name, url):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            elapsed = time.time() - t0
            return name, resp.status, elapsed
    except urllib.error.HTTPError as e:
        elapsed = time.time() - t0
        return name, e.code, elapsed
    except Exception as e:
        elapsed = time.time() - t0
        return name, str(e), elapsed

# =========================================================================
# Scenario A: /risk/score and /rebalance/plan concurrent
# =========================================================================
print("=== Scenario A: /risk/score and /rebalance/plan concurrent ===")
t0_a = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
    f_risk = ex.submit(fetch_one, '/risk/score', 'http://127.0.0.1:8000/api/risk/score')
    f_reb = ex.submit(fetch_one, '/rebalance/plan', 'http://127.0.0.1:8000/api/rebalance/plan')
    res_risk = f_risk.result()
    res_reb = f_reb.result()
t_total_a = time.time() - t0_a

print(f"{res_risk[0]:20s} | Status: {res_risk[1]} | Time: {res_risk[2]:.3f}s")
print(f"{res_reb[0]:20s} | Status: {res_reb[1]} | Time: {res_reb[2]:.3f}s")
print(f"Scenario A Total Time: {t_total_a:.3f}s")

# =========================================================================
# Scenario B: /rebalance/plan -> 0.1s -> /price
# =========================================================================
print("\n=== Scenario B: /rebalance/plan -> 0.1s -> /price ===")
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
    f_reb = ex.submit(fetch_one, '/rebalance/plan', 'http://127.0.0.1:8000/api/rebalance/plan')
    time.sleep(0.1)
    f_price = ex.submit(fetch_one, '/price', 'http://127.0.0.1:8000/api/stock/NVDA/price')
    res_price = f_price.result()
    res_reb = f_reb.result()

print(f"{res_price[0]:20s} | Status: {res_price[1]} | Time: {res_price[2]:.3f}s")
print(f"{res_reb[0]:20s} | Status: {res_reb[1]} | Time: {res_reb[2]:.3f}s")

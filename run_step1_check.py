# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
import urllib.request, json, time, subprocess

def run_cmd(cmd, cwd=r'C:\trading\package\nvda_trading_system\backend'):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. COMMITS & GIT STATUS")
print("==================================================")
out, _ = run_cmd("git show 60bb9dd")
print("--- [60bb9dd diff] ---")
print(out)

out, _ = run_cmd("git status --short")
print("--- [git status --short] ---")
print(out)

out, _ = run_cmd("git log --oneline -6")
print("--- [git log --oneline -6] ---")
print(out)

print("==================================================")
print("2. 1cdbedf FULL DIFF")
print("==================================================")
out, _ = run_cmd("git show 1cdbedf")
print(out)

print("==================================================")
print("3. GREP calculate_final_master_signal")
print("==================================================")
out, _ = run_cmd("git grep -n \"calculate_final_master_signal\"")
print(out)

print("==================================================")
print("4. CALLING 4 ENDPOINTS LIVE")
print("==================================================")
def call_url(name, url, method='GET', data=None):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method=method)
        if data:
            req.add_header('Content-Type', 'application/json')
            req.data = json.dumps(data).encode('utf-8')
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode('utf-8')
            print(f"[{name}] HTTP {resp.status} OK (body length: {len(body)})")
            try:
                j = json.loads(body)
                print(f"  Sample keys: {list(j.keys())[:8]}")
            except:
                pass
    except urllib.error.HTTPError as e:
        print(f"[{name}] HTTP {e.code} Error: {e.read().decode('utf-8', errors='replace')[:200]}")
    except Exception as e:
        print(f"[{name}] Error: {e}")

call_url("nvda.py:1439 (/api/nvda/analysis)", "http://127.0.0.1:8000/api/nvda/analysis")
call_url("stock.py:730 (/api/stock/NVDA/signal)", "http://127.0.0.1:8000/api/stock/NVDA/signal")
call_url("portfolio_manager (/api/portfolio/rebalance)", "http://127.0.0.1:8000/api/portfolio/rebalance", method='POST', data={"symbols": ["NVDA", "AAPL"]})
call_url("portfolio (/api/portfolio/summary)", "http://127.0.0.1:8000/api/portfolio/summary")


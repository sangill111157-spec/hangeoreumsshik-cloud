# -*- coding: utf-8 -*-
import sys, os, subprocess, json, urllib.request, time

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("==================================================")
print("1. [결함 57] git grep for investor_to_score callers")
print("==================================================")
res_grep_inv = subprocess.run('git grep -n "investor_to_score" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8')
print("investor_to_score occurrences in app/:\n", res_grep_inv.stdout)

print("\n==================================================")
print("2. [B-1 & 결함 56] Live Endpoint Verification on Fresh Server")
print("==================================================")
try:
    req = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("LIVE_SIGNAL_FULL_DUMP:")
        print(json.dumps(data, indent=2))
except Exception as e:
    print("Live endpoint query error:", e)

print("\n==================================================")
print("3. [결함 55 잔여] Runtime process app.__file__ and sys.path")
print("==================================================")
import app
print("app.__file__ :", app.__file__)
print("sys.path[0]  :", sys.path[0])


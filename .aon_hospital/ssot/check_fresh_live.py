# -*- coding: utf-8 -*-
import sys, os, subprocess, json, urllib.request

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("==================================================")
print("1. [결함 40] PodSignal dataclass definition in backend")
print("==================================================")
res_pod_def = subprocess.run('git grep -n "class PodSignal" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8')
print("PodSignal definition lines:\n", res_pod_def.stdout)

# Check the file containing PodSignal
with open(os.path.join(backend_dir, r'app\services\pod_manager.py'), 'r', encoding='utf-8') as f:
    pm_lines = f.readlines()
for i, l in enumerate(pm_lines):
    if 'class PodSignal' in l or 'class PodManager' in l:
        print(f"--- pod_manager.py line {i+1} ---")
        for j in range(i, min(len(pm_lines), i + 25)):
            print(f"{j+1:4d}: {pm_lines[j].rstrip()}")
        break

print("\n==================================================")
print("2. [B-1] Live /api/stock/NVDA/signal call on Fresh Server")
print("==================================================")
try:
    req = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Live /signal Response Status: 200 OK")
        print(f"  master_score: {data.get('master_score')}")
        print(f"  raw_score   : {data.get('raw_score')}")
        print(f"  coverage    : {data.get('coverage')}")
        print(f"  signal      : {data.get('signal')}")
        print("  components  :")
        for c in data.get("components", []):
            print(f"    - {c.get('name'):12s}: score={c.get('score')} | signal={c.get('signal'):12s} | conf={c.get('confidence')}")
except Exception as e:
    print("Live call error:", e)

print("\n==================================================")
print("3. [B-1] git log --oneline -3 and git status")
print("==================================================")
res_log = subprocess.run('git log --oneline -3', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8')
print(res_log.stdout)
res_st = subprocess.run('git status', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8')
print(res_st.stdout)


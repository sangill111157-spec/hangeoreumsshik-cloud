# -*- coding: utf-8 -*-
import urllib.request, json, subprocess, os

def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out.decode('utf-8', errors='ignore')

def safe_print(text):
    print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

# 1. §3 Live Raw JSON of /api/stock/NVDA/signal
safe_print('=== 1. §3 Raw JSON of /api/stock/NVDA/signal ===')
try:
    req = urllib.request.Request('http://127.0.0.1:8000/api/stock/NVDA/signal', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=35) as resp:
        d = json.loads(resp.read().decode('utf-8'))
        safe_print("master_score: " + str(d.get("master_score")))
        safe_print("confidence: " + str(d.get("confidence")))
        safe_print("coverage: " + str(d.get("coverage")))
        safe_print("available_module_count: " + str(d.get("available_module_count")))
        safe_print("unavailable_modules: " + json.dumps(d.get("unavailable_modules")))
        safe_print("\nComponents full array:")
        for c in d.get("components", []):
            safe_print("  " + json.dumps(c, ensure_ascii=False))
except Exception as e:
    safe_print("Error: " + str(e))

# 2. Grep 50 in master_signal.py
safe_print('\n=== 2. Grep 50 in master_signal.py ===')
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py', 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if '= 50' in l or 'or 50' in l or ', 50)' in l or ': 50' in l:
            safe_print(f"Line {i+1:4d}: {l.strip()}")

# 3. TS interfaces in App.tsx / api.ts / types.ts
safe_print('\n=== 3. Frontend Types in src/ ===')
for root, dirs, files in os.walk(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src'):
    for file in files:
        if file.endswith('.ts') or file.endswith('.tsx'):
            fpath = os.path.join(root, file)
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'interface MasterSignal' in content or 'type MasterSignal' in content:
                    safe_print(f"\n--- Found MasterSignal in {file} ---")
                    for l in content.split('\n'):
                        if 'MasterSignal' in l or 'master_score' in l or 'signal' in l or 'coverage' in l:
                            safe_print("  " + l)

# 4. KIS broker success=False lines and NVDA raw dict
safe_print('\n=== 4. KIS broker success=False lines & NVDA raw price dict ===')
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py', 'r', encoding='utf-8') as f:
    kis_lines = f.readlines()

for i, l in enumerate(kis_lines):
    if 'success' in l or 'rt_cd' in l or 'rt_code' in l:
        safe_print(f"Line {i+1:4d}: {l.strip()}")

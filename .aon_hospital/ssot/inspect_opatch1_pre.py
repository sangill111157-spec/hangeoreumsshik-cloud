# -*- coding: utf-8 -*-
import subprocess, os, json, urllib.request

def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out.decode('utf-8', errors='ignore')

def safe_print(text):
    print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

# 1. Condition 2: Grep 50 in master_signal.py
safe_print('=== 1. Grep 50 in master_signal.py ===')
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py', 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if '= 50' in l or 'or 50' in l or ', 50)' in l or ': 50' in l:
            safe_print(f"Line {i+1:4d}: {l.strip()}")

# 2. Condition 3: TS types in frontend
safe_print('\n=== 2. Frontend Signal types in api.ts / types.ts ===')
fe_files = [
    r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\services\api.ts',
    r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\types\index.ts',
    r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\types.ts'
]
for fpath in fe_files:
    if os.path.exists(fpath):
        safe_print(f"\n--- {os.path.basename(fpath)} ---")
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
            for l in content.split('\n'):
                if 'MasterSignal' in l or 'master_score' in l or 'ComponentScore' in l or 'signal:' in l:
                    safe_print("  " + l)

# 3. Pod weights and weighted_score calculation in pod_manager.py
safe_print('\n=== 3. Pod weights in pod_manager.py ===')
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\pod_manager.py', 'r', encoding='utf-8') as f:
    p_lines = f.readlines()

for i, l in enumerate(p_lines):
    if 'weight' in l or 'weighted_score' in l or 'PodManager' in l:
        if 80 < i < 125 or 470 < i < 515:
            safe_print(f"Line {i+1:4d}: {l.strip()}")

# 4. Confidence calculation around line 582 in master_signal.py
safe_print('\n=== 4. Confidence calculation in master_signal.py lines 570~595 ===')
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py', 'r', encoding='utf-8') as f:
    ms_lines = f.readlines()

for i in range(569, min(len(ms_lines), 595)):
    safe_print(f"{i+1:4d}: {ms_lines[i]}")

# 5. U-2 KIS broker raw dict on NYDA
safe_print('\n=== 5. U-2 KIS raw dict on NYDA ===')
try:
    req = urllib.request.Request('http://127.0.0.1:8000/api/stock/NYDA/price', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        safe_print(resp.read().decode('utf-8'))
except Exception as e:
    safe_print("Error: " + str(e))

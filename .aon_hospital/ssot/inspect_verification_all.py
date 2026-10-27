# -*- coding: utf-8 -*-
import subprocess, urllib.request, json, os

def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out.decode('utf-8', errors='ignore')

def safe_print(text):
    print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

# 1. §3 git show 49fed9d
safe_print('=== 1. §3 git show 49fed9d ===')
safe_print(run_cmd(r'cd /d C:\trading\package\nvda_trading_system\backend && git show 49fed9d'))

# 2. §4 Pod individual scores & confidence origin
safe_print('\n=== 2. §4 Pod individual scores & confidence in App.tsx ===')
try:
    req = urllib.request.Request('http://127.0.0.1:8000/api/stock/NVDA/signal', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        sig_data = json.loads(resp.read().decode('utf-8'))
        safe_print("Master confidence: " + str(sig_data.get('confidence')))
        safe_print("Components in response:")
        for c in sig_data.get('components', []):
            safe_print(f"  {c.get('name')}: score={c.get('score')}, signal={c.get('signal')}, confidence={c.get('confidence')}")
except Exception as e:
    safe_print("Error fetching /signal: " + str(e))

# Check App.tsx for recommendation confidence
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

safe_print('\nRecommendation card in App.tsx:')
for i, l in enumerate(app_lines):
    if '신뢰도' in l or 'confidence' in l and ('권장' in l or 'recommend' in l or 'masterSignal' in l):
        safe_print(f"Line {i+1:4d}: {l.strip()}")

# 3. §5 O-patch-1 weights and calculation in master_signal.py
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py', 'r', encoding='utf-8') as f:
    ms_lines = f.readlines()

safe_print('\n=== 3. §5 Weights & Master score calculation in master_signal.py ===')
for i, l in enumerate(ms_lines):
    if 'WEIGHTS' in l or 'weights' in l or 'calculate_final_master_signal' in l or 'raw_score' in l:
        if i < 200 or 520 < i < 570:
            safe_print(f"Line {i+1:4d}: {l.strip()}")

# 4. §6 U-2 kis_broker.py lines 400~430
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py', 'r', encoding='utf-8') as f:
    kis_lines = f.readlines()

safe_print('\n=== 4. §6 kis_broker.py lines 400~430 ===')
for i in range(399, min(len(kis_lines), 430)):
    safe_print(f"{i+1:4d}: {kis_lines[i]}")

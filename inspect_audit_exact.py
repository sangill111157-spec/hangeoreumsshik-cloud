# -*- coding: utf-8 -*-
import subprocess, os, json, sys

def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out.decode('utf-8', errors='ignore')

def safe_print(text):
    print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

# 1. Condition 2: Grep 50 in master_signal.py exact
safe_print('=== 1. Grep 50 in master_signal.py ===')
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py', 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if '= 50' in l or 'or 50' in l or ', 50)' in l or ': 50' in l:
            safe_print(f"Line {i+1:4d}: {l.strip()}")

# 2. git show 1cdbedf --stat & diff
safe_print('\n=== 2. git show 1cdbedf --stat ===')
safe_print(run_cmd(r'cd /d C:\trading\package\nvda_trading_system\backend && git show 1cdbedf --stat'))

# 3. Pod confidence calculation in pod_manager.py
safe_print('\n=== 3. Pod confidence calculation in pod_manager.py ===')
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\pod_manager.py', 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if 'confidence =' in l or 'confidence=' in l:
            safe_print(f"Line {i+1:4d}: {l.strip()}")

# 4. KIS broker success lines in kis_broker.py
safe_print('\n=== 4. Grep success in kis_broker.py ===')
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py', 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if 'success' in l:
            safe_print(f"Line {i+1:4d}: {l.strip()}")

# 5. TS interfaces in frontend
safe_print('\n=== 5. Types / Interfaces in src/ ===')
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if 'interface ' in l or 'type ' in l:
            if i < 200:
                safe_print(f"Line {i+1:4d}: {l.strip()}")

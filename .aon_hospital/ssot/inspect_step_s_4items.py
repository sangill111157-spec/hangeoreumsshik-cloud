# -*- coding: utf-8 -*-
import subprocess, os, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Search NoneType in all logs
log_file = r'C:\Users\sangi\.gemini\antigravity-ide\brain\c50a04a5-fee9-47e0-a2b5-abad2603eeca\.system_generated\tasks\task-1228.log'
print('=== 1. grep NoneType in task-1228.log ===')
with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
    for i, l in enumerate(f):
        if 'NoneType' in l:
            print(f"Line {i+1:4d}: {l.strip()}")

# 2. grep fetch_historical_data
print('\n=== 2. grep fetch_historical_data in backend/app ===')
out = subprocess.getoutput(r'cd /d C:\trading\package\nvda_trading_system\backend && findstr /S /N "fetch_historical_data" app\*.py')
print(out)

# 3. grep \.empty in correlation_engine.py
print('\n=== 3. grep \\.empty in correlation_engine.py ===')
ce_file = os.path.join(backend_dir, 'app', 'services', 'correlation_engine.py')
with open(ce_file, 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if '.empty' in l:
            print(f"Line {i+1:4d}: {l.strip()}")

# 4. yfinance version in requirements.txt
print('\n=== 4. yfinance version in requirements.txt ===')
req_file = os.path.join(backend_dir, 'requirements.txt')
with open(req_file, 'r', encoding='utf-8') as f:
    for l in f:
        if 'yfinance' in l:
            print(l.strip())

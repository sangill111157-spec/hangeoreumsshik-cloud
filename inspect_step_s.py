# -*- coding: utf-8 -*-
import os, re

# 1. Search full traceback in log
log_path = r'C:\Users\sangi\.gemini\antigravity-ide\brain\c50a04a5-fee9-47e0-a2b5-abad2603eeca\.system_generated\tasks\task-1228.log'
print('=== 1. Traceback in task-1228.log ===')
with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    log_text = f.read()

matches = [m.start() for m in re.finditer(r"'NoneType' object has no attribute 'empty'", log_text)]
for pos in matches:
    start = max(0, pos - 1000)
    end = min(len(log_text), pos + 500)
    print(log_text[start:end])
    print('\n' + '='*50 + '\n')

# 2. Grep .empty across backend services
services_dir = r'C:\trading\package\nvda_trading_system\backend\app'
print('\n=== 2. Grep .empty across backend ===')
for root, dirs, files in os.walk(services_dir):
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, services_dir)
            with open(p, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            for i, l in enumerate(lines):
                if '.empty' in l:
                    print(f"{rel}:{i+1:4d} | {l.strip()}")

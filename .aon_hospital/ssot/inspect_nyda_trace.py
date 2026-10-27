# -*- coding: utf-8 -*-
# Check traceback of NYDA call from log
log_path = r'C:\Users\sangi\.gemini\antigravity-ide\brain\c50a04a5-fee9-47e0-a2b5-abad2603eeca\.system_generated\tasks\task-1228.log'
with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print('=== Last 30 lines of backend log (NYDA traceback) ===')
for l in lines[-30:]:
    print(l, end='')

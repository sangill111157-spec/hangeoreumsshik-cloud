# -*- coding: utf-8 -*-
import subprocess

# Inspect recent backend logs
log_file = r'C:\Users\sangi\.gemini\antigravity-ide\brain\c50a04a5-fee9-47e0-a2b5-abad2603eeca\.system_generated\tasks\task-1228.log'
print('=== Recent Backend Log (task-1228) ===')
with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
for l in lines[-35:]:
    print(l, end='')

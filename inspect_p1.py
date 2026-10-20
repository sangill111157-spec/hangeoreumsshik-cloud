# -*- coding: utf-8 -*-
# 1. master_signal.py lines 585~620
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py', 'r', encoding='utf-8') as f:
    ms_lines = f.readlines()

print('=== P-1 (1): master_signal.py lines 585~620 ===')
for i in range(584, 620):
    print(f"{i+1:4d}: " + ms_lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

# 2. pod_manager.py analyze_all and pod definitions
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\pod_manager.py', 'r', encoding='utf-8') as f:
    pod_lines = f.readlines()

print('\n=== P-1 (2): pod_manager.py analyze_all / signals ===')
for i, line in enumerate(pod_lines):
    if 'class PodManager' in line or 'def analyze_all' in line or 'class PodSignal' in line:
        for j in range(i, min(len(pod_lines), i+35)):
            print(f"{j+1:4d}: " + pod_lines[j].encode('ascii', errors='backslashreplace').decode('ascii'), end='')
        print('\n---')

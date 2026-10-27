# -*- coding: utf-8 -*-
# Inspect Pod classes in pod_manager.py
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\pod_manager.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== 1. PodSignal dataclass (lines 35~48) ===')
for i in range(36, 48):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

print('\n=== 2. MomentumPod & TechnicalPod score calculation ===')
for i, l in enumerate(lines):
    if 'class MomentumPod' in l or 'class TechnicalPod' in l or 'class BasePod' in l:
        print(f"--- Line {i+1:4d}: {l.strip()} ---")
        for k in range(i, min(len(lines), i+35)):
            if 'score' in lines[k] or 'return PodSignal' in lines[k] or 'def calculate' in lines[k]:
                print(f"  {k+1:4d}: " + lines[k].strip().encode('ascii', errors='backslashreplace').decode('ascii'))

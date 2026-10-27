# -*- coding: utf-8 -*-
import os, re

services = [
    (r'C:\trading\package\nvda_trading_system\backend\app\services\risk_monitor.py', 'RiskMonitor'),
    (r'C:\trading\package\nvda_trading_system\backend\app\services\rebalance_engine.py', 'RebalanceEngine')
]

print('=== Inspecting self. assignments in RiskMonitor and RebalanceEngine ===')
for filepath, classname in services:
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f'\n--- Class: {classname} in {os.path.basename(filepath)} ---')
    in_class = False
    in_init = False
    found = []
    for i, line in enumerate(lines):
        if line.startswith(f'class {classname}'):
            in_class = True
        elif in_class and line.startswith('class '):
            in_class = False
        
        if in_class:
            if 'def __init__' in line:
                in_init = True
            elif line.strip().startswith('def ') and 'def __init__' not in line:
                in_init = False
            
            if not in_init:
                m = re.search(r'\bself\.(\w+)\s*=', line)
                if m:
                    found.append((i+1, line.strip()))
    
    if found:
        print(f"Found {len(found)} assignments:")
        for lno, text in found:
            print(f"  Line {lno:4d}: {text}")
    else:
        print("Assignments outside __init__: 0 (NONE)")

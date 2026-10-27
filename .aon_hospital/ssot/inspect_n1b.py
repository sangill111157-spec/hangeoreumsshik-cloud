# -*- coding: utf-8 -*-
import os, re

# 1. Inspect deps.py
deps_path = r'C:\trading\package\nvda_trading_system\backend\app\api\deps.py'
print('=== 1. app/api/deps.py ===')
if os.path.exists(deps_path):
    with open(deps_path, 'r', encoding='utf-8') as f:
        deps_lines = f.readlines()
    for i, line in enumerate(deps_lines):
        if any(fn in line for fn in ['def get_data_collector', 'def get_technical_analyzer', 'def get_investor_engine']):
            for j in range(i, min(len(deps_lines), i+15)):
                print(f"{j+1:4d}: " + deps_lines[j].encode('ascii', errors='backslashreplace').decode('ascii'), end='')
                if deps_lines[j].strip().startswith('return '):
                    break
            print('\n---')

# 2. Inspect self. assignment outside __init__
classes = [
    (r'C:\trading\package\nvda_trading_system\backend\app\services\data_collector.py', 'DataCollector'),
    (r'C:\trading\package\nvda_trading_system\backend\app\services\technical_analysis.py', 'TechnicalAnalyzer'),
    (r'C:\trading\package\nvda_trading_system\backend\app\services\investor_analysis.py', 'InvestorAnalysisEngine')
]

print('\n=== 2. self. assignments outside __init__ ===')
for filepath, classname in classes:
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
                # search for self.xxx = ...
                m = re.search(r'self\.\w+\s*=', line)
                if m:
                    found.append((i+1, line.strip()))
    
    if found:
        print(f"Found {len(found)} assignments:")
        for lno, text in found:
            print(f"  Line {lno:4d}: {text}")
    else:
        print("Assignments outside __init__: 0 (NONE)")

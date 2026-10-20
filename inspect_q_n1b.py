# -*- coding: utf-8 -*-
import os, re

# 1. STEP Q: Search setInterval, setTimeout in src/
frontend_src = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src'
print('=== STEP Q: Interval/Timeout/Polling in frontend src/ ===')

for root, dirs, files in os.walk(frontend_src):
    for f in files:
        if f.endswith(('.ts', '.tsx', '.js', '.jsx')):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, frontend_src)
            with open(p, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            for i, l in enumerate(lines):
                if any(kw in l for kw in ['setInterval', 'setTimeout', 'refetch', 'polling']):
                    print(f"{rel}:{i+1:4d} | {l.strip()}")

# 2. STEP N-1b Extended: Check all backend services for thread-safety (self. assignment outside __init__)
backend_services = r'C:\trading\package\nvda_trading_system\backend\app\services'
print('\n=== STEP N-1b Extended: self assignments outside __init__ in backend services ===')

service_files = [
    'data_collector.py', 'technical_analysis.py', 'investor_analysis.py',
    'llm_analyzer.py', 'options_flow.py', 'darkpool_analyzer.py',
    'event_engine.py', 'correlation_engine.py', 'pod_manager.py',
    'news_sentiment.py', 'edgar_tracker.py', 'master_signal.py'
]

for sf in service_files:
    p = os.path.join(backend_services, sf)
    if not os.path.exists(p):
        print(f"File not found: {sf}")
        continue
    with open(p, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    current_class = None
    in_init = False
    found = []
    
    for i, line in enumerate(lines):
        cl_match = re.match(r'^class\s+(\w+)', line)
        if cl_match:
            current_class = cl_match.group(1)
            in_init = False
        
        if current_class:
            if re.search(r'^\s+def\s+__init__', line):
                in_init = True
            elif re.search(r'^\s+def\s+(?!__init__)\w+', line):
                in_init = False
            
            if not in_init:
                # Check for self.xxx = ...
                m = re.search(r'\bself\.(\w+)\s*=', line)
                if m:
                    # Ignore inner function assignments or local properties if any
                    found.append((current_class, i+1, line.strip()))
    
    print(f"\n--- {sf} ---")
    if found:
        print(f"Found {len(found)} assignments:")
        for cl, lno, text in found:
            print(f"  [{cl}] Line {lno:4d}: {text}")
    else:
        print("Assignments outside __init__: 0 (NONE)")

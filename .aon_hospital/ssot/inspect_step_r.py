# -*- coding: utf-8 -*-
import os, re

routes_dir = r'C:\trading\package\nvda_trading_system\backend\app\api\routes'
print('=== STEP R: All routes with async def and 0 await ===')

for f in os.listdir(routes_dir):
    if f.endswith('.py') and f != '__init__.py':
        p = os.path.join(routes_dir, f)
        with open(p, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        current_route = None
        route_line = 0
        fn_name = None
        fn_body = []
        
        for i, l in enumerate(lines):
            if l.strip().startswith('@router.'):
                current_route = l.strip()
                route_line = i + 1
            elif current_route and l.strip().startswith('async def '):
                fn_name = re.search(r'async def\s+(\w+)', l).group(1)
                fn_start = i + 1
                # Collect body until next @router or unindented def
                body_lines = []
                for k in range(i+1, len(lines)):
                    if lines[k].strip().startswith('@router.') or (lines[k].startswith('def ') or lines[k].startswith('async def ')):
                        break
                    body_lines.append(lines[k])
                
                # Check await count
                await_count = sum(1 for bl in body_lines if re.search(r'\bawait\b', bl))
                if await_count == 0:
                    print(f"{f}:{fn_start:4d} | {fn_name:30s} | Route: {current_route:30s} | await count: 0")
                current_route = None

# Inspect /risk/score and /rebalance/plan specifically
print('\n=== Inspecting risk_router and rebalance_router ===')
for rf in ['risk.py', 'rebalance.py']:
    p = os.path.join(routes_dir, rf)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as file:
            c = file.read()
        print(f"\n--- {rf} ---")
        for i, l in enumerate(c.split('\n')):
            if any(k in l for k in ['def get_', 'def calculate', 'async def', 'router.']):
                print(f"{i+1:4d}: {l}")

# -*- coding: utf-8 -*-
import os, re, ast

backend_dir = r'C:\trading\package\nvda_trading_system\backend\app'
target_files = ['correlation_engine.py', 'darkpool_analyzer.py', 'options_flow.py', 'event_engine.py']

print('=== 1. grep "return None" in target service files ===')
for tf in target_files:
    p = os.path.join(backend_dir, 'services', tf)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"\n--- {tf} ---")
        curr_fn = "module"
        for i, l in enumerate(lines):
            if l.strip().startswith('def '):
                curr_fn = re.search(r'def\s+(\w+)', l).group(1)
            if 'return None' in l:
                print(f"Line {i+1:4d} in {curr_fn}(): {l.strip()}")

print('\n=== 2. Implicit return None (except blocks without return in returning functions) ===')
for tf in target_files:
    p = os.path.join(backend_dir, 'services', tf)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for sub in ast.walk(node):
                    if isinstance(sub, ast.ExceptHandler):
                        # check if handler has return or raise
                        has_ret = any(isinstance(n, (ast.Return, ast.Raise)) for n in ast.walk(sub))
                        if not has_ret:
                            print(f"{tf} -> {node.name}() line {sub.lineno}: except handler without return/raise")

print('\n=== 3. darkpool_analyzer.py: self.ticker_obj initialization ===')
dp_file = os.path.join(backend_dir, 'services', 'darkpool_analyzer.py')
with open(dp_file, 'r', encoding='utf-8') as f:
    dp_lines = f.readlines()
for i, l in enumerate(dp_lines):
    if 'ticker_obj' in l or '__init__' in l:
        print(f"Line {i+1:4d}: {l.strip()}")

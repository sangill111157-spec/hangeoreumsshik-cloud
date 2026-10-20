# -*- coding: utf-8 -*-
import sys, os, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
conftest_p = os.path.join(backend_dir, 'tests', 'conftest.py')

with open(conftest_p, 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'snapshot = \{(.*?)\}', text, re.DOTALL)
if m:
    block = m.group(1)
    lines = [line.strip() for line in block.strip().split('\n') if ':' in line and not line.strip().startswith('#')]
    print(f"len(snapshot) == {len(lines)}")
    for l in lines:
        print(" ", l)
else:
    print("snapshot block not found")

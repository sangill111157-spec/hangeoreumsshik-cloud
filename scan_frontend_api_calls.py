# -*- coding: utf-8 -*-
import os, re

frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src'
matches = set()
for root, dirs, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith(('.ts', '.tsx', '.js', '.jsx')):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                for m in re.finditer(r'/api/[a-zA-Z0-9_\-/]+', content):
                    matches.add((f, m.group(0)))

for f, url in sorted(matches):
    print(f"{f:25s} -> {url}")

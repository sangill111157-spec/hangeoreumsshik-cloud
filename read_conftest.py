# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

cp = os.path.join(backend_dir, 'tests', 'conftest.py')
with open(cp, 'r', encoding='utf-8', errors='replace') as f:
    print(f.read())

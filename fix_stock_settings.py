# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(stock_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

if "from app.core.config import settings" not in st_c:
    st_c = "from app.core.config import settings\n" + st_c

with open(stock_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

subprocess.run('git add app/api/routes/stock.py', cwd=backend_dir, shell=True)
subprocess.run('git commit -m "fix(stock): import settings in stock.py for ENABLE_LIVE_ORDERS check (defect 156)"', cwd=backend_dir, shell=True)

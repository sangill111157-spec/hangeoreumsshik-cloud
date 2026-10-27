# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Fix trader.py
trader_path = os.path.join(backend_dir, r'app\api\routes\trader.py')
with open(trader_path, 'r', encoding='utf-8') as f:
    trader_c = f.read()

if "from fastapi import" in trader_c:
    trader_c = trader_c.replace("from fastapi import", "from fastapi import Body, HTTPException, Depends, ")
else:
    trader_c = "from fastapi import Body, HTTPException, Depends\n" + trader_c

with open(trader_path, 'w', encoding='utf-8') as f:
    f.write(trader_c)

# 2. Fix nvda.py
nvda_path = os.path.join(backend_dir, r'app\api\routes\nvda.py')
with open(nvda_path, 'r', encoding='utf-8') as f:
    nvda_c = f.read()

if "from fastapi import" in nvda_c:
    nvda_c = nvda_c.replace("from fastapi import", "from fastapi import Body, HTTPException, Depends, ")
else:
    nvda_c = "from fastapi import Body, HTTPException, Depends\n" + nvda_c

with open(nvda_path, 'w', encoding='utf-8') as f:
    f.write(nvda_c)

# 3. Fix rebalance.py
rebal_path = os.path.join(backend_dir, r'app\api\routes\rebalance.py')
with open(rebal_path, 'r', encoding='utf-8') as f:
    rebal_c = f.read()

if "from fastapi import" in rebal_c:
    rebal_c = rebal_c.replace("from fastapi import", "from fastapi import Body, HTTPException, Depends, ")
else:
    rebal_c = "from fastapi import Body, HTTPException, Depends\n" + rebal_c

with open(rebal_path, 'w', encoding='utf-8') as f:
    f.write(rebal_c)

subprocess.run('git add app/api/routes/trader.py app/api/routes/nvda.py app/api/routes/rebalance.py', cwd=backend_dir, shell=True)
subprocess.run('git commit -m "fix(routes): ensure Body and HTTPException are cleanly imported (defect 166)"', cwd=backend_dir, shell=True)
print("Route imports cleanly fixed!")

# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
rebal_path = os.path.join(backend_dir, r'app\api\routes\rebalance.py')
with open(rebal_path, 'r', encoding='utf-8') as f:
    c = f.read()

if "from typing import" not in c:
    c = "from typing import Dict, Any, List, Optional\n" + c

with open(rebal_path, 'w', encoding='utf-8') as f:
    f.write(c)

subprocess.run('git add app/api/routes/rebalance.py', cwd=backend_dir, shell=True)
subprocess.run('git commit -m "fix(rebalance): import typing Dict, Any (defect 166)"', cwd=backend_dir, shell=True)
print("rebalance.py typing imported!")

# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# Update app/services/__init__.py to import BASE_WEIGHTS instead of WEIGHTS
init_path = os.path.join(backend_dir, r'app\services\__init__.py')
with open(init_path, 'r', encoding='utf-8') as f:
    init_c = f.read()

init_c = init_c.replace("    WEIGHTS,\n", "    BASE_WEIGHTS,\n")
with open(init_path, 'w', encoding='utf-8') as f:
    f.write(init_c)

subprocess.run('git add app/services/__init__.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(services): update __init__.py import from WEIGHTS to BASE_WEIGHTS (defect 99)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
bt_path = os.path.join(backend_dir, r'app\services\backtester.py')

with open(bt_path, 'r', encoding='utf-8') as f:
    bt_c = f.read()

old_dict_block = """# Default weights
DEFAULT_WEIGHTS = {
    "investor_analysis": 0.30,
    "pod_signals": 0.25,
    "technical": 0.20,
    "sentiment": 0.15,
    "institutional": 0.10
}"""

new_dict_block = """# Default weights (결함 103 완결: BASE_WEIGHTS 단일 원천 SSOT 통일)
from app.services.master_signal import BASE_WEIGHTS
DEFAULT_WEIGHTS = BASE_WEIGHTS"""

if old_dict_block in bt_c:
    bt_c = bt_c.replace(old_dict_block, new_dict_block)
else:
    # generic replace
    import re
    bt_c = re.sub(r'DEFAULT_WEIGHTS = \{[^}]+\}', 'DEFAULT_WEIGHTS = BASE_WEIGHTS', bt_c)

with open(bt_path, 'w', encoding='utf-8') as f:
    f.write(bt_c)

subprocess.run('git add app/services/backtester.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(backtester): unify DEFAULT_WEIGHTS to BASE_WEIGHTS SSOT (defect 103)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


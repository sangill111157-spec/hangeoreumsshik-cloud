# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
st_path = os.path.join(backend_dir, r'app\api\routes\stock.py')

with open(st_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

old_opt_block = """            opt_in = {"options_composite_score": 70.0, "options_signal": "BUY", "confidence": 85, "available": True}"""

new_opt_block = """            opt_mock = {"available": False} if (force_unavailable and "options_flow" in force_unavailable) else {"options_composite_score": 70.0, "options_signal": "BUY", "confidence": 85, "available": True}
            opt_in = opt_mock"""

if old_opt_block in st_c:
    st_c = st_c.replace(old_opt_block, new_opt_block)

with open(st_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

subprocess.run('git add app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(route): support options_flow in force_unavailable query parameter (defect 120)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ss_path = os.path.join(backend_dir, r'app\services\stock_scanner.py')
with open(ss_path, 'r', encoding='utf-8') as f:
    ss_content = f.read()

# Clean replacement of bb attributes
bad_str = "getattr(bb, 'upper_band', getattr(bb, 'upper', 0.0))_band"
good_str = "getattr(bb, 'upper_band', getattr(bb, 'upper', 0.0))"
ss_content = ss_content.replace(bad_str, good_str)

bad_str_lower = "getattr(bb, 'lower_band', getattr(bb, 'lower', 0.0))_band"
good_str_lower = "getattr(bb, 'lower_band', getattr(bb, 'lower', 0.0))"
ss_content = ss_content.replace(bad_str_lower, good_str_lower)

with open(ss_path, 'w', encoding='utf-8') as f:
    f.write(ss_content)

subprocess.run('git add app/services/stock_scanner.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(scanner): correct syntax in bollinger band calculation"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

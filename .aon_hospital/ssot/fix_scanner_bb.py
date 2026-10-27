# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ss_path = os.path.join(backend_dir, r'app\services\stock_scanner.py')
with open(ss_path, 'r', encoding='utf-8') as f:
    ss_content = f.read()

# Replace bb.upper, bb.lower, bb.middle with upper_band, lower_band, middle_band
ss_content_new = ss_content.replace("bb.upper", "getattr(bb, 'upper_band', getattr(bb, 'upper', 0.0))")
ss_content_new = ss_content_new.replace("bb.lower", "getattr(bb, 'lower_band', getattr(bb, 'lower', 0.0))")
ss_content_new = ss_content_new.replace("bb.middle", "getattr(bb, 'middle_band', getattr(bb, 'middle', 0.0))")

if ss_content != ss_content_new:
    with open(ss_path, 'w', encoding='utf-8') as f:
        f.write(ss_content_new)
    print("stock_scanner.py BollingerBands attribute references fixed!")
    subprocess.run('git add app/services/stock_scanner.py', cwd=backend_dir, shell=True)
    res_c = subprocess.run('git commit -m "fix(scanner): correct BollingerBands attribute names to upper_band/lower_band to prevent secondary scan crash"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print("Commit Output:\n", res_c.stdout)


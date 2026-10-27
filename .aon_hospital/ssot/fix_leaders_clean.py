# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, l in enumerate(lines):
    if "elif leaders == 0:" in l:
        # skip this line and the next adjustment -= 2 line
        skip = True
        continue
    if skip and "adjustment -= 2" in l:
        skip = False
        continue
    new_lines.append(l)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(correlation): cleanly remove leaders==0 -2 penalty (defects 36,50)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_lines = f.readlines()

new_lines = []
skip = False
for idx, line in enumerate(ms_lines):
    if 'def get_weights_for_modules(' in line:
        skip = True
        continue
    elif skip:
        if 'def _apply_market_regime(' in line:
            new_lines.append(line)
            skip = False
        continue
    else:
        new_lines.append(line)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal): completely delete obsolete get_weights_for_modules function from master_signal.py"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


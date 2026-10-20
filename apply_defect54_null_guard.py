# -*- coding: utf-8 -*-
import sys, os, subprocess

frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Patch App.tsx for 결함 54 (null guard on toFixed)
app_tsx = os.path.join(frontend_dir, r'src\App.tsx')
with open(app_tsx, 'r', encoding='utf-8') as f:
    app_c = f.read()

old_fix1 = "{data?.master_score != null ? data.master_score.toFixed(1) : '—'}"
# Check if toFixed(1) without null guard exists
old_pattern1 = "{data?.master_score.toFixed(1)}"
old_pattern2 = "{data?.raw_score.toFixed(1)}"

# Let's inspect App.tsx lines around 1970 and 2030
lines = app_c.splitlines()
new_lines = []
for idx, l in enumerate(lines):
    if 'data?.master_score.toFixed' in l and 'data?.master_score != null' not in l:
        new_l = l.replace('data?.master_score.toFixed(1)', "data?.master_score != null ? data.master_score.toFixed(1) : '—'")
        new_lines.append(new_l)
        print(f"Patched line {idx+1}: {new_l}")
    elif 'data?.raw_score.toFixed' in l and 'data?.raw_score != null' not in l:
        new_l = l.replace('data?.raw_score.toFixed(1)', "data?.raw_score != null ? data.raw_score.toFixed(1) : '—'")
        new_lines.append(new_l)
        print(f"Patched line {idx+1}: {new_l}")
    else:
        new_lines.append(l)

with open(app_tsx, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

subprocess.run('git add nvda-trading-dashboard/src/App.tsx', cwd=r'C:\trading\package\nvda_trading_system', shell=True)
res_c = subprocess.run('git commit -m "fix(ui): add null guard to master_score and raw_score toFixed calls preventing white screen crash (defect 54)"', cwd=r'C:\trading\package\nvda_trading_system', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


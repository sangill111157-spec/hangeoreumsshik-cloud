# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

old_corr = """    # 리더주 강세
    leaders = correlation.get("leader_stocks_positive", 0)
    if leaders >= 3:
        adjustment += 2
    elif leaders == 0:
        adjustment -= 2"""

new_corr = """    # 리더주 강세 (결함 36·50 완결: leaders==0 -2 패널티 제거 및 중립 0 처리)
    leaders = correlation.get("leader_stocks_positive", 0)
    if leaders >= 3:
        adjustment += 2"""

if old_corr in ms_c:
    ms_c = ms_c.replace(old_corr, new_corr)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(correlation): eliminate -2 penalty when leaders==0 (defects 36,50)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


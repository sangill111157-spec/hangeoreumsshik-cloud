# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

old_call = """        # 10. 켈리 계산
        kelly_res = calculate_kelly(
            win_rate=0.65, avg_win=1.8, avg_loss=1.0,
            account_balance=account_balance, stock_price=stock_price, position_direction=signal,
            confidence=master_conf
        )"""

new_call = """        # 10. 켈리 계산
        kelly_res = calculate_kelly(
            win_rate=0.65, avg_win=1.8, avg_loss=1.0,
            account_balance=account_balance, stock_price=stock_price, position_direction=signal,
            confidence=confidence
        )"""

if old_call in ms_c:
    ms_c = ms_c.replace(old_call, new_call)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(kelly): pass confidence variable correctly to calculate_kelly (defect 130)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


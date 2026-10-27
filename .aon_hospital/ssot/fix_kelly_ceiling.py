# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Update calculate_kelly implementation
old_calc_shares = """    recommended_shares = int(target_position_value / stock_price) if stock_price > 0 else 0
    actual_position_value = round(recommended_shares * stock_price, 2)
    actual_account_percentage = round((actual_position_value / account_balance) * 100, 2) if account_balance > 0 else 0.0"""

new_calc_shares = """    recommended_shares = int(target_position_value / stock_price) if stock_price > 0 else 0
    # 결함 115 완결: 1단계 드라이런 하드 실링 13주 ($2,819.05 <= $2,820 / 2.82%) 강제 적용
    STAGE_1_DRY_RUN_SHARE_CEILING = 13
    if recommended_shares > STAGE_1_DRY_RUN_SHARE_CEILING:
        recommended_shares = STAGE_1_DRY_RUN_SHARE_CEILING
    actual_position_value = round(recommended_shares * stock_price, 2)
    actual_account_percentage = round((actual_position_value / account_balance) * 100, 2) if account_balance > 0 else 0.0"""

if old_calc_shares in ms_c:
    ms_c = ms_c.replace(old_calc_shares, new_calc_shares)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(kelly): enforce STAGE_1_DRY_RUN_SHARE_CEILING = 13 (defect 115)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


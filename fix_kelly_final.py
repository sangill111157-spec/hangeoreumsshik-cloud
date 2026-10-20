# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

old_shares_code = """    # BUY / STRONG_BUY 구간: 정상 포지션 사이징
    target_pos_val = account_balance * kelly_fraction
    if stock_price > 0 and target_pos_val >= stock_price:
        shares = int(target_pos_val / stock_price)
    else:
        shares = 0

    actual_pos_val = round(shares * stock_price, 2)"""

new_shares_code = """    # BUY / STRONG_BUY 구간: 정상 포지션 사이징
    target_pos_val = account_balance * kelly_fraction
    if stock_price > 0 and target_pos_val >= stock_price:
        shares = int(target_pos_val / stock_price)
    else:
        shares = 0

    # 결함 115 완결: 1단계 드라이런 하드 실링 13주 ($2,819.05 <= $2,820 / 2.82%) 강제 적용
    STAGE_1_DRY_RUN_SHARE_CEILING = 13
    if shares > STAGE_1_DRY_RUN_SHARE_CEILING:
        shares = STAGE_1_DRY_RUN_SHARE_CEILING

    actual_pos_val = round(shares * stock_price, 2)"""

if old_shares_code in ms_c:
    ms_c = ms_c.replace(old_shares_code, new_shares_code)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(kelly): enforce STAGE_1_DRY_RUN_SHARE_CEILING = 13 in calculate_kelly (defect 115)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


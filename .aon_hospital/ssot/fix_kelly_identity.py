# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for l in lines:
    if l.startswith('def calculate_kelly('):
        new_lines.append("""def calculate_kelly(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    account_balance: float = 100000,
    stock_price: float = 220
) -> KellyCriterion:
    \"\"\"켈리 공식 계산 (결함 63·69: 최소 1주 배정 및 금액-수량 항등식 position_value = shares * price 보장)\"\"\"
    if avg_loss == 0:
        kelly_pct = 0.0
    else:
        win_loss_ratio = avg_win / abs(avg_loss)
        kelly_pct = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

    # 25% Fractional Kelly (0~50% 클램프)
    kelly_pct = max(0.0, min(kelly_pct * 0.25, 50.0))

    # 목표 투자 금액
    target_pos_val = account_balance * (kelly_pct / 100.0)
    
    # 켈리 배정 비율이 유효할 경우(>0) 최소 1주 배정하여 실주문 실행 가능 상태 보장
    if target_pos_val > 0 and stock_price > 0:
        shares = max(1, int(target_pos_val / stock_price))
    else:
        shares = 0
    
    actual_pos_val = round(shares * stock_price, 2)
    stop_loss = stock_price * 0.92

    return KellyCriterion(
        kelly_percentage=round(kelly_pct, 1),
        recommended_shares=shares,
        position_value=actual_pos_val,
        account_percentage=round((actual_pos_val / account_balance * 100.0) if account_balance > 0 else 0.0, 1),
        stop_loss=round(stop_loss, 2),
        stop_loss_pct=8.0
    )
""")
        skip = True
    elif skip:
        if l.startswith('class MasterSignalEngine:'):
            skip = False
            new_lines.append(l)
        continue
    else:
        new_lines.append(l)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal): guarantee minimum 1 share allocation and strict position_value = shares * price identity (defect 69)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


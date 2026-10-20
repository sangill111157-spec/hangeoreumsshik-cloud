# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "STAGE1_CAP_PCT = 0.0282" in line:
        start_idx = i
    if start_idx != -1 and "return KellyCriterion(" in line:
        # find the closing paren for this return
        for j in range(i, len(lines)):
            if lines[j].strip() == ")":
                end_idx = j + 1
                break
        break

print(f"Replacing lines {start_idx} to {end_idx}")

new_block = [
    "    STAGE1_CAP_PCT = 0.0282  # 1단계 2.82% ($2,820.00 상한)\n",
    "    ceiling_value = round(account_balance * STAGE1_CAP_PCT, 2)\n",
    "    max_ceiling_shares = int(ceiling_value / stock_price) if stock_price > 0 else 0\n",
    "\n",
    "    ceiling_applied = raw_shares > max_ceiling_shares\n",
    "    base_shares = max_ceiling_shares if ceiling_applied else raw_shares\n",
    "\n",
    "    # 결함 130 완결: 신뢰도 연동 사이징 정책 적용 (floor(Shares * Confidence/100), 신뢰도 < 40 시 0주)\n",
    "    if confidence < 40:\n",
    "        shares = 0\n",
    "    else:\n",
    "        conf_factor = float(confidence) / 100.0\n",
    "        shares = int(base_shares * conf_factor)\n",
    "\n",
    "    actual_pos_val = round(shares * stock_price, 2)\n",
    "    # 결함 121 완결: python -O 무력화 방지 ValueError 런타임 예외 적용\n",
    "    if actual_pos_val > ceiling_value + 1e-4:\n",
    "        raise ValueError(f'Position value ${actual_pos_val} exceeded stage 1 ceiling ${ceiling_value}!')\n",
    "    actual_account_pct = round((actual_pos_val / account_balance * 100.0) if account_balance > 0 else 0.0, 2)\n",
    "    stop_loss = round(stock_price * 0.92, 2) if stock_price > 0 else 0.0\n",
    "\n",
    "    return KellyCriterion(\n",
    "        kelly_percentage=kelly_percentage,\n",
    "        recommended_shares=shares,\n",
    "        position_value=actual_pos_val,\n",
    "        account_percentage=actual_account_pct,\n",
    "        stop_loss=stop_loss,\n",
    "        stop_loss_pct=8.0,\n",
    "        ceiling_applied=ceiling_applied,\n",
    "        ceiling_reason='stage1_dry_run' if ceiling_applied else None,\n",
    "        ceiling_shares=max_ceiling_shares if ceiling_applied else None\n",
    "    )\n"
]

lines[start_idx:end_idx] = new_block

with open(ms_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(kelly): precisely apply confidence-linked sizing formula (defect 130)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "class KellyCriterion:" in l:
        # Replace the fields in KellyCriterion
        lines[i+1] = "    kelly_percentage: float\n"
        lines[i+2] = "    recommended_shares: int\n"
        lines[i+3] = "    position_value: float\n"
        lines[i+4] = "    account_percentage: float\n"
        lines[i+5] = "    stop_loss: Optional[float] = None\n"
        lines[i+6] = "    stop_loss_pct: Optional[float] = None\n"
        # Insert ceiling fields
        lines.insert(i+7, "    ceiling_applied: bool = False\n")
        lines.insert(i+8, "    ceiling_reason: Optional[str] = None\n")
        lines.insert(i+9, "    ceiling_shares: Optional[int] = None\n")
        break

with open(ms_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(kelly): add ceiling fields directly into KellyCriterion dataclass (defect 118)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


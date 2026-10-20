# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

old_kc_dataclass = """@dataclass
class KellyCriterion:
    kelly_percentage: float
    recommended_shares: int
    position_value: float
    account_percentage: float
    stop_loss: Optional[float] = None
    stop_loss_pct: Optional[float] = None"""

new_kc_dataclass = """@dataclass
class KellyCriterion:
    kelly_percentage: float
    recommended_shares: int
    position_value: float
    account_percentage: float
    stop_loss: Optional[float] = None
    stop_loss_pct: Optional[float] = None
    ceiling_applied: bool = False
    ceiling_reason: Optional[str] = None
    ceiling_shares: Optional[int] = None"""

if old_kc_dataclass in ms_c:
    ms_c = ms_c.replace(old_kc_dataclass, new_kc_dataclass)

# Update HOLD return block in calculate_kelly
old_hold_ret = """        return KellyCriterion(
            kelly_percentage=kelly_percentage,
            recommended_shares=0,
            position_value=0.0,
            account_percentage=0.0,
            stop_loss=None,
            stop_loss_pct=None
        )"""

new_hold_ret = """        return KellyCriterion(
            kelly_percentage=kelly_percentage,
            recommended_shares=0,
            position_value=0.0,
            account_percentage=0.0,
            stop_loss=None,
            stop_loss_pct=None,
            ceiling_applied=False,
            ceiling_reason=None,
            ceiling_shares=None
        )"""

if old_hold_ret in ms_c:
    ms_c = ms_c.replace(old_hold_ret, new_hold_ret)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(kelly): add ceiling fields with defaults to KellyCriterion dataclass and HOLD path (defect 118)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


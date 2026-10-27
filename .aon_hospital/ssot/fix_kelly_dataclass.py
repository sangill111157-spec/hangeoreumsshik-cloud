# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

correct_kelly_class = """@dataclass
class KellyCriterion:
    kelly_percentage: float
    recommended_shares: int
    position_value: float
    account_percentage: float
    stop_loss: Optional[float] = None
    stop_loss_pct: Optional[float] = None
    ceiling_applied: bool = False
    ceiling_reason: Optional[str] = None
    ceiling_shares: Optional[int] = None

KellyResult = KellyCriterion
"""

import re
ms_c = re.sub(r'class KellyCriterion:.*?class MasterSignalResult:', correct_kelly_class + '\n\n@dataclass\nclass MasterSignalResult:', ms_c, flags=re.DOTALL)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
subprocess.run('git commit -m "fix(dataclass): properly decorate KellyCriterion with @dataclass"', cwd=backend_dir, shell=True)

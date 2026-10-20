# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Remove faulty import from app.schemas.nvda and define KellyResult alias
ms_c = ms_c.replace("from app.schemas.nvda import KellyResult, MasterSignalFinalResponse, ComponentScore, AdjustmentScore\n", "")
if "KellyResult = KellyCriterion" not in ms_c:
    ms_c = ms_c.replace("class KellyCriterion:", "class KellyCriterion:\n    pass\n\nKellyResult = KellyCriterion\n\nclass KellyCriterion:")

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
subprocess.run('git commit -m "fix(dataclass): alias KellyResult to KellyCriterion dataclass in master_signal.py"', cwd=backend_dir, shell=True)

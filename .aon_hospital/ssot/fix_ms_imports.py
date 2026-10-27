# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

header_imports = """from typing import Optional, List, Dict, Any
from app.schemas.nvda import KellyResult, MasterSignalFinalResponse, ComponentScore, AdjustmentScore
from app.services.institutional_flow import calculate_institutional_confidence
"""

if "from app.schemas.nvda import KellyResult" not in ms_c:
    ms_c = header_imports + ms_c

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
subprocess.run('git commit -m "fix(imports): ensure KellyResult and schemas are imported in master_signal.py"', cwd=backend_dir, shell=True)

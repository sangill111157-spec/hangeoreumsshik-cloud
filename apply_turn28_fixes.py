# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Create app/services/confidence.py
conf_path = os.path.join(backend_dir, r'app\services\confidence.py')
with open(conf_path, 'w', encoding='utf-8') as f:
    f.write('''# -*- coding: utf-8 -*-
"""
신뢰도 클램프 단일 원천 (SSOT)
"""

CONF_MIN: int = 10
CONF_MAX: int = 95

def clamp_conf(value: float) -> int:
    """모든 모듈의 신뢰도 방출 지점에서 반드시 통과해야 하는 유일 관문 (10~95)"""
    return int(max(CONF_MIN, min(CONF_MAX, round(value))))
''')

# 2. Create app/services/institutional_flow.py
inst_path = os.path.join(backend_dir, r'app\services\institutional_flow.py')
with open(inst_path, 'w', encoding='utf-8') as f:
    f.write('''# -*- coding: utf-8 -*-
"""
기관/13F 신뢰도 산출 모듈 (B-2 결함 84·89 해소)
"""
from app.services.confidence import clamp_conf

MIN_FILINGS_FOR_FULL: int = 10

def calculate_institutional_confidence(filings_count: int = 5, agreement_ratio: float = 0.5) -> int:
    """기관/13F 신뢰도 산출부"""
    coverage = min(1.0, filings_count / float(MIN_FILINGS_FOR_FULL))
    return clamp_conf(40.0 + coverage * agreement_ratio * 55.0)
''')

# 3. Update master_signal.py to use institutional_flow confidence calculation
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

if "from app.services.institutional_flow import calculate_institutional_confidence" not in ms_c:
    ms_c = "from app.services.institutional_flow import calculate_institutional_confidence\n" + ms_c

old_ms_inst_conf = '"institutional": float(institutional.get("confidence", 50))'
new_ms_inst_conf = '"institutional": float(institutional.get("confidence", calculate_institutional_confidence(institutional.get("filings_count", 5), institutional.get("agreement_ratio", 0.5))))'

if old_ms_inst_conf in ms_c:
    ms_c = ms_c.replace(old_ms_inst_conf, new_ms_inst_conf)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/confidence.py app/services/investor_analysis.py app/services/technical_analysis.py app/services/institutional_flow.py app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(confidence,investor,tech,inst): add confidence SSOT, symmetric investor coefs, tech clamp, and institutional confidence calculation (defects 101,102,84,89)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


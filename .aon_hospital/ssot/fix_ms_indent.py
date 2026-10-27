# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Fix the indent of eps_bonus
target = """        # 결함 167 완결: EPS 컨텍스트 가산 보정 공식 비활성 봉인 (0점 고정)
            eps_bonus = 0 if expected_eps > 0 else 3"""

correct = """        # 결함 167 완결: EPS 컨텍스트 가산 보정 공식 비활성 봉인 (0점 고정)
        eps_bonus = 0"""

if target in ms_c:
    ms_c = ms_c.replace(target, correct)
else:
    import re
    ms_c = re.sub(r'# 결함 167 완결:.*?eps_bonus = [^\n]+', '# 결함 167 완결: EPS 컨텍스트 가산 보정 공식 비활성 봉인 (0점 고정)\n        eps_bonus = 0', ms_c)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
subprocess.run('git commit -m "fix(master_signal): fix indentation on eps_bonus sealed line (defect 167)"', cwd=backend_dir, shell=True)
print("master_signal.py indent fixed successfully!")

# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

score_func = """def score_to_5level_signal(score: Optional[float]) -> str:
    \"\"\"0-100 점수를 5단계 표준 시그널로 단조 변환 (결함 74: 라벨 임계 단일 함수 이관)\"\"\"
    if score is None:
        return "UNAVAILABLE"
    if score >= 80.0:
        return "STRONG_BUY"
    if score >= 65.0:
        return "BUY"
    if score >= 35.0:
        return "HOLD"
    if score >= 20.0:
        return "SELL"
    return "STRONG_SELL"
"""

if "def score_to_5level_signal" not in ms_c:
    ms_c = score_func + "\n" + ms_c

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal): place score_to_5level_signal at top level in master_signal.py (defect 74)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


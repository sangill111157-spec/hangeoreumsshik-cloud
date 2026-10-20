# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# 1. Update investor_to_score definition
old_inv_def = """def investor_to_score(overall_confidence: int) -> float:
    \"\"\"5대 투자자 분석 confidence를 0-100 점수로 변환\"\"\"
    return float(overall_confidence)"""

new_inv_def = """def investor_to_score(investor_data: Any) -> float:
    \"\"\"5대 투자자 분석 점수 변환 (결함 53 해소: score 우선 참조)\"\"\"
    if isinstance(investor_data, dict):
        if "score" in investor_data:
            return float(investor_data["score"])
        return float(investor_data.get("overall_confidence", 50))
    if isinstance(investor_data, (int, float)):
        return float(investor_data)
    return 50.0"""

if old_inv_def in ms_c:
    ms_c = ms_c.replace(old_inv_def, new_inv_def)

# 2. Update line 477 caller
old_call = 'investor_score = investor_to_score(investor_analysis.get("overall_confidence", 50))'
new_call = 'investor_score = investor_to_score(investor_analysis)'

if old_call in ms_c:
    ms_c = ms_c.replace(old_call, new_call)
    print("master_signal.py line 477 caller patched!")

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal): pass full investor dict to investor_to_score to prioritize score field (defect 53)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


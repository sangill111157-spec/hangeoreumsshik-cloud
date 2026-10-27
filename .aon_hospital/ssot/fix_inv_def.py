# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

old_def = """def investor_to_score(investor_score: float) -> float:
    \"\"\"투자자 분석 -> 0-100 점수\"\"\"
    return investor_score"""

new_def = """def investor_to_score(investor_data: Any) -> float:
    \"\"\"5대 투자자 분석 점수 변환 (결함 53 해소: score 우선 참조)\"\"\"
    if isinstance(investor_data, dict):
        if "score" in investor_data:
            return float(investor_data["score"])
        return float(investor_data.get("overall_confidence", 50.0))
    if isinstance(investor_data, (int, float)):
        return float(investor_data)
    return 50.0"""

if old_def in ms_c:
    ms_c = ms_c.replace(old_def, new_def)
    with open(ms_path, 'w', encoding='utf-8') as f:
        f.write(ms_c)
    print("master_signal.py investor_to_score accurately updated!")

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal): accurately unpack investor_data in investor_to_score (defect 53)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


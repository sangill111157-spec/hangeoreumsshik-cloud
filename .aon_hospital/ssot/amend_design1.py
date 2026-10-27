# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_lines = f.readlines()

new_lines = []
skip = False
for idx, line in enumerate(ms_lines):
    if 'def pod_to_score(pod_signals: List[dict]) -> float:' in line:
        new_func = """def pod_to_score(pod_signals: List[dict]) -> float:
    \"\"\"Pod 신호 목록을 0-100 점수로 선형 변환 (설계 1: 원시점수 산술평균 직결)\"\"\"
    if not pod_signals:
        return 50.0

    raw_scores = [float(s.get("score", 0.0)) for s in pod_signals]
    if not raw_scores:
        return 50.0

    raw_avg = sum(raw_scores) / len(raw_scores)
    # [-100, +100] -> [0, 100] 선형 직결 변환
    return (raw_avg + 100.0) / 2.0
"""
        new_lines.append(new_func)
        skip = True
    elif skip:
        if 'def technical_to_score' in line:
            new_lines.append(line)
            skip = False
        continue
    else:
        new_lines.append(line)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit --amend -m "fix(signal,kis): bind pod score linearly (design 1) and apply 80/65/35/20 symmetric grid (defect 15) [Pre 60.09126984126984/HOLD -> Post 58.15000000000000/HOLD]"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Amend Commit Output:\n", res_c.stdout)


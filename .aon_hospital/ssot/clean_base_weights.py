# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_lines = f.readlines()

new_lines = []
in_base_weights = False
for idx, line in enumerate(ms_lines):
    if 'BASE_WEIGHTS = {' in line or 'BASE_WEIGHTS: Dict' in line:
        in_base_weights = True
        new_lines.append("""BASE_WEIGHTS = {
    "investor_analysis": 0.20,    # 5대 투자자 분석 20% (승인 벡터)
    "pod_signals": 0.20,          # 멀티전략(Pod) 20%
    "technical": 0.15,            # 기술적 분석 15%
    "options_flow": 0.15,         # 옵션 플로우 15% (승인 벡터)
    "llm_news": 0.12,             # AI 뉴스 분석 12%
    "darkpool": 0.10,             # 다크풀 분석 10%
    "institutional": 0.08,       # 13F 기관 8%
}
""")
    elif in_base_weights:
        if '}' in line:
            in_base_weights = False
        continue
    else:
        new_lines.append(line)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("master_signal.py BASE_WEIGHTS cleanly overwritten to approved 0.20/0.15 vector!")

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal): strictly enforce 0.20/0.15 approved BASE_WEIGHTS vector in master_signal.py"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


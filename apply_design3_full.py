# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_lines = f.readlines()

new_lines = []
skip = False
for idx, line in enumerate(ms_lines):
    if 'def _detect_unavailable_modules(' in line:
        new_detect = """    def _detect_unavailable_modules(
        self,
        investor_analysis: dict,
        pod_signals: list,
        technical: dict,
        llm_news: dict,
        options_flow: dict,
        darkpool: dict,
        institutional: dict,
    ) -> List[str]:
        \"\"\"사용 불가 모듈 2단 감지 (설계 3: 7개 모듈 전수 가용성 검증)\"\"\"
        unavailable = []

        def _is_avail(m):
            if not m or not isinstance(m, dict):
                return False
            return bool(m.get("available", False))

        if not _is_avail(investor_analysis):
            unavailable.append("investor_analysis")

        if not pod_signals or (isinstance(pod_signals, list) and len(pod_signals) == 0):
            unavailable.append("pod_signals")

        if not _is_avail(technical):
            unavailable.append("technical")

        if not _is_avail(llm_news):
            unavailable.append("llm_news")

        if not _is_avail(options_flow):
            unavailable.append("options_flow")

        if not _is_avail(darkpool):
            unavailable.append("darkpool")

        if not _is_avail(institutional):
            unavailable.append("institutional")

        return unavailable
"""
        new_lines.append(new_detect)
        skip = True
    elif skip:
        if 'def get_master_signal(' in line or 'def calculate_final_master_signal(' in line:
            new_lines.append(line)
            skip = False
        continue
    else:
        new_lines.append(line)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# Also check calculate_final_master_signal dynamic proportional weights
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_content = f.read()

# Replace get_weights_for_modules usage if any
old_weights_calc = """        # 4. 가중치 계산 (모듈 미지원 시 재분배)
        weights = get_weights_for_modules(unavailable_modules)"""

new_weights_calc = """        # 4. 가중치 계산 (설계 3: BASE_WEIGHTS 기반 동적 비례 재분배 단일 공식)
        available_modules = [m for m in BASE_WEIGHTS.keys() if m not in unavailable_modules]
        available_weights_sum = sum(BASE_WEIGHTS[m] for m in available_modules)
        coverage = available_weights_sum / total_base_weights if total_base_weights > 0 else 0.0
        available_module_count = len(available_modules)

        if coverage < 0.60 or available_weights_sum <= 0:
            return MasterSignalResult(
                signal="UNAVAILABLE",
                master_score=None,
                raw_score=None,
                confidence=None,
                components=components,
                key_drivers=["데이터 가용성 부족 (Coverage < 60%)"],
                symbol=symbol,
                coverage=round(coverage, 2),
                unavailable_modules=unavailable_modules,
                available_module_count=available_module_count
            )

        weights_used = {m: BASE_WEIGHTS[m] / available_weights_sum for m in available_modules}
        raw_score = sum(module_scores[m] * weights_used[m] for m in available_modules)"""

# Commit changes
subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal): unify coverage to dynamic BASE_WEIGHTS proportion and apply 7-module 2-stage availability guard (Design 3)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


# -*- coding: utf-8 -*-
import sys

# 1. Patch master_signal.py by lines
ms_file = r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py'
with open(ms_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1) Add coverage fields to MasterSignalResult around line 150
for i, l in enumerate(lines):
    if 'weights_used: Dict[str, float]' in l:
        lines[i] = l + '    coverage: float = 1.0                                          # 모듈 커버리지 (0.0~1.0)\n    available_module_count: int = 7                                # 가용 모듈 수\n'
        break

# 2) Replace lines 525 to 555
start_idx = None
end_idx = None
for i, l in enumerate(lines):
    if 'weights = get_weights_for_modules' in l:
        start_idx = i - 1  # include comment line
    if 'master_score = max(0, min(100, adjusted_score))' in l:
        end_idx = i + 1
        break

if start_idx is None or end_idx is None:
    print("ERROR: start_idx or end_idx not found")
    sys.exit(1)

new_block = """        # 2. 각 모듈 점수 변환
        investor_score = investor_to_score(investor_analysis.get("overall_confidence", 50))
        pod_score = pod_to_score(pod_signals)
        tech_score = technical_to_score(technical)
        news_score = llm_news_to_score(llm_news)
        inst_score = institutional_to_score(institutional, symbol)
        options_score = options_flow_to_score(options_flow)
        darkpool_score = darkpool_to_score(darkpool)

        module_scores = {
            "investor_analysis": investor_score,
            "pod_signals": pod_score,
            "technical": tech_score,
            "llm_news": news_score,
            "institutional": inst_score,
            "options_flow": options_score,
            "darkpool": darkpool_score
        }

        # 3. 가용 모듈 식별 및 동적 가중치 재정규화
        available_modules = [m for m in BASE_WEIGHTS.keys() if m not in unavailable_modules]
        available_weights_sum = sum(BASE_WEIGHTS[m] for m in available_modules)
        total_base_weights = sum(BASE_WEIGHTS.values())
        coverage = available_weights_sum / total_base_weights if total_base_weights > 0 else 0.0
        available_module_count = len(available_modules)

        # 4. 시장 상황 조정 계산
        event_adjustment, event_reason = event_to_adjustment(events)
        correlation_adjustment, corr_reason = correlation_to_adjustment(correlation)

        # 5. 커버리지 60% 하한 방어 (Zero division 포함)
        if coverage < 0.60 or available_weights_sum <= 0:
            logger.warning(f"Insufficient module coverage ({coverage:.1%}) for {symbol}. Returning UNAVAILABLE.")
            weights_used = {}
            raw_score = None
            master_score = None
            signal = "UNAVAILABLE"
            signal_ko = "데이터 부족"
        else:
            # 가중치 재정규화 (가용 모듈의 가중치 합을 1.0으로 환산)
            weights_used = {m: BASE_WEIGHTS[m] / available_weights_sum for m in available_modules}
            raw_score = sum(module_scores[m] * weights_used[m] for m in available_modules)
            adjusted_score = raw_score + event_adjustment + correlation_adjustment
            master_score = max(0, min(100, adjusted_score))
"""

lines[start_idx:end_idx] = [new_block]

# 3) Update MasterSignalResult constructor call
for i, l in enumerate(lines):
    if 'weights_used=weights' in l:
        lines[i] = '            weights_used=weights_used,\n            coverage=round(coverage, 2),\n            available_module_count=available_module_count\n'
        break

with open(ms_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("PATCH master_signal.py SUCCESS")

# -*- coding: utf-8 -*-
import sys

ms_file = r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py'
with open(ms_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find coverage check block and replace with early return
start_idx = None
end_idx = None
for i, l in enumerate(lines):
    if 'if coverage < 0.60 or available_weights_sum <= 0:' in l:
        start_idx = i
    if start_idx is not None and 'else:' in l:
        end_idx = i + 1
        break

if start_idx is None or end_idx is None:
    print("ERROR: indices not found")
    sys.exit(1)

early_return_block = """        if coverage < 0.60 or available_weights_sum <= 0:
            logger.warning(f"Insufficient module coverage ({coverage:.1%}) for {symbol}. Returning UNAVAILABLE.")
            return MasterSignalResult(
                symbol=symbol,
                master_score=None,
                raw_score=None,
                signal="UNAVAILABLE",
                signal_ko="데이터 부족",
                confidence=0,
                components=components,
                adjustments=[],
                kelly=KellyCriterion(0.0, 0, 0.0, 0.0, 0.0),
                recommendation="분석에 필요한 최소 데이터(60%)가 충족되지 않아 시그널을 산출할 수 없습니다.",
                risks=["데이터 부족으로 인한 분석 불가"],
                timestamp=datetime.now().isoformat(),
                unavailable_modules=unavailable_modules,
                weights_used={},
                coverage=round(coverage, 2),
                available_module_count=available_module_count
            )

        # 가중치 재정규화 (가용 모듈의 가중치 합을 1.0으로 환산)
        weights_used = {m: BASE_WEIGHTS[m] / available_weights_sum for m in available_modules}
        raw_score = sum(module_scores[m] * weights_used[m] for m in available_modules)
        adjusted_score = raw_score + event_adjustment + correlation_adjustment
        master_score = max(0, min(100, adjusted_score))
"""

# Find components creation line index to move components definition before early return
# In calculate_final_master_signal, components is created around line 600. Let's move components before step 5.


# -*- coding: utf-8 -*-
import sys

# 1. Patch master_signal.py
ms_file = r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py'
with open(ms_file, 'r', encoding='utf-8') as f:
    ms_content = f.read()

# Add coverage fields to MasterSignalResult
t_msr = """    unavailable_modules: List[str] = field(default_factory=list)  # 사용 불가 모듈
    weights_used: Dict[str, float] = field(default_factory=dict)   # 실제 사용된 가중치"""

r_msr = """    unavailable_modules: List[str] = field(default_factory=list)  # 사용 불가 모듈
    weights_used: Dict[str, float] = field(default_factory=dict)   # 실제 사용된 가중치
    coverage: float = 1.0                                          # 모듈 커버리지 (0.0~1.0)
    available_module_count: int = 7                                # 가용 모듈 수"""

if t_msr not in ms_content:
    print("ERROR: t_msr not found")
    sys.exit(1)
ms_content = ms_content.replace(t_msr, r_msr, 1)

# Replace master calculation with dynamic normalization and coverage check
t_calc = """        # 2. 가중치 결정 (재분배 로직)
        weights = get_weights_for_modules(unavailable_modules)

        # 3. 각 모듈 점수 변환
        investor_score = investor_to_score(investor_analysis.get("overall_confidence", 50))
        pod_score = pod_to_score(pod_signals)
        tech_score = technical_to_score(technical)
        news_score = llm_news_to_score(llm_news)
        inst_score = institutional_to_score(institutional, symbol)
        options_score = options_flow_to_score(options_flow)
        darkpool_score = darkpool_to_score(darkpool)

        # 4. 종합 점수 합산 (기본 점수)
        raw_score = (
            investor_score * weights["investor_analysis"] +
            pod_score * weights["pod_signals"] +
            tech_score * weights["technical"] +
            news_score * weights["llm_news"] +
            inst_score * weights["institutional"] +
            options_score * weights["options_flow"] +
            darkpool_score * weights["darkpool"]
        )

        # 5. 시장 상황 조정
        event_adjustment, event_reason = event_to_adjustment(events)
        correlation_adjustment, corr_reason = correlation_to_adjustment(correlation)

        # 6. 최종 점수 (0-125 범위 0-100 정규화)
        adjusted_score = raw_score + event_adjustment + correlation_adjustment
        master_score = max(0, min(100, adjusted_score))"""

r_calc = """        # 2. 각 모듈 점수 변환
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
            master_score = max(0, min(100, adjusted_score))"""

if t_calc not in ms_content:
    print("ERROR: t_calc not found")
    sys.exit(1)
ms_content = ms_content.replace(t_calc, r_calc, 1)

# Update return MasterSignalResult to include coverage
t_ret = """        return MasterSignalResult(
            symbol=symbol,
            master_score=master_score,
            raw_score=raw_score,
            signal=signal,
            signal_ko=signal_ko,
            confidence=confidence,
            components=components,
            adjustments=adjustments,
            kelly=kelly,
            recommendation=recommendation,
            risks=risks,
            timestamp=datetime.now().isoformat(),
            unavailable_modules=unavailable_modules,
            weights_used=weights
        )"""

r_ret = """        return MasterSignalResult(
            symbol=symbol,
            master_score=master_score,
            raw_score=raw_score,
            signal=signal,
            signal_ko=signal_ko,
            confidence=confidence,
            components=components,
            adjustments=adjustments,
            kelly=kelly,
            recommendation=recommendation,
            risks=risks,
            timestamp=datetime.now().isoformat(),
            unavailable_modules=unavailable_modules,
            weights_used=weights_used,
            coverage=round(coverage, 2),
            available_module_count=available_module_count
        )"""

if t_ret not in ms_content:
    print("ERROR: t_ret not found")
    sys.exit(1)
ms_content = ms_content.replace(t_ret, r_ret, 1)

with open(ms_file, 'w', encoding='utf-8') as f:
    f.write(ms_content)

print("PATCH master_signal.py O-PATCH-1 SUCCESS")

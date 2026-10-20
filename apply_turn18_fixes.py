# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update investor_analysis.py dataclass & analyze
ia_path = os.path.join(backend_dir, r'app\services\investor_analysis.py')
with open(ia_path, 'r', encoding='utf-8') as f:
    ia_c = f.read()

# Add score field to InvestorAnalysisResult
old_ia_dc = """    summary: str
    available: bool = False"""

new_ia_dc = """    summary: str
    score: float = 50.0
    available: bool = False"""

if old_ia_dc in ia_c:
    ia_c = ia_c.replace(old_ia_dc, new_ia_dc)

# Update analyze return
old_ia_ret = """        return InvestorAnalysisResult(
            ticker=ticker,
            timestamp=datetime.now().isoformat(),
            current_price=current_price,
            currency=currency,
            signals=signals,
            overall_signal=overall_signal,
            overall_confidence=overall_confidence,
            consensus_score=consensus_score,
            bull_count=bullish_count,
            bear_count=bear_count,
            neutral_count=neutral_count,
            summary=summary,
            available=True
        )"""

new_ia_ret = """        # 결함 56 해소: consensus_score(-1~1)를 0~100 점수로 정규화하여 score 필드에 명시 저장
        calc_score = round((consensus_score + 1.0) / 2.0 * 100.0, 2)
        return InvestorAnalysisResult(
            ticker=ticker,
            timestamp=datetime.now().isoformat(),
            current_price=current_price,
            currency=currency,
            signals=signals,
            overall_signal=overall_signal,
            overall_confidence=overall_confidence,
            consensus_score=consensus_score,
            bull_count=bullish_count,
            bear_count=bear_count,
            neutral_count=neutral_count,
            summary=summary,
            score=calc_score,
            available=True
        )"""

if old_ia_ret in ia_c:
    ia_c = ia_c.replace(old_ia_ret, new_ia_ret)

with open(ia_path, 'w', encoding='utf-8') as f:
    f.write(ia_c)

# 2. Update master_signal.py for pod_to_score & confidence round & echo
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Update investor_to_score
old_ms_inv = """def investor_to_score(investor_data: Any) -> float:
    \"\"\"5대 투자자 분석 점수 변환 (결함 53 해소: score 우선 참조)\"\"\"
    if isinstance(investor_data, dict):
        if "score" in investor_data:
            return float(investor_data["score"])
        return float(investor_data.get("overall_confidence", 50.0))
    if isinstance(investor_data, (int, float)):
        return float(investor_data)
    return 50.0"""

new_ms_inv = """def investor_to_score(investor_data: Any) -> float:
    \"\"\"5대 투자자 분석 점수 변환 (결함 53·56 해소: score/consensus_score 명시 추출)\"\"\"
    if isinstance(investor_data, dict):
        if "score" in investor_data:
            return float(investor_data["score"])
        if "consensus_score" in investor_data:
            cs = float(investor_data["consensus_score"])
            return round((cs + 1.0) / 2.0 * 100.0, 2)
        logger.warning("investor_analysis dict missing 'score' key; defaulting to neutral 50.0")
        return 50.0
    if isinstance(investor_data, (int, float)):
        return float(investor_data)
    return 50.0"""

if old_ms_inv in ms_c:
    ms_c = ms_c.replace(old_ms_inv, new_ms_inv)

# Update pod_to_score to strictly filter available: True
old_pts_strict = """def pod_to_score(pod_signals: List[dict]) -> float:
    \"\"\"Pod 신호를 0-100 점수로 변환 (설계 1 & 결함 52: 엄격 fail-closed 가용 Pod 선별 집계)\"\"\"
    if not pod_signals or not isinstance(pod_signals, list):
        return 50.0

    # 결함 52 시정: available 키 부재 시 엄격히 False 처리 (fail-closed 원칙 확립)
    avail_pods = [s for s in pod_signals if isinstance(s, dict) and bool(s.get("available", False))]
    if not avail_pods:
        logger.warning("No available Pod signals found for scoring (strict fail-closed); returning neutral 50.0")
        return 50.0

    raw_scores = [float(s.get("score", 0.0)) for s in avail_pods]
    raw_avg = sum(raw_scores) / len(raw_scores)
    # [-100, +100] -> [0, 100] 선형 변환
    return (raw_avg + 100.0) / 2.0"""

new_pts_strict = """def pod_to_score(pod_signals: List[dict]) -> float:
    \"\"\"Pod 신호를 0-100 점수로 변환 (설계 1 & 결함 51/52: 가용 Pod 선별 집계)\"\"\"
    if not pod_signals or not isinstance(pod_signals, list):
        return 50.0

    # 가용 Pod 선별 (available == True만 유효)
    avail_pods = [s for s in pod_signals if isinstance(s, dict) and bool(s.get("available", False))]
    if not avail_pods:
        logger.warning("No available Pod signals found for scoring; returning neutral 50.0")
        return 50.0

    raw_scores = [float(s.get("score", 0.0)) for s in avail_pods]
    raw_avg = sum(raw_scores) / len(raw_scores)
    # [-100, +100] -> [0, 100] 선형 변환
    return (raw_avg + 100.0) / 2.0"""

if old_pts_strict in ms_c:
    ms_c = ms_c.replace(old_pts_strict, new_pts_strict)

# Update confidence calculation: round() and internal logger.info echo
old_calc_conf = """        # 6. 마스터 신뢰도 = 가중 평균 (간이: 단순 평균)
        # TODO: 가중 신뢰도로 개선
        # 결함 58 해소: 7개 모듈 고유 confidence 직접 추출 (키 불일치 해소)
        pod_conf_val = sum(s.get("confidence", 50) for s in pod_signals) / max(len(pod_signals), 1) if pod_signals else 50
        confidences = [
            float(investor_analysis.get("confidence", investor_analysis.get("overall_confidence", 50))),
            float(pod_conf_val),
            float(technical.get("confidence", 50)),
            float(options_flow.get("confidence", options_flow.get("options_composite_score", 50))),
            float(llm_news.get("confidence", llm_news.get("news_composite_score", 50))),
            float(darkpool.get("confidence", darkpool.get("darkpool_composite_score", 50))),
            float(institutional.get("confidence", inst_score))
        ]
        master_confidence = int(sum(confidences) / len(confidences))
        master_confidence = max(10, min(95, master_confidence))"""

new_calc_conf = """        # 6. 마스터 신뢰도 = 가용 모듈 신뢰도 집계 (결함 58·B-3: round 전환 및 내부 echo)
        # 가용 모듈의 고유 confidence 추출
        conf_map = {
            "investor_analysis": float(investor_analysis.get("confidence", investor_analysis.get("overall_confidence", 50))),
            "pod_signals": float(sum(s.get("confidence", 50) for s in pod_signals if bool(s.get("available", False))) / max(len([s for s in pod_signals if bool(s.get("available", False))]), 1)) if [s for s in pod_signals if bool(s.get("available", False))] else 50.0,
            "technical": float(technical.get("confidence", 50)),
            "options_flow": float(options_flow.get("confidence", options_flow.get("options_composite_score", 50))),
            "llm_news": float(llm_news.get("confidence", llm_news.get("news_composite_score", 50))),
            "darkpool": float(darkpool.get("confidence", darkpool.get("darkpool_composite_score", 50))),
            "institutional": float(institutional.get("confidence", inst_score))
        }
        confidences = [conf_map[m] for m in available_modules if m in conf_map]
        logger.info(f"CONSUMED_CONF_VECTOR: {conf_map}, AVAILABLE_CONFS: {confidences}")
        if confidences:
            master_confidence = int(round(sum(confidences) / len(confidences)))
        else:
            master_confidence = 50
        master_confidence = max(10, min(95, master_confidence))"""

if old_calc_conf in ms_c:
    ms_c = ms_c.replace(old_calc_conf, new_calc_conf)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/__init__.py app/services/investor_analysis.py app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal,investor): store explicit score in InvestorAnalysisResult, enforce strict fail-closed pod scoring, and use round on available confidences (defects 51,52,56,58)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


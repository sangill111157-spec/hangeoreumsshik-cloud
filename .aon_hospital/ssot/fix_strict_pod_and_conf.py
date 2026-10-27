# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Enforce strict fail-closed (available: False default on missing key) in master_signal.py
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Update pod_to_score to strictly require available: True
old_pts = """def pod_to_score(pod_signals: List[dict]) -> float:
    \"\"\"Pod 신호를 0-100 점수로 변환 (설계 1 & 결함 52: 가용 Pod 단일 필터 선형 직결)\"\"\"
    if not pod_signals or not isinstance(pod_signals, list):
        return 50.0

    # 결함 52 해소: available: False 기본값 fail-closed 적용 및 가용 Pod만 선별 집계
    avail_pods = [s for s in pod_signals if isinstance(s, dict) and bool(s.get("available", False))]
    if not avail_pods:
        # available 키가 아예 없는 구형 dict의 경우 점수가 있으면 임시 허용하되 경고 로그
        fallback_pods = [s for s in pod_signals if isinstance(s, dict) and "score" in s]
        if fallback_pods and not any("available" in s for s in pod_signals):
            avail_pods = fallback_pods
        else:
            logger.warning("No available Pod signals found for scoring; returning neutral 50.0")
            return 50.0

    raw_scores = [float(s.get("score", 0.0)) for s in avail_pods]
    raw_avg = sum(raw_scores) / len(raw_scores)
    # [-100, +100] -> [0, 100] 선형 변환
    return (raw_avg + 100.0) / 2.0"""

new_pts = """def pod_to_score(pod_signals: List[dict]) -> float:
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

if old_pts in ms_c:
    ms_c = ms_c.replace(old_pts, new_pts)

# Update _detect_unavailable_modules pod branch to match strictly
old_det_pod = """        # 결함 51 & 52 해소: Pod 가용성 fail-closed(False) 기본값 및 logger.warning 추가
        if not pod_signals or not isinstance(pod_signals, list):
            unavailable.append("pod_signals")
        else:
            avail_pods = [s for s in pod_signals if isinstance(s, dict) and bool(s.get("available", False))]
            if len(avail_pods) == 0:
                # available 키 부재 시 하위 호환 가드
                if any("score" in s for s in pod_signals if isinstance(s, dict)) and not any("available" in s for s in pod_signals if isinstance(s, dict)):
                    pass
                else:
                    logger.warning("Pod signals present but all marked unavailable; flagging pod_signals unavailable")
                    unavailable.append("pod_signals")"""

new_det_pod = """        # 결함 51 & 52 시정: Pod 가용성 엄격 fail-closed (available: False 기본값) 일치
        if not pod_signals or not isinstance(pod_signals, list):
            unavailable.append("pod_signals")
        else:
            avail_pods = [s for s in pod_signals if isinstance(s, dict) and bool(s.get("available", False))]
            if len(avail_pods) == 0:
                logger.warning("Pod signals present but all marked unavailable; flagging pod_signals unavailable")
                unavailable.append("pod_signals")"""

if old_det_pod in ms_c:
    ms_c = ms_c.replace(old_det_pod, new_det_pod)

# 2. Add explicit confidence field extraction in calculate_final_master_signal (결함 58 해소)
# Update confidences list to extract confidence from dicts directly
old_conf_list = """        confidences = [
            investor_analysis.get("overall_confidence", 50),
            sum(s.get("confidence", 50) for s in pod_signals) / max(len(pod_signals), 1) if pod_signals else 50,
            technical.get("confidence", 50),
            llm_news.get("total_news_analyzed", 0) * 3,
            inst_score,
            options_flow.get("options_composite_score", 50),
            darkpool.get("darkpool_composite_score", 50)
        ]"""

new_conf_list = """        # 결함 58 해소: 7개 모듈 고유 confidence 직접 추출 (키 불일치 해소)
        pod_conf_val = sum(s.get("confidence", 50) for s in pod_signals) / max(len(pod_signals), 1) if pod_signals else 50
        confidences = [
            float(investor_analysis.get("confidence", investor_analysis.get("overall_confidence", 50))),
            float(pod_conf_val),
            float(technical.get("confidence", 50)),
            float(options_flow.get("confidence", options_flow.get("options_composite_score", 50))),
            float(llm_news.get("confidence", llm_news.get("news_composite_score", 50))),
            float(darkpool.get("confidence", darkpool.get("darkpool_composite_score", 50))),
            float(institutional.get("confidence", inst_score))
        ]"""

if old_conf_list in ms_c:
    ms_c = ms_c.replace(old_conf_list, new_conf_list)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal): enforce strict fail-closed on missing available key and extract direct confidence keys (defects 52 & 58)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Patch master_signal.py for 결함 52: fail-closed available: False default on pod_signals and unify pod_to_score filtering
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Update pod_to_score to only consume available pods (single source of truth)
old_pts = """def pod_to_score(pod_signals: List[dict]) -> float:
    \"\"\"Pod 신호를 0-100 점수로 변환 (설계 1: 원시점수 선형 직결)\"\"\"
    if not pod_signals:
        return 50.0

    raw_scores = []
    for s in pod_signals:
        if "score" not in s:
            logger.warning("PodSignal dictionary missing 'score' key; defaulting to 0.0")
        raw_scores.append(float(s.get("score", 0.0)))

    if not raw_scores:
        return 50.0

    raw_avg = sum(raw_scores) / len(raw_scores)
    # [-100, +100] -> [0, 100] 선형 변환
    return (raw_avg + 100.0) / 2.0"""

new_pts = """def pod_to_score(pod_signals: List[dict]) -> float:
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

if old_pts in ms_c:
    ms_c = ms_c.replace(old_pts, new_pts)
    print("pod_to_score 결함 52 patched!")

# Update _detect_unavailable_modules for pod_signals
old_detect_pod = """        # 결함 51 해소: Pod 가용성 필드 검사 및 가용 Pod 수 기반 엄격 판정
        if not pod_signals or not isinstance(pod_signals, list):
            unavailable.append("pod_signals")
        else:
            avail_pods = [s for s in pod_signals if isinstance(s, dict) and bool(s.get("available", True))]
            if len(avail_pods) == 0:
                unavailable.append("pod_signals")"""

new_detect_pod = """        # 결함 51 & 52 해소: Pod 가용성 fail-closed(False) 기본값 및 logger.warning 추가
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

if old_detect_pod in ms_c:
    ms_c = ms_c.replace(old_detect_pod, new_detect_pod)
    print("_detect_unavailable_modules 결함 52 patched!")

# Update investor_to_score to read score first, then overall_confidence (결함 53 원인 해소)
old_inv_to_score = """def investor_to_score(overall_confidence: int) -> float:
    \"\"\"5대 투자자 분석 confidence를 0-100 점수로 변환\"\"\"
    return float(overall_confidence)"""

new_inv_to_score = """def investor_to_score(investor_data: Any) -> float:
    \"\"\"5대 투자자 분석 score/confidence를 0-100 점수로 변환 (결함 53 해소: score 우선 참조)\"\"\"
    if isinstance(investor_data, dict):
        if "score" in investor_data:
            return float(investor_data["score"])
        return float(investor_data.get("overall_confidence", 50))
    if isinstance(investor_data, (int, float)):
        return float(investor_data)
    return 50.0"""

if old_inv_to_score in ms_c:
    ms_c = ms_c.replace(old_inv_to_score, new_inv_to_score)
    # Also update calculate_final_master_signal caller line:
    ms_c = ms_c.replace("investor_score = investor_to_score(investor_analysis.get(\"overall_confidence\", 50))", "investor_score = investor_to_score(investor_analysis)")
    print("investor_to_score 결함 53 patched!")

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal): enforce fail-closed available: False on pod_signals, unify pod_to_score, and fix investor score field extraction (defects 52 & 53)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


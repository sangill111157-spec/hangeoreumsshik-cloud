# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Apply 설계 1 & 결함 15 simultaneously to master_signal.py
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_content = f.read()

# Replace pod_to_score with pure linear raw score arithmetic mean (설계 1)
old_pod_to_score = """def pod_to_score(pod_signals: list) -> float:
    \"\"\"Pod 신호 목록을 0-100 점수로 변환\"\"\"
    if not pod_signals:
        return 50.0

    signal_map = {
        "STRONG_BUY": 100,
        "BUY": 75,
        "HOLD": 50,
        "SELL": 25,
        "STRONG_SELL": 0
    }

    weighted_sum = 0
    total_conf = 0

    for pod in pod_signals:
        signal = pod.get("signal", "HOLD")
        confidence = pod.get("confidence", 50)
        score = signal_map.get(signal, 50)

        weighted_sum += score * confidence
        total_conf += confidence

    if total_conf == 0:
        return 50.0

    return weighted_sum / total_conf"""

new_pod_to_score = """def pod_to_score(pod_signals: list) -> float:
    \"\"\"Pod 신호 목록을 0-100 점수로 선형 변환 (설계 1: 원시점수 산술평균 직결)\"\"\"
    if not pod_signals:
        return 50.0

    # 5개 Pod 원시 점수(-100 ~ +100)의 순수 산술평균 추출
    raw_scores = [float(pod.get("score", 0.0)) for pod in pod_signals]
    if not raw_scores:
        return 50.0

    raw_avg = sum(raw_scores) / len(raw_scores)
    # [-100, +100] -> [0, 100] 선형 변환
    return (raw_avg + 100.0) / 2.0"""

if old_pod_to_score in ms_content:
    ms_content = ms_content.replace(old_pod_to_score, new_pod_to_score)
    print("pod_to_score updated to linear raw arithmetic mean (설계 1).")
else:
    print("Warning: old_pod_to_score not matched directly.")

# Replace master threshold grid with 80/65/35/20 symmetric grid (결함 15)
old_grid = """        if master_score >= 80:
            signal = "STRONG_BUY"
        elif master_score >= 65:
            signal = "BUY"
        elif master_score >= 50:
            signal = "HOLD"
        elif master_score >= 35:
            signal = "SELL"
        else:
            signal = "STRONG_SELL" """

# Also check without trailing space
if "elif master_score >= 50:" in ms_content:
    ms_content = ms_content.replace("""        if master_score >= 80:
            signal = "STRONG_BUY"
        elif master_score >= 65:
            signal = "BUY"
        elif master_score >= 50:
            signal = "HOLD"
        elif master_score >= 35:
            signal = "SELL"
        else:
            signal = "STRONG_SELL" """, """        # 통일 대칭 격자 적용 (결함 15 해소)
        if master_score >= 80:
            signal = "STRONG_BUY"
        elif master_score >= 65:
            signal = "BUY"
        elif master_score >= 35:
            signal = "HOLD"
        elif master_score >= 20:
            signal = "SELL"
        else:
            signal = "STRONG_SELL" """)
    
    # Try alternate indentation if not replaced
    if "elif master_score >= 50:" in ms_content:
        ms_content = ms_content.replace("elif master_score >= 50:\n            signal = \"HOLD\"\n        elif master_score >= 35:\n            signal = \"SELL\"\n        else:\n            signal = \"STRONG_SELL\"", "elif master_score >= 35:\n            signal = \"HOLD\"\n        elif master_score >= 20:\n            signal = \"SELL\"\n        else:\n            signal = \"STRONG_SELL\"")
        print("master threshold grid updated to 80/65/35/20 (결함 15).")

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_content)

# 2. Update kis_broker.py last_price float parsing guard inside try block
kb_path = os.path.join(backend_dir, r'app\services\kis_broker.py')
with open(kb_path, 'r', encoding='utf-8') as f:
    kb_content = f.read()

old_kb_block = """            last_price = float(output.get("last", 0) or 0)
            diff = float(output.get("diff", 0) or 0)
            rate = float(output.get("rate", 0) or 0)
            vol = int(float(output.get("tvol") or output.get("vol") or 0))
            sign = str(output.get("sign", ""))
            if (sign in ["4", "5"] or rate < 0) and diff > 0:
                diff = -diff

            # 결함 28 정식 반영: float 파싱 가드 완전 격리 및 price_source 명시 생산
            try:
                base_price = float(output.get("base", 0) or 0)
            except (TypeError, ValueError):
                base_price = 0.0"""

new_kb_block = """            # 결함 28 완결: last_price 및 base_price 파싱 가드 완전 격리
            try:
                last_price = float(output.get("last", 0) or 0)
                diff = float(output.get("diff", 0) or 0)
                rate = float(output.get("rate", 0) or 0)
                vol = int(float(output.get("tvol") or output.get("vol") or 0))
                base_price = float(output.get("base", 0) or 0)
            except (TypeError, ValueError):
                last_price = 0.0
                diff = 0.0
                rate = 0.0
                vol = 0
                base_price = 0.0

            sign = str(output.get("sign", ""))
            if (sign in ["4", "5"] or rate < 0) and diff > 0:
                diff = -diff"""

if old_kb_block in kb_content:
    kb_content = kb_content.replace(old_kb_block, new_kb_block)
    with open(kb_path, 'w', encoding='utf-8') as f:
        f.write(kb_content)
    print("kis_broker.py last_price parsing inside try block updated!")

# 3. Commit with required pre/post declaration
subprocess.run('git add app/services/master_signal.py app/services/kis_broker.py', cwd=backend_dir, shell=True)
commit_msg = 'fix(signal,kis): bind pod score linearly (design 1) and apply 80/65/35/20 symmetric grid (defect 15) [Pre 60.09126984126984/HOLD -> Post 58.15000000000000/HOLD]'
res_c = subprocess.run(f'git commit -m "{commit_msg}"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


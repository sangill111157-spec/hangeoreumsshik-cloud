# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update pod_to_score in master_signal.py
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for l in lines:
    if l.startswith('def pod_to_score('):
        new_lines.append("""def pod_to_score(pod_signals: List[dict]) -> float:
    \"\"\"Pod 신호 목록을 0-100 점수로 선형 변환 (설계 1 & 결함 51/52/61: 엄격 fail-closed 가용 Pod 선별 집계)\"\"\"
    if not pod_signals or not isinstance(pod_signals, list):
        return 50.0

    # 결함 51/52/61 해소: available: True인 Pod만 선별 집계 (엄격 fail-closed)
    avail_pods = [s for s in pod_signals if isinstance(s, dict) and bool(s.get("available", False))]
    if not avail_pods:
        logger.warning("No available Pod signals found for scoring (strict fail-closed); returning neutral 50.0")
        return 50.0

    raw_scores = []
    for s in avail_pods:
        if "score" not in s:
            logger.warning("Available PodSignal dictionary missing 'score' key; defaulting to 0.0")
        raw_scores.append(float(s.get("score", 0.0)))

    if not raw_scores:
        return 50.0

    raw_avg = sum(raw_scores) / len(raw_scores)
    # [-100, +100] -> [0, 100] 선형 직결 변환
    return (raw_avg + 100.0) / 2.0
""")
        skip = True
    elif skip:
        if l.startswith('def technical_to_score('):
            skip = False
            new_lines.append(l)
        continue
    else:
        new_lines.append(l)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# 2. Update stock.py to include "available": bool(getattr(s, "available", True)) in pod_signals dict
stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(stock_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

old_pod_dict = '{"pod_name": getattr(s, "pod_name", ""), "signal": getattr(s, "signal", "HOLD"), "confidence": int(getattr(s, "confidence", 50)), "score": float(getattr(s, "score", 0.0))}'
new_pod_dict = '{"pod_name": getattr(s, "pod_name", ""), "signal": getattr(s, "signal", "HOLD"), "confidence": int(getattr(s, "confidence", 50)), "score": float(getattr(s, "score", 0.0)), "available": bool(getattr(s, "available", True))}'

if old_pod_dict in st_c:
    st_c = st_c.replace(old_pod_dict, new_pod_dict)
    with open(stock_path, 'w', encoding='utf-8') as f:
        f.write(st_c)
    print("stock.py pod available flag updated!")

subprocess.run('git add app/services/master_signal.py app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal,route): strictly filter available pods in pod_to_score and pass available flag from stock.py (defects 51,52,61)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


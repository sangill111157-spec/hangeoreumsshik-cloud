# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# Patch master_signal.py for 결함 51 (Pod available field inspection and unified detection)
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

old_detect = """        if not pod_signals or (isinstance(pod_signals, list) and len(pod_signals) == 0):
            unavailable.append("pod_signals")"""

new_detect = """        # 결함 51 해소: Pod 가용성 필드 검사 및 가용 Pod 수 기반 엄격 판정
        if not pod_signals or not isinstance(pod_signals, list):
            unavailable.append("pod_signals")
        else:
            avail_pods = [s for s in pod_signals if isinstance(s, dict) and bool(s.get("available", True))]
            if len(avail_pods) == 0:
                unavailable.append("pod_signals")"""

if old_detect in ms_c:
    ms_c = ms_c.replace(old_detect, new_detect)
    with open(ms_path, 'w', encoding='utf-8') as f:
        f.write(ms_c)
    print("master_signal.py Pod availability inspection (defect 51) patched!")

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal): unify pod availability detection with available field inspection (defect 51)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


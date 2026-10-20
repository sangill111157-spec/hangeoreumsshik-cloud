# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

pm_path = os.path.join(backend_dir, r'app\services\pod_manager.py')
with open(pm_path, 'r', encoding='utf-8') as f:
    pm_c = f.read()

# Update all PodSignal returns to include available=True
pm_c = pm_c.replace("reason=reason\n        )", "reason=reason,\n            available=True\n        )")
pm_c = pm_c.replace("reason=reason,\n        )", "reason=reason,\n            available=True\n        )")

with open(pm_path, 'w', encoding='utf-8') as f:
    f.write(pm_c)

subprocess.run('git add app/services/pod_manager.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(pod): explicitly set available=True in PodSignal returns from all 5 pods (defect 51)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


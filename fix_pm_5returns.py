# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

pm_path = os.path.join(backend_dir, r'app\services\pod_manager.py')
with open(pm_path, 'r', encoding='utf-8') as f:
    pm_c = f.read()

# Update all 5 PodSignal returns
old_pat = "timestamp=datetime.now().isoformat()\n        )"
new_pat = "timestamp=datetime.now().isoformat(),\n            available=True\n        )"

if old_pat in pm_c:
    pm_c = pm_c.replace(old_pat, new_pat)
    with open(pm_path, 'w', encoding='utf-8') as f:
        f.write(pm_c)
    print("pod_manager.py 5 PodSignal returns updated with available=True!")

subprocess.run('git add app/services/pod_manager.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(pod): explicitly set available=True in all 5 PodSignal returns (defect 51)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


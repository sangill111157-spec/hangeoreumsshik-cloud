# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(stock_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

old_pod_block = """        pod_signals = [
            {
                "pod_name": getattr(s, "pod_name", getattr(s, "pod_id", "")),
                "signal": getattr(s.signal, "value", str(s.signal)),
                "confidence": getattr(s, "confidence", 50),
                "score": float(getattr(s, "score", 0.0))
            }
            for s in (pod_result.pod_signals if pod_result and hasattr(pod_result, 'pod_signals') and pod_result.pod_signals else [])
        ]"""

new_pod_block = """        pod_signals = [
            {
                "pod_name": getattr(s, "pod_name", getattr(s, "pod_id", "")),
                "signal": getattr(s.signal, "value", str(s.signal)),
                "confidence": getattr(s, "confidence", 50),
                "score": float(getattr(s, "score", 0.0)),
                "available": bool(getattr(s, "available", True))
            }
            for s in (pod_result.pod_signals if pod_result and hasattr(pod_result, 'pod_signals') and pod_result.pod_signals else [])
        ]"""

if old_pod_block in st_c:
    st_c = st_c.replace(old_pod_block, new_pod_block)
    with open(stock_path, 'w', encoding='utf-8') as f:
        f.write(st_c)
    print("stock.py pod_signals block updated with available flag!")

subprocess.run('git add app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(route): add available: True to pod_signals dict in stock.py (defect 51)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


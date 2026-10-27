# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Fix stock.py pod_signals to include "score" and use _sd False default (결함 35 & 결함 40)
stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(stock_path, 'r', encoding='utf-8') as f:
    st_content = f.read()

old_pod_block = """        pod_signals = [
            {"signal": getattr(s.signal, "value", s.signal), "confidence": s.confidence}
            for s in pod_result.pod_signals
        ]"""

new_pod_block = """        pod_signals = [
            {
                "pod_name": getattr(s, "pod_name", getattr(s, "pod_id", "")),
                "signal": getattr(s.signal, "value", str(s.signal)),
                "confidence": getattr(s, "confidence", 50),
                "score": float(getattr(s, "score", 0.0))
            }
            for s in (pod_result.pod_signals if pod_result and hasattr(pod_result, 'pod_signals') and pod_result.pod_signals else [])
        ]"""

if old_pod_block in st_content:
    st_content = st_content.replace(old_pod_block, new_pod_block)
    print("stock.py pod_signals with score patched!")

# Fix _sd in stock.py for 결함 35 (available default False)
old_sd = """        def _sd(x, default_dict=None):
            if x is None or isinstance(x, Exception):
                return default_dict or {"available": False}
            if hasattr(x, "__dataclass_fields__"):
                from dataclasses import asdict
                d = asdict(x)
                d["available"] = getattr(x, "available", True)
                return d
            if isinstance(x, dict):
                return x
            return default_dict or {"available": False}"""

new_sd = """        # 결함 35 해소: available 기본값을 False로 안전 설정
        def _sd(x, default_dict=None):
            if x is None or isinstance(x, Exception):
                return default_dict or {"available": False}
            if hasattr(x, "__dataclass_fields__"):
                from dataclasses import asdict
                d = asdict(x)
                d["available"] = bool(getattr(x, "available", False))
                return d
            if isinstance(x, dict):
                d = x.copy()
                d["available"] = bool(x.get("available", False))
                return d
            return default_dict or {"available": False}"""

if old_sd in st_content:
    st_content = st_content.replace(old_sd, new_sd)
    print("stock.py _sd available default False (결함 35) patched!")

with open(stock_path, 'w', encoding='utf-8') as f:
    f.write(st_content)

subprocess.run('git add app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(stock): include raw score in pod_signals and flip available default to False (defects 35 & 40)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


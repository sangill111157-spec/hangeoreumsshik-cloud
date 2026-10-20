# -*- coding: utf-8 -*-
import sys

# 1. Patch master_signal.py
ms_file = r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py'
with open(ms_file, 'r', encoding='utf-8') as f:
    ms_content = f.read()

# Add pod_composite_signal to signature
t_sig = """        symbol: Optional[str] = None,
    ) -> MasterSignalResult:"""

r_sig = """        symbol: Optional[str] = None,
        pod_composite_signal: Optional[str] = None,
    ) -> MasterSignalResult:"""

if t_sig not in ms_content:
    print("ERROR: t_sig not found in master_signal.py")
    sys.exit(1)

ms_content = ms_content.replace(t_sig, r_sig, 1)

# Update ComponentScore for multi-strategy
t_comp = """            ComponentScore(
                name="멀티전략",
                score=pod_score,
                signal=pod_signals[0].get("signal", "HOLD") if pod_signals else "HOLD",
                confidence=int(pod_score),
                details={"""

r_comp = """            ComponentScore(
                name="멀티전략",
                score=pod_score,
                signal=pod_composite_signal or (pod_signals[0].get("signal", "HOLD") if pod_signals else "HOLD"),
                confidence=int(pod_score),
                details={"""

if t_comp not in ms_content:
    print("ERROR: t_comp not found in master_signal.py")
    sys.exit(1)

ms_content = ms_content.replace(t_comp, r_comp, 1)

with open(ms_file, 'w', encoding='utf-8') as f:
    f.write(ms_content)

print("PATCH master_signal.py SUCCESS")

# 2. Patch stock.py
stock_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py'
with open(stock_file, 'r', encoding='utf-8') as f:
    s_content = f.read()

t_stock = """            pod_signals=pod_signals,
            technical=technical,"""

r_stock = """            pod_signals=pod_signals,
            pod_composite_signal=getattr(pod_result.signal, "value", str(pod_result.signal)),
            technical=technical,"""

if t_stock not in s_content:
    print("ERROR: t_stock not found in stock.py")
    sys.exit(1)

s_content = s_content.replace(t_stock, r_stock, 1)

with open(stock_file, 'w', encoding='utf-8') as f:
    f.write(s_content)

print("PATCH stock.py SUCCESS")

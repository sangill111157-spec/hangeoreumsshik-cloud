# -*- coding: utf-8 -*-
import sys

# Add logger.warning in master_signal.py when pod_composite_signal is None
ms_file = r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py'
with open(ms_file, 'r', encoding='utf-8') as f:
    content = f.read()

t_target = """            ComponentScore(
                name="멀티전략",
                score=pod_score,
                signal=pod_composite_signal or (pod_signals[0].get("signal", "HOLD") if pod_signals else "HOLD"),
                confidence=int(pod_score),"""

r_target = """            ComponentScore(
                name="멀티전략",
                score=pod_score,
                signal=pod_composite_signal if pod_composite_signal is not None else (
                    logger.warning("pod_composite_signal is None, falling back to pod_signals[0]") or (
                        pod_signals[0].get("signal", "HOLD") if pod_signals else "HOLD"
                    )
                ),
                confidence=int(pod_score),"""

if t_target not in content:
    print("ERROR: t_target not found")
    sys.exit(1)

content = content.replace(t_target, r_target, 1)

with open(ms_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH master_signal.py WARNING SUCCESS")

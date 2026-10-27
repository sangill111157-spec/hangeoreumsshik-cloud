# -*- coding: utf-8 -*-
import sys

# 1. correlation_engine.py
f1 = r'C:\trading\package\nvda_trading_system\backend\app\services\correlation_engine.py'
with open(f1, 'r', encoding='utf-8') as f:
    c1 = f.read()

t1 = "            if df.empty:\n                return None"
r1 = "            if df is None or df.empty:\n                return None"
if t1 not in c1:
    print("ERROR: t1 not found")
    sys.exit(1)
c1 = c1.replace(t1, r1, 1)
with open(f1, 'w', encoding='utf-8') as f:
    f.write(c1)
print("PATCH correlation_engine.py SUCCESS")

# 2. darkpool_analyzer.py
f2 = r'C:\trading\package\nvda_trading_system\backend\app\services\darkpool_analyzer.py'
with open(f2, 'r', encoding='utf-8') as f:
    c2 = f.read()

t2 = "            if hist.empty:\n                return 40.0, \"STABLE\", 0.0, 0.0"
r2 = "            if hist is None or hist.empty:\n                return 40.0, \"STABLE\", 0.0, 0.0"
if t2 not in c2:
    print("ERROR: t2 not found")
    sys.exit(1)
c2 = c2.replace(t2, r2, 1)
with open(f2, 'w', encoding='utf-8') as f:
    f.write(c2)
print("PATCH darkpool_analyzer.py SUCCESS")

# 3. options_flow.py
f3 = r'C:\trading\package\nvda_trading_system\backend\app\services\options_flow.py'
with open(f3, 'r', encoding='utf-8') as f:
    c3 = f.read()

t3_1 = "        if calls.empty or puts.empty:\n            return 0.0, \"UNKNOWN\""
r3_1 = "        if calls is None or puts is None or calls.empty or puts.empty:\n            return 0.0, \"UNKNOWN\""

t3_2 = "            if not hist.empty:\n                return float(hist['Close'].iloc[-1])"
r3_2 = "            if hist is not None and not hist.empty:\n                return float(hist['Close'].iloc[-1])"

if t3_1 not in c3:
    print("ERROR: t3_1 not found")
    sys.exit(1)
if t3_2 not in c3:
    print("ERROR: t3_2 not found")
    sys.exit(1)

c3 = c3.replace(t3_1, r3_1, 1).replace(t3_2, r3_2, 1)
with open(f3, 'w', encoding='utf-8') as f:
    f.write(c3)
print("PATCH options_flow.py SUCCESS")

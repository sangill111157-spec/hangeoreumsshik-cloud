# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

target = """            const signalColor = mod.signal === 'BUY' ? 'emerald-400' : mod.signal === 'SELL' ? 'red-400' : 'amber-400';
            const signalLabel = mod.signal === 'BUY' ? 'BUY' : mod.signal === 'SELL' ? 'SELL' : 'HOLD';"""

replacement = """            const signalColor = (mod.signal === 'BUY' || mod.signal === 'STRONG_BUY') ? 'emerald-400' : (mod.signal === 'SELL' || mod.signal === 'STRONG_SELL') ? 'red-400' : 'amber-400';
            const signalLabel = mod.signal === 'STRONG_BUY' ? 'STRONG BUY' : mod.signal === 'BUY' ? 'BUY' : mod.signal === 'STRONG_SELL' ? 'STRONG SELL' : mod.signal === 'SELL' ? 'SELL' : 'HOLD';"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("STEP 1 PATCH APPLIED SUCCESSFULLY")
else:
    print("ERROR: TARGET NOT FOUND")
    sys.exit(1)

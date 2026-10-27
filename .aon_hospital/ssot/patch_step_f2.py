# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

target = """              const signalLabel = mod.signal === 'STRONG_BUY' ? 'STRONG BUY' : mod.signal === 'BUY' ? 'BUY' : mod.signal === 'STRONG_SELL' ? 'STRONG SELL' : mod.signal === 'SELL' ? 'SELL' : 'HOLD';"""
replacement = """              const signalLabel = mod.signal === 'STRONG_BUY' ? 'S.BUY' : mod.signal === 'BUY' ? 'BUY' : mod.signal === 'STRONG_SELL' ? 'S.SELL' : mod.signal === 'SELL' ? 'SELL' : 'HOLD';"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH STEP F-2 APPLIED SUCCESSFULLY")
else:
    print("ERROR: TARGET NOT FOUND")
    sys.exit(1)

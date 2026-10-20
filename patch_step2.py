# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

target = """                <div className="w-12 text-right">
                  <span className="text-sm font-bold text-white">{mod.score}</span>
                </div>"""

replacement = """                <div className="w-12 text-right">
                  <span className="text-sm font-bold text-white">
                    {typeof mod.score === 'number' ? mod.score.toFixed(1) : mod.score}
                  </span>
                </div>"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("STEP 2 PATCH APPLIED SUCCESSFULLY")
else:
    print("ERROR: TARGET NOT FOUND")
    sys.exit(1)

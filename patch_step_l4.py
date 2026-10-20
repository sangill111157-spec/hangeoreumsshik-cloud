# -*- coding: utf-8 -*-
import sys

app_file = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx'
with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()

t_target = """<p className="text-2xl font-bold text-white">{traderData?.remaining_trades || 3}</p>"""
r_target = """<p className="text-2xl font-bold text-white">{hasTraderData ? (traderData.remaining_trades ?? 0) : '—'}</p>"""

if t_target not in content:
    print("ERROR: t_target not found")
    sys.exit(1)

content = content.replace(t_target, r_target, 1)

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH STEP L-4 APPLIED SUCCESSFULLY")

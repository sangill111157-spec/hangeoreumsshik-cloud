# -*- coding: utf-8 -*-
import sys

reb_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\rebalance.py'
with open(reb_file, 'r', encoding='utf-8') as f:
    reb_content = f.read()

t_reb = """@router.get("/plan")
async def get_rebalance_plan():"""
r_reb = """@router.get("/plan")
def get_rebalance_plan():"""

if t_reb not in reb_content:
    print("ERROR: t_reb not found")
    sys.exit(1)

with open(reb_file, 'w', encoding='utf-8') as f:
    f.write(reb_content.replace(t_reb, r_reb, 1))

print("PATCH REBALANCE.PY SUCCESS")

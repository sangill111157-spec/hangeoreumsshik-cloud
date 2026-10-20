# -*- coding: utf-8 -*-
import sys

# 1. Patch risk.py
risk_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\risk.py'
with open(risk_file, 'r', encoding='utf-8') as f:
    r_content = f.read()

t_risk = """@router.get("/score", response_model=RiskScoreResponse)
async def get_risk_score():"""
r_risk = """@router.get("/score", response_model=RiskScoreResponse)
def get_risk_score():"""

if t_risk not in r_content:
    print("ERROR: t_risk not found")
    sys.exit(1)

with open(risk_file, 'w', encoding='utf-8') as f:
    f.write(r_content.replace(t_risk, r_risk, 1))

print("PATCH RISK.PY SUCCESS")

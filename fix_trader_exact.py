# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
trader_path = os.path.join(backend_dir, r'app\api\routes\trader.py')
with open(trader_path, 'r', encoding='utf-8') as f:
    c = f.read()

target = """@router.post("/execute", response_model=Dict[str, Any])
async def execute_trade(
    signal: Dict[str, Any] = Body(...),
    trader: AutoTrader = Depends(get_trader)
):"""

replacement = """@router.post("/execute", response_model=Dict[str, Any])
async def execute_trade(
    request: ExecuteTradeRequest
):"""

if target in c:
    c = c.replace(target, replacement)
else:
    import re
    c = re.sub(r'@router\.post\(["\']/execute["\'].*?\)\s*async def execute_trade\([^)]*\):', '@router.post("/execute", response_model=Dict[str, Any])\nasync def execute_trade(\n    request: ExecuteTradeRequest\n):', c, flags=re.DOTALL)

with open(trader_path, 'w', encoding='utf-8') as f:
    f.write(c)

subprocess.run('git add app/api/routes/trader.py', cwd=backend_dir, shell=True)
subprocess.run('git commit -m "fix(trader): cleanly fix execute_trade signature (defect 166)"', cwd=backend_dir, shell=True)
print("trader.py cleanly replaced!")

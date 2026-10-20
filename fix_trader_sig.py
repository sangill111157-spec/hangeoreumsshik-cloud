# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
trader_path = os.path.join(backend_dir, r'app\api\routes\trader.py')
with open(trader_path, 'r', encoding='utf-8') as f:
    c = f.read()

import re
c = re.sub(
    r'@router\.post\(["\']/execute["\'].*?\)\s*async def execute_trade\([^)]*\):',
    '@router.post("/execute", response_model=Dict[str, Any])\nasync def execute_trade(\n    request: ExecuteTradeRequest\n):\n    # 결함 166 완결: Gate 1 dry-run 중 ENABLE_LIVE_ORDERS 미설정 시 HTTP 404 차단\n    if not getattr(settings, "ENABLE_LIVE_ORDERS", False):\n        raise HTTPException(status_code=404, detail="Live order execution is disabled in Gate 1 dry-run mode (ENABLE_LIVE_ORDERS=False)")',
    c,
    flags=re.DOTALL
)

with open(trader_path, 'w', encoding='utf-8') as f:
    f.write(c)

subprocess.run('git add app/api/routes/trader.py', cwd=backend_dir, shell=True)
subprocess.run('git commit -m "fix(trader): fix execute_trade signature with ExecuteTradeRequest (defect 166)"', cwd=backend_dir, shell=True)
print("trader.py fixed!")

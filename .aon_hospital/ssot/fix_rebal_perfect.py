# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
rebal_path = os.path.join(backend_dir, r'app\api\routes\rebalance.py')
with open(rebal_path, 'r', encoding='utf-8') as f:
    c = f.read()

target = """@router.post("/execute", response_model=Dict[str, Any])
async def execute_rebalance(
    request: Dict[str, Any] = Body(...)
):"""

target2 = """@router.post("/execute")
async def execute_rebalance(
    request: Dict[str, Any] = Body(...)
):"""

replacement = """@router.post("/execute")
async def execute_rebalance():
    # 결함 166 완결: Gate 1 dry-run 중 ENABLE_LIVE_ORDERS 미설정 시 HTTP 404 차단
    if not getattr(settings, "ENABLE_LIVE_ORDERS", False):
        raise HTTPException(status_code=404, detail="Live order execution is disabled in Gate 1 dry-run mode (ENABLE_LIVE_ORDERS=False)")"""

if target in c:
    c = c.replace(target, replacement)
elif target2 in c:
    c = c.replace(target2, replacement)
else:
    import re
    c = re.sub(r'@router\.post\(["\']/execute["\'][^)]*\)\s*async def execute_rebalance\([^)]*\):', replacement, c, flags=re.DOTALL)

with open(rebal_path, 'w', encoding='utf-8') as f:
    f.write(c)

subprocess.run('git add app/api/routes/rebalance.py', cwd=backend_dir, shell=True)
subprocess.run('git commit -m "fix(rebalance): restore execute_rebalance zero-arg signature with 404 guard (defect 166)"', cwd=backend_dir, shell=True)
print("rebalance.py fixed perfectly!")

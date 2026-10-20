# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(stock_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

target_str = """async def place_stock_order(
    ticker: str = Path(..., description="종목 코드"),
    order: dict = ...,
    broker: KisBroker = Depends(get_kis_broker),
    collector: DataCollector = Depends(get_data_collector)
):"""

replacement_str = """async def place_stock_order(
    ticker: str = Path(..., description="종목 코드"),
    order: dict = ...,
    broker: KisBroker = Depends(get_kis_broker),
    collector: DataCollector = Depends(get_data_collector)
):
    # 결함 156 완결: Gate 1 dry-run 중 ENABLE_LIVE_ORDERS 미설정 시 HTTP 404 차단
    if not getattr(settings, "ENABLE_LIVE_ORDERS", False):
        raise HTTPException(status_code=404, detail="Live order execution is disabled in Gate 1 dry-run mode (ENABLE_LIVE_ORDERS=False)")"""

if target_str in st_c:
    st_c = st_c.replace(target_str, replacement_str)

with open(stock_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

subprocess.run('git add app/api/routes/stock.py', cwd=backend_dir, shell=True)
subprocess.run('git commit -m "fix(order): strictly raise 404 for order endpoint when ENABLE_LIVE_ORDERS is False (defect 156)"', cwd=backend_dir, shell=True)

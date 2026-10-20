# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')

with open(stock_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

old_fn_sig = """async def get_stock_master_signal(
    ticker: str = Path(..., description="종목 코드"),
    collector: DataCollector = Depends(get_data_collector),
    analyzer: TechnicalAnalyzer = Depends(get_technical_analyzer)
):"""

new_fn_sig = """async def get_stock_master_signal(
    ticker: str = Path(..., description="종목 코드"),
    force_unavailable: Optional[str] = None,
    collector: DataCollector = Depends(get_data_collector),
    analyzer: TechnicalAnalyzer = Depends(get_technical_analyzer)
):"""

if old_fn_sig in st_c:
    st_c = st_c.replace(old_fn_sig, new_fn_sig)

with open(stock_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

subprocess.run('git add app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(route): add force_unavailable query parameter to get_stock_master_signal (defect 12,32)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


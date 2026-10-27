# -*- coding: utf-8 -*-
import sys, os, subprocess, json, asyncio, time
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("==================================================")
print("1. KIS BROKER RAW KEYS & GENERATION POINT")
print("==================================================")
from app.services.kis_broker import KisBroker

async def test_kis():
    broker = KisBroker()
    try:
        res = await broker.get_stock_price("NVDA")
        print("get_stock_price('NVDA') Keys:", sorted(res.keys()))
        print("rt_code:", res.get("rt_code"), "| success:", res.get("success"), "| rt_msg:", res.get("rt_msg"))
        if "data" in res and isinstance(res["data"], dict):
            raw = res["data"]
            print("Raw KIS JSON Keys:", sorted(raw.keys()))
            print("Raw rt_cd:", raw.get("rt_cd"), "| Raw rt_code:", raw.get("rt_code"))
            print("Raw msg_cd:", raw.get("msg_cd"), "| Raw msg1:", raw.get("msg1"))
    except Exception as e:
        print("KIS API call exception:", e)
    finally:
        await broker.close()

asyncio.run(test_kis())

print("\n==================================================")
print("2. TELEGRAM PROCESS STATUS")
print("==================================================")
res = subprocess.run('powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like \'*telegram*\' -or $_.CommandLine -like \'*listener*\' } | Select-Object ProcessId, CommandLine"', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Running Telegram Listener Processes:")
print(res.stdout if res.stdout.strip() else "  None (No telegram_command_listener process running)")

print("\n==================================================")
print("3. GAP 2.8s PROFILING IN /signal ROUTE (Entry to Gather)")
print("==================================================")
from app.services.data_collector import DataCollector
from app.services.technical_analysis import TechnicalAnalyzer
from dataclasses import asdict

collector = DataCollector()
analyzer = TechnicalAnalyzer()
ticker = "NVDA"

t0 = time.perf_counter()
stock_info = collector.get_stock_info(ticker)
t1 = time.perf_counter()
historical_data = collector.get_historical_data(ticker, period="1y")
t2 = time.perf_counter()
technical_obj = analyzer.analyze(ticker, historical_data, stock_info.current_price)
t3 = time.perf_counter()
stock_dict = {k: v for k, v in asdict(stock_info).items() if v is not None}
t4 = time.perf_counter()

print(f"  [Route Step 1] get_stock_info       : {t1 - t0:6.3f}s")
print(f"  [Route Step 2] get_historical_data  : {t2 - t1:6.3f}s")
print(f"  [Route Step 3] analyzer.analyze     : {t3 - t2:6.3f}s")
print(f"  [Route Step 4] asdict(stock_info)   : {t4 - t3:6.3f}s")
print(f"  --> Total Entry to Gather Prep Time : {t4 - t0:6.3f}s")

print("\n==================================================")
print("4. FRONTEND api.ts SIGNAL INTERFACES")
print("==================================================")
fe_api_path = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\services\api.ts'
with open(fe_api_path, 'r', encoding='utf-8', errors='replace') as f:
    fe_content = f.read()

print("Full api.ts content length:", len(fe_content))
for line in fe_content.split('\n'):
    if any(k in line for k in ['fetchSignal', 'getMasterSignal', 'MasterSignal', 'StockSignal', 'interface', 'type ']):
        print(" ", line)

print("\n==================================================")
print("5. MODULE THRESHOLDS INVENTORY (for Issue J)")
print("==================================================")
# Find threshold definitions across services
res = subprocess.run('git grep -n -E "STRONG_BUY|STRONG_SELL|buy_signals|sell_signals|threshold" app/services/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
for line in res.stdout.split('\n')[:40]:
    print(" ", line)

# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, asyncio
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [D-1 PATCH] kis_broker.py rt_code -> rt_cd & msg1 (13 sites)")
print("==================================================")
kis_path = os.path.join(backend_dir, r'app\services\kis_broker.py')
with open(kis_path, 'r', encoding='utf-8') as f:
    kis_content = f.read()

# Replace 13 sites
new_kis = kis_content.replace('result.get("rt_code")', 'result.get("rt_cd")')
new_kis = new_kis.replace("result.get('rt_code')", "result.get('rt_cd')")
new_kis = new_kis.replace('result.get("rt_msg")', 'result.get("msg1")')
new_kis = new_kis.replace("result.get('rt_msg')", "result.get('msg1')")

with open(kis_path, 'w', encoding='utf-8') as f:
    f.write(new_kis)

out, _ = run_cmd('git diff app/services/kis_broker.py')
print("--- git diff app/services/kis_broker.py ---")
print(out)

# Commit D-1
run_cmd('git add app/services/kis_broker.py')
commit_msg, _ = run_cmd('git commit -m "fix(kis): correct response field names rt_cd/msg1 (13 sites)"')
print("Commit D-1 Output:\n", commit_msg)

print("\n==================================================")
print("2. [D-1 VERIFICATION] 4 Verification Items")
print("==================================================")
from app.services.kis_broker import KisBroker

async def verify_d1():
    broker = KisBroker()
    try:
        # (a) NVDA call
        res_nvda = await broker.get_stock_price("NVDA")
        print("(a) NVDA call:", {
            "success": res_nvda.get("success"),
            "current_price": res_nvda.get("current_price"),
            "rt_code": res_nvda.get("rt_code"),
            "rt_msg": res_nvda.get("rt_msg")
        })
        
        # (b) NYDA call
        res_nyda = await broker.get_stock_price("NYDA")
        print("(b) NYDA call:", {
            "success": res_nyda.get("success"),
            "current_price": res_nyda.get("current_price"),
            "rt_code": res_nyda.get("rt_code"),
            "rt_msg": res_nyda.get("rt_msg")
        })
        
        # (c) Balance call
        res_bal = await broker.get_account_balance()
        print("(c) Balance call:", {
            "success": res_bal.get("success"),
            "rt_code": res_bal.get("rt_code"),
            "rt_msg": res_bal.get("rt_msg")
        })
    finally:
        await broker.close()

asyncio.run(verify_d1())

print("\n==================================================")
print("3. [D-2 PATCH] App.tsx unify null rendering")
print("==================================================")
app_path = os.path.join(frontend_dir, r'src\App.tsx')
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

# 1942: gaugePercent
# 1973: toFixed(0)
# 973: c.master_score
# 2223: stock.master_score
# 2032: raw_score / master_score
# 1002: confidence
new_app = app_content
new_app = new_app.replace('const gaugePercent = data?.master_score || 50;', 'const gaugePercent = data?.master_score ?? 50;')
new_app = new_app.replace('{data?.master_score?.toFixed(0) || 0}', "{data?.master_score != null ? data.master_score.toFixed(0) : '—'}")
new_app = new_app.replace('{c.ticker} ({c.master_score}점)', "{c.ticker} ({c.master_score != null ? `${c.master_score}점` : '—'})")
new_app = new_app.replace('{stock.master_score}점', "{stock.master_score != null ? `${stock.master_score}점` : '—'}")
new_app = new_app.replace('원점수: {data?.raw_score?.toFixed(1)} → 최종: {data?.master_score?.toFixed(1)}', "원점수: {data?.raw_score != null ? data.raw_score.toFixed(1) : '—'} → 최종: {data?.master_score != null ? data.master_score.toFixed(1) : '—'}")
new_app = new_app.replace('c.confidence || 50', 'c.confidence ?? 50')

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(new_app)

out_ui, _ = run_cmd('git diff src/App.tsx', cwd=frontend_dir)
print("--- git diff src/App.tsx ---")
print(out_ui)

run_cmd('git add src/App.tsx', cwd=frontend_dir)
commit_ui, _ = run_cmd('git commit -m "fix(ui): unify null rendering for master_score and confidence"', cwd=frontend_dir)
print("Commit D-2 Output:\n", commit_ui)

print("\n==================================================")
print("4. [B-3 3-RUN GATHER TIMING] 8 Tasks Timing Benchmark x 3 Runs")
print("==================================================")
from app.services.data_collector import DataCollector
from app.services.technical_analysis import TechnicalAnalyzer
from app.services.llm_analyzer import LLMNewsAnalyzer
from app.services.options_flow import OptionsFlowEngine
from app.services.darkpool_analyzer import DarkPoolAnalyzer
from app.services.event_engine import EventEngine
from app.services.correlation_engine import CorrelationEngine
from app.services.investor_analysis import InvestorAnalysisEngine
from app.services.news_sentiment import create_fear_greed_index
from app.services.edgar_tracker import create_edgar_tracker
from dataclasses import asdict

async def benchmark_3runs():
    ticker = "NVDA"
    collector = DataCollector()
    analyzer = TechnicalAnalyzer()
    stock_info = collector.get_stock_info(ticker)
    hist = collector.get_historical_data(ticker, "1y")
    tech = analyzer.analyze(ticker, hist, stock_info.current_price)
    stock_dict = {k: v for k, v in asdict(stock_info).items() if v is not None}
    
    for r in range(1, 4):
        llm = LLMNewsAnalyzer(ticker=ticker)
        opt = OptionsFlowEngine(ticker=ticker)
        dp = DarkPoolAnalyzer(ticker=ticker)
        ev = EventEngine(ticker=ticker)
        corr = CorrelationEngine(ticker=ticker)
        inv = InvestorAnalysisEngine()
        fng = create_fear_greed_index()
        edgar = create_edgar_tracker()
        
        t_start = time.perf_counter()
        async def timed_task(name, coro_or_func, *args, is_async=True):
            ts = time.perf_counter() - t_start
            if is_async:
                res = await coro_or_func(*args)
            else:
                res = await asyncio.to_thread(coro_or_func, *args)
            te = time.perf_counter() - t_start
            return name, te - ts, ts, te

        tasks = await asyncio.gather(
            timed_task("llm_news", llm.analyze, ticker, is_async=True),
            timed_task("options_flow", opt.analyze, ticker, is_async=True),
            timed_task("darkpool", dp.analyze, ticker, is_async=False),
            timed_task("events", ev.analyze, ticker, is_async=False),
            timed_task("correlation", corr.analyze, ticker, is_async=False),
            timed_task("investor", inv.analyze, ticker, stock_dict, tech, hist, is_async=False),
            timed_task("fng_data", fng.fetch, is_async=True),
            timed_task("edgar", edgar.fetch_all, True, is_async=True),
            return_exceptions=True
        )
        t_total = time.perf_counter() - t_start
        print(f"\n--- Run {r} (Total Gather: {t_total:5.3f}s) ---")
        for item in tasks:
            if isinstance(item, tuple):
                name, dt, ts, te = item
                print(f"  {name:15s}: dur={dt:5.3f}s (start=+{ts:5.3f}s, end=+{te:5.3f}s)")
        time.sleep(1)

asyncio.run(benchmark_3runs())

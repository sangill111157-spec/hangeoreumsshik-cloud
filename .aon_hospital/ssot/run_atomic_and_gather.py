# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, asyncio
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# [A] KIS ATOMIC CALL PROOF (NVDA & NYDA)
print("==================================================")
print("1. [A-1] KIS ATOMIC CALL PROOF (NVDA & NYDA)")
print("==================================================")
from app.services.kis_broker import KisBroker

async def test_kis_atomic():
    broker = KisBroker()
    try:
        # 1) NVDA atomic test
        token = await broker.get_access_token()
        client = await broker._get_http_client()
        headers = {
            "authorization": f"Bearer {token}",
            "appkey": broker.app_key,
            "appsecret": broker.app_secret,
            "tr_id": "HHDFS00000300",
            "Content-Type": "application/json; charset=utf-8"
        }
        res_nvda = await client.get(f"{broker.base_url}/uapi/overseas-price/v1/quotations/price", headers=headers, params={"AUTH": "", "EXCD": "NAS", "SYMB": "NVDA"})
        result_nvda = res_nvda.json()
        parsed_nvda = await broker.get_stock_price("NVDA")
        
        print("--- [NVDA ATOMIC SINGLE CALL PROOF] ---")
        print({
            "sorted_result_keys": sorted(result_nvda.keys()),
            "rt_cd": result_nvda.get("rt_cd"),
            "rt_code_in_raw": result_nvda.get("rt_code"),
            "success_in_return_dict": parsed_nvda.get("success"),
            "current_price_in_return_dict": parsed_nvda.get("current_price"),
            "output_last": result_nvda.get("output", {}).get("last") if isinstance(result_nvda.get("output"), dict) else None
        })

        # 2) NYDA test
        res_nyda = await client.get(f"{broker.base_url}/uapi/overseas-price/v1/quotations/price", headers=headers, params={"AUTH": "", "EXCD": "NAS", "SYMB": "NYDA"})
        result_nyda = res_nyda.json()
        print("\n--- [NYDA (INVALID TICKER) RAW KIS RESPONSE] ---")
        print({
            "status_code": res_nyda.status_code,
            "sorted_keys": sorted(result_nyda.keys()),
            "rt_cd": result_nyda.get("rt_cd"),
            "msg_cd": result_nyda.get("msg_cd"),
            "msg1": result_nyda.get("msg1"),
            "output": result_nyda.get("output")
        })
    except Exception as e:
        print("KIS Atomic Test Error:", e)
    finally:
        await broker.close()

asyncio.run(test_kis_atomic())

# [B] GATHER 8 TASKS INDIVIDUAL TIMING BENCHMARK
print("\n==================================================")
print("2. [B-3] GATHER 8 TASKS INDIVIDUAL START/END TIMESTAMPS")
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

async def benchmark_gather_tasks():
    ticker = "NVDA"
    collector = DataCollector()
    analyzer = TechnicalAnalyzer()
    stock_info = collector.get_stock_info(ticker)
    historical_data = collector.get_historical_data(ticker, period="1y")
    technical_obj = analyzer.analyze(ticker, historical_data, stock_info.current_price)
    stock_dict = {k: v for k, v in asdict(stock_info).items() if v is not None}
    
    llm_analyzer = LLMNewsAnalyzer(ticker=ticker)
    options_engine = OptionsFlowEngine(ticker=ticker)
    darkpool_analyzer = DarkPoolAnalyzer(ticker=ticker)
    event_engine = EventEngine(ticker=ticker)
    corr_engine = CorrelationEngine(ticker=ticker)
    investor_engine = InvestorAnalysisEngine()
    fng_service = create_fear_greed_index()
    edgar_tracker = create_edgar_tracker()
    
    t_gather_start = time.perf_counter()
    
    async def timed_task(name, coro_or_func, *args, is_async=True):
        t_start = time.perf_counter() - t_gather_start
        if is_async:
            res = await coro_or_func(*args)
        else:
            res = await asyncio.to_thread(coro_or_func, *args)
        t_end = time.perf_counter() - t_gather_start
        dt = t_end - t_start
        print(f"  Task [{name:20s}]: start=+{t_start:5.3f}s | end=+{t_end:5.3f}s | duration={dt:5.3f}s")
        return res

    print("Launching 8 tasks in asyncio.gather:")
    res = await asyncio.gather(
        timed_task("0: llm_news", llm_analyzer.analyze, ticker, is_async=True),
        timed_task("1: options_flow", options_engine.analyze, ticker, is_async=True),
        timed_task("2: darkpool", darkpool_analyzer.analyze, ticker, is_async=False),
        timed_task("3: events", event_engine.analyze, ticker, is_async=False),
        timed_task("4: correlation", corr_engine.analyze, ticker, is_async=False),
        timed_task("5: investor", investor_engine.analyze, ticker, stock_dict, technical_obj, historical_data, is_async=False),
        timed_task("6: fng_data", fng_service.fetch, is_async=True),
        timed_task("7: edgar", edgar_tracker.fetch_all, True, is_async=True),
        return_exceptions=True
    )
    t_gather_end = time.perf_counter() - t_gather_start
    print(f"--> Total gather Wall time: {t_gather_end:5.3f}s")

asyncio.run(benchmark_gather_tasks())

# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, urllib.request
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("==================================================")
print("1. [B-1 DETAIL] kis_broker.py:360-440 get_stock_price full logic")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\kis_broker.py'), 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()
for i in range(355, 435):
    print(f"{i+1:4d}: {lines[i].rstrip()}")

print("\n==================================================")
print("2. [C DETAIL] All 4 module threshold conversion functions")
print("==================================================")
# Search darkpool threshold
for i, l in enumerate(lines):
    pass
with open(os.path.join(backend_dir, r'app\services\darkpool_analyzer.py'), 'r', encoding='utf-8', errors='replace') as f:
    dp_lines = f.readlines()
for i, l in enumerate(dp_lines):
    if 'def calculate_darkpool_score' in l or 'def _score_to_signal' in l or 'def analyze' in l:
        print(f"--- darkpool_analyzer.py at line {i+1} ---")
        for j in range(i, min(len(dp_lines), i + 35)):
            print(f"{j+1:4d}: {dp_lines[j].rstrip()}")
        break

with open(os.path.join(backend_dir, r'app\services\llm_analyzer.py'), 'r', encoding='utf-8', errors='replace') as f:
    llm_lines = f.readlines()
for i, l in enumerate(llm_lines):
    if 'def analyze' in l or 'def _calculate' in l or 'def calculate' in l:
        print(f"--- llm_analyzer.py at line {i+1} ---")
        for j in range(i, min(len(llm_lines), i + 40)):
            print(f"{j+1:4d}: {llm_lines[j].rstrip()}")
        break

print("\n==================================================")
print("3. [D] 4-POINT TIME MEASUREMENT x 5 RUNS")
print("==================================================")
# Import services directly for 4-point profiling in identical structure as stock.py
from app.services.data_collector import DataCollector
from app.services.technical_analysis import TechnicalAnalyzer
from app.services.llm_analyzer import LLMNewsAnalyzer
from app.services.options_flow import OptionsFlowEngine
from app.services.darkpool_analyzer import DarkPoolAnalyzer
from app.services.event_engine import EventEngine
from app.services.correlation_engine import CorrelationEngine
from app.services.investor_analysis import InvestorAnalysisEngine
from app.services.pod_manager import create_pod_manager
from app.services.news_sentiment import create_fear_greed_index
from app.services.edgar_tracker import create_edgar_tracker
from app.services.master_signal import MasterSignalEngine
from dataclasses import asdict
import asyncio

async def run_single_profile(run_id):
    ticker = "NVDA"
    collector = DataCollector()
    analyzer = TechnicalAnalyzer()
    
    t_wall_start = time.perf_counter()
    
    # t0: Entry
    t0 = time.perf_counter()
    
    # t1: get_stock_info + hist + tech
    stock_info = collector.get_stock_info(ticker)
    t1 = time.perf_counter()
    
    historical_data = collector.get_historical_data(ticker, period="1y")
    technical_obj = analyzer.analyze(ticker, historical_data, stock_info.current_price)
    stock_dict = {k: v for k, v in asdict(stock_info).items() if v is not None}
    
    # Engines prep
    llm_analyzer = LLMNewsAnalyzer(ticker=ticker)
    options_engine = OptionsFlowEngine(ticker=ticker)
    darkpool_analyzer = DarkPoolAnalyzer(ticker=ticker)
    event_engine = EventEngine(ticker=ticker)
    corr_engine = CorrelationEngine(ticker=ticker)
    investor_engine = InvestorAnalysisEngine()
    pod_mgr = create_pod_manager()
    fng_service = create_fear_greed_index()
    edgar_tracker = create_edgar_tracker()
    
    # gather
    t_gather_start = time.perf_counter()
    parallel_results = await asyncio.gather(
        llm_analyzer.analyze(ticker),
        options_engine.analyze(ticker),
        asyncio.to_thread(darkpool_analyzer.analyze, ticker),
        asyncio.to_thread(event_engine.analyze, ticker),
        asyncio.to_thread(corr_engine.analyze, ticker),
        asyncio.to_thread(investor_engine.analyze, ticker, stock_dict, technical_obj, historical_data),
        fng_service.fetch(),
        edgar_tracker.fetch_all(use_mock=True),
        return_exceptions=True
    )
    t2 = time.perf_counter()
    
    # Post-gather: PodManager + MasterSignal calculation
    llm_res, opt_res, dp_res, ev_res, corr_res, inv_res, fng_res, edgar_res = parallel_results
    
    sentiment_data = {
        "overall_score": (llm_res.news_composite_score - 50) / 50.0 if hasattr(llm_res, 'news_composite_score') and llm_res.news_composite_score is not None else 0.0,
        "sentiment_label": getattr(llm_res, 'sentiment_label', 'HOLD'),
        "trend": "STABLE",
        "news_count": getattr(llm_res, 'total_news_analyzed', 0),
        "confidence": 50
    }
    pod_data = {
        "stock_info": stock_dict,
        "technical": {"confidence": 50},
        "sentiment": sentiment_data,
        "fear_greed": {"value": 50, "label": "Neutral", "signal": "HOLD"},
        "portfolio": {"nvda": {"investors": []}, "overlaps": [], "recent_buys": []}
    }
    pod_result = await pod_mgr.analyze_all(pod_data)
    
    ms_engine = MasterSignalEngine()
    # Mock / calculated master signal
    t3 = time.perf_counter()
    t_wall_end = time.perf_counter()
    
    dt_info = t1 - t0
    dt_gather = t2 - t_gather_start
    dt_post = t3 - t2
    dt_total = t3 - t0
    dt_wall = t_wall_end - t_wall_start
    
    print(f"Run {run_id}: t0->t1 (get_info)={dt_info:5.3f}s | t1->t2 (gather)={dt_gather:5.3f}s | t2->t3 (post)={dt_post:5.3f}s | Total Handler={dt_total:5.3f}s | Wall={dt_wall:5.3f}s")
    return dt_info, dt_gather, dt_post, dt_total, dt_wall

async def main_profile():
    for i in range(1, 6):
        await run_single_profile(i)
        time.sleep(1)

asyncio.run(main_profile())

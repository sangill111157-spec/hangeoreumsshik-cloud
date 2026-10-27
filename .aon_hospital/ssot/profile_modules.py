# -*- coding: utf-8 -*-
import sys, os, time, asyncio, json
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\trading\package\nvda_trading_system\backend')

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

async def benchmark():
    ticker = "NVDA"
    print("==================================================")
    print("1. INDIVIDUAL MODULE PROFILING (Time per module)")
    print("==================================================")
    
    collector = DataCollector()
    t0 = time.perf_counter()
    stock_info = collector.get_stock_info(ticker)
    t_info = time.perf_counter() - t0
    print(f"  [0] DataCollector.get_stock_info : {t_info:6.3f}s")

    t0 = time.perf_counter()
    hist_data = collector.get_historical_data(ticker, "1y")
    t_hist = time.perf_counter() - t0
    print(f"  [1] DataCollector.get_hist_data  : {t_hist:6.3f}s")

    t0 = time.perf_counter()
    tech_analyzer = TechnicalAnalyzer()
    tech_obj = tech_analyzer.analyze(ticker, hist_data, current_price=stock_info.current_price)
    t_tech = time.perf_counter() - t0
    print(f"  [2] TechnicalAnalyzer.analyze    : {t_tech:6.3f}s")

    stock_dict = {k: v for k, v in asdict(stock_info).items() if v is not None}

    # Parallel 8 modules individual times
    llm_analyzer = LLMNewsAnalyzer(ticker=ticker)
    t0 = time.perf_counter()
    llm_res = await llm_analyzer.analyze(ticker)
    t_llm = time.perf_counter() - t0
    print(f"  [3] LLMNewsAnalyzer.analyze      : {t_llm:6.3f}s")

    options_engine = OptionsFlowEngine(ticker=ticker)
    t0 = time.perf_counter()
    opt_res = await options_engine.analyze(ticker)
    t_opt = time.perf_counter() - t0
    print(f"  [4] OptionsFlowEngine.analyze    : {t_opt:6.3f}s")

    darkpool_analyzer = DarkPoolAnalyzer(ticker=ticker)
    t0 = time.perf_counter()
    dp_res = darkpool_analyzer.analyze(ticker)
    t_dp = time.perf_counter() - t0
    print(f"  [5] DarkPoolAnalyzer.analyze     : {t_dp:6.3f}s")

    event_engine = EventEngine(ticker=ticker)
    t0 = time.perf_counter()
    ev_res = event_engine.analyze(ticker)
    t_ev = time.perf_counter() - t0
    print(f"  [6] EventEngine.analyze          : {t_ev:6.3f}s")

    corr_engine = CorrelationEngine(ticker=ticker)
    t0 = time.perf_counter()
    corr_res = corr_engine.analyze(ticker)
    t_corr = time.perf_counter() - t0
    print(f"  [7] CorrelationEngine.analyze    : {t_corr:6.3f}s")

    investor_engine = InvestorAnalysisEngine()
    t0 = time.perf_counter()
    inv_res = investor_engine.analyze(ticker, stock_dict, tech_obj, hist_data)
    t_inv = time.perf_counter() - t0
    print(f"  [8] InvestorAnalysisEngine       : {t_inv:6.3f}s")

    fng_service = create_fear_greed_index()
    t0 = time.perf_counter()
    fng_res = await fng_service.fetch()
    t_fng = time.perf_counter() - t0
    print(f"  [9] FearGreedService.fetch       : {t_fng:6.3f}s")

    edgar_tracker = create_edgar_tracker()
    t0 = time.perf_counter()
    edgar_res = await edgar_tracker.fetch_all(use_mock=True)
    t_edgar = time.perf_counter() - t0
    print(f"  [10] EdgarTracker.fetch_all      : {t_edgar:6.3f}s")

    # Pod Manager
    pod_mgr = create_pod_manager()
    sentiment_data = {
        "overall_score": (llm_res.news_composite_score - 50) / 50.0 if llm_res.news_composite_score is not None else 0.0,
        "sentiment_label": llm_res.sentiment_label,
        "trend": "STABLE",
        "news_count": llm_res.total_news_analyzed,
        "confidence": min(100, llm_res.total_news_analyzed * 5)
    }
    pod_data = {
        "stock_info": stock_dict,
        "technical": {
            "rsi": {"value": tech_obj.rsi.value},
            "macd": {"histogram": tech_obj.macd.histogram},
            "trend": tech_obj.trend,
            "bollinger_bands": {
                "upper": tech_obj.bollinger_bands.upper_band,
                "middle": tech_obj.bollinger_bands.middle_band,
                "lower": tech_obj.bollinger_bands.lower_band
            },
            "moving_averages": {
                "ma_20": tech_obj.moving_averages.ma_20,
                "ma_50": tech_obj.moving_averages.ma_50,
                "ma_200": tech_obj.moving_averages.ma_200
            },
            "confidence": tech_obj.confidence
        },
        "sentiment": sentiment_data,
        "fear_greed": {
            "value": fng_res.value,
            "label": fng_res.label,
            "signal": "HOLD"
        },
        "portfolio": {"nvda": {"investors": []}, "overlaps": [], "recent_buys": []}
    }
    t0 = time.perf_counter()
    pod_res = await pod_mgr.analyze_all(pod_data)
    t_pod = time.perf_counter() - t0
    print(f"  [11] PodManager.analyze_all      : {t_pod:6.3f}s")

    sum_all = t_info + t_hist + t_tech + t_llm + t_opt + t_dp + t_ev + t_corr + t_inv + t_fng + t_edgar + t_pod
    print(f"\n==> Pure Sequential Sum of All Steps: {sum_all:6.3f}s")

    # Measure Parallel gather execution time
    t0 = time.perf_counter()
    parallel_results = await asyncio.gather(
        llm_analyzer.analyze(ticker),
        options_engine.analyze(ticker),
        asyncio.to_thread(darkpool_analyzer.analyze, ticker),
        asyncio.to_thread(event_engine.analyze, ticker),
        asyncio.to_thread(corr_engine.analyze, ticker),
        asyncio.to_thread(investor_engine.analyze, ticker, stock_dict, tech_obj, hist_data),
        fng_service.fetch(),
        edgar_tracker.fetch_all(use_mock=True),
        return_exceptions=True
    )
    t_gather = time.perf_counter() - t0
    print(f"==> asyncio.gather (8 tasks in parallel): {t_gather:6.3f}s")
    print(f"==> Total with sequential pre/post + gather: {t_info + t_hist + t_tech + t_gather + t_pod:6.3f}s")

asyncio.run(benchmark())

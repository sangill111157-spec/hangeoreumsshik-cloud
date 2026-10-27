# -*- coding: utf-8 -*-
import sys

stock_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py'
with open(stock_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find line 584 (after technical_obj) to line 640
start_idx = None
end_idx = None
for i, l in enumerate(lines):
    if '# 2. LLM' in l or 'llm_analyzer = LLMNewsAnalyzer' in l:
        start_idx = i - 1
    if start_idx is not None and 'sentiment_data = {' in l:
        end_idx = i
        break

if start_idx is None or end_idx is None:
    print("ERROR: indices not found")
    sys.exit(1)

parallel_block = """        # 2. 분석 엔진 및 서비스 준비
        llm_analyzer = LLMNewsAnalyzer(ticker=ticker)
        options_engine = OptionsFlowEngine(ticker=ticker)
        darkpool_analyzer = DarkPoolAnalyzer(ticker=ticker)
        event_engine = EventEngine(ticker=ticker)
        corr_engine = CorrelationEngine(ticker=ticker)
        investor_engine = InvestorAnalysisEngine()
        stock_dict = {k: v for k, v in asdict(stock_info).items() if v is not None}

        from app.services.pod_manager import create_pod_manager, get_pod_manager
        from app.services.news_sentiment import create_fear_greed_index, get_fear_greed_index as get_fear_greed_service
        from app.services.edgar_tracker import create_edgar_tracker, get_edgar_tracker

        pod_mgr = get_pod_manager() or create_pod_manager()
        fng_service = get_fear_greed_service() or create_fear_greed_index()
        edgar_tracker = get_edgar_tracker() or create_edgar_tracker()

        # 3. 7개 모듈 및 비동기 데이터 수집 병렬 실행 (asyncio.to_thread + gather)
        parallel_results = await asyncio.gather(
            llm_analyzer.analyze(ticker),                                                                # 0: llm_news
            options_engine.analyze(ticker),                                                             # 1: options_flow
            asyncio.to_thread(darkpool_analyzer.analyze, ticker),                                       # 2: darkpool
            asyncio.to_thread(event_engine.analyze, ticker),                                           # 3: events
            asyncio.to_thread(corr_engine.analyze, ticker),                                            # 4: correlation
            asyncio.to_thread(investor_engine.analyze, ticker, stock_dict, technical_obj, historical_data), # 5: investor
            fng_service.fetch(),                                                                        # 6: fng_data
            edgar_tracker.fetch_all(use_mock=True),                                                     # 7: edgar
            return_exceptions=True
        )

        # 결과 언팩 및 예외 격리
        llm_raw, options_raw, darkpool_raw, event_raw, corr_raw, investor_raw, fng_raw, edgar_raw = parallel_results

        # 1) LLM 뉴스
        if isinstance(llm_raw, Exception):
            logger.error(f"llm_analyzer failed: {llm_raw}")
            llm_result = LLMNewsResult(news_composite_score=50.0, news_signal="HOLD", sentiment_label="NEUTRAL", total_news_analyzed=0, ceo_mentions=[])
        else:
            llm_result = llm_raw

        # 2) 옵션 플로우
        if isinstance(options_raw, Exception):
            logger.error(f"options_engine failed: {options_raw}")
            options_result = OptionsFlowResult(available=False, options_composite_score=50.0, options_signal="HOLD")
        else:
            options_result = options_raw

        # 3) 다크풀
        if isinstance(darkpool_raw, Exception):
            logger.error(f"darkpool_analyzer failed: {darkpool_raw}")
            darkpool_result = DarkPoolResult(available=False, darkpool_composite_score=50.0, darkpool_signal="HOLD")
        else:
            darkpool_result = darkpool_raw

        # 4) 이벤트
        if isinstance(event_raw, Exception):
            logger.error(f"event_engine failed: {event_raw}")
            event_result = EventResult(upcoming_events=[])
        else:
            event_result = event_raw

        # 5) 상관관계
        if isinstance(corr_raw, Exception):
            logger.error(f"corr_engine failed: {corr_raw}")
            corr_result = CorrelationResult(sector_momentum_score=50.0, macro_indicator_score=50.0)
        else:
            corr_result = corr_raw

        # 6) 5대 투자자
        if isinstance(investor_raw, Exception):
            logger.error(f"investor_engine failed: {investor_raw}")
            investor_result = InvestorAnalysisResult(overall_signal="HOLD", overall_confidence=50, bull_count=0, bear_count=0)
        else:
            investor_result = investor_raw

        # 7) Fear & Greed
        if isinstance(fng_raw, Exception):
            logger.error(f"fng_service failed: {fng_raw}")
            fng_data = FearGreedData(value=50, label="Neutral", previous_close=50, previous_1_week=50, previous_1_month=50, previous_1_year=50)
            fng_signal = {"signal": "HOLD"}
        else:
            fng_data = fng_raw
            fng_signal = fng_service.get_investment_signal(fng_data)

        # 8) EDGAR 데이터
        overlapping = edgar_tracker.get_overlapping_stocks(min_investors=2) if not isinstance(edgar_raw, Exception) else []
        recent_buys = edgar_tracker.get_recent_buys(limit=5) if not isinstance(edgar_raw, Exception) else []
        portfolio_data = {
            "nvda": {
                "investors": [
                    {"Name": "Warren Buffett", "transaction_type": "INCREASED", "value": 8500000},
                    {"Name": "Jim Simons", "transaction_type": "INCREASED", "value": 125000000}
                ]
            },
            "overlaps": overlapping,
            "recent_buys": [
                {"ticker": b.ticker, "current_value": b.current_value, "transaction_type": b.transaction_type.value}
                for b in recent_buys
            ]
        }
"""

lines[start_idx:end_idx] = [parallel_block]
with open(stock_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("PATCH stock.py O-PATCH-2 SUCCESS")

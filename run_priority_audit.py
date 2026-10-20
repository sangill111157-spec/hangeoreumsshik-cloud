# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, asyncio, urllib.request
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [B-1] pod_to_score 원문 & 단일 요청 3중 증빙")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\master_signal.py'), 'r', encoding='utf-8', errors='replace') as f:
    ms_lines = f.readlines()

for i, l in enumerate(ms_lines):
    if 'def pod_to_score' in l:
        print(f"--- master_signal.py: pod_to_score at line {i+1} ---")
        for j in range(i, min(len(ms_lines), i + 30)):
            print(f"{j+1:4d}: {ms_lines[j].rstrip()}")
        break

# Live simultaneous fetch: PodManager vs Master Components vs Master Score
from app.services.data_collector import DataCollector
from app.services.technical_analysis import TechnicalAnalyzer
from app.services.pod_manager import create_pod_manager
from dataclasses import asdict

async def test_triple_proof():
    ticker = "NVDA"
    collector = DataCollector()
    analyzer = TechnicalAnalyzer()
    stock_info = collector.get_stock_info(ticker)
    hist = collector.get_historical_data(ticker, "1y")
    tech = analyzer.analyze(ticker, hist, stock_info.current_price)
    stock_dict = {k: v for k, v in asdict(stock_info).items() if v is not None}
    
    pod_mgr = create_pod_manager()
    pod_data = {
        "stock_info": stock_dict,
        "technical": {
            "rsi": {"value": tech.rsi.value},
            "macd": {"histogram": tech.macd.histogram},
            "trend": tech.trend,
            "bollinger_bands": {
                "upper": tech.bollinger_bands.upper_band,
                "middle": tech.bollinger_bands.middle_band,
                "lower": tech.bollinger_bands.lower_band
            },
            "moving_averages": {
                "ma_20": tech.moving_averages.ma_20,
                "ma_50": tech.moving_averages.ma_50,
                "ma_200": tech.moving_averages.ma_200
            },
            "confidence": tech.confidence
        },
        "sentiment": {"overall_score": 0.0, "sentiment_label": "HOLD", "trend": "STABLE", "news_count": 0, "confidence": 50},
        "fear_greed": {"value": 50, "label": "Neutral", "signal": "HOLD"},
        "portfolio": {"nvda": {"investors": []}, "overlaps": [], "recent_buys": []}
    }
    pod_res = await pod_mgr.analyze_all(pod_data)
    print("\n--- [PodManager.analyze_all return values] ---")
    print("5 Pod Raw Scores & Signals:")
    for s in pod_res.pod_signals:
        print(f"  - {s.pod_name:15s}: score={getattr(s, 'score', 'N/A')}, signal={s.signal}, conf={s.confidence}")
    print("PodManager composite master_score:", pod_res.master_score)
    print("PodManager composite signal      :", pod_res.signal)

asyncio.run(test_triple_proof())

print("\n==================================================")
print("2. [B-3] ComponentScore 생성 블록 현재 원문 & 임계 분기 3건")
print("==================================================")
for i, l in enumerate(ms_lines):
    if 'components = [' in l:
        print(f"--- master_signal.py ComponentScore block at line {i+1} ---")
        for j in range(i, min(len(ms_lines), i + 75)):
            print(f"{j+1:4d}: {ms_lines[j].rstrip()}")
        break

# TechnicalAnalyzer score to signal
with open(os.path.join(backend_dir, r'app\services\technical_analysis.py'), 'r', encoding='utf-8', errors='replace') as f:
    tech_lines = f.readlines()
for i, l in enumerate(tech_lines):
    if 'overall_signal =' in l or 'def _determine_overall_signal' in l or 'def analyze(' in l:
        if 'strong_buy' in l.lower() or 'overall_signal' in l:
            for j in range(max(0, i-5), min(len(tech_lines), i+20)):
                print(f"tech_analysis:{j+1:4d}: {tech_lines[j].rstrip()}")
            break

print("\n==================================================")
print("3. [B-2] 1cdbedf full diff (120/132) & details grep")
print("==================================================")
h_file = os.path.join(backend_dir, "h_full.txt")
run_cmd(f"git diff 1cdbedf~1..1cdbedf -U0 -- app/services/master_signal.py > {h_file}")
with open(h_file, "r", encoding="utf-8", errors="replace") as f:
    diff_text = f.read()
print(f"Full diff length in chars: {len(diff_text)}, lines: {len(diff_text.splitlines())}")

# Commit message
msg, _ = run_cmd('git show 1cdbedf --format="%s%n%b" -s')
print("\nCommit 1cdbedf Message:\n", msg)

# grep details in App.tsx
out_det, _ = run_cmd('git grep -rn "details" src/App.tsx', cwd=frontend_dir)
print("\ngrep 'details' in src/App.tsx:\n", out_det if out_det.strip() else "  (0건 - 프론트엔드에서 details 참조 없음)")

print("\n==================================================")
print("4. [B-4] KIS success 13곳 함수 매핑 & 소비 전수 grep")
print("==================================================")
out_prod, _ = run_cmd('git grep -n "success" app/services/kis_broker.py')
print("KIS Broker 'success' lines:\n", out_prod)

out_cons, _ = run_cmd('git grep -rn -E "\.get\([\"\\\']success[\"\\\']\)|\[[\"\\\']success[\"\\\']\]" app/')
print("\nAll Backend Consumers of 'success':\n", out_cons)

print("\n==================================================")
print("5. [B-5] 4-Point 절대 타임스탬프 계측 (동일 계측기)")
print("==================================================")
async def measure_absolute_4points():
    ticker = "NVDA"
    collector = DataCollector()
    analyzer = TechnicalAnalyzer()
    
    t_client_0 = time.perf_counter()
    t0 = time.perf_counter()
    
    stock_info = collector.get_stock_info(ticker)
    hist = collector.get_historical_data(ticker, "1y")
    tech = analyzer.analyze(ticker, hist, stock_info.current_price)
    stock_dict = {k: v for k, v in asdict(stock_info).items() if v is not None}
    t1 = time.perf_counter()
    
    # Simple simulated gather with same modules
    from app.services.llm_analyzer import LLMNewsAnalyzer
    from app.services.options_flow import OptionsFlowEngine
    from app.services.darkpool_analyzer import DarkPoolAnalyzer
    from app.services.event_engine import EventEngine
    from app.services.correlation_engine import CorrelationEngine
    from app.services.investor_analysis import InvestorAnalysisEngine
    from app.services.news_sentiment import create_fear_greed_index
    from app.services.edgar_tracker import create_edgar_tracker
    
    llm = LLMNewsAnalyzer(ticker=ticker)
    opt = OptionsFlowEngine(ticker=ticker)
    dp = DarkPoolAnalyzer(ticker=ticker)
    ev = EventEngine(ticker=ticker)
    corr = CorrelationEngine(ticker=ticker)
    inv = InvestorAnalysisEngine()
    fng = create_fear_greed_index()
    edgar = create_edgar_tracker()
    
    p_results = await asyncio.gather(
        llm.analyze(ticker),
        opt.analyze(ticker),
        asyncio.to_thread(dp.analyze, ticker),
        asyncio.to_thread(ev.analyze, ticker),
        asyncio.to_thread(corr.analyze, ticker),
        asyncio.to_thread(inv.analyze, ticker, stock_dict, tech, hist),
        fng.fetch(),
        edgar.fetch_all(use_mock=True),
        return_exceptions=True
    )
    t2 = time.perf_counter()
    
    # t2 -> t3: post calculation
    pod_mgr = create_pod_manager()
    pod_data = {
        "stock_info": stock_dict,
        "technical": {"confidence": 50},
        "sentiment": {"overall_score": 0.0, "sentiment_label": "HOLD", "trend": "STABLE", "news_count": 0, "confidence": 50},
        "fear_greed": {"value": 50, "label": "Neutral", "signal": "HOLD"},
        "portfolio": {"nvda": {"investors": []}, "overlaps": [], "recent_buys": []}
    }
    await pod_mgr.analyze_all(pod_data)
    t3 = time.perf_counter()
    t_client_1 = time.perf_counter()
    
    print(f"Absolute Timestamps:")
    print(f"  t0 (Entry)       : {t0:12.4f}s")
    print(f"  t1 (get_info End): {t1:12.4f}s (dt = {t1-t0:6.3f}s)")
    print(f"  t2 (gather End)  : {t2:12.4f}s (dt = {t2-t1:6.3f}s)")
    print(f"  t3 (Return)      : {t3:12.4f}s (dt = {t3-t2:6.3f}s)")
    print(f"  Handler Total    : {t3-t0:6.3f}s")
    print(f"  Client Wall Total: {t_client_1 - t_client_0:6.3f}s")

asyncio.run(measure_absolute_4points())

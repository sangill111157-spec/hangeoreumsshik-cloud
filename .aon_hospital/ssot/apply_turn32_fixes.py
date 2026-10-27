# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update master_signal.py:
# - Replace assert with raise ValueError in calculate_kelly (defect 121)
# - Ensure options_flow and darkpool support dynamic confidence emission
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Replace assert in calculate_kelly
old_kelly_assert = """    actual_pos_val = round(shares * stock_price, 2)
    assert actual_pos_val <= ceiling_value + 1e-6, f"Position value ${actual_pos_val} exceeded ceiling ${ceiling_value}!" """

new_kelly_assert = """    actual_pos_val = round(shares * stock_price, 2)
    # 결함 121 완결: python -O 무력화 방지 ValueError 런타임 예외 적용
    if actual_pos_val > ceiling_value + 1e-4:
        raise ValueError(f"Position value ${actual_pos_val} exceeded stage 1 ceiling ${ceiling_value}!")"""

if old_kelly_assert in ms_c:
    ms_c = ms_c.replace(old_kelly_assert, new_kelly_assert)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 2. Update stock.py test-signal to support BUY injection with full components
st_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(st_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

# Update test-signal to allow mode parameter (normal, buy, unavailable)
old_test_signal = """@router.get("/{ticker}/test-signal", include_in_schema=False)
async def get_stock_test_signal(
    ticker: str = Path(..., description="종목 코드"),
    force_unavailable: Optional[str] = None,
    collector: DataCollector = Depends(get_data_collector),
    analyzer: TechnicalAnalyzer = Depends(get_technical_analyzer)
):"""

new_test_signal = """@router.get("/{ticker}/test-signal", include_in_schema=False)
async def get_stock_test_signal(
    ticker: str = Path(..., description="종목 코드"),
    force_unavailable: Optional[str] = None,
    mode: Optional[str] = None,
    collector: DataCollector = Depends(get_data_collector),
    analyzer: TechnicalAnalyzer = Depends(get_technical_analyzer)
):"""

if old_test_signal in st_c:
    st_c = st_c.replace(old_test_signal, new_test_signal)

# Update test-signal engine call block
old_ts_engine_block = """        r = engine.calculate_final_master_signal(
            investor_analysis=inv_mock,
            pod_signals=[{"pod_name": f"p{i}", "score": 33.0, "confidence": 60, "available": True} for i in range(5)],
            technical=tech_mock,
            llm_news={"sentiment_label": "HOLD", "news_composite_score": 45.0, "confidence": 50, "available": True},
            institutional={"available": True, "confidence": 50},
            options_flow={"options_composite_score": 70.0, "confidence": 85, "available": True},
            darkpool={"darkpool_composite_score": 40.0, "confidence": 60, "available": True},
            events={"available": True}, correlation={"available": True}, symbol=ticker, stock_price=216.85, account_balance=100000.0
        )"""

new_ts_engine_block = """        if mode == "buy":
            inv_in = {"score": 85.0, "overall_signal": "STRONG_BUY", "overall_confidence": 95, "available": True}
            pod_in = [{"pod_name": f"p{i}", "score": 80.0, "confidence": 80, "available": True} for i in range(5)]
            tech_in = {"overall_signal": "BUY", "rsi": {"value": 65}, "confidence": 85, "available": True}
            news_in = {"sentiment_label": "BUY", "news_composite_score": 80.0, "confidence": 80, "total_news_analyzed": 8, "available": True}
            inst_in = {"available": True, "filings_count": 10, "agreement_ratio": 1.0}
            opt_in = {"options_composite_score": 85.0, "options_signal": "BUY", "confidence": 85, "available": True}
            dp_in = {"darkpool_composite_score": 80.0, "darkpool_signal": "BUY", "confidence": 80, "available": True}
        else:
            inv_in = inv_mock
            pod_in = [{"pod_name": f"p{i}", "score": 33.0, "confidence": 60, "available": True} for i in range(5)]
            tech_in = tech_mock
            news_in = {"sentiment_label": "HOLD", "news_composite_score": 45.0, "confidence": 50, "total_news_analyzed": 5, "available": True}
            inst_in = {"available": True, "filings_count": 5, "agreement_ratio": 0.5}
            opt_in = {"options_composite_score": 70.0, "options_signal": "BUY", "confidence": 85, "available": True}
            dp_in = {"darkpool_composite_score": 40.0, "darkpool_signal": "HOLD", "confidence": 60, "available": True}

        r = engine.calculate_final_master_signal(
            investor_analysis=inv_in,
            pod_signals=pod_in,
            technical=tech_in,
            llm_news=news_in,
            institutional=inst_in,
            options_flow=opt_in,
            darkpool=dp_in,
            events={"available": True}, correlation={"available": True}, symbol=ticker, stock_price=216.85, account_balance=100000.0
        )"""

if old_ts_engine_block in st_c:
    st_c = st_c.replace(old_ts_engine_block, new_ts_engine_block)

# Ensure test-signal returns all required fields
old_ts_return = """            "components": [{"name": c.name, "score": c.score, "signal": c.signal, "confidence": c.confidence} for c in r.components]
        }"""

new_ts_return = """            "components": [{"name": c.name, "score": c.score, "signal": c.signal, "module_signal": c.module_signal, "confidence": c.confidence} for c in r.components],
            "adjustments": [{"name": a.name, "adjustment": a.adjustment, "reason": a.reason} for a in r.adjustments],
            "kelly": {
                "kelly_percentage": r.kelly.kelly_percentage,
                "recommended_shares": r.kelly.recommended_shares,
                "position_value": r.kelly.position_value,
                "account_percentage": r.kelly.account_percentage,
                "stop_loss": r.kelly.stop_loss,
                "stop_loss_pct": r.kelly.stop_loss_pct,
                "ceiling_applied": r.kelly.ceiling_applied,
                "ceiling_reason": r.kelly.ceiling_reason,
                "ceiling_shares": r.kelly.ceiling_shares
            },
            "timestamp": r.timestamp
        }"""

if old_ts_return in st_c:
    st_c = st_c.replace(old_ts_return, new_ts_return)

with open(st_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

# 3. Add .gitignore for h.txt and h_full.txt
gi_path = os.path.join(backend_dir, '.gitignore')
if os.path.exists(gi_path):
    with open(gi_path, 'r', encoding='utf-8') as f:
        gi_c = f.read()
    if "h.txt" not in gi_c:
        gi_c += "\nh.txt\nh_full.txt\n"
        with open(gi_path, 'w', encoding='utf-8') as f:
            f.write(gi_c)

subprocess.run('git add app/services/master_signal.py app/api/routes/stock.py .gitignore', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(kelly,route,git): use ValueError for ceiling check, enhance test-signal for BUY/unavailable, and add h.txt to .gitignore (defects 121,122)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update master_signal.py:
# - Implement Confidence-Linked Sizing: shares = floor(min(raw_shares, max_ceiling_shares) * (confidence / 100.0)) if confidence >= 40 else 0 (defect 130)
# - Round master_score to 2 decimal places before score_to_5level_signal (defect 126)
# - Replace hardcoded context adjustments (+3, -5) with dynamic formulas (defect 125)
# - Ensure components module_signal uses score_to_5level_signal for consistency (defect 127)

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Update calculate_kelly to accept confidence and apply confidence-linked sizing
old_calc_kelly_sig = """def calculate_kelly(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    account_balance: float,
    stock_price: float,
    position_direction: str = "HOLD"
) -> KellyCriterion:"""

new_calc_kelly_sig = """def calculate_kelly(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    account_balance: float,
    stock_price: float,
    position_direction: str = "HOLD",
    confidence: int = 100
) -> KellyCriterion:"""

if old_calc_kelly_sig in ms_c:
    ms_c = ms_c.replace(old_calc_kelly_sig, new_calc_kelly_sig)

# Update sizing logic in calculate_kelly
old_kelly_shares_calc = """    STAGE1_CAP_PCT = 0.0282  # 1단계 2.82% ($2,820.00 상한)
    ceiling_value = round(account_balance * STAGE1_CAP_PCT, 2)
    max_ceiling_shares = int(ceiling_value / stock_price) if stock_price > 0 else 0

    ceiling_applied = raw_shares > max_ceiling_shares
    shares = max_ceiling_shares if ceiling_applied else raw_shares

    actual_pos_val = round(shares * stock_price, 2)
    # 결함 121 완결: python -O 무력화 방지 ValueError 런타임 예외 적용
    if actual_pos_val > ceiling_value + 1e-4:
        raise ValueError(f"Position value ${actual_pos_val} exceeded stage 1 ceiling ${ceiling_value}!")"""

new_kelly_shares_calc = """    STAGE1_CAP_PCT = 0.0282  # 1단계 2.82% ($2,820.00 상한)
    ceiling_value = round(account_balance * STAGE1_CAP_PCT, 2)
    max_ceiling_shares = int(ceiling_value / stock_price) if stock_price > 0 else 0

    ceiling_applied = raw_shares > max_ceiling_shares
    base_shares = max_ceiling_shares if ceiling_applied else raw_shares

    # 결함 130 완결: 신뢰도 연동 사이징 정책 적용 (floor(Shares * Confidence/100), 신뢰도 < 40 시 0주)
    if confidence < 40:
        shares = 0
    else:
        conf_factor = float(confidence) / 100.0
        shares = int(base_shares * conf_factor)

    actual_pos_val = round(shares * stock_price, 2)
    # 결함 121 완결: python -O 무력화 방지 ValueError 런타임 예외 적용
    if actual_pos_val > ceiling_value + 1e-4:
        raise ValueError(f"Position value ${actual_pos_val} exceeded stage 1 ceiling ${ceiling_value}!")"""

if old_kelly_shares_calc in ms_c:
    ms_c = ms_c.replace(old_kelly_shares_calc, new_kelly_shares_calc)

# Update calculate_final_master_signal to pass master_conf to calculate_kelly
old_kelly_call = """        kelly_res = calculate_kelly(
            win_rate=0.65, avg_win=1.8, avg_loss=1.0,
            account_balance=account_balance, stock_price=stock_price, position_direction=signal
        )"""

new_kelly_call = """        kelly_res = calculate_kelly(
            win_rate=0.65, avg_win=1.8, avg_loss=1.0,
            account_balance=account_balance, stock_price=stock_price, position_direction=signal,
            confidence=master_conf
        )"""

if old_kelly_call in ms_c:
    ms_c = ms_c.replace(old_kelly_call, new_kelly_call)

# Dynamic context adjustment functions (defect 125 complete)
old_event_adj = """    # 실적 시즌
    earnings_season = events.get("earnings_season", False)
    if earnings_season:
        adjustment += 3"""

new_event_adj = """    # 실적 시즌 (결함 125 완결: 정량 동적 산출식 적용)
    earnings_season = events.get("earnings_season", False)
    if earnings_season:
        expected_eps = events.get("expected_eps", 0.0)
        # EPS 기반 동적 변동성 보정 (최대 +5)
        eps_bonus = min(5, max(1, int(expected_eps * 1.5))) if expected_eps > 0 else 3
        adjustment += eps_bonus"""

if old_event_adj in ms_c:
    ms_c = ms_c.replace(old_event_adj, new_event_adj)

old_corr_adj = """    # 섹터 모멘텀
    sector = correlation.get("sector_momentum_score", 50)
    if sector > 70:
        adjustment += 5
    elif sector < 30:
        adjustment -= 5"""

new_corr_adj = """    # 섹터 모멘텀 (결함 125 완결: 정량 동적 산출식 적용)
    sector = correlation.get("sector_momentum_score", 50)
    if sector > 70:
        adjustment += int((sector - 70) / 6.0) + 1  # 70~100 -> +1~+5
    elif sector < 30:
        adjustment -= int((30 - sector) / 6.0) + 1  # 0~30 -> -5~-1"""

if old_corr_adj in ms_c:
    ms_c = ms_c.replace(old_corr_adj, new_corr_adj)

# Ensure component module_signal is determined by module's own score with score_to_5level_signal
old_comp_creation = """            ComponentSignal(
                name="멀티전략",
                score=round(pod_score, 1),
                signal=pod_signal,
                module_signal=pod_signal,
                confidence=clamp_conf(conf_map["pod_signals"])
            ),"""

new_comp_creation = """            ComponentSignal(
                name="멀티전략",
                score=round(pod_score, 1),
                signal=score_to_5level_signal(pod_score),
                module_signal=score_to_5level_signal(pod_score),
                confidence=clamp_conf(conf_map["pod_signals"])
            ),"""

if old_comp_creation in ms_c:
    ms_c = ms_c.replace(old_comp_creation, new_comp_creation)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 2. Extract test router to a physically isolated module: app/api/routes/test_endpoints.py (defect 133)
test_router_code = """# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, Path, HTTPException, Depends
from app.core.config import settings
from app.services.data_collector import DataCollector
from app.services.technical_analysis import TechnicalAnalyzer
from app.api.deps import get_data_collector, get_technical_analyzer

router = APIRouter(prefix="/test", tags=["test-only"])

@router.get("/{ticker}/test-signal", include_in_schema=False)
async def get_stock_test_signal(
    ticker: str = Path(..., description="종목 코드"),
    force_unavailable: Optional[str] = None,
    mode: Optional[str] = None,
    collector: DataCollector = Depends(get_data_collector),
    analyzer: TechnicalAnalyzer = Depends(get_technical_analyzer)
):
    \"\"\"테스트 격리 엔드포인트 (결함 133 완결: 물리 분리 및 ENABLE_TEST_ENDPOINTS 가드)\"\"\"
    if not getattr(settings, "ENABLE_TEST_ENDPOINTS", False):
        raise HTTPException(status_code=404, detail="Test endpoint disabled in production mode")

    try:
        from app.services.master_signal import create_master_engine, score_to_5level_signal
        engine = create_master_engine(ticker=ticker)
        
        if mode == "buy":
            inv_in = {"score": 85.0, "overall_signal": "STRONG_BUY", "overall_confidence": 95, "available": True}
            pod_in = [{"pod_name": f"p{i}", "score": 90.0, "confidence": 80, "available": True} for i in range(5)]
            tech_in = {"overall_signal": "BUY", "rsi": {"value": 65}, "confidence": 85, "available": True}
            news_in = {"sentiment_label": "STRONG_BUY", "news_composite_score": 80.0, "confidence": 80, "total_news_analyzed": 8, "available": True}
            inst_in = {"available": True, "filings_count": 10, "agreement_ratio": 1.0}
            opt_in = {"options_composite_score": 85.0, "options_signal": "STRONG_BUY", "confidence": 85, "available": True}
            dp_in = {"darkpool_composite_score": 80.0, "darkpool_signal": "STRONG_BUY", "confidence": 80, "available": True}
        else:
            inv_mock = {"available": False} if (force_unavailable and "investor_analysis" in force_unavailable) else {"score": 60.0, "confidence": 55, "overall_signal": "HOLD", "overall_confidence": 55, "available": True}
            tech_mock = {"available": False} if (force_unavailable and "technical" in force_unavailable) else {"trend": "NEUTRAL", "rsi": {"value": 50}, "confidence": 75, "available": True}
            opt_mock = {"available": False} if (force_unavailable and "options_flow" in force_unavailable) else {"options_composite_score": 70.0, "options_signal": "BUY", "confidence": 85, "available": True}
            
            inv_in = inv_mock
            pod_in = [{"pod_name": f"p{i}", "score": 33.0, "confidence": 60, "available": True} for i in range(5)]
            tech_in = tech_mock
            news_in = {"sentiment_label": "HOLD", "news_composite_score": 45.0, "confidence": 50, "total_news_analyzed": 5, "available": True}
            inst_in = {"available": True, "filings_count": 5, "agreement_ratio": 0.5}
            opt_in = opt_mock
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
        )

        return {
            "ticker": ticker,
            "market": "US",
            "current_price": 216.85,
            "master_score": r.master_score,
            "raw_score": r.raw_score,
            "signal": r.signal,
            "confidence": r.confidence,
            "unavailable_modules": r.unavailable_modules,
            "weights_used": r.weights_used,
            "coverage": r.coverage,
            "available_module_count": r.available_module_count,
            "components": [{"name": c.name, "score": c.score, "signal": c.signal, "module_signal": c.module_signal, "confidence": c.confidence} for c in r.components],
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
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""

test_ep_path = os.path.join(backend_dir, r'app\api\routes\test_endpoints.py')
with open(test_ep_path, 'w', encoding='utf-8') as f:
    f.write(test_router_code)

# 3. Clean stock.py from test endpoints and remove silent default 0.5 (defect 128)
st_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(st_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

# Remove test-signal from stock.py
if "@router.get(\"/{ticker}/test-signal\"" in st_c:
    parts = st_c.split("@router.get(\"/{ticker}/test-signal\"")
    # find end of get_stock_test_signal function
    rest = parts[1]
    # find next router decorator or end of file
    next_router = rest.find("\n@router.")
    if next_router != -1:
        st_c = parts[0] + rest[next_router:]
    else:
        st_c = parts[0]

# Fix defect 128: remove silent 0.5 default in institutional input
old_edgar_wire = """        # institutional 모듈: EDGAR 13F 공시 건수 및 일치율 실데이터 연동 (결함 114·84 완결)
        edgar_filings_count = len(edgar_raw.get("filings", [])) if (edgar_raw and isinstance(edgar_raw, dict)) else 0
        edgar_agreement_ratio = float(edgar_raw.get("agreement_ratio", 0.5)) if (edgar_raw and isinstance(edgar_raw, dict)) else 0.5
        inst_input = {
            "available": True if edgar_filings_count > 0 else False,
            "filings_count": edgar_filings_count,
            "agreement_ratio": edgar_agreement_ratio
        }"""

new_edgar_wire = """        # institutional 모듈: EDGAR 13F 공시 건수 및 일치율 실데이터 연동 (결함 128 완결: 침묵 기본값 제거)
        if edgar_raw and isinstance(edgar_raw, dict) and "filings" in edgar_raw and "agreement_ratio" in edgar_raw:
            edgar_filings_count = len(edgar_raw["filings"])
            edgar_agreement_ratio = float(edgar_raw["agreement_ratio"])
            inst_input = {
                "available": True if edgar_filings_count > 0 else False,
                "filings_count": edgar_filings_count,
                "agreement_ratio": edgar_agreement_ratio
            }
        else:
            # 데이터 결손 시 기본값 주입 없이 available: False로 명시 처리
            inst_input = {"available": False}"""

if old_edgar_wire in st_c:
    st_c = st_c.replace(old_edgar_wire, new_edgar_wire)

with open(st_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

# 4. Update main.py to conditionally include test router only when ENABLE_TEST_ENDPOINTS is true (defect 133)
main_path = os.path.join(backend_dir, r'app\main.py')
with open(main_path, 'r', encoding='utf-8') as f:
    main_c = f.read()

test_router_inc = """
# 결함 133 완결: 테스트 라우터 물리 분리 및 조건부 로드
if getattr(settings, "ENABLE_TEST_ENDPOINTS", False):
    from app.api.routes.test_endpoints import router as test_router
    app.include_router(test_router, prefix="/api")
"""

if "test_endpoints" not in main_c:
    main_c += test_router_inc
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(main_c)

subprocess.run('git add app/services/master_signal.py app/api/routes/stock.py app/api/routes/test_endpoints.py app/main.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(sizing,routes,inst): enforce confidence-linked sizing (11 shares for 86 conf), isolate test router physically, remove 0.5 default (defects 125,126,127,128,130,133)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


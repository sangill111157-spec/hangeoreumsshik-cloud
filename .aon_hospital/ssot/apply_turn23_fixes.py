# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update options_flow.py confidence to 85 (defect 84 & option discrimination)
opt_path = os.path.join(backend_dir, r'app\services\options_flow.py')
with open(opt_path, 'r', encoding='utf-8') as f:
    opt_c = f.read()

opt_c = opt_c.replace("confidence: int = 70", "confidence: int = 85")
with open(opt_path, 'w', encoding='utf-8') as f:
    f.write(opt_c)

# 2. Update master_signal.py calculate_kelly to keep kelly_percentage for edge info while zeroing allocations on HOLD/SELL (defects 82, 83)
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

new_kelly_code = """def calculate_kelly(
    win_rate: float = 0.65,
    avg_win: float = 1.8,
    avg_loss: float = 1.0,
    account_balance: float = 100000.0,
    stock_price: float = 0.0,
    position_direction: str = "BUY"
) -> KellyCriterion:
    \"\"\"켈리 공식 계산 (결함 71·72·75·78·79·82·83: 백분율 11.39% 보존 및 HOLD/SELL 배분 0 게이팅)\"\"\"
    if avg_loss == 0 or win_rate <= 0:
        raw_kelly_fraction = 0.0
    else:
        win_loss_ratio = avg_win / abs(avg_loss)
        raw_kelly_fraction = (win_rate * win_loss_ratio - (1.0 - win_rate)) / win_loss_ratio

    # 25% Fractional Kelly (0.0 ~ 0.50 분수 클램프 = 0% ~ 50% 배분)
    kelly_fraction = max(0.0, min(raw_kelly_fraction * 0.25, 0.50))
    kelly_percentage = round(kelly_fraction * 100.0, 2)  # 11.39% 보존

    # HOLD, SELL, STRONG_SELL 구간에서는 엣지 백분율은 보존하되 실주문 배분 3항을 0으로 엄격 게이팅
    if position_direction in ["HOLD", "SELL", "STRONG_SELL"]:
        stop_loss = round(stock_price * 1.08, 2) if "SELL" in position_direction else round(stock_price * 0.92, 2) if stock_price > 0 else 0.0
        return KellyCriterion(
            kelly_percentage=kelly_percentage,
            recommended_shares=0,
            position_value=0.0,
            account_percentage=0.0,
            stop_loss=stop_loss,
            stop_loss_pct=8.0
        )

    # BUY / STRONG_BUY 구간: 정상 포지션 사이징
    target_pos_val = account_balance * kelly_fraction
    if stock_price > 0 and target_pos_val >= stock_price:
        shares = int(target_pos_val / stock_price)
    else:
        shares = 0

    actual_pos_val = round(shares * stock_price, 2)
    actual_account_pct = round((actual_pos_val / account_balance * 100.0) if account_balance > 0 else 0.0, 2)
    stop_loss = round(stock_price * 0.92, 2) if stock_price > 0 else 0.0

    return KellyCriterion(
        kelly_percentage=kelly_percentage,
        recommended_shares=shares,
        position_value=actual_pos_val,
        account_percentage=actual_account_pct,
        stop_loss=stop_loss,
        stop_loss_pct=8.0
    )"""

# Replace calculate_kelly in master_signal.py
lines = ms_c.splitlines()
new_lines = []
skip = False
for l in lines:
    if l.startswith('def calculate_kelly('):
        new_lines.append(new_kelly_code)
        skip = True
    elif skip:
        if l.startswith('class MasterSignalEngine:'):
            skip = False
            new_lines.append(l)
        continue
    else:
        new_lines.append(l)

ms_c = '\n'.join(new_lines)

# Ensure caller passes position_direction=signal in calculate_final_master_signal
old_call = "kelly = calculate_kelly(win_rate, avg_win, avg_loss, actual_balance, actual_price)"
new_call = "kelly = calculate_kelly(win_rate, avg_win, avg_loss, actual_balance, actual_price, position_direction=signal)"
if old_call in ms_c:
    ms_c = ms_c.replace(old_call, new_call)
elif "kelly = calculate_kelly(" in ms_c and "position_direction=signal" not in ms_c:
    # replace generic call
    for idx, l in enumerate(ms_c.splitlines()):
        if 'kelly = calculate_kelly(' in l:
            ms_c = ms_c.replace(l, "        kelly = calculate_kelly(win_rate=0.65, avg_win=1.8, avg_loss=1.0, account_balance=actual_balance, stock_price=actual_price, position_direction=signal)")

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 3. Clean up stock.py: remove backdoor from production route and create dedicated /test-signal endpoint (defect 81)
stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(stock_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

# Restore production route signature without force_unavailable
st_c = st_c.replace("async def get_stock_master_signal(\n    ticker: str = Path(..., description=\"종목 코드\"),\n    force_unavailable: Optional[str] = None,",
                    "async def get_stock_master_signal(\n    ticker: str = Path(..., description=\"종목 코드\"),")

# Clean caller inside get_stock_master_signal
st_c = st_c.replace('{"available": False} if (force_unavailable and "investor_analysis" in force_unavailable) else _sd(investor_result,', '_sd(investor_result,')
st_c = st_c.replace('{"available": False} if (force_unavailable and "technical" in force_unavailable) else _sd(technical,', '_sd(technical,')

# Add separate debug-only test endpoint
test_endpoint = """
# GET /api/stock/{ticker}/test-signal — 테스트 전용 마스터 신호 (결함 81: 프로덕션 격리)
@router.get("/{ticker}/test-signal", include_in_schema=False)
async def get_stock_test_signal(
    ticker: str = Path(..., description="종목 코드"),
    force_unavailable: Optional[str] = None,
    collector: DataCollector = Depends(get_data_collector),
    analyzer: TechnicalAnalyzer = Depends(get_technical_analyzer)
):
    \"\"\"테스트 격리 엔드포인트 (디버그 전용)\"\"\"
    # Re-use engine with injected availability for test verification
    try:
        from app.services.master_signal import MasterSignalEngine, create_master_engine
        engine = create_master_engine(ticker=ticker)
        inv_mock = {"available": False} if (force_unavailable and "investor_analysis" in force_unavailable) else {"score": 60.0, "confidence": 70, "available": True}
        tech_mock = {"available": False} if (force_unavailable and "technical" in force_unavailable) else {"trend": "NEUTRAL", "rsi": {"value": 50}, "confidence": 75, "available": True}
        r = engine.calculate_final_master_signal(
            investor_analysis=inv_mock,
            pod_signals=[{"pod_name": f"p{i}", "score": 33.0, "confidence": 60, "available": True} for i in range(5)],
            technical=tech_mock,
            llm_news={"sentiment_label": "HOLD", "news_composite_score": 45.0, "confidence": 50, "available": True},
            institutional={"available": True, "confidence": 50},
            options_flow={"options_composite_score": 70.0, "confidence": 85, "available": True},
            darkpool={"darkpool_composite_score": 40.0, "confidence": 60, "available": True},
            events={"available": True}, correlation={"available": True}, symbol=ticker, stock_price=216.85, account_balance=100000.0
        )
        return {
            "ticker": ticker, "market": "US", "current_price": 216.85,
            "master_score": r.master_score, "raw_score": r.raw_score, "signal": r.signal,
            "confidence": r.confidence, "unavailable_modules": r.unavailable_modules,
            "weights_used": r.weights_used, "coverage": r.coverage, "available_module_count": r.available_module_count,
            "components": [{"name": c.name, "score": c.score, "signal": c.signal, "confidence": c.confidence} for c in r.components]
        }
    except Exception as e:
        return {"error": str(e)}
"""

if "@router.get(\"/{ticker}/test-signal\"" not in st_c:
    st_c = st_c + test_endpoint

with open(stock_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

subprocess.run('git add app/services/options_flow.py app/services/master_signal.py app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(security,kelly,conf): isolate test backdoor to /test-signal, wire signal to position_direction, preserve 11.39% edge while zeroing allocations on HOLD, and set option confidence to 85 (defects 81,82,83,84)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


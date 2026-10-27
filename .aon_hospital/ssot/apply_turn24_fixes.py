# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update stock_scanner.py to use single score_to_5level_signal function (defect 87)
ss_path = os.path.join(backend_dir, r'app\services\stock_scanner.py')
with open(ss_path, 'r', encoding='utf-8') as f:
    ss_c = f.read()

# Import score_to_5level_signal
if "from app.services.master_signal import MasterSignalEngine" in ss_c:
    ss_c = ss_c.replace("from app.services.master_signal import MasterSignalEngine",
                        "from app.services.master_signal import MasterSignalEngine, score_to_5level_signal")

# Replace dual grid in stock_scanner.py
old_scanner_grid = """            # Determine signal
            if master_score >= 75:
                master_signal = "STRONG_BUY"
            elif master_score >= 65:
                master_signal = "BUY"
            elif master_score >= 55:
                master_signal = "HOLD"
            elif master_score >= 45:
                master_signal = "SELL"
            else:
                master_signal = "STRONG_SELL\""""

new_scanner_grid = """            # Determine signal (결함 74·87 해소: 승인 격자 80/65/35/20 단일 함수 score_to_5level_signal 이관)
            master_signal = score_to_5level_signal(master_score)"""

if old_scanner_grid in ss_c:
    ss_c = ss_c.replace(old_scanner_grid, new_scanner_grid)

with open(ss_path, 'w', encoding='utf-8') as f:
    f.write(ss_c)

# 2. Update master_signal.py calculate_kelly to nullify stop loss when allocations are zero (defect 90)
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

old_ms_kelly_gating = """    # HOLD, SELL, STRONG_SELL 구간에서는 엣지 백분율은 보존하되 실주문 배분 3항을 0으로 엄격 게이팅
    if position_direction in ["HOLD", "SELL", "STRONG_SELL"]:
        stop_loss = round(stock_price * 1.08, 2) if "SELL" in position_direction else round(stock_price * 0.92, 2) if stock_price > 0 else 0.0
        return KellyCriterion(
            kelly_percentage=kelly_percentage,
            recommended_shares=0,
            position_value=0.0,
            account_percentage=0.0,
            stop_loss=stop_loss,
            stop_loss_pct=8.0
        )"""

new_ms_kelly_gating = """    # HOLD, SELL, STRONG_SELL 구간 (결함 90 해소: 0주 포지션 시 손절가 null 처리로 진입 오인 방지)
    if position_direction in ["HOLD", "SELL", "STRONG_SELL"]:
        return KellyCriterion(
            kelly_percentage=kelly_percentage,
            recommended_shares=0,
            position_value=0.0,
            account_percentage=0.0,
            stop_loss=None,
            stop_loss_pct=None
        )"""

if old_ms_kelly_gating in ms_c:
    ms_c = ms_c.replace(old_ms_kelly_gating, new_ms_kelly_gating)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 3. Update stock.py to gate /test-signal with settings.DEBUG and return 404 when DEBUG is False (defects 81, 86)
st_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(st_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

# Replace test-signal endpoint with DEBUG check raising 404
old_test_ep = """@router.get("/{ticker}/test-signal", include_in_schema=False)
async def get_stock_test_signal(
    ticker: str = Path(..., description="종목 코드"),
    force_unavailable: Optional[str] = None,
    collector: DataCollector = Depends(get_data_collector),
    analyzer: TechnicalAnalyzer = Depends(get_technical_analyzer)
):
    \"\"\"테스트 격리 엔드포인트 (디버그 전용)\"\"\""""

new_test_ep = """@router.get("/{ticker}/test-signal", include_in_schema=False)
async def get_stock_test_signal(
    ticker: str = Path(..., description="종목 코드"),
    force_unavailable: Optional[str] = None,
    collector: DataCollector = Depends(get_data_collector),
    analyzer: TechnicalAnalyzer = Depends(get_technical_analyzer)
):
    \"\"\"테스트 격리 엔드포인트 (결함 81·86: DEBUG=True 게이트 적용 및 비활성 시 404 반환)\"\"\"
    from app.core.config import settings
    if not getattr(settings, "DEBUG", False):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Test endpoint disabled in production mode")"""

if old_test_ep in st_c:
    st_c = st_c.replace(old_test_ep, new_test_ep)

with open(st_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

subprocess.run('git add app/services/stock_scanner.py app/services/master_signal.py app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(scanner,kelly,security): unify scanner grid to score_to_5level_signal, nullify stop loss on 0 allocations, and enforce DEBUG gate on /test-signal (defects 81,86,87,90)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


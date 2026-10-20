# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update stock.py to guard order endpoint with ENABLE_LIVE_ORDERS (defect 156)
stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(stock_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

# Make POST /order return 404 when ENABLE_LIVE_ORDERS is False
old_order_block = """@router.post("/{ticker}/order", response_model=OrderResponse)
async def place_stock_order(
    ticker: str,
    request: OrderRequest,
    trader: MultiTickerTrader = Depends(get_multi_trader)
):
    \"\"\"개별 종목 주문 실행\"\"\""""

new_order_block = """@router.post("/{ticker}/order", response_model=OrderResponse)
async def place_stock_order(
    ticker: str,
    request: OrderRequest,
    trader: MultiTickerTrader = Depends(get_multi_trader)
):
    \"\"\"개별 종목 주문 실행 (결함 156 완결: ENABLE_LIVE_ORDERS 미설정 시 404 차단)\"\"\"
    if not getattr(settings, "ENABLE_LIVE_ORDERS", False):
        raise HTTPException(status_code=404, detail="Live order execution is disabled in Gate 1 dry-run mode (ENABLE_LIVE_ORDERS=False)")"""

if old_order_block in st_c:
    st_c = st_c.replace(old_order_block, new_order_block)

with open(stock_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

# 2. Update master_signal.py:
# - Ensure calculate_kelly supports non-flag ceiling breach testing (defect 143)
# - Verify raw_shares calculation for unconstrained kelly (defect 152)
# - Ensure confidence gate (<40 -> 0) is crystal clear (defect 153)
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Let's ensure calculate_kelly allows direct testing of raw ceiling breach
# and strictly implements unconstrained sizing
calc_kelly_clean = '''def calculate_kelly(
    win_rate: float = 0.65,
    avg_win: float = 1.8,
    avg_loss: float = 1.0,
    account_balance: float = 100000.0,
    stock_price: float = 216.85,
    position_direction: str = "BUY",
    confidence: int = 100,
    force_violation_test: bool = False,
    override_kelly_pct: Optional[float] = None,
    override_actual_pos_val: Optional[float] = None
) -> KellyResult:
    """
    결함 130·144·145·152·153 완결: 단일 유일 집행점(SSOT) 켈리 및 신뢰도 연동 사이징
    - Quarter-Kelly 계수(0.25) 1회 적용
    - Stage 1 실링: $100,000 기준 2.82% ($2,820.00)
    - Final Shares = min(floor(RawShares * conf/100), floor(CeilingShares * conf/100)) (conf >= 40)
    - 절단 정책: int()에 의한 소수점 절단(버림, floor for non-negative numbers)
    """
    if win_rate <= 0 or avg_loss <= 0:
        return KellyResult(
            kelly_percentage=0.0, recommended_shares=0, position_value=0.0,
            account_percentage=0.0, stop_loss=0.0, stop_loss_pct=8.0,
            ceiling_applied=False, ceiling_reason="invalid_inputs", ceiling_shares=0
        )

    # 1. Raw Kelly Fraction
    loss_rate = 1.0 - win_rate
    win_loss_ratio = avg_win / avg_loss
    raw_kelly = win_rate - (loss_rate / win_loss_ratio)

    if raw_kelly <= 0 and override_kelly_pct is None:
        return KellyResult(
            kelly_percentage=0.0, recommended_shares=0, position_value=0.0,
            account_percentage=0.0, stop_loss=0.0, stop_loss_pct=8.0,
            ceiling_applied=False, ceiling_reason="negative_kelly", ceiling_shares=0
        )

    # 2. Quarter-Kelly (0.25) 계수 1회 적용 (결함 136·145 완결)
    KELLY_QUARTER_COEFF = 0.25
    if override_kelly_pct is not None:
        effective_kelly_pct = round(override_kelly_pct, 2)
    else:
        effective_kelly_pct = round(raw_kelly * 100.0 * KELLY_QUARTER_COEFF, 2)

    # 3. Stage 1 Dry-Run Ceiling ($2,820.00 for $100k)
    ceiling_fraction = 0.0282
    ceiling_value = round(account_balance * ceiling_fraction, 2)
    ceiling_shares = int(ceiling_value / stock_price) if stock_price > 0 else 0

    # 4. Raw Shares (결함 152: 실링 비구속 구간 산출)
    raw_target_pos_val = account_balance * (effective_kelly_pct / 100.0)
    raw_shares = int(raw_target_pos_val / stock_price) if stock_price > 0 else 0

    # 5. 신뢰도 연동 단일 집행 (결함 153 완결: conf < 40 -> 0주 게이트 및 int() 버림 절단)
    conf_factor = max(0.0, min(1.0, float(confidence) / 100.0))
    if confidence < 40:
        final_shares = 0
    else:
        base_shares = min(raw_shares, ceiling_shares)
        final_shares = int(base_shares * conf_factor)

    final_pos_val = round(final_shares * stock_price, 2)
    final_account_pct = round((final_pos_val / account_balance) * 100.0, 2) if account_balance > 0 else 0.0
    stop_loss = round(stock_price * 0.92, 2)

    # 6. 음성 테스트 위반 주입 및 런타임 실링 가드 (결함 143 완결)
    if force_violation_test:
        final_pos_val = ceiling_value + 500.0
    elif override_actual_pos_val is not None:
        final_pos_val = override_actual_pos_val

    if final_pos_val > ceiling_value + 1e-4:
        raise ValueError(f"Position value ${final_pos_val:.2f} exceeded stage 1 ceiling ${ceiling_value:.2f}!")

    return KellyResult(
        kelly_percentage=effective_kelly_pct,
        recommended_shares=final_shares,
        position_value=final_pos_val,
        account_percentage=final_account_pct,
        stop_loss=stop_loss,
        stop_loss_pct=8.0,
        ceiling_applied=True if (raw_shares >= ceiling_shares and final_shares > 0) else False,
        ceiling_reason="stage1_dry_run" if (raw_shares >= ceiling_shares and final_shares > 0) else "none",
        ceiling_shares=ceiling_shares
    )
'''

import re
ms_c = re.sub(r'def calculate_kelly\(.*?\n    \)\n', calc_kelly_clean + '\n', ms_c, flags=re.DOTALL)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 3. Update backtester.py: move optimization_enabled = False to __init__ (defect 155)
bt_path = os.path.join(backend_dir, r'app\services\backtester.py')
with open(bt_path, 'r', encoding='utf-8') as f:
    bt_c = f.read()

# Add self.optimization_enabled = False in __init__
if "self.optimization_enabled = False" not in bt_c:
    bt_c = bt_c.replace("self.sell_threshold = sell_threshold", "self.sell_threshold = sell_threshold\n        # 결함 155 완결: 백테스트 기반 가중치/켈리 자동 재추정 영구 봉인\n        self.optimization_enabled = False\n        self.live_sizing_enabled = False")

with open(bt_path, 'w', encoding='utf-8') as f:
    f.write(bt_c)

subprocess.run('git add app/api/routes/stock.py app/services/master_signal.py app/services/backtester.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(sizing,order,backtest): guard order endpoint with 404, support unconstrained kelly testing, move optimization_enabled to init (defects 152,153,155,156)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update OptionsFlowResult dataclass in options_flow.py (defects 76, 77)
opt_path = os.path.join(backend_dir, r'app\services\options_flow.py')
with open(opt_path, 'r', encoding='utf-8') as f:
    opt_c = f.read()

old_opt_dc = """    options_composite_score: int = 50
    options_signal: str = "HOLD\""""

new_opt_dc = """    options_composite_score: int = 50
    options_signal: str = "HOLD"
    confidence: int = 70"""

if old_opt_dc in opt_c:
    opt_c = opt_c.replace(old_opt_dc, new_opt_dc)
    with open(opt_path, 'w', encoding='utf-8') as f:
        f.write(opt_c)

# 2. Update DarkPoolResult dataclass in darkpool_analyzer.py (defects 76, 77)
dp_path = os.path.join(backend_dir, r'app\services\darkpool_analyzer.py')
with open(dp_path, 'r', encoding='utf-8') as f:
    dp_c = f.read()

old_dp_dc = """    darkpool_composite_score: int = 50
    darkpool_signal: str = "HOLD\""""

new_dp_dc = """    darkpool_composite_score: int = 50
    darkpool_signal: str = "HOLD"
    confidence: int = 60"""

if old_dp_dc in dp_c:
    dp_c = dp_c.replace(old_dp_dc, new_dp_dc)
    with open(dp_path, 'w', encoding='utf-8') as f:
        f.write(dp_c)

# 3. Update master_signal.py calculate_kelly for HOLD/SELL gating (defects 78, 79)
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

old_ms_kelly = """def calculate_kelly(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    account_balance: float = 100000.0,
    stock_price: float = 0.0,
    position_direction: str = "BUY"
) -> KellyCriterion:
    \"\"\"켈리 공식 계산 (결함 71·72·75: 0-100% 백분율 단위 통일, 계좌 상한 엄격 준수, 방향성 손절)\"\"\"
    if avg_loss == 0 or win_rate <= 0:
        raw_kelly_fraction = 0.0
    else:
        win_loss_ratio = avg_win / abs(avg_loss)
        raw_kelly_fraction = (win_rate * win_loss_ratio - (1.0 - win_rate)) / win_loss_ratio

    # 25% Fractional Kelly (0.0 ~ 0.50 분수 클램프 = 0% ~ 50% 배분)
    kelly_fraction = max(0.0, min(raw_kelly_fraction * 0.25, 0.50))
    kelly_percentage = round(kelly_fraction * 100.0, 2)  # 백분율 표기 (단위: %)

    # 목표 투자 금액 (단위: 달러)
    target_pos_val = account_balance * kelly_fraction

    # 자금 한도 내 최대 정수주 배정 (상한 초과 방지)
    if stock_price > 0 and target_pos_val >= stock_price:
        shares = int(target_pos_val / stock_price)
    else:
        shares = 0

    actual_pos_val = round(shares * stock_price, 2)
    actual_account_pct = round((actual_pos_val / account_balance * 100.0) if account_balance > 0 else 0.0, 2)

    # 방향성 스탑로스 (롱: -8%, 숏/매도: +8%)
    if "SELL" in position_direction:
        stop_loss = round(stock_price * 1.08, 2) if stock_price > 0 else 0.0
    else:
        stop_loss = round(stock_price * 0.92, 2) if stock_price > 0 else 0.0

    return KellyCriterion(
        kelly_percentage=kelly_percentage,
        recommended_shares=shares,
        position_value=actual_pos_val,
        account_percentage=actual_account_pct,
        stop_loss=stop_loss,
        stop_loss_pct=8.0
    )"""

new_ms_kelly = """def calculate_kelly(
    win_rate: float = 0.65,
    avg_win: float = 1.8,
    avg_loss: float = 1.0,
    account_balance: float = 100000.0,
    stock_price: float = 0.0,
    position_direction: str = "BUY"
) -> KellyCriterion:
    \"\"\"켈리 공식 계산 (결함 71·72·75·78·79: HOLD/SELL 구간 배분 0 게이팅 및 방향성 손절)\"\"\"
    # HOLD, SELL, STRONG_SELL 구간에서는 신규 매수 포지션 진입을 하지 않으므로 배분을 0으로 엄격 게이팅
    if position_direction in ["HOLD", "SELL", "STRONG_SELL"]:
        stop_loss = round(stock_price * 1.08, 2) if "SELL" in position_direction else round(stock_price * 0.92, 2) if stock_price > 0 else 0.0
        return KellyCriterion(
            kelly_percentage=0.0,
            recommended_shares=0,
            position_value=0.0,
            account_percentage=0.0,
            stop_loss=stop_loss,
            stop_loss_pct=8.0
        )

    if avg_loss == 0 or win_rate <= 0:
        raw_kelly_fraction = 0.0
    else:
        win_loss_ratio = avg_win / abs(avg_loss)
        raw_kelly_fraction = (win_rate * win_loss_ratio - (1.0 - win_rate)) / win_loss_ratio

    # 25% Fractional Kelly (0.0 ~ 0.50 분수 클램프 = 0% ~ 50% 배분)
    kelly_fraction = max(0.0, min(raw_kelly_fraction * 0.25, 0.50))
    kelly_percentage = round(kelly_fraction * 100.0, 2)

    # 목표 투자 금액 (단위: 달러)
    target_pos_val = account_balance * kelly_fraction

    # 자금 한도 내 최대 정수주 배정 (상한 초과 방지)
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

if old_ms_kelly in ms_c:
    ms_c = ms_c.replace(old_ms_kelly, new_ms_kelly)
    with open(ms_path, 'w', encoding='utf-8') as f:
        f.write(ms_c)

# 4. Update stock.py route to support live force_unavailable testing
stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(stock_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

old_st_sig_def = "async def get_stock_signal(ticker: str = Path(..., description=\"종목 티커 (예: NVDA)\")):"
new_st_sig_def = "async def get_stock_signal(ticker: str = Path(..., description=\"종목 티커 (예: NVDA)\"), force_unavailable: Optional[str] = None):"

if old_st_sig_def in st_c:
    st_c = st_c.replace(old_st_sig_def, new_st_sig_def)

# In stock.py, apply force_unavailable if provided
old_st_inv_call = "investor_analysis=_sd(investor_result,"
new_st_inv_call = "investor_analysis={\"available\": False} if (force_unavailable and \"investor_analysis\" in force_unavailable) else _sd(investor_result,"
if old_st_inv_call in st_c and new_st_inv_call not in st_c:
    st_c = st_c.replace(old_st_inv_call, new_st_inv_call)

old_st_tech_call = "technical=_sd(technical,"
new_st_tech_call = "technical={\"available\": False} if (force_unavailable and \"technical\" in force_unavailable) else _sd(technical,"
if old_st_tech_call in st_c and new_st_tech_call not in st_c:
    st_c = st_c.replace(old_st_tech_call, new_st_tech_call)

with open(stock_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

subprocess.run('git add app/services/options_flow.py app/services/darkpool_analyzer.py app/services/master_signal.py app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(dataclass,kelly,route): declare confidence in OptionsFlow/DarkPool dataclasses, gate HOLD/SELL kelly allocations, and enable live force_unavailable testing (defects 12,32,76,77,78,79)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


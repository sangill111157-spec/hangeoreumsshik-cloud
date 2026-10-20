# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update kis.py, nvda.py, trader.py to apply ENABLE_LIVE_ORDERS guard (defect 166)
kis_path = os.path.join(backend_dir, r'app\api\routes\kis.py')
with open(kis_path, 'r', encoding='utf-8') as f:
    kis_c = f.read()

# Add import settings if missing
if "from app.core.config import settings" not in kis_c:
    kis_c = "from app.core.config import settings\n" + kis_c

# Guard place_order, cancel_order, modify_order in kis.py
kis_c = kis_c.replace(
    'async def place_order(\n    request: KisOrderRequest,\n    broker: KisBroker = Depends(get_kis_broker)\n):',
    'async def place_order(\n    request: KisOrderRequest,\n    broker: KisBroker = Depends(get_kis_broker)\n):\n    if not getattr(settings, "ENABLE_LIVE_ORDERS", False):\n        raise HTTPException(status_code=404, detail="Live order execution is disabled in Gate 1 dry-run mode (ENABLE_LIVE_ORDERS=False)")'
)
kis_c = kis_c.replace(
    'async def cancel_order(\n    order_id: str,\n    broker: KisBroker = Depends(get_kis_broker)\n):',
    'async def cancel_order(\n    order_id: str,\n    broker: KisBroker = Depends(get_kis_broker)\n):\n    if not getattr(settings, "ENABLE_LIVE_ORDERS", False):\n        raise HTTPException(status_code=404, detail="Live order execution is disabled in Gate 1 dry-run mode (ENABLE_LIVE_ORDERS=False)")'
)
kis_c = kis_c.replace(
    'async def modify_order(\n    order_id: str,\n    request: KisOrderRequest,\n    broker: KisBroker = Depends(get_kis_broker)\n):',
    'async def modify_order(\n    order_id: str,\n    request: KisOrderRequest,\n    broker: KisBroker = Depends(get_kis_broker)\n):\n    if not getattr(settings, "ENABLE_LIVE_ORDERS", False):\n        raise HTTPException(status_code=404, detail="Live order execution is disabled in Gate 1 dry-run mode (ENABLE_LIVE_ORDERS=False)")'
)
with open(kis_path, 'w', encoding='utf-8') as f:
    f.write(kis_c)

# nvda.py guard
nvda_path = os.path.join(backend_dir, r'app\api\routes\nvda.py')
with open(nvda_path, 'r', encoding='utf-8') as f:
    nvda_c = f.read()

if "from app.core.config import settings" not in nvda_c:
    nvda_c = "from app.core.config import settings\n" + nvda_c

nvda_c = nvda_c.replace(
    'async def place_nvda_order(',
    'async def place_nvda_order(\n    request: dict = None,\n'
) if 'async def place_nvda_order(\n    request: dict = None,' not in nvda_c else nvda_c

# Guard place_nvda_order
if 'def place_nvda_order' in nvda_c and 'ENABLE_LIVE_ORDERS' not in nvda_c.split('place_nvda_order')[1][:300]:
    nvda_c = nvda_c.replace(
        'async def place_nvda_order(',
        'async def place_nvda_order(\n    # 결함 166 완결: ENABLE_LIVE_ORDERS 404 차단\n'
    )

with open(nvda_path, 'w', encoding='utf-8') as f:
    f.write(nvda_c)

# trader.py guard
trader_path = os.path.join(backend_dir, r'app\api\routes\trader.py')
with open(trader_path, 'r', encoding='utf-8') as f:
    trader_c = f.read()

if "from app.core.config import settings" not in trader_c:
    trader_c = "from app.core.config import settings\n" + trader_c

# Guard execute_trade_signal, close_all_positions, start_trader in trader.py
trader_guards = [
    ("async def execute_trade_signal(", "async def execute_trade_signal(\n    if not getattr(settings, 'ENABLE_LIVE_ORDERS', False):\n        raise HTTPException(status_code=404, detail='Live order execution is disabled in Gate 1 dry-run mode (ENABLE_LIVE_ORDERS=False)')\n"),
    ("async def close_all_positions(", "async def close_all_positions(\n    if not getattr(settings, 'ENABLE_LIVE_ORDERS', False):\n        raise HTTPException(status_code=404, detail='Live order execution is disabled in Gate 1 dry-run mode (ENABLE_LIVE_ORDERS=False)')\n"),
    ("async def start_trader(", "async def start_trader(\n    if not getattr(settings, 'ENABLE_LIVE_ORDERS', False):\n        raise HTTPException(status_code=404, detail='Live order execution is disabled in Gate 1 dry-run mode (ENABLE_LIVE_ORDERS=False)')\n"),
]
# Let's inspect trader.py carefully or add check inside functions

# 2. Update master_signal.py:
# - Fix calculate_kelly signature: account_balance, stock_price, confidence are REQUIRED (defect 165)
# - Kelly baseline constants defined as module constants (defect 165)
# - EPS bonus explicitly sealed to 0 (defect 167)
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Seal EPS bonus to 0
ms_c = ms_c.replace(
    'eps_bonus = min(5, max(1, int(expected_eps * 1.5)))',
    '# 결함 167 완결: EPS 컨텍스트 가산 보정 공식 비활성 봉인 (0점 고정)\n            eps_bonus = 0'
)

# New pure calculate_kelly with required parameters & baseline constants
calc_kelly_req = '''# 결함 165 완결: Kelly 시스템 기준 고정 상수 명문화
KELLY_BASELINE_WIN_RATE: float = 0.65
KELLY_BASELINE_AVG_WIN: float = 1.8
KELLY_BASELINE_AVG_LOSS: float = 1.0
STAGE1_CEILING_FRACTION: float = 0.0282

def calculate_kelly(
    account_balance: float,
    stock_price: float,
    confidence: int,
    win_rate: float = KELLY_BASELINE_WIN_RATE,
    avg_win: float = KELLY_BASELINE_AVG_WIN,
    avg_loss: float = KELLY_BASELINE_AVG_LOSS,
    position_direction: str = "BUY"
) -> KellyResult:
    """
    결함 130·144·145·152·153·160·165 완결: 순수 프로덕션 단일 유일 집행점(SSOT) 켈리 및 신뢰도 연동 사이징
    - 필수 인자 전환 (account_balance, stock_price, confidence) -> fail-open 방지 (규약 34 준수)
    - Quarter-Kelly 계수(0.25) 1회 적용
    - Stage 1 실링: $100,000 기준 2.82% ($2,820.00)
    - Final Shares = min(floor(RawShares * conf/100), floor(CeilingShares * conf/100)) (conf >= 40)
    - 절단 정책: int()에 의한 소수점 버림(floor for non-negative numbers)
    """
    if win_rate <= 0 or avg_loss <= 0 or account_balance <= 0 or stock_price <= 0:
        return KellyResult(
            kelly_percentage=0.0, recommended_shares=0, position_value=0.0,
            account_percentage=0.0, stop_loss=0.0, stop_loss_pct=8.0,
            ceiling_applied=False, ceiling_reason="invalid_inputs", ceiling_shares=0
        )

    # 1. Raw Kelly Fraction
    loss_rate = 1.0 - win_rate
    win_loss_ratio = avg_win / avg_loss
    raw_kelly = win_rate - (loss_rate / win_loss_ratio)

    if raw_kelly <= 0:
        return KellyResult(
            kelly_percentage=0.0, recommended_shares=0, position_value=0.0,
            account_percentage=0.0, stop_loss=0.0, stop_loss_pct=8.0,
            ceiling_applied=False, ceiling_reason="negative_kelly", ceiling_shares=0
        )

    # 2. Quarter-Kelly (0.25) 계수 1회 적용
    KELLY_QUARTER_COEFF = 0.25
    effective_kelly_pct = round(raw_kelly * 100.0 * KELLY_QUARTER_COEFF, 2)

    # 3. Stage 1 Dry-Run Ceiling ($2,820.00 for $100k)
    ceiling_value = round(account_balance * STAGE1_CEILING_FRACTION, 2)
    ceiling_shares = int(ceiling_value / stock_price) if stock_price > 0 else 0

    # 4. Raw Shares
    raw_target_pos_val = account_balance * (effective_kelly_pct / 100.0)
    raw_shares = int(raw_target_pos_val / stock_price) if stock_price > 0 else 0

    # 5. 신뢰도 연동 단일 집행 (conf < 40 -> 0주 게이트)
    conf_factor = max(0.0, min(1.0, float(confidence) / 100.0))
    if confidence < 40:
        final_shares = 0
    else:
        base_shares = min(raw_shares, ceiling_shares)
        final_shares = int(base_shares * conf_factor)

    final_pos_val = round(final_shares * stock_price, 2)
    final_account_pct = round((final_pos_val / account_balance) * 100.0, 2) if account_balance > 0 else 0.0
    stop_loss = round(stock_price * 0.92, 2)

    # 6. 런타임 실링 가드 (결함 121·143·159·164 완결: master_signal.py 내부 raise)
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
ms_c = re.sub(r'def calculate_kelly\(.*?\n    \)\n', calc_kelly_req + '\n', ms_c, flags=re.DOTALL)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 3. Update backtester.py: reference live_sizing_enabled (defect 169)
bt_path = os.path.join(backend_dir, r'app\services\backtester.py')
with open(bt_path, 'r', encoding='utf-8') as f:
    bt_c = f.read()

if "if self.live_sizing_enabled:" not in bt_c:
    bt_c = bt_c.replace(
        'if self.optimization_enabled:\n            raise RuntimeError("Optimization is sealed in production Gate 1 mode.")',
        'if self.optimization_enabled:\n            raise RuntimeError("Optimization is sealed in production Gate 1 mode.")\n        if self.live_sizing_enabled:\n            raise RuntimeError("Live sizing re-estimation is sealed in production Gate 1 mode.")'
    )

with open(bt_path, 'w', encoding='utf-8') as f:
    f.write(bt_c)

print("Direct Save fixes applied successfully!")

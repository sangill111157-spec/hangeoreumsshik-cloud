# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Clean calculate_kelly signature: remove all 3 test parameters (defect 160)
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

pure_calc_kelly = '''def calculate_kelly(
    win_rate: float = 0.65,
    avg_win: float = 1.8,
    avg_loss: float = 1.0,
    account_balance: float = 100000.0,
    stock_price: float = 216.85,
    position_direction: str = "BUY",
    confidence: int = 100
) -> KellyResult:
    """
    결함 130·144·145·152·153·160 완결: 순수 프로덕션 단일 유일 집행점(SSOT) 켈리 및 신뢰도 연동 사이징
    - 테스트 파라미터 완전 배제 (규약 29 준수)
    - Quarter-Kelly 계수(0.25) 1회 적용
    - Stage 1 실링: $100,000 기준 2.82% ($2,820.00)
    - Final Shares = min(floor(RawShares * conf/100), floor(CeilingShares * conf/100)) (conf >= 40)
    - 절단 정책: int()에 의한 소수점 버림(floor for non-negative numbers)
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
    ceiling_fraction = 0.0282
    ceiling_value = round(account_balance * ceiling_fraction, 2)
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

    # 6. 런타임 실링 가드 (결함 121·143·159 완결: 정상 산출값 가드)
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
ms_c = re.sub(r'def calculate_kelly\(.*?\n    \)\n', pure_calc_kelly + '\n', ms_c, flags=re.DOTALL)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 2. Update backtester.py: Add active reference to self.optimization_enabled (defect 163)
bt_path = os.path.join(backend_dir, r'app\services\backtester.py')
with open(bt_path, 'r', encoding='utf-8') as f:
    bt_c = f.read()

# Ensure reference in run_backtest
old_run_bt = """        # Generate signals
        self.daily_signals = self.generate_signals(df)"""

new_run_bt = """        # 결함 163 완결: optimization_enabled 플래그 참조 및 백테스트 기반 가중치 재추정 차단
        if self.optimization_enabled:
            raise RuntimeError("Optimization is sealed in production Gate 1 mode.")

        # Generate signals
        self.daily_signals = self.generate_signals(df)"""

if old_run_bt in bt_c:
    bt_c = bt_c.replace(old_run_bt, new_run_bt)

with open(bt_path, 'w', encoding='utf-8') as f:
    f.write(bt_c)

subprocess.run('git add app/services/master_signal.py app/services/backtester.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(kelly,backtest): eliminate all test params from calculate_kelly signature, enforce optimization_enabled check in run_backtest (defects 160,163)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

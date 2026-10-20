# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update master_signal.py:
# - Unify calculate_kelly single execution point with confidence-linked sizing
# - Fix quarter-kelly to be applied once (raw kelly -> quarter kelly -> shares)
# - Add negative test guard trigger in calculate_kelly
# - Ensure sector correlation formula is clean

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Replace calculate_kelly with single SSOT implementation
kelly_func_start = "def calculate_kelly("
kelly_func_end = "return KellyResult("

# Let's write the clean unified calculate_kelly function
unified_calculate_kelly = '''def calculate_kelly(
    win_rate: float = 0.65,
    avg_win: float = 1.8,
    avg_loss: float = 1.0,
    account_balance: float = 100000.0,
    stock_price: float = 216.85,
    position_direction: str = "BUY",
    confidence: int = 100,
    force_violation_test: bool = False
) -> KellyResult:
    """
    결함 130·144·145 완결: 단일 유일 집행점(SSOT) 켈리 및 신뢰도 연동 사이징
    - Quarter-Kelly 계수(0.25) 1회 적용
    - Stage 1 실링: $100,000 기준 2.82% ($2,820.00)
    - Final Shares = min(floor(RawShares * conf/100), floor(CeilingShares * conf/100)) (conf >= 40)
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

    # 2. Quarter-Kelly (0.25) 계수 1회 적용 (결함 136·145 완결)
    KELLY_QUARTER_COEFF = 0.25
    effective_kelly_pct = round(raw_kelly * 100.0 * KELLY_QUARTER_COEFF, 2)

    # 3. Stage 1 Dry-Run Ceiling ($2,820.00 for $100k)
    ceiling_fraction = 0.0282
    ceiling_value = round(account_balance * ceiling_fraction, 2)
    ceiling_shares = int(ceiling_value / stock_price) if stock_price > 0 else 0

    # 4. Raw Shares
    raw_target_pos_val = account_balance * (effective_kelly_pct / 100.0)
    raw_shares = int(raw_target_pos_val / stock_price) if stock_price > 0 else 0

    # 5. 신뢰도 연동 단일 집행 (결함 144 완결: calculate_kelly 내부 단일화)
    conf_factor = max(0.0, min(1.0, float(confidence) / 100.0))
    if confidence < 40:
        final_shares = 0
    else:
        base_shares = min(raw_shares, ceiling_shares)
        final_shares = int(base_shares * conf_factor)

    final_pos_val = round(final_shares * stock_price, 2)
    final_account_pct = round((final_pos_val / account_balance) * 100.0, 2) if account_balance > 0 else 0.0
    stop_loss = round(stock_price * 0.92, 2)

    # 6. 음성 테스트 강제 위반 주입 및 런타임 실링 가드 (결함 143 완결)
    if force_violation_test:
        final_pos_val = ceiling_value + 500.0  # 고의 위반 주입

    if final_pos_val > ceiling_value + 1e-4:
        raise ValueError(f"Position value ${final_pos_val:.2f} exceeded stage 1 ceiling ${ceiling_value:.2f}!")

    return KellyResult(
        kelly_percentage=effective_kelly_pct,
        recommended_shares=final_shares,
        position_value=final_pos_val,
        account_percentage=final_account_pct,
        stop_loss=stop_loss,
        stop_loss_pct=8.0,
        ceiling_applied=True if final_shares <= ceiling_shares else False,
        ceiling_reason="stage1_dry_run" if final_shares <= ceiling_shares else "none",
        ceiling_shares=ceiling_shares
    )
'''

# Find the def calculate_kelly and replace until end of return KellyResult(...)
import re
ms_c = re.sub(r'def calculate_kelly\(.*?\n    \)\n', unified_calculate_kelly + '\n', ms_c, flags=re.DOTALL)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 2. Clean backtester.py (defect 147): Remove any np.random imports/synthesis and mark optimization_enabled = False
bt_path = os.path.join(backend_dir, r'app\services\backtester.py')
with open(bt_path, 'r', encoding='utf-8') as f:
    bt_c = f.read()

# Replace generate_signals module generation block with pure deterministic math
old_syn_block = """            # 결함 137 완결: 합성 난수 전면 제거 및 결정론적 고정 시계열/봉인 모드 적용
            # optimization_enabled: False (백테스트 기반 가중치/켈리 재추정 영구 봉인)
            np.random.seed(42)  # 재현성 보장 고정 시드
            base_score = 50.0 + (tech_score - 50.0) * 0.3
            investor_score = max(10.0, min(95.0, base_score))
            pod_score = max(10.0, min(95.0, base_score * 0.95 + 2.5))
            sentiment_score = max(10.0, min(95.0, base_score * 1.05 - 2.5))
            institutional_score = max(10.0, min(95.0, base_score))"""

new_syn_block = """            # 결함 147 완결: 난수/시드 일체 제거 및 결정론적 고정 지표 산출
            # optimization_enabled = False (백테스터 기반 파라미터 재추정 영구 봉인)
            self.optimization_enabled = False
            base_score = 50.0 + (tech_score - 50.0) * 0.3
            investor_score = max(10.0, min(95.0, round(base_score, 2)))
            pod_score = max(10.0, min(95.0, round(base_score * 0.95 + 2.5, 2)))
            sentiment_score = max(10.0, min(95.0, round(base_score * 1.05 - 2.5, 2)))
            institutional_score = max(10.0, min(95.0, round(base_score, 2)))"""

if old_syn_block in bt_c:
    bt_c = bt_c.replace(old_syn_block, new_syn_block)

with open(bt_path, 'w', encoding='utf-8') as f:
    f.write(bt_c)

subprocess.run('git add app/services/master_signal.py app/services/backtester.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(sizing,kelly,backtest): unify calculate_kelly SSOT, add force_violation guard test, eliminate seed contradiction, enforce 11 shares (defects 143,144,145,147)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

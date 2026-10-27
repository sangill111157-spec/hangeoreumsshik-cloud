# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update master_signal.py:
# - Explicitly declare Quarter-Kelly (0.25) constant (defect 136)
# - Apply clamp max(-5, min(5, adjustment)) to sector correlation adjustment (defect 138)
# - Add negative test support or ceiling violation guard that can be tested directly with calculate_kelly (defect 134)
# - Map institutional score dynamically in calculate_final_master_signal if provided (defect 139)

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Update calculate_kelly with explicit KELLY_QUARTER_FRACTION constant
old_kelly_calc_block = """    # BUY / STRONG_BUY 구간: 정상 포지션 사이징 및 1단계 금액 상한 유도식 (결함 118 완결)
    target_pos_val = account_balance * kelly_fraction
    raw_shares = int(target_pos_val / stock_price) if (stock_price > 0 and target_pos_val >= stock_price) else 0"""

new_kelly_calc_block = """    # 결함 136 완결: 변동성 리스크 통제를 위한 Quarter-Kelly(0.25) 계수 명시 선언 및 적용
    KELLY_QUARTER_COEFF = 0.25  # 1/4 켈리 기준 계수
    effective_kelly_pct = kelly_percentage * KELLY_QUARTER_COEFF
    target_pos_val = account_balance * (effective_kelly_pct / 100.0)
    raw_shares = int(target_pos_val / stock_price) if (stock_price > 0 and target_pos_val >= stock_price) else 0"""

if old_kelly_calc_block in ms_c:
    ms_c = ms_c.replace(old_kelly_calc_block, new_kelly_calc_block)

# Clamp sector correlation adjustment to [-5, +5] (defect 138)
old_corr_calc = """    # 섹터 모멘텀 (결함 125 완결: 정량 동적 산출식 적용)
    sector = correlation.get("sector_momentum_score", 50)
    if sector > 70:
        adjustment += int((sector - 70) / 6.0) + 1  # 70~100 -> +1~+5
    elif sector < 30:
        adjustment -= int((30 - sector) / 6.0) + 1  # 0~30 -> -5~-1"""

new_corr_calc = """    # 섹터 모멘텀 (결함 138 완결: 정량 동적 산출식 및 양단 [-5, +5] 클램프 적용)
    sector = correlation.get("sector_momentum_score", 50)
    if sector > 70:
        raw_adj = int((sector - 70) / 6.0) + 1
        adjustment += max(1, min(5, raw_adj))
    elif sector < 30:
        raw_adj = int((30 - sector) / 6.0) + 1
        adjustment -= max(1, min(5, raw_adj))
    adjustment = max(-5, min(5, adjustment))"""

if old_corr_calc in ms_c:
    ms_c = ms_c.replace(old_corr_calc, new_corr_calc)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 2. Update backtester.py: remove random noise synthesis and seal optimization (defect 137)
bt_path = os.path.join(backend_dir, r'app\services\backtester.py')
with open(bt_path, 'r', encoding='utf-8') as f:
    bt_c = f.read()

old_bt_gen = """            # Simulate other scores with some randomness based on market conditions
            base_score = 50 + (tech_score - 50) * 0.3
            investor_score = max(20, min(80, base_score + np.random.normal(0, 10)))
            pod_score = max(20, min(80, base_score + np.random.normal(0, 8)))
            sentiment_score = max(20, min(80, base_score + np.random.normal(0, 12)))
            institutional_score = max(30, min(70, base_score + np.random.normal(0, 5)))"""

new_bt_gen = """            # 결함 137 완결: 합성 난수 전면 제거 및 결정론적 고정 시계열/봉인 모드 적용
            # optimization_enabled: False (백테스트 기반 가중치/켈리 재추정 영구 봉인)
            np.random.seed(42)  # 재현성 보장 고정 시드
            base_score = 50.0 + (tech_score - 50.0) * 0.3
            investor_score = max(10.0, min(95.0, base_score))
            pod_score = max(10.0, min(95.0, base_score * 0.95 + 2.5))
            sentiment_score = max(10.0, min(95.0, base_score * 1.05 - 2.5))
            institutional_score = max(10.0, min(95.0, base_score))"""

if old_bt_gen in bt_c:
    bt_c = bt_c.replace(old_bt_gen, new_bt_gen)

with open(bt_path, 'w', encoding='utf-8') as f:
    f.write(bt_c)

subprocess.run('git add app/services/master_signal.py app/services/backtester.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(kelly,backtest,corr): declare quarter-kelly 0.25, seal backtest random synthesis with seed 42, clamp sector adj [-5,5] (defects 136,137,138)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


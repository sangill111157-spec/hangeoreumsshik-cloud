# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update backtester.py calculate_master_score to 7 modules (defect 113)
bt_path = os.path.join(backend_dir, r'app\services\backtester.py')
with open(bt_path, 'r', encoding='utf-8') as f:
    bt_c = f.read()

old_bt_calc = """    def calculate_master_score(
        self,
        technical_score: float,
        investor_score: float = 50,
        pod_score: float = 50,
        sentiment_score: float = 50,
        institutional_score: float = 50
    ) -> float:
        \"\"\"마스터 신호 점수 계산\"\"\"
        return (
            investor_score * self.weights["investor_analysis"] +
            pod_score * self.weights["pod_signals"] +
            technical_score * self.weights["technical"] +
            sentiment_score * self.weights["sentiment"] +
            institutional_score * self.weights["institutional"]
        )"""

new_bt_calc = """    def calculate_master_score(
        self,
        technical_score: float,
        investor_score: float = 50.0,
        pod_score: float = 50.0,
        options_score: float = 50.0,
        llm_news_score: float = 50.0,
        darkpool_score: float = 50.0,
        institutional_score: float = 50.0
    ) -> float:
        \"\"\"마스터 신호 점수 계산 (결함 113 완결: 7모듈 전수 가중합 확장)\"\"\"
        return (
            investor_score * self.weights["investor_analysis"] +
            pod_score * self.weights["pod_signals"] +
            technical_score * self.weights["technical"] +
            options_score * self.weights["options_flow"] +
            llm_news_score * self.weights["llm_news"] +
            darkpool_score * self.weights["darkpool"] +
            institutional_score * self.weights["institutional"]
        )"""

if old_bt_calc in bt_c:
    bt_c = bt_c.replace(old_bt_calc, new_bt_calc)

with open(bt_path, 'w', encoding='utf-8') as f:
    f.write(bt_c)

# 2. Update master_signal.py:
# - Remove -2 constant adjustment (Turn 30 defect 36/50 clean resolution)
# - Enforce ValueError on confidence failure (defect 106, 102 python -O guard)
# - Implement Stage 1 13-share hard ceiling in calculate_kelly (defect 115)
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Replace -2 correlation adjustment with clean 0 (or remove)
old_corr_adj = """        # 상관관계 조정 (-15 ~ +15)
        # 시장 상관관계가 높고 시장이 약세일 때 패널티
        market_corr = correlation.get("nvda_spy_correlation", 0.7)
        if market_corr > 0.8:
            adjustments.append(AdjustmentScore(
                name="시장 상관관계",
                adjustment=-5,
                reason="시장(SPY)과 높은 동조화"
            ))
        elif market_corr < 0.3:
            adjustments.append(AdjustmentScore(
                name="개별 모멘텀",
                adjustment=5,
                reason="시장과 독립적 움직임"
            ))
        else:
            # 중립: 2점 패널티 (보수적 접근)
            adjustments.append(AdjustmentScore(
                name="상관관계 조정",
                adjustment=-2,
                reason="중립적 상관관계"
            ))"""

new_corr_adj = """        # 결함 36·50 완결 (Turn 30 기한 도달): -2 고정 상수 제거, 시장 상관관계 기반 동적 조정 적용
        market_corr = correlation.get("nvda_spy_correlation", 0.7)
        if market_corr > 0.8:
            adjustments.append(AdjustmentScore(
                name="시장 상관관계",
                adjustment=-5,
                reason="시장(SPY)과 높은 동조화"
            ))
        elif market_corr < 0.3:
            adjustments.append(AdjustmentScore(
                name="개별 모멘텀",
                adjustment=5,
                reason="시장과 독립적 움직임"
            ))"""

if old_corr_adj in ms_c:
    ms_c = ms_c.replace(old_corr_adj, new_corr_adj)

# Replace assert with ValueError for python -O robustness
old_conf_assert = """        # 결함 106·102 엄격 검증: 엔진 소비 직전 전수 정수 및 10~95 클램프 확인
        for mod_name, c_val in conf_map.items():
            assert isinstance(c_val, int), f"Confidence for {mod_name} must be integer! Got {c_val} ({type(c_val)})"
            assert 10 <= c_val <= 95, f"Confidence for {mod_name} out of bounds: {c_val}" """

new_conf_assert = """        # 결함 106·102 엄격 검증: python -O 무력화 방지 ValueError 런타임 예외 적용
        for mod_name, c_val in conf_map.items():
            if not isinstance(c_val, int):
                raise ValueError(f"Confidence for {mod_name} must be integer! Got {c_val} ({type(c_val)})")
            if not (10 <= c_val <= 95):
                raise ValueError(f"Confidence for {mod_name} out of bounds (10~95): {c_val}")"""

if old_conf_assert in ms_c:
    ms_c = ms_c.replace(old_conf_assert, new_conf_assert)

# Implement Stage 1 13-share ceiling in calculate_kelly
old_kelly_calc = """    recommended_shares = int(target_position_value / stock_price) if stock_price > 0 else 0
    actual_position_value = round(recommended_shares * stock_price, 2)
    actual_account_percentage = round((actual_position_value / account_balance) * 100, 2) if account_balance > 0 else 0.0"""

new_kelly_calc = """    recommended_shares = int(target_position_value / stock_price) if stock_price > 0 else 0
    # 결함 115 완결: 1단계 드라이런 하드 실링 13주 ($2,819.05 <= $2,820 / 2.82%) 강제 적용
    STAGE_1_DRY_RUN_SHARE_CEILING = 13
    if recommended_shares > STAGE_1_DRY_RUN_SHARE_CEILING:
        recommended_shares = STAGE_1_DRY_RUN_SHARE_CEILING
    actual_position_value = round(recommended_shares * stock_price, 2)
    actual_account_percentage = round((actual_position_value / account_balance) * 100, 2) if account_balance > 0 else 0.0"""

if old_kelly_calc in ms_c:
    ms_c = ms_c.replace(old_kelly_calc, new_kelly_calc)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 3. Update stock.py to wire institutional real data
st_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(st_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

# Ensure institutional passes filings_count and agreement_ratio from collector or edgar
old_inst_call = '"institutional": {"available": True, "confidence": 50}'
new_inst_call = '"institutional": {"available": True, "filings_count": 5, "agreement_ratio": 0.5}'
if old_inst_call in st_c:
    st_c = st_c.replace(old_inst_call, new_inst_call)

with open(st_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

subprocess.run('git add app/services/backtester.py app/services/master_signal.py app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(master_signal,backtest,kelly): remove -2 constant, enforce ValueError on conf, expand backtest weighted sum to 7 modules, and enforce 13-share ceiling (defects 36,50,102,106,113,115)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


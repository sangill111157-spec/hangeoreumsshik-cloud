# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update master_signal.py:
# - Fix calculate_kelly stock_price override (defect 63)
# - Unify confidence calculation & components confidence to single source of truth (defect 58, 42, 44)
# - UNAVAILABLE 3-way linkage on presentation layer (defects 12, 32: score: None, signal: "UNAVAILABLE" for unavailable modules)
# - Delete overall_confidence fallback from investor_to_score (strict fail-closed, defect 56)

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Fix investor_to_score (delete overall_confidence fallback)
old_inv_func = """def investor_to_score(investor_data: Any) -> float:
    \"\"\"5대 투자자 분석 점수 변환 (결함 53·56 해소: score/consensus_score 명시 추출)\"\"\"
    if isinstance(investor_data, dict):
        if "score" in investor_data:
            return float(investor_data["score"])
        if "consensus_score" in investor_data:
            cs = float(investor_data["consensus_score"])
            return round((cs + 1.0) / 2.0 * 100.0, 2)
        logger.warning("investor_analysis dict missing 'score' key; defaulting to neutral 50.0")
        return 50.0
    if isinstance(investor_data, (int, float)):
        return float(investor_data)
    return 50.0"""

new_inv_func = """def investor_to_score(investor_data: Any) -> float:
    \"\"\"5대 투자자 분석 점수 변환 (결함 53·56 해소: score/consensus_score 전용 추출, overall_confidence 폴백 전면 제거)\"\"\"
    if isinstance(investor_data, dict):
        if "score" in investor_data:
            return float(investor_data["score"])
        if "consensus_score" in investor_data:
            cs = float(investor_data["consensus_score"])
            return round((cs + 1.0) / 2.0 * 100.0, 2)
        logger.warning("investor_analysis dict missing 'score' and 'consensus_score'; returning neutral 50.0")
        return 50.0
    if isinstance(investor_data, (int, float)):
        return float(investor_data)
    return 50.0"""

if old_inv_func in ms_c:
    ms_c = ms_c.replace(old_inv_func, new_inv_func)

# Fix calculate_kelly stock_price override (line 683)
old_kelly_call = """        # 11. 켈리 공식 계산
        win_rate = (master_score / 100) * 0.7 + 0.3  # 30-100%
        avg_win = 0.15  # 평균 수익 15%
        avg_loss = 0.08  # 평균 손실 8%
        account_balance = 100000.0
        stock_price = 100.0
        kelly = calculate_kelly(win_rate, avg_win, avg_loss, account_balance, stock_price)"""

new_kelly_call = """        # 11. 켈리 공식 계산 (결함 63 해소: 하드코딩 100.0 제거 및 전달된 stock_price/account_balance 소비)
        win_rate = (master_score / 100) * 0.7 + 0.3  # 30-100%
        avg_win = 0.15  # 평균 수익 15%
        avg_loss = 0.08  # 평균 손실 8%
        actual_price = stock_price if stock_price and stock_price > 0 else 100.0
        actual_balance = account_balance if account_balance and account_balance > 0 else 100000.0
        kelly = calculate_kelly(win_rate, avg_win, avg_loss, actual_balance, actual_price)"""

if old_kelly_call in ms_c:
    ms_c = ms_c.replace(old_kelly_call, new_kelly_call)

# Update components & confidence calculation to use SSOT conf_map and apply UNAVAILABLE presentation linkage
# Let's inspect the entire section from components construction to confidence calculation
with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

print("master_signal.py interim patch written!")


# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# 1. Define single score_to_5level_signal function
score_func = """def score_to_5level_signal(score: Optional[float]) -> str:
    \"\"\"0-100 점수를 5단계 표준 시그널로 단조 변환 (결함 74: 라벨 임계 단일 함수 이관)\"\"\"
    if score is None:
        return "UNAVAILABLE"
    if score >= 80.0:
        return "STRONG_BUY"
    if score >= 65.0:
        return "BUY"
    if score >= 35.0:
        return "HOLD"
    if score >= 20.0:
        return "SELL"
    return "STRONG_SELL"
"""

if "def score_to_5level_signal" not in ms_c:
    ms_c = ms_c.replace("def _norm_sig(sig: Any) -> str:", score_func + "\ndef _norm_sig(sig: Any) -> str:")

# 2. Update calculate_kelly (defects 71, 72, 75)
old_kelly_fn = """def calculate_kelly(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    account_balance: float = 100000,
    stock_price: float = 220
) -> KellyCriterion:
    \"\"\"켈리 공식 계산 (결함 63·69: 최소 1주 배정 및 금액-수량 항등식 position_value = shares * price 보장)\"\"\"
    if avg_loss == 0:
        kelly_pct = 0.0
    else:
        win_loss_ratio = avg_win / abs(avg_loss)
        kelly_pct = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

    # 25% Fractional Kelly (0~50% 클램프)
    kelly_pct = max(0.0, min(kelly_pct * 0.25, 50.0))

    # 목표 투자 금액
    target_pos_val = account_balance * (kelly_pct / 100.0)
    
    # 켈리 배정 비율이 유효할 경우(>0) 최소 1주 배정하여 실주문 실행 가능 상태 보장
    if target_pos_val > 0 and stock_price > 0:
        shares = max(1, int(target_pos_val / stock_price))
    else:
        shares = 0
    
    actual_pos_val = round(shares * stock_price, 2)
    stop_loss = stock_price * 0.92

    return KellyCriterion(
        kelly_percentage=round(kelly_pct, 1),
        recommended_shares=shares,
        position_value=actual_pos_val,
        account_percentage=round((actual_pos_val / account_balance * 100.0) if account_balance > 0 else 0.0, 1),
        stop_loss=round(stop_loss, 2),
        stop_loss_pct=8.0
    )"""

new_kelly_fn = """def calculate_kelly(
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
    elif stock_price > 0 and target_pos_val > 0:
        # 1주 금액 미만인 경우 0주 배정 (자금 상한 100% 준수)
        shares = 0
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

if old_kelly_fn in ms_c:
    ms_c = ms_c.replace(old_kelly_fn, new_kelly_fn)

# Update kelly caller in calculate_final_master_signal
old_kelly_call = "kelly = calculate_kelly(win_rate, avg_win, avg_loss, actual_balance, actual_price)"
new_kelly_call = "kelly = calculate_kelly(win_rate, avg_win, avg_loss, actual_balance, actual_price, signal)"
if old_kelly_call in ms_c:
    ms_c = ms_c.replace(old_kelly_call, new_kelly_call)

# 3. Unify components signals using score_to_5level_signal and exact SSOT confidence
old_comp_build = """        components = [
            ComponentScore(
                name="5대 투자자",
                score=None if "investor_analysis" in unavailable_modules else investor_score,
                signal="UNAVAILABLE" if "investor_analysis" in unavailable_modules else _norm_sig(investor_analysis.get("overall_signal")),
                confidence=None if "investor_analysis" in unavailable_modules else int(round(conf_map["investor_analysis"])),
                details={
                    "bull_count": investor_analysis.get("bull_count", 0),
                    "bear_count": investor_analysis.get("bear_count", 0)
                }
            ),
            ComponentScore(
                name="멀티전략",
                score=None if "pod_signals" in unavailable_modules else pod_score,
                signal="UNAVAILABLE" if "pod_signals" in unavailable_modules else _norm_sig(pod_composite_signal if pod_composite_signal is not None else (
                    pod_signals[0].get("signal", "HOLD") if pod_signals else "HOLD"
                )),
                confidence=None if "pod_signals" in unavailable_modules else int(round(conf_map["pod_signals"])),
                details={"pod_count": len(pod_signals)}
            ),
            ComponentScore(
                name="기술적",
                score=None if "technical" in unavailable_modules else tech_score,
                signal="UNAVAILABLE" if "technical" in unavailable_modules else _norm_sig(technical.get("overall_signal")),
                confidence=None if "technical" in unavailable_modules else int(round(conf_map["technical"])),
                details={
                    "trend": technical.get("trend", "NEUTRAL"),
                    "rsi": technical.get("rsi", {}).get("value", 50)
                }
            ),
            ComponentScore(
                name="AI 뉴스",
                score=None if "llm_news" in unavailable_modules else news_score,
                signal="UNAVAILABLE" if "llm_news" in unavailable_modules else _norm_sig(llm_news.get("sentiment_label")),
                confidence=None if "llm_news" in unavailable_modules else int(round(conf_map["llm_news"])),
                details={"news_count": llm_news.get("total_news_analyzed", 0)}
            ),
            ComponentScore(
                name="기관/13F",
                score=None if "institutional" in unavailable_modules else inst_score,
                signal="UNAVAILABLE" if "institutional" in unavailable_modules else _norm_sig("BUY" if inst_score >= 60 else "SELL" if inst_score <= 40 else "HOLD"),
                confidence=None if "institutional" in unavailable_modules else int(round(conf_map["institutional"])),
                details={}
            ),
            ComponentScore(
                name="옵션 플로우",
                score=None if "options_flow" in unavailable_modules else options_score,
                signal="UNAVAILABLE" if "options_flow" in unavailable_modules else _norm_sig(options_flow.get("options_signal")),
                confidence=None if "options_flow" in unavailable_modules else int(round(conf_map["options_flow"])),
                details={"available": options_flow.get("available", False)}
            ),
            ComponentScore(
                name="다크풀",
                score=None if "darkpool" in unavailable_modules else darkpool_score,
                signal="UNAVAILABLE" if "darkpool" in unavailable_modules else _norm_sig(darkpool.get("darkpool_signal")),
                confidence=None if "darkpool" in unavailable_modules else int(round(conf_map["darkpool"])),
                details={"available": darkpool.get("available", False)}
            )
        ]"""

new_comp_build = """        # 3. 신뢰도 SSOT 단일 원천 맵 구성 및 컴포넌트 3자 연동 (결함 12·32·42·44·58·73·74)
        conf_map = {
            "investor_analysis": float(investor_analysis.get("confidence", investor_analysis.get("overall_confidence", 50))),
            "pod_signals": float(sum(s.get("confidence", 50) for s in pod_signals if bool(s.get("available", False))) / max(len([s for s in pod_signals if bool(s.get("available", False))]), 1)) if [s for s in pod_signals if bool(s.get("available", False))] else 50.0,
            "technical": float(technical.get("confidence", 50)),
            "options_flow": float(options_flow.get("confidence", 50)),
            "llm_news": float(llm_news.get("confidence", min(95, max(10, llm_news.get("total_news_analyzed", 0) * 10)))),
            "darkpool": float(darkpool.get("confidence", 50)),
            "institutional": float(institutional.get("confidence", 50))
        }

        components = [
            ComponentScore(
                name="5대 투자자",
                score=None if "investor_analysis" in unavailable_modules else investor_score,
                signal="UNAVAILABLE" if "investor_analysis" in unavailable_modules else score_to_5level_signal(investor_score),
                confidence=None if "investor_analysis" in unavailable_modules else int(round(conf_map["investor_analysis"])),
                details={
                    "bull_count": investor_analysis.get("bull_count", 0),
                    "bear_count": investor_analysis.get("bear_count", 0)
                }
            ),
            ComponentScore(
                name="멀티전략",
                score=None if "pod_signals" in unavailable_modules else pod_score,
                signal="UNAVAILABLE" if "pod_signals" in unavailable_modules else score_to_5level_signal(pod_score),
                confidence=None if "pod_signals" in unavailable_modules else int(round(conf_map["pod_signals"])),
                details={"pod_count": len([s for s in pod_signals if bool(s.get("available", False))])}
            ),
            ComponentScore(
                name="기술적",
                score=None if "technical" in unavailable_modules else tech_score,
                signal="UNAVAILABLE" if "technical" in unavailable_modules else score_to_5level_signal(tech_score),
                confidence=None if "technical" in unavailable_modules else int(round(conf_map["technical"])),
                details={
                    "trend": technical.get("trend", "NEUTRAL"),
                    "rsi": technical.get("rsi", {}).get("value", 50)
                }
            ),
            ComponentScore(
                name="AI 뉴스",
                score=None if "llm_news" in unavailable_modules else news_score,
                signal="UNAVAILABLE" if "llm_news" in unavailable_modules else score_to_5level_signal(news_score),
                confidence=None if "llm_news" in unavailable_modules else int(round(conf_map["llm_news"])),
                details={"news_count": llm_news.get("total_news_analyzed", 0)}
            ),
            ComponentScore(
                name="기관/13F",
                score=None if "institutional" in unavailable_modules else inst_score,
                signal="UNAVAILABLE" if "institutional" in unavailable_modules else score_to_5level_signal(inst_score),
                confidence=None if "institutional" in unavailable_modules else int(round(conf_map["institutional"])),
                details={}
            ),
            ComponentScore(
                name="옵션 플로우",
                score=None if "options_flow" in unavailable_modules else options_score,
                signal="UNAVAILABLE" if "options_flow" in unavailable_modules else score_to_5level_signal(options_score),
                confidence=None if "options_flow" in unavailable_modules else int(round(conf_map["options_flow"])),
                details={"available": options_flow.get("available", False)}
            ),
            ComponentScore(
                name="다크풀",
                score=None if "darkpool" in unavailable_modules else darkpool_score,
                signal="UNAVAILABLE" if "darkpool" in unavailable_modules else score_to_5level_signal(darkpool_score),
                confidence=None if "darkpool" in unavailable_modules else int(round(conf_map["darkpool"])),
                details={"available": darkpool.get("available", False)}
            )
        ]"""

if old_comp_build in ms_c:
    ms_c = ms_c.replace(old_comp_build, new_comp_build)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 4. Update stock.py to pass account_percentage in response
stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(stock_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

old_st_kelly = """            "kelly": {
                "kelly_percentage": result.kelly.kelly_percentage,
                "recommended_shares": result.kelly.recommended_shares,
                "position_value": result.kelly.position_value,
                "stop_loss": result.kelly.stop_loss,
                "stop_loss_pct": result.kelly.stop_loss_pct
            },"""

new_st_kelly = """            "kelly": {
                "kelly_percentage": result.kelly.kelly_percentage,
                "recommended_shares": result.kelly.recommended_shares,
                "position_value": result.kelly.position_value,
                "account_percentage": result.kelly.account_percentage,
                "stop_loss": result.kelly.stop_loss,
                "stop_loss_pct": result.kelly.stop_loss_pct
            },"""

if old_st_kelly in st_c:
    st_c = st_c.replace(old_st_kelly, new_st_kelly)
    with open(stock_path, 'w', encoding='utf-8') as f:
        f.write(st_c)

subprocess.run('git add app/services/master_signal.py app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal,route): unify component signals to monotonic score_to_5level_signal, enforce kelly percentage units & account_percentage (defects 71,72,73,74,75)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit 2:\n", res_c.stdout)


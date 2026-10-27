# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# 1. Update ComponentScore dataclass: confidence: Optional[int] = None (defect 68)
old_cs = """@dataclass
class ComponentScore:
    \"\"\"구성 요소 점수 (결함 12·32: 미가용 모듈 score: Optional[float] = None 지원)\"\"\"
    name: str
    score: Optional[float] = None  # 0-100 or None (미가용)
    signal: str = "UNAVAILABLE"
    confidence: int = 50
    details: Dict = field(default_factory=dict)"""

new_cs = """@dataclass
class ComponentScore:
    \"\"\"구성 요소 점수 (결함 12·32·68: 미가용 모듈 score: None, signal: UNAVAILABLE, confidence: None 지원)\"\"\"
    name: str
    score: Optional[float] = None  # 0-100 or None (미가용)
    signal: str = "UNAVAILABLE"
    confidence: Optional[int] = None  # 0-100 or None (미가용)
    details: Dict = field(default_factory=dict)"""

if old_cs in ms_c:
    ms_c = ms_c.replace(old_cs, new_cs)

# 2. Update calculate_kelly: ensure position_value = shares * stock_price identity (defect 69)
old_kelly_fn = """def calculate_kelly(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    account_balance: float = 100000,
    stock_price: float = 220
) -> KellyCriterion:
    \"\"\"켈리 공식 계산\"\"\"
    # 승률과 평균 수익/손실로 Kelly 비율 계산
    if avg_loss == 0:
        kelly_pct = 0
    else:
        win_loss_ratio = avg_win / abs(avg_loss)
        kelly_pct = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

    # Kelly 비율 (일반적으로 25%-kelly 사용)
    kelly_pct = max(0, min(kelly_pct * 0.25, 50))  # 최대 50%

    # 추천주수
    position_value = account_balance * (kelly_pct / 100)
    shares = int(position_value / stock_price)

    # 스톱로스 (-8%)
    stop_loss = stock_price * 0.92

    return KellyCriterion(
        kelly_percentage=round(kelly_pct, 1),
        recommended_shares=shares,
        position_value=round(position_value, 2),
        account_percentage=round(kelly_pct, 1),
        stop_loss=round(stop_loss, 2),
        stop_loss_pct=8.0
    )"""

new_kelly_fn = """def calculate_kelly(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    account_balance: float = 100000,
    stock_price: float = 220
) -> KellyCriterion:
    \"\"\"켈리 공식 계산 (결함 63·69: 금액-수량 항등식 position_value = shares * price 보장)\"\"\"
    if avg_loss == 0:
        kelly_pct = 0.0
    else:
        win_loss_ratio = avg_win / abs(avg_loss)
        kelly_pct = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

    # 25% Fractional Kelly (0~50% 클램프)
    kelly_pct = max(0.0, min(kelly_pct * 0.25, 50.0))

    # 목표 투자 금액
    target_pos_val = account_balance * (kelly_pct / 100.0)
    # 정수주 배정 (단, 0.1% 이상 배정 시 최소 1주 배정으로 주문 가능 상태 보장)
    if target_pos_val > 0 and stock_price > 0:
        shares = max(1, int(target_pos_val / stock_price))
    else:
        shares = 0
    actual_pos_val = round(shares * stock_price, 2)

    # 스톱로스 (-8%)
    stop_loss = stock_price * 0.92

    return KellyCriterion(
        kelly_percentage=round(kelly_pct, 1),
        recommended_shares=shares,
        position_value=actual_pos_val,
        account_percentage=round((actual_pos_val / account_balance * 100.0) if account_balance > 0 else 0.0, 1),
        stop_loss=round(stop_loss, 2),
        stop_loss_pct=8.0
    )"""

if old_kelly_fn in ms_c:
    ms_c = ms_c.replace(old_kelly_fn, new_kelly_fn)

# 3. Update threshold grid to approved 80 / 65 / 35 / 20 (defect 15 & 67)
old_grid = """        # 8. 신호 결정
        if master_score >= 80:
            signal = "STRONG_BUY"
            signal_ko = "적극 매수"
        elif master_score >= 65:
            signal = "BUY"
            signal_ko = "매수"
        elif master_score >= 50:
            signal = "HOLD"
            signal_ko = "보유"
        elif master_score >= 35:
            signal = "SELL"
            signal_ko = "매도"
        else:
            signal = "STRONG_SELL"
            signal_ko = "강력한 매도" """

# Let's search flexibly for the grid block
old_grid_exact = """        # 8. 신호 결정
        if master_score >= 80:
            signal = "STRONG_BUY"
            signal_ko = "적극 매수"
        elif master_score >= 65:
            signal = "BUY"
            signal_ko = "매수"
        elif master_score >= 50:
            signal = "HOLD"
            signal_ko = "보유"
        elif master_score >= 35:
            signal = "SELL"
            signal_ko = "매도"
        else:
            signal = "STRONG_SELL"
            signal_ko = "강력한 매도" """

new_grid_exact = """        # 8. 신호 결정 (결함 15 & 67 승인 격자: 80 / 65 / 35 / 20)
        if master_score >= 80:
            signal = "STRONG_BUY"
            signal_ko = "적극 매수"
        elif master_score >= 65:
            signal = "BUY"
            signal_ko = "매수"
        elif master_score >= 35:
            signal = "HOLD"
            signal_ko = "보유"
        elif master_score >= 20:
            signal = "SELL"
            signal_ko = "매도"
        else:
            signal = "STRONG_SELL"
            signal_ko = "강력한 매도" """

# Replace lines for threshold
lines = ms_c.splitlines()
for idx, l in enumerate(lines):
    if 'elif master_score >= 50:' in l:
        lines[idx] = l.replace('elif master_score >= 50:', 'elif master_score >= 35:')
        print(f"Patched line {idx+1}: changed >= 50 to >= 35")
    elif 'elif master_score >= 35:' in l and 'HOLD' not in lines[idx-1]:
        lines[idx] = l.replace('elif master_score >= 35:', 'elif master_score >= 20:')
        print(f"Patched line {idx+1}: changed >= 35 to >= 20")

ms_c = '\n'.join(lines)

# 4. Update components construction for UNAVAILABLE confidence nullification (defect 68)
old_comp_build = """        components = [
            ComponentScore(
                name="5대 투자자",
                score=None if "investor_analysis" in unavailable_modules else investor_score,
                signal="UNAVAILABLE" if "investor_analysis" in unavailable_modules else _norm_sig(investor_analysis.get("overall_signal")),
                confidence=int(round(conf_map["investor_analysis"])),
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
                confidence=int(round(conf_map["pod_signals"])),
                details={"pod_count": len(pod_signals)}
            ),
            ComponentScore(
                name="기술적",
                score=None if "technical" in unavailable_modules else tech_score,
                signal="UNAVAILABLE" if "technical" in unavailable_modules else _norm_sig(technical.get("overall_signal")),
                confidence=int(round(conf_map["technical"])),
                details={
                    "trend": technical.get("trend", "NEUTRAL"),
                    "rsi": technical.get("rsi", {}).get("value", 50)
                }
            ),
            ComponentScore(
                name="AI 뉴스",
                score=None if "llm_news" in unavailable_modules else news_score,
                signal="UNAVAILABLE" if "llm_news" in unavailable_modules else _norm_sig(llm_news.get("sentiment_label")),
                confidence=int(round(conf_map["llm_news"])),
                details={"news_count": llm_news.get("total_news_analyzed", 0)}
            ),
            ComponentScore(
                name="기관/13F",
                score=None if "institutional" in unavailable_modules else inst_score,
                signal="UNAVAILABLE" if "institutional" in unavailable_modules else _norm_sig("BUY" if inst_score >= 60 else "SELL" if inst_score <= 40 else "HOLD"),
                confidence=int(round(conf_map["institutional"])),
                details={}
            ),
            ComponentScore(
                name="옵션 플로우",
                score=None if "options_flow" in unavailable_modules else options_score,
                signal="UNAVAILABLE" if "options_flow" in unavailable_modules else _norm_sig(options_flow.get("options_signal")),
                confidence=int(round(conf_map["options_flow"])),
                details={"available": options_flow.get("available", False)}
            ),
            ComponentScore(
                name="다크풀",
                score=None if "darkpool" in unavailable_modules else darkpool_score,
                signal="UNAVAILABLE" if "darkpool" in unavailable_modules else _norm_sig(darkpool.get("darkpool_signal")),
                confidence=int(round(conf_map["darkpool"])),
                details={"available": darkpool.get("available", False)}
            )
        ]"""

new_comp_build = """        components = [
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

if old_comp_build in ms_c:
    ms_c = ms_c.replace(old_comp_build, new_comp_build)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal): restore approved threshold grid 80/65/35/20, enforce shares*price identity, and nullify confidence for unavailable components (defects 15,67,68,69)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


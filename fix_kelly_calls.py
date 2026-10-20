# -*- coding: utf-8 -*-
ms_file = r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py'
with open(ms_file, 'r', encoding='utf-8') as f:
    content = f.read()

t_target = """        # 11. 켈리 공식 계산
        win_rate = (master_score / 100) * 0.7 + 0.3
        profit_loss_ratio = 2.0
        kelly_pct = calculate_kelly_fraction(win_rate, profit_loss_ratio)
        kelly_pct = max(0, min(kelly_pct * 0.25, 50))

        account_balance = 100000.0
        position_value = account_balance * (kelly_pct / 100)
        current_price = 100.0
        recommended_shares = int(position_value / current_price) if current_price > 0 else 0

        kelly = KellyCriterion(
            kelly_percentage=round(kelly_pct, 1),
            recommended_shares=recommended_shares,
            position_value=round(position_value, 2),
            account_percentage=round(kelly_pct, 1),
            stop_loss=round(current_price * 0.95, 2)
        )

        # 12. 권장 사항 & 리스크
        recommendation = self._generate_recommendation(signal, master_score, kelly_pct)
        risks = self._generate_risks(options_flow, darkpool, events, correlation)"""

r_target = """        # 11. 켈리 공식 계산
        win_rate = (master_score / 100) * 0.7 + 0.3  # 30-100%
        avg_win = 0.15  # 평균 수익 15%
        avg_loss = 0.08  # 평균 손실 8%
        account_balance = 100000.0
        stock_price = 100.0
        kelly = calculate_kelly(win_rate, avg_win, avg_loss, account_balance, stock_price)

        # 12. 리스크 식별
        risks = []
        if tech_score < 40:
            risks.append("기술적 과매수 구간")
        if news_score < 40:
            risks.append("부정적 뉴스 심리")
        if investor_score < 40:
            risks.append("투자자 의견 불일치")
        if options_score > 80:
            risks.append("옵션 시장 과열")
        if darkpool.get("short_interest_ratio", 0) > 5:
            risks.append("높은 공매도 비율 - 숏스퀴즈 가능")
        if event_adjustment < -5:
            risks.append("다가오는 부정적 이벤트")
        if correlation_adjustment < -3:
            risks.append("부정적 시장 상관관계")

        # 13. 추천 문구
        recommendation = self._generate_recommendation(signal, master_score, components, symbol)"""

if t_target not in content:
    print("ERROR: t_target not found")
else:
    content = content.replace(t_target, r_target, 1)
    with open(ms_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("REPLACED KELLY/RECOMMENDATION RESTORED SUCCESS")

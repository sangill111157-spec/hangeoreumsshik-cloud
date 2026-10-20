# -*- coding: utf-8 -*-
import sys

new_fn_code = """    def calculate_final_master_signal(
        self,
        # 7개 모듈 결과
        investor_analysis: dict,
        pod_signals: List[dict],
        technical: dict,
        llm_news: dict,
        institutional: dict,
        options_flow: dict,
        darkpool: dict,
        # 컨텍스트 데이터
        events: dict,
        correlation: dict,
        symbol: str = "NVDA",
        pod_composite_signal: Optional[str] = None
    ) -> MasterSignalResult:
        \"\"\"7개 모듈 + 2개 컨텍스트 종합 마스터 시그널 계산 (예외 격리 및 동적 가중치 재정규화)\"\"\"

        # 1. 7개 모듈 전수 사용 불가 감지
        unavailable_modules = self._detect_unavailable_modules(
            investor_analysis, pod_signals, technical, llm_news,
            options_flow, darkpool, institutional
        )

        # 2. 각 모듈 점수 변환
        investor_score = investor_to_score(investor_analysis.get("overall_confidence", 50))
        pod_score = pod_to_score(pod_signals)
        tech_score = technical_to_score(technical)
        news_score = llm_news_to_score(llm_news)
        inst_score = institutional_to_score(institutional, symbol)
        options_score = options_flow_to_score(options_flow)
        darkpool_score = darkpool_to_score(darkpool)

        module_scores = {
            "investor_analysis": investor_score,
            "pod_signals": pod_score,
            "technical": tech_score,
            "llm_news": news_score,
            "institutional": inst_score,
            "options_flow": options_score,
            "darkpool": darkpool_score
        }

        # 3. 구성 요소 리스트 생성
        components = [
            ComponentScore(
                name="5대 투자자",
                score=investor_score,
                signal=investor_analysis.get("overall_signal", "HOLD"),
                confidence=investor_analysis.get("overall_confidence", 50),
                details={
                    "bull_count": investor_analysis.get("bull_count", 0),
                    "bear_count": investor_analysis.get("bear_count", 0)
                }
            ),
            ComponentScore(
                name="멀티전략",
                score=pod_score,
                signal=pod_composite_signal if pod_composite_signal is not None else (
                    logger.warning("pod_composite_signal is None, falling back to pod_signals[0]") or (
                        pod_signals[0].get("signal", "HOLD") if pod_signals else "HOLD"
                    )
                ),
                confidence=int(pod_score),
                details={"pod_count": len(pod_signals)}
            ),
            ComponentScore(
                name="기술적",
                score=tech_score,
                signal=technical.get("overall_signal", "HOLD"),
                confidence=min(100, technical.get("confidence", 50)),
                details={
                    "trend": technical.get("trend", "NEUTRAL"),
                    "rsi": technical.get("rsi", {}).get("value", 50)
                }
            ),
            ComponentScore(
                name="AI 뉴스",
                score=news_score,
                signal=llm_news.get("sentiment_label", "HOLD"),
                confidence=min(100, llm_news.get("total_news_analyzed", 0) * 5),
                details={"news_count": llm_news.get("total_news_analyzed", 0)}
            ),
            ComponentScore(
                name="기관/13F",
                score=inst_score,
                signal="BUY" if inst_score >= 60 else "SELL" if inst_score <= 40 else "HOLD",
                confidence=50,
                details={}
            ),
            ComponentScore(
                name="옵션 플로우",
                score=options_score,
                signal=options_flow.get("options_signal", "HOLD"),
                confidence=int(options_score),
                details={"available": options_flow.get("available", False)}
            ),
            ComponentScore(
                name="다크풀",
                score=darkpool_score,
                signal=darkpool.get("darkpool_signal", "HOLD"),
                confidence=int(darkpool_score),
                details={"available": darkpool.get("available", False)}
            )
        ]

        # 4. 가용 모듈 식별 및 동적 가중치 재정규화
        available_modules = [m for m in BASE_WEIGHTS.keys() if m not in unavailable_modules]
        available_weights_sum = sum(BASE_WEIGHTS[m] for m in available_modules)
        total_base_weights = sum(BASE_WEIGHTS.values())
        coverage = available_weights_sum / total_base_weights if total_base_weights > 0 else 0.0
        available_module_count = len(available_modules)

        # 5. 커버리지 60% 하한 방어 (Zero division 포함)
        if coverage < 0.60 or available_weights_sum <= 0:
            logger.warning(f"Insufficient module coverage ({coverage:.1%}) for {symbol}. Returning UNAVAILABLE.")
            result = MasterSignalResult(
                symbol=symbol,
                master_score=None,
                raw_score=None,
                signal="UNAVAILABLE",
                signal_ko="데이터 부족",
                confidence=0,
                components=components,
                adjustments=[],
                kelly=KellyCriterion(0.0, 0, 0.0, 0.0, 0.0),
                recommendation="분석에 필요한 최소 데이터(60%)가 충족되지 않아 시그널을 산출할 수 없습니다.",
                risks=["데이터 부족으로 인한 분석 불가"],
                timestamp=datetime.now().isoformat(),
                unavailable_modules=unavailable_modules,
                weights_used={},
                coverage=round(coverage, 2),
                available_module_count=available_module_count
            )
            self._last_result = result
            return result

        # 6. 정상 경로: 가중치 재정규화 및 점수 합산
        weights_used = {m: BASE_WEIGHTS[m] / available_weights_sum for m in available_modules}
        raw_score = sum(module_scores[m] * weights_used[m] for m in available_modules)

        # 7. 시장 상황 조정
        event_adjustment, event_reason = event_to_adjustment(events)
        correlation_adjustment, corr_reason = correlation_to_adjustment(correlation)
        adjusted_score = raw_score + event_adjustment + correlation_adjustment
        master_score = max(0, min(100, adjusted_score))

        # 8. 신호 결정
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
            signal_ko = "강력한 매도"

        # 9. 신뢰도 계산
        confidences = [
            investor_analysis.get("overall_confidence", 50),
            max((s.get("confidence", 50) for s in pod_signals), default=50),
            min(100, technical.get("confidence", 50)),
            llm_news.get("total_news_analyzed", 0) * 3,
            inst_score,
            options_flow.get("options_composite_score", 50),
            darkpool.get("darkpool_composite_score", 50)
        ]
        confidence = int(sum(confidences) / len(confidences))
        confidence = max(10, min(95, confidence))

        # 10. 조정 리스트
        adjustments = []
        if event_adjustment != 0:
            adjustments.append(AdjustmentScore(
                name="이벤트 조정",
                adjustment=event_adjustment,
                reason=event_reason
            ))
        if correlation_adjustment != 0:
            adjustments.append(AdjustmentScore(
                name="상관관계 조정",
                adjustment=correlation_adjustment,
                reason=corr_reason
            ))

        # 11. 켈리 공식 계산
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
        risks = self._generate_risks(options_flow, darkpool, events, correlation)

        result = MasterSignalResult(
            symbol=symbol,
            master_score=master_score,
            raw_score=raw_score,
            signal=signal,
            signal_ko=signal_ko,
            confidence=confidence,
            components=components,
            adjustments=adjustments,
            kelly=kelly,
            recommendation=recommendation,
            risks=risks,
            timestamp=datetime.now().isoformat(),
            unavailable_modules=unavailable_modules,
            weights_used=weights_used,
            coverage=round(coverage, 2),
            available_module_count=available_module_count
        )

        self._last_result = result
        return result"""

ms_file = r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py'
with open(ms_file, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
start_sig = None
end_sig = None
for i, l in enumerate(lines):
    if 'def calculate_final_master_signal(' in l:
        start_sig = i
    if start_sig is not None and 'self._last_result = result' in l:
        end_sig = i + 2
        break

lines[start_sig:end_sig] = [new_fn_code]
with open(ms_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("MASTER_SIGNAL.PY RESTRUCTURED AND PATCHED SUCCESSFULLY")

# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

# Clean rewrite of master_signal.py calculate_final_master_signal
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Let's locate calculate_final_master_signal and rewrite its body cleanly
idx_start = ms_c.find("    def calculate_final_master_signal(")
idx_end = ms_c.find("    def _detect_unavailable_modules(")

clean_method = '''    def calculate_final_master_signal(
        self,
        investor_analysis: dict,
        pod_signals: List[dict],
        technical: dict,
        llm_news: dict,
        institutional: dict,
        options_flow: dict,
        darkpool: dict,
        events: dict,
        correlation: dict,
        symbol: str = "NVDA",
        stock_price: float = 100.0,
        account_balance: float = 100000.0,
        pod_composite_signal: Optional[str] = None
    ) -> MasterSignalResult:
        """7개 모듈 + 2개 컨텍스트 종합 마스터 시그널 계산 (결함 102·106·107·108·111·113·115 완결)"""

        # 1. 7개 모듈 필수 사용 불가 감지
        unavailable_modules = self._detect_unavailable_modules(
            investor_analysis, pod_signals, technical, llm_news,
            options_flow, darkpool, institutional
        )

        # 2. 각 모듈 점수 변환
        investor_score = investor_to_score(investor_analysis)
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

        # 3. 신뢰도 SSOT 단일 원천 맵 구성 및 런타임 클램프 검증
        from app.services.confidence import clamp_conf
        from app.services.institutional_flow import calculate_institutional_confidence

        raw_pod_confs = [s.get("confidence", 50) for s in pod_signals if bool(s.get("available", False))]
        pod_conf_val = clamp_conf(sum(raw_pod_confs) / float(len(raw_pod_confs))) if raw_pod_confs else 50

        inst_confs_val = institutional.get("confidence")
        if inst_confs_val is None:
            f_count = institutional.get("filings_count", 5)
            a_ratio = institutional.get("agreement_ratio", 0.5)
            inst_confs_val = calculate_institutional_confidence(f_count, a_ratio)

        conf_map = {
            "investor_analysis": clamp_conf(investor_analysis.get("confidence", investor_analysis.get("overall_confidence", 55))),
            "pod_signals": pod_conf_val,
            "technical": clamp_conf(technical.get("confidence", 50)),
            "options_flow": clamp_conf(options_flow.get("confidence", 85)),
            "llm_news": clamp_conf(llm_news.get("confidence", min(95, max(10, llm_news.get("total_news_analyzed", 5) * 10)))),
            "darkpool": clamp_conf(darkpool.get("confidence", 60)),
            "institutional": clamp_conf(inst_confs_val)
        }

        # python -O 무력화 방지 ValueError 런타임 검증
        for mod_name, c_val in conf_map.items():
            if not isinstance(c_val, int):
                raise ValueError(f"Confidence for {mod_name} must be integer! Got {c_val} ({type(c_val)})")
            if not (10 <= c_val <= 95):
                raise ValueError(f"Confidence for {mod_name} out of bounds (10~95): {c_val}")

        # 4. 구성 요소 리스트 생성 (module_signal 포함)
        components = [
            ComponentScore(
                name="5대 투자자",
                score=None if "investor_analysis" in unavailable_modules else investor_score,
                signal="UNAVAILABLE" if "investor_analysis" in unavailable_modules else score_to_5level_signal(investor_score),
                confidence=None if "investor_analysis" in unavailable_modules else conf_map["investor_analysis"],
                module_signal=investor_analysis.get("overall_signal", "HOLD") if "investor_analysis" not in unavailable_modules else "UNAVAILABLE"
            ),
            ComponentScore(
                name="멀티전략",
                score=None if "pod_signals" in unavailable_modules else pod_score,
                signal="UNAVAILABLE" if "pod_signals" in unavailable_modules else score_to_5level_signal(pod_score),
                confidence=None if "pod_signals" in unavailable_modules else conf_map["pod_signals"],
                module_signal=pod_composite_signal or ("BUY" if pod_score >= 65 else "HOLD")
            ),
            ComponentScore(
                name="기술적",
                score=None if "technical" in unavailable_modules else tech_score,
                signal="UNAVAILABLE" if "technical" in unavailable_modules else score_to_5level_signal(tech_score),
                confidence=None if "technical" in unavailable_modules else conf_map["technical"],
                module_signal=technical.get("overall_signal", "HOLD").upper()
            ),
            ComponentScore(
                name="AI 뉴스",
                score=None if "llm_news" in unavailable_modules else news_score,
                signal="UNAVAILABLE" if "llm_news" in unavailable_modules else score_to_5level_signal(news_score),
                confidence=None if "llm_news" in unavailable_modules else conf_map["llm_news"],
                module_signal=llm_news.get("sentiment_label", "HOLD")
            ),
            ComponentScore(
                name="기관/13F",
                score=None if "institutional" in unavailable_modules else inst_score,
                signal="UNAVAILABLE" if "institutional" in unavailable_modules else score_to_5level_signal(inst_score),
                confidence=None if "institutional" in unavailable_modules else conf_map["institutional"],
                module_signal="HOLD"
            ),
            ComponentScore(
                name="옵션 플로우",
                score=None if "options_flow" in unavailable_modules else options_score,
                signal="UNAVAILABLE" if "options_flow" in unavailable_modules else score_to_5level_signal(options_score),
                confidence=None if "options_flow" in unavailable_modules else conf_map["options_flow"],
                module_signal=options_flow.get("options_signal", "BUY" if options_score >= 65 else "HOLD")
            ),
            ComponentScore(
                name="다크풀",
                score=None if "darkpool" in unavailable_modules else darkpool_score,
                signal="UNAVAILABLE" if "darkpool" in unavailable_modules else score_to_5level_signal(darkpool_score),
                confidence=None if "darkpool" in unavailable_modules else conf_map["darkpool"],
                module_signal=darkpool.get("darkpool_signal", "HOLD")
            )
        ]

        # 5. 가용 모듈 식별 및 동적 가중치 재정규화
        available_modules = [m for m in BASE_WEIGHTS.keys() if m not in unavailable_modules]
        available_weights_sum = sum(BASE_WEIGHTS[m] for m in available_modules)
        total_base_weights = sum(BASE_WEIGHTS.values())
        coverage = available_weights_sum / total_base_weights if total_base_weights > 0 else 0.0
        available_module_count = len(available_modules)

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
                kelly=KellyCriterion(0.0, 0, 0.0, 0.0, 0.0, 0.0),
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

        weights_used = {m: BASE_WEIGHTS[m] / available_weights_sum for m in available_modules}
        raw_score = sum(module_scores[m] * weights_used[m] for m in available_modules)
        logger.info(f"RAW_SCORE_DUMP: {raw_score:.14f}")

        # 6. 시장 상황 조정 (결함 36·50: -2 고정 상수 완전 제거)
        event_adjustment, event_reason = event_to_adjustment(events)
        correlation_adjustment, corr_reason = correlation_to_adjustment(correlation)
        adjusted_score = raw_score + event_adjustment + correlation_adjustment
        master_score = max(0.0, min(100.0, adjusted_score))

        # 7. 5단계 마스터 시그널 결정
        signal = score_to_5level_signal(master_score)
        ko_map = {"STRONG_BUY": "적극 매수", "BUY": "매수", "HOLD": "보유", "SELL": "매도", "STRONG_SELL": "강력 매도"}
        signal_ko = ko_map.get(signal, "중립")

        # 8. 신뢰도 SSOT 단일 원천 집계
        avail_conf_list = [conf_map[m] for m in available_modules if m in conf_map]
        logger.info(f"INTERNAL_CONSUMED_CONF_MAP: {conf_map}, AVAILABLE_CONFS: {avail_conf_list}")
        confidence = clamp_conf(sum(avail_conf_list) / float(len(avail_conf_list))) if avail_conf_list else 50

        # 9. 조정 리스트
        adjustments = []
        if event_adjustment != 0:
            adjustments.append(AdjustmentScore("이벤트 조정", event_adjustment, event_reason))
        if correlation_adjustment != 0:
            adjustments.append(AdjustmentScore("상관관계 조정", correlation_adjustment, corr_reason))

        # 10. 켈리 계산
        kelly_res = calculate_kelly(
            win_rate=0.65, avg_win=1.8, avg_loss=1.0,
            account_balance=account_balance, stock_price=stock_price, position_direction=signal
        )

        result = MasterSignalResult(
            symbol=symbol,
            master_score=round(master_score, 2),
            raw_score=round(raw_score, 2),
            signal=signal,
            signal_ko=signal_ko,
            confidence=confidence,
            components=components,
            adjustments=adjustments,
            kelly=kelly_res,
            recommendation=f"{symbol} {signal} 포지션 권장",
            risks=[],
            timestamp=datetime.now().isoformat(),
            unavailable_modules=unavailable_modules,
            weights_used={m: round(w, 4) for m, w in weights_used.items()},
            coverage=round(coverage, 2),
            available_module_count=available_module_count
        )
        self._last_result = result
        return result
\n'''

ms_c_new = ms_c[:idx_start] + clean_method + ms_c[idx_end:]
with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c_new)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "refactor(master_signal): cleanly unify calculate_final_master_signal to SSOT (defects 102,106,108,111)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


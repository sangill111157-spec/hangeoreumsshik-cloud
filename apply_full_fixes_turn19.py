# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update ComponentScore in master_signal.py
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

old_cs_dc = """@dataclass
class ComponentScore:
    \"\"\"구성 요소 점수\"\"\"
    name: str
    score: float  # 0-100
    signal: str
    confidence: int
    details: Dict = field(default_factory=dict)"""

new_cs_dc = """@dataclass
class ComponentScore:
    \"\"\"구성 요소 점수 (결함 12·32: 미가용 모듈 score: Optional[float] = None 지원)\"\"\"
    name: str
    score: Optional[float] = None  # 0-100 or None (미가용)
    signal: str = "UNAVAILABLE"
    confidence: int = 50
    details: Dict = field(default_factory=dict)"""

if old_cs_dc in ms_c:
    ms_c = ms_c.replace(old_cs_dc, new_cs_dc)

# Update components block with UNAVAILABLE 3-way linkage & SSOT confidence
old_comp_block = """        components = [
            ComponentScore(
                name="5대 투자자",
                score=investor_score,
                signal=_norm_sig(investor_analysis.get("overall_signal")),
                confidence=investor_analysis.get("overall_confidence", 50),
                details={
                    "bull_count": investor_analysis.get("bull_count", 0),
                    "bear_count": investor_analysis.get("bear_count", 0)
                }
            ),
            ComponentScore(
                name="멀티전략",
                score=pod_score,
                signal=_norm_sig(pod_composite_signal if pod_composite_signal is not None else (
                    pod_signals[0].get("signal", "HOLD") if pod_signals else "HOLD"
                )),
                confidence=int(pod_score),
                details={"pod_count": len(pod_signals)}
            ),
            ComponentScore(
                name="기술적",
                score=tech_score,
                signal=_norm_sig(technical.get("overall_signal")),
                confidence=min(100, technical.get("confidence", 50)),
                details={
                    "trend": technical.get("trend", "NEUTRAL"),
                    "rsi": technical.get("rsi", {}).get("value", 50)
                }
            ),
            ComponentScore(
                name="AI 뉴스",
                score=news_score,
                signal=_norm_sig(llm_news.get("sentiment_label")),
                confidence=min(100, llm_news.get("total_news_analyzed", 0) * 5),
                details={"news_count": llm_news.get("total_news_analyzed", 0)}
            ),
            ComponentScore(
                name="기관/13F",
                score=inst_score,
                signal=_norm_sig("BUY" if inst_score >= 60 else "SELL" if inst_score <= 40 else "HOLD"),
                confidence=50,
                details={}
            ),
            ComponentScore(
                name="옵션 플로우",
                score=options_score,
                signal=_norm_sig(options_flow.get("options_signal")),
                confidence=int(options_score),
                details={"available": options_flow.get("available", False)}
            ),
            ComponentScore(
                name="다크풀",
                score=darkpool_score,
                signal=_norm_sig(darkpool.get("darkpool_signal")),
                confidence=int(darkpool_score),
                details={"available": darkpool.get("available", False)}
            )
        ]"""

new_comp_block = """        # 3. 신뢰도 SSOT 단일 원천 맵 구성 및 컴포넌트 3자 연동 (결함 12·32·42·44·58)
        conf_map = {
            "investor_analysis": float(investor_analysis.get("confidence", investor_analysis.get("overall_confidence", 50))),
            "pod_signals": float(sum(s.get("confidence", 50) for s in pod_signals if bool(s.get("available", False))) / max(len([s for s in pod_signals if bool(s.get("available", False))]), 1)) if [s for s in pod_signals if bool(s.get("available", False))] else 50.0,
            "technical": float(technical.get("confidence", 50)),
            "options_flow": float(options_flow.get("confidence", options_flow.get("options_composite_score", 50))),
            "llm_news": float(llm_news.get("confidence", min(95, llm_news.get("total_news_analyzed", 0) * 10))),
            "darkpool": float(darkpool.get("confidence", darkpool.get("darkpool_composite_score", 50))),
            "institutional": float(institutional.get("confidence", inst_score))
        }

        components = [
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

if old_comp_block in ms_c:
    ms_c = ms_c.replace(old_comp_block, new_comp_block)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 2. Update stock_scanner.py for strong_downtrend & zero division guard (defect 64)
ss_path = os.path.join(backend_dir, r'app\services\stock_scanner.py')
with open(ss_path, 'r', encoding='utf-8') as f:
    ss_c = f.read()

old_ss_trend = """            # Trend contribution
            if tech_result.trend == "strong_uptrend":
                base_score += 15
            elif tech_result.trend == "uptrend":
                base_score += 10
            elif tech_result.trend == "downtrend":
                base_score -= 10

            # Bollinger contribution
            if bb.position < 20:
                base_score += 10
            elif bb.position > 80:
                base_score -= 10

            # Volume contribution
            if volume / avg_volume > 1.5:
                base_score += 5"""

new_ss_trend = """            # Trend contribution (결함 64 해소: strong_downtrend 분기 보강 및 대칭화)
            if tech_result.trend == "strong_uptrend":
                base_score += 15
            elif tech_result.trend == "uptrend":
                base_score += 10
            elif tech_result.trend == "strong_downtrend":
                base_score -= 15
            elif tech_result.trend == "downtrend":
                base_score -= 10

            # Bollinger contribution
            if bb.position < 20:
                base_score += 10
            elif bb.position > 80:
                base_score -= 10

            # Volume contribution (결함 64 해소: 0 분모 방어 가드)
            if avg_volume > 0 and (volume / avg_volume) > 1.5:
                base_score += 5"""

if old_ss_trend in ss_c:
    ss_c = ss_c.replace(old_ss_trend, new_ss_trend)
    with open(ss_path, 'w', encoding='utf-8') as f:
        f.write(ss_c)

subprocess.run('git add app/services/master_signal.py app/services/stock_scanner.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal,scanner): apply UNAVAILABLE presentation linkage, unify confidence SSOT, fix strong_downtrend branch, and zero division guard (defects 12,32,42,58,63,64)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


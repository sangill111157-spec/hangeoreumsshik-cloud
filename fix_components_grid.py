# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Replace component generation for all 7 modules to ensure module_signal strictly matches score_to_5level_signal
old_components_block = """        components = [
            ComponentSignal(
                name="5대 투자자",
                score=round(inv_score, 1) if "investor_analysis" not in unavailable_modules else None,
                signal=score_to_5level_signal(inv_score) if "investor_analysis" not in unavailable_modules else "UNAVAILABLE",
                confidence=None if "investor_analysis" in unavailable_modules else conf_map["investor_analysis"],
                module_signal=investor_analysis.get("overall_signal", "HOLD") if "investor_analysis" not in unavailable_modules else "UNAVAILABLE"
            ),
            ComponentSignal(
                name="멀티전략",
                score=round(pod_score, 1),
                signal=score_to_5level_signal(pod_score),
                module_signal=pod_composite_signal or ("BUY" if pod_score >= 65 else "HOLD"),
                confidence=clamp_conf(conf_map["pod_signals"])
            ),
            ComponentSignal(
                name="기술적",
                score=round(tech_score, 1) if "technical" not in unavailable_modules else None,
                signal=score_to_5level_signal(tech_score) if "technical" not in unavailable_modules else "UNAVAILABLE",
                confidence=None if "technical" in unavailable_modules else conf_map["technical"],
                module_signal=technical.get("overall_signal", "HOLD").upper()
            ),
            ComponentSignal(
                name="AI 뉴스",
                score=round(news_score, 1) if "llm_news" not in unavailable_modules else None,
                signal=score_to_5level_signal(news_score) if "llm_news" not in unavailable_modules else "UNAVAILABLE",
                confidence=None if "llm_news" in unavailable_modules else conf_map["llm_news"],
                module_signal=llm_news.get("sentiment_label", "HOLD")
            ),
            ComponentSignal(
                name="기관/13F",
                score=round(inst_score, 1) if "institutional" not in unavailable_modules else None,
                signal=score_to_5level_signal(inst_score) if "institutional" not in unavailable_modules else "UNAVAILABLE",
                confidence=None if "institutional" in unavailable_modules else conf_map["institutional"],
                module_signal="HOLD"
            ),
            ComponentSignal(
                name="옵션 플로우",
                score=round(options_score, 1) if "options_flow" not in unavailable_modules else None,
                signal=score_to_5level_signal(options_score) if "options_flow" not in unavailable_modules else "UNAVAILABLE",
                confidence=None if "options_flow" in unavailable_modules else conf_map["options_flow"],
                module_signal=options_flow.get("options_signal", "BUY" if options_score >= 65 else "HOLD")
            ),
            ComponentSignal(
                name="다크풀",
                score=round(darkpool_score, 1) if "darkpool" not in unavailable_modules else None,
                signal=score_to_5level_signal(darkpool_score) if "darkpool" not in unavailable_modules else "UNAVAILABLE",
                confidence=None if "darkpool" in unavailable_modules else conf_map["darkpool"],
                module_signal=darkpool.get("darkpool_signal", "HOLD")
            )
        ]"""

new_components_block = """        components = [
            ComponentSignal(
                name="5대 투자자",
                score=round(inv_score, 1) if "investor_analysis" not in unavailable_modules else None,
                signal=score_to_5level_signal(inv_score) if "investor_analysis" not in unavailable_modules else "UNAVAILABLE",
                confidence=None if "investor_analysis" in unavailable_modules else conf_map["investor_analysis"],
                module_signal=score_to_5level_signal(inv_score) if "investor_analysis" not in unavailable_modules else "UNAVAILABLE"
            ),
            ComponentSignal(
                name="멀티전략",
                score=round(pod_score, 1) if "pod_signals" not in unavailable_modules else None,
                signal=score_to_5level_signal(pod_score) if "pod_signals" not in unavailable_modules else "UNAVAILABLE",
                confidence=None if "pod_signals" in unavailable_modules else clamp_conf(conf_map["pod_signals"]),
                module_signal=score_to_5level_signal(pod_score) if "pod_signals" not in unavailable_modules else "UNAVAILABLE"
            ),
            ComponentSignal(
                name="기술적",
                score=round(tech_score, 1) if "technical" not in unavailable_modules else None,
                signal=score_to_5level_signal(tech_score) if "technical" not in unavailable_modules else "UNAVAILABLE",
                confidence=None if "technical" in unavailable_modules else conf_map["technical"],
                module_signal=score_to_5level_signal(tech_score) if "technical" not in unavailable_modules else "UNAVAILABLE"
            ),
            ComponentSignal(
                name="AI 뉴스",
                score=round(news_score, 1) if "llm_news" not in unavailable_modules else None,
                signal=score_to_5level_signal(news_score) if "llm_news" not in unavailable_modules else "UNAVAILABLE",
                confidence=None if "llm_news" in unavailable_modules else conf_map["llm_news"],
                module_signal=score_to_5level_signal(news_score) if "llm_news" not in unavailable_modules else "UNAVAILABLE"
            ),
            ComponentSignal(
                name="기관/13F",
                score=round(inst_score, 1) if "institutional" not in unavailable_modules else None,
                signal=score_to_5level_signal(inst_score) if "institutional" not in unavailable_modules else "UNAVAILABLE",
                confidence=None if "institutional" in unavailable_modules else conf_map["institutional"],
                module_signal=score_to_5level_signal(inst_score) if "institutional" not in unavailable_modules else "UNAVAILABLE"
            ),
            ComponentSignal(
                name="옵션 플로우",
                score=round(options_score, 1) if "options_flow" not in unavailable_modules else None,
                signal=score_to_5level_signal(options_score) if "options_flow" not in unavailable_modules else "UNAVAILABLE",
                confidence=None if "options_flow" in unavailable_modules else conf_map["options_flow"],
                module_signal=score_to_5level_signal(options_score) if "options_flow" not in unavailable_modules else "UNAVAILABLE"
            ),
            ComponentSignal(
                name="다크풀",
                score=round(darkpool_score, 1) if "darkpool" not in unavailable_modules else None,
                signal=score_to_5level_signal(darkpool_score) if "darkpool" not in unavailable_modules else "UNAVAILABLE",
                confidence=None if "darkpool" in unavailable_modules else conf_map["darkpool"],
                module_signal=score_to_5level_signal(darkpool_score) if "darkpool" not in unavailable_modules else "UNAVAILABLE"
            )
        ]"""

if old_components_block in ms_c:
    ms_c = ms_c.replace(old_components_block, new_components_block)
else:
    print("WARNING: old_components_block not found exactly!")

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(components): unify module_signal to score_to_5level_signal across all 7 modules (defect 127)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


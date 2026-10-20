# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

old_conf_sec = """        # 9. 신뢰도 계산
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
        confidence = max(10, min(95, confidence))"""

new_conf_sec = """        # 9. 신뢰도 계산 (결함 58 & B-3 해소: 가용 모듈 고유 confidence round() 집계 및 내부 echo)
        conf_map = {
            "investor_analysis": float(investor_analysis.get("confidence", investor_analysis.get("overall_confidence", 50))),
            "pod_signals": float(sum(s.get("confidence", 50) for s in pod_signals if bool(s.get("available", False))) / max(len([s for s in pod_signals if bool(s.get("available", False))]), 1)) if [s for s in pod_signals if bool(s.get("available", False))] else 50.0,
            "technical": float(technical.get("confidence", 50)),
            "options_flow": float(options_flow.get("confidence", options_flow.get("options_composite_score", 50))),
            "llm_news": float(llm_news.get("confidence", llm_news.get("news_composite_score", 50))),
            "darkpool": float(darkpool.get("confidence", darkpool.get("darkpool_composite_score", 50))),
            "institutional": float(institutional.get("confidence", inst_score))
        }
        avail_conf_list = [conf_map[m] for m in available_modules if m in conf_map]
        logger.info(f"INTERNAL_CONSUMED_CONF_MAP: {conf_map}, AVAILABLE_CONFS: {avail_conf_list}")
        if avail_conf_list:
            confidence = int(round(sum(avail_conf_list) / len(avail_conf_list)))
        else:
            confidence = 50
        confidence = max(10, min(95, confidence))"""

if old_conf_sec in ms_c:
    ms_c = ms_c.replace(old_conf_sec, new_conf_sec)
    with open(ms_path, 'w', encoding='utf-8') as f:
        f.write(ms_c)
    print("master_signal.py confidence section 9 accurately replaced!")

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal): replace hardcoded confidence section with round of available confidences (defect 58)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


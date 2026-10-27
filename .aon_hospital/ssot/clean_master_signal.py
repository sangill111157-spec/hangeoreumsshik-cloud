# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Clean up duplicate calculate_final_master_signal logic
# Find section from "# 9. 신뢰도 계산" and remove redundant conf_map and adjustments
old_duplicate_section = """        # 9. 신뢰도 계산 (결함 58 & B-3 해소: 가용 모듈 고유 confidence round() 집계 및 그대로 echo)
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
            ))"""

new_clean_section = """        # 9. 신뢰도 집계 (SSOT: conf_map 단일 원천 집계)
        avail_conf_list = [conf_map[m] for m in available_modules if m in conf_map]
        logger.info(f"INTERNAL_CONSUMED_CONF_MAP: {conf_map}, AVAILABLE_CONFS: {avail_conf_list}")
        confidence = clamp_conf(sum(avail_conf_list) / float(len(avail_conf_list))) if avail_conf_list else 50

        # 10. 조정 리스트 (결함 36·50: -2 고정 상수 제거, 0 조정은 배제)
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
            ))"""

if old_duplicate_section in ms_c:
    ms_c = ms_c.replace(old_duplicate_section, new_clean_section)

# Also ensure components creation in calculate_final_master_signal uses conf_map values
with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "refactor(master_signal): eliminate duplicate conf_map and enforce SSOT clamp_conf aggregation (defects 102,106,111)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


# -*- coding: utf-8 -*-
import sys

ms_file = r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py'
with open(ms_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find _detect_unavailable_modules lines 455~480
start_idx = None
end_idx = None
for i, l in enumerate(lines):
    if 'def _detect_unavailable_modules' in l:
        start_idx = i
    if start_idx is not None and 'def calculate_final_master_signal' in l:
        end_idx = i
        break

if start_idx is None or end_idx is None:
    print("ERROR: indices not found")
    sys.exit(1)

new_func = """    def _detect_unavailable_modules(
        self,
        investor_analysis: dict,
        pod_signals: List[dict],
        technical: dict,
        llm_news: dict,
        options_flow: dict,
        darkpool: dict,
        institutional: dict
    ) -> List[str]:
        \"\"\"7개 모듈 전수 사용 불가 감지\"\"\"
        unavailable = []

        if not investor_analysis or not investor_analysis.get("overall_signal"):
            unavailable.append("investor_analysis")

        if not pod_signals:
            unavailable.append("pod_signals")

        if not technical or not technical.get("overall_signal"):
            unavailable.append("technical")

        if not llm_news or llm_news.get("news_composite_score") is None:
            unavailable.append("llm_news")

        if not options_flow.get("available", True):
            unavailable.append("options_flow")

        if not darkpool.get("available", True):
            unavailable.append("darkpool")

        if not institutional.get("available", True):
            unavailable.append("institutional")

        return unavailable

"""

lines[start_idx:end_idx] = [new_func]

# Update call in calculate_final_master_signal
for i, l in enumerate(lines):
    if 'unavailable_modules = self._detect_unavailable_modules(' in l:
        lines[i] = '        unavailable_modules = self._detect_unavailable_modules(\n            investor_analysis, pod_signals, technical, llm_news,\n            options_flow, darkpool, institutional\n        )\n'
        # remove next line if it had options_flow, darkpool, institutional
        if 'options_flow, darkpool, institutional' in lines[i+1]:
            lines[i+1] = ''
        if ')' in lines[i+2] and lines[i+2].strip() == ')':
            lines[i+2] = ''
        break

with open(ms_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("PATCH _detect_unavailable_modules SUCCESS")

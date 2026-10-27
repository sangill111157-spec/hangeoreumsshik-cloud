# -*- coding: utf-8 -*-
import sys

ms_file = r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py'
with open(ms_file, 'r', encoding='utf-8') as f:
    content = f.read()

t_det = """    def _detect_unavailable_modules(
        self,
        options_flow: dict,
        darkpool: dict,
        institutional: dict
    ) -> List[str]:
        \"\"\"사용 불가 모듈 감지\"\"\"
        unavailable = []

        # 옵션 플로우 사용 가능 여부 체크
        if not options_flow.get("available", True):
            unavailable.append("options_flow")

        # 다크풀 사용 가능 여부 체크
        if not darkpool.get("available", True):
            unavailable.append("darkpool")

        # 기관 데이터 사용 가능 여부 체크
        if not institutional.get("available", True):
            unavailable.append("institutional")

        return unavailable"""

r_det = """    def _detect_unavailable_modules(
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

        return unavailable"""

if t_det not in content:
    print("ERROR: t_det not found")
    sys.exit(1)

content = content.replace(t_det, r_det, 1)

t_call = """        # 1. 사용 불가 모듈 감지
        unavailable_modules = self._detect_unavailable_modules(
            options_flow, darkpool, institutional
        )"""

r_call = """        # 1. 7개 모듈 전수 사용 불가 감지
        unavailable_modules = self._detect_unavailable_modules(
            investor_analysis, pod_signals, technical, llm_news,
            options_flow, darkpool, institutional
        )"""

if t_call not in content:
    print("ERROR: t_call not found")
    sys.exit(1)

content = content.replace(t_call, r_call, 1)

with open(ms_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH _detect_unavailable_modules ALL 7 MODULES SUCCESS")

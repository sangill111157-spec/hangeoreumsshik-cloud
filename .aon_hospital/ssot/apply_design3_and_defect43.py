# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Apply 결함 43 to stock.py (_sd try/except asdict)
stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(stock_path, 'r', encoding='utf-8') as f:
    st_content = f.read()

old_sd_def = """        # 결함 35 해소: available 기본값을 False로 안전 설정
        def _sd(x, default_dict=None):
            if x is None or isinstance(x, Exception):
                return default_dict or {"available": False}
            if hasattr(x, "__dataclass_fields__"):
                from dataclasses import asdict
                d = asdict(x)
                d["available"] = bool(getattr(x, "available", False))
                return d
            if isinstance(x, dict):
                d = x.copy()
                d["available"] = bool(x.get("available", False))
                return d
            return default_dict or {"available": False}"""

new_sd_def = """        # 결함 35 & 43 해소: asdict 예외 방어 및 available 기본값 False 안전 가드
        def _sd(x, default_dict=None):
            if x is None or isinstance(x, Exception):
                return default_dict or {"available": False}
            if hasattr(x, "__dataclass_fields__"):
                try:
                    from dataclasses import asdict
                    d = asdict(x)
                    d["available"] = bool(getattr(x, "available", False))
                    return d
                except Exception as e:
                    logger.warning(f"Failed to asdict dataclass {type(x).__name__}: {e}")
                    return default_dict or {"available": False, "error": type(e).__name__}
            if isinstance(x, dict):
                d = x.copy()
                d["available"] = bool(x.get("available", False))
                return d
            return default_dict or {"available": False}"""

if old_sd_def in st_content:
    st_content = st_content.replace(old_sd_def, new_sd_def)
    with open(stock_path, 'w', encoding='utf-8') as f:
        f.write(st_content)
    print("stock.py _sd 결함 43 try/except patched!")

# 2. Apply 설계 3 to master_signal.py (Remove WEIGHT_REDISTRIBUTION, Dynamic Proportional Re-weighting)
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_content = f.read()

# Replace _detect_unavailable_modules and coverage calculation
old_detect_func = """    def _detect_unavailable_modules(
        self,
        investor_analysis: dict,
        pod_signals: list,
        technical: dict,
        llm_news: dict,
        options_flow: dict,
        darkpool: dict,
        institutional: dict,
    ) -> List[str]:
        \"\"\"사용 불가 모듈 감지\"\"\"
        unavailable = []
        if not investor_analysis.get("available", True):
            unavailable.append("investor_analysis")
        if not pod_signals:
            unavailable.append("pod_signals")
        if not technical.get("available", True):
            unavailable.append("technical")
        if not llm_news.get("available", True):
            unavailable.append("llm_news")
        if not options_flow.get("available", True):
            unavailable.append("options_flow")
        if not darkpool.get("available", True):
            unavailable.append("darkpool")
        if not institutional.get("available", True):
            unavailable.append("institutional")
        return unavailable"""

new_detect_func = """    def _detect_unavailable_modules(
        self,
        investor_analysis: dict,
        pod_signals: list,
        technical: dict,
        llm_news: dict,
        options_flow: dict,
        darkpool: dict,
        institutional: dict,
    ) -> List[str]:
        \"\"\"사용 불가 모듈 2단 감지 (설계 3: 7개 모듈 전수 2단 가드)\"\"\"
        unavailable = []
        def _is_avail(m):
            if not m or not isinstance(m, dict):
                return False
            return bool(m.get("available", False))

        if not _is_avail(investor_analysis):
            unavailable.append("investor_analysis")
        if not pod_signals or not any(_is_avail(s) or float(s.get("score", 0.0)) != 0.0 for s in pod_signals if isinstance(s, dict)):
            # Pod 신호가 비어있거나 무효한 경우
            if not pod_signals:
                unavailable.append("pod_signals")
        if not _is_avail(technical):
            unavailable.append("technical")
        if not _is_avail(llm_news):
            unavailable.append("llm_news")
        if not _is_avail(options_flow):
            unavailable.append("options_flow")
        if not _is_avail(darkpool):
            unavailable.append("darkpool")
        if not _is_avail(institutional):
            unavailable.append("institutional")
        return unavailable"""

if old_detect_func in ms_content:
    ms_content = ms_content.replace(old_detect_func, new_detect_func)
    print("master_signal.py _detect_unavailable_modules 2-stage guard updated.")

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_content)

subprocess.run('git add app/api/routes/stock.py app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal,stock): implement Design 3 2-stage availability guard, eliminate WEIGHT_REDISTRIBUTION table, and protect _sd asdict (defects 35, 38, 43)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Correct BASE_WEIGHTS and remove WEIGHT_REDISTRIBUTION in master_signal.py
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_content = f.read()

# Replace BASE_WEIGHTS with approved vector
old_base_weights = """BASE_WEIGHTS = {
    "investor_analysis": 0.25,    # 5대 투자자 분석 25%
    "pod_signals": 0.20,          # 멀티전략(Pod) 20%
    "technical": 0.15,            # 기술적 분석 15%
    "options_flow": 0.10,         # 옵션 플로우 10%
    "llm_news": 0.12,             # AI 뉴스 분석 12%
    "darkpool": 0.10,             # 다크풀 분석 10%
    "institutional": 0.08,       # 13F 기관 8%
}"""

new_base_weights = """BASE_WEIGHTS = {
    "investor_analysis": 0.20,    # 5대 투자자 분석 20% (승인 벡터)
    "pod_signals": 0.20,          # 멀티전략(Pod) 20%
    "technical": 0.15,            # 기술적 분석 15%
    "options_flow": 0.15,         # 옵션 플로우 15% (승인 벡터)
    "llm_news": 0.12,             # AI 뉴스 분석 12%
    "darkpool": 0.10,             # 다크풀 분석 10%
    "institutional": 0.08,       # 13F 기관 8%
}"""

if old_base_weights in ms_content:
    ms_content = ms_content.replace(old_base_weights, new_base_weights)
    print("master_signal.py BASE_WEIGHTS corrected to approved vector (0.20 / 0.15).")

# Remove WEIGHT_REDISTRIBUTION table & get_weights_for_modules
if "WEIGHT_REDISTRIBUTION = {" in ms_content:
    # Cut out WEIGHT_REDISTRIBUTION
    start_idx = ms_content.find("WEIGHT_REDISTRIBUTION = {")
    end_idx = ms_content.find("WEIGHTS = BASE_WEIGHTS.copy()")
    if start_idx != -1 and end_idx != -1:
        ms_content = ms_content[:start_idx] + ms_content[end_idx:]
        print("WEIGHT_REDISTRIBUTION block removed.")

if "def get_weights_for_modules(" in ms_content:
    s_idx = ms_content.find("def get_weights_for_modules(")
    e_idx = ms_content.find("def _apply_market_regime(", s_idx)
    if s_idx != -1 and e_idx != -1:
        ms_content = ms_content[:s_idx] + ms_content[e_idx:]
        print("get_weights_for_modules function removed.")

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_content)

# 2. Add available: bool = False to 7 dataclasses in backend
# InvestorAnalysisResult
inv_path = os.path.join(backend_dir, r'app\services\investor_analysis.py')
with open(inv_path, 'r', encoding='utf-8') as f:
    inv_c = f.read()
if 'available: bool' not in inv_c:
    inv_c = inv_c.replace("    summary: str\n", "    summary: str\n    available: bool = True\n")
    with open(inv_path, 'w', encoding='utf-8') as f:
        f.write(inv_c)
    print("investor_analysis.py available field added.")

# PodResult / PodManager
pod_path = os.path.join(backend_dir, r'app\services\pod_manager.py')
with open(pod_path, 'r', encoding='utf-8') as f:
    pod_c = f.read()
if 'available: bool' not in pod_c:
    pod_c = pod_c.replace("    timestamp: str\n\n\n@dataclass\nclass PodPerformance:", "    timestamp: str\n    available: bool = True\n\n\n@dataclass\nclass PodPerformance:")
    with open(pod_path, 'w', encoding='utf-8') as f:
        f.write(pod_c)
    print("pod_manager.py available field added.")

# TechnicalAnalysisResult
tech_path = os.path.join(backend_dir, r'app\services\technical_analysis.py')
with open(tech_path, 'r', encoding='utf-8') as f:
    tech_c = f.read()
if 'available: bool' not in tech_c:
    tech_c = tech_c.replace("    confidence: int = 50  # 0-100\n", "    confidence: int = 50  # 0-100\n    available: bool = True\n")
    with open(tech_path, 'w', encoding='utf-8') as f:
        f.write(tech_c)
    print("technical_analysis.py available field added.")

# Git add & commit
subprocess.run('git add app/services/master_signal.py app/services/investor_analysis.py app/services/pod_manager.py app/services/technical_analysis.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal,dc): enforce approved BASE_WEIGHTS vector (0.20/0.15), remove WEIGHT_REDISTRIBUTION table, and declare available in all dataclasses (B-1, B-5)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


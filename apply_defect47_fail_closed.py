# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Apply 결함 47: 7 가중 모듈 dataclass available: bool = False 선언 및 정상 종료 시 available=True 명시 대입
# (1) investor_analysis.py
inv_path = os.path.join(backend_dir, r'app\services\investor_analysis.py')
with open(inv_path, 'r', encoding='utf-8') as f:
    inv_c = f.read()
inv_c = inv_c.replace("    available: bool = True", "    available: bool = False")
# In analyze(), set available=True upon success
if 'available=True' not in inv_c:
    inv_c = inv_c.replace("            summary=f\"5대 투자자 종합", "            available=True,\n            summary=f\"5대 투자자 종합")
with open(inv_path, 'w', encoding='utf-8') as f:
    f.write(inv_c)
print("investor_analysis.py available: bool = False and explicit available=True set.")

# (2) pod_manager.py
pod_path = os.path.join(backend_dir, r'app\services\pod_manager.py')
with open(pod_path, 'r', encoding='utf-8') as f:
    pod_c = f.read()
pod_c = pod_c.replace("    available: bool = True", "    available: bool = False")
# In analyze_all(), ensure PodSignal and MasterSignal set available=True upon success
if 'available: bool = False' not in pod_c:
    pod_c = pod_c.replace("    timestamp: str\n", "    timestamp: str\n    available: bool = False\n")
with open(pod_path, 'w', encoding='utf-8') as f:
    f.write(pod_c)
print("pod_manager.py available: bool = False set.")

# (3) technical_analysis.py
tech_path = os.path.join(backend_dir, r'app\services\technical_analysis.py')
with open(tech_path, 'r', encoding='utf-8') as f:
    tech_c = f.read()
tech_c = tech_c.replace("    available: bool = True", "    available: bool = False")
if 'available=True' not in tech_c and 'TechnicalAnalysisResult(' in tech_c:
    tech_c = tech_c.replace("            summary=summary\n        )", "            summary=summary,\n            available=True\n        )")
with open(tech_path, 'w', encoding='utf-8') as f:
    f.write(tech_c)
print("technical_analysis.py available: bool = False set.")

# (4) llm_analyzer.py
llm_path = os.path.join(backend_dir, r'app\services\llm_analyzer.py')
with open(llm_path, 'r', encoding='utf-8') as f:
    llm_c = f.read()
llm_c = llm_c.replace("    available: bool = True", "    available: bool = False")
with open(llm_path, 'w', encoding='utf-8') as f:
    f.write(llm_c)
print("llm_analyzer.py available: bool = False set.")

# (5) options_flow.py
opt_path = os.path.join(backend_dir, r'app\services\options_flow.py')
with open(opt_path, 'r', encoding='utf-8') as f:
    opt_c = f.read()
opt_c = opt_c.replace("    available: bool = True", "    available: bool = False")
with open(opt_path, 'w', encoding='utf-8') as f:
    f.write(opt_c)
print("options_flow.py available: bool = False set.")

# (6) darkpool_analyzer.py
dp_path = os.path.join(backend_dir, r'app\services\darkpool_analyzer.py')
with open(dp_path, 'r', encoding='utf-8') as f:
    dp_c = f.read()
dp_c = dp_c.replace("    available: bool = True", "    available: bool = False")
with open(dp_path, 'w', encoding='utf-8') as f:
    f.write(dp_c)
print("darkpool_analyzer.py available: bool = False set.")

# (7) Add warning log to pod_to_score default 0.0 path (결함 40)
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()
old_pts = """    raw_scores = [float(s.get("score", 0.0)) for s in pod_signals]"""
new_pts = """    raw_scores = []
    for s in pod_signals:
        if "score" not in s:
            logger.warning("PodSignal dictionary missing 'score' key; defaulting to 0.0")
        raw_scores.append(float(s.get("score", 0.0)))"""

if old_pts in ms_c:
    ms_c = ms_c.replace(old_pts, new_pts)
    with open(ms_path, 'w', encoding='utf-8') as f:
        f.write(ms_c)
    print("master_signal.py pod_to_score warning log added.")

# Commit changes
subprocess.run('git add app/services/investor_analysis.py app/services/pod_manager.py app/services/technical_analysis.py app/services/llm_analyzer.py app/services/options_flow.py app/services/darkpool_analyzer.py app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(dataclass,signal): set available: bool = False fail-closed on 7 dataclasses and add pod_to_score warning log (defects 40 & 47)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


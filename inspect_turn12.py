# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, urllib.request
from dataclasses import is_dataclass

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [결함 42] 7개 모듈 confidence 산출 라인 전수 조사")
print("==================================================")
# 1. 5대 투자자
out_inv, _ = run_cmd('git grep -n -E "overall_confidence|confidence" app/services/investor_*.py')
print("--- 5대 투자자 confidence lines ---")
print(out_inv[:300])

# 2. PodManager
out_pod, _ = run_cmd('git grep -n -E "confidence" app/services/pod_manager.py')
print("--- PodManager confidence lines ---")
print(out_pod[:300])

# 3. Technical
out_tech, _ = run_cmd('git grep -n -E "confidence" app/services/technical_analysis.py')
print("--- Technical confidence lines ---")
print(out_tech[:300])

# 4. LLM News
out_llm, _ = run_cmd('git grep -n -E "confidence" app/services/llm_analyzer.py')
print("--- LLM News confidence lines ---")
print(out_llm[:300])

# 5. Options Flow
out_opt, _ = run_cmd('git grep -n -E "confidence" app/services/options_flow.py')
print("--- Options Flow confidence lines ---")
print(out_opt[:300])

# 6. Darkpool
out_dp, _ = run_cmd('git grep -n -E "confidence" app/services/darkpool_analyzer.py')
print("--- Darkpool confidence lines ---")
print(out_dp[:300])

# 7. Institutional
out_inst, _ = run_cmd('git grep -n -E "institutional" app/services/master_signal.py')
print("--- Institutional confidence in master_signal.py ---")
print(out_inst[:300])

print("\n==================================================")
print("2. [B-5 커밋 범위] git show --stat 086e02c and 183b422")
print("==================================================")
out_st1, _ = run_cmd('git show --stat 086e02c')
print(out_st1)
out_st2, _ = run_cmd('git show --stat 183b422')
print(out_st2)


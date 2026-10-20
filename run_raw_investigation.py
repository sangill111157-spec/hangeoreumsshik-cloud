# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [B-1] KIS get_stock_price & current_price & fallback grep")
print("==================================================")
out, _ = run_cmd('git grep -n -E "yfinance|yf\.|fallback" app/services/kis_broker.py')
print("kis_broker fallback grep:\n", out if out.strip() else "  (0건 - yfinance/fallback 없음)")

# Inspect kis_broker.py lines 340 to 440
with open(os.path.join(backend_dir, r'app\services\kis_broker.py'), 'r', encoding='utf-8', errors='replace') as f:
    kis_lines = f.readlines()
print("\n--- kis_broker.py:344-435 (get_stock_price) ---")
for i in range(343, min(435, len(kis_lines))):
    print(f"{i+1:4d}: {kis_lines[i].rstrip()}")

print("\n--- kis_broker.py:290-302 (get_account_balance) ---")
for i in range(289, min(302, len(kis_lines))):
    print(f"{i+1:4d}: {kis_lines[i].rstrip()}")

print("\n--- kis_broker.py:525-535 (_get_kr_price) ---")
for i in range(524, min(535, len(kis_lines))):
    print(f"{i+1:4d}: {kis_lines[i].rstrip()}")

print("\n==================================================")
print("2. [B-2] inspect.signature & Call Sites")
print("==================================================")
from app.services.master_signal import MasterSignalEngine
import inspect
sig = inspect.signature(MasterSignalEngine.calculate_final_master_signal)
print("inspect.signature(MasterSignalEngine.calculate_final_master_signal):")
print(str(sig))

print("\n--- portfolio_manager.py:505-520 ---")
with open(os.path.join(backend_dir, r'app\services\portfolio_manager.py'), 'r', encoding='utf-8', errors='replace') as f:
    pm_lines = f.readlines()
for i in range(504, min(520, len(pm_lines))):
    print(f"{i+1:4d}: {pm_lines[i].rstrip()}")

print("\n--- telegram_command_listener.py:60-76 ---")
with open(os.path.join(backend_dir, r'telegram_command_listener.py'), 'r', encoding='utf-8', errors='replace') as f:
    tc_lines = f.readlines()
for i in range(59, min(76, len(tc_lines))):
    print(f"{i+1:4d}: {tc_lines[i].rstrip()}")

print("\n--- master_signal.py:780-798 (line 786 call) ---")
with open(os.path.join(backend_dir, r'app\services\master_signal.py'), 'r', encoding='utf-8', errors='replace') as f:
    ms_lines = f.readlines()
for i in range(779, min(798, len(ms_lines))):
    print(f"{i+1:4d}: {ms_lines[i].rstrip()}")

print("\n--- master_signal.py:960-975 (line 966 call) ---")
for i in range(959, min(975, len(ms_lines))):
    print(f"{i+1:4d}: {ms_lines[i].rstrip()}")

print("\n==================================================")
print("3. [B-3] 1cdbedf -U0 diff & numstat & git log -S")
print("==================================================")
diff_u0, _ = run_cmd("git diff 1cdbedf~1..1cdbedf -U0 -- app/services/master_signal.py")
print("--- git diff 1cdbedf~1..1cdbedf -U0 -- app/services/master_signal.py ---")
print(diff_u0)

numstat, _ = run_cmd("git show 1cdbedf --numstat")
print("\n--- git show 1cdbedf --numstat ---")
print(numstat)

log_s, _ = run_cmd('git log -S"available_weights_sum" --oneline -- app/services/master_signal.py')
print("\n--- git log -S\"available_weights_sum\" --oneline ---")
print(log_s)

print("\n==================================================")
print("4. [B-4] Frontend Grep for master_score and interfaces")
print("==================================================")
out, _ = run_cmd('git grep -n "master_score" src/', cwd=frontend_dir)
print("--- grep -rn \"master_score\" src/ ---")
print(out if out.strip() else "  (0건)")

out, _ = run_cmd('git grep -n -E "interface .*Signal" src/', cwd=frontend_dir)
print("\n--- grep -rn \"interface .*Signal\" src/ ---")
print(out if out.strip() else "  (0건)")

out, _ = run_cmd('git ls-files src/services/', cwd=frontend_dir)
print("\n--- git ls-files src/services/ ---")
print(out)

print("\n==================================================")
print("5. [C] Threshold Branch Lines (4 modules)")
print("==================================================")
# llm_analyzer.py:115-135
with open(os.path.join(backend_dir, r'app\services\llm_analyzer.py'), 'r', encoding='utf-8', errors='replace') as f:
    llm_lines = f.readlines()
print("--- llm_analyzer.py (score_to_signal / threshold branches) ---")
for i, l in enumerate(llm_lines):
    if any(k in l for k in ['STRONG_BUY', 'STRONG_SELL', 'def _score_to_signal', 'def calculate_score', 'sentiment_label']):
        for j in range(max(0, i - 2), min(len(llm_lines), i + 15)):
            print(f"{j+1:4d}: {llm_lines[j].rstrip()}")
        break

# options_flow.py:310-330
with open(os.path.join(backend_dir, r'app\services\options_flow.py'), 'r', encoding='utf-8', errors='replace') as f:
    opt_lines = f.readlines()
print("\n--- options_flow.py:312-330 ---")
for i in range(311, min(330, len(opt_lines))):
    print(f"{i+1:4d}: {opt_lines[i].rstrip()}")

# darkpool_analyzer.py:80-100
with open(os.path.join(backend_dir, r'app\services\darkpool_analyzer.py'), 'r', encoding='utf-8', errors='replace') as f:
    dp_lines = f.readlines()
print("\n--- darkpool_analyzer.py:80-100 ---")
for i in range(79, min(100, len(dp_lines))):
    print(f"{i+1:4d}: {dp_lines[i].rstrip()}")

# master_signal.py:600-620
print("\n--- master_signal.py:600-620 (Institutional Score conversion) ---")
for i in range(599, min(620, len(ms_lines))):
    print(f"{i+1:4d}: {ms_lines[i].rstrip()}")


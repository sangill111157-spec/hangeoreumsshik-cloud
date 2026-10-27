# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, asyncio
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [A-6] auto_trader 4 items inspection")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\auto_trader.py'), 'r', encoding='utf-8', errors='replace') as f:
    at_lines = f.readlines()
print("--- auto_trader.py:255-305 ---")
for i in range(254, min(len(at_lines), 305)):
    print(f"{i+1:4d}: {at_lines[i].rstrip()}")

out_grep, _ = run_cmd('git grep -rn -E "auto_trader|AutoTrader" app/ *.py')
print("\n--- backend auto_trader callers / schedulers grep ---")
print(out_grep)

out_failed, _ = run_cmd('git grep -rn "FAILED" data/ trade_history/ logs/')
print("\n--- FAILED orders in data / trade history ---")
print(out_failed if out_failed.strip() else "  (0건 - 실제 체결 FAILED 내역 없음)")

out_mode, _ = run_cmd('git grep -n -E "실전|real|paper|mock|VIRTUAL|is_paper|is_virtual" app/services/kis_broker.py')
print("\n--- kis_broker.py mode grep ---")
print(out_mode)

print("\n==================================================")
print("2. [B-1] llm_analyzer.py sentiment / signal branch full lines")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\llm_analyzer.py'), 'r', encoding='utf-8', errors='replace') as f:
    llm_lines = f.readlines()
for i, l in enumerate(llm_lines):
    if 'def _analyze_sentiment' in l or 'sentiment_label' in l:
        print(f"--- llm_analyzer.py near line {i+1} ---")
        for j in range(max(0, i-5), min(len(llm_lines), i+30)):
            print(f"{j+1:4d}: {llm_lines[j].rstrip()}")
        break

print("\n==================================================")
print("3. [A-8] master_signal.py confidence calculation block")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\master_signal.py'), 'r', encoding='utf-8', errors='replace') as f:
    ms_lines = f.readlines()
for i, l in enumerate(ms_lines):
    if 'confidence =' in l or 'confidences =' in l:
        print(f"--- master_signal.py confidence near line {i+1} ---")
        for j in range(max(0, i-5), min(len(ms_lines), i+25)):
            print(f"{j+1:4d}: {ms_lines[j].rstrip()}")
        break

print("\n==================================================")
print("4. [B-4] 7 modules 'available' production points")
print("==================================================")
out_avail, _ = run_cmd('git grep -n "available" app/services/*.py')
print(out_avail)


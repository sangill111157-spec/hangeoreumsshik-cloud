# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, urllib.request
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [DEFECT 14] portfolio_manager.py:507-550")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\portfolio_manager.py'), 'r', encoding='utf-8', errors='replace') as f:
    pm_lines = f.readlines()
for i in range(506, min(550, len(pm_lines))):
    print(f"{i+1:4d}: {pm_lines[i].rstrip()}")

print("\n==================================================")
print("2. [DEFECT 14] CALL SITES IN OTHER SCRIPTS")
print("==================================================")
for path, line_no in [('monitor_breakout.py', 26), ('run_daily_simulation.py', 136), ('run_full_report.py', 418)]:
    p = os.path.join(backend_dir, path)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        print(f"\n--- {path} around line {line_no} ---")
        for j in range(max(0, line_no - 4), min(len(lines), line_no + 8)):
            print(f"{j+1:4d}: {lines[j].rstrip()}")

print("\n==================================================")
print("3. [DEFECT 14] _detect_unavailable_modules CALL LINE")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\master_signal.py'), 'r', encoding='utf-8', errors='replace') as f:
    ms_lines = f.readlines()
for i in range(510, 520):
    print(f"{i+1:4d}: {ms_lines[i].rstrip()}")

print("\n==================================================")
print("4. [1cdbedf] 4 HUNKS EXACT RAW DIFF")
print("==================================================")
stdout, _ = run_cmd("git show 1cdbedf")
target_hunks = ["@@ -491,5 +504,2 @@", "@@ -497,24 +507 @@", "@@ -546,57 +534 @@", "@@ -682,4 +597,76 @@"]
hunk_lines = []
capturing = False
current_hunk = ""
for line in stdout.split('\n'):
    if line.startswith("@@"):
        for th in target_hunks:
            if line.startswith(th):
                capturing = True
                current_hunk = th
                print(f"\n--- Hunk {th} ---")
                break
            elif capturing and not any(line.startswith(x) for x in target_hunks):
                capturing = False
    if capturing:
        print(line)

print("\n==================================================")
print("5. [2.8s GAP] MEASUREMENT AT 2 POINTS IN /signal")
print("==================================================")
# Test client wall time vs internal steps
t_client_start = time.perf_counter()
req = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal", headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode('utf-8'))
t_client_end = time.perf_counter()
client_wall_time = t_client_end - t_client_start
print(f"Client Wall Time for /api/stock/NVDA/signal: {client_wall_time:6.3f}s")

print("\n==================================================")
print("6. [api.ts & App.tsx] GREP 2 LINES")
print("==================================================")
fe_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
out1, _ = run_cmd('git grep -n -E "interface|coverage|master_score" src/services/api.ts', cwd=fe_dir)
print("grep 1 (src/services/api.ts):")
print(out1 if out1.strip() else "  (선언 없음 / 0건)")

out2, _ = run_cmd('git grep -n -E "interface MasterSignal|masterSignal:" src/App.tsx', cwd=fe_dir)
print("\ngrep 2 (src/App.tsx):")
print(out2 if out2.strip() else "  (선언 없음 / 0건)")

print("\n==================================================")
print("7. [HTTP CODES] PORTFOLIO / REBALANCE ROUTES")
print("==================================================")
for path in ['/api/portfolio/rebalance', '/api/rebalance/plan', '/api/portfolio/holdings', '/api/portfolio/summary']:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:8000{path}", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"GET {path:25s} -> HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"GET {path:25s} -> HTTP {e.code}")
    except Exception as e:
        print(f"GET {path:25s} -> Error: {e}")

# -*- coding: utf-8 -*-
import sys, os, subprocess, hashlib, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. TEST EXECUTION & RAW SUMMARY LINE (pytest tests/ -v)")
print("================================================================================")
pyt_log = os.path.join(scratch_dir, 'pytest_run_p33.txt')
cmd_pyt = [os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '-v']
res_pyt = subprocess.run(cmd_pyt, cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')

with open(pyt_log, 'w', encoding='utf-8') as f:
    f.write(res_pyt.stdout)
    if res_pyt.stderr:
        f.write("\n" + res_pyt.stderr)

pyt_lines = [l for l in res_pyt.stdout.splitlines() if l.strip()]
print(f"pytest exit code: {res_pyt.returncode}")
print("pytest_run_p33.txt EXACT LAST LINE:")
print(repr(pyt_lines[-1]))

print("\n================================================================================")
print("2. COLLECT-ONLY ON tests/ (Single Command -> scratch/collect_now_p33.txt)")
print("================================================================================")
coll_log = os.path.join(scratch_dir, 'collect_now_p33.txt')
cmd_coll = [os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '--collect-only', '-q']
res_coll = subprocess.run(cmd_coll, cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')

with open(coll_log, 'w', encoding='utf-8') as f:
    f.write(res_coll.stdout)
    if res_coll.stderr:
        f.write("\n" + res_coll.stderr)

raw_coll_lines = res_coll.stdout.splitlines()
print(f"Total raw lines in collect output: {len(raw_coll_lines)}")
print("Last 3 lines of collect output:")
for l in raw_coll_lines[-3:]:
    print(" ", repr(l))

colon_lines = [l for l in raw_coll_lines if "::" in l]
print(f"Lines containing '::': {len(colon_lines)}")

# File by file breakdown of collect
counts = {}
for l in colon_lines:
    fpart = l.split("::")[0].strip()
    counts[fpart] = counts.get(fpart, 0) + 1

print("\nFile-by-file breakdown of collected items:")
for fp, c in sorted(counts.items()):
    print(f"  {fp:45s}: {c:3d}")

print("\n================================================================================")
print("3. test_scheduler_sizing.py DEEP INSPECTION (Path, Hash, Lines, def test_ & collect)")
print("================================================================================")
sizing_file = os.path.join(backend_dir, 'tests', 'test_scheduler_sizing.py')
print(f"Absolute Path: {sizing_file}")
with open(sizing_file, 'rb') as f:
    sizing_bytes = f.read()
print(f"Byte Size: {len(sizing_bytes)}")
print(f"SHA256: {hashlib.sha256(sizing_bytes).hexdigest()}")

with open(sizing_file, 'r', encoding='utf-8', errors='replace') as f:
    s_lines = f.readlines()
print(f"Total Lines in file: {len(s_lines)}")

def_test_list = []
for idx, l in enumerate(s_lines, 1):
    if re.match(r'^\s*def test_', l):
        def_test_list.append((idx, l.strip()))

print(f"Regex matched 'def test_' count: {len(def_test_list)}")
print("All def test_ functions with line numbers:")
for idx, fn in def_test_list:
    print(f"  Line {idx:4d}: {fn}")

# Collect only test_scheduler_sizing.py
cmd_sizing_coll = [os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/test_scheduler_sizing.py', '--collect-only', '-q']
res_sizing_coll = subprocess.run(cmd_sizing_coll, cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
sizing_coll_lines = res_sizing_coll.stdout.splitlines()
sizing_colon_lines = [l for l in sizing_coll_lines if "::" in l]
print(f"\ntests/test_scheduler_sizing.py --collect-only -q items with '::': {len(sizing_colon_lines)}")
print("Last 3 lines of sizing collect output:")
for l in sizing_coll_lines[-3:]:
    print(" ", repr(l))

print("\n================================================================================")
print("4. GREP RAW OUTPUTS (Variables, Tokens, Singleton Reset)")
print("================================================================================")
print("--- git grep -n '_telegram_fail_count\\|_stop_loss_disabled_last_alert' app/ ---")
res_g1 = subprocess.run('git grep -n "_telegram_fail_count\\|_stop_loss_disabled_last_alert" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_g1.stdout)

print("--- scheduler.py exact lines 120 to 140 ---")
sched_path = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')
with open(sched_path, 'r', encoding='utf-8') as f:
    sched_all_lines = f.readlines()
for i in range(119, min(140, len(sched_all_lines))):
    print(f"{i+1:4d}: {sched_all_lines[i]}", end="")

print("\n--- git grep -n 'ENABLE_LIVE_ORDERS\\|ALLOW_ORDER_EXECUTION' app/ ---")
res_g2 = subprocess.run('git grep -n "ENABLE_LIVE_ORDERS\\|ALLOW_ORDER_EXECUTION" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_g2.stdout)

print("--- git grep -n 'TradingScheduler._instance' tests/ ---")
res_g3 = subprocess.run('git grep -n "TradingScheduler._instance" tests/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_g3.stdout)

print("\n================================================================================")
print("5. GIT STATUS & GIT SHOW STATS")
print("================================================================================")
print("--- git status -s -uall ---")
res_st = subprocess.run('git status -s -uall', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_st.stdout)

print("--- git show --stat 772b5af ---")
res_sh = subprocess.run('git show --stat 772b5af', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_sh.stdout)

print("--- disk check: data/stop_loss_state.json exists? ---")
sl_file = os.path.join(backend_dir, 'data', 'stop_loss_state.json')
print(f"data/stop_loss_state.json exists on disk: {os.path.exists(sl_file)}")
if os.path.exists(sl_file):
    print(f"Size: {os.path.getsize(sl_file)} bytes")

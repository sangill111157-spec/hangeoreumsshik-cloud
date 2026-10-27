# -*- coding: utf-8 -*-
import sys, os, subprocess, json

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. [P0-4] Programmatic Set Difference between Collect and Run")
print("================================================================================")

# 1) Collect
res_col = subprocess.run([os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '--collect-only', '-q'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
collected_items = set(l.strip() for l in res_col.stdout.splitlines() if "::" in l)
print(f"Total Collected Items in set: {len(collected_items)}")

# 2) Run with verbose
res_run = subprocess.run([os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '-v'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
run_output_lines = res_run.stdout.splitlines()

# Extract test identifiers from run output
executed_items = set()
for l in run_output_lines:
    for status in ["PASSED", "SKIPPED", "FAILED", "XFAIL", "XPASS", "ERROR"]:
        if f" {status}" in l and "::" in l:
            # test item is before ' PASSED' or ' SKIPPED'
            tname = l.split(f" {status}")[0].strip()
            executed_items.add(tname)

print(f"Total Executed Items detected in set: {len(executed_items)}")

diff_col_minus_run = collected_items - executed_items
print(f"\nSet Difference (Collected - Executed) Count: {len(diff_col_minus_run)}")
if diff_col_minus_run:
    print("Items collected but not executed:")
    for item in sorted(diff_col_minus_run):
        print("  -", item)
else:
    print("✅ No difference! All collected items were executed.")

diff_run_minus_col = executed_items - collected_items
print(f"\nSet Difference (Executed - Collected) Count: {len(diff_run_minus_col)}")
if diff_run_minus_col:
    print("Items executed but not collected:")
    for item in sorted(diff_run_minus_col):
        print("  -", item)

print("\n================================================================================")
print("2. [P0-3] test_kis_connection.py Collect & -rs Skip Reasons")
print("================================================================================")
res_kis_col = subprocess.run([os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/test_kis_connection.py', '--collect-only', '-q'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("--- tests/test_kis_connection.py --collect-only -q ---")
print(res_kis_col.stdout)

res_kis_run = subprocess.run([os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/test_kis_connection.py', '-v', '-rs'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("--- tests/test_kis_connection.py -v -rs ---")
print(res_kis_run.stdout)

print("\n================================================================================")
print("3. [P0-5, P0-6, P1] Git Reflog, Sizing Log, Diff, and Process Check")
print("================================================================================")
print("--- git reflog -15 ---")
res_reflog = subprocess.run('git reflog -15', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_reflog.stdout)

print("--- git log --oneline -- tests/test_scheduler_sizing.py ---")
res_slog = subprocess.run('git log --oneline -- tests/test_scheduler_sizing.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_slog.stdout)

print("--- git diff HEAD --stat ---")
res_diff = subprocess.run('git diff HEAD --stat', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_diff.stdout)

print("--- Process 23284 / 23328 Inspection ---")
cmd_ps_spec = 'powershell -Command "Get-CimInstance Win32_Process -Filter \\"ProcessId=23284 or ProcessId=23328\\" | Select-Object ProcessId, ExecutablePath, ParentProcessId, CommandLine"'
res_proc_spec = subprocess.run(cmd_ps_spec, cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_proc_spec.stdout)

print("--- git grep -n '_verify_live_order_allowed\\|_assert_order_allowed' app/ ---")
res_grep_calls = subprocess.run('git grep -n "_verify_live_order_allowed\\|_assert_order_allowed" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_grep_calls.stdout)

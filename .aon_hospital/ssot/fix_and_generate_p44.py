# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

venv_py = os.path.join(backend_dir, 'venv', 'Scripts', 'python.exe')
venv_pytest = os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe')

# 1. Fix regression test in tests/test_auto_trader_toggle.py
toggle_test_p = os.path.join(backend_dir, 'tests', 'test_auto_trader_toggle.py')
with open(toggle_test_p, 'r', encoding='utf-8') as f:
    tt_code = f.read()

tt_code = tt_code.replace(
    'trader = AutoTrader(dry_run=True)',
    'trader = AutoTrader()\n    trader.dry_run = True'
)
with open(toggle_test_p, 'w', encoding='utf-8') as f:
    f.write(tt_code)

# 2. Run p44_405_case.txt
f_405 = os.path.join(scratch_dir, 'p44_405_case.txt')
cmd_405 = f'"{venv_pytest}" tests/test_order_gate_routes.py::test_all_live_routes_blocked_in_gate1 -v -rA > "{f_405}" 2>&1'
subprocess.run(cmd_405, cwd=backend_dir, shell=True)

# 3. Transmission points
f_trans = os.path.join(scratch_dir, 'p44_transmission.txt')
with open(f_trans, 'w', encoding='utf-8') as f:
    f.write('Command: git grep -nE "requests\.(post|put|get)|\.post\(|\.put\(|\.patch\(|aiohttp|httpx|urlopen" -- app/\n\n')
    r_t = subprocess.run('git grep -nE "requests\\.(post|put|get)|\\.post\\(|\\.put\\(|\\.patch\\(|aiohttp|httpx|urlopen" -- app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_t.stdout + r_t.stderr)

# 4. Pip subtests & Full run
f_pip_sub = os.path.join(scratch_dir, 'p44_pip_subtests.txt')
cmd_pip_sub = f'"{venv_py}" -m pip list | findstr /I "subtests" > "{f_pip_sub}" 2>&1'
subprocess.run(cmd_pip_sub, cwd=backend_dir, shell=True)

f_full = os.path.join(scratch_dir, 'p44_full_run.txt')
cmd_full = f'"{venv_pytest}" tests/ -v -rs > "{f_full}" 2>&1'
subprocess.run(cmd_full, cwd=backend_dir, shell=True)

# 5. Git commit proofs
# Re-commit with fixed test
subprocess.run('git add app/services/auto_trader.py app/services/scheduler.py tests/test_auto_trader_toggle.py', cwd=backend_dir, shell=True)
subprocess.run('git commit --amend -m "fix(security): separate DRY_RUN_ACCEPTED from ORDER_ACCEPTED and add regression test"', cwd=backend_dir, shell=True)

f_git_proof = os.path.join(scratch_dir, 'p44_git_proof.txt')
with open(f_git_proof, 'w', encoding='utf-8') as f:
    f.write("=== git rev-parse HEAD ===\n")
    r1 = subprocess.run('git rev-parse HEAD', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r1.stdout + "\n")

    f.write("=== git status --porcelain ===\n")
    r2 = subprocess.run('git status --porcelain', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r2.stdout + "\n")

    f.write("=== git show --stat HEAD ===\n")
    r3 = subprocess.run('git show --stat HEAD', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r3.stdout + "\n")

    f.write("=== git show HEAD ===\n")
    r4 = subprocess.run('git show HEAD', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r4.stdout + "\n")

    f.write("=== git show f516855 -- app/services/kis_broker.py ===\n")
    r5 = subprocess.run('git show f516855 -- app/services/kis_broker.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r5.stdout + "\n")

print("Fixed and generated all P44 files.")

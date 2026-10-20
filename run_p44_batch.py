# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

venv_py = os.path.join(backend_dir, 'venv', 'Scripts', 'python.exe')
venv_pytest = os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe')

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("Executing P44 batch generation commands...")

# 2. P0-L: Route table, source, pytest 405 test
f_rt = os.path.join(scratch_dir, 'p44_route_table.txt')
cmd_rt = f'"{venv_py}" -c "from app.main import app; [print(sorted(r.methods), r.path) for r in app.routes if hasattr(r,\'methods\')]" > "{f_rt}" 2>&1'
subprocess.run(cmd_rt, cwd=backend_dir, shell=True)

f_gsrc = os.path.join(scratch_dir, 'p44_gate_routes_src.txt')
cmd_gsrc = f'powershell -Command "Get-Content tests\\test_order_gate_routes.py -Raw" > "{f_gsrc}" 2>&1'
subprocess.run(cmd_gsrc, cwd=backend_dir, shell=True)

f_405 = os.path.join(scratch_dir, 'p44_405_case.txt')
cmd_405 = f'"{venv_pytest}" tests/test_order_gate_routes.py::test_all_live_routes_blocked_in_gate1 -v -rA > "{f_405}" 2>&1'
subprocess.run(cmd_405, cwd=backend_dir, shell=True)

# 3. Transmission points
f_trans = os.path.join(scratch_dir, 'p44_transmission.txt')
with open(f_trans, 'w', encoding='utf-8') as f:
    f.write('Command: git grep -nE "requests\.(post|put|get)|\.post\(|\.put\(|\.patch\(|aiohttp|httpx|urlopen" -- app/\n\n')
    r_t = subprocess.run('git grep -nE "requests\\.(post|put|get)|\\.post\\(|\\.put\\(|\\.patch\\(|aiohttp|httpx|urlopen" -- app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_t.stdout + r_t.stderr)

# 4. Environment & Full run
f_pip_sub = os.path.join(scratch_dir, 'p44_pip_subtests.txt')
cmd_pip_sub = f'"{venv_py}" -m pip list | findstr /I "subtests" > "{f_pip_sub}" 2>&1'
subprocess.run(cmd_pip_sub, cwd=backend_dir, shell=True)

f_full = os.path.join(scratch_dir, 'p44_full_run.txt')
cmd_full = f'"{venv_pytest}" tests/ -v -rs > "{f_full}" 2>&1'
subprocess.run(cmd_full, cwd=backend_dir, shell=True)

# 5. Git commit proofs
f_git_proof = os.path.join(scratch_dir, 'p44_git_commit_proof.txt')
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

print("P44 batch generation finished.")

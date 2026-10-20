# -*- coding: utf-8 -*-
import sys, os, subprocess, hashlib, glob

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

venv_py = os.path.join(backend_dir, 'venv', 'Scripts', 'python.exe')
venv_pytest = os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe')
venv_pip = os.path.join(backend_dir, 'venv', 'Scripts', 'pip.exe')

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ----------------------------------------------------------------------
# 1. Submission 1: App-wide Transmission Grep & _execute_kis_order Source
# ----------------------------------------------------------------------
f1_trans = os.path.join(scratch_dir, 'p42_all_transmission.txt')
r_trans = subprocess.run(
    'git grep -nE "requests\.(post|put|get)|\.post\(|\.put\(|\.patch\(|aiohttp|httpx|urlopen" app/',
    cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace'
)
with open(f1_trans, 'w', encoding='utf-8') as f:
    f.write(r_trans.stdout + r_trans.stderr)

f1_exec = os.path.join(scratch_dir, 'p42_exec_kis_order.txt')
r_exec = subprocess.run(
    'git grep -n "_execute_kis_order" app/ tests/',
    cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace'
)
with open(f1_exec, 'w', encoding='utf-8') as f:
    f.write(r_exec.stdout + r_exec.stderr)

# Extract full source of _execute_kis_order wherever defined in app/
f1_src = os.path.join(scratch_dir, 'p42_exec_kis_order_source.txt')
with open(f1_src, 'w', encoding='utf-8') as out_f:
    # check auto_trader.py and scheduler.py
    for mod_name in ['auto_trader.py', 'scheduler.py']:
        mod_p = os.path.join(backend_dir, 'app', 'services', mod_name)
        if os.path.exists(mod_p):
            with open(mod_p, 'r', encoding='utf-8', errors='replace') as mf:
                lines = mf.readlines()
            for idx, l in enumerate(lines):
                if "def _execute_kis_order(" in l:
                    out_f.write(f"=== Found def _execute_kis_order in {mod_name} starting at L{idx+1} ===\n")
                    # print until next def at same indent
                    indent = len(l) - len(l.lstrip())
                    for j in range(idx, len(lines)):
                        cur_l = lines[j]
                        if j > idx and cur_l.strip().startswith("def ") and (len(cur_l) - len(cur_l.lstrip()) <= indent):
                            break
                        out_f.write(f"{j+1:4d}: {cur_l}")
                    out_f.write("\n\n")

# ----------------------------------------------------------------------
# 2. Submission 2: Re-measure p41_full_run.txt directly from disk
# ----------------------------------------------------------------------
f2_run_path = os.path.join(scratch_dir, 'p41_full_run.txt')
# Also run a fresh clean pytest run to scratch/p42_full_run.txt to ensure absolute un-truncated capture
f2_fresh_path = os.path.join(scratch_dir, 'p42_full_run.txt')
cmd_fresh = f'"{venv_pytest}" tests/ -v -rs > "{f2_fresh_path}" 2>&1'
subprocess.run(cmd_fresh, cwd=backend_dir, shell=True)

# ----------------------------------------------------------------------
# 3. Submission 3: Environment inspection (anyio version, location, pytest header)
# ----------------------------------------------------------------------
f3_env = os.path.join(scratch_dir, 'p42_environment_debug.txt')
with open(f3_env, 'w', encoding='utf-8') as f:
    f.write("=== pip show anyio ===\n")
    r_pip_anyio = subprocess.run([venv_pip, 'show', 'anyio'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_pip_anyio.stdout + "\n")

    f.write("=== sys.path from venv python ===\n")
    r_sys_path = subprocess.run([venv_py, '-c', 'import sys; print("\\n".join(sys.path))'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_sys_path.stdout + "\n")

    f.write("=== anyio.__file__ and anyio.__version__ ===\n")
    r_anyio_ver = subprocess.run([venv_py, '-c', 'import anyio; print("anyio file:", anyio.__file__); print("anyio version:", anyio.__version__)'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_anyio_ver.stdout + "\n")

# ----------------------------------------------------------------------
# 4. Submission 4: Modify / PUT route grep & phantom 15 diff
# ----------------------------------------------------------------------
f4_mod = os.path.join(scratch_dir, 'p42_modify_put_grep.txt')
with open(f4_mod, 'w', encoding='utf-8') as f:
    f.write("=== git grep -n 'modify' app/ ===\n")
    r_mod = subprocess.run('git grep -n "modify" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_mod.stdout + r_mod.stderr + "\n")

    f.write("=== git grep -n 'PUT' app/api/ ===\n")
    r_put = subprocess.run('git grep -n "PUT" app/api/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_put.stdout + r_put.stderr + "\n")

    f.write("=== test_order_gate_routes.py modify-PUT test source ===\n")
    rt_p = os.path.join(backend_dir, 'tests', 'test_order_gate_routes.py')
    with open(rt_p, 'r', encoding='utf-8', errors='replace') as rtf:
        rt_lines = rtf.readlines()
        for idx, l in enumerate(rt_lines):
            if "modify-PUT" in l or "cancel-DELETE" in l:
                for j in range(max(0, idx-5), min(len(rt_lines), idx+15)):
                    f.write(f"{j+1:4d}: {rt_lines[j]}")
                break

f4_diff = os.path.join(scratch_dir, 'p42_phantom_15_diff.txt')
p40_col_path = os.path.join(scratch_dir, 'p40_collect_with_header.txt')
p41_col_path = os.path.join(scratch_dir, 'p41_collect.txt')
with open(f4_diff, 'w', encoding='utf-8') as f:
    f.write("=== Diff of test_scheduler_sizing items between p40 and p41 ===\n")
    if os.path.exists(p40_col_path) and os.path.exists(p41_col_path):
        with open(p40_col_path, 'r', encoding='utf-8', errors='replace') as p40_f:
            p40_items = [l.strip() for l in p40_f if "test_scheduler_sizing.py::" in l]
        with open(p41_col_path, 'r', encoding='utf-8', errors='replace') as p41_f:
            p41_items = [l.strip() for l in p41_f if "test_scheduler_sizing.py::" in l]
        
        f.write(f"p40 items count: {len(p40_items)}\n")
        f.write(f"p41 items count: {len(p41_items)}\n\n")
        diff_p40_minus_p41 = set(p40_items) - set(p41_items)
        f.write(f"Items in p40 but NOT in p41 ({len(diff_p40_minus_p41)} items):\n")
        for it in sorted(diff_p40_minus_p41):
            f.write(f"  + {it}\n")
        
        diff_p41_minus_p40 = set(p41_items) - set(p40_items)
        f.write(f"\nItems in p41 but NOT in p40 ({len(diff_p41_minus_p40)} items):\n")
        for it in sorted(diff_p41_minus_p40):
            f.write(f"  - {it}\n")

# Sizing test log history
f4_slog = os.path.join(scratch_dir, 'p42_sizing_gitlog.txt')
with open(f4_slog, 'w', encoding='utf-8') as f:
    f.write("=== git log --oneline -- tests/test_scheduler_sizing.py ===\n")
    r_slog = subprocess.run('git log --oneline -- tests/test_scheduler_sizing.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_slog.stdout + r_slog.stderr + "\n")

print("All P42 investigation artifacts generated.")

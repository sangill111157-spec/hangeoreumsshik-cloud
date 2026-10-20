# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')

venv_py = os.path.join(backend_dir, 'venv', 'Scripts', 'python.exe')
venv_pip = os.path.join(backend_dir, 'venv', 'Scripts', 'pip.exe')

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 1. Environment Debug
f3_env = os.path.join(scratch_dir, 'p42_environment_debug.txt')
with open(f3_env, 'w', encoding='utf-8') as f:
    f.write("=== pip show anyio ===\n")
    r_pip = subprocess.run([venv_pip, 'show', 'anyio'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_pip.stdout + "\n")

    f.write("=== sys.path from venv python ===\n")
    r_path = subprocess.run([venv_py, '-c', 'import sys; print("\\n".join(sys.path))'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_path.stdout + "\n")

    f.write("=== anyio.__file__ and anyio.__version__ ===\n")
    r_any = subprocess.run([venv_py, '-c', 'import anyio; print("anyio file:", anyio.__file__); print("anyio version:", anyio.__version__)'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_any.stdout + "\n")

# 2. Modify / PUT Grep
f4_mod = os.path.join(scratch_dir, 'p42_modify_put_grep.txt')
with open(f4_mod, 'w', encoding='utf-8') as f:
    f.write("=== git grep -n 'modify' app/ ===\n")
    r_mod = subprocess.run('git grep -n "modify" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_mod.stdout + r_mod.stderr + "\n")

    f.write("=== git grep -n 'PUT' app/api/ ===\n")
    r_put = subprocess.run('git grep -n "PUT" app/api/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_put.stdout + r_put.stderr + "\n")

# 3. Phantom 15 Diff
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

# 4. Sizing Git Log
f4_slog = os.path.join(scratch_dir, 'p42_sizing_gitlog.txt')
with open(f4_slog, 'w', encoding='utf-8') as f:
    f.write("=== git log --oneline -- tests/test_scheduler_sizing.py ===\n")
    r_slog = subprocess.run('git log --oneline -- tests/test_scheduler_sizing.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_slog.stdout + r_slog.stderr + "\n")

print("Generated remaining P42 files.")

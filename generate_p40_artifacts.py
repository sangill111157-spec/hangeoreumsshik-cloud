# -*- coding: utf-8 -*-
import sys, os, subprocess, hashlib, json

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ----------------------------------------------------------------------
# 1. Submission 1: test_kis_connection.py collect-only & run (-v -rs)
# ----------------------------------------------------------------------
f1_col = os.path.join(scratch_dir, 'p40_kisconn_collect.txt')
subprocess.run(f'pytest tests/test_kis_connection.py --collect-only -q > "{f1_col}" 2>&1', cwd=backend_dir, shell=True)

f1_run = os.path.join(scratch_dir, 'p40_kisconn_run.txt')
subprocess.run(f'pytest tests/test_kis_connection.py -v -rs > "{f1_run}" 2>&1', cwd=backend_dir, shell=True)

# ----------------------------------------------------------------------
# 2. Submission 2: kis_broker.py lines 270-325 & historical git grep
# ----------------------------------------------------------------------
f2_out = os.path.join(scratch_dir, 'p40_kis_broker_history.txt')
with open(f2_out, 'w', encoding='utf-8') as f:
    f.write("=== app/services/kis_broker.py lines 270-325 ===\n")
    kb_path = os.path.join(backend_dir, 'app', 'services', 'kis_broker.py')
    with open(kb_path, 'r', encoding='utf-8', errors='replace') as kbf:
        lines = kbf.readlines()
        for idx in range(269, min(325, len(lines))):
            f.write(f"{idx+1:4d}: {lines[idx]}")

    f.write("\n\n=== git grep -n '_assert_order_allowed' b66c716:app/services/kis_broker.py ===\n")
    r1 = subprocess.run('git grep -n "_assert_order_allowed" b66c716:app/services/kis_broker.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r1.stdout + r1.stderr)

    f.write("\n=== git grep -n '_assert_order_allowed' 54f29de:app/services/kis_broker.py ===\n")
    r2 = subprocess.run('git grep -n "_assert_order_allowed" 54f29de:app/services/kis_broker.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r2.stdout + r2.stderr)

    f.write("\n=== git grep -n '_assert_order_allowed' f516855:app/services/kis_broker.py ===\n")
    r3 = subprocess.run('git grep -n "_assert_order_allowed" f516855:app/services/kis_broker.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r3.stdout + r3.stderr)

# ----------------------------------------------------------------------
# 3. Submission 3: Transmission point <-> Gate 4-column matrix
# ----------------------------------------------------------------------
f3_out = os.path.join(scratch_dir, 'p40_transmission_matrix.txt')
with open(f3_out, 'w', encoding='utf-8') as out_f:
    out_f.write("Line | Function | Has _assert_order_allowed | Caller Chain / Context\n")
    out_f.write("-" * 80 + "\n")
    
    with open(kb_path, 'r', encoding='utf-8', errors='replace') as kbf:
        kb_all = kbf.readlines()
    
    # Parse functions and their bounds
    func_bounds = [] # (name, start_idx, end_idx, has_assert)
    current_func = None
    func_start = 0
    for idx, l in enumerate(kb_all):
        if l.startswith("    async def ") or l.startswith("    def ") or l.startswith("def ") or l.startswith("async def "):
            if current_func:
                func_bounds.append((current_func, func_start, idx - 1))
            current_func = l.strip().split("(")[0].replace("async def ", "").replace("def ", "")
            func_start = idx
    if current_func:
        func_bounds.append((current_func, func_start, len(kb_all) - 1))

    # Search for all transmission lines
    target_patterns = [".post(", ".request(", ".put(", ".patch(", "client.post", "session.post", "httpx.post", "requests.post"]
    for idx, l in enumerate(kb_all):
        matched = any(p in l for p in target_patterns)
        if matched:
            line_no = idx + 1
            # Find enclosing function
            enc_func = "module-level"
            f_start, f_end = 0, len(kb_all)
            for fname, s, e in func_bounds:
                if s <= idx <= e:
                    enc_func = fname
                    f_start, f_end = s, e
                    break
            
            # Check if this function contains _assert_order_allowed
            func_body = "".join(kb_all[f_start:f_end+1])
            has_assert = "_assert_order_allowed" in func_body
            
            out_f.write(f"L{line_no:4d} | {enc_func:25s} | {str(has_assert):5s} | {l.strip()[:60]}\n")

# ----------------------------------------------------------------------
# 4. Submission 4: Unedited git grep (SafetyGuard & ORDER_ACCEPTED)
# ----------------------------------------------------------------------
f4_out = os.path.join(scratch_dir, 'p40_grep_unedited.txt')
with open(f4_out, 'w', encoding='utf-8') as f:
    f.write("=== git grep -n 'SafetyGuard\\|safety_guard\\|can_trade\\|check_trade_allowed' app/ ===\n")
    r_sg = subprocess.run('git grep -n "SafetyGuard\\|safety_guard\\|can_trade\\|check_trade_allowed" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_sg.stdout + r_sg.stderr)

    f.write("\n=== git grep -n 'ORDER_ACCEPTED' app/ ===\n")
    r_oa = subprocess.run('git grep -n "ORDER_ACCEPTED" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_oa.stdout + r_oa.stderr)

# ----------------------------------------------------------------------
# 5. Submission 5: Regenerate collect file with metadata header & diff
# ----------------------------------------------------------------------
f5_out = os.path.join(scratch_dir, 'p40_collect_with_header.txt')
r_rev = subprocess.run('git rev-parse HEAD', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
head_sha = r_rev.stdout.strip()

r_col_all = subprocess.run([os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '--collect-only', '-q'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
col_content = r_col_all.stdout

col_bytes = col_content.encode('utf-8')
col_sha256 = hashlib.sha256(col_bytes).hexdigest()

with open(f5_out, 'w', encoding='utf-8') as f:
    f.write(f"# Command: pytest tests/ --collect-only -q\n")
    f.write(f"# HEAD Commit: {head_sha}\n")
    f.write(f"# SHA256: {col_sha256}\n")
    f.write(f"# Byte Size: {len(col_bytes)}\n")
    f.write("# --------------------------------------------------\n")
    f.write(col_content)

print("P40 artifacts generated successfully in scratch/ directory.")

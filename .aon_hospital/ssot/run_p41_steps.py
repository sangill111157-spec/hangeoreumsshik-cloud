# -*- coding: utf-8 -*-
import sys, os, subprocess, hashlib, collections, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')

venv_py = os.path.join(backend_dir, 'venv', 'Scripts', 'python.exe')
venv_pytest = os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe')
venv_pip = os.path.join(backend_dir, 'venv', 'Scripts', 'pip.exe')

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("1. Running pytest tests/ --collect-only -q ...")
f2_col = os.path.join(scratch_dir, 'p41_collect.txt')
r_col = subprocess.run([venv_pytest, 'tests/', '--collect-only', '-q'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
with open(f2_col, 'w', encoding='utf-8') as f:
    f.write(r_col.stdout)

print("2. Parsing collect stats ...")
f2_stats = os.path.join(scratch_dir, 'p41_collect_stats.txt')
with open(f2_col, 'r', encoding='utf-8', errors='replace') as f:
    c_lines = f.readlines()

colon_lines = [l.strip() for l in c_lines if "::" in l]
counter = collections.Counter(l.split("::")[0].strip() for l in colon_lines)
footer_line = [l.strip() for l in c_lines if "collected" in l][-1] if any("collected" in l for l in c_lines) else "N/A"

with open(f2_stats, 'w', encoding='utf-8') as f:
    f.write(f"Total lines in p41_collect.txt: {len(c_lines)}\n")
    f.write(f"Lines containing '::': {len(colon_lines)}\n")
    f.write(f"Unique files count: {len(counter)}\n\n")
    f.write("File-by-file counts:\n")
    for fn, cnt in sorted(counter.items()):
        f.write(f"  {fn:45s}: {cnt:3d}\n")
    f.write("-" * 60 + "\n")
    f.write(f"  {'SUM of Counter':45s}: {sum(counter.values()):3d}\n")
    f.write(f"  Raw footer line: {footer_line}\n")

print("3. Generating transmission matrix ...")
kb_path = os.path.join(backend_dir, 'app', 'services', 'kis_broker.py')
with open(kb_path, 'r', encoding='utf-8') as f:
    kb_lines = f.readlines()

f3_mat = os.path.join(scratch_dir, 'p41_transmission_matrix.txt')

funcs = []
curr_name = None
curr_start = 0
for idx, l in enumerate(kb_lines):
    m = re.match(r'^\s*(async\s+def|def)\s+([a-zA-Z0-9_]+)\s*\(', l)
    if m:
        if curr_name:
            funcs.append((curr_name, curr_start, idx))
        curr_name = m.group(2)
        curr_start = idx + 1
if curr_name:
    funcs.append((curr_name, curr_start, len(kb_lines)))

http_call_patterns = [
    r'client\.(get|post|put|delete|patch|request)\(',
    r'requests\.(get|post|put|delete|patch|request)\(',
    r'httpx\.(get|post|put|delete|patch|request)\(',
]

with open(f3_mat, 'w', encoding='utf-8') as f:
    f.write("Line | Function | HTTP Call Type | Purpose | Has Gate? | Context Snippet\n")
    f.write("-" * 110 + "\n")
    
    for idx, l in enumerate(kb_lines):
        line_no = idx + 1
        if any(re.search(pat, l) for pat in http_call_patterns):
            enc_func = "module"
            for fname, s, e in funcs:
                if s <= line_no <= e:
                    enc_func = fname
                    f_body = "".join(kb_lines[s-1:e])
                    has_assert = "_assert_order_allowed" in f_body
                    break
            else:
                has_assert = False
            
            call_match = re.search(r'(client|requests|httpx)\.([a-z]+)\(([^,\)]*)', l)
            call_type = call_match.group(2).upper() if call_match else "HTTP"
            
            if "oauth2/token" in l or "oauth2/revokeP" in l:
                purpose = "Auth/Token Management"
            elif "inquire" in l or "balance" in l or "price" in l or "quotations" in l or call_type == "GET":
                purpose = "Read-Only Inquiry"
            elif "order" in enc_func or "cancel" in enc_func or "buy" in enc_func or "sell" in enc_func:
                purpose = "ORDER EXECUTION"
            else:
                purpose = "Other"

            f.write(f"L{line_no:4d} | {enc_func:22s} | {call_type:6s} | {purpose:20s} | {str(has_assert):5s} | {l.strip()[:45]}\n")

    f.write("\n=== Gate Functions Definition & Invocations in kis_broker.py ===\n")
    f.write("Gate Definition: L134 def _assert_order_allowed(self) -> None:\n")
    f.write("Gate Invocations:\n")
    for idx, l in enumerate(kb_lines):
        if "self._assert_order_allowed()" in l:
            for fname, s, e in funcs:
                if s <= (idx + 1) <= e:
                    f.write(f"  - L{idx+1:4d} inside {fname}()\n")
                    break

print("4. Generating git log and f516855 info ...")
f4_git = os.path.join(scratch_dir, 'p41_kis_broker_gitlog.txt')
with open(f4_git, 'w', encoding='utf-8') as f:
    f.write("=== git log --oneline -- app/services/kis_broker.py ===\n")
    r_glog = subprocess.run('git log --oneline -- app/services/kis_broker.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8')
    f.write(r_glog.stdout + "\n")
    
    f.write("=== git show f516855 --stat ===\n")
    r_f51 = subprocess.run('git show f516855 --stat', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8')
    f.write(r_f51.stdout + "\n")
    
    f.write("=== git show f516855 -- app/services/kis_broker.py ===\n")
    r_f51_diff = subprocess.run('git show f516855 -- app/services/kis_broker.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8')
    f.write(r_f51_diff.stdout + "\n")

print("5. Running full pytest suite tests/ -v -rs ...")
f1_run = os.path.join(scratch_dir, 'p41_full_run.txt')
r_run = subprocess.run([venv_pytest, 'tests/', '-v', '-rs'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
with open(f1_run, 'w', encoding='utf-8') as f:
    f.write(r_run.stdout)
    if r_run.stderr:
        f.write("\n--- STDERR ---\n" + r_run.stderr)

print("ALL STEPS COMPLETED!")

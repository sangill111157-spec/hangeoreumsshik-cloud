# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

out_path = os.path.join(scratch_dir, 'pytest_complete.txt')
cmd = [os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '-v']

print("Running pytest tests/ -v synchronously...")
res = subprocess.run(cmd, cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(res.stdout)
    if res.stderr:
        f.write("\n" + res.stderr)

print("Saved pytest_complete.txt successfully.")
lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
print("Exact last line:", repr(lines[-1]))

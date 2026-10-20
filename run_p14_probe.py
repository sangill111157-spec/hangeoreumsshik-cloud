# -*- coding: utf-8 -*-
import subprocess
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

cmd = [r"C:\trading\package\nvda_trading_system\backend\venv\Scripts\pytest.exe", "-q"]
cwd = r"C:\trading\package\nvda_trading_system\backend"

t_start = time.time()
res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
t_end = time.time()

wall_clock = t_end - t_start

print(f"P14_WALL_CLOCK: {wall_clock:.2f}s")
print(f"P14_RETURN_CODE: {res.returncode}")

out_lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
for line in out_lines[-5:]:
    print(f"OUTPUT: {line}")

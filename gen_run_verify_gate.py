# -*- coding: utf-8 -*-
"""Execute verify.ps1 with external stopwatch and measure wall clock."""
import datetime
import subprocess
import time

print("=== Final Verification Gate Execution with External Stopwatch ===")
start_ts = time.perf_counter()
start_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
print(f"Start Time: {start_dt}")

cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/verify.ps1"]
proc = subprocess.run(cmd, capture_output=True, text=True)

end_ts = time.perf_counter()
end_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
ext_wall = end_ts - start_ts

print(f"End Time: {end_dt}")
print(f"External Wall-Clock (A_ExtWall): {ext_wall:.2f} s")
print("\n--- verify.ps1 stdout ---")
print(proc.stdout)
if proc.stderr:
    print("--- verify.ps1 stderr ---")
    print(proc.stderr)
print(f"verify.ps1 Exit Code: {proc.returncode}")

import subprocess
import urllib.request
import json
import re

backend_dir = r"C:\trading\package\nvda_trading_system\backend"
server_log = r"C:\trading\package\nvda_trading_system\backend\logs\server_20261004.log"

print("=== 1. Check Port 8000 OwningProcess ===")
res_netstat = subprocess.run(
    ["netstat", "-ano"],
    capture_output=True, text=True
)
port_8000_lines = [l for l in res_netstat.stdout.splitlines() if ":8000 " in l]
for l in port_8000_lines:
    print(l)

print("\n=== 2. Check GET /health ===")
try:
    req = urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=5)
    status_code = req.getcode()
    body = req.read().decode("utf-8")
    print(f"Status Code: {status_code}")
    print(f"Body: {body[:300]}")
except Exception as e:
    print(f"Health check failed: {e}")

print("\n=== 3. Check git status --short ===")
res_git = subprocess.run(
    ["git", "status", "--short"],
    cwd=backend_dir, capture_output=True, text=True, encoding="utf-8"
)
print(res_git.stdout)

print("\n=== 4. Check server_20261004.log keywords ===")
with open(server_log, "r", encoding="utf-8", errors="replace") as f:
    log_content = f.read()

keywords = ["SCHEDULER_LOOP_ATTACHED", "Added job", "Traceback", "ImportError"]
for kw in keywords:
    matches = [l for l in log_content.splitlines() if kw in l]
    print(f"'{kw}' count: {len(matches)}")
    if matches and len(matches) <= 10:
        for m in matches:
            print(f"  -> {m}")

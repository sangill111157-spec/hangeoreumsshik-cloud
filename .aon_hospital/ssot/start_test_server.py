# -*- coding: utf-8 -*-
import os, sys, subprocess, time

os.environ["ENABLE_TEST_ENDPOINTS"] = "true"

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# Kill existing port 8000
subprocess.run("powershell -Command \"Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess -Force -ErrorAction SilentlyContinue\"", shell=True)
time.sleep(1)

# Start uvicorn
cmd = f'"{os.path.join(backend_dir, r"venv\Scripts\python.exe")}" -m uvicorn app.main:app --port 8000 --host 127.0.0.1'
proc = subprocess.Popen(cmd, cwd=backend_dir, env=os.environ, shell=True)
print(f"Started uvicorn PID: {proc.pid}")
time.sleep(3)


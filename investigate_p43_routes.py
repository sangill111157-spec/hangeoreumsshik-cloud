# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')

venv_py = os.path.join(backend_dir, 'venv', 'Scripts', 'python.exe')
venv_pytest = os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe')

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ----------------------------------------------------------------------
# 1. Investigate test_order_gate_routes.py & kis.py routes
# ----------------------------------------------------------------------
f_route = os.path.join(scratch_dir, 'p43_route_gate_investigation.txt')
with open(f_route, 'w', encoding='utf-8') as f:
    f.write("=== @router routes in app/api/routes/kis.py ===\n")
    r_kis_rt = subprocess.run('git grep -n "@router\\." app/api/routes/kis.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r_kis_rt.stdout + "\n")

    f.write("=== test_all_live_routes_blocked_in_gate1 Source in tests/test_order_gate_routes.py ===\n")
    rt_file = os.path.join(backend_dir, 'tests', 'test_order_gate_routes.py')
    with open(rt_file, 'r', encoding='utf-8', errors='replace') as rf:
        f.write(rf.read())

# Run a dedicated test script to record actual status codes of all 11 routes under gate 1
code_tester = """
import os, pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

routes = [
    ("/api/kis/orders", "POST"),
    ("/api/kis/orders/overseas", "POST"),
    ("/api/nvda/order", "POST"),
    ("/api/rebalance/execute", "POST"),
    ("/api/stock/order", "POST"),
    ("/api/stock/order/overseas", "POST"),
    ("/api/trader/execute", "POST"),
    ("/api/trader/order/buy", "POST"),
    ("/api/trader/order/sell", "POST"),
    ("/api/kis/orders/123/cancel", "DELETE"),
    ("/api/kis/orders/123/modify", "PUT"),
    ("/api/kis/orders/123/modify", "POST"),
]

print("=== Actual HTTP Status Code for Each Route (Gate 1 Closed) ===")
for path, method in routes:
    if method == "POST":
        res = client.post(path, json={}, headers={"X-Order-Secret": "mock_secret"})
    elif method == "PUT":
        res = client.put(path, json={}, headers={"X-Order-Secret": "mock_secret"})
    elif method == "DELETE":
        res = client.delete(path, headers={"X-Order-Secret": "mock_secret"})
    print(f"[{method:6s}] {path:35s} -> Status {res.status_code} ({res.text[:80]})")
"""

r_status = subprocess.run([venv_py, '-c', code_tester], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
with open(f_route, 'a', encoding='utf-8') as f:
    f.write("\n" + r_status.stdout + "\n")

print("Route gate investigation completed.")

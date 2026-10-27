# -*- coding: utf-8 -*-
import sys, os, inspect

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

target_routes = [
    "/api/kis/orders",
    "/api/kis/orders/{order_id}/cancel",
    "/api/kis/orders/{order_id}/modify",
    "/api/stock/{ticker}/order",
    "/api/nvda/order",
    "/api/trader/close-all",
    "/api/trader/execute",
    "/api/trader/start",
]

print("Scanning app routes for target order endpoints...")
for r in app.routes:
    cls_name = r.__class__.__name__
    if cls_name == "_IncludedRouter":
        orig = getattr(r, "original_router", None)
        if orig and hasattr(orig, "routes"):
            for sub_r in orig.routes:
                path = getattr(sub_r, "path", "")
                methods = getattr(sub_r, "methods", set())
                endpoint = getattr(sub_r, "endpoint", None)
                if path in target_routes and "POST" in methods:
                    file_path = inspect.getsourcefile(endpoint)
                    print(f"Found Target Route: POST {path} -> {endpoint.__name__} in {file_path}")

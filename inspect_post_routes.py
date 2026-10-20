# -*- coding: utf-8 -*-
import sys, os, inspect

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

routes_info = []
for r in app.routes:
    cls_name = r.__class__.__name__
    if cls_name == "_IncludedRouter":
        orig = getattr(r, "original_router", None)
        if orig and hasattr(orig, "routes"):
            for sub_r in orig.routes:
                path = getattr(sub_r, "path", "")
                methods = list(getattr(sub_r, "methods", ["GET"]))
                endpoint = getattr(sub_r, "endpoint", None)
                if "POST" in methods:
                    file_path = inspect.getsourcefile(endpoint) if endpoint else ""
                    routes_info.append({"path": path, "methods": methods, "name": getattr(sub_r, "name", ""), "file": file_path})

for item in routes_info:
    print(f"POST {item['path']} -> {item['name']} in {os.path.basename(item['file'])}")

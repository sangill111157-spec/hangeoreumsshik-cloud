import sys
sys.path.insert(0, r'C:\trading\package\nvda_trading_system\backend')
from app.main import app

def print_all_fastapi_routes(app_instance):
    count = 0
    for r in app_instance.routes:
        cls_name = r.__class__.__name__
        if cls_name == "_IncludedRouter":
            orig = getattr(r, "original_router", None)
            if orig and hasattr(orig, "routes"):
                for sub_r in orig.routes:
                    methods = list(getattr(sub_r, "methods", ["GET"]))
                    path = getattr(sub_r, "path", "")
                    name = getattr(sub_r, "name", "")
                    count += 1
                    print(f"  {str(methods):24s} -> {path:40s} (Endpoint: {name})")
        else:
            methods = list(getattr(r, "methods", ["GET"]))
            path = getattr(r, "path", "")
            name = getattr(r, "name", "")
            count += 1
            print(f"  {str(methods):24s} -> {path:40s} (Endpoint: {name})")
    print(f"\nTotal endpoints printed: {count}")

print_all_fastapi_routes(app)

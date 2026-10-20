# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
main_path = os.path.join(backend_dir, r'app\main.py')

with open(main_path, 'r', encoding='utf-8') as f:
    main_c = f.read()

# Fix settings import in main.py
old_test_inc = """# 결함 133 완결: 테스트 라우터 물리 분리 및 조건부 로드
if getattr(settings, "ENABLE_TEST_ENDPOINTS", False):
    from app.api.routes.test_endpoints import router as test_router
    app.include_router(test_router, prefix="/api")"""

new_test_inc = """# 결함 133 완결: 테스트 라우터 물리 분리 및 조건부 로드
from app.core.config import settings
if getattr(settings, "ENABLE_TEST_ENDPOINTS", False):
    from app.api.routes.test_endpoints import router as test_router
    app.include_router(test_router, prefix="/api")"""

if old_test_inc in main_c:
    main_c = main_c.replace(old_test_inc, new_test_inc)

with open(main_path, 'w', encoding='utf-8') as f:
    f.write(main_c)

subprocess.run('git add app/main.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(main): import settings in main.py for conditional test router registration (defect 133)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update config.py to set ENABLE_TEST_ENDPOINTS: bool = False in all environments by default (defects 81, 86)
cfg_path = os.path.join(backend_dir, r'app\core\config.py')
with open(cfg_path, 'r', encoding='utf-8') as f:
    cfg_c = f.read()

if "ENABLE_TEST_ENDPOINTS: bool = False" not in cfg_c:
    cfg_c = cfg_c.replace("class Settings(BaseSettings):", "class Settings(BaseSettings):\n    ENABLE_TEST_ENDPOINTS: bool = False")
    with open(cfg_path, 'w', encoding='utf-8') as f:
        f.write(cfg_c)

# 2. Update stock.py to check settings.ENABLE_TEST_ENDPOINTS
st_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(st_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

st_c = st_c.replace('if not getattr(settings, "DEBUG", False):', 'if not getattr(settings, "ENABLE_TEST_ENDPOINTS", False):')
with open(st_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

subprocess.run('git add app/core/config.py app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(security): strictly gate test endpoints behind ENABLE_TEST_ENDPOINTS=False by default (defects 81, 86)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


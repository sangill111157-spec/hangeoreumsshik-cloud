# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update master_signal.py calculate_correlation_adjustment
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

old_corr_block = """    # 리더주 강세
    leaders = correlation.get("leader_stocks_positive", 0)
    if leaders >= 3:
        adjustment += 2
    elif leaders == 0:
        adjustment -= 2"""

new_corr_block = """    # 리더주 강세 (결함 36·50 완결: leaders==0 패널티 제거 및 중립 0 처리)
    leaders = correlation.get("leader_stocks_positive", 0)
    if leaders >= 3:
        adjustment += 2"""

if old_corr_block in ms_c:
    ms_c = ms_c.replace(old_corr_block, new_corr_block)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 2. Update stock.py to include module_signal in components return dictionary
st_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(st_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

old_st_comp = """              "components": [
                  {
                      "name": c.name,
                      "score": c.score,
                      "signal": c.signal,
                      "confidence": c.confidence
                  }
                  for c in result.components
              ],"""

new_st_comp = """              "components": [
                  {
                      "name": c.name,
                      "score": c.score,
                      "signal": c.signal,
                      "confidence": c.confidence,
                      "module_signal": getattr(c, "module_signal", None)
                  }
                  for c in result.components
              ],"""

if old_st_comp in st_c:
    st_c = st_c.replace(old_st_comp, new_st_comp)

with open(st_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

subprocess.run('git add app/services/master_signal.py app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(master_signal,stock): remove leaders==0 -2 penalty and expose module_signal in API response (defects 36,50,107)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


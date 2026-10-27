# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update master_signal.py: remove WEIGHTS = BASE_WEIGHTS.copy() and unify on BASE_WEIGHTS (defect 99)
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Remove WEIGHTS = BASE_WEIGHTS.copy()
old_weights_copy = "WEIGHTS = BASE_WEIGHTS.copy()"
new_weights_copy = "# 결함 25·99 해소: WEIGHTS 가변 제2 원천 제거, BASE_WEIGHTS 단일 원천(SSOT) 통일"

if old_weights_copy in ms_c:
    ms_c = ms_c.replace(old_weights_copy, new_weights_copy)

# Add RAW_SCORE_DUMP logging in MasterSignalEngine.calculate_final_master_signal
old_log_conf = """        logger.info(f"INTERNAL_CONSUMED_CONF_MAP: {conf_map}, AVAILABLE_CONFS: {available_confs}")"""
new_log_conf = """        logger.info(f"INTERNAL_CONSUMED_CONF_MAP: {conf_map}, AVAILABLE_CONFS: {available_confs}")
        # 결함 96·97 해소: RAW_SCORE_DUMP 로깅 (항별 7값 + 합계)
        raw_components_map = {m: scores.get(m, 50.0) * weights_used.get(m, 0.0) for m in available_modules}
        logger.info(f"RAW_SCORE_DUMP: components_contrib={raw_components_map}, sum_raw={raw_score:.14f}, master_score={master_score:.14f}")"""

if old_log_conf in ms_c:
    ms_c = ms_c.replace(old_log_conf, new_log_conf)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 2. Update stock.py to add BUY mock endpoint for live route testing if needed or direct route
st_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(st_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

# Ensure stock.py uses BASE_WEIGHTS SSOT
st_c = st_c.replace("WEIGHTS", "BASE_WEIGHTS")
with open(st_path, 'w', encoding='utf-8') as f:
    f.write(st_c)

# 3. Update stock_scanner.py to mark master_score as deprecated (defects 41, 94)
ss_path = os.path.join(backend_dir, r'app\services\stock_scanner.py')
with open(ss_path, 'r', encoding='utf-8') as f:
    ss_c = f.read()

ss_c = ss_c.replace('master_score: float = 0.0  # 하위 호환성 유지용', 'master_score: float = 0.0  # @deprecated: screening_score 사용 권장 (결함 94)')
with open(ss_path, 'w', encoding='utf-8') as f:
    f.write(ss_c)

subprocess.run('git add app/services/master_signal.py app/api/routes/stock.py app/services/stock_scanner.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(master_signal,scanner): remove WEIGHTS second SSOT source, add RAW_SCORE_DUMP logging, mark master_score deprecated in CandidateStock (defects 94,96,99)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


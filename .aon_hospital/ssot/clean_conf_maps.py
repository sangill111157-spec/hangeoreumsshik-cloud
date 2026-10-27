# -*- coding: utf-8 -*-
import sys, os, subprocess, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Pattern for the redundant early conf_map
p1 = r'        # 3\. 신뢰도 SSOT 단일 원천 맵.*?        logger\.info\(f"AVAILABLE_CONFS: \{avail_conf_list\}"\)'
# Replace all redundant conf_maps with clean logic
ms_c = re.sub(p1, '', ms_c, flags=re.DOTALL)

# Ensure the main calculate_final_master_signal uses ONLY the SSOT conf_map
# Let's inspect where conf_map is defined in calculate_final_master_signal
with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# Let's check remaining conf_map
matches = re.findall(r'conf_map = \{.*?\}', ms_c, flags=re.DOTALL)
print(f"Remaining conf_map count: {len(matches)}")


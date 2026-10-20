# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')

with open(ms_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the second def calculate_final_master_signal
first_idx = -1
second_idx = -1
for i, l in enumerate(lines):
    if "def calculate_final_master_signal(" in l:
        if first_idx == -1:
            first_idx = i
        else:
            second_idx = i
            break

print(f"First idx: {first_idx}, Second idx: {second_idx}")
if second_idx != -1:
    # Find end of second method (next method in MasterSignalEngine or class end)
    end_idx = len(lines)
    for j in range(second_idx + 1, len(lines)):
        if lines[j].startswith("    def ") and not lines[j].strip().startswith("#"):
            end_idx = j
            break
        elif lines[j].startswith("class "):
            end_idx = j
            break
    print(f"Deleting lines {second_idx} to {end_idx}")
    lines = lines[:second_idx] + lines[end_idx:]

with open(ms_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

subprocess.run('git add app/services/master_signal.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(master_signal): delete duplicate second calculate_final_master_signal method (defects 102,106,108,111)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


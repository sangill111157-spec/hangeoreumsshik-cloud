# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
tech_path = os.path.join(backend_dir, r'app\services\technical_analysis.py')

with open(tech_path, 'r', encoding='utf-8') as f:
    tech_c = f.read()

# Fix technical_analysis.py confidence calculation
old_block = """        # Calculate confidence with SSOT clamp_conf
        total_indicators = len(signals)
        aligned_signals = sum(1 for s in signals if s.lower() in overall_signal.lower() or overall_signal.lower() in s.lower())
        confidence = clamp_conf((aligned_signals / float(total_indicators) if total_indicators > 0 else 0.5) * 100.0)

        return trend, overall_signal, confidence"""

new_block = """        # Calculate confidence with SSOT clamp_conf (결함 102 완결)
        confidence = clamp_conf(ratio * 100.0)

        return trend, overall_signal, confidence"""

if old_block in tech_c:
    tech_c = tech_c.replace(old_block, new_block)

with open(tech_path, 'w', encoding='utf-8') as f:
    f.write(tech_c)

subprocess.run('git add app/services/technical_analysis.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(technical): calculate confidence directly from ratio using clamp_conf (defect 102)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# Patch technical_analysis.py TechnicalAnalysisResult return with available=True
tech_path = os.path.join(backend_dir, r'app\services\technical_analysis.py')
with open(tech_path, 'r', encoding='utf-8') as f:
    tech_c = f.read()

old_tech_ret = """            trend=trend,
            overall_signal=overall_signal,
            confidence=confidence
        )"""

new_tech_ret = """            trend=trend,
            overall_signal=overall_signal,
            confidence=confidence,
            available=True
        )"""

if old_tech_ret in tech_c:
    tech_c = tech_c.replace(old_tech_ret, new_tech_ret)
    with open(tech_path, 'w', encoding='utf-8') as f:
        f.write(tech_c)
    print("technical_analysis.py TechnicalAnalysisResult return patched with available=True!")

# Commit
subprocess.run('git add app/services/technical_analysis.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(tech): set available=True on TechnicalAnalysisResult return (defect 48 recovery)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


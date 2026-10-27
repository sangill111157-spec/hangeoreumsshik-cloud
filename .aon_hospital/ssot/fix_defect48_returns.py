# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Patch investor_analysis.py InvestorAnalysisResult return with available=True
inv_path = os.path.join(backend_dir, r'app\services\investor_analysis.py')
with open(inv_path, 'r', encoding='utf-8') as f:
    inv_c = f.read()

old_inv_ret = """        return InvestorAnalysisResult(
            ticker=ticker,
            timestamp=datetime.now().isoformat(),
            current_price=current_price,
            currency=currency,
            signals=signals,
            overall_signal=overall_signal,
            overall_confidence=overall_confidence,
            consensus_score=consensus_score,
            bull_count=bullish_count,
            bear_count=bear_count,
            neutral_count=neutral_count,
            summary=summary
        )"""

new_inv_ret = """        return InvestorAnalysisResult(
            ticker=ticker,
            timestamp=datetime.now().isoformat(),
            current_price=current_price,
            currency=currency,
            signals=signals,
            overall_signal=overall_signal,
            overall_confidence=overall_confidence,
            consensus_score=consensus_score,
            bull_count=bullish_count,
            bear_count=bear_count,
            neutral_count=neutral_count,
            summary=summary,
            available=True
        )"""

if old_inv_ret in inv_c:
    inv_c = inv_c.replace(old_inv_ret, new_inv_ret)
    with open(inv_path, 'w', encoding='utf-8') as f:
        f.write(inv_c)
    print("investor_analysis.py return patched with available=True!")

# 2. Patch stock.py technical dict creation with available
stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(stock_path, 'r', encoding='utf-8') as f:
    st_c = f.read()

old_tech_dict = """        technical = {
            "overall_signal": technical_obj.overall_signal,
            "confidence": technical_obj.confidence,
            "trend": technical_obj.trend
        }"""

new_tech_dict = """        technical = {
            "overall_signal": technical_obj.overall_signal,
            "confidence": technical_obj.confidence,
            "trend": technical_obj.trend,
            "available": bool(getattr(technical_obj, "available", True))
        }"""

if old_tech_dict in st_c:
    st_c = st_c.replace(old_tech_dict, new_tech_dict)
    with open(stock_path, 'w', encoding='utf-8') as f:
        f.write(st_c)
    print("stock.py technical dict patched with available!")

# 3. Patch technical_analysis.py TechnicalAnalysisResult return with available=True
tech_path = os.path.join(backend_dir, r'app\services\technical_analysis.py')
with open(tech_path, 'r', encoding='utf-8') as f:
    tech_c = f.read()

if 'available=True' not in tech_c and 'TechnicalAnalysisResult(' in tech_c:
    tech_c = tech_c.replace("summary=summary\n        )", "summary=summary,\n            available=True\n        )")
    with open(tech_path, 'w', encoding='utf-8') as f:
        f.write(tech_c)
    print("technical_analysis.py return patched with available=True!")

# Commit changes
subprocess.run('git add app/services/investor_analysis.py app/services/technical_analysis.py app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(stock,inv,tech): explicitly assign available=True on successful returns to restore coverage 1.00 (defects 47 & 48)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


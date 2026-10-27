# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'C:\trading\package\nvda_trading_system\backend\app\services\investor_analysis.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old = '''        # 4. Debt/Equity - Dynamic data
        if debt_to_equity and debt_to_equity > 0:
            key_metrics["debt_to_equity"] = f"{debt_to_equity * 100:.1f}%"
            if debt_to_equity < 0.5:
                bullish_count += 1
                reasoning.append(f"\ubd80\ucc44\ube44\uc728: {debt_to_equity * 100:.1f}% (\uc6b0\uc218)")
            elif debt_to_equity < 1.0:
                reasoning.append(f"\ubd80\ucc44\ube44\uc728: {debt_to_equity * 100:.1f}% (\uc591\ud638)")'''

new = '''        # 4. Debt/Equity - Dynamic data
        # yfinance debtToEquity\ub294 \uc774\ubbf8 \ubc31\ubd84\uc728 (\uc608: 6.555 = 6.555%)
        if debt_to_equity is not None and debt_to_equity > 0:
            key_metrics["debt_to_equity"] = f"{debt_to_equity:.1f}%"
            if debt_to_equity < 50.0:
                bullish_count += 1
                reasoning.append(f"\ubd80\ucc44\ube44\uc728: {debt_to_equity:.1f}% (\uac74\uc804)")
            elif debt_to_equity < 100.0:
                reasoning.append(f"\ubd80\ucc44\ube44\uc728: {debt_to_equity:.1f}% (\uc591\ud638)")
            else:
                reasoning.append(f"\ubd80\ucc44\ube44\uc728: {debt_to_equity:.1f}% (\uc8fc\uc758)")'''

if old in content:
    content = content.replace(old, new)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('PATCHED OK')
else:
    print('TARGET NOT FOUND - searching for current text...')
    # Debug: find the actual text
    import re
    match = re.search(r'# 4\. Debt.*?(?=# 5\.)', content, re.DOTALL)
    if match:
        print(repr(match.group()))
    else:
        print('Section 4 not found at all')

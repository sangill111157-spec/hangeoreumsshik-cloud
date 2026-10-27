# -*- coding: utf-8 -*-
ms_file = r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py'
with open(ms_file, 'r', encoding='utf-8') as f:
    content = f.read()

t = "kelly=KellyCriterion(0.0, 0, 0.0, 0.0, 0.0)"
r = "kelly=KellyCriterion(0.0, 0, 0.0, 0.0, 0.0, 0.0)"

content = content.replace(t, r)
with open(ms_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("FIXED KellyCriterion call")

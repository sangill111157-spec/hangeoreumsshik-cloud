# -*- coding: utf-8 -*-
import os, sys

# 1. Inspect P-1 lines in stock.py and master_signal.py
with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8') as f:
    s_lines = f.readlines()

print('=== 1. stock.py pod_result lines (665~690) ===')
for i in range(665, 690):
    print(f"{i+1:4d}: {s_lines[i]}", end='')

with open(r'C:\trading\package\nvda_trading_system\backend\app\services\pod_manager.py', 'r', encoding='utf-8') as f:
    p_lines = f.readlines()
print('\n=== PodManager.analyze_all signature ===')
for i in range(485, 495):
    print(f"{i+1:4d}: {p_lines[i]}", end='')

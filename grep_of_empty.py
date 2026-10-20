# -*- coding: utf-8 -*-
import subprocess, os

# 1. grep .empty in options_flow.py
of_file = r'C:\trading\package\nvda_trading_system\backend\app\services\options_flow.py'
with open(of_file, 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if '.empty' in l:
            print(f"Line {i+1:4d}: {l.strip()}")

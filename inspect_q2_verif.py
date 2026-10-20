# -*- coding: utf-8 -*-
import subprocess, os, re

# =========================================================================
# 1. Section 2: Q-2 inspection
# =========================================================================
print('=== 1. Section 2: Q-2 inspection ===')
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

print('--- App.tsx lines 275~305 ---')
for i in range(274, min(len(app_lines), 305)):
    print(f"{i+1:4d}: {app_lines[i]}", end='')

print('\n--- App.tsx lines 395~420 (masterLoadingRef) ---')
for i in range(394, min(len(app_lines), 420)):
    print(f"{i+1:4d}: {app_lines[i]}", end='')

print('\n--- grep useRef in App.tsx ---')
for i, l in enumerate(app_lines):
    if 'useRef' in l:
        print(f"{i+1:4d}: {l.strip()}")

print('\n--- grep function App in App.tsx ---')
for i, l in enumerate(app_lines):
    if 'function App' in l or 'const App' in l:
        print(f"{i+1:4d}: {l.strip()}")

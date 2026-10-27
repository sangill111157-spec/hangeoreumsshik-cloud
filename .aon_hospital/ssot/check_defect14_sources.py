# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

print("==================================================")
print("1. [F 착수 조건 1] portfolio_manager.py and telegram_command_listener.py original source")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\portfolio_manager.py'), 'r', encoding='utf-8') as f:
    pm_lines = f.readlines()
print("--- portfolio_manager.py lines 500-525 ---")
for i in range(495, min(len(pm_lines), 525)):
    print(f"portfolio_manager.py:{i+1:4d}: {pm_lines[i].rstrip()}")

with open(os.path.join(backend_dir, r'app\services\telegram_command_listener.py'), 'r', encoding='utf-8') as f:
    tc_lines = f.readlines()
print("\n--- telegram_command_listener.py lines 60-80 ---")
for i in range(58, min(len(tc_lines), 80)):
    print(f"telegram_command_listener.py:{i+1:4d}: {tc_lines[i].rstrip()}")

print("\n==================================================")
print("2. [F 착수 조건 2] stock_scanner.py secondary filter exception handling")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\stock_scanner.py'), 'r', encoding='utf-8') as f:
    ss_lines = f.readlines()
for i in range(255, min(len(ss_lines), 305)):
    print(f"stock_scanner.py:{i+1:4d}: {ss_lines[i].rstrip()}")


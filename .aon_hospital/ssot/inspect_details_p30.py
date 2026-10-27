# -*- coding: utf-8 -*-
import sys, os, subprocess, json, inspect

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def read_file_lines(path, start=1, end=None):
    full_path = os.path.join(backend_dir, path)
    with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    if end is None:
        end = len(lines)
    return "".join(f"{i+1:4d}: {lines[i]}" for i in range(start-1, min(end, len(lines))))

print("==================================================")
print("1. _send_telegram in scheduler.py & auto_trader.py")
print("==================================================")
print("\n--- scheduler.py _send_telegram (lines 240 to 285) ---")
print(read_file_lines('app/services/scheduler.py', 240, 285))

print("\n--- auto_trader.py _send_telegram (lines 130 to 175) ---")
print(read_file_lines('app/services/auto_trader.py', 130, 175))

print("\n==================================================")
print("2. telegram_notifier.py session lifecycle & __init__")
print("==================================================")
print(read_file_lines('app/services/telegram_notifier.py', 1, 120))
print("\n--- telegram_notifier.py send_message / http methods ---")
print(read_file_lines('app/services/telegram_notifier.py', 121, 250))

print("\n==================================================")
print("3. calculate_master_signal in scheduler.py & master_signal.py")
print("==================================================")
print("\n--- scheduler.py lines 200 to 240 (startup / health check) ---")
print(read_file_lines('app/services/scheduler.py', 200, 240))

print("\n--- scheduler.py lines 600 to 640 (auto-trading job) ---")
print(read_file_lines('app/services/scheduler.py', 600, 640))

print("\n--- master_signal.py lines 1210 to 1240 ---")
print(read_file_lines('app/services/master_signal.py', 1210, 1240))

print("\n==================================================")
print("4. job_stop_loss_monitor full source (scheduler.py)")
print("==================================================")
print(read_file_lines('app/services/scheduler.py', 335, 555))

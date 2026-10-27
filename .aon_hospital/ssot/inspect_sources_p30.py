# -*- coding: utf-8 -*-
import sys, os, subprocess, json, inspect

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def print_section(title, content):
    print("=" * 60)
    print(title)
    print("=" * 60)
    print(content)

# 1. _send_telegram in scheduler.py
with open(os.path.join(backend_dir, 'app/services/scheduler.py'), 'r', encoding='utf-8') as f:
    sched_lines = f.readlines()
print_section("1. _send_telegram in scheduler.py (lines 245 to 290)", "".join(f"{i+1:4d}: {sched_lines[i]}" for i in range(244, min(290, len(sched_lines)))))

# 2. _send_telegram in auto_trader.py
with open(os.path.join(backend_dir, 'app/services/auto_trader.py'), 'r', encoding='utf-8') as f:
    trader_lines = f.readlines()
print_section("2. _send_telegram in auto_trader.py (lines 135 to 175)", "".join(f"{i+1:4d}: {trader_lines[i]}" for i in range(134, min(175, len(trader_lines)))))

# 3. telegram_notifier.py full lifecycle & session
with open(os.path.join(backend_dir, 'app/services/telegram_notifier.py'), 'r', encoding='utf-8') as f:
    tn_lines = f.readlines()
print_section("3. telegram_notifier.py (lines 20 to 180)", "".join(f"{i+1:4d}: {tn_lines[i]}" for i in range(19, min(180, len(tn_lines)))))

# 4. calculate_master_signal branch in scheduler.py lines 205 to 235
print_section("4. calculate_master_signal branch in scheduler.py (lines 205 to 240)", "".join(f"{i+1:4d}: {sched_lines[i]}" for i in range(204, min(240, len(sched_lines)))))

# 5. git log to check previous commits
res_git_log = subprocess.run('git log --oneline -n 10', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print_section("5. Recent git commits", res_git_log.stdout)

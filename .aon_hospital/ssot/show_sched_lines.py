# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

with open(os.path.join(backend_dir, 'app/services/scheduler.py'), 'r', encoding='utf-8') as f:
    lines = f.readlines()

def show_range(start, end, title):
    print(f"\n{'='*50}\n{title} (lines {start} to {end})\n{'='*50}")
    for i in range(start-1, min(end, len(lines))):
        print(f"{i+1:4d}: {lines[i]}", end="")

show_range(135, 185, "_load_stop_loss_state")
show_range(335, 385, "job_stop_loss_monitor entry & disabled check")
show_range(740, 785, "get_status / stop / shutdown")

# -*- coding: utf-8 -*-
import os

backend_dir = r"C:\trading\package\nvda_trading_system\backend"
sched_path = os.path.join(backend_dir, "app", "services", "scheduler.py")

with open(sched_path, "r", encoding="utf-8") as f:
    c = f.read()

target = "CronTrigger(day_of_week='mon-fri', hour='9-16', minute=30, timezone=ny_tz)"
replacement = "CronTrigger(day_of_week='mon-fri', hour='9-15', minute=30, timezone=ny_tz)"

if target in c:
    c = c.replace(target, replacement, 1)
    # Also update comment if present
    c = c.replace("09:30 ~ 16:30 ET", "09:30 ~ 15:30 ET", 1)
    with open(sched_path, "w", encoding="utf-8") as f:
        f.write(c)
    print("SUCCESS: hourly_scan updated to hour='9-15'")
else:
    print("ERROR: target not found")

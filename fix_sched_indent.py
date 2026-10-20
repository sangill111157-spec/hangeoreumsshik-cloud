# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sched_file = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')

with open(sched_file, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "            self._stop_loss_disabled = False\n        self._stop_loss_disabled_last_alert: float = 0.0",
    "            self._stop_loss_disabled = False\n            self._stop_loss_disabled_last_alert: float = 0.0"
)

with open(sched_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed indent in scheduler.py")

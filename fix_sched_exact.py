# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sched_file = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')

with open(sched_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for idx, line in enumerate(lines):
    # If line contains self._stop_loss_disabled_last_alert inside _load_stop_loss_state, skip it
    if "self._stop_loss_disabled_last_alert: float = 0.0" in line:
        continue
    if "self._telegram_fail_count: int = 0" in line:
        continue
    if "self._stop_loss_disabled: bool = False" in line:
        new_lines.append(line)
        new_lines.append("        self._stop_loss_disabled_last_alert: float = 0.0\n")
        new_lines.append("        self._telegram_fail_count: int = 0\n")
        continue
    new_lines.append(line)

with open(sched_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Applied exact line-based fix to scheduler.py")

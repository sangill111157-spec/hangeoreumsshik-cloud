# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding='utf-8')
target_sched = r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py"

with open(target_sched, "r", encoding="utf-8") as f:
    text = f.read()

# Replace with self._stop_loss_telegram_lock:
bad_lock = '''        with self._stop_loss_telegram_lock:
            if not self._stop_loss_telegram_deferred_alerts:
                return'''

good_check = '''        if not self._stop_loss_telegram_deferred_alerts:
            return'''

assert bad_lock in text, "bad_lock not found"
text = text.replace(bad_lock, good_check, 1)

with open(target_sched, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)

print("Fixed lock attribute error successfully!")

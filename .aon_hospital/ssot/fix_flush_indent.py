# -*- coding: utf-8 -*-
import sys

target_sched = r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py"

with open(target_sched, "r", encoding="utf-8") as f:
    text = f.read()

bad_check = '''        if not self._stop_loss_telegram_deferred_alerts:
            return'''

good_check = '''        if self._stop_loss_telegram_deferred_alerts:'''

assert bad_check in text, "bad_check not found"
text = text.replace(bad_check, good_check, 1)

with open(target_sched, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)

print("Restored if self._stop_loss_telegram_deferred_alerts: successfully!")

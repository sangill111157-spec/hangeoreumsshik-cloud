# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("Why test_stop_loss_disabled_alert.py failed:")
print("================================================================================")
# In test_stop_loss_disabled_alert.py:
# It wrote invalid json to STOP_LOSS_STATE_FILE (which was monkeypatched to a temporary file by conftest!),
# BUT in test_stop_loss_disabled_alert.py, it imports STOP_LOSS_STATE_FILE at module load time (before conftest monkeypatching took effect, or it used the old path).
# Let's inspect test_stop_loss_disabled_alert.py L10-25
p = os.path.join(backend_dir, 'tests', 'test_stop_loss_disabled_alert.py')
with open(p, 'r', encoding='utf-8', errors='replace') as f:
    print(f.read())

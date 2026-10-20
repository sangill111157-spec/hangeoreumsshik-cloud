import sys
sys.stdout.reconfigure(encoding='utf-8')

target_file = r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py"

with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

import_stmt = "from app.services.telegram_notifier import format_telegram_alert\n"
if import_stmt not in code:
    code = import_stmt + code
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: format_telegram_alert prepended to scheduler.py")
else:
    print("Already present")

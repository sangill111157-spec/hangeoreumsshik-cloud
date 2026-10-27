import sys
sys.stdout.reconfigure(encoding='utf-8')

target_file = r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py"

with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

target = "from app.services.telegram_notifier import get_telegram_notifier, TelegramMessage"
replacement = "from app.services.telegram_notifier import get_telegram_notifier, TelegramMessage, format_telegram_alert"

if target in code:
    code = code.replace(target, replacement, 1)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: format_telegram_alert imported in scheduler.py")
else:
    print("Target not found, checking alternative import pattern")
    target_alt = "from app.services.telegram_notifier import"
    for line in code.splitlines():
        if "from app.services.telegram_notifier import" in line:
            print("Found line:", repr(line))

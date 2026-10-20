import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "3600" in line or "1시간" in line or "_stop_loss_fetch_fail_last_alert" in line:
        print(f"{i+1}: {line.strip()[:140]}")

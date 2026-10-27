target_file = r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "_stop_loss_scan_fail" in l or "_stop_loss_fetch_fail" in l or "3600.0" in l or "def job_stop_loss_monitor" in l or "for ticker in active_tickers:" in l:
        print(f"{i+1}: {repr(l)}")

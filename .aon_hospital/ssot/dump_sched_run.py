import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'def job_stop_loss_monitor' in line or 'def _run_async' in line or 'asyncio.run' in line:
        for j in range(max(0, i-2), min(len(lines), i+30)):
            print(f"{j+1}: {lines[j]}", end='')
        print("\n" + "="*40 + "\n")

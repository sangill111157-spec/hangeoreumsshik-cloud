import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if any(k in line for k in ['65536', 'misfire', 'EVENT_JOB', 'max_instances', 'stop_loss']):
        print(f"{i+1}: {line.strip()}")

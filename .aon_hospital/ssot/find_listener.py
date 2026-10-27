import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'add_listener' in line or '_listener' in line or 'EVENT_' in line:
            print(f"{i+1}: {line.strip()}")

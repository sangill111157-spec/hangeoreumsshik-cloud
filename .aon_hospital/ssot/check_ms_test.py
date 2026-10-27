import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\trading\package\nvda_trading_system\backend\tests\test_master_signal_none_weight_zero.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[25:], 26):
        print(f"{i}: {line}", end='')

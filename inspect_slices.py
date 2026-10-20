import sys
sys.stdout.reconfigure(encoding='utf-8')

target_file = r"C:\trading\package\nvda_trading_system\backend\tests\test_scheduler_sizing.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("=== SLICE 2050-2130 ===")
for i in range(2050, 2130):
    print(f"{i+1}: {repr(lines[i])}")

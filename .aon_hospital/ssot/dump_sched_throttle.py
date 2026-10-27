import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("=== Lines 910-930 ===")
for i in range(909, 930):
    print(f"{i+1}: {lines[i]}", end='')

print("\n=== Lines 1330-1350 ===")
for i in range(1329, 1350):
    print(f"{i+1}: {lines[i]}", end='')

import sys
sys.stdout.reconfigure(encoding='utf-8')

p = r"C:\trading\package\nvda_trading_system\backend\scripts\verify.ps1"
with open(p, "r", encoding="utf-8", errors="replace") as f:
    print(f.read())

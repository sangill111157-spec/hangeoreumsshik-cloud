import sys
sys.stdout.reconfigure(encoding='utf-8')

server_log = r"C:\trading\package\nvda_trading_system\backend\logs\server_20261004.log"
with open(server_log, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "Traceback" in l:
        print(f"=== Line {i+1} ===")
        start = max(0, i - 2)
        end = min(len(lines), i + 20)
        for j in range(start, end):
            print(f"{j+1}: {lines[j]}", end="")
        print()

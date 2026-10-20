kis_broker_path = r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py"
with open(kis_broker_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "rt_cd" in line and ("output" in line or "None" in line):
        for j in range(max(0, i-2), min(len(lines), i+8)):
            print(f"{j+1}: {lines[j]}", end="")
        print("---")

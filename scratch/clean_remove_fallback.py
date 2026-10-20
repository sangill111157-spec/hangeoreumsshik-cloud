kis_broker_path = r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py"

with open(kis_broker_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip_next = False
for line in lines:
    if 'if rt_cd is None and ("output" in data or "output1" in data):' in line:
        skip_next = True
        continue
    if skip_next and 'rt_cd = "0"' in line:
        skip_next = False
        continue
    new_lines.append(line)

with open(kis_broker_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Cleanly removed rt_cd fallback from kis_broker.py!")

import sys
import re
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

server_log = r"C:\trading\package\nvda_trading_system\backend\logs\server_20261004.log"
with open(server_log, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

print("=== 1. Traceback 2건 원문 추출 ===")
tb_indices = [i for i, l in enumerate(lines) if "Traceback (most recent call last):" in l]
print(f"Traceback header line indices: {tb_indices}")

# We saw line 430 and line 1539
for idx in [429, 1538]:  # 0-indexed
    print(f"\n--- Traceback around line {idx+1} ---")
    start = max(0, idx - 15)
    end = min(len(lines), idx + 25)
    for j in range(start, end):
        print(f"{j+1}: {lines[j]}", end="")

print("\n\n=== 2. EGW00201 27건 전수 추출 ===")
egw_records = []
for i, l in enumerate(lines):
    if "EGW00201" in l or "초당 거래건수를 초과" in l:
        egw_records.append((i, l))

print(f"Total EGW00201 lines: {len(egw_records)}")

# Let's inspect each occurrence and its context
parsed_egw = []
for idx, line in egw_records:
    # timestamp
    ts_match = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})", line)
    ts_str = ts_match.group(1) if ts_match else "unknown"
    
    # context around this line (±5 lines)
    context_lines = lines[max(0, idx-5):min(len(lines), idx+6)]
    
    parsed_egw.append({
        "line_no": idx + 1,
        "raw_line": line.strip(),
        "timestamp": ts_str,
        "context": context_lines
    })

print(f"Successfully collected {len(parsed_egw)} EGW00201 events.")

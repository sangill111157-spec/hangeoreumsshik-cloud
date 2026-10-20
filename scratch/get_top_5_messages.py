import sys
import re
from datetime import datetime, timedelta
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

server_log_path = r"C:\trading\package\nvda_trading_system\backend\logs\server_20261004.log"

with open(server_log_path, "r", encoding="utf-8", errors="replace") as f:
    s_lines = f.readlines()

start_dt = datetime(2026, 10, 4, 12, 24, 21)
window_30m_end = start_dt + timedelta(minutes=30)

first_30m_lines = []
for l in s_lines:
    m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", l)
    if m:
        dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
        if start_dt <= dt <= window_30m_end:
            first_30m_lines.append(l)

print(f"Total lines in first 30 minutes (12:24 ~ 12:54): {len(first_30m_lines)}")

normalized = []
for l in first_30m_lines:
    msg = re.sub(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - ", "", l.strip())
    msg = re.sub(r"'elapsed_sec': \d+\.\d+", "'elapsed_sec': <N>", msg)
    msg = re.sub(r"next run at: [^\)]+", "next run at: <TIME>", msg)
    msg = re.sub(r"scheduled at: [^\)]+", "scheduled at: <TIME>", msg)
    normalized.append(msg)

counts = Counter(normalized)
print("\n=== Top 5 Messages in First 30 Minutes ===")
for msg, cnt in counts.most_common(5):
    print(f"[{cnt}건] {msg[:120]}")

import os
import sys
import re
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

server_log_path = r"C:\trading\package\nvda_trading_system\backend\logs\server_20261004.log"
app_log_path = r"C:\trading\package\nvda_trading_system\backend\logs\app.log"

with open(server_log_path, "r", encoding="utf-8", errors="replace") as f:
    s_lines = f.readlines()

# find first timestamp in server_log
start_dt = None
for l in s_lines:
    m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", l)
    if m:
        start_dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
        break

# find latest timestamp
latest_dt = None
for l in reversed(s_lines):
    m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", l)
    if m:
        latest_dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
        break

print(f"Start DateTime: {start_dt}")
print(f"Latest DateTime: {latest_dt}")

elapsed_sec = (latest_dt - start_dt).total_seconds()
elapsed_min = elapsed_sec / 60.0
elapsed_hours = elapsed_sec / 3600.0

server_size_bytes = os.path.getsize(server_log_path)
app_size_bytes = os.path.getsize(app_log_path)

print(f"Elapsed: {elapsed_min:.1f} minutes ({elapsed_hours:.2f} hours)")
print(f"server_20261004.log size: {server_size_bytes:,} bytes ({server_size_bytes / 1024:.2f} KB)")
print(f"app.log size: {app_size_bytes:,} bytes ({app_size_bytes / 1024:.2f} KB)")

# Size at 30 min (pro-rated / exact)
bytes_per_sec = server_size_bytes / elapsed_sec
size_at_30m = bytes_per_sec * 1800.0
daily_server_mb = (bytes_per_sec * 86400.0) / (1024 * 1024)

print(f"\nBytes per second: {bytes_per_sec:.2f} B/s")
print(f"30-min server log size (estimated): {size_at_30m / 1024:.2f} KB")
print(f"Daily server_20261004.log estimate: {daily_server_mb:.2f} MB / day")

# Check app.log lines added during server run
# Find app.log lines starting around start_dt
with open(app_log_path, "r", encoding="utf-8", errors="replace") as f:
    a_lines = f.readlines()

server_app_lines = []
for l in a_lines:
    m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", l)
    if m:
        dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
        if dt >= start_dt:
            server_app_lines.append(l)

app_added_bytes = sum(len(l.encode("utf-8")) for l in server_app_lines)
print(f"\napp.log lines added since server start ({start_dt}): {len(server_app_lines)} lines")
print(f"app.log bytes added since server start: {app_added_bytes:,} bytes ({app_added_bytes / 1024:.2f} KB)")

daily_app_mb = (app_added_bytes / elapsed_sec * 86400.0) / (1024 * 1024)
print(f"Daily app.log increase estimate: {daily_app_mb:.2f} MB / day")

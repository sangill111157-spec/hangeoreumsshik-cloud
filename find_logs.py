import sys
sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\sangi\.gemini\antigravity-ide\brain\ec6dfafd-d033-4251-9255-a00a3f742816\.system_generated\tasks\task-4193.log"

with open(log_path, "r", encoding="utf-8", errors="replace") as f:
    first_lines = [f.readline() for _ in range(10)]

print("First 10 lines of task-4193.log:")
for l in first_lines:
    print(l.strip())

# Check backend logs directory
import os
print("\nChecking C:\\trading\\package\\nvda_trading_system\\backend for log files:")
for root, dirs, files in os.walk(r"C:\trading\package\nvda_trading_system\backend"):
    for file in files:
        if file.endswith(".log") or "log" in file:
            p = os.path.join(root, file)
            print(f"{p} ({os.path.getsize(p)} bytes)")

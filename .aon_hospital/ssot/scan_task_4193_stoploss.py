import sys
import re
sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\sangi\.gemini\antigravity-ide\brain\ec6dfafd-d033-4251-9255-a00a3f742816\.system_generated\tasks\task-4193.log"

patterns = ['stop_loss', 'STOP_LOSS', '손절', '65536', 'max_instances', 'job_stop_loss_monitor']

print("Searching task-4193.log...")
with open(log_path, "r", encoding="utf-8", errors="replace") as f:
    for line_num, line in enumerate(f, 1):
        if any(p in line for p in patterns):
            if "2026-09-25 09:" in line or "2026-09-25 10:0" in line:
                print(f"{line_num}: {line.strip()[:150]}")

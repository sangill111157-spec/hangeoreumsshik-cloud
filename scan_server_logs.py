import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

brain_dir = r"C:\Users\sangi\.gemini\antigravity-ide\brain\ec6dfafd-d033-4251-9255-a00a3f742816\.system_generated\tasks"

def scan_file(fname):
    p = os.path.join(brain_dir, fname)
    if not os.path.exists(p):
        print(f"File {fname} not found")
        return
    print(f"=== Scanning {fname} (size: {os.path.getsize(p)}) ===")
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            if any(k in line for k in ['65536', 'misfire', '스킵', 'Event loop', 'scan_watchlist', 'AttributeError', 'STOP_LOSS', 'stop_loss_monitor']):
                print(f"[{fname}:{i}] {line.strip()[:140]}")

scan_file("task-4193.log")
scan_file("task-4735.log")

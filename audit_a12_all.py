import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
backend_dir = r"C:\trading\package\nvda_trading_system\backend"

print("=================================================================")
print("=== a-1 (D-111): git log -L & git blame on scheduler.py ===")
print("=================================================================")
p_log = subprocess.run(["git", "-C", backend_dir, "log", "-L", "59,89:app/services/scheduler.py", "--oneline"], capture_output=True, text=True)
print("--- git log -L 59,89:app/services/scheduler.py --oneline ---")
print(p_log.stdout)
print("Exit code:", p_log.returncode)

p_blame = subprocess.run(["git", "-C", backend_dir, "blame", "-L", "78,86", "--", "app/services/scheduler.py"], capture_output=True, text=True)
print("--- git blame -L 78,86 -- app/services/scheduler.py ---")
print(p_blame.stdout)
print("Exit code:", p_blame.returncode)


print("\n=================================================================")
print("=== a-2 (D-112): kis_broker.py POST & ORDER ENDPOINTS AUDIT ===")
print("=================================================================")
kb_path = os.path.join(backend_dir, "app", "services", "kis_broker.py")
with open(kb_path, "r", encoding="utf-8", errors="ignore") as fp:
    kb_lines = fp.readlines()

coords = [231, 310, 710, 799, 800, 977, 1098, 1099, 1216, 1217, 1282]
for c in [231, 310, 710, 799, 977, 1098, 1216, 1282]:
    start_l = max(0, c - 15)
    end_l = min(len(kb_lines), c + 15)
    print(f"\n--- Coordinate around Line {c} (Lines {start_l+1} to {end_l}) ---")
    for j in range(start_l, end_l):
        print(f"  L{j+1:04d}: {kb_lines[j]}", end="")


print("\n=================================================================")
print("=== a-3 (D-119, D-110): add_job BLOCK & auto_trader.py DRY-RUN ===")
print("=================================================================")
sch_path = os.path.join(backend_dir, "app", "services", "scheduler.py")
with open(sch_path, "r", encoding="utf-8", errors="ignore") as fp:
    sch_lines = fp.readlines()

print("--- scheduler.py setup_schedule() add_job blocks (lines 344-390) ---")
for j in range(343, min(390, len(sch_lines))):
    print(f"  L{j+1:03d}: {sch_lines[j]}", end="")

at_path = os.path.join(backend_dir, "app", "services", "auto_trader.py")
with open(at_path, "r", encoding="utf-8", errors="ignore") as fp:
    at_lines = fp.readlines()

print("\n--- auto_trader.py dry_run branch around Line 261 (lines 250-275) ---")
for j in range(249, min(275, len(at_lines))):
    print(f"  L{j+1:03d}: {at_lines[j]}", end="")


print("\n=================================================================")
print("=== a-4 (D-126, D-87): backend/data MTIME FORENSICS (TOP 40) ===")
print("=================================================================")
data_dir = os.path.join(backend_dir, "data")
all_data_files = []
for root, dirs, files in os.walk(data_dir):
    for f in files:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, backend_dir)
        sz = os.path.getsize(fp)
        mtime = datetime.fromtimestamp(os.path.getmtime(fp)).astimezone()
        all_data_files.append((rel, sz, mtime))

all_data_files.sort(key=lambda x: x[2], reverse=True)
print(f"Total files in backend/data: {len(all_data_files)}")
print("--- Top 40 Files by Mtime Descending ---")
for rel, sz, mtime in all_data_files[:40]:
    print(f"  {rel:45s} | Size={sz:8d} B | Mtime={mtime.isoformat()}")

print("\n--- Explicit Check for 4 Core Tracking Files ---")
core_files = ["data/kis_token_cache.json", "data/telegram_offset.txt", "data/performance_log.json", "data/scheduler_log.json"]
for cf in core_files:
    full_p = os.path.join(backend_dir, cf)
    if os.path.exists(full_p):
        sz = os.path.getsize(full_p)
        mtime = datetime.fromtimestamp(os.path.getmtime(full_p)).astimezone().isoformat()
        print(f"  {cf:35s} | Size={sz:8d} B | Mtime={mtime}")
    else:
        print(f"  {cf:35s} | NOT_FOUND")


print("\n=================================================================")
print("=== a-6 (D-118): data/performance_log.json GIT DIFF & MTIME ===")
print("=================================================================")
perf_path = os.path.join(backend_dir, "data", "performance_log.json")
p_diff_perf = subprocess.run(["git", "-C", backend_dir, "diff", "--", "data/performance_log.json"], capture_output=True, text=True)
print("--- git diff -- data/performance_log.json ---")
print(p_diff_perf.stdout)
print("Exit code:", p_diff_perf.returncode)
if os.path.exists(perf_path):
    print("File Mtime:", datetime.fromtimestamp(os.path.getmtime(perf_path)).astimezone().isoformat())


print("\n=================================================================")
print("=== a-7 (D-121): .gitignore BOM & .env CHECK-IGNORE AUDIT ===")
print("=================================================================")
p_ci_env = subprocess.run(["git", "-C", backend_dir, "check-ignore", "-v", ".env"], capture_output=True, text=True)
print("git check-ignore -v .env ->", repr(p_ci_env.stdout.strip()), "Exit code:", p_ci_env.returncode)

p_ls_env = subprocess.run(["git", "-C", backend_dir, "ls-files", "--error-unmatch", ".env"], capture_output=True, text=True)
print("git ls-files --error-unmatch .env ->", repr(p_ls_env.stdout.strip()), "Exit code:", p_ls_env.returncode)

gi_p = os.path.join(backend_dir, ".gitignore")
with open(gi_p, "rb") as fp:
    head_bytes = fp.read(16)
print(".gitignore First 16 bytes hexdump:", head_bytes.hex(" "))

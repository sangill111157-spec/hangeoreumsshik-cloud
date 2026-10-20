import sys
import os
import subprocess
import json
import hashlib
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
backend_dir = r"C:\trading\package\nvda_trading_system\backend"
temp_dir = os.environ.get("TEMP", r"C:\Users\sangi\AppData\Local\Temp")

print("=================================================================")
print("=== a-1 [최우선-1]: scheduler_output.log FORENSICS ===")
print("=================================================================")
log_path = os.path.join(backend_dir, "data", "scheduler_output.log")
if os.path.exists(log_path):
    with open(log_path, "rb") as fp:
        raw_bytes = fp.read()
    log_sz = len(raw_bytes)
    log_mtime = datetime.fromtimestamp(os.path.getmtime(log_path)).astimezone().isoformat()
    log_sha = hashlib.sha256(raw_bytes).hexdigest().upper()
    print(f"Path: {log_path}")
    print(f"Size: {log_sz} bytes")
    print(f"Mtime: {log_mtime}")
    print(f"SHA256: {log_sha}")
    
    log_text = raw_bytes.decode("utf-8", errors="replace")
    log_lines = log_text.splitlines()
    print(f"Total lines: {len(log_lines)}")
    
    print("\n--- 1) Head 40 lines ---")
    for lno, l in enumerate(log_lines[:40], 1):
        print(f"  L{lno:05d}: {l}")
        
    print("\n--- 2) Tail 200 lines (sample first 20 & last 20) ---")
    tail_200 = log_lines[-200:]
    for lno, l in enumerate(tail_200[-40:], len(log_lines)-39):
        print(f"  L{lno:05d}: {l}")
        
    print("\n--- 3) Matching lines around 2026-08-25 06:2, 06:3, 07:0 and 2026-08-24 09:0 ---")
    target_stamps = ["2026-08-25 06:2", "2026-08-25 06:3", "2026-08-25 07:0", "2026-08-24 09:0", "08-25 06:2", "08-25 06:3", "08-25 07:0", "08-24 09:0"]
    for lno, l in enumerate(log_lines, 1):
        if any(ts in l for ts in target_stamps):
            print(f"  L{lno:05d}: {l}")
            
    print("\n--- 4) Keyword Grep Analysis (Counts & Samples) ---")
    keywords = ["order", "주문", "order-cash", "execute_trade", "DRY_RUN", "Traceback", "ERROR", "Exception", "token", "run_daily_simulation"]
    for kw in keywords:
        matches = [(lno, l) for lno, l in enumerate(log_lines, 1) if kw.lower() in l.lower()]
        print(f"Keyword '{kw}': Count = {len(matches)}")
        for lno, l in matches[:5]:
            print(f"    L{lno:05d}: {l}")
            
    print("\n--- 5) Repeating Cycle Pattern Sample ---")
    for lno in range(len(log_lines)-10, len(log_lines)):
        print(f"  L{lno+1:05d}: {log_lines[lno]}")
else:
    print("scheduler_output.log not found")


print("\n=================================================================")
print("=== a-2 [최우선-2]: kis_broker.py FULL CLASSIFICATION & ALIGNMENT ===")
print("=================================================================")
kb_path = os.path.join(backend_dir, "app", "services", "kis_broker.py")
with open(kb_path, "r", encoding="utf-8", errors="ignore") as fp:
    kb_lines = fp.readlines()

coords = [231, 310, 710, 799, 977, 1098, 1216, 1282]
for c in coords:
    s_idx = max(0, c - 15)
    e_idx = min(len(kb_lines), c + 15)
    print(f"\n--- [Coordinate Line {c}] (Lines {s_idx+1} to {e_idx}) ---")
    for j in range(s_idx, e_idx):
        print(f"  L{j+1:04d}: {kb_lines[j]}", end="")


print("\n=================================================================")
print("=== a-3 (D-129): COMMIT TIMING vs PID 23940 STARTTIME ===")
print("=================================================================")
p_cinfo = subprocess.run(["git", "-C", backend_dir, "log", "-1", "--format=%H %cI %s", "6397e94"], capture_output=True, text=True)
print("git log -1 --format='%H %cI %s' 6397e94:")
print(" ", p_cinfo.stdout.strip())

p_blame_assert = subprocess.run(["git", "-C", backend_dir, "blame", "-L", "131,148", "--", "app/services/kis_broker.py"], capture_output=True, text=True)
print("\ngit blame on _assert_order_allowed definition (lines 131-148):")
print(p_blame_assert.stdout)

# Check blame on calls
for cl in [618, 667, 762, 1055, 1140, 1166, 1194]:
    p_bl = subprocess.run(["git", "-C", backend_dir, "blame", "-L", f"{cl},{cl}", "--", "app/services/kis_broker.py"], capture_output=True, text=True)
    print(f"Line {cl} blame: {p_bl.stdout.strip()}")


print("\n=================================================================")
print("=== a-4 (D-133, D-135): WMI THREAD METRICS & POLLING LOOP AUDIT ===")
print("=================================================================")
with open(r"c:\Users\sangi\Downloads\shin-agent\a4_a5_snapshot_output.json", "r", encoding="utf-8") as fp:
    snap_data = json.load(fp)

s1 = snap_data["s1"]
s2 = snap_data["s2"]
dt = snap_data["real_elapsed"]
print(f"Real Elapsed Time: {dt:.3f} seconds")
print(f"Process S1 TotalProcessorTime: {s1['Process']['TotalProcessorTime']}s")
print(f"Process S2 TotalProcessorTime: {s2['Process']['TotalProcessorTime']}s")
proc_delta = s2['Process']['TotalProcessorTime'] - s1['Process']['TotalProcessorTime']
print(f"Process Total CPU Delta: {proc_delta:.4f}s ({proc_delta/dt*100:.2f}%)")

print("\n--- WMI Raw Threads Snapshot 1 vs Snapshot 2 ---")
t1_map = {t["IDThread"]: t for t in s1.get("Threads", []) if isinstance(t, dict)}
thread_deltas = []
for t2 in s2.get("Threads", []):
    if isinstance(t2, dict):
        tid = t2["IDThread"]
        t1 = t1_map.get(tid, {})
        raw_cpu1 = int(t1.get("PercentProcessorTime", 0) or 0)
        raw_cpu2 = int(t2.get("PercentProcessorTime", 0) or 0)
        raw_user1 = int(t1.get("PercentUserTime", 0) or 0)
        raw_user2 = int(t2.get("PercentUserTime", 0) or 0)
        raw_priv1 = int(t1.get("PercentPrivilegedTime", 0) or 0)
        raw_priv2 = int(t2.get("PercentPrivilegedTime", 0) or 0)
        ts1 = int(t1.get("Timestamp_Sys100NS", 0) or 0)
        ts2 = int(t2.get("Timestamp_Sys100NS", 0) or 0)
        
        d_raw_cpu = raw_cpu2 - raw_cpu1
        d_ts = ts2 - ts1
        cpu_sec = d_raw_cpu / 10000000.0 if d_raw_cpu >= 0 else 0
        thread_deltas.append({
            "IDThread": tid,
            "Raw1": raw_cpu1,
            "Raw2": raw_cpu2,
            "DeltaRaw": d_raw_cpu,
            "CpuSec": cpu_sec,
            "ThreadState": t2.get("ThreadState"),
            "WaitReason": t2.get("ThreadWaitReason")
        })

thread_deltas.sort(key=lambda x: x["DeltaRaw"], reverse=True)
for td in thread_deltas:
    print(f"  Thread ID {td['IDThread']:6d}: DeltaRaw={td['DeltaRaw']:12d} (~{td['CpuSec']:.4f}s), State={td['ThreadState']}, WaitReason={td['WaitReason']}")

# Telegram listener loop ±20 lines
tgl_path = os.path.join(backend_dir, "telegram_command_listener.py")
print("\n--- telegram_command_listener.py Polling Loop (lines 110-150) ---")
with open(tgl_path, "r", encoding="utf-8", errors="ignore") as fp:
    tgl_lines = fp.readlines()
for j in range(105, min(155, len(tgl_lines))):
    print(f"  L{j+1:03d}: {tgl_lines[j]}", end="")


print("\n=================================================================")
print("=== a-5 (D-134): SYSTEM MEMORY & COMMIT LIMIT EXHAUSTION ===")
print("=================================================================")
sm = s2["SystemMemory"]
tot_vis_mb = sm["TotalVisibleMemorySizeKB"] / 1024.0
free_phys_mb = sm["FreePhysicalMemoryKB"] / 1024.0
tot_virt_mb = sm["TotalVirtualMemorySizeKB"] / 1024.0
free_virt_mb = sm["FreeVirtualMemoryKB"] / 1024.0
page_sz_mb = sm["SizeStoredInPagingFilesKB"] / 1024.0
free_page_mb = sm["FreeSpaceInPagingFilesKB"] / 1024.0

print(f"Physical RAM Total: {tot_vis_mb:.2f} MB, Free: {free_phys_mb:.2f} MB")
print(f"Virtual (Commit Limit) Total: {tot_virt_mb:.2f} MB, Free (Available Commit): {free_virt_mb:.2f} MB")
print(f"Paging File Total: {page_sz_mb:.2f} MB, Free: {free_page_mb:.2f} MB")
print(f"Process WorkingSet: {s2['Process']['WorkingSet64']/(1024*1024):.2f} MB")
print(f"Process PrivateMemory (Commit): {s2['Process']['PrivateMemorySize64']/(1024*1024):.2f} MB")

# Projections to exhaust free commit
avail_commit_mb = free_virt_mb
hours_at_430 = avail_commit_mb / 430.0
hours_at_715 = avail_commit_mb / 715.0
print(f"\n--- Exhaustion Projection for Available Commit ({avail_commit_mb:.2f} MB) ---")
print(f"Scenario 1 (430 MB/h): {hours_at_430:.2f} hours (~{hours_at_430/24:.2f} days)")
print(f"Scenario 2 (715 MB/h): {hours_at_715:.2f} hours (~{hours_at_715/24:.2f} days)")


print("\n=================================================================")
print("=== a-6 (D-131): TOKEN CACHING CODE PATHS AUDIT ===")
print("=================================================================")
print("--- Grep for kis_token_cache, token_cache, access_token file writes ---")
for root, dirs, files in os.walk(backend_dir):
    dirs[:] = [d for d in dirs if d not in ["__pycache__", "venv", ".git", "node_modules"]]
    for f in files:
        if f.endswith(".py"):
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, backend_dir)
            with open(fp, "r", encoding="utf-8", errors="ignore") as file_p:
                for lno, line in enumerate(file_p, 1):
                    if any(k in line for k in ["token_cache", "kis_token", "access_token"]) and any(w in line for w in ["open(", "dump(", "write(", "save"]):
                        print(f"  {rel}:{lno}: {line.strip()}")


print("\n=================================================================")
print("=== a-7 (D-138): data/performance_log.json GIT DIFF REDIRECT ===")
print("=================================================================")
diff_perf_file = os.path.join(temp_dir, "phase1623_perf_diff.txt")
p_dp = subprocess.run(["git", "-C", backend_dir, "diff", "--", "data/performance_log.json"], capture_output=True, text=True)
with open(diff_perf_file, "w", encoding="utf-8") as fp:
    fp.write(p_dp.stdout)

dp_sz = os.path.getsize(diff_perf_file)
dp_mtime = datetime.fromtimestamp(os.path.getmtime(diff_perf_file)).astimezone().isoformat()
with open(diff_perf_file, "rb") as fp:
    dp_sha = hashlib.sha256(fp.read()).hexdigest().upper()

print(f"Redirect File: {diff_perf_file}")
print(f"Size: {dp_sz} bytes, Mtime: {dp_mtime}, SHA256: {dp_sha}, ExitCode: {p_dp.returncode}")

perf_raw_path = os.path.join(backend_dir, "data", "performance_log.json")
with open(perf_raw_path, "rb") as fp:
    cur_perf_sha = hashlib.sha256(fp.read()).hexdigest().upper()
print(f"Current data/performance_log.json SHA256: {cur_perf_sha}")


print("\n=================================================================")
print("=== a-8 (D-137, D-139): PACKAGE VERSIONS ===")
print("=================================================================")
p_pip = subprocess.run([os.path.join(backend_dir, "venv", "Scripts", "pip.exe"), "show", "fastapi", "starlette", "httpx", "anyio"], capture_output=True, text=True)
print(p_pip.stdout)

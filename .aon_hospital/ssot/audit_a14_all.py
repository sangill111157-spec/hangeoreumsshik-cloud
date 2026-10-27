import sys
import os
import subprocess
import json
import hashlib
import shutil
import re
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
backend_dir = r"C:\trading\package\nvda_trading_system\backend"
temp_dir = os.environ.get("TEMP", r"C:\Users\sangi\AppData\Local\Temp")

print("=================================================================")
print("=== PART B-13: BACKUP TO %TEMP% (3 FILES) ===")
print("=================================================================")
backup_files = [
    ("app/services/kis_broker.py", os.path.join(backend_dir, "app", "services", "kis_broker.py")),
    ("app/services/auto_trader.py", os.path.join(backend_dir, "app", "services", "auto_trader.py")),
    ("tests/test_order_auth.py", os.path.join(backend_dir, "tests", "test_order_auth.py")),
]

for rel_p, src_p in backup_files:
    dest_name = "backup_phase1624_" + rel_p.replace("/", "_").replace("\\", "_")
    dest_p = os.path.join(temp_dir, dest_name)
    shutil.copy2(src_p, dest_p)
    
    with open(src_p, "rb") as fp:
        src_raw = fp.read()
    src_sha = hashlib.sha256(src_raw).hexdigest().upper()
    src_sz = len(src_raw)
    src_mtime = datetime.fromtimestamp(os.path.getmtime(src_p)).astimezone().isoformat()
    
    with open(dest_p, "rb") as fp:
        dst_raw = fp.read()
    dst_sha = hashlib.sha256(dst_raw).hexdigest().upper()
    dst_sz = len(dst_raw)
    dst_mtime = datetime.fromtimestamp(os.path.getmtime(dest_p)).astimezone().isoformat()
    
    print(f"File: {rel_p}")
    print(f"  Source: {src_p} | Size={src_sz} B | Mtime={src_mtime} | SHA256={src_sha}")
    print(f"  Backup: {dest_p} | Size={dst_sz} B | Mtime={dst_mtime} | SHA256={dst_sha}")
    print(f"  Match: {src_sha == dst_sha}")


print("\n=================================================================")
print("=== a-1 [최우선-1]: scheduler_output.log ATOMIC FORENSICS ===")
print("=================================================================")
log_path = os.path.join(backend_dir, "data", "scheduler_output.log")
with open(log_path, "rb") as fp:
    raw_bytes = fp.read()
log_sz = len(raw_bytes)
log_mtime = datetime.fromtimestamp(os.path.getmtime(log_path)).astimezone().isoformat()
log_sha = hashlib.sha256(raw_bytes).hexdigest().upper()
log_text = raw_bytes.decode("utf-8", errors="replace")
log_lines = log_text.splitlines()
total_lines = len(log_lines)

print(f"Atomic Log File: {log_path}")
print(f"Size: {log_sz} bytes")
print(f"Mtime: {log_mtime}")
print(f"SHA256: {log_sha}")
print(f"Total Lines: {total_lines}")

print("\n--- 1) Non-skip Lines (Full dump with line numbers) ---")
non_skip = []
for idx, line in enumerate(log_lines, 1):
    if "skipped: maximum number of running instances reached" not in line:
        non_skip.append((idx, line))

print(f"Total non-skip lines: {len(non_skip)} / {total_lines}")
for lno, line in non_skip:
    print(f"  L{lno:05d}: {line}")

print("\n--- 2) Lines 14580 to 14610 Continuous Text (Including L14590) ---")
for lno in range(14580, min(14611, total_lines + 1)):
    print(f"  L{lno:05d}: {log_lines[lno-1]}")

print("\n--- 3) Specific Window Dumps ---")
def dump_window(label, pattern):
    print(f"=== Window: {label} (pattern: {pattern}) ===")
    matches = [(idx, line) for idx, line in enumerate(log_lines, 1) if pattern in line]
    print(f"Match count: {len(matches)}")
    for lno, line in matches:
        print(f"  L{lno:05d}: {line}")

dump_window("2026-08-24 08:55~09:10", "2026-08-24 09:")
dump_window("2026-08-24 08:5x", "2026-08-24 08:5")
dump_window("2026-08-25 06:25~06:40", "2026-08-25 06:3")
dump_window("2026-08-25 06:2x", "2026-08-25 06:2")
dump_window("2026-08-25 07:00~07:10", "2026-08-25 07:0")

print("\n--- 4) Grep Re-execution with Positive Control ---")
grep_keywords = [
    ("UnicodeEncodeError", "UnicodeEncodeError (Positive Control)"),
    ("order", "order (Case-insensitive)"),
    ("주문", "주문"),
    ("order-cash", "order-cash"),
    ("execute_trade", "execute_trade"),
    ("DRY_RUN", "DRY_RUN"),
    ("Traceback", "Traceback"),
    ("error", "error (Case-insensitive)"),
    ("Exception", "Exception (Case-insensitive)"),
    ("token", "token (Case-insensitive)"),
    ("simulation", "simulation (Case-insensitive)"),
    ('Job "', 'Job " (Job name marker)')
]

for kw, desc in grep_keywords:
    # Exact case-insensitive grep across full text
    matches = [(idx, line) for idx, line in enumerate(log_lines, 1) if kw.lower() in line.lower()]
    print(f"Grep [{desc}]: Count = {len(matches)}")
    for lno, line in matches[:10]:
        print(f"    L{lno:05d}: {line}")

print("\n--- 5) Continuous Gap in 'next run at' >= 60 seconds (Top 20) ---")
# Parse timestamps from skip lines: next run at: YYYY-MM-DD HH:MM:SS KST
gap_pattern = re.compile(r"next run at: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) KST")
ts_list = []
for idx, line in enumerate(log_lines, 1):
    m = gap_pattern.search(line)
    if m:
        dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
        ts_list.append((idx, dt))

gaps = []
for i in range(len(ts_list) - 1):
    lno1, dt1 = ts_list[i]
    lno2, dt2 = ts_list[i+1]
    diff_sec = (dt2 - dt1).total_seconds()
    if diff_sec >= 60.0:
        gaps.append((dt1, dt2, diff_sec, lno1, lno2))

gaps.sort(key=lambda x: x[2], reverse=True)
print(f"Total gaps >= 60s found: {len(gaps)}")
print("Top 20 Gaps:")
for idx, (dt1, dt2, diff_s, l1, l2) in enumerate(gaps[:20], 1):
    print(f"  #{idx:02d}: {dt1.strftime('%Y-%m-%d %H:%M:%S')} -> {dt2.strftime('%Y-%m-%d %H:%M:%S')} | Gap = {diff_s:8.1f}s ({diff_s/60:5.1f}m) | Lines {l1} -> {l2}")


print("\n=================================================================")
print("=== a-2 [최우선-2]: 06:30 PATHWAY CODE INVENTORY ===")
print("=================================================================")
sch_p = os.path.join(backend_dir, "app", "services", "scheduler.py")
with open(sch_p, "r", encoding="utf-8", errors="ignore") as fp:
    sch_lines = fp.readlines()

print("--- scheduler.py job_us_market_close (Lines 80-160) ---")
for idx, l in enumerate(sch_lines, 1):
    if 85 <= idx <= 150:
        print(f"  L{idx:03d}: {l}", end="")

sim_p = os.path.join(backend_dir, "run_daily_simulation.py")
with open(sim_p, "r", encoding="utf-8", errors="ignore") as fp:
    sim_lines = fp.readlines()

print("\n--- run_daily_simulation.py __main__ and execution block (Lines 190-250) ---")
for idx, l in enumerate(sim_lines, 1):
    if 190 <= idx <= 250:
        print(f"  L{idx:03d}: {l}", end="")


print("\n=================================================================")
print("=== a-3: REPOSITORY STATUS & GATES RAW AUDIT ===")
print("=================================================================")
p_st = subprocess.run(["git", "-C", backend_dir, "status", "--porcelain"], capture_output=True, text=True)
print("--- git status --porcelain ---")
print(p_st.stdout)
print("Exit code:", p_st.returncode)

p_stash = subprocess.run(["git", "-C", backend_dir, "stash", "list"], capture_output=True, text=True)
print("--- git stash list ---")
print(p_stash.stdout)
print("Exit code:", p_stash.returncode)

p_stat = subprocess.run(["git", "-C", backend_dir, "diff", "--stat"], capture_output=True, text=True)
print("--- git diff --stat ---")
print(p_stat.stdout)
print("Exit code:", p_stat.returncode)

kb_path = os.path.join(backend_dir, "app", "services", "kis_broker.py")
with open(kb_path, "r", encoding="utf-8", errors="ignore") as fp:
    kb_lines = fp.readlines()

print("\n--- Gate 7 lines +-3 lines raw text ---")
gate_lines = [618, 667, 762, 1055, 1140, 1166, 1194]
for gl in gate_lines:
    print(f"\n--- Gate Line {gl} (Lines {gl-3} to {gl+3}) ---")
    for j in range(gl-4, gl+3):
        if 0 <= j < len(kb_lines):
            print(f"  L{j+1:04d}: {kb_lines[j]}", end="")

print("\n--- 8 Coordinates +-15 lines raw text ---")
coords = [231, 310, 710, 799, 977, 1098, 1216, 1282]
for c in coords:
    print(f"\n=================================================================")
    print(f"=== Coordinate Line {c} (Lines {c-15} to {c+15}) ===")
    print(f"=================================================================")
    for j in range(c-16, c+15):
        if 0 <= j < len(kb_lines):
            print(f"  L{j+1:04d}: {kb_lines[j]}", end="")


print("\n=================================================================")
print("=== a-4 / a-5: METRICS FROM CLEAN ISOLATED SAMPLER ===")
print("=================================================================")
with open(r"c:\Users\sangi\Downloads\shin-agent\clean_isolated_metrics.json", "r", encoding="utf-8") as fp:
    m_clean = json.load(fp)

s1 = m_clean["s1"]
s2 = m_clean["s2"]
dt = m_clean["real_elapsed_seconds"]

p1 = s1["Process"]
p2 = s2["Process"]

print(f"Pure Isolated Elapsed Time: {dt:.3f} seconds")
print(f"S1 Timestamp: {s1['Timestamp']}")
print(f"S2 Timestamp: {s2['Timestamp']}")
print(f"Process StartTime (Authoritative): {p1['StartTime']}")

print(f"S1 TotalProcessorTime: {p1['TotalProcessorTime']:.4f}s")
print(f"S2 TotalProcessorTime: {p2['TotalProcessorTime']:.4f}s")
d_cpu = p2['TotalProcessorTime'] - p1['TotalProcessorTime']
d_user = p2['UserProcessorTime'] - p1['UserProcessorTime']
d_priv = p2['PrivilegedProcessorTime'] - p1['PrivilegedProcessorTime']
print(f"Delta TotalProcessorTime: {d_cpu:.4f}s ({d_cpu/dt*100:.2f}%)")
print(f"Delta UserProcessorTime: {d_user:.4f}s ({d_user/dt*100:.2f}%)")
print(f"Delta PrivilegedProcessorTime: {d_priv:.4f}s ({d_priv/dt*100:.2f}%)")

print(f"S1 WorkingSet64: {p1['WorkingSet64']/(1024*1024):.2f} MB")
print(f"S2 WorkingSet64: {p2['WorkingSet64']/(1024*1024):.2f} MB")
print(f"S1 PrivateMemorySize64: {p1['PrivateMemorySize64']/(1024*1024):.2f} MB")
print(f"S2 PrivateMemorySize64: {p2['PrivateMemorySize64']/(1024*1024):.2f} MB")
d_priv_mb = (p2['PrivateMemorySize64'] - p1['PrivateMemorySize64']) / (1024*1024)
print(f"Delta PrivateMemorySize64: {d_priv_mb:.2f} MB ({d_priv_mb / (dt/60):.2f} MB/min = {d_priv_mb / (dt/3600):.2f} MB/h)")

print("\n--- System Memory 3 Samples ---")
for idx, mem in enumerate([m_clean["mem1"], m_clean["mem2"], m_clean["mem3"]], 1):
    tot_vis_mb = mem["TotalVisibleMemorySizeKB"] / 1024.0
    free_phys_mb = mem["FreePhysicalMemoryKB"] / 1024.0
    tot_virt_mb = mem["TotalVirtualMemorySizeKB"] / 1024.0
    free_virt_mb = mem["FreeVirtualMemoryKB"] / 1024.0
    page_sz_mb = mem["SizeStoredInPagingFilesKB"] / 1024.0
    free_page_mb = mem["FreeSpaceInPagingFilesKB"] / 1024.0
    print(f"Sample {idx} ({mem['Timestamp']}):")
    print(f"  Physical RAM: Total={tot_vis_mb:.2f} MB, Free={free_phys_mb:.2f} MB ({free_phys_mb/tot_vis_mb*100:.2f}%)")
    print(f"  Virtual (Commit): Total={tot_virt_mb:.2f} MB, Free={free_virt_mb:.2f} MB")
    print(f"  Paging File: Total={page_sz_mb:.2f} MB, Free={free_page_mb:.2f} MB")


print("\n=================================================================")
print("=== a-6: telegram_command_listener.py poll_telegram_once ===")
print("=================================================================")
tg_p = os.path.join(backend_dir, "telegram_command_listener.py")
with open(tg_p, "r", encoding="utf-8", errors="ignore") as fp:
    tg_lines = fp.readlines()

print("--- poll_telegram_once full function (lines 124-155) ---")
for idx, l in enumerate(tg_lines, 1):
    if 120 <= idx <= 155:
        print(f"  L{idx:03d}: {l}", end="")


print("\n=================================================================")
print("=== a-7: STRICT TESTS, PERF DIFF HEAD/TAIL, TOKEN GREP ===")
print("=================================================================")
test_p = os.path.join(temp_dir, "phase1622_tests.txt")
if os.path.exists(test_p):
    with open(test_p, "r", encoding="utf-8", errors="ignore") as fp:
        t_lines = fp.readlines()
    print(f"phase1622_tests.txt Total lines: {len(t_lines)}")
    print("--- Head 40 lines ---")
    for l in t_lines[:40]:
        print(l, end="")
    print("\n--- Tail 40 lines ---")
    for l in t_lines[-40:]:
        print(l, end="")

perf_diff_p = os.path.join(temp_dir, "phase1623_perf_diff.txt")
if os.path.exists(perf_diff_p):
    with open(perf_diff_p, "r", encoding="utf-8", errors="ignore") as fp:
        pd_lines = fp.readlines()
    print(f"\nphase1623_perf_diff.txt Total lines: {len(pd_lines)}")
    print("--- Head 40 lines ---")
    for l in pd_lines[:40]:
        print(l, end="")
    print("\n--- Tail 40 lines ---")
    for l in pd_lines[-40:]:
        print(l, end="")

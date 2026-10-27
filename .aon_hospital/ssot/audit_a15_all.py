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
perm_backup_dir = r"C:\trading\_evidence_backup_20260826"

print("=================================================================")
print("=== PART B-14: PERSISTENT BACKUP TO C:\\trading\\_evidence_backup_20260826 ===")
print("=================================================================")
os.makedirs(perm_backup_dir, exist_ok=True)

perm_backup_targets = [
    "app/core/order_auth.py",
    "app/core/order_gate.py",
    "app/main.py",
    "app/api/routes/kis.py",
    "app/api/routes/nvda.py",
    "app/api/routes/rebalance.py",
    "app/api/routes/stock.py",
    "app/api/routes/trader.py",
    "app/services/kis_broker.py",
    "app/services/auto_trader.py",
    "app/services/scheduler.py",
    "tests/test_order_auth.py",
    "tests/test_order_gate.py",
    "tests/test_kis_chokepoint.py",
    ".gitignore"
]

print(f"{'Relative Path':32s} | {'Size':8s} | {'Source SHA256':16s} | {'Backup SHA256':16s} | {'Match'}")
print("-" * 90)
for rel_p in perm_backup_targets:
    src_p = os.path.join(backend_dir, rel_p.replace("/", os.sep))
    dest_name = rel_p.replace("/", "_").replace("\\", "_")
    dst_p = os.path.join(perm_backup_dir, dest_name)
    
    if os.path.exists(src_p):
        shutil.copy2(src_p, dst_p)
        with open(src_p, "rb") as fp:
            s_raw = fp.read()
        s_sha = hashlib.sha256(s_raw).hexdigest().upper()
        s_sz = len(s_raw)
        s_mtime = datetime.fromtimestamp(os.path.getmtime(src_p)).astimezone().isoformat()
        
        with open(dst_p, "rb") as fp:
            d_raw = fp.read()
        d_sha = hashlib.sha256(d_raw).hexdigest().upper()
        d_sz = len(d_raw)
        
        match = (s_sha == d_sha)
        print(f"{rel_p:32s} | {s_sz:6d} B | {s_sha[:16]}... | {d_sha[:16]}... | {match}")
    else:
        print(f"{rel_p:32s} | NOT_FOUND")


print("\n=================================================================")
print("=== a-1 [최우선-1]: LOG AUDIT, 987 NON-SKIP LINES & MISSING 252 LINES ===")
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

print(f"Log Path: {log_path}")
print(f"Size: {log_sz} bytes | Total Lines: {total_lines} | SHA256: {log_sha}")

non_skip_lines = []
for idx, line in enumerate(log_lines, 1):
    if "skipped: maximum number of running instances reached" not in line:
        non_skip_lines.append((idx, line))

print(f"\n1) Total non-skip lines: {len(non_skip_lines)}")
# Dump all 987 lines to a dedicated temp file to preserve 100% full content
non_skip_dump_path = os.path.join(temp_dir, "phase1625_non_skip_987.txt")
with open(non_skip_dump_path, "w", encoding="utf-8") as fp:
    for lno, line in non_skip_lines:
        fp.write(f"L{lno:05d}: {line}\n")
print(f"Full 987 non-skip lines written to {non_skip_dump_path} (Size: {os.path.getsize(non_skip_dump_path)} B)")

# 2) 252 lines containing 'Job "' that are non-skip
job_non_skip = []
for lno, line in non_skip_lines:
    if 'job "' in line.lower():
        job_non_skip.append((lno, line))

print(f"\n2) Total non-skip lines containing 'job \"': {len(job_non_skip)}")
missed_jobs = []
for lno, line in job_non_skip:
    # check category
    if "was missed" in line:
        m_type = "MISSED"
    elif "executed" in line:
        m_type = "EXECUTED"
    else:
        m_type = "OTHER"
    missed_jobs.append((lno, m_type, line))

print(f"Sample of non-skip job lines (Total {len(missed_jobs)}):")
for lno, m_type, line in missed_jobs[:20]:
    print(f"  L{lno:05d} [{m_type}]: {line}")

# 3) Logging configuration in run_scheduler.py and scheduler.py
print("\n3) Logging configuration code:")
rs_path = os.path.join(backend_dir, "run_scheduler.py")
with open(rs_path, "r", encoding="utf-8", errors="ignore") as fp:
    rs_lines = fp.readlines()
print("--- run_scheduler.py Logging Setup (Lines 1-45) ---")
for idx, l in enumerate(rs_lines[:45], 1):
    print(f"  L{idx:03d}: {l}", end="")

sch_path = os.path.join(backend_dir, "app", "services", "scheduler.py")
with open(sch_path, "r", encoding="utf-8", errors="ignore") as fp:
    sch_lines = fp.readlines()
print("\n--- scheduler.py Logging Setup (Lines 1-35) ---")
for idx, l in enumerate(sch_lines[:35], 1):
    print(f"  L{idx:03d}: {l}", end="")

# 4) Grep re-execution with positive controls
print("\n4) Grep Re-execution with Positive Controls:")
grep_kw_list = [
    ("UnicodeEncodeError", "UnicodeEncodeError (Positive Control 1)"),
    ("[tg poll 오류]", "[tg poll 오류] (Positive Control 2)"),
    ("마감 분석", "마감 분석"),
    ("분석 시작", "분석 시작"),
    ("분석 완료", "분석 완료"),
    ("===", "==="),
    ("Run time of job", "Run time of job"),
    ("was missed", "was missed"),
    ("자동매매", "자동매매"),
    ("비활성화", "비활성화"),
    ("simulation", "simulation"),
    ("주간 성과", "주간 성과")
]

for kw, desc in grep_kw_list:
    matches = [(idx, line) for idx, line in enumerate(log_lines, 1) if kw.lower() in line.lower()]
    print(f"Grep [{desc}]: Count = {len(matches)}")
    for lno, line in matches[:5]:
        print(f"    L{lno:05d}: {line}")

# 5) Line index based window dumps around 08-24 09:00 and 08-25 06:30
print("\n5) Line Index-Based Window Dumps (Anchor +-40 lines):")
def dump_anchor_window(target_str, label):
    anchor_lno = None
    for idx, line in enumerate(log_lines, 1):
        if target_str in line:
            anchor_lno = idx
            break
    if anchor_lno:
        s_l = max(1, anchor_lno - 40)
        e_l = min(total_lines, anchor_lno + 40)
        print(f"--- {label} (Anchor Line L{anchor_lno:05d}, Range L{s_l:05d} to L{e_l:05d}) ---")
        for j in range(s_l - 1, e_l):
            print(f"  L{j+1:05d}: {log_lines[j]}")
    else:
        print(f"--- {label}: Target anchor '{target_str}' not found ---")

dump_anchor_window("2026-08-24 09:", "2026-08-24 09:00 Anchor Window")
dump_anchor_window("2026-08-25 06:32:35", "2026-08-25 06:30 Anchor Window")

# 6) Gap analysis >= 60s
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
print(f"\n6) Gaps >= 60s (Top 20 of {len(gaps)} total):")
for idx, (dt1, dt2, diff_s, l1, l2) in enumerate(gaps[:20], 1):
    print(f"  #{idx:02d}: {dt1.strftime('%Y-%m-%d %H:%M:%S')} -> {dt2.strftime('%Y-%m-%d %H:%M:%S')} | Gap = {diff_s:8.1f}s ({diff_s/60:5.1f}m) | Lines {l1} -> {l2}")


print("\n=================================================================")
print("=== a-2 [최우선-2]: 06:30 PATHWAY CODE & AUTO_TRADE_ENABLED ===")
print("=================================================================")
sim_path = os.path.join(backend_dir, "run_daily_simulation.py")
with open(sim_path, "r", encoding="utf-8", errors="ignore") as fp:
    sim_lines = fp.readlines()

print("--- run_daily_simulation.py __main__ block (Lines 220-270) ---")
for idx, l in enumerate(sim_lines, 1):
    if 220 <= idx <= 270:
        print(f"  L{idx:03d}: {l}", end="")

cfg_path = os.path.join(backend_dir, "app", "core", "config.py")
if os.path.exists(cfg_path):
    with open(cfg_path, "r", encoding="utf-8", errors="ignore") as fp:
        cfg_lines = fp.readlines()
    print("\n--- app/core/config.py Settings AUTO_TRADE_ENABLED definition ---")
    for idx, l in enumerate(cfg_lines, 1):
        if "auto_trade" in l.lower() or "settings" in l.lower() or "dry_run" in l.lower():
            print(f"  L{idx:03d}: {l}", end="")

# Check .env for AUTO_TRADE_ENABLED
dotenv_p = os.path.join(backend_dir, ".env")
if os.path.exists(dotenv_p):
    with open(dotenv_p, "r", encoding="utf-8", errors="ignore") as fp:
        env_raw = fp.read()
    m_ate = re.search(r"(?m)^AUTO_TRADE_ENABLED=(.*)$", env_raw)
    if m_ate:
        print(f"\n.env AUTO_TRADE_ENABLED Exists: True, Length: {len(m_ate.group(1).strip())}")
    else:
        print("\n.env AUTO_TRADE_ENABLED Exists: False (Not in .env)")

at_path = os.path.join(backend_dir, "app", "services", "auto_trader.py")
with open(at_path, "r", encoding="utf-8", errors="ignore") as fp:
    at_lines = fp.readlines()

print("\n--- auto_trader.py dry_run initialization (Lines 45-65) ---")
for idx, l in enumerate(at_lines, 1):
    if 45 <= idx <= 65:
        print(f"  L{idx:03d}: {l}", end="")

print("\n--- auto_trader.py _execute_kis_order B-8-1 guard (Lines 310-335) ---")
for idx, l in enumerate(at_lines, 1):
    if 310 <= idx <= 335:
        print(f"  L{idx:03d}: {l}", end="")


print("\n=================================================================")
print("=== a-3: REPOSITORY STATUS & GATES RAW AUDIT ===")
print("=================================================================")
p_stash = subprocess.run(["git", "-C", backend_dir, "stash", "list"], capture_output=True, text=True)
print("--- git stash list ---")
print(p_stash.stdout)
print("Exit code:", p_stash.returncode)

p_diff_stat = subprocess.run(["git", "-C", backend_dir, "diff", "--stat"], capture_output=True, text=True)
print("--- git diff --stat ---")
print(p_diff_stat.stdout)
print("Exit code:", p_diff_stat.returncode)

p_diff_numstat = subprocess.run(["git", "-C", backend_dir, "diff", "--numstat"], capture_output=True, text=True)
print("--- git diff --numstat ---")
print(p_diff_numstat.stdout)
print("Exit code:", p_diff_numstat.returncode)

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

print("\n--- 4 POST Coordinates +-15 lines raw text ---")
post_coords = [710, 799, 1098, 1216]
for c in post_coords:
    print(f"\n=================================================================")
    print(f"=== POST Coordinate Line {c} (Lines {c-15} to {c+15}) ===")
    print(f"=================================================================")
    for j in range(c-16, c+15):
        if 0 <= j < len(kb_lines):
            print(f"  L{j+1:04d}: {kb_lines[j]}", end="")

# app/core/order_gate.py & order_auth.py full code
og_p = os.path.join(backend_dir, "app", "core", "order_gate.py")
with open(og_p, "r", encoding="utf-8", errors="ignore") as fp:
    og_text = fp.readlines()
print(f"\n--- app/core/order_gate.py Full Text ({len(og_text)} lines) ---")
for idx, l in enumerate(og_text, 1):
    print(f"  L{idx:03d}: {l}", end="")

oa_p = os.path.join(backend_dir, "app", "core", "order_auth.py")
with open(oa_p, "r", encoding="utf-8", errors="ignore") as fp:
    oa_text = fp.readlines()
print(f"\n--- app/core/order_auth.py Full Text ({len(oa_text)} lines) ---")
for idx, l in enumerate(oa_text, 1):
    print(f"  L{idx:03d}: {l}", end="")


print("\n=================================================================")
print("=== a-4 / a-5: METRICS FROM CLEAN 1.6-25 ISOLATED SAMPLER ===")
print("=================================================================")
with open(r"c:\Users\sangi\Downloads\shin-agent\phase1625_isolated_metrics.json", "r", encoding="utf-8") as fp:
    m_clean = json.load(fp)

s1 = m_clean["s1"]
s2 = m_clean["s2"]
p1 = s1["Process"]
p2 = s2["Process"]

t1_str = s1["Timestamp"]
t2_str = s2["Timestamp"]
dt1 = datetime.fromisoformat(t1_str)
dt2 = datetime.fromisoformat(t2_str)
real_dt = (dt2 - dt1).total_seconds()

print(f"S1 Timestamp: {t1_str}")
print(f"S2 Timestamp: {t2_str}")
print(f"Real Elapsed: {real_dt:.3f} seconds")
print(f"Authoritative StartTime: {p1['StartTime']}")

print(f"\n--- S1 & S2 Cumulative Absolute Metrics (PID 23940) ---")
print(f"  TotalProcessorTime: S1={p1['TotalProcessorTime']:.4f}s | S2={p2['TotalProcessorTime']:.4f}s | Delta={p2['TotalProcessorTime']-p1['TotalProcessorTime']:.4f}s ({ (p2['TotalProcessorTime']-p1['TotalProcessorTime'])/real_dt*100:.2f}%)")
print(f"  UserProcessorTime:  S1={p1['UserProcessorTime']:.4f}s | S2={p2['UserProcessorTime']:.4f}s | Delta={p2['UserProcessorTime']-p1['UserProcessorTime']:.4f}s ({ (p2['UserProcessorTime']-p1['UserProcessorTime'])/real_dt*100:.2f}%)")
print(f"  PrivilegedProcTime: S1={p1['PrivilegedProcessorTime']:.4f}s | S2={p2['PrivilegedProcessorTime']:.4f}s | Delta={p2['PrivilegedProcessorTime']-p1['PrivilegedProcessorTime']:.4f}s ({ (p2['PrivilegedProcessorTime']-p1['PrivilegedProcessorTime'])/real_dt*100:.2f}%)")
print(f"  WorkingSet64:       S1={p1['WorkingSet64']/(1024*1024):.2f} MB | S2={p2['WorkingSet64']/(1024*1024):.2f} MB | Delta={(p2['WorkingSet64']-p1['WorkingSet64'])/(1024*1024):.2f} MB")
print(f"  PrivateMemorySize:  S1={p1['PrivateMemorySize64']/(1024*1024):.2f} MB | S2={p2['PrivateMemorySize64']/(1024*1024):.2f} MB | Delta={(p2['PrivateMemorySize64']-p1['PrivateMemorySize64'])/(1024*1024):.2f} MB")
print(f"  PagedMemorySize:    S1={p1['PagedMemorySize64']/(1024*1024):.2f} MB | S2={p2['PagedMemorySize64']/(1024*1024):.2f} MB | Delta={(p2['PagedMemorySize64']-p1['PagedMemorySize64'])/(1024*1024):.2f} MB")
print(f"  HandleCount:        S1={p1['HandleCount']} | S2={p2['HandleCount']} | Delta={p2['HandleCount']-p1['HandleCount']}")
print(f"  Threads.Count:      S1={p1['ThreadCount']} | S2={p2['ThreadCount']} | Delta={p2['ThreadCount']-p1['ThreadCount']}")

print("\n--- Win32_PerfRawData_PerfProc_Thread S1 Table ---")
for t in s1.get("Threads", []):
    if isinstance(t, dict):
        print(f"  IDThread={t.get('IDThread'):6d} | RawCPU={t.get('PercentProcessorTime')} | RawUser={t.get('PercentUserTime')} | RawPriv={t.get('PercentPrivilegedTime')} | State={t.get('ThreadState')} | WR={t.get('ThreadWaitReason')} | TS={t.get('Timestamp_Sys100NS')}")

print("\n--- Win32_PerfRawData_PerfProc_Thread S2 Table ---")
for t in s2.get("Threads", []):
    if isinstance(t, dict):
        print(f"  IDThread={t.get('IDThread'):6d} | RawCPU={t.get('PercentProcessorTime')} | RawUser={t.get('PercentUserTime')} | RawPriv={t.get('PercentPrivilegedTime')} | State={t.get('ThreadState')} | WR={t.get('ThreadWaitReason')} | TS={t.get('Timestamp_Sys100NS')}")

print("\n--- System Memory 5 Samples ---")
for idx, mem in enumerate(m_clean["mem_samples"], 1):
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
print("=== a-6: TELEGRAM CHANNEL INVESTIGATION ===")
print("=================================================================")
tg_off_p = os.path.join(backend_dir, "data", "telegram_offset.txt")
if os.path.exists(tg_off_p):
    with open(tg_off_p, "rb") as fp:
        raw_off = fp.read()
    off_mtime = datetime.fromtimestamp(os.path.getmtime(tg_off_p)).astimezone().isoformat()
    print(f"telegram_offset.txt: Raw={repr(raw_off.decode('utf-8', errors='replace'))} | Size={len(raw_off)} B | Mtime={off_mtime}")

tgl_path = os.path.join(backend_dir, "telegram_command_listener.py")
with open(tgl_path, "r", encoding="utf-8", errors="ignore") as fp:
    tgl_lines = fp.readlines()

print("\n--- telegram_command_listener.py _read_offset & _write_offset & HANDLERS ---")
for idx, l in enumerate(tgl_lines, 1):
    if 95 <= idx <= 125:
        print(f"  L{idx:03d}: {l}", end="")

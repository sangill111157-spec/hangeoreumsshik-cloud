import time
import os
import subprocess
import json
from datetime import datetime

pid = 23940

def get_process_and_wmi_threads():
    ps_cmd = f"""
    $proc = Get-Process -Id {pid} -ErrorAction SilentlyContinue
    $threads_raw = Get-CimInstance Win32_PerfRawData_PerfProc_Thread | Where-Object {{ $_.IDProcess -eq {pid} }} | Select-Object IDThread, PercentProcessorTime, PercentUserTime, PercentPrivilegedTime, ThreadState, ThreadWaitReason, Timestamp_Sys100NS
    
    $res = @{{
        Timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffzzz")
        Process = @{{
            Id = $proc.Id
            ProcessName = $proc.ProcessName
            StartTime = $proc.StartTime.ToString("o")
            TotalProcessorTime = $proc.TotalProcessorTime.TotalSeconds
            UserProcessorTime = $proc.UserProcessorTime.TotalSeconds
            PrivilegedProcessorTime = $proc.PrivilegedProcessorTime.TotalSeconds
            WorkingSet64 = $proc.WorkingSet64
            PrivateMemorySize64 = $proc.PrivateMemorySize64
            PagedMemorySize64 = $proc.PagedMemorySize64
            PeakPagedMemorySize64 = $proc.PeakPagedMemorySize64
            HandleCount = $proc.HandleCount
            ThreadCount = $proc.Threads.Count
        }}
        Threads = $threads_raw
    }}
    $res | ConvertTo-Json -Depth 4
    """
    p = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
    if p.stdout.strip():
        try:
            return json.loads(p.stdout.strip())
        except Exception as e:
            return {"raw": p.stdout.strip(), "error": str(e)}
    return {"status": "NOT_FOUND", "stderr": p.stderr}

def get_system_memory():
    ps_cmd = """
    $os = Get-CimInstance Win32_OperatingSystem
    $res = @{
        Timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffzzz")
        TotalVisibleMemorySizeKB = [int64]$os.TotalVisibleMemorySize
        FreePhysicalMemoryKB = [int64]$os.FreePhysicalMemory
        TotalVirtualMemorySizeKB = [int64]$os.TotalVirtualMemorySize
        FreeVirtualMemoryKB = [int64]$os.FreeVirtualMemory
        SizeStoredInPagingFilesKB = [int64]$os.SizeStoredInPagingFiles
        FreeSpaceInPagingFilesKB = [int64]$os.FreeSpaceInPagingFiles
    }
    $res | ConvertTo-Json
    """
    p = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
    if p.stdout.strip():
        try:
            return json.loads(p.stdout.strip())
        except Exception as e:
            return {"raw": p.stdout.strip(), "error": str(e)}
    return {"status": "NOT_FOUND", "stderr": p.stderr}

print("=== STARTING PURE ISOLATED 120s A-4/A-5 SAMPLER ===")
t_start = time.time()
s1 = get_process_and_wmi_threads()
mem1 = get_system_memory()
print(f"S1 timestamp: {s1.get('Timestamp')}")

print("Sleeping 60 seconds (Phase 1)...")
time.sleep(60)
mem2 = get_system_memory()
print(f"Memory Sample 2 timestamp: {mem2.get('Timestamp')}")

print("Sleeping 60 seconds (Phase 2)...")
time.sleep(60)
s2 = get_process_and_wmi_threads()
mem3 = get_system_memory()
t_end = time.time()
print(f"S2 timestamp: {s2.get('Timestamp')}")
print(f"Memory Sample 3 timestamp: {mem3.get('Timestamp')}")

res = {
    "s1": s1,
    "s2": s2,
    "mem1": mem1,
    "mem2": mem2,
    "mem3": mem3,
    "real_elapsed_seconds": t_end - t_start
}

out_p = r"c:\Users\sangi\Downloads\shin-agent\clean_isolated_metrics.json"
with open(out_p, "w", encoding="utf-8") as fp:
    json.dump(res, fp, indent=2, ensure_ascii=False)

print(f"Successfully wrote pure isolated metrics to {out_p}")

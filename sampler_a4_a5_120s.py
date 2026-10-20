import time
import os
import subprocess
import json
from datetime import datetime

pid = 23940

def get_snapshot():
    ps_cmd = f"""
    $proc = Get-Process -Id {pid} -ErrorAction SilentlyContinue
    $os = Get-CimInstance Win32_OperatingSystem
    
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
            PagefileUsage = $proc.PagedMemorySize64
            PeakPagefileUsage = $proc.PeakPagedMemorySize64
            HandleCount = $proc.HandleCount
            ThreadCount = $proc.Threads.Count
        }}
        SystemMemory = @{{
            TotalVisibleMemorySizeKB = $os.TotalVisibleMemorySize
            FreePhysicalMemoryKB = $os.FreePhysicalMemory
            TotalVirtualMemorySizeKB = $os.TotalVirtualMemorySize
            FreeVirtualMemoryKB = $os.FreeVirtualMemory
            SizeStoredInPagingFilesKB = $os.SizeStoredInPagingFiles
            FreeSpaceInPagingFilesKB = $os.FreeSpaceInPagingFiles
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

print("=== STARTING A-4 / A-5 120-SECOND ISOLATED SAMPLING ===")
s1 = get_snapshot()
t1 = time.time()
print(f"Snapshot 1 captured at {s1.get('Timestamp')}")

time.sleep(120)

s2 = get_snapshot()
t2 = time.time()
print(f"Snapshot 2 captured at {s2.get('Timestamp')}")

with open(r"c:\Users\sangi\Downloads\shin-agent\a4_a5_snapshot_output.json", "w", encoding="utf-8") as fp:
    json.dump({"s1": s1, "s2": s2, "real_elapsed": t2 - t1}, fp, indent=2, ensure_ascii=False)

print("Saved snapshot results to a4_a5_snapshot_output.json")

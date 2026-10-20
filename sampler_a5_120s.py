import time
import os
import subprocess
import json
from datetime import datetime

pid = 23940

def get_threads_snapshot():
    cmd = """
    $proc = Get-Process -Id 23940 -ErrorAction SilentlyContinue
    if ($proc) {
        $threads = $proc.Threads | Select-Object Id, 
            @{N='TotalSec';E={$_.TotalProcessorTime.TotalSeconds}}, 
            @{N='UserSec';E={$_.UserProcessorTime.TotalSeconds}}, 
            @{N='PrivilegedSec';E={$_.PrivilegedProcessorTime.TotalSeconds}}, 
            ThreadState, WaitReason, PriorityLevel, 
            @{N='StartTime';E={$_.StartTime.ToString('o')}}
        $res = @{
            Id = $proc.Id
            ProcessName = $proc.ProcessName
            TotalProcessorTime = $proc.TotalProcessorTime.TotalSeconds
            UserProcessorTime = $proc.UserProcessorTime.TotalSeconds
            PrivilegedProcessorTime = $proc.PrivilegedProcessorTime.TotalSeconds
            WorkingSet64 = $proc.WorkingSet64
            PrivateMemorySize64 = $proc.PrivateMemorySize64
            Threads = $threads
        }
        $res | ConvertTo-Json -Depth 3
    }
    """
    p = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
    if p.stdout.strip():
        try:
            return json.loads(p.stdout.strip())
        except Exception as e:
            return {"raw": p.stdout.strip(), "error": str(e)}
    return {"status": "NOT_FOUND"}

now1 = datetime.now().astimezone().isoformat()
m1 = get_threads_snapshot()
t1 = time.time()
print(f"=== SNAPSHOT 1 (Time: {now1}) ===")
print(json.dumps(m1, indent=2))

print("\nSleeping 120 seconds for isolated thread sampling...")
time.sleep(120)

now2 = datetime.now().astimezone().isoformat()
m2 = get_threads_snapshot()
t2 = time.time()
print(f"\n=== SNAPSHOT 2 (Time: {now2}) ===")
print(json.dumps(m2, indent=2))

elapsed = t2 - t1
print(f"\n=== 120-SECOND INTERVAL COMPARISON ===")
print(f"Real Elapsed: {elapsed:.3f}s")
tot1 = m1.get("TotalProcessorTime", 0)
tot2 = m2.get("TotalProcessorTime", 0)
dtot = tot2 - tot1
avg_cpu = (dtot / elapsed) * 100 if elapsed > 0 else 0
print(f"Process TotalProcessorTime: S1={tot1:.4f}s, S2={tot2:.4f}s, Delta={dtot:.4f}s (Avg 점유율: {avg_cpu:.2f}%)")

print("\n=== GET-COUNTER 3 SAMPLES PROBE ===")
for c_idx in range(3):
    cmd_counter = """
    $samples = Get-Counter -Counter "\\Process(python*)\\* ID Process", "\\Process(python*)\\% Processor Time", "\\Process(python*)\\IO Read Operations/sec", "\\Process(python*)\\IO Read Bytes/sec" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CounterSamples
    $samples | Where-Object { $_.Path -like "*python*" } | Select-Object Path, CookedValue | Format-Table -AutoSize
    """
    p_cnt = subprocess.run(["powershell", "-Command", cmd_counter], capture_output=True, text=True)
    print(f"--- Counter Sample {c_idx+1}/3 ({datetime.now().astimezone().isoformat()}) ---")
    print(p_cnt.stdout)
    if c_idx < 2:
        time.sleep(2)

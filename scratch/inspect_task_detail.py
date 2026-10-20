# -*- coding: utf-8 -*-
import subprocess

def inspect_task_and_pid():
    print("=== 1. Windows Task Scheduler: NVDA Scheduler 상세 ===")
    res = subprocess.run(['schtasks', '/query', '/tn', 'NVDA Scheduler', '/fo', 'LIST', '/v'], capture_output=True, text=True, errors='ignore')
    print(res.stdout)

    print("\n=== 2. PID 26304 프로세스 정보 ===")
    cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -eq 26304 } | Select-Object ProcessId, Name, CommandLine, Path | Format-List"'
    res2 = subprocess.run(cmd, shell=True, capture_output=True, text=True, errors='ignore')
    print(res2.stdout)

if __name__ == "__main__":
    inspect_task_and_pid()

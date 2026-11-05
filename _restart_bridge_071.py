import os, subprocess, sys, time
time.sleep(2)
my_pid = os.getpid()
ps_kill = f"Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*s1_rgon_to_anchongri_bridge.py*' -and $_.ProcessId -ne {my_pid} } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill], capture_output=True)
time.sleep(1)
flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000) | getattr(subprocess, 'DETACHED_PROCESS', 0x00000008)
subprocess.Popen([sys.executable, "s1_rgon_to_anchongri_bridge.py"], cwd=r"C:\Users\sangi\Downloads\shin-agent", creationflags=flags, close_fds=True)

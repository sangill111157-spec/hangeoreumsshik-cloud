# -*- coding: utf-8 -*-
import subprocess
import os
import sys

def get_python_details():
    cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq \'python.exe\' } | Select-Object ProcessId, CommandLine | Format-List"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, errors='ignore')
    print("=== Python Processes ===")
    print(res.stdout)

if __name__ == "__main__":
    get_python_details()

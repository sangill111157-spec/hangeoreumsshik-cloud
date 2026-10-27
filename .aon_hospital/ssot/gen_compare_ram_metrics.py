# -*- coding: utf-8 -*-
"""Compare memory metrics between GlobalMemoryStatusEx and CIM FreePhysicalMemory."""
import ctypes
import datetime
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def compare_ram_metrics():
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

    res = subprocess.run(
        ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
        capture_output=True,
        text=True,
        check=True,
    )
    free_kb = float(res.stdout.strip())
    free_mb = free_kb / 1024.0
    avail_mb = stat.ullAvailPhys / (1024 * 1024)
    total_mb = stat.ullTotalPhys / (1024 * 1024)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{now}] Official Memory Metrics Comparison:")
    print(f"Total Physical Memory: {total_mb:.2f} MB")
    print(f"GlobalMemoryStatusEx (ullAvailPhys / PhysicalAvailable): {avail_mb:.2f} MB")
    print(f"CIM FreePhysicalMemory: {free_mb:.2f} MB")
    print(f"Difference: {abs(avail_mb - free_mb):.2f} MB")


if __name__ == "__main__":
    compare_ram_metrics()

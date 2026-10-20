# -*- coding: utf-8 -*-
import subprocess
import csv
import io
import re

def check_schtasks_and_ports():
    print("=== 1. Windows Task Scheduler 조사 ===")
    try:
        res = subprocess.run(['schtasks', '/query', '/fo', 'CSV'], capture_output=True, text=True, errors='ignore')
        reader = csv.reader(io.StringIO(res.stdout))
        for row in reader:
            if len(row) > 0 and any(k in row[0].lower() for k in ["nvda", "trading", "stock", "kis", "python"]):
                print("  발견된 작업:", row)
    except Exception as e:
        print("schtasks error:", e)

    print("\n=== 2. 리스닝 중인 포트 조사 (netstat) ===")
    try:
        res = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, errors='ignore')
        for line in res.stdout.splitlines():
            if any(p in line for p in [":8000", ":8080", ":3000", ":5173", ":8501", ":6379", ":5432"]):
                print("  포트 활성:", line.strip())
    except Exception as e:
        print("netstat error:", e)

if __name__ == "__main__":
    check_schtasks_and_ports()

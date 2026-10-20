import hashlib
import sys
sys.stdout.reconfigure(encoding='utf-8')

log_path = r"c:\Users\sangi\Downloads\shin-agent\pytest_full_run.log"

h = hashlib.sha256()
with open(log_path, "rb") as f:
    while chunk := f.read(65536):
        h.update(chunk)

print(f"pytest_full_run.log SHA-256: {h.hexdigest()}")

with open(log_path, "r", encoding="utf-8-sig", errors="replace") as f:
    lines = f.readlines()
    print(f"Total lines: {len(lines)}")
    print("=== Last 20 lines ===")
    for line in lines[-20:]:
        print(line, end='')

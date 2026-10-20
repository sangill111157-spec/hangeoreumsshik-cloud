import hashlib
import sys
sys.stdout.reconfigure(encoding='utf-8')

log_path = r"c:\Users\sangi\Downloads\shin-agent\verify_ps1_run.log"

h = hashlib.sha256()
with open(log_path, "rb") as f:
    while chunk := f.read(65536):
        h.update(chunk)

print(f"verify_ps1_run.log SHA-256: {h.hexdigest()}")
print("=== Contents of verify_ps1_run.log ===")
with open(log_path, "r", encoding="utf-8-sig", errors="replace") as f:
    print(f.read())

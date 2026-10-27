import sys
sys.stdout.reconfigure(encoding='utf-8')

log_path = r"c:\Users\sangi\Downloads\shin-agent\verify_ps1_a855d01.log"
with open(log_path, "r", encoding="utf-8-sig", errors="replace") as f:
    print(f.read())

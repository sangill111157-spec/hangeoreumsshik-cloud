import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

res = subprocess.run(
    ["git", "diff", "-U0"],
    cwd=r"C:\trading\package\nvda_trading_system\backend",
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

deleted_lines = []
current_file = ""

for line in res.stdout.splitlines():
    if line.startswith("--- a/"):
        current_file = line[6:]
    elif line.startswith("-") and not line.startswith("---"):
        deleted_lines.append((current_file, line[1:]))

print(f"Total deleted lines: {len(deleted_lines)}")

files = {}
for f, l in deleted_lines:
    files.setdefault(f, []).append(l)

for f, lines_list in files.items():
    print(f"\n=== File: {f} (Deleted {len(lines_list)} lines) ===")
    for l in lines_list:
        stripped = l.strip()
        if stripped.startswith("def ") or stripped.startswith("class ") or "hasattr" in stripped:
            print(f"  [DEF/SIG/HASATTR]: {stripped}")
        else:
            print(f"  [-] {stripped[:90]}")

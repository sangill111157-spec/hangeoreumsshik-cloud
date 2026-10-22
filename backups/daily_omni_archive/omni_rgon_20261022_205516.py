import os
import re
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(r"C:\Users\sangi\Downloads\shin-agent")
BRIDGE_PY = BASE_DIR / "rgon_telegram_bridge.py"


def inspect_omni_queue():
    out = ["🎯 [rgon_aside_extension / OMNI_QUEUE 정밀 해부]"]
    ext_dirs = []
    for root, dirs, files in os.walk(str(BASE_DIR)):
        if "node_modules" in root or ".git" in root:
            continue
        for fn in files:
            if fn.endswith(".js"):
                fp = os.path.join(root, fn)
                try:
                    txt = Path(fp).read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                if "OMNI_QUEUE" in txt:
                    lines = txt.splitlines()
                    for idx, line in enumerate(lines):
                        if "OMNI_QUEUE" in line:
                            s = max(0, idx - 5)
                            e = min(len(lines), idx + 35)
                            snip = "\n".join(f"L{j+1}: {lines[j][:110]}" for j in range(s, e))
                            out.append(f"\n📄 [{fp} : L{idx+1}]\n{snip}")
    return "\n".join(out)


def main():
    report = inspect_omni_queue()
    print(report)
    if BRIDGE_PY.exists():
        subprocess.run([sys.executable, str(BRIDGE_PY), "--send-text", report[:3500]], cwd=str(BASE_DIR))


if __name__ == "__main__":
    main()
Copy
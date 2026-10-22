import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(r"C:\Users\sangi\Downloads\shin-agent")
BRIDGE_PY = BASE_DIR / "rgon_telegram_bridge.py"

cands = list(BASE_DIR.rglob("background.js"))
if cands:
    lines = cands[0].read_text(encoding="utf-8", errors="replace").splitlines()
    top = "\n".join(f"L{i+1}: {lines[i]}" for i in range(min(45, len(lines))))
    msg = f"🎯 [background.js 맨 위 45줄 (진짜 포트 번호)]\n{top}"
else:
    msg = "background.js 없음"

print(msg[:1000])
subprocess.run([sys.executable, str(BRIDGE_PY), "--send-text", msg[:3500]], cwd=str(BASE_DIR))
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(r"C:\Users\sangi\Downloads\shin-agent")
BRIDGE_PY = BASE_DIR / "rgon_telegram_bridge.py"
BG_JS = BASE_DIR / "rgon_aside_extension" / "background.js"


def main():
    if not BG_JS.exists():
        # 혹시 다른 경로에 있으면 찾기
        cands = list(BASE_DIR.rglob("background.js"))
        bg = cands[0] if cands else None
    else:
        bg = BG_JS

    if not bg:
        msg = "background.js 없음"
    else:
        lines = bg.read_text(encoding="utf-8", errors="replace").splitlines()
        out = [f"📄 [{bg}] 총 {len(lines)}줄"]
        for i, line in enumerate(lines):
            if "OMNI_QUEUE" in line or "OMNI_SAVE" in line:
                s = max(0, i - 2)
                e = min(len(lines), i + 28)
                out.append("\n".join(f"L{j+1}: {lines[j]}" for j in range(s, e)))
        msg = "\n---\n".join(out)

    # 마지막 요약에도 그대로 찍히도록 print는 핵심 25줄만 출력
    print(msg[:1200])
    if BRIDGE_PY.exists():
        subprocess.run([sys.executable, str(BRIDGE_PY), "--send-text", msg[:3500]], cwd=str(BASE_DIR))


if __name__ == "__main__":
    main()
Copy
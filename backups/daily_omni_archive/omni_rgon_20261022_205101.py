import os
import re
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(r"C:\Users\sangi\Downloads\shin-agent")
BRIDGE_PY = BASE_DIR / "rgon_telegram_bridge.py"

SEARCH_ROOTS = [
    Path(r"C:\Users\sangi\Downloads"),
    Path(r"C:\Users\sangi\Desktop"),
    Path(r"C:\Users\sangi\Documents"),
    Path(r"C:\trading"),
    Path(r"C:\Users\sangi\AppData\Local\Google\Chrome\User Data\Default\Extensions"),
]


def find_real_extension():
    hits = []
    ports = set()
    skip_dirs = {"node_modules", ".git", "__pycache__", "venv", ".venv", "Cache", "Code Cache"}

    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(str(root)):
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]
            for fn in filenames:
                if not fn.endswith((".js", ".json", ".html")):
                    continue
                fp = os.path.join(dirpath, fn)
                try:
                    if os.path.getsize(fp) > 3 * 1024 * 1024:
                        continue
                    with open(fp, "r", encoding="utf-8", errors="replace") as f:
                        txt = f.read()
                except Exception:
                    continue

                if any(k in txt for k in ("큐 등록 실패", "안총리 실행 큐", "Omni-Link Hub")):
                    lines = txt.splitlines()
                    snippets = []
                    for i, line in enumerate(lines):
                        if any(k in line for k in ("큐 등록", "안총리 실행 큐", "127.0.0.1", "localhost", "fetch(")):
                            start = max(0, i - 2)
                            end = min(len(lines), i + 6)
                            snip = "\n".join(f"L{j+1}: {lines[j][:110]}" for j in range(start, end))
                            snippets.append(snip)
                            for pm in re.findall(r"(?:127\.0\.0\.1|localhost):(\d{2,5})", "\n".join(lines[start:end])):
                                ports.add(int(pm))
                            if len(snippets) >= 4:
                                break
                    hits.append((fp, "\n---\n".join(snippets)))
                    if len(hits) >= 5:
                        return hits, sorted(ports)
    return hits, sorted(ports)


def main():
    hits, ports = find_real_extension()
    out = ["🎯 [만능 소통창(Omni-Link Hub) 진짜 위치 색출 결과]"]
    if not hits:
        out.append("⚠️ 파일 매칭 없음")
    else:
        out.append(f"• 발견된 파일 수: {len(hits)}개")
        out.append(f"• 발견된 포트 번호: {ports}")
        for fp, snip in hits:
            out.append(f"\n📂 경로: {fp}\n{snip}")

    report = "\n".join(out)
    print(report)
    if BRIDGE_PY.exists():
        subprocess.run([sys.executable, str(BRIDGE_PY), "--send-text", report[:3500]], cwd=str(BASE_DIR))


if __name__ == "__main__":
    main()
Copy
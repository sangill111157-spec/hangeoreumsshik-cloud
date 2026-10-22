import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(r"C:\Users\sangi\Downloads\shin-agent")
EXT_DIR = BASE_DIR / "chrome_omni_commander"
BRIDGE_PY = BASE_DIR / "rgon_telegram_bridge.py"


def inspect_extension():
    report_lines = ["🔍 [크롬 만능 소통창 버튼 정밀 해부 보고서]"]
    if not EXT_DIR.exists():
        report_lines.append(f"⚠️ 폴더 없음: {EXT_DIR}")
        return "\n".join(report_lines)

    files = list(EXT_DIR.rglob("*"))
    js_files = [f for f in files if f.is_file() and f.suffix.lower() in (".js", ".json", ".html")]
    report_lines.append(f"• 스캔 파일 수: {len(js_files)}개")

    keywords = ["큐 등록", "안총리 실행 큐", "shin-agent 저장", "127.0.0.1", "localhost", "fetch(", "chrome.downloads"]
    found_blocks = []

    for f in js_files:
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        lines = txt.splitlines()
        for idx, line in enumerate(lines):
            if any(k in line for k in keywords):
                start = max(0, idx - 3)
                end = min(len(lines), idx + 8)
                snippet = "\n".join(f"  L{i+1}: {lines[i][:120]}" for i in range(start, end))
                found_blocks.append(f"\n📄 [{f.name} : {idx+1}줄 근처]\n{snippet}")
                if len(found_blocks) >= 12:
                    break
        if len(found_blocks) >= 12:
            break

    if found_blocks:
        report_lines.extend(found_blocks)
    else:
        report_lines.append("• 키워드 매칭 없음 (파일 목록): " + ", ".join(f.name for f in js_files))

    return "\n".join(report_lines)


def main():
    report = inspect_extension()
    print(report)
    out_file = BASE_DIR / "ext_diagnosis_report.txt"
    out_file.write_text(report, encoding="utf-8")
    if BRIDGE_PY.exists():
        subprocess.run([sys.executable, str(BRIDGE_PY), "--send-text", report[:3500]], cwd=str(BASE_DIR))


if __name__ == "__main__":
    main()
Copy
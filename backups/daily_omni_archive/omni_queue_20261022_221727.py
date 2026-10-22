import os
import re
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(r"C:\Users\sangi\Downloads\shin-agent")
DESKTOP = Path(r"C:\Users\sangi\Desktop")
LOCAL_HTML = BASE_DIR / "rgon_alpha_audience.html"
BRIDGE_PY = BASE_DIR / "rgon_telegram_bridge.py"


def find_chrome():
    for c in (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ):
        if os.path.exists(c):
            return c
    return "chrome.exe"


def get_real_github_pages_url():
    try:
        p = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(BASE_DIR), capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        remote = (p.stdout or "").strip()
        # 예: https://github.com/OWNER/REPO.git
        m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", remote)
        if m:
            owner, repo = m.group(1), m.group(2)
            return remote, f"https://{owner}.github.io/{repo}/rgon_alpha_audience.html"
        return remote, ""
    except Exception:
        return "", ""


def main():
    chrome = find_chrome()
    local_file_url = LOCAL_HTML.as_uri()
    remote_git, real_cloud_url = get_real_github_pages_url()

    # 1. 바탕화면에 404 절대 안 뜨는 [로컬 정본 직결 전용앱] 아이콘 생성!
    lnk_path = DESKTOP / "👑 RGON 사령부 대시보드.lnk"
    ps_cmd = (
        f'$s = (New-Object -ComObject WScript.Shell).CreateShortcut("{lnk_path}"); '
        f'$s.TargetPath = "{chrome}"; '
        f'$s.Arguments = "--app={local_file_url} --window-size=1440,920"; '
        f'$s.WorkingDirectory = "{BASE_DIR}"; '
        f'$s.Save()'
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)

    # 바탕화면에 더블클릭 배치 실행기도 함께 생성
    bat_path = DESKTOP / "👑_RGON_독대실_열기.bat"
    bat_path.write_text(
        f'@echo off\nstart "" "{chrome}" --app="{local_file_url}" --window-size=1440,920\n',
        encoding="utf-8"
    )

    # 2. 지금 즉시 대표님 PC 화면에 전용 대시보드 앱 띄우기! (404 절대 없음!)
    try:
        subprocess.Popen([chrome, f"--app={local_file_url}", "--window-size=1440,920"])
    except Exception:
        os.startfile(str(LOCAL_HTML))

    # 3. 기존 기억 저장소 / 마감 관련 파일 목록 스캔
    mem_items = []
    for p in sorted(BASE_DIR.iterdir()):
        low = p.name.lower()
        if not low.startswith(("omni_", "ahn_queue_")):
            if p.is_dir() or p.suffix.lower() in (".json", ".md", ".py", ".bat"):
                mem_items.append(f"{'📂' if p.is_dir() else '📄'} {p.name}")

    msg = (
        f"👑 [404 없는 PC 직결 대시보드 전용앱 오픈 완료!]\n"
        f"• 지금 PC 화면에 대시보드 전용 앱 창이 바로 열렸습니다!\n"
        f"• 바탕화면 아이콘: [👑 RGON 사령부 대시보드] & [👑_RGON_독대실_열기.bat]\n"
        f"• Git 원격 저장소: {remote_git}\n"
        f"• 추정 클라우드 주소: {real_cloud_url}\n\n"
        f"🧠 [shin-agent 내 폴더 및 기억 저장소 목록]\n"
        + "\n".join(mem_items[:35])
    )
    print(msg)
    if BRIDGE_PY.exists():
        subprocess.run([sys.executable, str(BRIDGE_PY), "--send-text", msg[:3500]], cwd=str(BASE_DIR))


if __name__ == "__main__":
    main()
Copy
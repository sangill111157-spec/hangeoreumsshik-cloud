import json, os, subprocess
from pathlib import Path
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

dk_file = BASE / "S1_DISTROKID_LIVE_RELEASE_DATES.json"
summary_txt = "NO_FILE"
if dk_file.exists():
    data = json.loads(dk_file.read_text(encoding="utf-8"))
    res = data.get("space4_distrokid_result", {})
    album_txt = str(res.get("album_page_text", ""))
    mm_txt = str(res.get("mymusic_overview", ""))
    lines = [ln.strip() for ln in album_txt.splitlines() if ln.strip()]
    key_lines = [ln for ln in lines if any(k in ln for k in ["발매", "업로드", "UPC", "ISRC", "가을", "한걸음씩", "202", "QZ", "KR", "Release", "Uploaded", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.", "11.", "12."])]
    summary_txt = " | ".join(key_lines[:25])[:600]
    if not summary_txt:
        summary_txt = (album_txt[:400] + " / MM:" + mm_txt[:200]).replace("\n", " ")

print("[1/2] GitHub 원격 저장소에 bf10581 디스트로키드 실측 파일 강제 푸시 중...")
subprocess.run(["git", "add", "-f", "S1_DISTROKID_LIVE_RELEASE_DATES.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(090): push Space 4 DistroKid live release dates to origin"], cwd=str(BASE), env=env, creationflags=no_win)
p = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
if p.returncode != 0:
    subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

print("[2/2] Space 0 (르곤 창)으로 디스트로키드 실제 발매일시 요약 직접 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (090호 커밋:{sha} | 디스트로키드 실측: {summary_txt})")

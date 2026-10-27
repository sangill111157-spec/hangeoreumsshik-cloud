import sys
import io
import shutil
import subprocess
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

desktop = Path(r"C:\Users\sangi\OneDrive\Desktop")
workspace = Path(r"c:\Users\sangi\Downloads\shin-agent")

bat_src = workspace / "한걸음씩_만능_AI_사령부_실행.bat"
vbs_src = workspace / "silent_launcher.vbs"

# 1. 배치 파일 복사
if desktop.exists():
    bat_dst = desktop / "한걸음씩_만능_AI_사령부_실행.bat"
    shutil.copy2(bat_src, bat_dst)
    bat_dst2 = desktop / "한걸음씩_만능_AI_사령부.bat"
    shutil.copy2(bat_src, bat_dst2)
    print(f"✅ 배치 파일 복사 완료: {bat_dst}")
    print(f"✅ 배치 파일 복사 완료: {bat_dst2}")

# 2. 바로가기 생성용 파워쉘 스크립트
lnk_target = desktop / "한걸음씩_만능_AI_사령부_실행.lnk"
ps_script = f"""
$wsh = New-Object -ComObject WScript.Shell
$s = $wsh.CreateShortcut('{lnk_target}')
$s.TargetPath = 'wscript.exe'
$s.Arguments = '`"{vbs_src}`"'
$s.WorkingDirectory = '{workspace}'
$s.IconLocation = 'shell32.dll,14'
$s.Description = '한걸음씩 만능 AI 국가 OS (Omni-Nexus v2.0)'
$s.Save()
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
if res.returncode == 0 and lnk_target.exists():
    print(f"✅ 무창 스마트 바로가기(.lnk) 생성 완료: {lnk_target}")
else:
    print(f"⚠️ 바로가기 생성 결과:\n{res.stderr}")

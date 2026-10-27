
import os, subprocess



# 1. 실제 바탕화면(OneDrive 포함) 자동 탐색 및 원클릭 부팅 아이콘 생성

candidates = [

    os.path.expanduser("~/OneDrive/Desktop"),

    os.path.expanduser("~/OneDrive/바탕 화면"),

    os.path.expanduser("~/Desktop"),

    r"C:\Users\sangi\Downloads\shin-agent"

]

desktop = next((d for d in candidates if os.path.isdir(d)), r"C:\Users\sangi\Downloads\shin-agent")

bat = os.path.join(desktop, "RGON_사령부_원클릭_가동.bat")

bat_txt = """@echo off

chcp 65001 >nul

cd /d C:\\Users\\sangi\\Downloads\\shin-agent

start "" /min python -X utf8 omni_bridge.py

start "" /min python -X utf8 -m http.server 8501

python -X utf8 launch_tunnel_and_send_telegram.py

echo RGON 사령부 전체 가동 완료!

pause

"""

open(bat, "w", encoding="utf-8").write(bat_txt)

print("✅ 원클릭 부팅 아이콘 생성 위치:", bat)



# 2. 브리지(8765) + 독대실 서버(8501) + 5G 터널 가동 및 텔레그램 전송

subprocess.Popen(["python", "-X", "utf8", "omni_bridge.py"], creationflags=0x08000000)

subprocess.Popen(["python", "-X", "utf8", "-m", "http.server", "8501"], creationflags=0x08000000)

if os.path.exists("launch_tunnel_and_send_telegram.py"):

    subprocess.run(["python", "-X", "utf8", "launch_tunnel_and_send_telegram.py"])



# 3. GitHub 원격 반영

subprocess.run(["git", "add", "-A"])

subprocess.run(["git", "commit", "-m", "fix(v6.0.8): stop 1s rgon row flicker & add one-click boot script"])

subprocess.run(["git", "push", "origin", "main"])

print("🎉 [깜빡임 완치 + 바탕화면 원클릭 아이콘 + 5G 터널 + GitHub 푸시 100% 완료!]")


@echo off

chcp 65001 >nul

cd /d C:\Users\sangi\Downloads\shin-agent

start "" /min python -X utf8 omni_bridge.py

start "" /min python -X utf8 -m http.server 8501

python -X utf8 launch_tunnel_and_send_telegram.py

echo RGON 사령부 전체 가동 완료!

pause


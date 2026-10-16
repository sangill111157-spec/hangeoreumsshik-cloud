@echo off
chcp 65001 > nul
title 한걸음씩 만능 AI 사령부 (Omni-Nexus v2.0)

:: 작업 디렉터리로 이동
cd /d "c:\Users\sangi\Downloads\shin-agent"

:: 8501 포트가 이미 실행 중인지 확인
netstat -ano | findstr /r /c:":8501 .*LISTENING" > nul
if %errorlevel% equ 0 (
    start http://127.0.0.1:8501
    exit /b 0
)

:: pythonw를 사용하여 검은 콘솔 창 없이 백그라운드로 서버 기동
start "" pythonw run_dashboard.py 2>nul
if %errorlevel% neq 0 (
    start /min "" python run_dashboard.py
)

:: 잠시 후 브라우저 팝업
timeout /t 2 /nobreak > nul
start http://127.0.0.1:8501
exit /b 0

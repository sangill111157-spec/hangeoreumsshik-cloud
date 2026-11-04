@echo off
chcp 65001 >nul
title S1 호스트 3분할 & 에고라이트 마스터 기동기 (038·039호)
cd /d "c:\Users\sangi\Downloads\shin-agent"
echo [S1 039호] 호스트 물리 화면 3분할 정렬, 에고라이트 기동, 실물 캡처 및 Space 0 자동 보고를 시작합니다...
python "c:\Users\sangi\Downloads\shin-agent\s1_host_desktop_agent.py"
echo.
echo [완료] 모든 작업이 완료되었습니다. 3초 후 창이 자동으로 닫힙니다.
timeout /t 3 >nul
exit /b 0


@echo off
chcp 65001 > nul
title [한걸음씩 만능 AI] 모바일 전용 외부 터널 실행기
cd /d "%~dp0"

echo ========================================================
echo  [한걸음씩 만능 AI 사령부] 스마트폰(외부/LTE) 원격 터널
echo ========================================================
echo.
echo * 집 밖(통근버스, 회사, 모바일)에서 스마트폰으로 대시보드를
echo   안전하게 열 수 있는 초고속 Cloudflare HTTPS 보안 터널을 엽니다.
echo.
.\cloudflared.exe tunnel --url http://127.0.0.1:8501
pause

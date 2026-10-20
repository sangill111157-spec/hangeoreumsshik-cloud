@echo off
chcp 65001 > nul
title [안실장] 젠스파크 5시간 스마트 릴레이 어시스턴트
echo ===================================================================
echo [안실장] 젠스파크 AI 5시간 스마트 릴레이 어시스턴트를 실행합니다.
echo ===================================================================
cd /d C:\trading\package\nvda_trading_system\backend
.\venv\Scripts\python.exe C:\Users\sangi\Downloads\shin-agent\smart_relay_5h.py
pause

@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting RGON Omni-Link bridge on 127.0.0.1:8765 ...
python omni_bridge.py
pause

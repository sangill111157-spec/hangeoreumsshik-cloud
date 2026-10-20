# -*- coding: utf-8 -*-
import os
import shutil
import zipfile

src_root = r"C:\trading\package\nvda_trading_system"
temp_dir = r"C:\trading\package\temp_migration_package"
desktop_onedrive = r"C:\Users\sangi\OneDrive\Desktop"
desktop_local = r"C:\Users\sangi\Desktop"

target_desktop = desktop_onedrive if os.path.exists(desktop_onedrive) else desktop_local
zip_filename = "NVDA_트레이딩시스템_새노트북_이전패키지.zip"
zip_path = os.path.join(target_desktop, zip_filename)

print(f"Target zip: {zip_path}")

if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir, ignore_errors=True)
os.makedirs(temp_dir, exist_ok=True)

# 1. 파일 복사 (제외 패턴)
ignore_patterns = shutil.ignore_patterns(
    "venv", "node_modules", "dist", ".git", ".githooks",
    ".pytest_cache", ".ruff_cache", "__pycache__", "*.pyc",
    "*.log", "--store-dir"
)

# 복사 대상: backend, nvda-trading-dashboard, docs, README.md, .gitignore
for item in ["backend", "nvda-trading-dashboard", "docs"]:
    s = os.path.join(src_root, item)
    d = os.path.join(temp_dir, item)
    if os.path.exists(s):
        print(f"Copying {item}...")
        shutil.copytree(s, d, ignore=ignore_patterns)

for item in ["README.md", ".gitignore"]:
    s = os.path.join(src_root, item)
    d = os.path.join(temp_dir, item)
    if os.path.exists(s):
        shutil.copy2(s, d)

# 2. 배치 파일 및 가이드 생성
bat1 = """@echo off
chcp 65001 > nul
title [안실장] 엔비디아 트레이딩 시스템 - 최초 1회 설치 및 실행
color 0A
echo ========================================================
echo   [안실장] 엔비디아 트레이딩 시스템 새 노트북 자동 세팅
echo ========================================================
echo.
cd /d "%~dp0backend"

echo [1/3] 파이썬 설치 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [오류] 파이썬이 설치되어 있지 않거나 환경변수(PATH)에 등록되지 않았습니다!
    echo.
    echo 해결 방법:
    echo 1. python.org 에서 파이썬 (3.10~3.12) 다운로드
    echo 2. 설치 첫 화면 맨 아래 '[v] Add python.exe to PATH' 꼭 체크 후 설치!
    echo.
    pause
    exit /b 1
)
python --version

echo.
echo [2/3] 가상환경(venv) 생성 및 필수 라이브러리 자동 설치 중...
echo (인터넷 속도에 따라 약 1~3분 정도 걸립니다. 잠시만 기다려주세요!)
if not exist "venv" (
    echo 가상환경(venv) 폴더 생성 중...
    python -m venv venv
)

call venv\\Scripts\\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

echo.
echo [3/3] 축하합니다! 세팅이 완료되었습니다.
echo 백엔드 트레이딩 서버(포트 8000)를 지금 가동합니다!
echo (이 검은색 창을 닫지 마시고 최소화해두시면 서버가 24시간 계속 작동합니다.)
echo ========================================================
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
"""

bat2 = """@echo off
chcp 65001 > nul
title [안실장] 엔비디아 트레이딩 서버 (백엔드)
color 0B
echo ========================================================
echo   [안실장] 엔비디아 트레이딩 서버 시작 (백엔드)
echo ========================================================
echo.
cd /d "%~dp0backend"
if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
    echo 서버(포트 8000)가 정상 가동 중입니다.
    echo 이 창을 닫지 마시고 최소화해두세요!
    echo ========================================================
    uvicorn app.main:app --host 0.0.0.0 --port 8000
) else (
    color 0C
    echo [안내] 가상환경이 아직 생성되지 않았습니다.
    echo 먼저 '1_새노트북_처음설치_및_서버실행.bat'을 실행해주세요!
    pause
)
"""

bat3 = """@echo off
chcp 65001 > nul
title [안실장] 트레이딩 대시보드 (웹 화면)
color 0E
echo ========================================================
echo   [안실장] 트레이딩 대시보드 웹 화면 시작
echo ========================================================
echo.
cd /d "%~dp0nvda-trading-dashboard"
where npm >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [오류] Node.js 가 설치되어 있지 않습니다!
    echo 대시보드 웹 화면을 띄우시려면 nodejs.org 에서 LTS 버전을 설치해주세요.
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo [안내] 대시보드 패키지를 최초 1회 자동 설치합니다...
    call npm install
)
echo.
echo 대시보드 웹 화면을 시작합니다! 브라우저 창이 뜨면 확인하실 수 있습니다.
call npm run dev
pause
"""

guide_txt = """======================================================================
  [안실장 특급 가이드] 엔비디아 트레이딩 시스템 새 노트북 이사 안내서
======================================================================

사장님, 축하드립니다! 트레이딩 전용 노트북으로 쾌적하게 이전해볼까요?
딱 3가지만 순서대로 하시면 됩니다!

----------------------------------------------------------------------
[1단계] 새 노트북에 기본 프로그램 1개 (필요시 2개) 설치하기
----------------------------------------------------------------------
1. 파이썬(Python) 설치 (필수!)
   - 웹브라우저에서 https://www.python.org 접속 -> Downloads 클릭
   - ⚠️ 가장 중요한 점:
     다운로드받은 파이썬 설치 파일을 실행했을 때 첫 화면 맨 아래에 있는
     [✓] Add python.exe to PATH (경로 추가) 체크박스를 반드시 체크하고!
     "Install Now"를 눌러주세요.

2. Node.js 설치 (대시보드 웹 화면도 새 노트북에서 띄우실 경우만 설치)
   - https://nodejs.org 접속 -> LTS 버전 다운로드 후 기본값으로 계속 다음(Next) 눌러 설치.

----------------------------------------------------------------------
[2단계] 이 압축파일(NVDA_트레이딩시스템_새노트북_이전패키지.zip) 풀기
----------------------------------------------------------------------
- 새 노트북의 원하는 위치 (추천: C:\\trading\\package\\nvda_trading_system)에
  압축을 풀어주세요.

----------------------------------------------------------------------
[3단계] 더블클릭으로 자동 실행!
----------------------------------------------------------------------
1. 가장 먼저:
   👉 "1_새노트북_처음설치_및_서버실행.bat" 더블클릭!
   - 알아서 새 노트북 환경에 맞게 가상환경(venv)을 만들고,
     필요한 라이브러리를 전부 자동으로 깔아준 뒤 서버(포트 8000)를 가동합니다.
   - 검은 창에 서버가 켜지면 창을 끄지 마시고 최소화해두시면 됩니다!

2. (선택사항) 웹 대시보드 화면도 보실 때:
   👉 "3_대시보드_화면_실행.bat" 더블클릭!
   - 예쁜 차트와 매매 상태가 나오는 웹 대시보드가 브라우저에 열립니다.

3. 다음 날부터 서버를 다시 켤 때:
   👉 "2_평상시_서버실행.bat"만 가볍게 더블클릭하시면 바로 켜집니다!

----------------------------------------------------------------------
[중요 확인 사항]
- 한국투자증권(KIS) API 키와 텔레그램 봇 토큰 등 모든 핵심 설정은
  backend/.env 파일에 그대로 보존되어 함께 들어있습니다. 별도 재입력 필요 없음!
- 점핑클럽 와이파이가 끊기지 않게 연결되어 있는지 확인해주세요.
----------------------------------------------------------------------
"""

with open(os.path.join(temp_dir, "1_새노트북_처음설치_및_서버실행.bat"), "w", encoding="utf-8") as f:
    f.write(bat1)

with open(os.path.join(temp_dir, "2_평상시_서버실행.bat"), "w", encoding="utf-8") as f:
    f.write(bat2)

with open(os.path.join(temp_dir, "3_대시보드_화면_실행.bat"), "w", encoding="utf-8") as f:
    f.write(bat3)

with open(os.path.join(temp_dir, "[필독]_새_노트북_설치_및_실행방법.txt"), "w", encoding="utf-8") as f:
    f.write(guide_txt)

# 3. zip 압축 생성
print(f"Creating zip file at {zip_path}...")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, temp_dir)
            zipf.write(file_path, arcname)

# 정리
shutil.rmtree(temp_dir, ignore_errors=True)

size_mb = os.path.getsize(zip_path) / (1024 * 1024)
print(f"SUCCESS: Package created! File size: {size_mb:.2f} MB")

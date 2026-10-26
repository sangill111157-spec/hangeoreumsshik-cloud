# ASUS ZenBook Duo 하단 화면(ScreenPad Plus) 복구 스크립트
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " [안총리 & 아온이] 하단 화면(ScreenPad Plus) 복구 작전! 💧" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan

# 1. 멈춰있는 사용자 UI 프로세스 종료
Get-Process AsusScreenXpertUserUI -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 800

# 2. ScreenXpert 앱 실행
Start-Process "explorer.exe" "shell:AppsFolder\B9ECED6F.ScreenPadMaster_qmba6cd70vzyy!B9ECED6F.ScreenPadMaster"
Start-Sleep -Milliseconds 800

# 3. 보조 UI 프로세스 보강 실행
$exePath = "C:\Program Files\ASUS\AsusScreenXpert\AsusScreenXpertUserUI.exe"
if (Test-Path $exePath) {
    Start-Process $exePath -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host ">> 복구 명령이 성공적으로 전송되었습니다!" -ForegroundColor Green
Write-Host ">> 하단 화면의 숨겨진 반투명 탭이나 좌측 화살표(▶)를 살짝 터치해보세요!" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Start-Sleep -Seconds 2

# -*- coding: utf-8 -*-
"""
win_auto_typer_daemon.py
--------------------------------------------------------------------------------
⚡ 윈도우 무인 오토 타이퍼 데몬 (Windows Native Auto-Typer Daemon)

이상일 대표님([COMMANDER-000])의 특명:
클립보드에 르곤이 시그널('⟪⚡RGON_SIGNAL_READY⚡⟫') 또는 '안실장(' 감지 시:
1. NEXT_TASK_FOR_ANTIGRAVITY.md & omni_agent_bus.json에 자동 기록
2. Windows 창 활성화 (AppActivate) -> Ctrl+V (붙여넣기) -> Enter (전송) 실제 키보드 자동 타건!
--------------------------------------------------------------------------------
"""

import os
import sys
import time
import json
import hashlib
import subprocess
import datetime
from pathlib import Path
import ctypes

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent
TASK_FILE = ROOT_DIR / "NEXT_TASK_FOR_ANTIGRAVITY.md"
BUS_FILE = ROOT_DIR / "omni_agent_bus.json"
PID_FILE = ROOT_DIR / ".win_auto_typer.pid"
LOG_FILE = ROOT_DIR / ".win_auto_typer.log"

CF_UNICODETEXT = 13

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def get_clipboard_text():
    """Win32 API로 0ms 초고속 유니코드 클립보드 텍스트 읽기"""
    text = ""
    try:
        if user32.OpenClipboard(0):
            h_data = user32.GetClipboardData(CF_UNICODETEXT)
            if h_data:
                p_data = kernel32.GlobalLock(h_data)
                if p_data:
                    text = ctypes.c_wchar_p(p_data).value or ""
                    kernel32.GlobalUnlock(h_data)
            user32.CloseClipboard()
    except Exception:
        # Fallback to powershell if ctypes fails
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                                 capture_output=True, text=True, encoding="utf-8", errors="replace")
            text = res.stdout
        except Exception:
            pass
    return text

def trigger_auto_type_into_antigravity():
    """PowerShell WScript.Shell을 이용해 Antigravity IDE 창 포커스 -> Ctrl+V -> Enter 전송"""
    ps_script = """
    $wshell = New-Object -ComObject WScript.Shell
    # 1. Antigravity 창 활성화 시도
    $activated = $wshell.AppActivate('Antigravity')
    if (-not $activated) {
        $activated = $wshell.AppActivate('Cursor')
    }
    if (-not $activated) {
        $activated = $wshell.AppActivate('Visual Studio Code')
    }
    Start-Sleep -Milliseconds 250
    # 2. 붙여넣기 (Ctrl+V) & 엔터 (Enter)
    $wshell.SendKeys('^v')
    Start-Sleep -Milliseconds 200
    $wshell.SendKeys('{ENTER}')
    Write-Output "TYPED_SUCCESS"
    """
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5)
        return "TYPED_SUCCESS" in res.stdout
    except Exception as e:
        print(f"⚠️ Auto-type error: {e}")
        return False

def record_task_and_bus(raw_text):
    """작업 파일 및 버스에 등록"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_prompt = raw_text.strip()

    # 1. NEXT_TASK_FOR_ANTIGRAVITY.md 기록
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        f.write(f"# ⚡ [오토 타이퍼 감지] 신규 과업 지시서\n- **일시**: {now}\n\n---\n\n{clean_prompt}\n")

    # 2. omni_agent_bus.json 기록
    if BUS_FILE.exists():
        try:
            with open(BUS_FILE, "r", encoding="utf-8") as f:
                bus = json.load(f)
            msg_id = f"MSG-{datetime.datetime.now().strftime('%Y%m%d')}-{len(bus.get('messages', [])) + 1:04d}"
            bus.setdefault("messages", []).append({
                "msg_id": msg_id,
                "timestamp": now,
                "from": "RGON-001",
                "to": "AGV-101",
                "type": "AUTO_SIGNAL_IN",
                "content": clean_prompt[:200] + ("..." if len(clean_prompt) > 200 else ""),
                "status": "AUTO_INJECTED"
            })
            with open(BUS_FILE, "w", encoding="utf-8") as f:
                json.dump(bus, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    print(line, end="")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass

def run_loop():
    """상시 백그라운드 클립보드 감시 루프"""
    log("🚀 [win_auto_typer_daemon] 백그라운드 클립보드 감시 시작 (주기: 0.5초)")
    with open(PID_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))

    last_hash = ""
    while True:
        try:
            text = get_clipboard_text()
            if text:
                cur_hash = hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest()
                if cur_hash != last_hash:
                    # 키워드 검사: 르곤이 시그널 또는 안실장 호출
                    has_signal = "⟪⚡RGON_SIGNAL_READY⚡⟫" in text or "RGON_SIGNAL_READY" in text
                    has_call = "안실장(" in text or "[COMMANDER-000]" in text

                    if has_signal or has_call:
                        last_hash = cur_hash
                        log(f"🎯 [시그널 감지!] 텍스트 길이: {len(text)}자 -> 작업 기록 및 키보드 자동 타건 개시")
                        record_task_and_bus(text)

                        # 실제 Ctrl+V + Enter 자동 타건!
                        typed = trigger_auto_type_into_antigravity()
                        log(f"⌨️ [키보드 자동 타건 결과]: {'성공 (Ctrl+V + Enter 완료)' if typed else '창 활성화 실패'}")
            time.sleep(0.5)
        except Exception as e:
            log(f"⚠️ Loop exception: {e}")
            time.sleep(1)

def check_status():
    """데몬 상태 확인"""
    if PID_FILE.exists():
        try:
            pid = int(open(PID_FILE, "r").read().strip())
            # check if pid is running
            import ctypes
            PROCESS_QUERY_INFORMATION = 0x0400
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, 0, pid)
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                print(f"✅ win_auto_typer_daemon is RUNNING (PID: {pid})")
                return True
        except Exception:
            pass
    print("❌ win_auto_typer_daemon is NOT running")
    return False

if __name__ == "__main__":
    if "--status" in sys.argv:
        is_running = check_status()
        sys.exit(0 if is_running else 1)
    if "--type-test" in sys.argv:
        print("Testing trigger_auto_type_into_antigravity...")
        res = trigger_auto_type_into_antigravity()
        print(f"Result: {res}")
        sys.exit(0 if res else 1)

    run_loop()

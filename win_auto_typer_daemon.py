# -*- coding: utf-8 -*-
"""
══════════════════════════════════════════════════════════════════
 ⚡ 윈도우 무인 오토 타이퍼 데몬 (Windows Native Auto-Typer Daemon v2.0)
 win_auto_typer_daemon.py
 
 [핵심 기능]
 1. 0.3초 주기 Win32 무부하 클립보드 감시 (RGON_SIGNAL_READY / 안실장 / 30자 이상)
 2. 감지 즉시 "띠리링!" 사운드 피드백 (winsound.Beep)
 3. NEXT_TASK_FOR_ANTIGRAVITY.md & omni_agent_bus.json 즉시 동기화
 4. Win32 EnumWindows -> SetForegroundWindow -> Ctrl+L -> Ctrl+V -> Enter 하드웨어 레벨 타건
 5. 스마트폰 원격 복붙 API 연동 지원 (set_clipboard_text & direct trigger)
══════════════════════════════════════════════════════════════════
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
from ctypes import wintypes

try:
    import winsound
except ImportError:
    winsound = None

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent
TASK_FILE = ROOT_DIR / "NEXT_TASK_FOR_ANTIGRAVITY.md"
BUS_FILE = ROOT_DIR / "omni_agent_bus.json"
PID_FILE = ROOT_DIR / ".win_auto_typer.pid"
LOG_FILE = ROOT_DIR / ".win_auto_typer.log"

# Win32 상수
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
SW_RESTORE = 9
VK_CONTROL = 0x11
VK_RETURN = 0x0D
VK_L = 0x4C
VK_V = 0x56
KEYEVENTF_KEYUP = 0x0002

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def play_success_beep():
    """대표님께 복사 즉시 반응을 알리는 경쾌한 '띠리링!' 비프음"""
    if winsound:
        try:
            winsound.Beep(1000, 150)
            winsound.Beep(1500, 200)
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
        pass
    return text

def set_clipboard_text(text: str):
    """Win32 API로 유니코드 텍스트를 클립보드에 정확히 쓰기"""
    try:
        if not user32.OpenClipboard(0):
            return False
        user32.EmptyClipboard()
        # UTF-16LE 바이트 버퍼 생성 (surrogate safe)
        encoded = text.encode("utf-16le", errors="replace") + b"\x00\x00"
        h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
        if not h_mem:
            user32.CloseClipboard()
            return False
        p_mem = kernel32.GlobalLock(h_mem)
        if not p_mem:
            kernel32.GlobalFree(h_mem)
            user32.CloseClipboard()
            return False
        ctypes.memmove(p_mem, encoded, len(encoded))
        kernel32.GlobalUnlock(h_mem)
        user32.SetClipboardData(CF_UNICODETEXT, h_mem)
        user32.CloseClipboard()
        return True
    except Exception as e:
        log(f"⚠️ set_clipboard_text failed: {e}")
        return False

def find_target_window():
    """Antigravity, shin-agent, Cursor, VS Code 등 메인 IDE 창 핸들 탐색"""
    target_hwnds = []

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def enum_windows_callback(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value
                lower_title = title.lower()
                # 우선순위 키워드
                if any(k in lower_title for k in ["antigravity", "shin-agent", "cursor", "visual studio code"]):
                    target_hwnds.append((hwnd, title))
        return True

    cb = WNDENUMPROC(enum_windows_callback)
    user32.EnumWindows(cb, 0)

    if not target_hwnds:
        return None, None

    # 최적의 윈도우 선택 (Antigravity 또는 shin-agent 우선)
    for hwnd, title in target_hwnds:
        if "antigravity" in title.lower() or "shin-agent" in title.lower():
            return hwnd, title
    return target_hwnds[0]

def send_native_key(vk_code):
    """Win32 keybd_event로 하드웨어 레벨 키 입력"""
    user32.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)

def send_native_ctrl_key(vk_code):
    """Win32 keybd_event로 Ctrl + Key 조합 전송"""
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)

def trigger_auto_type_into_antigravity(prompt_text: str = None):
    """
    Antigravity IDE 창을 활성화하고 채팅창에 Ctrl+V + Enter 하드웨어 레벨 타건
    """
    if prompt_text:
        # 프롬프트 텍스트를 클립보드에 확실히 세팅
        set_clipboard_text(prompt_text)

    # 1. 대상 윈도우 찾기
    hwnd, title = find_target_window()
    if not hwnd:
        log("⚠️ 대상 IDE 창을 찾지 못했습니다. 활성 창에 직접 타건을 시도합니다.")
    else:
        log(f"🪟 대상 창 발견: [{title}] (HWND: {hwnd}) -> 강제 활성화")
        try:
            user32.ShowWindow(hwnd, SW_RESTORE)
            user32.SetForegroundWindow(hwnd)
            user32.BringWindowToTop(hwnd)
        except Exception as e:
            log(f"⚠️ 창 활성화 실패: {e}")

    time.sleep(0.3)

    # 2. 채팅창 포커스 활성화 (단축키 Ctrl + L 전송 시도)
    try:
        send_native_ctrl_key(VK_L)
        time.sleep(0.2)
    except Exception:
        pass

    # 3. 붙여넣기 (Ctrl + V)
    log("📋 [하드웨어 타건] Ctrl + V (붙여넣기) 실행")
    send_native_ctrl_key(VK_V)

    # 4. 0.3초 대기 후 전송 (Enter)
    time.sleep(0.3)
    log("🚀 [하드웨어 타건] Enter (전송) 실행")
    send_native_key(VK_RETURN)

    return True

def record_task_and_bus(raw_text):
    """작업 파일 및 메시지 버스에 안전하게 기록"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_prompt = raw_text.strip()

    # 1. NEXT_TASK_FOR_ANTIGRAVITY.md 기록
    try:
        with open(TASK_FILE, "w", encoding="utf-8", errors="replace") as f:
            f.write(f"# ⚡ [오토 타이퍼 감지] 신규 과업 지시서\n- **일시**: {now}\n\n---\n\n{clean_prompt}\n")
    except Exception as e:
        log(f"⚠️ TASK_FILE write error: {e}")

    # 2. omni_agent_bus.json 기록
    if BUS_FILE.exists():
        try:
            with open(BUS_FILE, "r", encoding="utf-8", errors="replace") as f:
                bus = json.load(f)
            msg_id = f"MSG-{datetime.datetime.now().strftime('%Y%m%d')}-{len(bus.get('messages', [])) + 1:04d}"
            bus.setdefault("messages", []).append({
                "msg_id": msg_id,
                "timestamp": now,
                "from": "RGON-001",
                "to": "AGV-101",
                "type": "AUTO_SIGNAL_IN",
                "content": clean_prompt[:250] + ("..." if len(clean_prompt) > 250 else ""),
                "status": "AUTO_INJECTED"
            })
            with open(BUS_FILE, "w", encoding="utf-8", errors="replace") as f:
                json.dump(bus, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log(f"⚠️ BUS_FILE write error: {e}")

def run_loop():
    """상시 백그라운드 클립보드 감시 루프 (0.3초 주기)"""
    log("🚀 [win_auto_typer_daemon v2.0] 백그라운드 감시 가동 (주기: 0.3s)")
    with open(PID_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))

    # 시작 시 기존 클립보드 내용을 해시로 초기화하여 중복 발동 방지
    init_text = get_clipboard_text()
    last_hash = hashlib.md5(init_text.encode("utf-8", errors="ignore")).hexdigest() if init_text else ""

    while True:
        try:
            text = get_clipboard_text()
            if text and len(text.strip()) >= 30:
                cur_hash = hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest()
                if cur_hash != last_hash:
                    # 정밀 감지 조건: 르곤이 시그널 또는 안실장 호출
                    has_signal = "⟪⚡RGON_SIGNAL_READY⚡⟫" in text or "RGON_SIGNAL_READY" in text
                    has_call = "안실장" in text or "[COMMANDER-000]" in text or "[AGV-101]" in text

                    if has_signal or has_call:
                        last_hash = cur_hash
                        log(f"🎯 [시그널 포착!] 텍스트 길이: {len(text)}자 -> 청각 피드백 발동!")
                        play_success_beep()
                        record_task_and_bus(text)

                        # 하드웨어 레벨 자동 타건
                        trigger_auto_type_into_antigravity(text)
                        log("✅ [무인 타건 완료] IDE 채팅창에 Ctrl+V + Enter 주입 완료!")
            time.sleep(0.3)
        except Exception as e:
            log(f"⚠️ Loop error: {e}")
            time.sleep(1)

def check_status():
    """데몬 구동 여부 확인"""
    if PID_FILE.exists():
        try:
            pid = int(open(PID_FILE, "r").read().strip())
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
        play_success_beep()
        res = trigger_auto_type_into_antigravity()
        print(f"Result: {res}")
        sys.exit(0 if res else 1)
    if "--remote-trigger" in sys.argv:
        # 스마트폰 원격 호출 시: sys.stdin 바이너리 버퍼에서 utf-8 디코딩 수신
        try:
            raw = sys.stdin.buffer.read().decode('utf-8', errors='replace')
        except Exception:
            raw = sys.stdin.read()
        if raw:
            play_success_beep()
            record_task_and_bus(raw)
            trigger_auto_type_into_antigravity(raw)
            sys.exit(0)

    run_loop()

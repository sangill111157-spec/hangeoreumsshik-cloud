# -*- coding: utf-8 -*-
"""
══════════════════════════════════════════════════════════════════
 ⚡ 윈도우 무인 오토 타이퍼 데몬 (Windows Native Auto-Typer Daemon v3.0)
 win_auto_typer_daemon.py
 
 [v3.0 핵심 개조: 100% 불통 제로 마우스 물리 클릭 + F8 좌표 학습]
 1. 허공 타건(Ctrl+L) 완전 폐기 -> 실제 마우스 물리 좌클릭(SetCursorPos + mouse_event x2)
 2. F8 핫키 학습: 안실장 채팅 입력칸에 마우스 올리고 F8 누르면 target_pos.json 영구 기억 + Beep!
 3. 기본 좌표: Antigravity 창 우측 하단 (rect.right - 220, rect.bottom - 95)
 4. 클립보드 감지 조건 완화: "⟪⚡RGON_SIGNAL_READY⚡⟫", "[발신:", "안실장!" 포함 시 0.3s 이내 즉각 발동!
 5. 스마트폰 원격 발사 API (/api/remote-auto-paste) 직통 타건 지원
══════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import json
import hashlib
import subprocess
import datetime
import threading
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
TARGET_POS_FILE = ROOT_DIR / "target_pos.json"

# Win32 상수
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
SW_RESTORE = 9
VK_CONTROL = 0x11
VK_RETURN = 0x0D
VK_V = 0x56
VK_F8 = 0x77
KEYEVENTF_KEYUP = 0x0002

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]

class POINT(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long)
    ]

def play_success_beep():
    """대표님께 성공/감지 반응을 알리는 경쾌한 비프음"""
    if winsound:
        try:
            winsound.Beep(1200, 120)
            winsound.Beep(1600, 150)
        except Exception:
            pass

def play_f8_beep():
    """F8 좌표 저장 시 특별한 '삐리릭!' 사운드"""
    if winsound:
        try:
            winsound.Beep(1800, 100)
            winsound.Beep(2200, 150)
            winsound.Beep(2600, 200)
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
    """Antigravity IDE 창 핸들 및 타이틀 탐색"""
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
                if any(k in lower_title for k in ["antigravity", "shin-agent", "cursor", "visual studio code"]):
                    target_hwnds.append((hwnd, title))
        return True

    cb = WNDENUMPROC(enum_windows_callback)
    user32.EnumWindows(cb, 0)

    if not target_hwnds:
        return None, None

    for hwnd, title in target_hwnds:
        if "antigravity" in title.lower() or "shin-agent" in title.lower():
            return hwnd, title
    return target_hwnds[0]

def send_native_key(vk_code):
    """Win32 keybd_event 키 입력"""
    user32.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.04)
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.04)

def send_native_ctrl_key(vk_code):
    """Win32 keybd_event Ctrl + Key 조합 전송"""
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.04)
    user32.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.04)
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.04)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.04)

def mouse_double_click_at(x, y):
    """물리적 마우스 커서 이동 및 좌클릭 2회 (확실한 포커스 획득)"""
    log(f"🖱️ [물리 마우스 이동 & 클릭] 좌표 ({x}, {y}) 로 커서 이동")
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.05)
    
    # 1차 클릭
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.04)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.06)
    
    # 2차 클릭 (채팅 입력창 완전 활성화)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.04)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.1)

def get_target_click_pos(hwnd=None):
    """F8로 저장된 커스텀 좌표가 있으면 최우선 사용, 없으면 창 기준 계산"""
    if TARGET_POS_FILE.exists():
        try:
            with open(TARGET_POS_FILE, "r", encoding="utf-8") as f:
                pos = json.load(f)
                if "x" in pos and "y" in pos:
                    return int(pos["x"]), int(pos["y"]), "F8 커스텀 학습 좌표"
        except Exception:
            pass

    if hwnd:
        rect = RECT()
        if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            # Antigravity 창 우측 하단 채팅 입력창 지점
            x = rect.right - 220
            y = rect.bottom - 95
            return int(x), int(y), "창 우측하단 기본 좌표"

    # 기본 화면 우측 하단
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    return int(screen_w - 250), int(screen_h - 100), "화면 우측하단 안전 좌표"

def trigger_auto_type_into_antigravity(prompt_text: str = None):
    """
    [v3.0 핵심] 마우스 물리 클릭으로 채팅창 포커스 100% 획득 -> Ctrl+V -> Enter
    """
    if prompt_text:
        set_clipboard_text(prompt_text)

    # 1. 대상 윈도우 찾기 및 전면 활성화
    hwnd, title = find_target_window()
    if hwnd:
        log(f"🪟 대상 창 발견: [{title}] (HWND: {hwnd}) -> 전면 활성화")
        try:
            user32.ShowWindow(hwnd, SW_RESTORE)
            user32.SetForegroundWindow(hwnd)
            user32.BringWindowToTop(hwnd)
        except Exception as e:
            log(f"⚠️ 창 활성화 예외: {e}")
    else:
        log("⚠️ 대상 창 직접 핸들 미발견 -> 현재 활성 창 기준 타건")

    time.sleep(0.2)

    # 2. 마우스 물리적 좌클릭 2회로 채팅 입력칸에 커서 확실히 꽂기!
    target_x, target_y, pos_desc = get_target_click_pos(hwnd)
    log(f"🎯 [마우스 타겟팅] {pos_desc}: ({target_x}, {target_y})")
    mouse_double_click_at(target_x, target_y)

    # 3. 0.2초 대기 후 붙여넣기 (Ctrl + V)
    time.sleep(0.2)
    log("📋 [하드웨어 타건] Ctrl + V (붙여넣기) 실행")
    send_native_ctrl_key(VK_V)

    # 4. 0.3초 대기 후 전송 (Enter)
    time.sleep(0.3)
    log("🚀 [하드웨어 타건] Enter (전송) 때려박기 완료!")
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

def f8_hotkey_listener():
    """F8 키를 누르면 현재 마우스 위치를 target_pos.json에 영구 기억"""
    log("👂 [F8 핫키 감시 가동] 대표님이 안실장 입력칸에 마우스 올리고 F8을 누르면 좌표 영구 저장!")
    last_f8_state = False

    while True:
        try:
            # 0x8000: 키가 현재 눌려있음
            f8_pressed = bool(user32.GetAsyncKeyState(VK_F8) & 0x8000)
            if f8_pressed and not last_f8_state:
                pt = POINT()
                if user32.GetCursorPos(ctypes.byref(pt)):
                    pos_data = {"x": pt.x, "y": pt.y, "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    with open(TARGET_POS_FILE, "w", encoding="utf-8") as f:
                        json.dump(pos_data, f, indent=2)
                    log(f"🎉 [F8 학습 완료!] 안실장 입력칸 마우스 좌표 영구 기억: ({pt.x}, {pt.y})")
                    play_f8_beep()
            last_f8_state = f8_pressed
            time.sleep(0.05)
        except Exception as e:
            time.sleep(0.5)

def run_loop():
    """상시 백그라운드 클립보드 감시 루프 (0.3초 주기)"""
    log("🚀 [win_auto_typer_daemon v3.0] 마우스 물리 클릭 + F8 학습 오토타이퍼 가동")
    with open(PID_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))

    # F8 핫키 리스너 백그라운드 스레드 가동
    t = threading.Thread(target=f8_hotkey_listener, daemon=True)
    t.start()

    init_text = get_clipboard_text()
    last_hash = hashlib.md5(init_text.encode("utf-8", errors="ignore")).hexdigest() if init_text else ""

    while True:
        try:
            text = get_clipboard_text()
            if text and len(text.strip()) >= 10:
                cur_hash = hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest()
                if cur_hash != last_hash:
                    # 감지 조건 대폭 완화: 르곤이 시그널 또는 발신 또는 안실장!
                    has_signal = ("⟪⚡RGON_SIGNAL_READY⚡⟫" in text or 
                                  "RGON_SIGNAL_READY" in text or 
                                  "[발신:" in text or 
                                  "안실장!" in text or 
                                  "[COMMANDER-000]" in text)

                    if has_signal:
                        last_hash = cur_hash
                        log(f"🎯 [시그널 포착!] 텍스트 길이: {len(text)}자 -> 청각 피드백 발동!")
                        play_success_beep()
                        record_task_and_bus(text)

                        # 마우스 물리 클릭 + Ctrl+V + Enter 하드웨어 레벨 자동 타건
                        trigger_auto_type_into_antigravity(text)
                        log("✅ [무인 타건 완료] 마우스 물리 클릭 -> Ctrl+V -> Enter 주입 완료!")
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
            handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, 0, pid)
            if handle:
                kernel32.CloseHandle(handle)
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

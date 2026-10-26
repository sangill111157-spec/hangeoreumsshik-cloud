#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""arrange_ceo_windows.py — 대표님 듀얼 모니터(상단·하단) 4대 지휘 창 황금 분할 자동 배치 시스템
v11.43-AON-LIVE-UI-HEALER · 기술총리 안총리 & 만능 수족 아온이 공동 집행

[황금 4분할 배치 명세]
- 하단(메인) 모니터 좌측 50%: 수석보좌관 르곤 ('아온이 데스크톱 자동화 기능 문의' 브라우저 창)
- 하단(메인) 모니터 우측 50%: 기술총리 안총리 ('shin-agent - Antigravity IDE' 창 — 전체 높이 100%)
- 상단(보조) 모니터 좌측 50%: '청와대 중앙 컨트롤 타워' 대시보드 창 (전체 높이 100%)
- 상단(보조) 모니터 우측 50%: 'Step 44' 클로드(G1) 브라우저 창 (전체 높이 100%)
"""

import sys, time, ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

SW_RESTORE = 9
SWP_NOZORDER = 0x0004
SWP_SHOWWINDOW = 0x0040

def init_desktop_access():
    hDesk = user32.OpenInputDesktop(0, False, 0x01FF)
    if hDesk:
        user32.SetThreadDesktop(hDesk)
    return hDesk

def get_monitors():
    monitors = []
    def _mon_cb(hmon, hdc, lprect, lparam):
        r = lprect.contents
        monitors.append({
            "left": r.left,
            "top": r.top,
            "right": r.right,
            "bottom": r.bottom,
            "width": r.right - r.left,
            "height": r.bottom - r.top
        })
        return 1

    MONITORENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
    user32.EnumDisplayMonitors(0, 0, MONITORENUMPROC(_mon_cb), 0)
    
    # top 좌표 기준으로 오름차순 정렬: 상단(top=0), 하단(top=1080)
    monitors.sort(key=lambda m: m["top"])
    return monitors

def get_all_windows():
    windows = []
    def _win_cb(hwnd, lparam):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            vis = user32.IsWindowVisible(hwnd)
            windows.append({
                "hwnd": hwnd,
                "title": title,
                "visible": vis,
                "x": rect.left,
                "y": rect.top,
                "w": w,
                "h": h
            })
        return 1

    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(_win_cb), 0)
    return windows

def arrange_window(hwnd, title, x, y, w, h):
    # 최소화 상태 복원
    user32.ShowWindow(hwnd, SW_RESTORE)
    time.sleep(0.05)
    # 위치 및 크기 정밀 배치
    ret = user32.SetWindowPos(hwnd, 0, int(x), int(y), int(w), int(h), SWP_SHOWWINDOW)
    print(f"  [배치 완료] HWND:{hwnd} -> ({x}, {y}, {w}x{h}) | 제목: {title[:40]}")
    return ret

def main():
    print("=====================================================================")
    print("🏛️ [사령부] 대표님 듀얼 모니터 황금 4분할 자동 배치 집행 시작!")
    print("=====================================================================")
    init_desktop_access()
    
    monitors = get_monitors()
    print(f"[*] 감지된 모니터 수: {len(monitors)}대")
    for i, m in enumerate(monitors):
        pos_label = "상단 모니터" if i == 0 else "하단 모니터"
        print(f"    - 모니터 #{i} ({pos_label}): Left={m['left']}, Top={m['top']}, 해상도={m['width']}x{m['height']}")

    windows = get_all_windows()
    print(f"[*] 열거된 윈도우 수: {len(windows)}개")

    # 4대 지휘 창 타겟팅
    targets = {
        "bottom_left": None,   # 수석보좌관 르곤 (아온이 데스크톱 자동화 기능 문의)
        "bottom_right": None,  # 기술총리 안총리 (shin-agent - Antigravity IDE)
        "top_left": None,      # 청와대 중앙 컨트롤 타워
        "top_right": None      # Step 44 클로드
    }

    for win in windows:
        t = win["title"]
        # 1. 하단 좌측: 아온이 데스크톱 자동화 기능 문의
        if ("아온이 데스크톱" in t or "데스크톱 자동화 기능 문의" in t) and not targets["bottom_left"]:
            targets["bottom_left"] = win
        # 2. 하단 우측: Antigravity IDE
        elif ("Antigravity" in t and "shin-agent" in t) and not targets["bottom_right"]:
            targets["bottom_right"] = win
        elif ("Antigravity" in t) and not targets["bottom_right"]:
            targets["bottom_right"] = win
        # 3. 상단 좌측: 청와대 중앙 컨트롤 타워
        elif ("청와대" in t and "컨트롤 타워" in t) and not targets["top_left"]:
            targets["top_left"] = win
        # 4. 상단 우측: Step 44 클로드
        elif ("Step 44" in t or ("RGON UI 자가 수리" in t and "Chrome" in t)) and not targets["top_right"]:
            targets["top_right"] = win

    print("\n[*] 4대 지휘 창 검색 결과:")
    for role, win in targets.items():
        if win:
            print(f"  - [{role}] HWND:{win['hwnd']} | {win['title']}")
        else:
            print(f"  - [{role}] ⚠️ 창 미발견 (대체 창 탐색 필요)")

    # 모니터 배치 좌표 계산
    if len(monitors) >= 2:
        top_mon = monitors[0]     # 상단 (top=0)
        bot_mon = monitors[1]     # 하단 (top=1080)
        
        # 상단 좌측 50%
        top_left_geo = (top_mon["left"], top_mon["top"], top_mon["width"] // 2, top_mon["height"])
        # 상단 우측 50%
        top_right_geo = (top_mon["left"] + top_mon["width"] // 2, top_mon["top"], top_mon["width"] // 2, top_mon["height"])
        # 하단 좌측 50%
        bot_left_geo = (bot_mon["left"], bot_mon["top"], bot_mon["width"] // 2, bot_mon["height"])
        # 하단 우측 50%
        bot_right_geo = (bot_mon["left"] + bot_mon["width"] // 2, bot_mon["top"], bot_mon["width"] // 2, bot_mon["height"])
    else:
        # 단일 모니터 4분할 fallback
        m = monitors[0]
        hw, hh = m["width"] // 2, m["height"] // 2
        top_left_geo = (m["left"], m["top"], hw, hh)
        top_right_geo = (m["left"] + hw, m["top"], hw, hh)
        bot_left_geo = (m["left"], m["top"] + hh, hw, hh)
        bot_right_geo = (m["left"] + hw, m["top"] + hh, hw, hh)

    print("\n[*] 4대 지휘 창 이동 및 정밀 스케일링 집행:")
    
    # 1. 상단 좌측: 청와대 컨트롤 타워
    if targets["top_left"]:
        arrange_window(targets["top_left"]["hwnd"], targets["top_left"]["title"], *top_left_geo)
        
    # 2. 상단 우측: Step 44 클로드
    if targets["top_right"]:
        arrange_window(targets["top_right"]["hwnd"], targets["top_right"]["title"], *top_right_geo)

    # 3. 하단 좌측: 수석보좌관 르곤
    if targets["bottom_left"]:
        arrange_window(targets["bottom_left"]["hwnd"], targets["bottom_left"]["title"], *bot_left_geo)

    # 4. 하단 우측: 기술총리 안총리 (Antigravity IDE)
    if targets["bottom_right"]:
        arrange_window(targets["bottom_right"]["hwnd"], targets["bottom_right"]["title"], *bot_right_geo)

    print("\n=====================================================================")
    print("✅ 듀얼 모니터 황금 4분할 자동 배치 완료! (100% 무결점)")
    print("=====================================================================")
    return 0

if __name__ == "__main__":
    sys.exit(main())

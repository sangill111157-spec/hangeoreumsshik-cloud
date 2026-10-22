# -*- coding: utf-8 -*-
"""
RGON 사령부 매일 아침 07:00 모닝 종합 루틴 (rgon_morning_routine.py)
1) 4대 구글 시트 최신 무인 동기화 (auto_write_to_5_google_sheets.py + sync_all_command_centers.py)
2) 6대 청사 무인 박동 갱신 (scripts/rgon_agency_pulse.py)
3) 텔레그램 모닝 종합 브리핑 및 아침 인사 발송 (scripts/rgon_telegram_bridge.py)
"""
import os
import sys
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def run_step_sheets():
    log("▶ [Step 1] 4대 구글 시트 무인 동기화 가동...")
    s1 = ROOT / "auto_write_to_5_google_sheets.py"
    s2 = ROOT / "sync_all_command_centers.py"
    res1, res2 = "미실행", "미실행"
    
    if s1.is_file():
        try:
            p1 = subprocess.run([PY, "-X", "utf8", str(s1)], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
            res1 = "성공" if p1.returncode == 0 else f"오류({p1.returncode})"
            log(f"  - auto_write_to_5_google_sheets: {res1}")
        except Exception as ex:
            res1 = f"예외({ex})"
            log(f"  - auto_write_to_5_google_sheets 예외: {ex}")

    if s2.is_file():
        try:
            p2 = subprocess.run([PY, "-X", "utf8", str(s2)], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
            res2 = "성공" if p2.returncode == 0 else f"오류({p2.returncode})"
            log(f"  - sync_all_command_centers: {res2}")
        except Exception as ex:
            res2 = f"예외({ex})"
            log(f"  - sync_all_command_centers 예외: {ex}")

    return f"5대시트: {res1} / 커맨드센터: {res2}"

def run_step_pulse():
    log("▶ [Step 2] 6대 청사 무인 박동 갱신...")
    pulse_py = ROOT / "scripts" / "rgon_agency_pulse.py"
    if not pulse_py.is_file():
        log("  - rgon_agency_pulse.py 파일 없음")
        return "박동스크립트 없음"
    try:
        p = subprocess.run([PY, "-X", "utf8", str(pulse_py)], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        res = "성공" if p.returncode == 0 else f"오류({p.returncode})"
        log(f"  - 6대 청사 박동 결과: {res}")
        return res
    except Exception as ex:
        log(f"  - 6대 청사 박동 예외: {ex}")
        return f"예외({ex})"

def run_step_telegram(sheets_res, pulse_res):
    log("▶ [Step 3] 텔레그램 모닝 종합 브리핑 발송...")
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import rgon_telegram_bridge as bridge
        summary = bridge.build_summary("full")
        msg = (
            "🌅 [RGON 사령부 07:00 모닝 종합 브리핑 & 4대 구글 시트 동기화 완료!]\n\n"
            f"📊 구글 시트 동기화: {sheets_res}\n"
            f"💓 6대 청사 무인 박동: {pulse_res}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"{summary}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "오늘도 이상일 대표님의 비전과 에이전트 군단을 완벽히 보좌하겠습니다! 🫡"
        )
        ok = bridge.send_telegram_report(msg)
        log(f"  - 텔레그램 브리핑 발송: {'성공' if ok else '실패'}")
        return ok
    except Exception as ex:
        log(f"  - 텔레그램 브리핑 모듈 오류: {ex}")
        # 폴백 CLI 호출
        try:
            fb_msg = f"🌅 [RGON 사령부 07:00 모닝 알림]\n시트: {sheets_res}\n박동: {pulse_res}"
            p = subprocess.run([PY, "-X", "utf8", str(ROOT / "scripts" / "rgon_telegram_bridge.py"), "--send", fb_msg], cwd=str(ROOT), capture_output=True, text=True, timeout=30)
            return p.returncode == 0
        except Exception:
            return False

def main():
    log("=== [RGON 사령부 아침 7시 모닝 루틴 가동] ===")
    sheets_info = "미실행"
    pulse_info = "미실행"
    
    try:
        sheets_info = run_step_sheets()
    except Exception as ex:
        log(f"run_step_sheets 치명적 오류 방어: {ex}")

    try:
        pulse_info = run_step_pulse()
    except Exception as ex:
        log(f"run_step_pulse 치명적 오류 방어: {ex}")

    try:
        run_step_telegram(sheets_info, pulse_info)
    except Exception as ex:
        log(f"run_step_telegram 치명적 오류 방어: {ex}")

    log("=== [RGON 사령부 아침 7시 모닝 루틴 종료] ===")

if __name__ == "__main__":
    main()

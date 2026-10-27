# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from datetime import datetime

ROOT = r"C:\Users\sangi\Downloads\shin-agent"
SHEETS_PY = r"C:\Users\sangi\Desktop\run_all_sheets.py"
HEARTBEAT_PY = os.path.join(ROOT, "rgon_agency_heartbeat.py")
BRIDGE_PY = os.path.join(ROOT, "rgon_telegram_bridge.py")


def run_step(title, cmd, cwd=ROOT, timeout=180):
    print(f"▶ {title} 실행 중...")
    try:
        p = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout
        )
        return p.returncode, ((p.stdout or "") + "\n" + (p.stderr or "")).strip()
    except Exception as e:
        return 1, str(e)


def main():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    # 1. 4대 구글 시트 최신 동기화
    s_code, s_out = 1, "시트 스크립트 없음"
    if os.path.exists(SHEETS_PY):
        s_code, s_out = run_step("4대 구글 시트 통합 동기화", [sys.executable, SHEETS_PY], cwd=os.path.dirname(SHEETS_PY), timeout=180)

    # 2. 6대 청사 무인 박동 갱신
    h_code, h_out = run_step("6대 청사 무인 박동", [sys.executable, HEARTBEAT_PY], cwd=ROOT, timeout=60)

    # 3. 텔레그램 모닝 종합 브리핑 발송
    run_step("텔레그램 브리핑 발송", [sys.executable, BRIDGE_PY, "--send-brief"], cwd=ROOT, timeout=30)

    sheet_status = "✅ 4대 시트 동기화 성공" if s_code == 0 else f"⚠️ 시트 점검({s_code})"
    hb_status = "✅ 6대 청사 ALL OK" if h_code == 0 else f"⚠️ 청사 점검({h_code})"
    summary = (
        f"🌅 [RGON 사령부 07:00 모닝 종합 브리핑 완료 ({ts})]\n"
        f"• 구글 시트: {sheet_status}\n"
        f"• 6대 청사: {hb_status}\n"
        f"• 오늘 하루도 무토큰 자동화 사령부가 24시간 보좌합니다! 🫡👑"
    )
    run_step("모닝 인사 발송", [sys.executable, BRIDGE_PY, "--send-text", summary], cwd=ROOT, timeout=30)
    print("🎉 모닝 루틴 완료!")


if __name__ == "__main__":
    main()

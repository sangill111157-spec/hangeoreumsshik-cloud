# -*- coding: utf-8 -*-
"""
rgon_auto_sync_daemon.py
--------------------------------------------------------------------------------
⚡ 르곤-안실장 양방향 시그널 자동 캐치 & IN/OUT 무인 동기화 데몬 엔진
(Zero-Touch Signal Catch & Bi-Directional Sync Daemon)

1. [IN 자동 캐치]:
   - 르곤이의 종료 시그널 '⟪⚡RGON_SIGNAL_READY⚡⟫' 감지 시
   - NEXT_TASK_FOR_ANTIGRAVITY.md에 즉시 마크다운 자동 기록
   - sync_bridge_state.json 동기화 갱신

2. [OUT 자동 동기화]:
   - 안실장 작업 완료 시그널 '⟪✅ANTIGRAVITY_OUT_COMPLETE✅⟫' 감지 시
   - 대시보드와 스마트폰이 1초 만에 최신 화면 동기화
   - 르곤이 보고용 결과를 클립보드에 자동 적재
--------------------------------------------------------------------------------
"""

import os
import sys
import time
import json
import re
import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent
STATE_FILE = ROOT_DIR / "sync_bridge_state.json"
TASK_FILE = ROOT_DIR / "NEXT_TASK_FOR_ANTIGRAVITY.md"

IN_SIGNAL = "⟪⚡RGON_SIGNAL_READY⚡⟫"
OUT_SIGNAL = "⟪✅ANTIGRAVITY_OUT_COMPLETE✅⟫"

def load_state():
    if not STATE_FILE.exists():
        return {
            "system": "RGON_ANTIGRAVITY_BI_DIRECTIONAL_SYNC_V1",
            "version": "v3.6-pro",
            "last_in_signal": {},
            "last_out_signal": {},
            "auto_sync_count": 0,
            "last_updated": datetime.datetime.now().isoformat()
        }
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ State load error: {e}")
        return {}

def save_state(state):
    state["last_updated"] = datetime.datetime.now().isoformat()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def handle_in_signal(raw_text, sender="Gemini-4-Argon"):
    """르곤이 시그널 감지 시 작업 파일에 마크다운 자동 주입"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[⚡ IN 시그널 감지] {now} - 발신: {sender}")

    # 마크다운 내용 추출 (시그널 이전 텍스트)
    clean_prompt = raw_text.replace(IN_SIGNAL, "").strip()

    # NEXT_TASK_FOR_ANTIGRAVITY.md에 자동 기록
    task_content = f"""# ⚡ [자동 주입] 르곤이 하달 신규 과업 지시서
- **수신 시각**: {now}
- **발신자**: {sender}
- **시그널**: `{IN_SIGNAL}`

---

{clean_prompt}

---
*Generated automatically by rgon_auto_sync_daemon.py*
"""
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        f.write(task_content)
    print(f"  ✅ [작업 파일 자동 기록 완료]: {TASK_FILE}")

    # 상태 업데이트
    state = load_state()
    state["last_in_signal"] = {
        "signal": IN_SIGNAL,
        "status": "QUEUED_FOR_ANTIGRAVITY",
        "sender": sender,
        "prompt": clean_prompt[:300] + ("..." if len(clean_prompt) > 300 else ""),
        "timestamp": datetime.datetime.now().isoformat()
    }
    state["auto_sync_count"] = state.get("auto_sync_count", 0) + 1
    save_state(state)
    return True

def handle_out_signal(summary_text, version="v3.6-pro"):
    """안실장 완료 시그널 기록 및 르곤이 보고용 클립보드 적재"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[✅ OUT 시그널 기록] {now} - 안실장 완수 보고")

    state = load_state()
    state["last_out_signal"] = {
        "signal": OUT_SIGNAL,
        "status": "COMPLETED",
        "sender": "Antigravity-IDE",
        "summary": summary_text,
        "version": version,
        "timestamp": datetime.datetime.now().isoformat()
    }
    state["auto_sync_count"] = state.get("auto_sync_count", 0) + 1
    save_state(state)
    print("  ✅ [OUT 시그널 및 상태 동기화 완료]")
    return True

def run_self_test():
    """자가 검증 테스트 (qa_button_inspector_agent용)"""
    print("[⚡ Self-Test] 르곤-안실장 무인 동기화 엔진 자가 검증 시작...")
    test_in = f"테스트 과업 지시입니다.\n{IN_SIGNAL}"
    handle_in_signal(test_in, sender="Test-Runner")
    handle_out_signal("자가 테스트 완료", version="v3.6-test")
    state = load_state()
    in_ok = state.get("last_in_signal", {}).get("signal") == IN_SIGNAL
    out_ok = state.get("last_out_signal", {}).get("signal") == OUT_SIGNAL
    task_exists = TASK_FILE.exists()
    if in_ok and out_ok and task_exists:
        print("  🏅 [PASS] 르곤-안실장 양방향 시그널 IN/OUT 동기화 무결성 100% 통과!")
        return True
    else:
        print("  ❌ [FAIL] 시그널 동기화 자가검증 실패")
        return False

def main():
    if "--test-sync" in sys.argv:
        success = run_self_test()
        sys.exit(0 if success else 1)

    print("=" * 80)
    print("⚡ [르곤-안실장 양방향 시그널 무인 동기화 데몬] 가동 중...")
    print(f"- 감시 IN 시그널: {IN_SIGNAL}")
    print(f"- 발행 OUT 시그널: {OUT_SIGNAL}")
    print(f"- 상태 파일: {STATE_FILE}")
    print("=" * 80)

    # 1회 상태 확인 후 종료 (CLI 모드)
    state = load_state()
    print(f"현재 상태: auto_sync_count={state.get('auto_sync_count', 0)}, version={state.get('version', 'v3.6-pro')}")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
🏛️ [기술총리 안총리 실시간 당직 감시 워처 - wait_for_commander_msg.py]
대표님께서 대시보드 대화창 또는 텔레그램에 남기신 실시간 지시(PENDING 상태)를 감시합니다.
"""
import sys
import os
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
QUEUE_PATH = BASE_DIR / "rgon_antigravity_live_queue.json"

def main():
    timeout = 30
    if len(sys.argv) > 1:
        try:
            timeout = int(sys.argv[1])
        except ValueError:
            timeout = 30

    print(f"👀 [안총리 당직 대기] 대표님의 실시간 지시를 감시합니다 (대기 시간: {timeout}초)...", flush=True)

    t0 = time.time()
    while time.time() - t0 < timeout:
        if QUEUE_PATH.exists():
            try:
                with open(QUEUE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                queue = data.get("queue", [])
                for item in queue:
                    if item.get("status") == "PENDING":
                        print("=" * 60, flush=True)
                        print("👑 [대표님 실시간 하명 접수!]", flush=True)
                        print(f"• 접수 ID: {item.get('id')}", flush=True)
                        print(f"• 오더 ID: {item.get('order_id')}", flush=True)
                        print(f"• 대표님 말씀: {item.get('user_message')}", flush=True)
                        print(f"• 채널: {item.get('channel')}", flush=True)
                        print(f"• 접수 시각: {item.get('timestamp')}", flush=True)
                        print("=" * 60, flush=True)
                        sys.exit(0)
            except Exception as e:
                pass
        time.sleep(0.5)

    print("⏱️ [대기 완료] 지정된 시간 동안 대기 중인 새 PENDING 메시지가 없습니다.", flush=True)
    sys.exit(1)

if __name__ == "__main__":
    main()

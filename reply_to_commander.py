# -*- coding: utf-8 -*-
"""
⚡ [기술총리 안총리 직접 회신 도구 - reply_to_commander.py]
안총리가 직접 작성한 명쾌한 답변을 rgon_antigravity_live_queue.json에 등록하여
대시보드 대화창과 텔레그램에 실시간 직통으로 전달합니다.
"""
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
QUEUE_PATH = BASE_DIR / "rgon_antigravity_live_queue.json"
STREAM_PATH = BASE_DIR / "hq_kakao_tg_live_stream.json"

def main():
    if len(sys.argv) < 2:
        print("사용법: python reply_to_commander.py \"<답변 내용>\" [msg_id] [speaker]")
        sys.exit(1)

    reply_text = sys.argv[1]
    target_msg_id = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    speaker = sys.argv[3] if len(sys.argv) > 3 else "⚡ 기술총리 안총리 (Antigravity 직접 답변)"

    if not QUEUE_PATH.exists():
        data = {"version": "v11.58-AON-LIVE-BRAIN-MOTION", "queue": []}
    else:
        try:
            with open(QUEUE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"version": "v11.58-AON-LIVE-BRAIN-MOTION", "queue": []}

    queue = data.setdefault("queue", [])

    matched_item = None
    if target_msg_id:
        for it in queue:
            if it.get("id") == target_msg_id:
                matched_item = it
                break
    else:
        # PENDING 상태인 가장 최근 아이템 찾기
        for it in reversed(queue):
            if it.get("status") == "PENDING":
                matched_item = it
                break
        # 없으면 가장 최근 아이템
        if not matched_item and queue:
            matched_item = queue[-1]

    if not matched_item:
        # 큐가 비어있는 경우 새로 생성
        msg_id = f"ag-msg-{int(time.time()*1000)}"
        matched_item = {
            "id": msg_id,
            "order_id": "ORD-LIVE",
            "status": "PENDING",
            "user_message": "(수동 직통 발송)",
            "channel": "ALL",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        queue.append(matched_item)

    # 답변 업데이트
    matched_item["status"] = "ANSWERED"
    matched_item["antigravity_reply"] = reply_text
    matched_item["speaker"] = speaker
    matched_item["answered_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # hq_kakao_tg_live_stream.json에도 추가
    try:
        stream_data = []
        if STREAM_PATH.exists():
            with open(STREAM_PATH, "r", encoding="utf-8") as f:
                stream_data = json.load(f)
        stream_data.append({
            "order_id": matched_item.get("order_id", "ORD-LIVE"),
            "sender_name": speaker,
            "text": reply_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        with open(STREAM_PATH, "w", encoding="utf-8") as f:
            json.dump(stream_data[-50:], f, ensure_ascii=False, indent=2)
    except Exception as e:
        pass

    # 텔레그램 실제 발송 시도
    try:
        from rgon_kakao_tg_live_server import send_real_telegram
        tg_text = f"{speaker}:\n{reply_text}"
        channel = matched_item.get("channel", "ALL")
        target_bot = 'bot3' if channel == 'NVDA' else ('bot1' if channel == 'LUMI' else 'bot2')
        send_real_telegram(target_bot, tg_text)
    except Exception:
        pass

    print("=" * 60)
    print("⚡ [안총리 직통 답변 등록 완료!]")
    print(f"• 대상 메시지 ID: {matched_item.get('id')}")
    print(f"• 오더 ID: {matched_item.get('order_id')}")
    print(f"• 발신자: {speaker}")
    print(f"• 답변 내용:\n{reply_text}")
    print("=" * 60)

if __name__ == "__main__":
    main()

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\trading\package\nvda_trading_system\backend')

from app.services.telegram_notifier import format_telegram_alert, get_telegram_notifier, TelegramMessage

# Test formatting of all 3 tiers
urgent_msg = format_telegram_alert(
    level="긴급",
    is_paper=True,
    title="손절 감시 계좌 조회 실패 (연속 3회)",
    impact="손절 감시가 3분째 일시 중단된 상태입니다.",
    action="브로커 OpenAPI 및 모의서버 응답 상태를 확인하십시오.",
    tech_info="ACCOUNT_STATE_FAIL: Event loop is closed *critical_marker*"
)

warning_msg = format_telegram_alert(
    level="주의",
    is_paper=True,
    title="장중 정기 종목 스캔 지연",
    impact="워치리스트 10개 종목 스캔 중 시세 수신이 5초 지연되었습니다.",
    action="조치 불필요, 자동 재시도 중",
    tech_info="TIMEOUT_WARN: KIS price inquiry delayed (retry 1/3)"
)

info_msg = format_telegram_alert(
    level="정보",
    is_paper=True,
    title="손절 감시 정상 복구 완료",
    impact="브로커 계좌 조회가 복구되어 손절 감시가 정상 작동 중입니다.",
    action="조치 불필요, 자동 감시 중",
    tech_info="중단 시간: 약 3분 (180초)"
)

heartbeat_msg = format_telegram_alert(
    level="정보",
    is_paper=True,
    title="시스템 정상 작동 중 - 일일 마감 요약",
    impact="오늘 모든 예약 작업이 정상 수행되었습니다.",
    action="특이사항 없음",
    tech_info="일일 수익률: +0.00% | 총 평가금액: $100,000.00"
)

print("=== [1. 긴급 알림 서식] ===")
print(urgent_msg)
print("\n=== [2. 주의 알림 서식] ===")
print(warning_msg)
print("\n=== [3. 정보 알림 (복구) 서식] ===")
print(info_msg)
print("\n=== [4. 정보 알림 (생존신호) 서식] ===")
print(heartbeat_msg)

# Try actual sending through notifier if credentials configured
notifier = get_telegram_notifier()
if notifier.enabled:
    print("\nAttempting actual send to Telegram...")
    res = notifier.send_message_sync(TelegramMessage(chat_id=notifier.chat_id, text=urgent_msg, parse_mode="HTML"))
    print(f"Telegram send result: {res}")
else:
    print("\nTelegram notifier disabled (mock mode, credentials not configured in env)")

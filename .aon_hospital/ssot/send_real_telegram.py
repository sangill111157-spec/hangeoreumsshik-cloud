import sys
import os
import requests
import html

# Load .env
env_path = r"C:\trading\package\nvda_trading_system\backend\.env"
bot_token = None
chat_id = None
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                bot_token = line.strip().split("=", 1)[1]
            elif line.startswith("TELEGRAM_CHAT_ID="):
                chat_id = line.strip().split("=", 1)[1]

print(f"Loaded credentials: Token={'YES' if bot_token else 'NO'}, ChatID={'YES' if chat_id else 'NO'}")

def format_telegram_alert(
    level: str,          # "긴급", "주의", "정보"
    is_paper: bool,      # True: "모의", False: "실전"
    title: str,          # 무슨 일인지 한 줄
    impact: str,         # 지금 무엇이 멈췄는지 (예: "손절 감시가 3분째 멈춤")
    action: str,         # 대표가 해야 할 것, 또는 "조치 불필요, 자동 재시도 중"
    tech_info: str = ""  # 오류 코드/원문 (맨 아래 한 줄)
) -> str:
    level_tag = f"[{level}]"
    mode_tag = "[모의]" if is_paper else "[실전]"

    msg = (
        f"<b>{level_tag}{mode_tag} {html.escape(title)}</b>\n"
        f"<b>영향:</b> {html.escape(impact)}\n"
        f"<b>할 일:</b> {html.escape(action)}"
    )
    if tech_info:
        msg += f"\n<b>기술 정보:</b> <code>{html.escape(tech_info)}</code>"
    return msg

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

messages = [
    ("긴급", format_telegram_alert(
        level="긴급",
        is_paper=True,
        title="손절 감시 계좌 조회 실패 (연속 3회)",
        impact="손절 감시가 3분째 일시 중단되었습니다.",
        action="브로커 OpenAPI 및 모의서버 응답 상태를 확인하십시오.",
        tech_info="ACCOUNT_STATE_FAIL: Event loop is closed"
    )),
    ("주의", format_telegram_alert(
        level="주의",
        is_paper=True,
        title="장중 정기 종목 스캔 지연",
        impact="워치리스트 종목 스캔 중 시세 수신이 5초 지연되었습니다.",
        action="조치 불필요, 자동 재시도 중",
        tech_info="TIMEOUT_WARN: KIS price inquiry delayed (retry 1/3)"
    )),
    ("정보", format_telegram_alert(
        level="정보",
        is_paper=True,
        title="시스템 정상 작동 중 (미국장 개장 전 생존 신호)",
        impact="모든 시스템 데몬 및 감시 스케줄러가 정상 가동 중입니다.",
        action="특이사항 없음",
        tech_info="모의 서버 연결 정상 | 손절 감시 대기 중 | 서머타임 반영 (개장 22:30 KST)"
    )),
    ("복구", format_telegram_alert(
        level="정보",
        is_paper=True,
        title="손절 감시 정상 복구 완료",
        impact="브로커 계좌 조회가 복구되어 손절 감시가 정상 작동 중입니다.",
        action="조치 불필요, 자동 감시 중",
        tech_info="중단 시간: 약 3분 (180초)"
    ))
]

for label, text in messages:
    resp = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
    print(f"[{label}] Status: {resp.status_code}, Response: {resp.text}")

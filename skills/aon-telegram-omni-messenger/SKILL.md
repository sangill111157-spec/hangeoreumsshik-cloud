---
name: aon-telegram-omni-messenger
description: 제32기관 아온 듀얼 텔레그램·카톡형 실시간 양방향 메신저 엔진 스킬. 대표님 기존 사용 중인 2개 텔레그램(1호기 @hangaeum_lumi_bot, 2호기 @sangi_ai_secretary_bot) 실시간 연동, 카톡식 실시간 읽음 증명, 지시서 수신 공식 원장(#ORD) 영구 봉인.
---

# AON Telegram Omni Messenger (#52)

- **기관:** 제32기관 아온 듀얼 텔레그램·카톡형 실시간 양방향 메신저 (`rgon_aon_telegram_omni_messenger.py`)
- **버전:** `v11.55-AON-TELEGRAM-MESSENGER`
- **항체:** `R56_TELEGRAM_KAKAO_BIDIRECTIONAL_LIVE_MESSENGER_LOCK` (`R1~R56`)
- **주역:** `#58 태위택(兌爲澤) — 기쁨과 화답, 두 연못이 이어져 끊임없이 소통하는 대길상`
- **역할:**
  1. 대표님 2대 텔레그램 봇(루미비서, Sangi AI 비서) 듀얼 실시간 양방향 핫라인 관리.
  2. 카톡식 실시간 읽음/접수 증명 (`1 (전송중)` ➔ `✔✔ 읽음 (접수 #ORD-XXX · TG 발송 완료)`).
  3. 실시간 도착 지시 공식 원장(`commander_live_orders.json`, `COMMANDER_INBOX.md`) SHA-256 봉인.
  4. 보안 헌법 R2: 실전 토큰/Chat ID의 Git 노출 0% 엄수 (로컬 `.env.telegram_local` 격리).

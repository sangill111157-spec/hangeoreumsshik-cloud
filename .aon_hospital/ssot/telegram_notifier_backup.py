from app.core.masking import mask_sensitive_info
"""
Telegram 알림 모듈
매수/매도 신호 발생 시 Telegram 메시지 전송
"""

import httpx
import asyncio
import logging
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)


@dataclass
class TelegramMessage:
    """텔레그램 메시지"""
    chat_id: str
    text: str
    parse_mode: str = "Markdown"

    def __post_init__(self):
        if isinstance(self.text, str):
            self.text = mask_sensitive_info(self.text)


class TelegramNotifier:
    """
    텔레그램 알림 전송기

    사용법:
    1. Telegram BotFather에서 봇 생성
    2. Bot API Token 획득
    3. @userinfobot으로 chat_id 획득
    4. 환경변수 설정:
       - TELEGRAM_BOT_TOKEN
       - TELEGRAM_CHAT_ID
    """

    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.enabled = bool(self.bot_token and self.chat_id)

        if not self.enabled:
            logger.warning("Telegram notifier disabled: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        else:
            logger.info("Telegram notifier enabled")

    async def send_message(self, message: TelegramMessage) -> bool:
        """
        메시지 전송

        Args:
            message: TelegramMessage 객체

        Returns:
            성공 여부
        """
        if message and hasattr(message, "text") and message.text:
            message.text = mask_sensitive_info(message.text)
        if not self.enabled:
            logger.debug("Telegram disabled, skipping message")
            return False

        url = f"{self.BASE_URL}{self.bot_token}/sendMessage"

        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                payload = {
                    "chat_id": message.chat_id,
                    "text": message.text,
                    "parse_mode": message.parse_mode or ""
                }
                response = await client.post(url, json=payload)

                if response.status_code == 200:
                    logger.info("Telegram message sent successfully")
                    return True
                elif response.status_code == 400 and message.parse_mode:
                    # Markdown 파싱 실패(400) 시 parse_mode를 제거하여 일반 텍스트로 1회 재시도 (알림 유실 방지)
                    logger.warning(f"Telegram Markdown parse failed (400), retrying in plain text: {response.text}")
                    payload["parse_mode"] = ""
                    retry_resp = await client.post(url, json=payload)
                    if retry_resp.status_code == 200:
                        logger.info("Telegram message sent successfully on fallback retry")
                        return True
                    else:
                        logger.error(f"Telegram API retry error: {retry_resp.status_code} - {retry_resp.text}")
                        return False
                else:
                    logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                    return False

            except Exception as e:
                logger.error(f"Failed to send Telegram message: {str(e)}")
                return False

    def send_message_sync(self, message: TelegramMessage) -> bool:
        """동기 버전 메시지 전송"""
        return asyncio.run(self.send_message(message))

    async def send_signal_alert(
        self,
        signal: str,
        confidence: int,
        price: float,
        ticker: str = "NVDA",
        market: str = "US",
        reason: str = ""
    ) -> bool:
        """
        매수/매도 신호 알림 전송

        Args:
            signal: 신호 (STRONG_BUY, BUY, SELL, STRONG_SELL)
            confidence: 신뢰도
            price: 현재가
            ticker: 티커 (기본값: NVDA)
            market: 시장 (US/KR)
            reason: 신호 이유
        """
        emoji = self._get_signal_emoji(signal)
        signal_text = self._get_signal_text(signal)
        currency = "₩" if market == "KR" else "$"
        market_label = "KRX" if market == "KR" else "NASDAQ"

        message_text = f"""
{emoji} *{ticker} 신호 알림* ({market_label})

📊 신호: *{signal_text}*
🎯 신뢰도: *{confidence}%*
💵 현재가: *{currency}{price:.2f}*

📝 이유:
{reason}

⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

        message = TelegramMessage(
            chat_id=self.chat_id,
            text=message_text
        )

        return await self.send_message(message)

    async def send_order_notification(
        self,
        side: str,
        quantity: int,
        price: float,
        status: str,
        ticker: str = "NVDA",
        market: str = "US",
        order_id: str = ""
    ) -> bool:
        """
        주문 실행 알림 전송

        Args:
            side: buy/sell
            quantity: 수량
            price: 가격
            status: 상태
            ticker: 티커 (기본값: NVDA)
            market: 시장 (US/KR)
            order_id: 주문 ID
        """
        emoji = "🟢" if side.lower() == "buy" else "🔴"
        total = quantity * price
        currency = "₩" if market == "KR" else "$"
        market_label = "KRX" if market == "KR" else "NASDAQ"

        message_text = f"""
{emoji} *{ticker} 주문 {status}* ({market_label})

📈 주문: *{side.upper()}*
🔢 수량: *{quantity}주*
💵 가격: *{currency}{price:.2f}*
💰 총액: *{currency}{total:,.2f}*
{f'📋 주문ID: `{order_id}`' if order_id else ''}

⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

        message = TelegramMessage(
            chat_id=self.chat_id,
            text=message_text
        )

        return await self.send_message(message)

    async def send_investor_consensus(
        self,
        overall_signal: str,
        bull_count: int,
        bear_count: int,
        price: float,
        ticker: str = "NVDA",
        market: str = "US",
        details: str = ""
    ) -> bool:
        """
        투자자 합의 알림 전송

        Args:
            overall_signal: 종합 신호
            bull_count: 매수 신호 수
            bear_count: 매도 신호 수
            price: 현재가
            ticker: 티커 (기본값: NVDA)
            market: 시장 (US/KR)
            details: 상세 내용
        """
        emoji = self._get_signal_emoji(overall_signal)
        currency = "₩" if market == "KR" else "$"
        market_label = "KRX" if market == "KR" else "NASDAQ"

        message_text = f"""
📊 *5대 투자자 분석 결과* ({ticker})

{emoji} 종합 신호: *{overall_signal}*
💵 현재가: *{currency}{price:.2f}* ({market_label})

📈 매수: *{bull_count}명*
📉 매도: *{bear_count}명*

{details}

⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

        message = TelegramMessage(
            chat_id=self.chat_id,
            text=message_text
        )

        return await self.send_message(message)

    async def send_error_alert(
        self,
        error_type: str,
        error_message: str,
        context: str = ""
    ) -> bool:
        """
        에러 알림 전송

        Args:
            error_type: 에러 유형
            error_message: 에러 메시지
            context: 컨텍스트
        """
        message_text = f"""
⚠️ *NVDA Trading System Alert*

🚨 에러 유형: *{error_type}*
📝 메시지: {error_message}
{f'📋 컨텍스트: {context}' if context else ''}

⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

        message = TelegramMessage(
            chat_id=self.chat_id,
            text=message_text
        )

        return await self.send_message(message)

    def _get_signal_emoji(self, signal: str) -> str:
        """신호별 이모지 반환"""
        emoji_map = {
            "STRONG_BUY": "🟢🟢",
            "BUY": "🟢",
            "HOLD": "🟡",
            "SELL": "🔴",
            "STRONG_SELL": "🔴🔴"
        }
        return emoji_map.get(signal, "⚪")

    def _get_signal_text(self, signal: str) -> str:
        """신호 텍스트 반환"""
        text_map = {
            "STRONG_BUY": "강력한 매수",
            "BUY": "매수",
            "HOLD": "보유",
            "SELL": "매도",
            "STRONG_SELL": "강력한 매도"
        }
        return text_map.get(signal, "알 수 없음")

    # =============================================================================
    # 13F FILING NOTIFICATIONS (STEP 17)
    # =============================================================================

    async def send_13f_filing_alert(
        self,
        investor: str,
        quarter: str,
        new_positions: List[str] = None,
        increased_positions: List[str] = None,
        decreased_positions: List[str] = None,
        sold_out: List[str] = None
    ) -> bool:
        """
        13F Filing 알림 전송

        Args:
            investor: 투자자 이름
            quarter: 분기
            new_positions: 신규 매수 종목
            increased_positions: 증액 매수 종목
            decreased_positions:减持 종목
            sold_out: 완전 매도 종목
        """
        new_positions = new_positions or []
        increased_positions = increased_positions or []
        decreased_positions = decreased_positions or []
        sold_out = sold_out or []

        # Investor emoji mapping
        investor_emoji = {
            "Warren Buffett": "👑",
            "Ray Dalio": "🌍",
            "Jim Simons": "🧮"
        }
        emoji = investor_emoji.get(investor, "🏛️")

        message_text = f"""
{emoji} *13F 속보!*

🏛️ *{investor}* - {quarter}

{f"*신규 매수:* {', '.join(new_positions)}" if new_positions else ''}
{f"*增持:* {', '.join(increased_positions)}" if increased_positions else ''}
{f"*减持:* {', '.join(decreased_positions)}" if decreased_positions else ''}
{f"*완전 매도:* {', '.join(sold_out)}" if sold_out else ''}

⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

        message = TelegramMessage(
            chat_id=self.chat_id,
            text=message_text
        )

        return await self.send_message(message)

    async def send_overlap_buy_alert(
        self,
        ticker: str,
        investors: List[dict]
    ) -> bool:
        """
        겹치는 투자자 매수 알림

        Args:
            ticker: 종목 티커
            investors: 투자자 리스트
        """
        buy_signals = [i["Name"] for i in investors if i.get("transaction_type") in ["NEW", "INCREASED"]]

        if len(buy_signals) < 2:
            return False

        message_text = f"""
🔥 *겹침 매수 발견!*

📈 *{ticker}* - {len(buy_signals)}개 투자자 동시 매수!

👥 매수 투자자:
{chr(10).join(f"• {name}" for name in buy_signals)}

⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

        message = TelegramMessage(
            chat_id=self.chat_id,
            text=message_text
        )

        return await self.send_message(message)

    async def send_pod_signal_alert(
        self,
        buy_count: int,
        sell_count: int,
        pod_details: List[dict] = None
    ) -> bool:
        """
        멀티 Pod 동시 신호 알림

        Args:
            buy_count: 매수 신호 수
            sell_count: 매도 신호 수
            pod_details: Pod 상세
        """
        if buy_count < 3 and sell_count < 3:
            return False

        signal_type = "BUY" if buy_count >= 3 else "SELL"
        count = buy_count if buy_count >= 3 else sell_count
        emoji = "🟢" if signal_type == "BUY" else "🔴"

        message_text = f"""
{emoji} *Pod 신호 알림!*

🔥 *{count}개 Pod 동시 {signal_type} 신호!*

{'📈 매수 신호:' if signal_type == 'BUY' else '📉 매도 신호:'}
{chr(10).join(f"• {p['pod_name']}" for p in (pod_details or []) if signal_type in p.get('signal', 'HOLD'))}

⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

        message = TelegramMessage(
            chat_id=self.chat_id,
            text=message_text
        )

        return await self.send_message(message)

    async def send_master_signal_alert(
        self,
        master_score: float,
        signal: str,
        confidence: int,
        ticker: str = "NVDA",
        market: str = "US",
        components: List[dict] = None,
        recommendation: str = ""
    ) -> bool:
        """
        마스터 신호 알림

        Args:
            master_score: 마스터 점수
            signal: 신호
            confidence: 신뢰도
            ticker: 티커 (기본값: NVDA)
            market: 시장 (US/KR)
            components: 구성 요소
            recommendation: 추천
        """
        emoji = self._get_signal_emoji(signal)
        signal_text = self._get_signal_text(signal)
        market_label = "KRX" if market == "KR" else "NASDAQ"

        # 점수 게이지
        score_bar = "█" * int(master_score / 10) + "░" * (10 - int(master_score / 10))

        message_text = f"""
🎯 *마스터 신호 업데이트!* ({ticker})

{emoji} *{signal_text}* ({master_score:.0f}/100)
`{score_bar}`

🎯 신뢰도: *{confidence}%*
📍 시장: *{market_label}*

📊 구성 요소 점수:
{chr(10).join(f"• {c['name']}: {c['score']:.0f} ({c['signal']})" for c in (components or [])[:5])}

{f"💡 {recommendation}" if recommendation else ''}

⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

        message = TelegramMessage(
            chat_id=self.chat_id,
            text=message_text
        )

        return await self.send_message(message)


# =============================================================================
# SIGNAL CHANGE DETECTOR (신호 변경 감지)
# =============================================================================

class SignalChangeDetector:
    """
    신호 변경 감지 및 자동 알림
    이전 신호와 비교하여 변경되었을 때만 알림 전송
    """

    def __init__(self, notifier: TelegramNotifier):
        self.notifier = notifier
        self._last_signal: Optional[str] = None
        self._last_confidence: int = 0

    async def check_and_notify(
        self,
        new_signal: str,
        new_confidence: int,
        price: float,
        ticker: str = "NVDA",
        market: str = "US",
        reason: str = ""
    ) -> bool:
        """
        신호 변경 감지 및 알림 전송

        Args:
            new_signal: 새로운 신호
            new_confidence: 새로운 신뢰도
            price: 현재가
            ticker: 티커 (기본값: NVDA)
            market: 시장 (US/KR)
            reason: 이유

        Returns:
            알림이 전송되었는지 여부
        """
        # 신호 변경 감지
        signal_changed = self._last_signal != new_signal
        confidence_significant = abs(new_confidence - self._last_confidence) >= 10

        should_notify = signal_changed or confidence_significant

        if should_notify:
            logger.info(f"Signal change detected for {ticker}: {self._last_signal} -> {new_signal}")

            # 신호 변경 상세 내용
            change_detail = f"""
*신호 변경:* {self._get_signal_emoji(self._last_signal or 'HOLD')} {self._last_signal or 'N/A'} → {self._get_signal_emoji(new_signal)} {new_signal}
*신뢰도 변경:* {self._last_confidence}% → {new_confidence}%
            """.strip()

            await self.notifier.send_signal_alert(
                signal=new_signal,
                confidence=new_confidence,
                price=price,
                ticker=ticker,
                market=market,
                reason=change_detail
            )

            # 상태 업데이트
            self._last_signal = new_signal
            self._last_confidence = new_confidence

            return True

        return False

    def get_last_signal(self) -> Optional[str]:
        """마지막 신호 반환"""
        return self._last_signal

    def _get_signal_emoji(self, signal: str) -> str:
        """신호별 이모지 반환"""
        emoji_map = {
            "STRONG_BUY": "🟢🟢",
            "BUY": "🟢",
            "HOLD": "🟡",
            "SELL": "🔴",
            "STRONG_SELL": "🔴🔴"
        }
        return emoji_map.get(signal, "⚪")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_telegram_notifier() -> TelegramNotifier:
    """텔레그램 알림 생성"""
    return TelegramNotifier()


def create_signal_detector(notifier: TelegramNotifier = None) -> SignalChangeDetector:
    """신호 변경 감지 생성"""
    if notifier is None:
        notifier = create_telegram_notifier()
    return SignalChangeDetector(notifier)


# =============================================================================
# SINGLETON PATTERN
# =============================================================================

_telegram_notifier_instance: Optional[TelegramNotifier] = None


def get_telegram_notifier() -> TelegramNotifier:
    """Get singleton TelegramNotifier instance"""
    global _telegram_notifier_instance
    if _telegram_notifier_instance is None:
        _telegram_notifier_instance = create_telegram_notifier()
    return _telegram_notifier_instance


def send_telegram_alert(message: str) -> bool:
    """최상위 동기식 긴급 텔레그램 알림 전송 헬퍼 (Fail-safe, requests.post timeout=5s, settings SSOT)"""
    message = mask_sensitive_info(message)
    try:
        from app.core.config import settings
        import requests
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None) or os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None) or os.getenv('TELEGRAM_CHAT_ID')
        if not bot_token or not chat_id:
            logger.warning("Telegram alert skipped: missing bot token or chat ID")
            return False
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        resp = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
        return resp.status_code == 200
    except Exception as e:
        logger.warning(f"send_telegram_alert helper failed: {e}")
        return False

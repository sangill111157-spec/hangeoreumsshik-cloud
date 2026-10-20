# -*- coding: utf-8 -*-
import os, sys

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update app/services/scheduler.py
sched_p = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')
with open(sched_p, 'r', encoding='utf-8') as f:
    c = f.read()

# Add fields to __init__
old_init = '''        self._telegram_fail_count: int = 0
        self._telegram_timeout_sec: float = 3.0

        self._load_stop_loss_state()'''

new_init = '''        self._telegram_fail_count: int = 0
        self._telegram_timeout_sec: float = 3.0
        self._startup_ts: float = time.time()
        self._startup_window_sec: float = 60.0
        self._startup_suppressed_count: int = 0
        self._startup_summary_logged: bool = False

        self._load_stop_loss_state()'''

assert old_init in c, "old_init not found in scheduler.py"
c = c.replace(old_init, new_init)

# Add _is_restart_suppressed_message method and startup suppression check in _send_telegram
old_send = '''    def _send_telegram(self, message: str) -> Optional[bool]:
        """텔레그램 메시지 전송 (성공: True, 비활성: None, 실패: False 3-state 반환)
        [BACKLOG_1_VERIFIED_DELIVERY] 비동기 전송 확인 기반 마커 확정 체계:
        - 전송 성공 확인 시에만 True 반환 (마커 확정)
        - 실패/예외/타임아웃/루프 부재 시 False 반환 (마커 미확정 및 차회 재시도 보장)
        - 비활성 시 None 반환 (마커 확정으로 알림 비활성 환경 폭주 방지)
        """
        message = mask_sensitive_info(message)
        if not self.notifier_enabled or not self.notifier:
            logger.info("Telegram notifier disabled, skipping message")
            return None

        timeout = getattr(self, "_telegram_timeout_sec", 3.0)'''

new_send = '''    @staticmethod
    def _is_restart_suppressed_message(message: str) -> bool:
        """재기동 시 누적/재발신되는 블랙리스트 알림 감지 (실제 손절 주문/체결/트리거는 억제 제외)"""
        blacklist_keywords = [
            "긴급 손절 잠금 일일 리마인더",
            "LOCKED_TICKER_DAILY_REMINDER",
            "국내주식 손절 감시 불가",
            "KR_STOCK_STOP_LOSS_GUARD",
            "긴급 손절 감시 제외",
            "AVG_PRICE_ZERO_GUARD",
            "긴급 손절 재기동 보고",
            "RESTART_LOCK_REPORT",
            "stop_loss_state.json 상태 파일 로드 실패",
        ]
        return any(kw in message for kw in blacklist_keywords)

    def _send_telegram(self, message: str) -> Optional[bool]:
        """텔레그램 메시지 전송 (성공: True, 비활성: None, 실패: False 3-state 반환)
        [BACKLOG_1_VERIFIED_DELIVERY] 비동기 전송 확인 기반 마커 확정 체계:
        - 전송 성공 확인 시에만 True 반환 (마커 확정)
        - 실패/예외/타임아웃/루프 부재 시 False 반환 (마커 미확정 및 차회 재시도 보장)
        - 비활성 시 None 반환 (마커 확정으로 알림 비활성 환경 폭주 방지)
        """
        message = mask_sensitive_info(message)
        if not self.notifier_enabled or not self.notifier:
            logger.info("Telegram notifier disabled, skipping message")
            return None

        # [BACKLOG_2_STARTUP_SUPPRESSION] 기동 억제 창(Startup Suppression Window) 가드
        # 기동 후 60초 창 내에서 재기동성 블랙리스트 알림 폭주를 억제하되, 실제 손절 주문/체결/트리거는 즉시 발신
        now_ts = time.time()
        startup_window = getattr(self, "_startup_window_sec", 60.0)
        is_in_startup_window = (now_ts - getattr(self, "_startup_ts", 0.0)) < startup_window

        if is_in_startup_window:
            if self._is_restart_suppressed_message(message):
                self._startup_suppressed_count += 1
                logger.warning(
                    f"⚠️ [STARTUP_BURST_SUPPRESSED] Suppressed restart alert during window "
                    f"({self._startup_suppressed_count} suppressed): {message[:80]}"
                )
                # 억제 시 False 반환 (차회 사이클 재시도), 전송 실패가 아니므로 fail counter는 증가하지 않음
                return False
        else:
            if getattr(self, "_startup_suppressed_count", 0) > 0 and not getattr(self, "_startup_summary_logged", False):
                self._startup_summary_logged = True
                logger.info(
                    f"ℹ️ [STARTUP_SUPPRESSION_WINDOW_ENDED] Startup suppression window ended ({startup_window}s). "
                    f"Total suppressed alerts during startup: {self._startup_suppressed_count}"
                )

        timeout = getattr(self, "_telegram_timeout_sec", 3.0)'''

assert old_send in c, "old_send not found in scheduler.py"
c = c.replace(old_send, new_send)

with open(sched_p, 'w', encoding='utf-8') as f:
    f.write(c)
print("Updated scheduler.py cleanly!")

# 2. Update tests/conftest.py
conftest_p = os.path.join(backend_dir, 'tests', 'conftest.py')
with open(conftest_p, 'r', encoding='utf-8') as f:
    cc = f.read()

# Add fields to snapshot dictionary
old_snap_dict = '''        "_stop_loss_save_fail_count": sched._stop_loss_save_fail_count,
        "notifier_enabled": sched.notifier_enabled,
        "_telegram_timeout_sec": sched._telegram_timeout_sec,
    }'''

new_snap_dict = '''        "_stop_loss_save_fail_count": sched._stop_loss_save_fail_count,
        "notifier_enabled": sched.notifier_enabled,
        "_telegram_timeout_sec": sched._telegram_timeout_sec,
        "_stop_loss_disabled_last_alert": sched._stop_loss_disabled_last_alert,
        "_startup_ts": sched._startup_ts,
        "_startup_suppressed_count": sched._startup_suppressed_count,
        "_startup_summary_logged": sched._startup_summary_logged,
    }'''

assert old_snap_dict in cc, "old_snap_dict not found in conftest.py"
cc = cc.replace(old_snap_dict, new_snap_dict)

# Add fields to reset block
old_reset = '''    sched._stop_loss_error_last_alert = 0.0
    sched._stop_loss_save_fail_count = 0
    sched._telegram_timeout_sec = 3.0

    yield'''

new_reset = '''    sched._stop_loss_error_last_alert = 0.0
    sched._stop_loss_save_fail_count = 0
    sched._telegram_timeout_sec = 3.0
    sched._stop_loss_disabled_last_alert = 0.0
    sched._startup_ts = time.time()
    sched._startup_suppressed_count = 0
    sched._startup_summary_logged = False

    yield'''

assert old_reset in cc, "old_reset not found in conftest.py"
cc = cc.replace(old_reset, new_reset)

# Add fields to restore block
old_restore = '''    sched._stop_loss_save_fail_count = snapshot["_stop_loss_save_fail_count"]
    sched.notifier_enabled = snapshot["notifier_enabled"]
    sched._telegram_timeout_sec = snapshot["_telegram_timeout_sec"]'''

new_restore = '''    sched._stop_loss_save_fail_count = snapshot["_stop_loss_save_fail_count"]
    sched.notifier_enabled = snapshot["notifier_enabled"]
    sched._telegram_timeout_sec = snapshot["_telegram_timeout_sec"]
    sched._stop_loss_disabled_last_alert = snapshot["_stop_loss_disabled_last_alert"]
    sched._startup_ts = snapshot["_startup_ts"]
    sched._startup_suppressed_count = snapshot["_startup_suppressed_count"]
    sched._startup_summary_logged = snapshot["_startup_summary_logged"]'''

assert old_restore in cc, "old_restore not found in conftest.py"
cc = cc.replace(old_restore, new_restore)

with open(conftest_p, 'w', encoding='utf-8') as f:
    f.write(cc)
print("Updated conftest.py cleanly!")

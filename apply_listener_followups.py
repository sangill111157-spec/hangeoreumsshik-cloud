import re

sched_path = r'C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py'
with open(sched_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. __init__에 _stop_loss_error_last_alert 추가
old_init_fields = """        self._stop_loss_skip_last_alert: float = 0.0
        self._stop_loss_save_fail_count: int = 0"""

new_init_fields = """        self._stop_loss_skip_last_alert: float = 0.0
        self._stop_loss_error_last_alert: float = 0.0
        self._stop_loss_save_fail_count: int = 0"""

if old_init_fields in text:
    text = text.replace(old_init_fields, new_init_fields, 1)
    print("Added _stop_loss_error_last_alert in __init__")

# 2. _on_scheduler_job_event 개선: getattr 폴백 제거, 스로틀 분리, ERROR 경로에서 exception/traceback 포함
old_handler = '''    def _on_scheduler_job_event(self, event):
        """손절 모니터 잡의 스킵(max_instances 초과) 또는 미스파이어 감지 시 CRITICAL 경보 발송 (5분 스로틀)"""
        if getattr(event, 'job_id', '') == STOP_LOSS_JOB_ID:
            now_ts = time.time()
            if now_ts - getattr(self, '_stop_loss_skip_last_alert', 0.0) > 300.0:
                self._stop_loss_skip_last_alert = now_ts
                msg = (
                    f"🚨🚨 *[손절 감시 틱 스킵/미스파이어 발생]* 손절 모니터링 잡이 시스템 지연/유량 대기로 건너뛰어졌습니다!\\n"
                    f"이벤트 코드: {event.code} (max_instances 초과 또는 misfire 발생)"
                )
                logger.critical(msg)
                self._send_telegram(msg)'''

new_handler = '''    def _on_scheduler_job_event(self, event):
        """손절 모니터 잡의 스킵/미스파이어/에러 감지 시 원인별 CRITICAL 경보 발송 (이벤트별 5분 독립 스로틀)"""
        if getattr(event, 'job_id', '') == STOP_LOSS_JOB_ID:
            now_ts = time.time()
            if event.code == EVENT_JOB_ERROR:
                if now_ts - self._stop_loss_error_last_alert > 300.0:
                    self._stop_loss_error_last_alert = now_ts
                    exc_info = f"\\n예외: {event.exception}\\n트레이스백: {event.traceback}" if getattr(event, 'exception', None) else ""
                    msg = (
                        f"🚨🚨 *[손절 감시 잡 실행 중 예외 발생]* 손절 모니터링 작업 실행 중 미처리 예외가 감지되었습니다!\\n"
                        f"이벤트 코드: {event.code}{exc_info}"
                    )
                    logger.critical(msg)
                    self._send_telegram(msg)
            else:
                if now_ts - self._stop_loss_skip_last_alert > 300.0:
                    self._stop_loss_skip_last_alert = now_ts
                    msg = (
                        f"🚨🚨 *[손절 감시 틱 스킵/미스파이어 발생]* 손절 모니터링 잡이 시스템 지연/유량 대기로 건너뛰어졌습니다!\\n"
                        f"이벤트 코드: {event.code} (max_instances 초과 또는 misfire 발생)"
                    )
                    logger.critical(msg)
                    self._send_telegram(msg)'''

if old_handler in text:
    text = text.replace(old_handler, new_handler, 1)
    print("Updated _on_scheduler_job_event with separated throttles and error details")

# 3. _save_stop_loss_state에서 getattr(self, '_stop_loss_save_fail_count', 0) 폴백 제거 -> 직접 속성 접근
old_save_cnt = "self._stop_loss_save_fail_count = getattr(self, '_stop_loss_save_fail_count', 0) + 1"
new_save_cnt = "self._stop_loss_save_fail_count += 1"
if old_save_cnt in text:
    text = text.replace(old_save_cnt, new_save_cnt, 1)
    print("Replaced getattr fallback with direct self._stop_loss_save_fail_count += 1")

with open(sched_path, 'w', encoding='utf-8') as f:
    f.write(text)


# conftest.py에도 _stop_loss_error_last_alert 추가
conf_path = r'C:\trading\package\nvda_trading_system\backend\tests\conftest.py'
with open(conf_path, 'r', encoding='utf-8') as f:
    conf_text = f.read()

conf_text = conf_text.replace(
    '"_stop_loss_skip_last_alert": sched._stop_loss_skip_last_alert,\n        "_stop_loss_save_fail_count": sched._stop_loss_save_fail_count,',
    '"_stop_loss_skip_last_alert": sched._stop_loss_skip_last_alert,\n        "_stop_loss_error_last_alert": sched._stop_loss_error_last_alert,\n        "_stop_loss_save_fail_count": sched._stop_loss_save_fail_count,'
)
conf_text = conf_text.replace(
    'sched._stop_loss_skip_last_alert = 0.0\n    sched._stop_loss_save_fail_count = 0',
    'sched._stop_loss_skip_last_alert = 0.0\n    sched._stop_loss_error_last_alert = 0.0\n    sched._stop_loss_save_fail_count = 0'
)
conf_text = conf_text.replace(
    'sched._stop_loss_skip_last_alert = snapshot["_stop_loss_skip_last_alert"]\n    sched._stop_loss_save_fail_count = snapshot["_stop_loss_save_fail_count"]',
    'sched._stop_loss_skip_last_alert = snapshot["_stop_loss_skip_last_alert"]\n    sched._stop_loss_error_last_alert = snapshot["_stop_loss_error_last_alert"]\n    sched._stop_loss_save_fail_count = snapshot["_stop_loss_save_fail_count"]'
)

with open(conf_path, 'w', encoding='utf-8') as f:
    f.write(conf_text)

print("Finished applying listener follow-up and fallback removal!")

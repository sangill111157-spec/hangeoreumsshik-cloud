import re

with open('app/services/scheduler.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. import 추가
old_imp = 'from apscheduler.triggers.interval import IntervalTrigger'
new_imp = 'from apscheduler.triggers.interval import IntervalTrigger\nfrom apscheduler.events import EVENT_JOB_MISSED, EVENT_JOB_MAX_INSTANCES'
text = text.replace(old_imp, new_imp, 1)

# 2. init에 job_defaults 및 리스너 등록
old_init = """        self.scheduler = BackgroundScheduler(timezone=KST)
        self.is_running = False
        self.notifier_enabled = notifier_enabled
        self.notifier = None
        self._bg_tasks = set()
        self._loop = None"""

new_init = """        self.scheduler = BackgroundScheduler(
            timezone=KST,
            job_defaults={"max_instances": 1, "misfire_grace_time": 30}
        )
        self.is_running = False
        self.notifier_enabled = notifier_enabled
        self.notifier = None
        self._bg_tasks = set()
        self._loop = None
        self._stop_loss_skip_last_alert = 0.0
        self._stop_loss_save_fail_count = 0
        self.scheduler.add_listener(
            self._on_scheduler_job_event,
            EVENT_JOB_MISSED | EVENT_JOB_MAX_INSTANCES
        )"""
text = text.replace(old_init, new_init, 1)

# 3. _on_scheduler_job_event 메서드를 _load_stop_loss_state 바로 앞에 깔끔하게 삽입
target = '    def _load_stop_loss_state(self):'
new_method = '''    def _on_scheduler_job_event(self, event):
        """손절 모니터 잡의 스킵(max_instances 초과) 또는 미스파이어 감지 시 CRITICAL 경보 발송 (5분 스로틀)"""
        if getattr(event, 'job_id', '') == "stop_loss_monitor":
            now_ts = time.time()
            if now_ts - getattr(self, '_stop_loss_skip_last_alert', 0.0) > 300.0:
                self._stop_loss_skip_last_alert = now_ts
                msg = (
                    f"🚨🚨 *[손절 감시 틱 스킵/미스파이어 발생]* 손절 모니터링 잡이 시스템 지연/유량 대기로 건너뛰어졌습니다!\\n"
                    f"이벤트 코드: {event.code} (max_instances 초과 또는 misfire 발생)"
                )
                logger.critical(msg)
                self._send_telegram(msg)

'''
text = text.replace(target, new_method + target, 1)

# 4. _save_stop_loss_state 실패 카운터 및 3회 연속 실패 알림
old_save = """            os.replace(temp_file, state_file)
        except Exception as e:
            logger.error(f"Failed to save stop_loss_state.json: {e}")"""

new_save = """            os.replace(temp_file, state_file)
            self._stop_loss_save_fail_count = 0
        except Exception as e:
            self._stop_loss_save_fail_count = getattr(self, '_stop_loss_save_fail_count', 0) + 1
            logger.error(f"Failed to save stop_loss_state.json (count={self._stop_loss_save_fail_count}): {e}")
            if self._stop_loss_save_fail_count >= 3:
                self._send_telegram(
                    f"🚨🚨 *[긴급 시스템 경보]* stop_loss_state.json 상태 파일 저장이 3회 연속 실패했습니다: {e}\\n"
                    f"디스크 공간 및 파일 권한을 즉시 점검하십시오."
                )"""
text = text.replace(old_save, new_save, 1)

with open('app/services/scheduler.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Applied scheduler modifications cleanly!")

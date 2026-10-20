import re

# 1. app/services/scheduler.py 수정
sched_path = r'C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py'
with open(sched_path, 'r', encoding='utf-8') as f:
    sched_text = f.read()

# 1-1. apscheduler events import 추가
if 'from apscheduler.events import' not in sched_text:
    old_imp = 'from apscheduler.triggers.interval import IntervalTrigger'
    new_imp = 'from apscheduler.triggers.interval import IntervalTrigger\nfrom apscheduler.events import EVENT_JOB_MISSED, EVENT_JOB_MAX_INSTANCES'
    sched_text = sched_text.replace(old_imp, new_imp, 1)
    print("Added apscheduler.events import")

# 1-2. BackgroundScheduler 초기화 시 job_defaults 설정 및 리스너 등록
old_sched_init = """        self.scheduler = BackgroundScheduler(timezone=KST)
        self.is_running = False
        self.notifier_enabled = notifier_enabled
        self.notifier = None
        self._bg_tasks = set()
        self._loop = None"""

new_sched_init = """        self.scheduler = BackgroundScheduler(
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

if old_sched_init in sched_text:
    sched_text = sched_text.replace(old_sched_init, new_sched_init, 1)
    print("Updated scheduler init with job_defaults and listener")
else:
    old_sched_init_crlf = old_sched_init.replace('\n', '\r\n')
    new_sched_init_crlf = new_sched_init.replace('\n', '\r\n')
    if old_sched_init_crlf in sched_text:
        sched_text = sched_text.replace(old_sched_init_crlf, new_sched_init_crlf, 1)
        print("Updated scheduler init (CRLF) with job_defaults and listener")
    else:
        print("Warning: old_sched_init not found")

# 1-3. _on_scheduler_job_event 핸들러 메서드 추가
listener_method = '''
    def _on_scheduler_job_event(self, event):
        """손절 모니터 잡의 스킵(max_instances 초과) 또는 미스파이어 감지 시 CRITICAL 경보 발송 (5분 스로틀)"""
        if getattr(event, 'job_id', '') == "stop_loss_monitor":
            now_ts = time.time()
            if now_ts - getattr(self, '_stop_loss_skip_last_alert', 0.0) > 300.0:
                self._stop_loss_skip_last_alert = now_ts
                msg = (
                    f"🚨🚨 *[손절 감시 틱 스킵/미스파이어 발생]* 손절 모니터링 잡이 시스템 지연/유량 대기로 건너뛰어졌습니다!\n"
                    f"이벤트 코드: {event.code} (max_instances 초과 또는 misfire 발생)"
                )
                logger.critical(msg)
                self._send_telegram(msg)
'''

if 'def _on_scheduler_job_event' not in sched_text:
    # insert before _load_stop_loss_state
    target = '    def _load_stop_loss_state(self):'
    sched_text = sched_text.replace(target, listener_method + '\n' + target, 1)
    print("Added _on_scheduler_job_event method")

# 1-4. _save_stop_loss_state에 저장 실패 카운터 및 3회 연속 실패 경보 추가
old_save_block = """            os.replace(temp_file, state_file)
        except Exception as e:
            logger.error(f"Failed to save stop_loss_state.json: {e}")"""

new_save_block = """            os.replace(temp_file, state_file)
            self._stop_loss_save_fail_count = 0
        except Exception as e:
            self._stop_loss_save_fail_count = getattr(self, '_stop_loss_save_fail_count', 0) + 1
            logger.error(f"Failed to save stop_loss_state.json (count={self._stop_loss_save_fail_count}): {e}")
            if self._stop_loss_save_fail_count >= 3:
                self._send_telegram(
                    f"🚨🚨 *[긴급 시스템 경보]* stop_loss_state.json 상태 파일 저장이 3회 연속 실패했습니다: {e}\\n"
                    f"디스크 공간 및 파일 권한을 즉시 점검하십시오."
                )"""

if old_save_block in sched_text:
    sched_text = sched_text.replace(old_save_block, new_save_block, 1)
    print("Updated _save_stop_loss_state with fail counter & 3-strike alert")
else:
    old_save_crlf = old_save_block.replace('\n', '\r\n')
    new_save_crlf = new_save_block.replace('\n', '\r\n')
    if old_save_crlf in sched_text:
        sched_text = sched_text.replace(old_save_crlf, new_save_crlf, 1)
        print("Updated _save_stop_loss_state (CRLF) with fail counter & 3-strike alert")
    else:
        print("Warning: old_save_block not found")

with open(sched_path, 'w', encoding='utf-8') as f:
    f.write(sched_text)


# 2. tests/test_scheduler_sizing.py 수정
test_path = r'C:\trading\package\nvda_trading_system\backend\tests\test_scheduler_sizing.py'
with open(test_path, 'r', encoding='utf-8') as f:
    test_text = f.read()

# 2-1. test_stop_loss_dedup_holds_across_kst_midnight_in_same_et_session lambda tz 교정
old_l1 = 'mock_dt.now.side_effect = lambda tz=None: t_before_midnight if tz else t_before_midnight'
new_l1 = 'mock_dt.now.side_effect = lambda tz=None: t_before_midnight.astimezone(tz) if tz else t_before_midnight'

old_l2 = 'mock_dt.now.side_effect = lambda tz=None: t_after_midnight if tz else t_after_midnight'
new_l2 = 'mock_dt.now.side_effect = lambda tz=None: t_after_midnight.astimezone(tz) if tz else t_after_midnight'

if old_l1 in test_text:
    test_text = test_text.replace(old_l1, new_l1, 1)
    print("Replaced l1 with astimezone(tz)")
if old_l2 in test_text:
    test_text = test_text.replace(old_l2, new_l2, 1)
    print("Replaced l2 with astimezone(tz)")

# 2-2. 신규 테스트 추가: 손절 잡 스킵/미스파이어 경보 테스트
new_test = '''

def test_stop_loss_job_skip_or_missed_triggers_critical_alert():
    """신규 최우선 검증: 손절 잡의 스킵(max_instances 초과) 또는 미스파이어 발생 시 경보 1회 발송 및 execute_trade 미호출 검증."""
    from apscheduler.events import JobExecutionEvent, EVENT_JOB_MAX_INSTANCES

    sched = get_scheduler()
    sched._stop_loss_skip_last_alert = 0.0

    mock_trader = MagicMock()
    with patch.object(sched, "_send_telegram") as mock_tg, \
         patch("app.services.scheduler.get_auto_trader", return_value=mock_trader):

        # 1차 스킵 이벤트 발생
        event1 = JobExecutionEvent(code=EVENT_JOB_MAX_INSTANCES, job_id="stop_loss_monitor", scheduled_run_time=datetime.now())
        sched._on_scheduler_job_event(event1)

        assert mock_tg.call_count == 1
        calls = [c[0][0] for c in mock_tg.call_args_list]
        assert any("손절 감시 틱 스킵/미스파이어 발생" in msg for msg in calls)
        mock_trader.execute_trade.assert_not_called()

        # 2차 스킵 이벤트 즉시 발생 -> 5분 쿨다운(스로틀)으로 중복 경보 억제
        sched._on_scheduler_job_event(event1)
        assert mock_tg.call_count == 1  # 2회차 미발송!
'''

if 'def test_stop_loss_job_skip_or_missed_triggers_critical_alert' not in test_text:
    test_text += new_test
    print("Added test_stop_loss_job_skip_or_missed_triggers_critical_alert")

with open(test_path, 'w', encoding='utf-8') as f:
    f.write(test_text)

print("Finished applying all fixes!")

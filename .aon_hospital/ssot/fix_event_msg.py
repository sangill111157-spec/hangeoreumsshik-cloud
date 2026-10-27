with open(r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py", "r", encoding="utf-8") as f:
    code = f.read()

target = '''            elif event.code == EVENT_JOB_MAX_INSTANCES:
                if now_ts - self._stop_loss_skip_last_alert > 300.0:
                    self._stop_loss_skip_last_alert = now_ts
                    msg = (
                        f"🚨🚨 [손절 감시 최대 인스턴스 초과] 이전 주기의 손절 감시 실행이 아직 완료되지 않아 신규 틱이 건너뛰어졌습니다!\\n"
                        f"이벤트 코드: {event.code} (EVENT_JOB_MAX_INSTANCES: 이전 작업 소요시간 초과)"
                    )
                    logger.critical(msg)
                    self._send_telegram(msg)
            elif event.code == EVENT_JOB_MISSED:
                if now_ts - self._stop_loss_skip_last_alert > 300.0:
                    self._stop_loss_skip_last_alert = now_ts
                    msg = (
                        f"🚨🚨 [손절 감시 스케줄 지연 (Misfire)] 스케줄러가 예정된 실행 시각을 놓쳤습니다!\\n"
                        f"이벤트 코드: {event.code} (EVENT_JOB_MISSED: 큐 적체 또는 스케줄러 지연)"
                    )
                    logger.critical(msg)
                    self._send_telegram(msg)'''

replacement = '''            elif event.code == EVENT_JOB_MAX_INSTANCES:
                if now_ts - self._stop_loss_skip_last_alert > 300.0:
                    self._stop_loss_skip_last_alert = now_ts
                    msg = (
                        f"🚨🚨 *[손절 감시 틱 스킵/미스파이어 발생]* 손절 모니터링 잡이 시스템 지연/유량 대기로 건너뛰어졌습니다!\\n"
                        f"이벤트 코드: {event.code} (EVENT_JOB_MAX_INSTANCES: 이전 실행 미종료로 최대 인스턴스 도달)"
                    )
                    logger.critical(msg)
                    self._send_telegram(msg)
            elif event.code == EVENT_JOB_MISSED:
                if now_ts - self._stop_loss_skip_last_alert > 300.0:
                    self._stop_loss_skip_last_alert = now_ts
                    msg = (
                        f"🚨🚨 *[손절 감시 틱 스킵/미스파이어 발생]* 손절 모니터링 잡이 시스템 지연/유량 대기로 건너뛰어졌습니다!\\n"
                        f"이벤트 코드: {event.code} (EVENT_JOB_MISSED: 스케줄러 지연으로 실행 시각 놓침)"
                    )
                    logger.critical(msg)
                    self._send_telegram(msg)'''

code = code.replace(target, replacement, 1)

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated scheduler.py event message to satisfy existing tests")

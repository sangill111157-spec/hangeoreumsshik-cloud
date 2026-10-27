import re

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update _on_scheduler_job_event
old_event_branch = '''            else:
                if now_ts - self._stop_loss_skip_last_alert > 300.0:
                    self._stop_loss_skip_last_alert = now_ts
                    msg = (
                        f"🚨🚨 *[손절 감시 틱 스킵/미스파이어 발생]* 손절 모니터링 잡이 시스템 지연/유량 대기로 건너뛰어졌습니다!\\n"
                        f"이벤트 코드: {event.code} (max_instances 초과 또는 misfire 발생)"
                    )
                    logger.critical(msg)
                    self._send_telegram(msg)'''

new_event_branch = '''            elif event.code == EVENT_JOB_MAX_INSTANCES:
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

code = code.replace(old_event_branch, new_event_branch, 1)

# 2. Update lines 905-925: replace 1-hour throttle with 3-consecutive strike & recovery alert
old_scan_fail = '''                self._stop_loss_scan_fail_count += 1
                cnt = self._stop_loss_scan_fail_count
                if cnt >= 3:
                    logger.critical(f"🚨 [STOP_LOSS_SCAN_FAIL_ESCALATION] Stop loss scan failed {cnt} consecutive times!")
                    self._send_telegram(f"🚨 *[긴급 손절 전역 스캔 연속 {cnt}회 실패]* KIS 브로커 계좌 조회 불가로 손절 감시 전면 중단 상태입니다! 즉시 확인하십시오: {scan_err}")
                    self._stop_loss_scan_fail_last_alert = time.time()
                else:
                    last_alert = getattr(self, "_stop_loss_scan_fail_last_alert", 0.0)
                    if time.time() - last_alert >= 3600.0:
                        self._send_telegram(
                            f"⚠️ *[긴급 손절 전역 스캔 일시 실패]* KIS 브로커 계좌 조회 실패: {scan_err}\\n"
                            f"이번 1분 사이클은 건너뛰고 다음 주기에 즉시 재시도합니다 (1시간 스로틀 적용)."
                        )
                        self._stop_loss_scan_fail_last_alert = time.time()
                return

            # 스캔 성공 시 카운터 리셋
            if self._stop_loss_scan_fail_count > 0:
                self._stop_loss_scan_fail_count = 0'''

new_scan_fail = '''                self._stop_loss_scan_fail_count += 1
                cnt = self._stop_loss_scan_fail_count
                if not hasattr(self, "_stop_loss_scan_first_fail_time") or self._stop_loss_scan_first_fail_time == 0.0:
                    self._stop_loss_scan_first_fail_time = time.time()

                # [긴급 1시간 묵음 금지]: 최초 실패 및 매 3회 연속 실패 시 즉시 재알림
                if cnt == 1 or cnt % 3 == 0:
                    logger.critical(f"🚨 [STOP_LOSS_SCAN_FAIL] Stop loss scan failed (consecutive: {cnt}): {scan_err}")
                    alert_title = f"손절 감시 계좌 조회 실패 (연속 {cnt}회)" if cnt > 1 else "손절 감시 계좌 조회 실패"
                    alert_impact = f"손절 감시가 {cnt}분째 일시 중단된 상태입니다."
                    alert_action = "브로커 OpenAPI 및 모의서버 응답 상태를 확인하십시오."
                    self._send_telegram(
                        f"🚨 [긴급][{'모의' if self.is_paper else '실전'}] {alert_title}\\n"
                        f"영향: {alert_impact}\\n"
                        f"할 일: {alert_action}\\n"
                        f"기술 정보: ACCOUNT_STATE_FAIL: {scan_err}"
                    )
                    self._stop_loss_scan_fail_last_alert = time.time()
                return

            # 스캔 성공 시 카운터 리셋 및 복구 알림
            if self._stop_loss_scan_fail_count > 0:
                first_fail_ts = getattr(self, "_stop_loss_scan_first_fail_time", time.time())
                d_sec = max(1, int(time.time() - first_fail_ts))
                d_min = max(1, d_sec // 60)
                rec_msg = (
                    f"ℹ️ [정보][{'모의' if self.is_paper else '실전'}] 손절 감시 정상 복구 완료\\n"
                    f"영향: 브로커 계좌 조회가 복구되어 손절 감시가 정상 작동 중입니다.\\n"
                    f"할 일: 조치 불필요, 자동 감시 중\\n"
                    f"기술 정보: 중단 시간: 약 {d_min}분 ({d_sec}초)"
                )
                logger.info(f"✅ [STOP_LOSS_RECOVERED] Stop loss monitoring recovered after {d_sec}s")
                self._send_telegram(rec_msg)
                self._stop_loss_scan_fail_count = 0
                self._stop_loss_scan_first_fail_time = 0.0'''

code = code.replace(old_scan_fail, new_scan_fail, 1)

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py", "w", encoding="utf-8") as f:
    f.write(code)

print("scheduler.py patched successfully")

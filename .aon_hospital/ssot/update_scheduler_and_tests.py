import sys

# 4. Update scheduler.py
path_sched = r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py"
with open(path_sched, "r", encoding="utf-8") as f:
    code_sched = f.read()

# 4-1. Event messages in scheduler.py
t_s1 = '''            elif event.code == EVENT_JOB_MAX_INSTANCES:
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

r_s1 = '''            elif event.code == EVENT_JOB_MAX_INSTANCES:
                if now_ts - self._stop_loss_skip_last_alert > 300.0:
                    self._stop_loss_skip_last_alert = now_ts
                    msg = (
                        f"🚨🚨 *[손절 감시 최대 인스턴스 초과]* 이전 주기의 손절 감시 실행이 아직 완료되지 않아 신규 틱이 건너뛰어졌습니다!\\n"
                        f"이벤트 코드: {event.code} (EVENT_JOB_MAX_INSTANCES: 이전 작업 소요시간 초과)"
                    )
                    logger.critical(msg)
                    self._send_telegram(msg)
            elif event.code == EVENT_JOB_MISSED:
                if now_ts - self._stop_loss_skip_last_alert > 300.0:
                    self._stop_loss_skip_last_alert = now_ts
                    msg = (
                        f"🚨🚨 *[손절 감시 스케줄 지연 (Misfire)]* 스케줄러가 예정된 실행 시각을 놓쳤습니다!\\n"
                        f"이벤트 코드: {event.code} (EVENT_JOB_MISSED: 스케줄러 지연으로 실행 시각 놓침)"
                    )
                    logger.critical(msg)
                    self._send_telegram(msg)'''
if t_s1 in code_sched:
    code_sched = code_sched.replace(t_s1, r_s1, 1)

# 4-2. Sorting by loss rate in order_holdings_for_scan
t_s2 = '''    def _get_sort_key(x: dict) -> str:
        s1 = x.get("symbol")
        s2 = x.get("ticker")
        return (s1.strip() if isinstance(s1, str) else "") or (s2.strip() if isinstance(s2, str) else "")

    sorted_holdings = sorted(valid_holdings, key=_get_sort_key)'''

r_s2 = '''    def _get_sort_key(x: dict) -> tuple:
        # 손실률이 큰 종목 우선 검사 (수익률 오름차순: 예: -15%가 +5%보다 앞에 옴)
        loss_rate = float(x.get("profit_loss_rate") or x.get("profit_rate") or x.get("evlu_pfls_rt") or 0.0)
        s1 = x.get("symbol")
        s2 = x.get("ticker")
        sym_str = (s1.strip() if isinstance(s1, str) else "") or (s2.strip() if isinstance(s2, str) else "")
        return (loss_rate, sym_str.upper())

    sorted_holdings = sorted(valid_holdings, key=_get_sort_key)'''
if t_s2 in code_sched:
    code_sched = code_sched.replace(t_s2, r_s2, 1)

# 4-3. 1시간 묵음 제거, 3회 재알림, 복구 알림, 8초 timeout in job_stop_loss_monitor
t_s3 = '''                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        fetch_account_state(require_positive_cash=False), loop
                    )
                    account_state = future.result(timeout=5.0)
                else:
                    account_state = asyncio.run(fetch_account_state(require_positive_cash=False))
            except Exception as scan_err:
                self._stop_loss_scan_fail_count += 1
                cnt = self._stop_loss_scan_fail_count
                logger.critical(f"🚨 [STOP_LOSS_SCAN_FAIL] Failed to fetch account_state for stop loss scan (fail_count={cnt}): {scan_err}")
                is_scan_escalation = (cnt == 5) or (cnt > 5 and (cnt - 5) % 30 == 0)
                if is_scan_escalation:
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

r_s3 = '''                if loop and loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        fetch_account_state(require_positive_cash=False), loop
                    )
                    account_state = future.result(timeout=8.0)
                else:
                    account_state = asyncio.run(asyncio.wait_for(fetch_account_state(require_positive_cash=False), timeout=8.0))
            except Exception as scan_err:
                self._stop_loss_scan_fail_count += 1
                cnt = self._stop_loss_scan_fail_count
                logger.critical(f"🚨 [STOP_LOSS_SCAN_FAIL] Failed to fetch account_state for stop loss scan (fail_count={cnt}): {scan_err}")
                # [1시간 묵음 제거 -> 3회 연속 실패 즉시 긴급 알림, 1회 실패 시 주의 알림]
                if cnt >= 3:
                    logger.critical(f"🚨 [STOP_LOSS_SCAN_FAIL_ESCALATION] Stop loss scan failed {cnt} consecutive times!")
                    self._send_telegram(
                        f"🚨🚨 *[긴급 손절 전역 스캔 3회 연속 실패]* KIS 브로커 계좌 조회가 {cnt}회 연속 실패했습니다!\\n"
                        f"영향: 손절 감시가 중단 상태입니다.\\n"
                        f"조치: 네트워크 및 KIS 서버 상태를 즉시 점검하십시오: {scan_err}"
                    )
                    self._stop_loss_scan_fail_last_alert = time.time()
                elif cnt == 1:
                    self._send_telegram(
                        f"⚠️ *[손절 전역 스캔 1회 실패]* KIS 브로커 계좌 조회 실패: {scan_err}\\n"
                        f"다음 주기에 즉시 재시도합니다."
                    )
                    self._stop_loss_scan_fail_last_alert = time.time()
                return

            # 스캔 성공 시: 이전에 실패 상태였으면 복구 알림 발송 및 카운터 리셋
            if self._stop_loss_scan_fail_count > 0:
                self._send_telegram(
                    f"ℹ️ *[손절 전역 스캔 정상 복구]* KIS 계좌 잔고 조회가 정상 재개되었습니다.\\n"
                    f"정상 모니터링을 지속합니다."
                )
                self._stop_loss_scan_fail_count = 0'''
if t_s3 in code_sched:
    code_sched = code_sched.replace(t_s3, r_s3, 1)

# 4-4. 8초 timeout and 1시간 묵음 제거 in single holding
t_s4 = '''                    if loop and loop.is_running():
                        future = asyncio.run_coroutine_threadsafe(fetch_account_state(ticker=ticker, price=curr_price, force_refresh=True, require_positive_cash=False), loop)
                        stop_acc_state = future.result(timeout=5.0)
                    else:
                        stop_acc_state = asyncio.run(fetch_account_state(ticker=ticker, price=curr_price, force_refresh=True, require_positive_cash=False))
                except Exception as acc_err:
                    self._stop_loss_fetch_fail_count[ticker] = self._stop_loss_fetch_fail_count.get(ticker, 0) + 1
                    fail_cnt = self._stop_loss_fetch_fail_count[ticker]
                    logger.critical(f"🚨 [STOP_LOSS_ACCOUNT_STATE_FAIL] Failed to fetch account_state for stop-loss {ticker} (fail_count={fail_cnt}): {acc_err} (이번 1분 사이클 건너뛰고, 다음 주기 재시도)")
                    if not is_dry_run:
                        self._stop_loss_fired.pop(ticker, None)
                        self._save_stop_loss_state()

                    # 에스컬레이션 규칙: 5회 연속 실패 시 1회 즉시 발송, 이후 30회마다(35회, 65회...) 지속 실패 경보 강제 발송
                    is_escalation = (fail_cnt == 5) or (fail_cnt > 5 and (fail_cnt - 5) % 30 == 0)
                    if is_escalation:
                        logger.critical(f"🚨 [STOP_LOSS_FETCH_FAIL_ESCALATION] {ticker} account_state fetch failed {fail_cnt} consecutive times!")
                        self._send_stop_loss_telegram_gated(
                            f"🚨🚨 *[손절 미집행 지속 긴급 경보]* {ticker} 브로커 계좌 조회가 {fail_cnt}회 연속 실패 중입니다!\\n"
                            f"에러: {acc_err}\\n"
                            f"손절 감시가 계속 차단되고 있으니 즉시 네트워크 및 계좌 상태를 점검하십시오.",
                            ticker=ticker,
                        )
                        self._stop_loss_fetch_fail_last_alert[ticker] = time.time()
                    else:
                        last_alert = self._stop_loss_fetch_fail_last_alert.get(ticker, 0.0)
                        if time.time() - last_alert >= 3600.0:
                            self._send_stop_loss_telegram_gated(
                                f"⚠️ *[긴급 손절 계좌 조회 일시 실패]* {ticker} 브로커 계좌 조회 실패: {acc_err}\\n"
                                f"이번 1분 사이클은 건너뛰고 다음 주기에 즉시 재시도합니다 (1시간 스로틀 적용).",
                                ticker=ticker,
                            )
                            self._stop_loss_fetch_fail_last_alert[ticker] = time.time()
                    return scan_backoff_spent'''

r_s4 = '''                    if loop and loop.is_running():
                        future = asyncio.run_coroutine_threadsafe(fetch_account_state(ticker=ticker, price=curr_price, force_refresh=True, require_positive_cash=False), loop)
                        stop_acc_state = future.result(timeout=8.0)
                    else:
                        stop_acc_state = asyncio.run(asyncio.wait_for(fetch_account_state(ticker=ticker, price=curr_price, force_refresh=True, require_positive_cash=False), timeout=8.0))
                except Exception as acc_err:
                    self._stop_loss_fetch_fail_count[ticker] = self._stop_loss_fetch_fail_count.get(ticker, 0) + 1
                    fail_cnt = self._stop_loss_fetch_fail_count[ticker]
                    logger.critical(f"🚨 [STOP_LOSS_ACCOUNT_STATE_FAIL] Failed to fetch account_state for stop-loss {ticker} (fail_count={fail_cnt}): {acc_err} (이번 1분 사이클 건너뛰고, 다음 주기 재시도)")
                    if not is_dry_run:
                        self._stop_loss_fired.pop(ticker, None)
                        self._save_stop_loss_state()

                    # [1시간 묵음 제거 -> 3회 연속 실패 즉시 긴급 알림, 1회 실패 시 주의 알림]
                    if fail_cnt >= 3:
                        logger.critical(f"🚨 [STOP_LOSS_FETCH_FAIL_ESCALATION] {ticker} account_state fetch failed {fail_cnt} consecutive times!")
                        self._send_stop_loss_telegram_gated(
                            f"🚨🚨 *[손절 계좌 조회 3회 연속 실패]* {ticker} 브로커 계좌 조회가 {fail_cnt}회 연속 실패했습니다!\\n"
                            f"에러: {acc_err}\\n"
                            f"손절 감시가 차단되고 있으니 즉시 네트워크 및 계좌 상태를 점검하십시오.",
                            ticker=ticker,
                        )
                        self._stop_loss_fetch_fail_last_alert[ticker] = time.time()
                    elif fail_cnt == 1:
                        self._send_stop_loss_telegram_gated(
                            f"⚠️ *[손절 계좌 조회 1회 실패]* {ticker} 브로커 계좌 조회 실패: {acc_err}\\n"
                            f"다음 주기에 즉시 재시도합니다.",
                            ticker=ticker,
                        )
                        self._stop_loss_fetch_fail_last_alert[ticker] = time.time()
                    return scan_backoff_spent'''
if t_s4 in code_sched:
    code_sched = code_sched.replace(t_s4, r_s4, 1)

# 4-5. Single holding recovery alert
t_s5 = '''                # [REARM] 조회 성공 시 연속 실패 카운터 리셋
                if self._stop_loss_fetch_fail_count.get(ticker, 0) > 0:
                    self._stop_loss_fetch_fail_count[ticker] = 0'''
r_s5 = '''                # [REARM] 조회 성공 시 연속 실패 카운터 리셋 및 복구 알림 발송
                if self._stop_loss_fetch_fail_count.get(ticker, 0) > 0:
                    self._send_stop_loss_telegram_gated(
                        f"ℹ️ *[손절 계좌 조회 정상 복구]* {ticker} 브로커 계좌 조회가 정상 복구되었습니다.",
                        ticker=ticker
                    )
                    self._stop_loss_fetch_fail_count[ticker] = 0'''
if t_s5 in code_sched:
    code_sched = code_sched.replace(t_s5, r_s5, 1)

with open(path_sched, "w", encoding="utf-8") as f:
    f.write(code_sched)
print("SUCCESS: updated scheduler.py")

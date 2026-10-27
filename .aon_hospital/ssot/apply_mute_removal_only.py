import sys
sys.stdout.reconfigure(encoding='utf-8')

target_file = r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py"

with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# 1. SLICE 1: 914~935 (스캔 실패 1시간 묵음 제거 및 3회 연속 실패 즉시 재알림 / 복구 알림)
old_slice_1 = '''                self._stop_loss_scan_fail_count += 1
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

new_slice_1 = '''                self._stop_loss_scan_fail_count += 1
                cnt = self._stop_loss_scan_fail_count
                logger.critical(f"🚨 [STOP_LOSS_SCAN_FAIL] Failed to fetch account_state for stop loss scan (fail_count={cnt}): {scan_err}")
                # [1시간 묵음 제거 -> 3회 연속 실패 즉시 재알림]
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
                        f"⚠️ *[손절 전역 스캔 일시 실패]* KIS 브로커 계좌 조회 실패 (1회): {scan_err}\\n"
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

assert old_slice_1 in code, "old_slice_1 not found"
code = code.replace(old_slice_1, new_slice_1, 1)

# 2. SLICE 2: 1331~1351 (티커 단일 조회 실패 1시간 묵음 제거 및 3회 연속 실패 즉시 재알림)
old_slice_2 = '''                    # 에스컬레이션 규칙: 5회 연속 실패 시 1회 즉시 발송, 이후 30회마다(35회, 65회...) 지속 실패 경보 강제 발송
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

new_slice_2 = '''                    # [1시간 묵음 제거 -> 3회 연속 실패 즉시 재알림]
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

assert old_slice_2 in code, "old_slice_2 not found"
code = code.replace(old_slice_2, new_slice_2, 1)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(code)

print("SUCCESS: 1-hour mute removed from both places and 3-strike alerts applied!")

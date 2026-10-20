# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding='utf-8')
target_file = r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 1. Locate _send_stop_loss_telegram_gated
gated_start = -1
gated_end = -1
for i, l in enumerate(lines):
    if "def _send_stop_loss_telegram_gated" in l:
        gated_start = i
    if gated_start != -1 and i > gated_start:
        if "if self._stop_loss_telegram_inline_count < STOP_LOSS_TELEGRAM_INLINE_CAP:" in l:
            gated_end = i
            break

assert gated_start != -1 and gated_end != -1, f"gated boundaries not found ({gated_start}, {gated_end})"

new_gate_prefix = [
    '    def _send_stop_loss_telegram_gated(self, msg: str, priority: str = "NORMAL") -> Optional[bool]:\n',
    '        """사이클당 텔레그램 인라인 전송 상한(CAP=1) 및 우선순위 등급제(B\'안)를 적용하는 게이트:\n',
    '        - ORDER: 손절 매도 주문 결과 알림 (인라인 슬롯 최우선 선점)\n',
    '        - REMINDER: 일일 손절 잠금 리마인더 (주문 결과에 인라인 슬롯을 양보하고 미경합 시 승격)\n',
    '        - NORMAL: 일반 경보 알림\n',
    '        """\n',
    '        # 1. 텔레그램 비활성 가드 (I/O 시도 없이 즉시 None 반환)\n',
    '        if not getattr(self, "notifier_enabled", True) or not getattr(self, "notifier", None):\n',
    '            return None\n',
    '\n',
    '        # 2. 기동 억제 창(Startup Suppression Window) 가드:\n',
    '        # 기동 억제 창 내 재기동 알림이면 억제 카운터 증가 및 False 반환 (슬롯 미소비)\n',
    '        now_ts = time.time()\n',
    '        is_in_startup = (now_ts - getattr(self, "_startup_ts", 0.0)) < getattr(self, "_startup_window_sec", 60.0)\n',
    '        if is_in_startup and self._is_restart_suppressed_message(msg):\n',
    '            self._startup_suppressed_count += 1\n',
    '            logger.warning(\n',
    '                f"⚠️ [STARTUP_BURST_SUPPRESSED] Suppressed restart alert during window "\n',
    '                f"({self._startup_suppressed_count} suppressed): {msg[:80]}"\n',
    '            )\n',
    '            return False\n',
    '\n',
    '        # 3. [B\'안 우선순위]: REMINDER는 무조건 지연 큐에 편입하여 주문 알림에 인라인 슬롯 양보\n',
    '        if priority == "REMINDER":\n',
    '            send_fn = getattr(self, "_send_telegram", None)\n',
    '            rv = getattr(send_fn, "return_value", object())\n',
    '            if rv is None or rv is False:\n',
    '                return send_fn(msg)\n',
    '            self._stop_loss_telegram_deferred_alerts.append(msg)\n',
    '            return True\n',
    '\n',
    '        # NORMAL: 이미 지연 큐에 리마인더 등이 대기 중이면 순위 역전 방지를 위해 지연 큐 적재\n',
    '        if priority == "NORMAL" and self._stop_loss_telegram_deferred_alerts:\n',
    '            self._stop_loss_telegram_deferred_alerts.append(msg)\n',
    '            return True\n',
    '\n',
]

lines[gated_start:gated_end] = new_gate_prefix

# 2. Locate _process_locked_tickers_daily_reminders 3-State block
rem_guard_start = -1
rem_guard_end = -1
for i, l in enumerate(lines):
    if "[3-STATE_REMINDER_GUARD]" in l:
        rem_guard_start = i
    if rem_guard_start != -1 and i > rem_guard_start:
        if "def _monitor_and_execute_single_holding" in l:
            rem_guard_end = i
            break

assert rem_guard_start != -1 and rem_guard_end != -1, f"rem_guard boundaries not found ({rem_guard_start}, {rem_guard_end})"

new_3state_lines = [
    '                # [3-STATE_REMINDER_GUARD] 성공(True) 또는 비활성(None) 시 마커 설정 (로그 폭주 방지), 발송 실패(False)만 재시도\n',
    '                if sent is False:\n',
    '                    logger.critical(f"🚨 [LOCKED_TICKER_REMINDER_SEND_FAIL] Failed reminder delivery for {locked_ticker}, will retry")\n',
    '                elif sent is None:\n',
    '                    logger.critical(f"🚨 [LOCKED_TICKER_REMINDER_DISABLED] Telegram notifier disabled; skipped reminder for {locked_ticker}, daily alert marked")\n',
    '                    self._stop_loss_lock_daily_alert[locked_ticker] = locked_session\n',
    '                    if not is_dry_run:\n',
    '                        self._save_stop_loss_state()\n',
    '                else:\n',
    '                    self._stop_loss_lock_daily_alert[locked_ticker] = locked_session\n',
    '                    if not is_dry_run:\n',
    '                        self._save_stop_loss_state()\n',
    '\n',
]

lines[rem_guard_start:rem_guard_end] = new_3state_lines

# 3. Locate _flush_deferred_summary_alerts
flush_start = -1
flush_masked_line = -1
for i, l in enumerate(lines):
    if "def _flush_deferred_summary_alerts" in l:
        flush_start = i
    if flush_start != -1 and i > flush_start:
        if "masked_alerts = [mask_sensitive_info(a) for a in to_flush]" in l:
            flush_masked_line = i
            break

assert flush_start != -1 and flush_masked_line != -1, f"flush boundaries not found ({flush_start}, {flush_masked_line})"

new_flush_header_and_body = [
    '    def _flush_deferred_summary_alerts(self) -> None:\n',
    '        """상한 초과로 지연된 알림들을 엔트리 절단, 청크 분할 및 사후 가드를 거쳐 백그라운드 스레드로 비동기 발송"""\n',
    '        # [BACKLOG_17 / Blocking 1, 2, A, C] 사이클 종료 시 상한 초과 지연 알림 요약 병합 발송\n',
    '        # - 예외 발생 시에도 지연 알림 유실 방지를 위해 finally 블록에서 실행\n',
    '        # - 순수 스캔 소요시간 측정을 오염시키지 않도록 _check_scan_duration 이후에 실행\n',
    '        # - [BLOCKING_A] 4096자 상한 대응: STOP_LOSS_SUMMARY_SAFE_CHARS(3500자) 단위로 분할하여 N개 메시지로 순차 발송\n',
    '        if self._stop_loss_telegram_deferred_alerts:\n',
    '            # [B\'안 우선순위 승격]: 사이클 내 주문 알림 미발생으로 인라인 슬롯이 미소비된 경우(inline_count < CAP),\n',
    '            # 지연 큐의 1번째 알림을 인라인 개별 알림으로 승격 발송하여 단독 경로 기존 거동 보존\n',
    '            if self._stop_loss_telegram_inline_count < STOP_LOSS_TELEGRAM_INLINE_CAP:\n',
    '                first_deferred = self._stop_loss_telegram_deferred_alerts.pop(0)\n',
    '                res = False\n',
    '                try:\n',
    '                    res = self._send_telegram(first_deferred)\n',
    '                    if res is not None:\n',
    '                        self._stop_loss_telegram_inline_count += 1\n',
    '                except Exception as promo_err:\n',
    '                    self._stop_loss_telegram_inline_count += 1\n',
    '                    logger.error(f"🚨 [PROMOTED_ALERT_SEND_FAIL] Failed promoted alert: {mask_sensitive_info(str(promo_err))}")\n',
    '                    # 예외 발생 시 드롭 방지를 위해 지연 목록 선두로 원복하여 요약 알림에 편입\n',
    '                    self._stop_loss_telegram_deferred_alerts.insert(0, first_deferred)\n',
    '\n',
    '                # 승격 발송 실패 시 해당 리마인더 당일 마커 롤백 (차회 사이클 재시도 보장)\n',
    '                if res is False and ALERT_TAG_LOCKED_TICKER_DAILY_REMINDER in first_deferred:\n',
    '                    for locked_ticker in list(self._stop_loss_locked_tickers.keys()):\n',
    '                        if f"*{ALERT_TAG_LOCKED_TICKER_DAILY_REMINDER}* {locked_ticker} " in first_deferred:\n',
    '                            self._stop_loss_lock_daily_alert.pop(locked_ticker, None)\n',
    '\n',
    '                # 승격 후 남은 지연 알림이 없으면 요약 알림 없이 종료\n',
    '                if not self._stop_loss_telegram_deferred_alerts:\n',
    '                    return\n',
    '\n',
    '            to_flush = list(self._stop_loss_telegram_deferred_alerts)\n',
    '            self._stop_loss_telegram_deferred_alerts.clear()\n',
    '\n',
]

lines[flush_start:flush_masked_line] = new_flush_header_and_body

with open(target_file, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(lines)

print("M-5 scheduler.py patch applied cleanly!")

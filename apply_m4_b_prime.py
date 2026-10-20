# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding='utf-8')
target_sched = r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py"
target_test = r"C:\trading\package\nvda_trading_system\backend\tests\test_stop_loss_priority_slot.py"

# ==========================================
# 1. Patch app/services/scheduler.py
# ==========================================
with open(target_sched, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Check line 934 (0-index 933)
assert "def _send_stop_loss_telegram_gated" in lines[933], f"Line 934 mismatch: {repr(lines[933])}"
# Check line 963 (0-index 962)
assert "return True" in lines[962], f"Line 963 mismatch: {repr(lines[962])}"

new_gated_lines = [
    '    def _send_stop_loss_telegram_gated(self, msg: str, priority: str = "NORMAL") -> Optional[bool]:\n',
    '        """사이클당 텔레그램 알림 발송 제한(CAP=1) 및 우선순위 공급(Plan B\')을 적용하는 게이트:\n',
    '        - ORDER: 손절 매도 주문 결과 알림 (인라인 슬롯 최우선 선점)\n',
    '        - REMINDER: 당일 손절 잠금 리마인더 (주문 결과에 인라인 슬롯을 무조건 양보하고 미경합 시 승격)\n',
    '        - NORMAL: 일반 경보 알림\n',
    '        """\n',
    '        # [B\'안 우선순위]: REMINDER는 무조건 지연 큐에 편입하여 주문 알림에 인라인 슬롯 양보\n',
    '        if priority == "REMINDER":\n',
    '            self._stop_loss_telegram_deferred_alerts.append(msg)\n',
    '            return True\n',
    '\n',
    '        # NORMAL: 이미 지연 큐에 리마인더 등이 대기 중이면 순위 역전 방지를 위해 지연 큐에 적재\n',
    '        if priority == "NORMAL" and self._stop_loss_telegram_deferred_alerts:\n',
    '            self._stop_loss_telegram_deferred_alerts.append(msg)\n',
    '            return True\n',
]

lines[933:964] = new_gated_lines

# Re-locate _process_locked_tickers_daily_reminders
proc_idx = -1
for i, l in enumerate(lines):
    if "def _process_locked_tickers_daily_reminders" in l:
        proc_idx = i
        break
assert proc_idx != -1, "def _process_locked_tickers_daily_reminders not found"

# Locate _monitor_and_execute_single_holding
mon_idx = -1
for i, l in enumerate(lines):
    if "def _monitor_and_execute_single_holding" in l:
        mon_idx = i
        break
assert mon_idx != -1, "def _monitor_and_execute_single_holding not found"

new_reminders_lines = [
    '    def _process_locked_tickers_daily_reminders(self, is_dry_run: bool) -> None:\n',
    '        """영구 잠금 종목 독립 순회 및 개장 시 1일 1회 데일리 리마인더 발송"""\n',
    '        # [LOCKED_TICKER_DAILY_REMINDER_INDEPENDENT]\n',
    '        # holdings 루프와 무관하게 모든 영구 잠금 종목을 직접 독립 순회하여\n',
    '        # 해당 종목 시장 개장 시 데일리 리마인더 알림 발송 (종목별 1일 1회)\n',
    '        for locked_ticker, lock_reason in list(self._stop_loss_locked_tickers.items()):\n',
    '            locked_session = get_session_date_for_ticker(locked_ticker)\n',
    '            if not is_market_open_for_ticker(locked_ticker):\n',
    '                continue\n',
    '            if self._stop_loss_lock_daily_alert.get(locked_ticker) != locked_session:\n',
    '                logger.critical(f"🚨 [LOCKED_TICKER_DAILY_REMINDER] {locked_ticker} is locked: {lock_reason}")\n',
    '                # [INLINE_TELEGRAM_SENT_CONSUMER_1] sent 소비 지점 1: 인라인 성공 및 제한 계산 포함 (통계 왜곡 방지)\n',
    '                sent = self._send_stop_loss_telegram_gated(\n',
    '                    f"🚨🚨 *{ALERT_TAG_LOCKED_TICKER_DAILY_REMINDER}* {locked_ticker} 종목이 리스크 오류로 손절 잠금 상태입니다.\\n"\n',
    '                    f"사유: {lock_reason}\\n"\n',
    '                    f"HTS/MTS 수동 확인 및 data/stop_loss_state.json 수동 잠금 해제가 필요합니다.",\n',
    '                    priority="REMINDER",\n',
    '                )\n',
    '                # [3-STATE_REMINDER_GUARD] 지연 큐 편입(True/None) 시 임시 마커 설정 (사이클 종료 시 승격/요약 발송 결과로 확정/롤백)\n',
    '                if sent is not False:\n',
    '                    self._stop_loss_lock_daily_alert[locked_ticker] = locked_session\n',
    '\n',
    '\n',
]

lines[proc_idx:mon_idx] = new_reminders_lines

# Re-locate _flush_deferred_summary_alerts
flush_idx = -1
for i, l in enumerate(lines):
    if "def _flush_deferred_summary_alerts" in l:
        flush_idx = i
        break
assert flush_idx != -1, "def _flush_deferred_summary_alerts not found"

# Locate 'to_flush = list(self._stop_loss_telegram_deferred_alerts)'
to_flush_idx = -1
for i in range(flush_idx, flush_idx + 60):
    if "to_flush = list(self._stop_loss_telegram_deferred_alerts)" in lines[i]:
        to_flush_idx = i
        break
assert to_flush_idx != -1, "to_flush line not found"

new_flush_prefix = [
    '    def _flush_deferred_summary_alerts(self) -> None:\n',
    '        try:\n',
    '            is_dry_run = get_auto_trader().get_status().get("dry_run", True)\n',
    '        except Exception:\n',
    '            is_dry_run = True\n',
    '        """상한 초과로 지연된 알림들을 엔트리 절단, 청크 분할 및 사후 가드를 거쳐 백그라운드 스레드로 비동기 발송"""\n',
    '        # [BACKLOG_17 / Blocking 1, 2, A, C] 사이클 종료 시 상한 초과 지연 알림 요약 병합 발송\n',
    '        # - 예외 발생 시에도 지연 알림 유실 방지를 위해 finally 블록에서 실행\n',
    '        with self._stop_loss_telegram_lock:\n',
    '            if not self._stop_loss_telegram_deferred_alerts:\n',
    '                return\n',
    '\n',
    '            # [BLOCKING_B] 지연 큐 내 단독 알림 1건 승격 발송 (인라인 슬롯 미소진 시)\n',
    '            # 지연 큐의 1번째 알림을 인라인 개별 알림으로 승격 발송하여 단독 경로 기존 거동 보존\n',
    '            if self._stop_loss_telegram_inline_count < STOP_LOSS_TELEGRAM_INLINE_CAP:\n',
    '                first_deferred = self._stop_loss_telegram_deferred_alerts.pop(0)\n',
    '                res = False\n',
    '                try:\n',
    '                    res = self._send_telegram(first_deferred)\n',
    '                    if res is not None:\n',
    '                        self._stop_loss_telegram_inline_count += 1\n',
    '                except Exception as promo_err:\n',
    '                    logger.error(f"🚨 [PROMOTED_ALERT_SEND_FAIL] Failed promoted alert: {mask_sensitive_info(str(promo_err))}")\n',
    '                    # 예외 발생 시 드롭 방지를 위해 지연 목록 선두로 원복하여 요약 알림에 편입\n',
    '                    self._stop_loss_telegram_deferred_alerts.insert(0, first_deferred)\n',
    '\n',
    '                # [3-STATE_REMINDER_POST_GUARD] 승격된 알림이 리마인더인 경우 3-State 상태 확정 및 롤백\n',
    '                if ALERT_TAG_LOCKED_TICKER_DAILY_REMINDER in first_deferred:\n',
    '                    for locked_ticker in list(self._stop_loss_locked_tickers.keys()):\n',
    '                        if locked_ticker in first_deferred:\n',
    '                            if res is False:\n',
    '                                logger.critical(f"🚨 [LOCKED_TICKER_REMINDER_SEND_FAIL] Failed reminder delivery for {locked_ticker}, will retry")\n',
    '                                self._stop_loss_lock_daily_alert.pop(locked_ticker, None)\n',
    '                            elif res is None:\n',
    '                                logger.critical(f"🚨 [LOCKED_TICKER_REMINDER_DISABLED] Telegram notifier disabled; skipped reminder for {locked_ticker}, daily alert marked")\n',
    '                                if not is_dry_run:\n',
    '                                    self._save_stop_loss_state()\n',
    '                            else:\n',
    '                                if not is_dry_run:\n',
    '                                    self._save_stop_loss_state()\n',
    '                            break\n',
    '\n',
    '                # 승격 후 남은 지연 알림이 없으면 요약 알림 없이 종료\n',
    '                if not self._stop_loss_telegram_deferred_alerts:\n',
    '                    return\n',
    '\n',
    '            to_flush = list(self._stop_loss_telegram_deferred_alerts)\n',
    '            self._stop_loss_telegram_deferred_alerts.clear()\n',
    '            # [3-STATE_REMINDER_POST_GUARD] 요약 알림으로 병합 발송되는 리마인더 상태 확정\n',
    '            for msg_item in to_flush:\n',
    '                if ALERT_TAG_LOCKED_TICKER_DAILY_REMINDER in msg_item:\n',
    '                    for locked_ticker in list(self._stop_loss_locked_tickers.keys()):\n',
    '                        if locked_ticker in msg_item:\n',
    '                            if not is_dry_run:\n',
    '                                self._save_stop_loss_state()\n',
    '                            break\n',
]

# Find clear line
clear_idx = to_flush_idx + 1
while clear_idx < len(lines) and "self._stop_loss_telegram_deferred_alerts.clear()" not in lines[clear_idx]:
    clear_idx += 1
clear_idx += 1 # include the clear line

lines[flush_idx:clear_idx] = new_flush_prefix

with open(target_sched, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(lines)

print("scheduler.py patched successfully!")

# ==========================================
# 2. Patch tests/test_stop_loss_priority_slot.py
# ==========================================
with open(target_test, "r", encoding="utf-8") as f:
    t_lines = f.readlines()

t_fn_idx = -1
for i, l in enumerate(t_lines):
    if "def test_order_alert_preempts_locked_reminder_inline_slot():" in l:
        t_fn_idx = i
        break
assert t_fn_idx != -1, "test_order_alert_preempts_locked_reminder_inline_slot not found"

# Replace signature with monkeypatch
t_lines[t_fn_idx] = "def test_order_alert_preempts_locked_reminder_inline_slot(monkeypatch):\n"

# Replace sched._send_telegram = mock_send with monkeypatch.setattr
for i in range(t_fn_idx, t_fn_idx + 40):
    if "sched._send_telegram = mock_send" in t_lines[i]:
        t_lines[i] = "    monkeypatch.setattr(sched, '_send_telegram', mock_send)\n"
    if "sched._stop_loss_locked_tickers = {" in t_lines[i]:
        t_lines[i] = "    monkeypatch.setattr(sched, '_stop_loss_locked_tickers', {\n"
    if 'sched._stop_loss_lock_daily_alert = {}' in t_lines[i]:
        t_lines[i] = "    monkeypatch.setattr(sched, '_stop_loss_lock_daily_alert', {})\n"

with open(target_test, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(t_lines)

print("test_stop_loss_priority_slot.py patched successfully!")

# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding='utf-8')
target_file = r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

g_start = -1
g_end = -1
for i, l in enumerate(lines):
    if "def _send_stop_loss_telegram_gated" in l:
        g_start = i
    if g_start != -1 and i > g_start:
        if "if self._stop_loss_telegram_inline_count < STOP_LOSS_TELEGRAM_INLINE_CAP:" in l:
            g_end = i
            break

assert g_start != -1 and g_end != -1, f"boundaries not found: {g_start}, {g_end}"

new_lines = [
    '    def _send_stop_loss_telegram_gated(self, msg: str, priority: str = "NORMAL") -> Optional[bool]:\n',
    '        """사이클당 텔레그램 인라인 전송 상한(CAP=1) 및 우선순위 등급제(B\'안)를 적용하는 게이트:\n',
    '        - ORDER: 손절 매도 주문 결과 알림 (인라인 슬롯 최우선 선점)\n',
    '        - REMINDER: 일일 손절 잠금 리마인더 (주문 결과에 인라인 슬롯을 양보하고 미경합 시 승격)\n',
    '        - NORMAL: 일반 경보 알림\n',
    '        """\n',
    '        # 1. 텔레그램 비활성 가드 (I/O 시도 없이 즉시 반환)\n',
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
    '            self._stop_loss_telegram_deferred_alerts.append(msg)\n',
    '            return True\n',
    '\n',
    '        # NORMAL: 이미 지연 큐에 리마인더 등이 대기 중이면 순위 역전 방지를 위해 지연 큐 적재\n',
    '        if priority == "NORMAL" and self._stop_loss_telegram_deferred_alerts:\n',
    '            self._stop_loss_telegram_deferred_alerts.append(msg)\n',
    '            return True\n',
    '\n',
]

lines[g_start:g_end] = new_lines

with open(target_file, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(lines)

print(f"Updated lines {g_start} to {g_end} successfully!")

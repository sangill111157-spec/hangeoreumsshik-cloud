import sys
sys.stdout.reconfigure(encoding='utf-8')

target_file = r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py"

with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# 40초 상한선 상수 정의 추가
target_def = '''    def job_stop_loss_monitor(self):
        """손절 모니터링 작업 (매 1분) - Fail-closed 및 엄격한 3-State/3-Strike/1시간 재알림 체계"""
        job_name = "stop_loss_monitor"
        t_scan_start = time.perf_counter()'''

replacement_def = '''    def job_stop_loss_monitor(self):
        """손절 모니터링 작업 (매 1분) - Fail-closed 및 40초 상한선/3회 재알림/복구알림 체계"""
        job_name = "stop_loss_monitor"
        t_scan_start = time.perf_counter()
        STOP_LOSS_SCAN_TIMEOUT_SEC = 40.0'''

assert target_def in code, "target_def not found"
code = code.replace(target_def, replacement_def, 1)

# 루프 순회 시 40초 상한선 검사 추가
target_loop = '''            scan_backoff_spent = 0.0
            for item in holdings:
                scan_backoff_spent = self._monitor_and_execute_single_holding('''

replacement_loop = '''            scan_backoff_spent = 0.0
            for item in holdings:
                # [40초 상한선 검사] 시간 초과 시 즉시 중단 및 긴급 알림
                if time.perf_counter() - t_scan_start > STOP_LOSS_SCAN_TIMEOUT_SEC:
                    elapsed = time.perf_counter() - t_scan_start
                    abort_msg = (
                        f"🚨🚨 *[손절 감시 40초 상한선 초과로 중단]*\\n"
                        f"손절 감시 작업이 {elapsed:.1f}초 동안 지연되어 안전을 위해 즉시 중단되었습니다.\\n"
                        f"조치: 증권사 API 응답 지연 여부를 확인하십시오."
                    )
                    logger.critical(abort_msg)
                    self._send_telegram(abort_msg)
                    return

                scan_backoff_spent = self._monitor_and_execute_single_holding('''

assert target_loop in code, "target_loop not found"
code = code.replace(target_loop, replacement_loop, 1)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(code)

print("SUCCESS: 40s timeout logic added to scheduler.py")

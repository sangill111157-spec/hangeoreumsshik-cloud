import re

target_file = r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py"

with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# 1. 1시간 묵음(3600.0) 2곳 수정 및 연속 3회 실패 재알림 / 복구 알림
# 첫 번째: KIS 계좌 잔고 스캔 실패 (라인 924 부근)
old_scan_fail = '''                    last_alert = getattr(self, "_stop_loss_scan_fail_last_alert", 0.0)
                    if time.time() - last_alert >= 3600.0:
                        self._send_telegram(
                            f"🚨 *[손절 감시 계좌 스캔 일시 실패]* KIS 계좌 잔고 조회 실패: {scan_err}\\n"
                            f"기존 캐시({len(active_tickers)}종목)로 모니터링을 지속합니다."
                        )
                        self._stop_loss_scan_fail_last_alert = time.time()'''

new_scan_fail = '''                    self._stop_loss_scan_consecutive_fails = getattr(self, "_stop_loss_scan_consecutive_fails", 0) + 1
                    # 1시간 묵음 제거 -> 3회 연속 실패 시 즉시 재알림
                    if self._stop_loss_scan_consecutive_fails >= 3:
                        msg = format_telegram_alert(
                            level="긴급",
                            is_paper=is_dry_run,
                            title="손절 감시 계좌 스캔 3회 연속 실패",
                            impact=f"KIS 계좌 잔고 조회가 {self._stop_loss_scan_consecutive_fails}회 연속 실패했습니다.",
                            action="증권사 점검 또는 네트워크 상태 확인 필요",
                            tech_info=str(scan_err)
                        )
                        logger.critical(msg)
                        self._send_telegram(msg)
                    elif self._stop_loss_scan_consecutive_fails == 1:
                        msg = format_telegram_alert(
                            level="주의",
                            is_paper=is_dry_run,
                            title="손절 감시 계좌 스캔 1회 실패",
                            impact="기존 캐시 잔고로 모니터링을 임시 지속합니다.",
                            action="자동 재시도 대기",
                            tech_info=str(scan_err)
                        )
                        logger.warning(msg)
                        self._send_telegram(msg)'''

if old_scan_fail in code:
    code = code.replace(old_scan_fail, new_scan_fail, 1)
    print("SUCCESS: replaced old_scan_fail")
else:
    print("WARNING: old_scan_fail not matched")

# 두 번째: ticker 개별 계좌 조회 실패 (라인 1344 부근)
old_fetch_fail = '''                        last_alert = self._stop_loss_fetch_fail_last_alert.get(ticker, 0.0)
                        if time.time() - last_alert >= 3600.0:
                            self._send_stop_loss_telegram_gated(
                                f"🚨 *[손절 감시 단일 조회 일시 실패]* {ticker} 계좌 잔고 조회 실패: {acc_err}\\n"
                                f"기존 평단가({entry_price:.2f})로 모니터링을 지속합니다."
                            )
                            self._stop_loss_fetch_fail_last_alert[ticker] = time.time()'''

new_fetch_fail = '''                        fails = self._stop_loss_fetch_fail_count.get(ticker, 0) + 1
                        self._stop_loss_fetch_fail_count[ticker] = fails
                        # 1시간 묵음 제거 -> 3회 연속 실패 시 즉시 재알림
                        if fails >= 3:
                            msg = format_telegram_alert(
                                level="긴급",
                                is_paper=is_dry_run,
                                title=f"손절 감시 {ticker} 잔고 조회 3회 연속 실패",
                                impact=f"{ticker} 평단가 갱신 불가, 손절 모니터링 위험",
                                action="수동 잔고 확인 요망",
                                tech_info=str(acc_err)
                            )
                            logger.critical(msg)
                            self._send_telegram(msg)
                        elif fails == 1:
                            msg = format_telegram_alert(
                                level="주의",
                                is_paper=is_dry_run,
                                title=f"손절 감시 {ticker} 잔고 조회 1회 실패",
                                impact=f"기존 평단가({entry_price:.2f})로 임시 지속",
                                action="자동 재시도 대기",
                                tech_info=str(acc_err)
                            )
                            logger.warning(msg)
                            self._send_telegram(msg)'''

if old_fetch_fail in code:
    code = code.replace(old_fetch_fail, new_fetch_fail, 1)
    print("SUCCESS: replaced old_fetch_fail")
else:
    print("WARNING: old_fetch_fail not matched")

# 복구 알림 로직: 스캔 성공 시 이전에 실패 상태였으면 복구 알림 발송
old_scan_success = '''            # [10B_SSOT_SCAN] 정상 조회 성공: active_tickers 및 positions_detail 캐시 갱신'''
new_scan_success = '''            # [10B_SSOT_SCAN] 정상 조회 성공: 복구 감지 시 복구 알림 전송
            if getattr(self, "_stop_loss_scan_consecutive_fails", 0) > 0:
                rec_msg = format_telegram_alert(
                    level="정보",
                    is_paper=is_dry_run,
                    title="손절 감시 계좌 스캔 정상 복구",
                    impact="KIS 계좌 잔고 조회가 정상 재개되었습니다.",
                    action="정상 자동매매 및 손절 감시 진행 중"
                )
                logger.info(rec_msg)
                self._send_telegram(rec_msg)
                self._stop_loss_scan_consecutive_fails = 0

            # [10B_SSOT_SCAN] 정상 조회 성공: active_tickers 및 positions_detail 캐시 갱신'''

if old_scan_success in code:
    code = code.replace(old_scan_success, new_scan_success, 1)
    print("SUCCESS: replaced old_scan_success")
else:
    print("WARNING: old_scan_success not matched")

# 40초 상한선: STOP_LOSS_SCAN_TIMEOUT_SEC = 40.0
# job_stop_loss_monitor 시작 부분에 상한선 체크
old_job_start = '''    def job_stop_loss_monitor(self):
        """손절 모니터링 작업 (매 1분) - Fail-closed 및 강화된 3-State/3-Strike/1시간 재알림 체계"""
        job_name = "stop_loss_monitor"
        t_scan_start = time.perf_counter()'''

new_job_start = '''    def job_stop_loss_monitor(self):
        """손절 모니터링 작업 (매 1분) - Fail-closed 및 40초 시간 상한선 적용"""
        job_name = "stop_loss_monitor"
        t_scan_start = time.perf_counter()
        STOP_LOSS_MAX_TIMEOUT_SEC = 40.0'''

if old_job_start in code:
    code = code.replace(old_job_start, new_job_start, 1)
    print("SUCCESS: replaced old_job_start")
else:
    print("WARNING: old_job_start not matched")

# 루프 순회 중 40초 초과 시 중단 및 긴급 알림
old_loop_check = '''            for ticker in active_tickers:
                try:'''
new_loop_check = '''            for ticker in active_tickers:
                # 40초 상한선 검사: 초과 시 즉시 중단 및 [긴급] 알림
                if time.perf_counter() - t_scan_start > STOP_LOSS_MAX_TIMEOUT_SEC:
                    elapsed = time.perf_counter() - t_scan_start
                    abort_msg = format_telegram_alert(
                        level="긴급",
                        is_paper=is_dry_run,
                        title="손절 감시 40초 상한선 초과로 작업 강제 중단",
                        impact=f"손절 감시 작업이 {elapsed:.1f}초 동안 지연되어 다음 주기를 위해 안전 중단되었습니다.",
                        action="증권사 API 지연 확인 및 네트워크 상태 점검 필요",
                        tech_info=f"elapsed={elapsed:.2f}s > limit={STOP_LOSS_MAX_TIMEOUT_SEC}s"
                    )
                    logger.critical(abort_msg)
                    self._send_telegram(abort_msg)
                    return

                try:'''

if old_loop_check in code:
    code = code.replace(old_loop_check, new_loop_check, 1)
    print("SUCCESS: replaced old_loop_check")
else:
    print("WARNING: old_loop_check not matched")

# 미국장 기준 생존 신호 메소드 추가
heartbeat_method = '''
    def job_us_market_heartbeat(self, stage: str = "PRE_MARKET"):
        """미국 정규장 기준 생존 신호 전송 (개장 전 30분, 마감 후 30분, 서머타임 EDT/EST 자동 반영)"""
        try:
            from zoneinfo import ZoneInfo
        except ImportError:
            from backports.zoneinfo import ZoneInfo
        
        now_ny = datetime.now(ZoneInfo("America/New_York"))
        is_dst = bool(now_ny.dst())
        tz_name = "EDT (서머타임)" if is_dst else "EST (표준시)"
        now_kst = datetime.now(KST)

        trader = get_auto_trader()
        is_dry_run = trader.get_status().get("dry_run", True)

        stage_desc = "미국 정규장 개장 전(09:00 ET)" if stage == "PRE_MARKET" else "미국 정규장 마감 후(16:30 ET)"
        msg = format_telegram_alert(
            level="정보",
            is_paper=is_dry_run,
            title=f"시스템 생존 신호 - {stage_desc}",
            impact="스케줄러 및 자동매매 엔진 정상 가동 중",
            action="정상 모니터링 진행 중",
            tech_info=f"NY: {now_ny.strftime('%Y-%m-%d %H:%M:%S')} {tz_name} | KST: {now_kst.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        logger.info(msg)
        self._send_telegram(msg)
'''

if "def job_us_market_heartbeat" not in code:
    # run_job_manually 앞에 삽입
    target_point = "    def run_job_manually(self, job_id: str) -> bool:"
    code = code.replace(target_point, heartbeat_method + "\n" + target_point, 1)
    print("SUCCESS: added job_us_market_heartbeat")

# job_map에 us_market_heartbeat 등록
old_job_map = '''        job_map = {
            "hourly_scan": self.job_hourly_scan,
            "daily_analysis": self.job_daily_analysis,
            "stop_loss_monitor": self.job_stop_loss_monitor,
            "weekly_report": self.job_weekly_report
        }'''
new_job_map = '''        job_map = {
            "hourly_scan": self.job_hourly_scan,
            "daily_analysis": self.job_daily_analysis,
            "stop_loss_monitor": self.job_stop_loss_monitor,
            "weekly_report": self.job_weekly_report,
            "us_market_heartbeat": self.job_us_market_heartbeat
        }'''
if old_job_map in code:
    code = code.replace(old_job_map, new_job_map, 1)
    print("SUCCESS: updated job_map")

with open(target_file, "w", encoding="utf-8") as f:
    f.write(code)

print("ALL DONE: scheduler.py updated successfully")

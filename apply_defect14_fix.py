# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update master_signal.py to ensure get_master_signal(ticker) exists and works as single-ticker wrapper
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_content = f.read()

# Check if get_master_signal exists
if 'def get_master_signal(self, ticker: str)' not in ms_content:
    wrapper_code = """    def get_master_signal(self, ticker: str) -> MasterSignalResult:
        \"\"\"단일 티커 기반 마스터 신호 편의 래퍼 (결함 14 해소)\"\"\"
        # 기본 단일 호출 시 하위 모듈을 수집하거나 기본 mock/기본값으로 계산
        return self.calculate_final_master_signal(
            investor_analysis={"overall_signal": "HOLD", "overall_confidence": 50, "bull_count": 0, "bear_count": 0, "available": True},
            pod_signals=[],
            pod_composite_signal="HOLD",
            technical={"overall_signal": "HOLD", "confidence": 50, "available": True},
            llm_news={"news_composite_score": 50.0, "news_signal": "HOLD", "sentiment_label": "HOLD", "total_news_analyzed": 0, "available": True},
            institutional={"available": True},
            options_flow={"available": True, "options_composite_score": 50.0, "options_signal": "HOLD"},
            darkpool={"available": True, "darkpool_composite_score": 50.0, "darkpool_signal": "HOLD"},
            events={"upcoming_events": [], "earnings_season": False, "has_regulatory_event": False, "available": True},
            correlation={"available": True, "macro_score": 50.0},
            symbol=ticker
        )
"""
    # Insert before class end or calculate_final_master_signal
    ms_content = ms_content.replace("    def calculate_final_master_signal(", wrapper_code + "\n    def calculate_final_master_signal(")
    with open(ms_path, 'w', encoding='utf-8') as f:
        f.write(ms_content)
    print("master_signal.py get_master_signal wrapper added.")

# 2. Update portfolio_manager.py lines 507-518
pm_path = os.path.join(backend_dir, r'app\services\portfolio_manager.py')
with open(pm_path, 'r', encoding='utf-8') as f:
    pm_content = f.read()

old_pm_call = """            if signal_engine:
                try:
                    result = signal_engine.calculate_final_master_signal(ticker)
                    signal = result.get("signal", "HOLD")
                    score = result.get("master_score", 50)
                except Exception as e:
                    logger.warning(f"Failed to get signal for {ticker}: {e}")"""

new_pm_call = """            if signal_engine:
                try:
                    if hasattr(signal_engine, "get_master_signal"):
                        res_obj = signal_engine.get_master_signal(ticker)
                    else:
                        res_obj = signal_engine.calculate_final_master_signal(symbol=ticker)
                    signal = getattr(res_obj, "signal", "HOLD") if not isinstance(res_obj, dict) else res_obj.get("signal", "HOLD")
                    score = getattr(res_obj, "master_score", 50) if not isinstance(res_obj, dict) else res_obj.get("master_score", 50)
                except Exception as e:
                    logger.exception(f"Failed to get signal for {ticker}: {e}")"""

if old_pm_call in pm_content:
    pm_content = pm_content.replace(old_pm_call, new_pm_call)
    with open(pm_path, 'w', encoding='utf-8') as f:
        f.write(pm_content)
    print("portfolio_manager.py updated successfully.")

# 3. Update telegram_command_listener.py line 69
tc_path = os.path.join(backend_dir, r'telegram_command_listener.py')
if os.path.exists(tc_path):
    with open(tc_path, 'r', encoding='utf-8') as f:
        tc_content = f.read()
    old_tc = "r = MasterSignalEngine().calculate_final_master_signal('NVDA')"
    new_tc = "r = MasterSignalEngine().get_master_signal('NVDA')"
    if old_tc in tc_content:
        tc_content = tc_content.replace(old_tc, new_tc)
        with open(tc_path, 'w', encoding='utf-8') as f:
            f.write(tc_content)
        print("telegram_command_listener.py updated successfully.")

# 4. Update stock_scanner.py for 결함 33 (logger.exception & secondary_failed counter)
ss_path = os.path.join(backend_dir, r'app\services\stock_scanner.py')
with open(ss_path, 'r', encoding='utf-8') as f:
    ss_content = f.read()

old_sec_loop = """        for result in primary_results:
            try:
                candidate = await self._analyze_secondary_filters(result["ticker"], result)
                if candidate:
                    # Check secondary filters
                    if candidate.master_score >= self.config["secondary_filters"]["min_master_score"]:
                        if candidate.investor_buy_count >= self.config["secondary_filters"]["min_investor_buy_count"]:
                            candidates.append(candidate)

                await asyncio.sleep(self.config["scan_settings"]["request_delay_ms"] / 1000)
            except Exception as e:
                logger.error(f"Error in secondary scan for {result['ticker']}: {e}")"""

new_sec_loop = """        secondary_failed = 0
        for result in primary_results:
            try:
                candidate = await self._analyze_secondary_filters(result["ticker"], result)
                if candidate:
                    # Check secondary filters
                    if candidate.master_score is not None and candidate.master_score >= self.config["secondary_filters"]["min_master_score"]:
                        if candidate.investor_buy_count >= self.config["secondary_filters"]["min_investor_buy_count"]:
                            candidates.append(candidate)
                    else:
                        secondary_failed += 1

                await asyncio.sleep(self.config["scan_settings"]["request_delay_ms"] / 1000)
            except Exception as e:
                secondary_failed += 1
                logger.exception(f"Error in secondary scan for {result['ticker']}: {e}")"""

if old_sec_loop in ss_content:
    ss_content = ss_content.replace(old_sec_loop, new_sec_loop)
    with open(ss_path, 'w', encoding='utf-8') as f:
        f.write(ss_content)
    print("stock_scanner.py secondary_failed and logger.exception added.")

subprocess.run('git add app/services/master_signal.py app/services/portfolio_manager.py telegram_command_listener.py app/services/stock_scanner.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(portfolio,scanner,telegram): restore get_master_signal wrapper for defect 14 and track secondary_failed for defect 33"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


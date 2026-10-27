# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sched_file = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')

with open(sched_file, 'r', encoding='utf-8') as f:
    content = f.read()

old_accepted_block = """                        elif order_state == "ORDER_ACCEPTED":
                            # 성공 확정 시 카운터 초기화 및 잠금 해제
                            self._stop_loss_reject_count[ticker] = 0
                            self._stop_loss_locked_tickers.pop(ticker, None)
                            self._save_stop_loss_state()

                            # 미체결/잔량 점검: LIVE 모드 execute_trade 직후 잔량 확인
                            if not is_dry_run:
                                try:
                                    post_portfolio = portfolio.get_portfolio_summary()
                                    post_holdings = post_portfolio.get("holdings", [])
                                    rem_pos = next((h for h in post_holdings if h['ticker'] == ticker), None)
                                    rem_shares = rem_pos.get("shares", 0) if rem_pos else 0
                                    if rem_shares > 0:
                                        logger.critical(f"🚨 [PARTIAL_FILL_WARNING] {ticker} stop-loss executed but {rem_shares} shares remain!")
                                        self._send_telegram(
                                            f"🚨 *[긴급 손절 잔여 수량 발생]* {ticker} 손절 주문 후 {rem_shares}주 미체결 잔량이 남아있습니다. HTS/MTS를 확인하십시오."
                                        )
                                except Exception as pe:
                                    logger.error(f"Failed to check post-stop-loss holdings: {pe}")"""

new_accepted_block = """                        elif order_state == "ORDER_ACCEPTED":
                            # 성공 확정 시 카운터 초기화 및 잠금 해제
                            self._stop_loss_reject_count[ticker] = 0
                            self._stop_loss_locked_tickers.pop(ticker, None)
                            self._save_stop_loss_state()

                            # 체결 접수 성공 알림 전송
                            order_id = trade_result.get("order_id", "")
                            self._send_telegram(
                                f"✅ *[긴급 손절 주문 접수 완료]* {ticker} {shares}주 손절 매도 주문이 접수되었습니다."
                                f"{f' (주문ID: `{order_id}`)' if order_id else ''}"
                            )

                            # 미체결/잔량 점검: LIVE 모드 execute_trade 직후 잔량 확인
                            if not is_dry_run:
                                try:
                                    post_portfolio = portfolio.get_portfolio_summary()
                                    post_holdings = post_portfolio.get("holdings", [])
                                    rem_pos = next((h for h in post_holdings if h['ticker'] == ticker), None)
                                    rem_shares = rem_pos.get("shares", 0) if rem_pos else 0
                                    if rem_shares > 0:
                                        logger.critical(f"🚨🚨 [PARTIAL_FILL_WARNING] {ticker} stop-loss executed but {rem_shares} shares remain!")
                                        self._send_telegram(
                                            f"🚨🚨 *[긴급 손절 잔여 수량 발생 - 수동 개입 필요]* {ticker} 손절 주문 후 {rem_shares}주 미체결 잔량이 남아있습니다! 즉시 HTS/MTS를 확인하십시오."
                                        )
                                except Exception as pe:
                                    logger.error(f"Failed to check post-stop-loss holdings: {pe}")"""

if old_accepted_block in content:
    content = content.replace(old_accepted_block, new_accepted_block)
    with open(sched_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated ORDER_ACCEPTED notification & remaining shares critical alert in scheduler.py")
else:
    print("WARNING: old_accepted_block not matched exactly!")

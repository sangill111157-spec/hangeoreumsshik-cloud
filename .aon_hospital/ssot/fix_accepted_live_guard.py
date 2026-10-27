# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sched_file = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')

with open(sched_file, 'r', encoding='utf-8') as f:
    content = f.read()

old_accepted = """                        elif order_state == "ORDER_ACCEPTED":
                            # 성공 확정 시 카운터 초기화 및 잠금 해제
                            self._stop_loss_reject_count[ticker] = 0
                            self._stop_loss_locked_tickers.pop(ticker, None)
                            self._save_stop_loss_state()

                            # 체결 접수 성공 알림 전송
                            order_id = trade_result.get("order_id", "")
                            self._send_telegram(
                                f"✅ *[긴급 손절 주문 접수 완료]* {ticker} {shares}주 손절 매도 주문이 접수되었습니다."
                                f"{f' (주문ID: `{order_id}`)' if order_id else ''}"
                            )"""

new_accepted = """                        elif order_state == "ORDER_ACCEPTED":
                            # 성공 확정 시 카운터 초기화 및 잠금 해제
                            self._stop_loss_reject_count[ticker] = 0
                            self._stop_loss_locked_tickers.pop(ticker, None)
                            self._save_stop_loss_state()

                            # 체결 접수 성공 알림 전송 (LIVE 모드에서만 전송, DRY_RUN은 사전 발동 알림 세션 1회로 억제)
                            if not is_dry_run:
                                order_id = trade_result.get("order_id", "")
                                self._send_telegram(
                                    f"✅ *[긴급 손절 주문 접수 완료]* {ticker} {shares}주 손절 매도 주문이 접수되었습니다."
                                    f"{f' (주문ID: `{order_id}`)' if order_id else ''}"
                                )"""

if old_accepted in content:
    content = content.replace(old_accepted, new_accepted)
    with open(sched_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated ORDER_ACCEPTED alert with live-only guard in scheduler.py")
else:
    print("WARNING: old_accepted block not matched")

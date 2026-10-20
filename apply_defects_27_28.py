# -*- coding: utf-8 -*-
import sys, os, subprocess
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Apply 결함 27 to master_signal.py
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_content = f.read()

old_norm = """        def _norm_sig(sig) -> str:
            if not sig:
                return "HOLD"
            s = str(sig).upper()
            return "HOLD" if s in ["NEUTRAL", "NONE", "N/A"] else s"""

new_norm = '''        def _norm_sig(sig) -> str:
            if not sig:
                return "UNAVAILABLE"
            s = str(sig).strip()
            ko_map = {
                "강력매수": "STRONG_BUY", "적극매수": "STRONG_BUY",
                "매수": "BUY", "보유": "HOLD", "중립": "HOLD",
                "매도": "SELL", "강력매도": "STRONG_SELL"
            }
            if s in ko_map:
                return ko_map[s]
            norm = s.upper().replace(" ", "_").replace("-", "_")
            if norm in ["NONE", "N/A", "NULL", "UNAVAILABLE"]:
                return "UNAVAILABLE"
            if norm in ["NEUTRAL"]:
                return "HOLD"
            valid_signals = {"STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL", "UNAVAILABLE"}
            return norm if norm in valid_signals else "UNAVAILABLE"'''

if old_norm in ms_content:
    ms_content = ms_content.replace(old_norm, new_norm)
    with open(ms_path, 'w', encoding='utf-8') as f:
        f.write(ms_content)
    print("master_signal.py _norm_sig updated successfully.")
else:
    print("Warning: old_norm not matched directly.")

# 2. Apply 결함 28 to auto_trader.py
at_path = os.path.join(backend_dir, r'app\services\auto_trader.py')
with open(at_path, 'r', encoding='utf-8') as f:
    at_content = f.read()

old_at_block = """        # 2. 가격 조회
        price_data = await self._broker.get_stock_price(symbol)
        if not price_data or not price_data.get("success"):
            logger.warning(f"Failed to get price for {symbol}")
            return None

        current_price = price_data.get("current_price", 0)"""

new_at_block = """        # 2. 가격 조회 (결함 28 방어: 체결가 아닌 기준가 대체 시 주문 보류)
        price_data = await self._broker.get_stock_price(symbol)
        if not price_data or not price_data.get("success"):
            logger.warning(f"Failed to get price for {symbol}")
            return None

        if price_data.get("price_source") == "base" or price_data.get("is_halted_or_premarket"):
            logger.warning(f"Order held: {symbol} price is base/premarket, not live last price")
            return None

        current_price = price_data.get("current_price", 0)"""

if old_at_block in at_content:
    at_content = at_content.replace(old_at_block, new_at_block)
    with open(at_path, 'w', encoding='utf-8') as f:
        f.write(at_content)
    print("auto_trader.py price_source guard updated.")

# Git diff and commit
subprocess.run('git add app/services/master_signal.py app/services/auto_trader.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(signal,trader): enhance label normalization with ko/space support and guard against base_price orders"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

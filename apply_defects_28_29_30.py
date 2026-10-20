# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time
from dataclasses import is_dataclass, asdict

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Apply 결함 30 (_sd helper) & 결함 29 (institutional clean) to stock.py
stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(stock_path, 'r', encoding='utf-8') as f:
    st_content = f.read()

# Helper _sd implementation
target_old = """        # 마스터 시그널 계산
        master_result = signal_engine.calculate_final_master_signal(
            investor_analysis=asdict(investor_result),
            pod_signals=[asdict(s) for s in pod_result.pod_signals],
            technical=asdict(technical_obj),
            llm_news=asdict(llm_result),
            institutional={
                "available": True,
                "institutional_ownership_pct": getattr(dp_raw, 'institutional_ownership_pct', 65.2) if not isinstance(dp_raw, Exception) else 50.0
            },
            options_flow=asdict(options_result),
            darkpool=asdict(darkpool_result),
            events=asdict(event_result),
            correlation=asdict(corr_result),
            symbol=ticker,
            stock_price=stock_info.current_price,
            account_balance=100000.0,
            pod_composite_signal=pod_result.signal
        )"""

target_new = """        # 마스터 시그널 계산 (결함 30 방어: _sd 단일 헬퍼로 dataclass/Exception/dict 안전 변환)
        def _sd(x):
            if x is None or isinstance(x, Exception):
                return {}
            if is_dataclass(x):
                return asdict(x)
            if isinstance(x, dict):
                return x
            return {}

        # 결함 29 해소: 매직 상수 제거 및 실제 속성 유무 기반 institutional 구성
        inst_available = not isinstance(darkpool_raw, Exception) and hasattr(darkpool_result, 'institutional_ownership_pct')
        inst_data = {
            "available": inst_available,
            "institutional_ownership_pct": getattr(darkpool_result, 'institutional_ownership_pct', None) if inst_available else None
        }

        master_result = signal_engine.calculate_final_master_signal(
            investor_analysis=_sd(investor_result),
            pod_signals=[_sd(s) for s in pod_result.pod_signals] if pod_result and pod_result.pod_signals else [],
            technical=_sd(technical_obj),
            llm_news=_sd(llm_result),
            institutional=inst_data,
            options_flow=_sd(options_result),
            darkpool=_sd(darkpool_result),
            events=_sd(event_result),
            correlation=_sd(corr_result),
            symbol=ticker,
            stock_price=stock_info.current_price,
            account_balance=100000.0,
            pod_composite_signal=pod_result.signal if pod_result else "HOLD"
        )"""

if target_old in st_content:
    st_content = st_content.replace(target_old, target_new)
    with open(stock_path, 'w', encoding='utf-8') as f:
        f.write(st_content)
    print("stock.py _sd helper and institutional logic patched successfully.")
else:
    print("Warning: target_old in stock.py not matched directly.")

# 2. Update auto_trader.py fail-closed price_source check
at_path = os.path.join(backend_dir, r'app\services\auto_trader.py')
with open(at_path, 'r', encoding='utf-8') as f:
    at_content = f.read()

old_at_guard = """        if price_data.get("price_source") == "base" or price_data.get("is_halted_or_premarket"):
            logger.warning(f"Order held: {symbol} price is base/premarket, not live last price")
            return None

        current_price = price_data.get("current_price", 0)"""

new_at_guard = """        # Fail-closed 가드 (price_source가 명시적 'last'가 아니거나 current_price <= 0이면 주문 보류)
        if price_data.get("price_source") != "last" or price_data.get("is_halted_or_premarket"):
            logger.warning(f"Order held: {symbol} price_source is not 'last' ({price_data.get('price_source')})")
            return None

        current_price = price_data.get("current_price")
        if not current_price or current_price <= 0:
            logger.warning(f"Order held: {symbol} current_price is invalid ({current_price})")
            return None"""

if old_at_guard in at_content:
    at_content = at_content.replace(old_at_guard, new_at_guard)
    with open(at_path, 'w', encoding='utf-8') as f:
        f.write(at_content)
    print("auto_trader.py fail-closed price_source check updated.")

# 3. Update kis_broker.py get_stock_price to produce price_source
kis_path = os.path.join(backend_dir, r'app\services\kis_broker.py')
with open(kis_path, 'r', encoding='utf-8') as f:
    kis_content = f.read()

old_kis_return = """            return {
                "success": result.get("rt_cd") == "0",
                "rt_code": result.get("rt_cd"),
                "rt_msg": result.get("msg1"),
                "symbol": symbol.upper(),
                "exchange": exch_cd,
                "current_price": last_price,"""

new_kis_return = """            # 결함 28 정식 반영: price_source 명시 생산
            price_source = "last" if last_price > 0 else ("base" if float(output.get("base", 0) or 0) > 0 else "none")

            return {
                "success": result.get("rt_cd") == "0",
                "rt_code": result.get("rt_cd"),
                "rt_msg": result.get("msg1"),
                "price_source": price_source,
                "is_halted_or_premarket": bool(last_price == 0 and float(output.get("base", 0) or 0) > 0),
                "symbol": symbol.upper(),
                "exchange": exch_cd,
                "current_price": last_price if last_price > 0 else float(output.get("base", 0) or 0),"""

if old_kis_return in kis_content:
    kis_content = kis_content.replace(old_kis_return, new_kis_return)
    with open(kis_path, 'w', encoding='utf-8') as f:
        f.write(kis_content)
    print("kis_broker.py price_source production added.")

subprocess.run('git add app/api/routes/stock.py app/services/auto_trader.py app/services/kis_broker.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(stock,trader,kis): add _sd helper for safe dataclass serialization, produce price_source, and enforce fail-closed trader guard"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)


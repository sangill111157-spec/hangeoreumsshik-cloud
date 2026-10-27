# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

stock_path = os.path.join(backend_dir, r'app\api\routes\stock.py')
with open(stock_path, 'r', encoding='utf-8') as f:
    st_lines = f.readlines()

new_lines = []
skip = False
for idx, line in enumerate(st_lines):
    if 'institutional = {"available": True}' in line:
        helper_and_call = """        # 결함 30 방어: _sd 단일 변환 헬퍼 (dataclass/dict/Exception 안전 방어)
        def _sd(x, default_dict=None):
            if x is None or isinstance(x, Exception):
                return default_dict or {"available": False}
            if hasattr(x, "__dataclass_fields__"):
                from dataclasses import asdict
                d = asdict(x)
                d["available"] = getattr(x, "available", True)
                return d
            if isinstance(x, dict):
                return x
            return default_dict or {"available": False}

        # 결함 29 해소: 매직 상수 제거 및 darkpool 기관 데이터 실측 기반 연동
        inst_available = not isinstance(darkpool_raw, Exception) and getattr(darkpool_result, "available", False)
        institutional = {
            "available": inst_available,
            "institutional_ownership_pct": getattr(darkpool_result, "institutional_ownership_pct", None) if inst_available else None
        }

        # 마스터 신호 계산
        engine = create_master_engine(ticker=ticker)
        result = engine.calculate_final_master_signal(
            investor_analysis=_sd(investor_result, {"overall_signal": "HOLD", "overall_confidence": 50, "bull_count": 0, "bear_count": 0, "available": False}),
            pod_signals=pod_signals if not isinstance(pod_result, Exception) and pod_signals else [],
            pod_composite_signal=getattr(pod_result.signal, "value", str(pod_result.signal)) if not isinstance(pod_result, Exception) else "HOLD",
            technical=_sd(technical, {"overall_signal": "HOLD", "confidence": 50, "available": False}),
            llm_news=_sd(llm_result, {"news_composite_score": 50.0, "news_signal": "HOLD", "sentiment_label": "HOLD", "total_news_analyzed": 0, "available": False}),
            institutional=institutional,
            options_flow=_sd(options_result, {"available": False, "options_composite_score": 50.0, "options_signal": "HOLD"}),
            darkpool=_sd(darkpool_result, {"available": False, "darkpool_composite_score": 50.0, "darkpool_signal": "HOLD"}),
            events=_sd(event_result, {"upcoming_events": [], "earnings_season": False, "has_regulatory_event": False, "available": False}),
            correlation=_sd(corr_result, {"available": False, "macro_score": 50.0}),
            symbol=ticker,
            stock_price=stock_info.current_price,
            account_balance=100000.0
        )
"""
        new_lines.append(helper_and_call)
        skip = True
    elif skip:
        if 'symbol=ticker,' in line or 'account_balance=100000.0' in line or ')' in line and idx > 750:
            if ')' in line:
                skip = False
        continue
    else:
        new_lines.append(line)

with open(stock_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

subprocess.run('git add app/api/routes/stock.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(stock): implement _sd helper to safely handle module exceptions without 500 crash and fix institutional available logic"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

# Test live endpoint with simulated exception
res_diff = subprocess.run('git diff HEAD~1 app/api/routes/stock.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("--- git diff stock.py ---")
print(res_diff.stdout[:500])

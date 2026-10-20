import re

# 1. app/api/routes/stock.py 수정
with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8') as f:
    stock_code = f.read()

target_stock = '''        current_price = stock_info.current_price
        technical = analyzer.analyze(ticker, historical_data, current_price)

        return {
            "ticker": ticker,
            "current_price": current_price,
            "trend": technical.trend,
            "overall_signal": technical.overall_signal,
            "confidence": technical.confidence,
            "moving_averages": technical.moving_averages,
            "rsi": technical.rsi,
            "macd": technical.macd,
            "bollinger_bands": technical.bollinger_bands,
            "volume": technical.volume,
            "timestamp": datetime.now().isoformat()
        }'''

replacement_stock = '''        current_price = stock_info.current_price
        technical = analyzer.analyze(ticker, historical_data, current_price)
        is_avail = bool(getattr(technical, "available", False)) and (current_price is not None and current_price > 0)

        return {
            "ticker": ticker,
            "current_price": current_price if (current_price is not None and current_price > 0) else None,
            "available": is_avail,
            "trend": technical.trend if is_avail else None,
            "overall_signal": technical.overall_signal if is_avail else "UNAVAILABLE",
            "confidence": technical.confidence if is_avail else 0,
            "moving_averages": technical.moving_averages if is_avail else None,
            "rsi": technical.rsi if is_avail else None,
            "macd": technical.macd if is_avail else None,
            "bollinger_bands": technical.bollinger_bands if is_avail else None,
            "volume": technical.volume if is_avail else None,
            "timestamp": datetime.now().isoformat()
        }'''

if target_stock in stock_code:
    stock_code = stock_code.replace(target_stock, replacement_stock, 1)
    with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'w', encoding='utf-8') as f:
        f.write(stock_code)
    print("stock.py updated successfully")
else:
    print("stock.py target not found")

# 2. app/api/routes/risk.py 수정
with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\risk.py', 'r', encoding='utf-8') as f:
    risk_route_code = f.read()

target_risk_route = '''class RiskScoreResponse(BaseModel):
    score: int
    level: str
    level_color: str
    details: dict'''

replacement_risk_route = '''class RiskScoreResponse(BaseModel):
    score: Optional[int] = None
    level: str
    level_color: str
    details: dict
    available: bool = True'''

if target_risk_route in risk_route_code:
    risk_route_code = risk_route_code.replace(target_risk_route, replacement_risk_route, 1)
    with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\risk.py', 'w', encoding='utf-8') as f:
        f.write(risk_route_code)
    print("risk.py route updated successfully")
else:
    print("risk.py route target not found")

# 3. app/services/risk_monitor.py 수정 (데이터 없을 때 score: null, level: UNAVAILABLE)
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\risk_monitor.py', 'r', encoding='utf-8') as f:
    rm_code = f.read()

target_rm = '''            # 레벨 결정
            if total_score >= 60:
                level = "HIGH"
                color = "🔴"
            elif total_score >= 30:
                level = "MEDIUM"
                color = "🟡"
            else:
                level = "LOW"
                color = "🟢"

            return {
                "success": True,
                "data": {
                    "score": total_score,
                    "level": level,
                    "level_color": color,
                    "details": details
                }
            }'''

replacement_rm = '''            # 데이터 부재 판정 (포트폴리오 alerts도 없고 market 데이터도 없거나 부재할 때)
            has_market_data = market_result.get("success", False) and bool(market_result.get("data"))
            has_portfolio_data = portfolio_result.get("success", False) and bool(portfolio_result.get("data", {}).get("cash_ratio") is not None)

            if not has_market_data and not has_portfolio_data:
                return {
                    "success": True,
                    "data": {
                        "score": None,
                        "level": "UNAVAILABLE",
                        "level_color": "⚪",
                        "details": {},
                        "available": False
                    }
                }

            # 레벨 결정
            if total_score >= 60:
                level = "HIGH"
                color = "🔴"
            elif total_score >= 30:
                level = "MEDIUM"
                color = "🟡"
            else:
                level = "LOW"
                color = "🟢"

            return {
                "success": True,
                "data": {
                    "score": total_score,
                    "level": level,
                    "level_color": color,
                    "details": details,
                    "available": True
                }
            }'''

if target_rm in rm_code:
    rm_code = rm_code.replace(target_rm, replacement_rm, 1)
    with open(r'C:\trading\package\nvda_trading_system\backend\app\services\risk_monitor.py', 'w', encoding='utf-8') as f:
        f.write(rm_code)
    print("risk_monitor.py updated successfully")
else:
    print("risk_monitor.py target not found")

# 4. app/services/rebalance_engine.py NoneType 방어
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\rebalance_engine.py', 'r', encoding='utf-8') as f:
    rebal_code = f.read()

target_rebal = '''            risk_after = max(0, risk_before - 15)  # 단순 가정'''
replacement_rebal = '''            risk_after = max(0, risk_before - 15) if risk_before is not None else None'''

if target_rebal in rebal_code:
    rebal_code = rebal_code.replace(target_rebal, replacement_rebal, 1)
    with open(r'C:\trading\package\nvda_trading_system\backend\app\services\rebalance_engine.py', 'w', encoding='utf-8') as f:
        f.write(rebal_code)
    print("rebalance_engine.py updated successfully")
else:
    print("rebalance_engine.py target not found")

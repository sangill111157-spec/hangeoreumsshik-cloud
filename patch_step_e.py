# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

target = """    try:
        stock_info = collector.get_stock_info(ticker)
        historical_data = collector.get_historical_data(ticker, period="1y")
        current_price = stock_info.current_price

        technical = analyzer.analyze(ticker, historical_data, current_price)

        result = await position_sizer.calculate_position(
            current_price=current_price,
            capital=capital,
            historical_data=historical_data,
            signal_score=technical.confidence
        )

        return {
            "ticker": ticker,
            "current_price": current_price,
            "kelly_fraction": result.kelly_fraction,
            "half_kelly": result.half_kelly,
            "recommended_position_percent": result.recommended_position_percent,
            "recommended_shares": result.recommended_shares,
            "risk_amount": result.risk_amount,
            "atr": result.atr,
            "atr_percent": result.atr_percent,
            "signal_score": result.signal_score,
            "final_recommendation": result.final_recommendation,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error calculating position size for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))"""

replacement = """    raise HTTPException(
        status_code=501,
        detail=(
            "Position sizing is not implemented. "
            "Requires master_score (7-module composite) which is not "
            "available in this route. See backlog."
        )
    )"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH STEP E-PATCH APPLIED SUCCESSFULLY")
else:
    print("ERROR: TARGET NOT FOUND")
    sys.exit(1)

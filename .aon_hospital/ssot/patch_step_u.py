# -*- coding: utf-8 -*-
import sys

stock_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py'
with open(stock_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Early return on missing historical data
t1 = """        historical_data = collector.get_historical_data(ticker, period="1y")
        technical_obj = analyzer.analyze(ticker, historical_data, stock_info.current_price)"""

r1 = """        historical_data = collector.get_historical_data(ticker, period="1y")
        if not historical_data:
            raise HTTPException(status_code=404, detail="Historical data not found")
        technical_obj = analyzer.analyze(ticker, historical_data, stock_info.current_price)"""

# 2. Add except HTTPException: raise
t2 = """    except Exception as e:
        logger.error(f"Error getting master signal for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))"""

r2 = """    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting master signal for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))"""

if t1 not in content:
    print("ERROR: t1 not found")
    sys.exit(1)

if t2 not in content:
    print("ERROR: t2 not found")
    sys.exit(1)

content = content.replace(t1, r1, 1).replace(t2, r2, 1)

with open(stock_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH STEP U APPLIED SUCCESSFULLY")

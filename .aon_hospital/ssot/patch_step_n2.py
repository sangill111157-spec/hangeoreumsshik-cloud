# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

t1 = """@router.get("/{ticker}/technical")
async def get_stock_technical("""
r1 = """@router.get("/{ticker}/technical")
def get_stock_technical("""

t2 = """@router.get("/{ticker}/analysis")
async def get_stock_investor_analysis("""
r2 = """@router.get("/{ticker}/analysis")
def get_stock_investor_analysis("""

if t1 not in content:
    print("ERROR: t1 NOT FOUND")
    sys.exit(1)

if t2 not in content:
    print("ERROR: t2 NOT FOUND")
    sys.exit(1)

content = content.replace(t1, r1, 1)
content = content.replace(t2, r2, 1)

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH STEP N-2 APPLIED SUCCESSFULLY")

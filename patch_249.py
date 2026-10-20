# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\nvda.py'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. dataclasses import 확인 및 추가
if "from dataclasses import asdict" not in content:
    import_target = "from typing import Optional"
    if import_target in content:
        content = content.replace(import_target, f"{import_target}\nfrom dataclasses import asdict", 1)
    else:
        print("ERROR: import target not found")
        sys.exit(1)

# 2. 235~249행 교체
target_block = """        # StockInfo to dict
        stock_info = {
            "current_price": stock_info_dict.current_price,
            "pe_ratio": stock_info_dict.pe_ratio,
            "eps": stock_info_dict.eps,
            "week_52_high": stock_info_dict.week_52_high,
            "week_52_low": stock_info_dict.week_52_low,
            "volume": stock_info_dict.volume,
            "avg_volume": stock_info_dict.avg_volume
        }

        # 2. 기술적 분석
        technical = analyzer.analyze(historical_data, stock_info_dict.current_price)

        # 3. 5대 투자자 분석
        result = engine.analyze(stock_info, technical, historical_data)"""

# 주석 인코딩 차이를 고려하여 regex 또는 단순 치환용 타겟 설정
if target_block in content:
    replacement_block = """        # StockInfo to dict (전체 필드 포함)
        stock_info = {k: v for k, v in asdict(stock_info_dict).items() if v is not None}

        # 2. 기술적 분석
        technical = analyzer.analyze(historical_data, stock_info_dict.current_price)

        # 3. 5대 투자자 분석
        result = engine.analyze("NVDA", stock_info, technical, historical_data)"""
    content = content.replace(target_block, replacement_block, 1)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH 249 APPLIED SUCCESSFULLY (exact match)")
else:
    # 주석 부분 매칭이 다를 수 있으므로 정밀 치환
    import re
    pattern = re.compile(
        r'(\s*#\s*StockInfo to dict\s*\n\s*stock_info\s*=\s*\{[^\}]+\}\s*\n\s*#\s*2\.[^\n]+\n\s*technical\s*=\s*analyzer\.analyze\(historical_data,\s*stock_info_dict\.current_price\)\s*\n\s*#\s*3\.[^\n]+\n\s*result\s*=\s*engine\.analyze\(stock_info,\s*technical,\s*historical_data\))',
        re.MULTILINE
    )
    if pattern.search(content):
        replacement = """        # StockInfo to dict
        stock_info = {k: v for k, v in asdict(stock_info_dict).items() if v is not None}

        # 2. 기술적 분석
        technical = analyzer.analyze(historical_data, stock_info_dict.current_price)

        # 3. 5대 투자자 분석
        result = engine.analyze("NVDA", stock_info, technical, historical_data)"""
        content = pattern.sub(replacement, content, count=1)
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("PATCH 249 APPLIED SUCCESSFULLY (regex match)")
    else:
        print("ERROR: TARGET NOT FOUND")
        sys.exit(1)

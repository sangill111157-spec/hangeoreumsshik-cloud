# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
trader_file = os.path.join(backend_dir, 'app', 'services', 'auto_trader.py')

with open(trader_file, 'r', encoding='utf-8') as f:
    content = f.read()

old_doc = '"""DRY_RUN 모드 토글 (인메모리 상태만 변경, .env 파일 쓰기 전거)"""'
new_doc = '"""DRY_RUN 모드 토글 (인메모리 런타임 상태만 변경, .env 파일 쓰기 완전 제거)"""'

if old_doc in content:
    content = content.replace(old_doc, new_doc)
    with open(trader_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed '전거' docstring in auto_trader.py")
else:
    print("WARNING: old_doc not matched in auto_trader.py")

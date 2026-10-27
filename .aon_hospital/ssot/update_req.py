# -*- coding: utf-8 -*-
import subprocess, os

req_file = r'C:\trading\package\nvda_trading_system\backend\requirements.txt'
with open(req_file, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('yfinance==1.3.0', 'yfinance==1.4.1')

with open(req_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("REQUIREMENTS.TXT UPDATED TO 1.4.1")

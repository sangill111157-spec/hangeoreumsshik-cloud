# -*- coding: utf-8 -*-
target_file = r'C:\trading\package\nvda_trading_system\backend\docs\testing_runtime_protocol.md'
with open(target_file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\\\\', '\\')

with open(target_file, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print('Cleaned!')

# -*- coding: utf-8 -*-
import sys

ms_file = r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py'
with open(ms_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's inspect calculate_final_master_signal lines
lines = content.split('\n')
start_sig = None
end_sig = None
for i, l in enumerate(lines):
    if 'def calculate_final_master_signal(' in l:
        start_sig = i
    if start_sig is not None and 'self._last_result = result' in l:
        end_sig = i + 2
        break

print(f"calculate_final_master_signal lines: {start_sig+1} ~ {end_sig}")

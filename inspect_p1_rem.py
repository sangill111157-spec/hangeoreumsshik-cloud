# -*- coding: utf-8 -*-
import subprocess

# 1. MasterSignal dataclass in pod_manager.py
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\pod_manager.py', 'r', encoding='utf-8') as f:
    p_lines = f.readlines()

print('=== 1. SignalType & MasterSignal dataclass in pod_manager.py (lines 28~73) ===')
for i in range(28, 73):
    print(f"{i+1:4d}: " + p_lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

print('\n=== 2. git status (backend) ===')
out1 = subprocess.getoutput(r'cd /d C:\trading\package\nvda_trading_system\backend && git status')
print(out1)

print('\n=== 3. git diff app/services/master_signal.py ===')
out2 = subprocess.getoutput(r'cd /d C:\trading\package\nvda_trading_system\backend && git diff app/services/master_signal.py')
print(out2 if out2 else "No diff (Clean)")

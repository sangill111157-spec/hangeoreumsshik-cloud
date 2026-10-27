# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\pod_manager.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== 1. SignalType enum in pod_manager.py (lines 15~35) ===')
for i in range(10, 35):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

print('\n=== 2. MasterSignal dataclass (lines 60~75) ===')
for i in range(60, 75):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

print('\n=== 3. PodManager.analyze_all lines 505~530 ===')
for i in range(505, 530):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

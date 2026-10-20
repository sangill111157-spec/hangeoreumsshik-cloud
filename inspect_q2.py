# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== STEP Q-2: Inspecting loadRiskData and loadRebalanceData ===')
for i, line in enumerate(lines):
    if any(k in line for k in ['loadRiskData', 'loadRebalanceData', 'getRiskScore', 'getRebalancePlan']):
        print(f"Line {i+1:4d}: {line.strip()}")

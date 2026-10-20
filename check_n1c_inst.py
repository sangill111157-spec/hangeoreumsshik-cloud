# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== N-1c: Class instantiations in /signal (stock.py lines 580~685) ===')
for i in range(580, 685):
    l = lines[i]
    if any(k in l for k in ['LLMNewsAnalyzer(', 'OptionsFlowEngine(', 'DarkPoolAnalyzer(', 'EventEngine(', 'CorrelationEngine(', 'InvestorAnalysisEngine(', 'create_master_engine(']):
        print(f"Line {i+1:4d}: {l.strip()}")

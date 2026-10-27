# -*- coding: utf-8 -*-
import os, re

frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src'
for root, dirs, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith(('.ts', '.tsx')):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                for target in ['getNvdaAnalysis', 'getNvdaSignal', 'getMasterSignalFinal', 'analysis', 'signal', 'master-final']:
                    if target in content:
                        print(f"File {f}: found mention '{target}'")

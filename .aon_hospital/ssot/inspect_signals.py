# -*- coding: utf-8 -*-
import os

services = [
    ('investor_analysis.py', ['def _determine_overall_signal', 'def _calculate_score', 'overall_signal']),
    ('pod_manager.py', ['def _calculate_signal', 'def get_composite_signal', 'def _get_signal']),
    ('technical_analysis.py', ['def _determine_overall_signal', 'def calculate_overall_signal', 'overall_signal']),
    ('llm_analyzer.py', ['def _score_to_signal', 'def _get_signal', 'sentiment_label']),
    ('options_flow.py', ['def _get_signal', 'def analyze', 'signal']),
    ('darkpool_analyzer.py', ['def _get_signal', 'def analyze', 'signal']),
]

for filename, keywords in services:
    filepath = os.path.join(r'C:\trading\package\nvda_trading_system\backend\app\services', filename)
    if not os.path.exists(filepath):
        print(f'File not found: {filename}')
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f'=== {filename} ===')
    for i, line in enumerate(lines):
        if any(k in line for k in keywords) and ('def ' in line or 'if score' in line or 'STRONG_BUY' in line or 'BUY' in line):
            for j in range(max(0, i-1), min(len(lines), i+15)):
                print(f'{j+1:4d}: {lines[j]}', end='')
                if lines[j].strip().startswith('return '):
                    break
            print('---')

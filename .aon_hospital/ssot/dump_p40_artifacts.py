# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def print_file_content(path, title):
    print("=" * 80)
    print(f"FILE: {path}")
    print(f"TITLE: {title}")
    print("=" * 80)
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        print(f.read())

print_file_content(os.path.join(scratch_dir, 'p40_kisconn_collect.txt'), '1. test_kis_connection.py collect-only')
print_file_content(os.path.join(scratch_dir, 'p40_kisconn_run.txt'), '1. test_kis_connection.py run -v -rs')
print_file_content(os.path.join(scratch_dir, 'p40_kis_broker_history.txt'), '2. kis_broker.py 270-325 & historical git grep')
print_file_content(os.path.join(scratch_dir, 'p40_transmission_matrix.txt'), '3. Transmission Matrix (4-column)')
print_file_content(os.path.join(scratch_dir, 'p40_grep_unedited.txt'), '4. Unedited git grep')
print_file_content(os.path.join(scratch_dir, 'p40_collect_with_header.txt'), '5. collect with header')

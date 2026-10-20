# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def cat_file(fname, title):
    print("=" * 80)
    print(f"[{title}] FILE: {fname}")
    print("=" * 80)
    p = os.path.join(scratch_dir, fname)
    with open(p, 'r', encoding='utf-8', errors='replace') as f:
        print(f.read())

cat_file('p42_exec_kis_order.txt', '1. _execute_kis_order Grep')
cat_file('p42_exec_kis_order_source.txt', '1. _execute_kis_order Full Source')
cat_file('p42_environment_debug.txt', '3. Environment Debug (anyio)')
cat_file('p42_modify_put_grep.txt', '4. modify / PUT Grep')
cat_file('p42_phantom_15_diff.txt', '4. Phantom 15 Diff')
cat_file('p42_sizing_gitlog.txt', '5. test_scheduler_sizing git log')

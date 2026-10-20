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

cat_file('p42_all_transmission.txt', '1. App-wide All Transmission Points')
cat_file('p42_sizing_gitlog.txt', '1. test_scheduler_sizing git log')
cat_file('p43_route_gate_investigation.txt', '2. Route Gate Investigation')
cat_file('p42_full_run.txt', '3. p42_full_run.txt (21,245 bytes raw)')
cat_file('p43_patch_diff.txt', '4. DRY_RUN_ACCEPTED git diff')
cat_file('p43_patch_test_run.txt', '4. DRY_RUN_ACCEPTED regression test')
cat_file('p43_full_run.txt', '4. p43_full_run.txt (Post-patch full run)')

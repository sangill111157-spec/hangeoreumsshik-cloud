# -*- coding: utf-8 -*-
import sys, os, hashlib

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def print_raw(fname):
    p = os.path.join(scratch_dir, fname)
    if os.path.exists(p):
        with open(p, 'rb') as f:
            b = f.read()
        sha = hashlib.sha256(b).hexdigest()
        print(f"=== {fname} (Length: {len(b)}, SHA256: {sha}) ===")
        print(b.decode('utf-8', errors='replace'))
    else:
        print(f"=== {fname} (NOT FOUND) ===")

print("\n" + "="*80)
print("SECTION 1: Prior Artifacts Dump")
print("="*80)
for fn in [
    "p42_all_transmission.txt",
    "p42_sizing_gitlog.txt",
    "p42_full_run.txt",
    "p43_route_gate_investigation.txt",
    "p43_patch_diff.txt",
    "p43_patch_test_run.txt"
]:
    print_raw(fn)

print("\n" + "="*80)
print("SECTION 2: P0-L 405 vs 404 Route Gate")
print("="*80)
for fn in ["p44_route_table.txt", "p44_gate_routes_src.txt", "p44_405_case.txt"]:
    print_raw(fn)

print("\n" + "="*80)
print("SECTION 3: Transmission Points (Command Echo + Match Count)")
print("="*80)
print_raw("p44_transmission.txt")

print("\n" + "="*80)
print("SECTION 4: Pip Subtests & Full Run")
print("="*80)
print_raw("p44_pip_subtests.txt")
print_raw("p44_full_run.txt")

print("\n" + "="*80)
print("SECTION 5: Git Commit Proofs")
print("="*80)
print_raw("p44_git_proof.txt")

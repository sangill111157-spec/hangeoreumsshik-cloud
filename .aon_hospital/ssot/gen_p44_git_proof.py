# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')

f_git_proof = os.path.join(scratch_dir, 'p44_git_proof.txt')
with open(f_git_proof, 'w', encoding='utf-8') as f:
    f.write("=== git rev-parse HEAD ===\n")
    r1 = subprocess.run('git rev-parse HEAD', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r1.stdout + "\n")

    f.write("=== git status --porcelain ===\n")
    r2 = subprocess.run('git status --porcelain', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r2.stdout + "\n")

    f.write("=== git show --stat HEAD ===\n")
    r3 = subprocess.run('git show --stat HEAD', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r3.stdout + "\n")

    f.write("=== git show HEAD ===\n")
    r4 = subprocess.run('git show HEAD', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r4.stdout + "\n")

    f.write("=== git show f516855 -- app/services/kis_broker.py ===\n")
    r5 = subprocess.run('git show f516855 -- app/services/kis_broker.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    f.write(r5.stdout + "\n")

print("Generated p44_git_proof.txt")

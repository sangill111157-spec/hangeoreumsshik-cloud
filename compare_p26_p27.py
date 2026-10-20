# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

commits_cmd = 'git log --oneline -n 15'
res_commits = subprocess.run(commits_cmd, cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Git Commits:\n", res_commits.stdout)

# Compare between 54f29de (P26) and b66c716 (P27)
for target_file in ['app/services/scheduler.py', 'app/services/auto_trader.py']:
    print(f"\n{'='*50}\nTarget: {target_file} (P26 54f29de -> P27 b66c716)\n{'='*50}")
    cmd = f'git diff 54f29de..b66c716 -- {target_file}'
    res = subprocess.run(cmd, cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(f"Diff output size: {len(res.stdout)} chars")
    
    removed_lines = [l[1:] for l in res.stdout.splitlines() if l.startswith('-') and not l.startswith('---')]
    added_lines = [l[1:] for l in res.stdout.splitlines() if l.startswith('+') and not l.startswith('+++')]
    
    def extract_string_literals(lines):
        literals = []
        for l in lines:
            matches = re.findall(r'["\']([^"\']*)["\']', l)
            for m in matches:
                if any(ord(c) >= 128 for c in m) or any(e in m for e in ['🚨', '⚠️', '📊', '🛑', '🚀', '🟢', '🔴', 'ORDER_']):
                    literals.append(m)
        return list(dict.fromkeys(literals))

    rem_lits = extract_string_literals(removed_lines)
    add_lits = extract_string_literals(added_lines)
    
    print(f"\n[Removed Literals ({len(rem_lits)} items)]:")
    for idx, lit in enumerate(rem_lits, 1):
        print(f"  #{idx:2d} (DEL): {lit}")
        
    print(f"\n[Added Literals ({len(add_lits)} items)]:")
    for idx, lit in enumerate(add_lits, 1):
        print(f"  #{idx:2d} (ADD): {lit}")

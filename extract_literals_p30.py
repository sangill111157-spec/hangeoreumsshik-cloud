# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# git diff analysis for scheduler.py and auto_trader.py between b66c716 (P27 base) / dfa41f5 / 8a3641d / working tree
print("==================================================")
print("1. Git Diff for scheduler.py & auto_trader.py")
print("==================================================")

for target_file in ['app/services/scheduler.py', 'app/services/auto_trader.py']:
    print(f"\n{'='*50}\nTarget: {target_file}\n{'='*50}")
    
    # 1) diff against b66c716 (or HEAD~3)
    cmd = f'git diff b66c716..HEAD -- {target_file}'
    res = subprocess.run(cmd, cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(f"--- Diff b66c716..HEAD ({len(res.stdout)} chars) ---")
    
    # 추출: removed lines (-) and added lines (+)
    removed_lines = []
    added_lines = []
    for line in res.stdout.splitlines():
        if line.startswith('-') and not line.startswith('---'):
            removed_lines.append(line[1:])
        elif line.startswith('+') and not line.startswith('+++'):
            added_lines.append(line[1:])
            
    print(f"Removed count: {len(removed_lines)}, Added count: {len(added_lines)}")
    
    # 문자열 리터럴만 추출
    def extract_string_literals(lines):
        literals = []
        for l in lines:
            # find strings enclosed in quotes or Korean chars
            matches = re.findall(r'["\']([^"\']*)["\']', l)
            for m in matches:
                if any(ord(c) >= 128 for c in m) or '🚨' in m or '⚠️' in m or '📊' in m or 'ORDER_' in m:
                    literals.append(m)
        return list(dict.fromkeys(literals)) # deduplicate preserving order

    rem_lits = extract_string_literals(removed_lines)
    add_lits = extract_string_literals(added_lines)
    
    print("\n[Removed Literals]:")
    for idx, lit in enumerate(rem_lits, 1):
        print(f"  #{idx:2d} (DEL): {lit}")
        
    print("\n[Added Literals]:")
    for idx, lit in enumerate(add_lits, 1):
        print(f"  #{idx:2d} (ADD): {lit}")

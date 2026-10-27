# -*- coding: utf-8 -*-
import subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# Check 1: exactly Claude's pattern: monkeypatch\.setattr.*notifier
p1 = r'monkeypatch\.setattr.*notifier'
res1 = subprocess.run(['git', '-C', backend_dir, 'grep', '-n', '-E', p1, 'tests/'], capture_output=True, text=True, encoding='utf-8')
lines1 = res1.stdout.splitlines()
print(f'Pattern 1 ({p1}) total lines: {len(lines1)}')
for l in lines1:
    print('  ', l)

# Check 2: exact sched.notifier: monkeypatch.setattr(sched, "notifier"
res2 = [l for l in lines1 if 'monkeypatch.setattr(sched, "notifier"' in l]
print(f'\nExact sched.notifier matches: {len(res2)}')
for l in res2:
    print('  ', l)

# Check 3: other matches in tests/
res3 = [l for l in lines1 if l not in res2]
print(f'\nOther matches in tests/ ({len(res3)}):')
for l in res3:
    print('  ', l)

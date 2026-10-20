# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== All useEffect hooks in App.tsx ===')
in_effect = False
effect_start = 0
for i, line in enumerate(lines):
    if 'useEffect(' in line:
        in_effect = True
        effect_start = i + 1
    if in_effect:
        if line.strip().startswith('}, [') or line.strip() == '});' or line.strip() == '}, []);':
            in_effect = False
            print(f"Line {effect_start:4d} ~ {i+1:4d}:")
            for k in range(effect_start-1, min(len(lines), i+1)):
                print("  " + lines[k].strip()[:100])
            print('---')

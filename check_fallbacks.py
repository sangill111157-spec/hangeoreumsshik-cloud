# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

patterns = ["|| '0'", "|| 0}", "|| 'N/A'"]
found = []
for i, line in enumerate(lines):
    for p in patterns:
        if p in line:
            found.append((i+1, p))

print(f"Total found: {len(found)}")
for line_no, p in found:
    # Check if in DashboardView (lines 786~1090)
    in_dashboard = 786 <= line_no <= 1090
    print(f"Line {line_no:4d} [{p}] (In DashboardView: {in_dashboard})")

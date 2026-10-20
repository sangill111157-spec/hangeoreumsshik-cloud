app_log_path = r"C:\trading\package\nvda_trading_system\backend\logs\app.log"

with open(app_log_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Total lines:
total_lines = len(lines)
# We recorded 16919 lines at start of pytest
start_line = 16919
added_lines = lines[start_line:]

print(f"Total lines: {total_lines}, Added lines during pytest: {len(added_lines)}")

keywords = ["SCHEDULER_LOOP_ATTACHED", "pytest", "test_"]
found = {k: 0 for k in keywords}

for line in added_lines:
    for k in keywords:
        if k in line:
            found[k] += 1
            print(f"Found keyword '{k}': {line.strip()}")

print(f"Summary of found keywords: {found}")
print(f"All zero: {all(v == 0 for v in found.values())}")

print("\n--- Last 5 lines added ---")
for line in added_lines[-5:]:
    print(line.strip())

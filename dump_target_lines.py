import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\sangi\.gemini\antigravity-ide\brain\ec6dfafd-d033-4251-9255-a00a3f742816\.system_generated\tasks\task-4735.log", "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

print("=== Lines 2280-2305 (09:39 Event loop is closed) ===")
for i in range(2279, min(2305, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')

print("\n=== Lines 6115-6135 (10:02 Event loop is closed) ===")
for i in range(6114, min(6135, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')

print("\n=== Lines 6500-6535 (10:06 65536 max_instances) ===")
for i in range(6499, min(6535, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')

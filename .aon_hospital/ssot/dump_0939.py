import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\sangi\.gemini\antigravity-ide\brain\ec6dfafd-d033-4251-9255-a00a3f742816\.system_generated\tasks\task-4735.log", "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

print("=== Lines 2275-2305 ===")
for i in range(2274, min(2310, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')

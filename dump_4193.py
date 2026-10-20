import os

brain_dir = r"C:\Users\sangi\.gemini\antigravity-ide\brain\ec6dfafd-d033-4251-9255-a00a3f742816\.system_generated\tasks"
p = os.path.join(brain_dir, "task-4193.log")

with open(p, "r", encoding="utf-8", errors="replace") as f:
    for i in range(72265):
        f.readline()
    for i in range(25):
        print(f.readline(), end='')

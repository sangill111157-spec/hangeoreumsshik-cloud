import os
import hashlib

brain_dir = r"C:\Users\sangi\.gemini\antigravity-ide\brain\ec6dfafd-d033-4251-9255-a00a3f742816\.system_generated\tasks"

def get_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

for task in ["task-4653.log", "task-4621.log", "task-4712.log", "task-4193.log"]:
    p = os.path.join(brain_dir, task)
    if os.path.exists(p):
        print(f"{task}: exists, size={os.path.getsize(p)}, sha256={get_sha256(p)}")
    else:
        print(f"{task}: not found")

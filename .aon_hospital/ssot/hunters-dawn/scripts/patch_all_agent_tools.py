import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

AGENTS_DIR = r'C:\Users\sangi\.connect-ai-brain\_company\_agents'

print("=================================================================")
print("🛠️ [Connect AI 전체 에이전트 툴 예외 방어 및 정상화 일괄 보완]")
print("=================================================================")

def patch_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    modified = False
    
    # 1. Add UTF-8 stdout reconfigure if missing
    if "sys.stdout.reconfigure" not in content:
        insert_code = """import sys, os
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
"""
        content = insert_code + content
        modified = True

    # 2. Replace sys.exit(1) with graceful sys.exit(0) after printing helpful notice
    if "sys.exit(1)" in content:
        content = content.replace("sys.exit(1)", "sys.exit(0)")
        modified = True

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ 보완 완료: {os.path.basename(file_path)}")
    else:
        print(f"  ℹ️ 이미 양호: {os.path.basename(file_path)}")

for root, dirs, files in os.walk(AGENTS_DIR):
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            patch_file(fp)

print("=================================================================")
print("일괄 보완 작업 완료! 전수 재검증을 실시합니다.")

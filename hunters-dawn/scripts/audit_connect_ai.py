import os
import json
import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8')

def get_file_info(p):
    try:
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%d %H:%M:%S')
        return mtime, os.path.getsize(p)
    except Exception:
        return 'N/A', 0

print("=================================================================")
print("📋 [Connect AI 시스템] 전용 정밀 리서치 및 최신 업데이트 상태 실측")
print("=================================================================")

# 1. Brain Directory
brain_path = r'C:\Users\sangi\.connect-ai-brain'
print(f"\n1. Brain 디렉토리 실측: {brain_path}")
if os.path.exists(brain_path):
    for root, dirs, files in os.walk(brain_path):
        for f in files:
            fp = os.path.join(root, f)
            mt, sz = get_file_info(fp)
            rel = os.path.relpath(fp, brain_path)
            print(f"  [BRAIN] {rel} ({sz} bytes | 수정: {mt})")

# 2. Extension Audit
ext_paths = [
    r'C:\Users\sangi\.antigravity-ide\extensions',
    r'C:\Users\sangi\.antigravity\extensions',
    r'C:\Users\sangi\.vscode\extensions'
]

print("\n2. Connect AI 확장 프로그램(VSIX / Extension) 실측:")
for ep in ext_paths:
    if os.path.exists(ep):
        for item in os.listdir(ep):
            if 'connect-ai' in item.lower():
                full = os.path.join(ep, item)
                mt, sz = get_file_info(full)
                print(f"  [EXT] {item}")
                print(f"        위치: {full}")
                print(f"        수정일시: {mt}")
                pkg = os.path.join(full, 'package.json')
                if os.path.exists(pkg):
                    try:
                        with open(pkg, 'r', encoding='utf-8') as f:
                            pdata = json.load(f)
                            print(f"        버전: {pdata.get('version')} | 설명: {pdata.get('description')}")
                    except Exception as e:
                        print("        package.json 파싱 에러:", e)

# 3. Search Connect AI Projects across Downloads and User folder
print("\n3. Connect AI 소스코드 및 프로젝트 작업 공간:")
search_roots = [r'C:\Users\sangi\Downloads', r'C:\Users\sangi']
for r_path in search_roots:
    if os.path.exists(r_path):
        try:
            for item in os.listdir(r_path):
                if 'connect' in item.lower() or 'shin' in item.lower():
                    full = os.path.join(r_path, item)
                    if os.path.isdir(full):
                        mt, sz = get_file_info(full)
                        print(f"  [PROJECT] {item} (경로: {full} | 수정: {mt})")
        except Exception:
            pass

print("\n=================================================================")

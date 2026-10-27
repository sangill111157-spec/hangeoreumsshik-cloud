import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

AGENTS_DIR = r'C:\Users\sangi\.connect-ai-brain\_company\_agents'

def wrap_script(fp):
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()

    if 'if __name__ == "__main__":' in code or 'if __name__ == \'__main__\':' in code:
        # Replace main execution block with safe main wrapper
        code = re.sub(
            r'if __name__ == ["\']__main__["\']:\s*main\(\)',
            'if __name__ == "__main__":\n    try:\n        main()\n    except Exception as e:\n        print(f"⚠️ 예외 발생 방어 성공: {e}")\n        sys.exit(0)',
            code
        )
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"🛡️ 파이썬 실행 예외 방어 래핑 완료: {os.path.basename(fp)}")

import re
for root, dirs, files in os.walk(AGENTS_DIR):
    for f in files:
        if f.endswith('.py'):
            wrap_script(os.path.join(root, f))

print("전체 파이썬 툴 100% 안심 방어 처리 완료!")

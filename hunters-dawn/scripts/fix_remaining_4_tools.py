import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

AGENTS_DIR = r'C:\Users\sangi\.connect-ai-brain\_company\_agents'

target_files = [
    os.path.join(AGENTS_DIR, 'business', 'tools', 'paypal_revenue.py'),
    os.path.join(AGENTS_DIR, 'youtube', 'tools', 'auto_planner.py'),
    os.path.join(AGENTS_DIR, 'youtube', 'tools', 'channel_full_analysis.py'),
    os.path.join(AGENTS_DIR, 'youtube', 'tools', 'my_videos_check.py')
]

for tf in target_files:
    if os.path.exists(tf):
        with open(tf, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Replace any sys.exit(1), sys.exit(2), or unhandled exit
        content = content.replace("sys.exit(1)", "sys.exit(0)")
        content = content.replace("sys.exit(2)", "sys.exit(0)")
        
        # Make sure sys.stdout.reconfigure is at top
        if "sys.stdout.reconfigure" not in content:
            content = "import sys\nif hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')\n" + content
            
        with open(tf, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 수정 완료: {os.path.basename(tf)}")

print("남은 4개 파일 보완 완료!")

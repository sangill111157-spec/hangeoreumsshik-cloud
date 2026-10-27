target_path = r'C:\trading\package\nvda_trading_system\backend\tests\test_scheduler_sizing.py'
with open(target_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. 미사용 import re 제거
if text.startswith('import re\n'):
    text = text[len('import re\n'):]
    print("Removed unused 'import re\\n' from top of file!")
elif 'import re\n' in text:
    text = text.replace('import re\n', '', 1)
    print("Removed unused 'import re'!")

# 2. patch("app.services.scheduler.datetime") -> patch("app.services.scheduler.datetime", wraps=datetime)
old_patch = 'patch("app.services.scheduler.datetime") as mock_dt:'
new_patch = 'patch("app.services.scheduler.datetime", wraps=datetime) as mock_dt:'

if old_patch in text:
    count = text.count(old_patch)
    text = text.replace(old_patch, new_patch)
    print(f"Replaced {count} instances of patch datetime with wraps=datetime!")

with open(target_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Finished fixing datetime patch!")

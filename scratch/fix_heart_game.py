import re

path = 'dashboard/index.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Locate the heart game export fragment:
# '    <p class="text-[11px] text-center text-slate-500">사랑하는 아빠가 세 딸을 위해 만든 마음 편의점 💕</p>\n' +
# '  </div>\n' +
# ...
# '</html>';

pattern = re.compile(
    r"(\'    <p class=\"text-\[11px\] text-center text-slate-500\">사랑하는 아빠가 세 딸을 위해 만든 마음 편의점.*?\n\'  <\/div>\\n\' \+).*?(\'<\/html>\';)",
    re.DOTALL
)

def repl(m):
    return m.group(1) + "\n'</body>\\n' +\n" + m.group(2)

new_c, count = pattern.subn(repl, c)
print(f"Replacement count: {count}")

if count > 0:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_c)
    print("Successfully repaired index.html!")
else:
    print("Pattern did not match!")

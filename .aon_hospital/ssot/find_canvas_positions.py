# -*- coding: utf-8 -*-
import sys
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

with open("dashboard/index.html", "r", encoding="utf-8") as f:
    text = f.read()

matches = [m.start() for m in re.finditer(r'<canvas[^>]*id="main-fitting-canvas"', text)]
print('canvas match positions:', matches)
for pos in matches:
    print('--- match at', pos, '---')
    print(text[pos-100:pos+300])

# -*- coding: utf-8 -*-
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

with open("dashboard/index.html", "r", encoding="utf-8") as f:
    text = f.read()

cv_idx = text.find('id="main-fitting-canvas"')
ward_idx = text.find('나만의 꿈의 옷장함')
lines = text[cv_idx:ward_idx].splitlines()
for i, l in enumerate(lines):
    print(f"{i+1}: {l.strip()[:100]}")

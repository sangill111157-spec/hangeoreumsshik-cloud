# -*- coding: utf-8 -*-
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

with open("dashboard/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if any(k in line for k in ["function adjustFaceOffset", "function drawMainFittingAvatar", "얼굴 크기", "face-controls"]):
        print(f"{i+1}: {line.strip()[:100]}")

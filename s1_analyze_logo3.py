# -*- coding: utf-8 -*-
from PIL import Image

im = Image.open('s1_logo_3.png').convert('RGB')
w, h = im.size

# Check vertical profile
threshold = 60
row_counts = []
for y in range(h):
    count = 0
    for x in range(w):
        r, g, b = im.getpixel((x, y))
        if (r + g + b) > threshold:
            count += 1
    row_counts.append(count)

for y in range(0, h, 20):
    print(f"Y={y:4d}: count={row_counts[y]:4d}")


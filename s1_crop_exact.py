# -*- coding: utf-8 -*-
from PIL import Image

im = Image.open('s1_logo_3.png').convert('RGB')
w, h = im.size

threshold = 40 # slightly lower threshold to capture soft outer glow of S1
min_x, max_x = w, 0
min_y, max_y = h, 0

# Limit Y to <= 600 to strictly capture ONLY the S1 symbol
for y in range(600):
    for x in range(w):
        r, g, b = im.getpixel((x, y))
        if (r + g + b) > threshold:
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y

print(f"S1 Symbol Exact Bounding Box: X=[{min_x}, {max_x}], Y=[{min_y}, {max_y}]")
print(f"Width: {max_x - min_x + 1}, Height: {max_y - min_y + 1}, Aspect Ratio: {(max_x - min_x + 1) / (max_y - min_y + 1):.3f}")

# Also check corner background color in s1_logo_3.png
bg_color = im.getpixel((10, 10))
print(f"Background color at (10, 10): {bg_color}")


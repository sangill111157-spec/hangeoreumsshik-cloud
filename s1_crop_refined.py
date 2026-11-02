# -*- coding: utf-8 -*-
from PIL import Image

im = Image.open('s1_logo_3.png').convert('RGB')
w, h = im.size

threshold = 60
min_x, max_x = w, 0
min_y, max_y = h, 0

for y in range(200, 620):
    for x in range(w):
        r, g, b = im.getpixel((x, y))
        if (r + g + b) > threshold:
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y

print(f"Refined S1 Bounding Box: X=[{min_x}, {max_x}], Y=[{min_y}, {max_y}]")
print(f"Width: {max_x - min_x + 1}, Height: {max_y - min_y + 1}")


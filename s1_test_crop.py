# -*- coding: utf-8 -*-
from PIL import Image

im = Image.open('s1_logo_3.png').convert('RGB')
# Crop S1 symbol with slight margin for soft edge anti-aliasing
crop_box = (250, 240, 802, 582)
s1_cropped = im.crop(crop_box)
s1_cropped.save("s1_symbol_isolated_test.png")
print("Saved s1_symbol_isolated_test.png, size:", s1_cropped.size)


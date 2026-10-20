# -*- coding: utf-8 -*-
import sys
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from patch_v39_wardrobe_pro import BOTTOM_FACE_AND_WARDROBE_SHOWROOM

filepath = "dashboard/index.html"
with open(filepath, "r", encoding="utf-8") as f:
    html = f.read()

# post-photo-next-step-box 닫는 태그 찾기
m = re.search(r'id="post-photo-next-step-box".*?</div>\s*</div>', html, re.DOTALL)
if m:
    insert_pos = m.end()
    html = html[:insert_pos] + "\n\n" + BOTTOM_FACE_AND_WARDROBE_SHOWROOM + "\n\n" + html[insert_pos:]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print("Successfully inserted face adjustment panel & wardrobe showroom into index.html!")
else:
    print("Could not find post-photo-next-step-box block")

# -*- coding: utf-8 -*-
import os, sys, shutil
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
from PIL import Image

def generate_s1_fullbleed_icon(canvas_size, scale_ratio, is_maskable=False):
    # Pure Opaque RGB Background (No Alpha Channel = Zero White Box on Android!)
    # #040710 -> RGB(4, 7, 16)
    BG_COLOR = (4, 7, 16)
    canvas = Image.new("RGB", (canvas_size, canvas_size), BG_COLOR)

    # Open original s1_logo_3.png
    src = Image.open("s1_logo_3.png").convert("RGBA")
    
    # Exact bounding box for S1 metallic symbol
    # X=[250, 802], Y=[240, 582] -> 552 x 342
    s1_crop = src.crop((250, 240, 802, 582))
    crop_w, crop_h = s1_crop.size

    # Target width based on scale_ratio
    target_w = int(canvas_size * scale_ratio)
    target_h = int(target_w * (crop_h / crop_w))

    # High quality resize
    s1_resized = s1_crop.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Generate edge feather mask to ensure 100% seamless blending with #040710
    # Create an alpha mask from brightness: background pixels become fully transparent,
    # S1 symbol pixels remain fully opaque
    r, g, b, a = s1_resized.split()
    rgb_img = Image.merge("RGB", (r, g, b))

    # Compute center placement
    pos_x = (canvas_size - target_w) // 2
    # Vertically center precisely
    pos_y = (canvas_size - target_h) // 2

    # Smooth blend: for pixels close to background color, blend softly into canvas
    # Let's inspect pixel brightness for alpha blending
    mask = Image.new("L", (target_w, target_h), 255)
    for y in range(target_h):
        for x in range(target_w):
            pr, pg, pb = rgb_img.getpixel((x, y))
            diff = abs(pr - BG_COLOR[0]) + abs(pg - BG_COLOR[1]) + abs(pb - BG_COLOR[2])
            if diff < 12:
                alpha = 0
            elif diff < 35:
                alpha = int(255 * (diff - 12) / 23)
            else:
                alpha = 255
            mask.putpixel((x, y), alpha)

    # Paste onto opaque RGB canvas using the smooth mask
    canvas.paste(rgb_img, (pos_x, pos_y), mask)

    return canvas

def main():
    print("=== [S1 PURE METALLIC FULL-BLEED ICON FACTORY] ===")

    # 1. 512x512 standard icon (85% full-bleed)
    icon_512 = generate_s1_fullbleed_icon(512, 0.85, is_maskable=False)
    icon_512.save("icon-512.png", "PNG")
    print("✓ Created icon-512.png (512x512, 85% S1 full-bleed, Opaque RGB #040710)")

    # 2. 512x512 maskable icon (76% safe-zone full-bleed)
    icon_maskable = generate_s1_fullbleed_icon(512, 0.76, is_maskable=True)
    icon_maskable.save("icon-512-maskable.png", "PNG")
    print("✓ Created icon-512-maskable.png (512x512, 76% S1 maskable, Opaque RGB #040710)")

    # 3. 192x192 standard icon (85% full-bleed)
    icon_192 = generate_s1_fullbleed_icon(192, 0.85, is_maskable=False)
    icon_192.save("icon-192.png", "PNG")
    print("✓ Created icon-192.png (192x192, 85% S1 full-bleed, Opaque RGB #040710)")

    # 4. 180x180 Apple Touch Icon (85% full-bleed)
    icon_180 = generate_s1_fullbleed_icon(180, 0.85, is_maskable=False)
    icon_180.save("apple-touch-icon.png", "PNG")
    print("✓ Created apple-touch-icon.png (180x180, 85% S1 full-bleed, Opaque RGB #040710)")

    # 5. Multi-size favicon.ico (16, 32, 48, 64)
    icon_64 = generate_s1_fullbleed_icon(64, 0.85, is_maskable=False)
    icon_48 = generate_s1_fullbleed_icon(48, 0.85, is_maskable=False)
    icon_32 = generate_s1_fullbleed_icon(32, 0.85, is_maskable=False)
    icon_16 = generate_s1_fullbleed_icon(16, 0.85, is_maskable=False)
    icon_64.save("favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print("✓ Created favicon.ico (multi-size, 85% S1 full-bleed)")

    # Mirror to docs/ and dashboard/
    for t in ["docs", "dashboard"]:
        os.makedirs(t, exist_ok=True)
        for fname in ["icon-512.png", "icon-512-maskable.png", "icon-192.png", "apple-touch-icon.png", "favicon.ico"]:
            shutil.copy2(fname, os.path.join(t, fname))
            print(f"✓ Mirrored {fname} -> {t}/{fname}")

    print("=== All S1 Pure Metallic Full-Bleed Icons Successfully Created! ===")

if __name__ == "__main__":
    main()


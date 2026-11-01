# -*- coding: utf-8 -*-
import os, sys, shutil
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw, ImageFilter

def create_aon_icon(size, is_maskable=False):
    # Base canvas: Dark space navy gradient
    img = Image.new("RGBA", (size, size), (5, 7, 14, 255))
    draw = ImageDraw.Draw(img)
    
    # Outer subtle glow / vignette
    cx, cy = size // 2, size // 2
    r_max = int(size * 0.48)
    
    # Draw radial gradient background
    for r in range(r_max, 0, -2):
        alpha = int(25 * (1.0 - r / r_max))
        # Warm gold-cyan core ambiance
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(12, 22, 45, alpha))
        
    # Open official logo 2 (Sangseonyaksu Emblem) and Avatar
    logo2 = Image.open("s1_logo_2.png").convert("RGBA")
    
    # Determine safe scaling factor
    if is_maskable:
        # Maskable safe zone: 65% of size to ensure 100% visibility in any squircle/circle
        target_size = int(size * 0.72)
    else:
        target_size = int(size * 0.88)
        
    logo_resized = logo2.resize((target_size, target_size), Image.Resampling.LANCZOS)
    
    # Gold ambient circle behind emblem
    if not is_maskable:
        ring_r = int(target_size * 0.46)
        draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], 
                     outline=(212, 175, 55, 120), width=max(2, size // 120))
                     
    # Paste centered
    offset_x = (size - target_size) // 2
    offset_y = (size - target_size) // 2
    img.alpha_composite(logo_resized, (offset_x, offset_y))
    
    return img

def main():
    print("=== [S1 MOBILE ICON FACTORY] ===")
    
    # 1. Generate 512x512 standard
    icon_512 = create_aon_icon(512, is_maskable=False)
    icon_512.save("icon-512.png", "PNG")
    print("✓ Created icon-512.png (512x512)")
    
    # 2. Generate 512x512 maskable (Safe Zone compliant)
    icon_maskable = create_aon_icon(512, is_maskable=True)
    icon_maskable.save("icon-512-maskable.png", "PNG")
    print("✓ Created icon-512-maskable.png (512x512 maskable)")
    
    # 3. Generate 192x192
    icon_192 = create_aon_icon(192, is_maskable=False)
    icon_192.save("icon-192.png", "PNG")
    print("✓ Created icon-192.png (192x192)")
    
    # 4. Generate 180x180 Apple Touch Icon
    icon_180 = create_aon_icon(180, is_maskable=False)
    icon_180.save("apple-touch-icon.png", "PNG")
    print("✓ Created apple-touch-icon.png (180x180)")
    
    # 5. Generate Multi-size Favicon.ico (16, 32, 48, 64)
    icon_64 = create_aon_icon(64, is_maskable=False)
    icon_48 = create_aon_icon(48, is_maskable=False)
    icon_32 = create_aon_icon(32, is_maskable=False)
    icon_16 = create_aon_icon(16, is_maskable=False)
    icon_64.save("favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print("✓ Created favicon.ico (multi-size 16~64)")
    
    # Copy to target directories: docs/ and dashboard/
    targets = ["docs", "dashboard"]
    for t in targets:
        os.makedirs(t, exist_ok=True)
        for fname in ["icon-512.png", "icon-512-maskable.png", "icon-192.png", "apple-touch-icon.png", "favicon.ico"]:
            shutil.copy2(fname, os.path.join(t, fname))
            print(f"✓ Mirrored {fname} -> {t}/{fname}")
            
    print("=== All SUN-ONE AON App Icons Successfully Built! ===")

if __name__ == "__main__":
    main()

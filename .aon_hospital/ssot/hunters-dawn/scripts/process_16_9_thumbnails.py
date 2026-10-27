from PIL import Image, ImageFilter, ImageEnhance
import os, glob

art_dir = r'C:\Users\sangi\.gemini\antigravity-ide\brain\bc8a551c-acf7-4bde-a174-2e3cb9ec9625'
export_dir = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\04_export'
downloads_dir = r'C:\Users\sangi\Downloads'

target_w, target_h = 1920, 1080

def convert_to_16_9(src_path, out_paths):
    im = Image.open(src_path).convert('RGB')
    orig_w, orig_h = im.size
    
    # Method: Create 16:9 frame with high-quality blurred ambient background + center hero framing
    # 1. Background image scaled to fill 1920x1080
    bg = im.resize((target_w, int(target_w * orig_h / orig_w)), Image.Resampling.LANCZOS)
    # Crop top and bottom of bg to make exactly 1920x1080
    bg_h = bg.height
    top = (bg_h - target_h) // 2
    bg_cropped = bg.crop((0, top, target_w, top + target_h))
    
    # Apply cinematic blur and slight dimming to background
    bg_blurred = bg_cropped.filter(ImageFilter.GaussianBlur(radius=25))
    enhancer = ImageEnhance.Brightness(bg_blurred)
    bg_darkened = enhancer.enhance(0.7)
    
    # 2. Main subject: center crop/fit 16:9 active subject
    # Scale main subject to fit height 1080
    scaled_h = target_h
    scaled_w = int(orig_w * scaled_h / orig_h) # 1080 x 1080 square in center
    main_fg = im.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
    
    # Paste main_fg onto center of bg_darkened
    paste_x = (target_w - scaled_w) // 2
    bg_darkened.paste(main_fg, (paste_x, 0))
    
    # Save to all target paths
    for p in out_paths:
        bg_darkened.save(p, quality=98)
    print(f"Successfully converted {os.path.basename(src_path)} to 1920x1080 16:9!")

def process_all():
    for i in range(1, 6):
        fname = f"v2_thumbnail_{i}.png"
        src_path = os.path.join(art_dir, fname)
        if os.path.exists(src_path):
            out_name = f"yt_16_9_thumbnail_{i}.png"
            out_paths = [
                os.path.join(art_dir, out_name),
                os.path.join(export_dir, out_name),
                os.path.join(downloads_dir, out_name),
                os.path.join(downloads_dir, f"thumbnail_16_9_{i}.png")
            ]
            convert_to_16_9(src_path, out_paths)

if __name__ == '__main__':
    process_all()

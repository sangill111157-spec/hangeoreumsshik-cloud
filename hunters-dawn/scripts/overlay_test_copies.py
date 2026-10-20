import os
import glob
from PIL import Image, ImageDraw, ImageFont

art_dir = r'C:\Users\sangi\.gemini\antigravity-ide\brain\bc8a551c-acf7-4bde-a174-2e3cb9ec9625'
export_dir = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\04_export'
downloads_dir = r'C:\Users\sangi\Downloads'

# Find source image
src_file = None
for f in glob.glob(os.path.join(downloads_dir, '*.*')):
    name = os.path.basename(f)
    if '사냥꾼의 새벽 썸네일 이미지' in name or '사냥꾼' in name and '썸네일' in name:
        src_file = f
        break

if not src_file:
    raise FileNotFoundError("Could not find 사냥꾼의 새벽 썸네일 이미지.png in Downloads")

print("Source Image:", src_file)
base_img = Image.open(src_file).convert('RGB')
w, h = base_img.size # 3840 x 2160

# 5 Test Copy Concepts
TEST_COPIES = [
    {
        "id": 1,
        "title": "TYPE 1 [알고리즘 CTR 극대화]",
        "sub": "사냥꾼의 새벽 | Hunter's Dawn",
        "main": "절망을 사냥하라",
        "tag": "OFFICIAL MUSIC VIDEO",
        "main_color": "#FFD700", # Golden yellow
        "align": "left"
    },
    {
        "id": 2,
        "title": "TYPE 2 [감성 서사 몰입형]",
        "sub": "어둠을 뚫고 나온 순수한 빛",
        "main": "내 안의 빛으로",
        "tag": "Break the Chains of Dark",
        "main_color": "#FFFFFF",
        "align": "left"
    },
    {
        "id": 3,
        "title": "TYPE 3 [수노 음원 힐링 타겟]",
        "sub": "지친 영혼을 깨우는 아침 선율",
        "main": "너라는 기적",
        "tag": "Acoustic Folk Pop MV",
        "main_color": "#00FFFF", # Cyan neon accent
        "align": "left"
    },
    {
        "id": 4,
        "title": "TYPE 4 [직관적 임팩트 카피]",
        "sub": "사냥꾼의 새벽 1",
        "main": "부정의 마인드를 깨부숴라",
        "tag": "Action Over Fear",
        "main_color": "#FF3366", # Vibrant pink-red accent
        "align": "left"
    },
    {
        "id": 5,
        "title": "TYPE 5 [시네마틱 아티스트 커버]",
        "sub": "SUNO AI ORIGINAL SOUNDTRACK",
        "main": "HUNTER'S DAWN",
        "tag": "빛의 길로 함께 걷는다",
        "main_color": "#FFCC00",
        "align": "left"
    }
]

# Load Font (Pretendard / Malgun Gothic / Arial)
font_paths = [
    r"C:\Windows\Fonts\malgunbd.ttf",
    r"C:\Windows\Fonts\malgun.ttf",
    r"C:\Windows\Fonts\arialbd.ttf"
]

font_main_path = font_paths[0]

def draw_text_with_shadow(draw, position, text, font, text_color, shadow_color="#000000", stroke_width=6):
    x, y = position
    # Draw stroke/outline
    draw.text((x, y), text, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=shadow_color)

def generate_text_thumbnails():
    font_main = ImageFont.truetype(font_main_path, 150)
    font_sub = ImageFont.truetype(font_main_path, 75)
    font_tag = ImageFont.truetype(font_main_path, 60)

    for item in TEST_COPIES:
        img = base_img.copy()
        draw = ImageDraw.Draw(img)

        # Positioning: Upper-Left safe area (x=180, y=180) to avoid YouTube timestamp overlay (bottom-right)
        start_x = 180
        start_y = 180

        # Draw Tag/Badge
        draw_text_with_shadow(draw, (start_x, start_y), f"[{item['tag']}]", font_tag, "#FFD700", stroke_width=4)

        # Draw Main Headline
        draw_text_with_shadow(draw, (start_x, start_y + 100), item['main'], font_main, item['main_color'], stroke_width=10)

        # Draw Subtitle
        draw_text_with_shadow(draw, (start_x, start_y + 300), item['sub'], font_sub, "#FFFFFF", stroke_width=6)

        out_name = f"thumbnail_test_{item['id']}.png"
        out_paths = [
            os.path.join(art_dir, out_name),
            os.path.join(export_dir, out_name),
            os.path.join(downloads_dir, out_name),
            os.path.join(downloads_dir, f"사냥꾼의새벽_테스트문구_{item['id']}.png")
        ]

        for p in out_paths:
            img.save(p, quality=98)
        print(f"Generated Test Copy Thumbnail {item['id']} successfully!")

if __name__ == '__main__':
    generate_text_thumbnails()

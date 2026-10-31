import json, pathlib, subprocess
from PIL import Image, ImageDraw, ImageFont
root = next(pathlib.Path('G:/').rglob('S1_SUN_ONE_AON'))
spec_p = root / '01_design_spec' / 'S1_EP01_spec.json'
spec = json.loads(spec_p.read_text(encoding='utf-8'))
vis_dir = root / '02_visual_clips'
out_dir = root / '04_final_mp4'
out_dir.mkdir(exist_ok=True)
font_bold = "C:/Windows/Fonts/malgunbd.ttf"
sub_clips = []
for sc in spec['scenes']:
    sno = sc['scene_no']
    raw_clip = vis_dir / f"clip_{sno}.mp4"
    ov_png = vis_dir / f"overlay_{sno}.png"
    sub_clip = vis_dir / f"sub_clip_{sno}.mp4"
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    for y in range(1320, 1780):
        alpha = int(170 * (1 - abs(y - 1550) / 240))
        alpha = max(0, min(170, alpha))
        dr.line([(60, y), (1020, y)], fill=(8, 12, 22, alpha))
    f_cap = ImageFont.truetype(font_bold, 78)
    lines = sc['impact_caption'].split('\n')
    for idx, line in enumerate(lines[:2]):
        yy = 1430 + idx * 110
        color = (255, 225, 80, 255) if idx == 0 else (255, 255, 255, 255)
        for dx in (-4, 0, 4):
            for dy in (-4, 0, 4):
                if dx or dy:
                    dr.text((540 + dx, yy + dy), line, font=f_cap, fill=(0, 0, 0, 240), anchor="mm")
        dr.text((540, yy), line, font=f_cap, fill=color, anchor="mm")
    f_logo = ImageFont.truetype(font_bold, 30)
    dr.rounded_rectangle[880, 1810, 1030, 1870]  if False else dr.rectangle([880, 1810, 1030, 1870], fill=(15, 20, 30, 140), outline=(210, 220, 240, 160), width=2)
    dr.text((955, 1840), "S1 AON", font=f_logo, fill=(235, 240, 255, 210), anchor="mm")
    im.save(ov_png)
    subprocess.run(['ffmpeg','-y','-i',str(raw_clip),'-i',str(ov_png),'-filter_complex','[0:v][1:v]overlay=0:0,format=yuv420p','-c:v','libx264','-preset','fast','-crf','19',str(sub_clip)], capture_output=True)
    sub_clips.append(str(sub_clip))
concat_v = vis_dir / 'concat_v.txt'
concat_v.write_text('\n'.join([f"file '{p.replace(chr(92), '/')}'" for p in sub_clips]), encoding='utf-8')
merged_v = vis_dir / 'merged_v.mp4'
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat_v),'-c','copy',str(merged_v)], capture_output=True)
final_mp4 = out_dir / 'S1_EP01_FINAL_MASTER.mp4'
master_audio = spec['master_audio_path']
subprocess.run(['ffmpeg','-y','-i',str(merged_v),'-i',str(master_audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-shortest',str(final_mp4)], capture_output=True)
snaps = []
for sc in spec['scenes']:
    sno = sc['scene_no']
    mid_t = round(sc['start_sec'] + sc['duration_sec']/2, 2)
    snap_p = out_dir / f"verify_scene_{sno}.jpg"
    subprocess.run(['ffmpeg','-y','-ss',s(tr(mid_t)) if False else str(mid_t),'-i',str(final_mp4),'-frames:v','1','-q:v','2',str(snap_p)], capture_output=True)
    snaps.append((sno, snap_p.exists()))
print('WORKSHOP_04_FINAL_MP4 ->', final_mp4, '| SIZE_KB:', round(final_mp4.stat().st_size/1024, 1), 't Snaps:', snaps)

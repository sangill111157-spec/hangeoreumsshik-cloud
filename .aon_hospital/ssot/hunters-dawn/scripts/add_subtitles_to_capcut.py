import os
import json
import uuid

# Subtitle entries with microsecond timing
SRT_ENTRIES = [
    {"start": 0, "end": 16724000, "text": "사냥꾼의 새벽 (Hunter's Dawn)\nAI Music Video", "is_title": True},
    {"start": 0, "end": 16724000, "text": "(휘파람 인트로 / Whistling Intro)\n[바깥세상이 그를 부르는 소리]", "is_title": False},
    {"start": 16724000, "end": 25000000, "text": "어두운 방 안, 멈춰버린 시간\nIn a dim grey room, time has stopped", "is_title": False},
    {"start": 25000000, "end": 35000000, "text": "창틈으로 흘러든 작은 빛 줄기 하나\nA thin blade of light drifts through the gap", "is_title": False},
    {"start": 35000000, "end": 45991000, "text": "오래된 기타 위에 살포시 내려앉은 홀씨\nA dandelion seed settles on the dusty guitar", "is_title": False},
    {"start": 45991000, "end": 54000000, "text": "하지만 난 나의 칼을 뽑아든다 (어쿠스틱 기타를 잡는다)\nBut I draw my sword", "is_title": False},
    {"start": 54000000, "end": 62712000, "text": "커튼을 젖히자 몰아치는 봄날의 햇살\nSweep open the curtains, sunshine floods in", "is_title": False},
    {"start": 62712000, "end": 75000000, "text": "사슬을 끊어내고 문밖으로 발을 내딛는다\nBreak the chains and step into the light", "is_title": False},
    {"start": 75000000, "end": 85000000, "text": "일어나라, 사냥꾼이여! 눈부신 초원 속으로\nRise up, Hunter! Into the sunlit meadow", "is_title": False},
    {"start": 85000000, "end": 96160000, "text": "슬픔을 추격하며 바람 속을 뛰어오른다\nHunting down the sorrow in the wind", "is_title": False},
    {"start": 96160000, "end": 106000000, "text": "오직 너만이 이 봄의 주인공이다\nYou are the one", "is_title": False},
    {"start": 106000000, "end": 116000000, "text": "자전거를 타고 달리는 리드미컬한 시골길\nRiding the old bicycle down the sunny path", "is_title": False},
    {"start": 116000000, "end": 125432000, "text": "마을 사람들과 나누는 따뜻한 미소\nExchanging warmth with people on the street", "is_title": False},
    {"start": 125432000, "end": 135000000, "text": "개울물을 차오르며 튀어 오르는 영롱한 빗방울\nSplashing through the stream, droplets scattering", "is_title": False},
    {"start": 135000000, "end": 145000000, "text": "영혼의 갑옷을 입고 빛을 향해 걷는다\nArmor for your soul, walking into the light", "is_title": False},
    {"start": 145000000, "end": 150511000, "text": "바람이 불어오는 커다란 벚꽃나무 아래\nUnder the huge blossoming tree", "is_title": False},
    {"start": 150511000, "end": 160000000, "text": "가슴속에서 반짝이는 다이아몬드를 믿어라\nTrust the diamond in your chest", "is_title": False},
    {"start": 160000000, "end": 171417000, "text": "눈을 뜨면 마주하는 확신에 찬 평온함\nOpening eyes with calm certainty", "is_title": False},
    {"start": 171417000, "end": 178000000, "text": "이제 우리는 함께 이 길을 걸어간다\nNow we walk this golden path together", "is_title": False},
    {"start": 178000000, "end": 182000000, "text": "모두가 어우러져 들려주는 희망의 리듬\nClapping in rhythm, singing under the sky", "is_title": False},
    {"start": 182000000, "end": 184000000, "text": "하늘 높이 휘파람을 불며 응답한다\nWhistling back into the golden sky", "is_title": False},
    {"start": 184000000, "end": 185480000, "text": "(자유롭게 날아오르는 갈색 새와 민들레 홀씨)\n[The bird and dandelion seed released into light]", "is_title": False}
]

def make_capcut_text_material(text, is_title=False):
    text_id = str(uuid.uuid4()).upper()
    
    # Format HTML content for CapCut XML/HTML text renderer
    html_content = f"<font color=\"#ffffff\"><span>{text.replace(chr(10), '<br>')}</span></font>"

    size = 10.0 if is_title else 5.5
    
    mat = {
        "add_type": 0,
        "alignment": 1, # Center alignment
        "background_alpha": 1.0,
        "background_color": "",
        "background_height": 1.0,
        "background_horizontal_offset": 0.0,
        "background_round_radius": 0.0,
        "background_style": 0,
        "background_vertical_offset": 0.0,
        "background_width": 1.0,
        "bold_alpha": 1.0,
        "border_color": "",
        "border_width": 0.0,
        "check_flag": 7,
        "combo_info": {"text_templates": []},
        "content": html_content,
        "font_category_id": "",
        "font_category_name": "",
        "font_id": "",
        "font_name": "Pretendard",
        "font_path": "",
        "font_resource_id": "",
        "font_size": size,
        "font_title": "none",
        "font_url": "",
        "fonts": [],
        "global_alpha": 1.0,
        "has_shadow": True,
        "id": text_id,
        "initial_scale": 1.0,
        "inner_padding": -1.0,
        "italic_degree": 0,
        "ktv_color": "",
        "language": "",
        "layer_weight": 1,
        "letter_spacing": 0.0,
        "line_feed": 1,
        "line_spacing": 0.02,
        "name": "Title Text" if is_title else "Subtitle Text",
        "original_size": [],
        "preset_category": "",
        "preset_category_id": "",
        "preset_has_set_alignment": False,
        "preset_id": "",
        "preset_index": 0,
        "preset_name": "",
        "recognize_type": 0,
        "shadow_alpha": 0.9,
        "shadow_angle": -45.0,
        "shadow_color": "#000000",
        "shadow_distance": 6.0,
        "shadow_point": {"x": 0.005, "y": -0.005},
        "shadow_smoothing": 0.15,
        "shadow_use": True,
        "stroke_color": "#000000",
        "stroke_width": 0.06,
        "style_name": "",
        "sub_type": 0,
        "text_alpha": 1.0,
        "text_color": "#FFFFFF",
        "text_curve": None,
        "text_preset_resource_id": "",
        "text_size": 30 if is_title else 22,
        "text_to_audio_ids": [],
        "type": "text",
        "use_event": False
    }
    return text_id, mat

def update_capcut_project():
    p_dir = r'C:\Users\sangi\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\0801'
    draft_content_path = os.path.join(p_dir, 'draft_content.json')
    backup_path = os.path.join(p_dir, 'draft_content.json.bak')

    with open(draft_content_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Save Backup
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Backup created at:", backup_path)

    # Prepare Title & Subtitle Materials and Segments
    title_segments = []
    sub_segments = []

    text_materials = data["materials"].get("texts", [])

    for entry in SRT_ENTRIES:
        t_id, mat = make_capcut_text_material(entry["text"], entry["is_title"])
        text_materials.append(mat)

        seg_id = str(uuid.uuid4()).upper()
        dur = entry["end"] - entry["start"]

        y_pos = 0.65 if entry["is_title"] else -0.75 # Top-center for title, Bottom-center for subtitles

        seg = {
            "clip": {
                "alpha": 1.0,
                "flip": {"horizontal": False, "vertical": False},
                "rotation": 0.0,
                "scale": {"x": 1.0, "y": 1.0},
                "transform": {"x": 0.0, "y": y_pos}
            },
            "common_keyframes": [],
            "enable_adjust": True,
            "enable_color_curves": True,
            "enable_color_wheels": True,
            "enable_lut": True,
            "enable_smart_color_adjust": False,
            "extra_material_refs": [],
            "group_id": "",
            "id": seg_id,
            "intensifies_audio": False,
            "is_placeholder": False,
            "is_unsupported_sub_video": False,
            "keyframe_refs": [],
            "material_id": t_id,
            "render_index": 0,
            "responsive_layout": {
                "enable": False,
                "horizontal_pos_type": 0,
                "target_follow": "",
                "vertical_pos_type": 0
            },
            "reverse": False,
            "source_timerange": {"duration": 0, "start": 0},
            "speed": 1.0,
            "target_timerange": {
                "duration": dur,
                "start": entry["start"]
            },
            "track_attribute": 0,
            "track_render_index": 0,
            "visible": True
        }

        if entry["is_title"]:
            title_segments.append(seg)
        else:
            sub_segments.append(seg)

    data["materials"]["texts"] = text_materials

    # Remove previous text tracks if any
    data["tracks"] = [t for t in data["tracks"] if t.get("type") != "text"]

    # Add Title Track
    title_track_id = str(uuid.uuid4()).upper()
    data["tracks"].append({
        "attribute": 0,
        "flag": 0,
        "id": title_track_id,
        "is_main_track": False,
        "name": "Main Title",
        "segments": title_segments,
        "type": "text"
    })

    # Add Subtitles Track
    sub_track_id = str(uuid.uuid4()).upper()
    data["tracks"].append({
        "attribute": 0,
        "flag": 0,
        "id": sub_track_id,
        "is_main_track": False,
        "name": "Lyrics Subtitles",
        "segments": sub_segments,
        "type": "text"
    })

    # Write updated draft_content.json
    with open(draft_content_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Successfully added Title (1 segment) and Subtitles ({len(sub_segments)} segments) to CapCut 0801 project!")

if __name__ == '__main__':
    update_capcut_project()

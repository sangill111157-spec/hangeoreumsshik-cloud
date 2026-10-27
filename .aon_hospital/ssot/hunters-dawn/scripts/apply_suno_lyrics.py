import os
import json
import uuid

# Official Suno Lyrics for "사냥꾼의 새벽 1 (Hunter's Dawn)"
SUNO_LYRICS = [
    # Intro
    {"start": 0, "end": 16724000, "text": "사냥꾼의 새벽 1 (Hunter's Dawn)\nAI Music Video", "is_title": True},
    {"start": 0, "end": 16724000, "text": "(Intro - Whistling & Cold Wind)", "is_title": False},
    
    # Verse 1
    {"start": 16724000, "end": 23000000, "text": "심장을 파고드는 Cold shadows in the night", "is_title": False},
    {"start": 23000000, "end": 30000000, "text": "도망쳐봐도 끈질긴 Demons in my mind", "is_title": False},
    {"start": 30000000, "end": 38000000, "text": "\"난 안 될 거야\"라는 The lies they keep on telling", "is_title": False},
    {"start": 38000000, "end": 45991000, "text": "내 영혼을 갉아먹는 The darkness they’re compelling", "is_title": False},
    {"start": 45991000, "end": 50000000, "text": "But I draw my sword, 이 침묵을 베어내", "is_title": False},
    {"start": 50000000, "end": 54000000, "text": "No more falling back, 이제는 깨어나야 해", "is_title": False},

    # Pre-Chorus
    {"start": 54000000, "end": 60000000, "text": "가장 깊은 어둠은 The darkest hour before dawn", "is_title": False},
    {"start": 60000000, "end": 65000000, "text": "포기하지 마, Your spirit’s not yet gone", "is_title": False},
    {"start": 65000000, "end": 70000000, "text": "차가운 빗줄기는 The armor for your soul", "is_title": False},
    {"start": 70000000, "end": 75000000, "text": "너를 더 단단하게 해, To make you finally whole", "is_title": False},

    # Chorus 1
    {"start": 75000000, "end": 79000000, "text": "Rise up, Hunter! 넌 무너지지 않아", "is_title": False},
    {"start": 79000000, "end": 83000000, "text": "내 안의 빛으로 Break the chains of the dark", "is_title": False},
    {"start": 83000000, "end": 87000000, "text": "너라는 기적은 The only reason I survive", "is_title": False},
    {"start": 87000000, "end": 91500000, "text": "살아가야 할 이유, You keep my heart alive", "is_title": False},
    {"start": 91500000, "end": 94500000, "text": "You are the one, 세상을 밝힐 유일한 존재", "is_title": False},
    {"start": 94500000, "end": 96160000, "text": "절망을 사냥해, Until the light remains for me and you", "is_title": False},

    # Verse 2
    {"start": 96160000, "end": 101000000, "text": "Abundance is a choice, 풍요는 나의 결단", "is_title": False},
    {"start": 101000000, "end": 106000000, "text": "부정의 마인드란 The monster’s last resistance", "is_title": False},
    {"start": 106000000, "end": 111000000, "text": "비난보다는 확신을, Action over fear", "is_title": False},
    {"start": 111000000, "end": 116000000, "text": "승리의 함성이 The victory is near", "is_title": False},
    {"start": 116000000, "end": 121000000, "text": "내 생각의 크기가 The map of my domain", "is_title": False},
    {"start": 121000000, "end": 125432000, "text": "Hunting down the sorrow, washing off the pain", "is_title": False},

    # Bridge
    {"start": 125432000, "end": 131704000, "text": "상처 입은 영혼이여, Trust the diamond in your chest", "is_title": False},
    {"start": 131704000, "end": 137976000, "text": "지친 너의 어깨 위로 Sunshine will do the rest", "is_title": False},
    {"start": 137976000, "end": 144248000, "text": "너의 존재 자체가 A sacred masterpiece", "is_title": False},
    {"start": 144248000, "end": 150519000, "text": "어둠을 뚫고 나와, Find your inner peace!", "is_title": False},

    # Chorus 2
    {"start": 150519000, "end": 154700000, "text": "Rise up, Hunter! 넌 무너지지 않아", "is_title": False},
    {"start": 154700000, "end": 158881000, "text": "내 안의 빛으로 Break the chains of the dark", "is_title": False},
    {"start": 158881000, "end": 163062000, "text": "너라는 기적은 The only reason I survive", "is_title": False},
    {"start": 163062000, "end": 167243000, "text": "살아가야 할 이유, You keep my heart alive", "is_title": False},
    {"start": 167243000, "end": 169500000, "text": "You are the one, 세상을 밝힐 유일한 존재", "is_title": False},
    {"start": 169500000, "end": 171425000, "text": "절망을 사냥해, Until the light remains for me and you", "is_title": False},

    # Outro
    {"start": 171425000, "end": 175606000, "text": "I am the hunter, I am the light.", "is_title": False},
    {"start": 175606000, "end": 179787000, "text": "감사함으로 깨운 아침, The demons take flight.", "is_title": False},
    {"start": 179787000, "end": 182923000, "text": "이제 빛의 길로, Together we walk.", "is_title": False},
    {"start": 182923000, "end": 185480000, "text": "Into the dawn.", "is_title": False}
]

def format_srt_time(ms):
    s, ms_rem = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms_rem:03d}"

def update_srt_and_capcut():
    # 1. Update subs.srt
    srt_path = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\04_export\subs.srt'
    idx = 1
    srt_lines = []
    
    for item in SUNO_LYRICS:
        start_ms = item["start"] // 1000
        end_ms = item["end"] // 1000
        time_str = f"{format_srt_time(start_ms)} --> {format_srt_time(end_ms)}"
        srt_lines.append(f"{idx}\n{time_str}\n{item['text']}\n\n")
        idx += 1
        
    with open(srt_path, 'w', encoding='utf-8') as f:
        f.writelines(srt_lines)
    print("Successfully updated 04_export/subs.srt with official Suno lyrics!")

    # 2. Update CapCut 0801 Project
    p_dir = r'C:\Users\sangi\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\0801'
    draft_content_path = os.path.join(p_dir, 'draft_content.json')
    
    with open(draft_content_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    title_segments = []
    sub_segments = []
    text_materials = []

    for entry in SUNO_LYRICS:
        t_id = str(uuid.uuid4()).upper()
        size = 10.0 if entry["is_title"] else 5.5
        html_content = f"<font color=\"#ffffff\"><span>{entry['text'].replace(chr(10), '<br>')}</span></font>"
        
        mat = {
            "add_type": 0,
            "alignment": 1,
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
            "id": t_id,
            "initial_scale": 1.0,
            "inner_padding": -1.0,
            "italic_degree": 0,
            "ktv_color": "",
            "language": "",
            "layer_weight": 1,
            "letter_spacing": 0.0,
            "line_feed": 1,
            "line_spacing": 0.02,
            "name": "Title Text" if entry["is_title"] else "Subtitle Text",
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
            "text_size": 30 if entry["is_title"] else 22,
            "text_to_audio_ids": [],
            "type": "text",
            "use_event": False
        }
        text_materials.append(mat)

        seg_id = str(uuid.uuid4()).upper()
        dur = entry["end"] - entry["start"]
        y_pos = 0.65 if entry["is_title"] else -0.75

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
    data["tracks"] = [t for t in data["tracks"] if t.get("type") != "text"]

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

    with open(draft_content_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Successfully injected official Suno lyrics ({len(sub_segments)} segments) into CapCut 0801 project!")

if __name__ == '__main__':
    update_srt_and_capcut()

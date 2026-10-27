import json

def update_shots():
    # Sound Map Ground Truth Cut Schedule (43 cuts total with S14b, S19b, S20b)
    new_shots = [
        # INTRO (G1)
        {"id": "S01", "section": "INTRO", "tc_in": 0.000, "tc_out": 4.181, "beats": 8, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Extreme macro, dew drop on a blade of grass at dawn, golden light, 16mm film still", "motion_prompt": "Dew drop falls on whistle sound", "note": "휘파람 1악절"},
        {"id": "S03", "section": "INTRO", "tc_in": 4.181, "tc_out": 8.362, "beats": 8, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Wide hillside village waking in morning mist, dark window in frame", "motion_prompt": "Mist drifts slowly", "note": "휘파람 2악절 (S03 교차)"},
        {"id": "S02", "section": "INTRO", "tc_in": 8.362, "tc_out": 10.453, "beats": 4, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Small brown bird on a power line backlit by sun", "motion_prompt": "Bird tilts head and pauses", "note": "휘파람 멎음 (bird_ref.png 저장)"},
        {"id": "S04", "section": "INTRO", "tc_in": 10.453, "tc_out": 13.589, "beats": 6, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Dim bedroom interior, thin blade of light, dandelion seed floating in", "motion_prompt": "Seed drifts through light shaft", "note": "바깥의 부름 침투"},
        {"id": "S05", "section": "INTRO", "tc_in": 13.589, "tc_out": 16.724, "beats": 6, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Dandelion seed settles on dusty honey acoustic guitar", "motion_prompt": "Seed lands and rests", "note": "휘파람 13.89s 재진입 포함"},

        # VERSE 1 (G2)
        {"id": "S06", "section": "VERSE 1", "tc_in": 16.724, "tc_out": 21.951, "beats": 10, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Man lying awake on bed in dim room, grey overcast light", "motion_prompt": "Shifts slightly, exhales", "note": "무기력"},
        {"id": "S07", "section": "VERSE 1", "tc_in": 21.951, "tc_out": 27.178, "beats": 10, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Close-up face tired open eyes staring at ceiling", "motion_prompt": "Slow blink", "note": "expr_tired 참조"},
        {"id": "S08", "section": "VERSE 1", "tc_in": 27.178, "tc_out": 30.314, "beats": 6, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Phone screen glowing in dim room, scrolling feed", "motion_prompt": "Endless scroll", "note": ""},
        {"id": "S09", "section": "VERSE 1", "tc_in": 30.314, "tc_out": 33.440, "beats": 6, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Macro seed on guitar body, light shaft widening", "motion_prompt": "Dust motes drift", "note": "32.395 박수 픽업 후 33.440 진입"},
        {"id": "S10", "section": "VERSE 1", "tc_in": 33.440, "tc_out": 39.721, "beats": 12, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Hand reaches into light shaft and closes around guitar neck", "motion_prompt": "Hand grips guitar firmly", "note": "★1막 전환점 (33.440 시작 고정)"},
        {"id": "S11", "section": "VERSE 1", "tc_in": 39.721, "tc_out": 45.991, "beats": 12, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "First strum, dust explodes into light beam around soundhole", "motion_prompt": "Strings vibrate, light blooms", "note": "45.991에 정확히 종료"},

        # PRECHORUS (G3)
        {"id": "S12", "section": "PRE-CHORUS", "tc_in": 45.991, "tc_out": 50.172, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Throws open curtains, sunlight floods room", "motion_prompt": "Curtains sweep open", "note": "빛 유입"},
        {"id": "S13", "section": "PRE-CHORUS", "tc_in": 50.172, "tc_out": 54.354, "beats": 8, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Macro raindrops on windowpane, sunlit", "motion_prompt": "Drop slides down catching light", "note": "★리프 4타(51.220~52.788) 싱크"},
        {"id": "S14", "section": "PRE-CHORUS", "tc_in": 54.354, "tc_out": 58.535, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Steps out front door onto wet street, guitar on back", "motion_prompt": "Steps through doorway", "note": ""},
        {"id": "S14b", "section": "PRE-CHORUS", "tc_in": 58.535, "tc_out": 62.712, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Walking toward meadow entrance, sunlight brightening", "motion_prompt": "Fast stride forward", "note": "신규 확보 컷 (프롬프트 추가 예정)"},

        # CHORUS 1 (G4)
        {"id": "S15", "section": "CHORUS 1", "tc_in": 62.712, "tc_out": 66.893, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "HERO shot, walks into vast sunlit spring meadow", "motion_prompt": "Walks toward camera, petals swirl", "note": "HERO shot"},
        {"id": "S16", "section": "CHORUS 1", "tc_in": 66.893, "tc_out": 71.074, "beats": 8, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Low angle blossom branches against blue sky", "motion_prompt": "Petals fall toward camera", "note": ""},
        {"id": "S17", "section": "CHORUS 1", "tc_in": 71.074, "tc_out": 75.255, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Close-up genuine open smile, sunlight on face", "motion_prompt": "Laughs and turns head", "note": "expr_laugh 참조"},
        {"id": "S18", "section": "CHORUS 1", "tc_in": 75.255, "tc_out": 77.346, "beats": 4, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Jumps and spins once in meadow", "motion_prompt": "Full spin and landing", "note": "4b로 축소"},
        {"id": "S19", "section": "CHORUS 1", "tc_in": 77.346, "tc_out": 81.527, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Stands still in tall grass, extreme wide long shot", "motion_prompt": "Grass sways in wind", "note": "★휘파람 78-80 포함. 인물 원경 고정, 립싱크 금지!"},
        {"id": "S19b", "section": "CHORUS 1", "tc_in": 81.527, "tc_out": 85.708, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Same wide framing, slow push-in toward silhouette", "motion_prompt": "Camera slow push-in", "note": "슬로우 푸시인"},
        {"id": "S20", "section": "CHORUS 1", "tc_in": 85.708, "tc_out": 89.889, "beats": 8, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Extreme wide aerial, tiny figure crossing hillside", "motion_prompt": "Camera rises and pulls back", "note": ""},
        {"id": "S20b", "section": "CHORUS 1", "tc_in": 89.889, "tc_out": 96.160, "beats": 12, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Wide vista sweeping shadow across green hills", "motion_prompt": "Clouds move fast overhead", "note": "신규 Chorus1 종결 컷"},

        # VERSE 2 (G5)
        {"id": "S21", "section": "VERSE 2", "tc_in": 96.160, "tc_out": 100.341, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Steadicam tracking stride along country road", "motion_prompt": "Camera tracks beside him", "note": ""},
        {"id": "S22", "section": "VERSE 2", "tc_in": 100.341, "tc_out": 104.522, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Rides old bicycle down tree-lined path", "motion_prompt": "Rides past camera", "note": ""},
        {"id": "S23", "section": "VERSE 2", "tc_in": 104.522, "tc_out": 108.703, "beats": 8, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Macro hands strumming acoustic guitar fast", "motion_prompt": "Hand strums rhythmically", "note": "115 BPM 온비트 동기화"},
        {"id": "S24", "section": "VERSE 2", "tc_in": 108.703, "tc_out": 112.884, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Passes neighbor and child exchanging nod", "motion_prompt": "Waves and laughs", "note": ""},
        {"id": "S25", "section": "VERSE 2", "tc_in": 112.884, "tc_out": 117.065, "beats": 8, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Top-down drone view of winding trail", "motion_prompt": "Camera rotates overhead", "note": ""},
        {"id": "S26", "section": "VERSE 2", "tc_in": 117.065, "tc_out": 121.246, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Splashes through shallow clear stream laughing", "motion_prompt": "Kicks water upward", "note": "축소 조정"},
        {"id": "S27", "section": "TRANSITION", "tc_in": 121.246, "tc_out": 125.432, "beats": 8, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Dandelion seeds drifting across pastel sky", "motion_prompt": "Seeds drift left to right", "note": "★Verse2->Bridge 전환 컷"},

        # BRIDGE (G6)
        {"id": "S28", "section": "BRIDGE", "tc_in": 125.432, "tc_out": 131.704, "beats": 12, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Sits under blossoming tree guitar in lap eyes closed", "motion_prompt": "Slow push-in", "note": "expr_peaceful 참조"},
        {"id": "S29", "section": "BRIDGE", "tc_in": 131.704, "tc_out": 137.976, "beats": 12, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Close-up chest sunlight filtering through leaves over heart", "motion_prompt": "Light patch pulses", "note": "★리프 4타(131.704~133.272)가 S28->S29 컷 타격!"},
        {"id": "S30", "section": "BRIDGE", "tc_in": 137.976, "tc_out": 144.248, "beats": 12, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Over-shoulder sun sweeping across shoulders", "motion_prompt": "Light sweeps across", "note": ""},
        {"id": "S31", "section": "BRIDGE", "tc_in": 144.248, "tc_out": 150.511, "beats": 12, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Extreme close-up opens eyes light reflected in iris", "motion_prompt": "Eyes open slowly", "note": ""},

        # CHORUS 2 (G7)
        {"id": "S32", "section": "CHORUS 2", "tc_in": 150.511, "tc_out": 154.692, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Same meadow four or five friends walk beside him", "motion_prompt": "Group walks toward camera", "note": "S15 동일 로케이션"},
        {"id": "S33", "section": "CHORUS 2", "tc_in": 154.692, "tc_out": 158.873, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Group jumping together mid-air laughing", "motion_prompt": "Jump and land", "note": ""},
        {"id": "S34", "section": "CHORUS 2", "tc_in": 158.873, "tc_out": 163.054, "beats": 8, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Close-up montage of laughing faces in sunlight", "motion_prompt": "Faces turn toward light", "note": ""},
        {"id": "S35", "section": "CHORUS 2", "tc_in": 163.054, "tc_out": 167.235, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Plays guitar in middle of group clapping in rhythm", "motion_prompt": "Strums, group claps on beat", "note": "박수 온비트 동기화"},
        {"id": "S36", "section": "CHORUS 2", "tc_in": 167.235, "tc_out": 171.417, "beats": 8, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Extreme wide group cresting green hill", "motion_prompt": "Crest hill and continue", "note": ""},

        # OUTRO (G7)
        {"id": "S37", "section": "OUTRO", "tc_in": 171.417, "tc_out": 175.598, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Golden hour group walking away down country road", "motion_prompt": "Walk away from camera", "note": ""},
        {"id": "S38", "section": "OUTRO", "tc_in": 175.598, "tc_out": 179.779, "beats": 8, "model_img": "NanoBanana", "model_vid": "Gemini Omni Flash", "char": "Y", "img_prompt": "Medium close-up stops walking purses lips and whistles", "motion_prompt": "Lifts chin and whistles", "note": "★주인공 휘파람 177-179 포함! (단독)"},
        {"id": "S39", "section": "OUTRO", "tc_in": 179.779, "tc_out": 183.437, "beats": 7, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Exact same bird on power line calling back then flying", "motion_prompt": "Bird calls and launches upward", "note": "bird_ref.png 필수 (휘파람 180- 진입)"},
        {"id": "S40", "section": "OUTRO", "tc_in": 183.437, "tc_out": 185.480, "beats": 4, "model_img": "NanoBanana", "model_vid": "Grok Imagine", "char": "N", "img_prompt": "Single dandelion seed floating up into warm white light", "motion_prompt": "Seed drifts upward into overexposure", "note": "페이드아웃"}
    ]

    for s in new_shots:
        s["duration"] = round(s["tc_out"] - s["tc_in"], 3)

    with open("shots.json", "w", encoding="utf-8") as f:
        json.dump(new_shots, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Updated shots.json with {len(new_shots)} cuts.")
    print(f"Total Duration Sum: {sum(s['duration'] for s in new_shots):.3f}s (Target: 185.480s)")

    # G8 Verification
    long_clips = [s for s in new_shots if s["duration"] > 5.0]
    print(f"Clips > 5.0s count: {len(long_clips)}")
    for lc in long_clips:
        print(f" - {lc['id']} ({lc['section']}): {lc['duration']}s | Model: {lc['model_vid']}")

if __name__ == '__main__':
    update_shots()

# -*- coding: utf-8 -*-
"""
[RULE_DATE / REASON / EXPIRY_CONDITION]
- Rule Date: 2026-11-02
- Reason: 7-Day Non-Viral Threads & Instagram High-Conversion Funnel with S1 Humanizer.
- Expiry Condition: Permanent (Universal 7-Day Growth Engine).

[INPUT / OUTPUT / KILL_SWITCH_CMD]
- Input: 12-Track Emotion Themes + 4-Track Genesis Master Info
- Output: S1_7DAYS_THREADS_GLOBAL_PACK (.json, .md) with AI cliches purged
- Kill Switch Command: S1_THREADS_DISABLED=1
"""
import os, sys, json
import s1_humanizer

# ==============================================================================
# [영양분 #3: instagram-agent-skill 26대 바이럴 훅 라이브러리 & 3단 해시태그]
# ==============================================================================
VIRAL_HOOKS_LIBRARY = {
    "curiosity_gap": [
        "대부분의 사람들이 모르는 3분 쉼표의 치명적인 비밀",
        "스포티파이 알고리즘이 침묵과 여백을 추천하기 시작한 이유",
        "번아웃 직전까지 아무도 알려주지 않았던 진실 하나",
        "단 1곡으로 머릿속 잡념을 90% 소거하는 음향 구조",
        "왜 성공한 사람들은 새벽에 이 잔잔한 멜로디만 반복해서 들을까?",
        "밤 11시 40분, 막차 승강장에서 모두가 멈춰 선 진짜 이유",
        "한 번 들으면 머릿속에서 떠나지 않는 '상선약수' 물의 주파수",
        "AI 시대에 가장 인간적인 음악이 살아남는 놀라운 원리",
        "당신이 밤에 잠들지 못했던 건 피로 때문이 아닙니다"
    ],
    "contrarian": [
        "열심히 살지 마세요. 오늘은 그냥 쉬어도 충분합니다",
        "음악을 들으며 억지 동기부여를 얻으려 하지 마세요",
        "더 빨리 가려는 노력이 오히려 당신의 영혼을 메마르게 합니다",
        "수백만 조회수 쇼츠보다 단 1명의 진성 청자가 귀한 이유",
        "성공학 책 100권보다 퇴근길 3분의 사색이 강력한 이유",
        "다투지 않고 낮은 곳으로 흐르는 음악이 어떻게 전 세계를 감동시키는가",
        "화려한 테크닉을 다 덜어낸 가장 단순한 어쿠스틱 선율의 힘",
        "침묵과 여백이 가장 거대한 오케스트라보다 위대한 이유"
    ],
    "story_opening": [
        "막차가 떠난 플랫폼 벤치에 혼자 앉아 이 글을 씁니다",
        "어머니가 차려주신 따뜻한 국 한 그릇이 문득 떠오르던 날",
        "새벽 2시, 모니터 불빛 앞에서 모든 걸 포기하고 싶었을 때",
        "초등학교 4학년 딸아이가 그려준 작은 물방울 스케치에서 시작된 기적",
        "차가운 겨울바람이 불어올 때면 문득 생각나는 한 사람",
        "10년 전 오늘, 나는 세상에서 가장 소중한 것을 잃어버렸습니다",
        "말없이 건넨 따뜻한 차 한 잔이 한 사람의 오늘을 살렸습니다",
        "서울의 좁은 방 한구석에서 조용히 울려 퍼진 통기타 선율",
        "아무에게도 털어놓지 못했던 그날 밤의 속마음을 여기에 털어놓습니다"
    ]
}

def generate_3tier_hashtags(niche_tags, category_tags, branded_tags, total=10):
    niche_count = max(1, int(total * 0.4))
    cat_count = max(1, int(total * 0.4))
    brand_count = total - niche_count - cat_count
    selected_niche = niche_tags[:niche_count]
    selected_cat = category_tags[:cat_count]
    selected_brand = branded_tags[:brand_count]
    combined = selected_niche + selected_cat + selected_brand
    return {
        "niche": selected_niche,
        "category": selected_cat,
        "branded": selected_brand,
        "formatted_text": " ".join([f"#{t.replace(' ', '')}" for t in combined])
    }


ROOT_DIR = r"C:\Users\sangi\Downloads\shin-agent"
OUT_DIR = os.path.join(ROOT_DIR, "studio_vault", "THREADS_FUNNEL_OUT")
os.makedirs(OUT_DIR, exist_ok=True)

THREADS_DATA = {
    "pack_name": "S1_7DAYS_THREADS_GLOBAL_PACK",
    "version": "2.0.0",
    "created_at": "2026-11-02T00:50:00+09:00",
    "architecture": "3-Tier Non-Viral High-Conversion Organic Funnel",
    "korean_series_hangeoreum": [
        {
            "day": 1,
            "target_track": "01. 막차 (Last Train)",
            "funnel_tier_1_hook": "오늘 하루도 참 치열하게 버텼습니다. 마지막 열차에 기대어 듣는 작은 숨소리 하나.\n\n(🎬 첨부: 01_SHORTS_HANGEOREUM_MAKCHA_1080x1920.mp4 영상 재생)",
            "funnel_tier_2_story": "밤 11시 40분, 승강장 불빛 아래 서 있는 사람들의 어깨는 모두 조금씩 내려앉아 있습니다. 성공이나 속도보다 중요한 건, 오늘 하루를 정직하게 살아낸 자신을 토닥여주는 일입니다. 상선약수(上善若水)의 물처럼, 조용히 마음을 적시는 멜로디를 남깁니다.",
            "funnel_tier_3_conversion": "🎧 한걸음씩 정규 1집 전곡(41분) 듣기 & 전 세계 음원 사이트 발매:\n유튜브 풀영상: https://www.youtube.com/@한걸음씩-r4i\n스포티파이/애플뮤직: DistroKid UPC 700563848544\n\n여러분의 오늘 하루는 어떠셨나요? 댓글로 짧은 안부를 나눠주세요 🍂"
        },
        {
            "day": 2,
            "target_track": "02. 창을 닫지 마 (Don't Close the Window)",
            "funnel_tier_1_hook": "바람이 차가워졌다고 마음의 문까지 닫아걸진 마세요.\n\n(🎬 첨부: 02_SHORTS_HANGEOREUM_DONT_CLOSE_WINDOW_1080x1920.mp4 영상 재생)",
            "funnel_tier_2_story": "서늘한 계절이 오면 우리는 상처받지 않으려 스스로를 고립시키곤 합니다. 하지만 창문을 조금만 열어두면, 여전히 세상엔 우리를 응원하는 다정한 온기가 흘러들어옵니다.",
            "funnel_tier_3_conversion": "따스한 온기가 필요한 분들을 위한 12곡의 이야기:\n🔗 유튜브 채널: @한걸음씩-r4i\n멜론/지니/스포티파이 공식 발매 중"
        },
        {
            "day": 3,
            "target_track": "03. 첫 입김 (First Breath in Cold Air)",
            "funnel_tier_1_hook": "입김이 하얗게 피어오르는 순간, 비로소 겨울이 왔음을 실감합니다.\n\n(🎬 첨부: 03_SHORTS_HANGEOREUM_FIRST_BREATH_1080x1920.mp4 영상 재생)",
            "funnel_tier_2_story": "어릴 적 손을 모아 불던 첫 입김의 순수함을 기억하시나요? 세월이 흘러도 변치 않는 소중한 것들은 언제나 우리 가장 가까운 곁에 있습니다.",
            "funnel_tier_3_conversion": "소박하지만 깊은 울림, 정규 1집 『가을과 겨울 사이』 전곡 감상하기:\n👉 프로필 링크에서 41분 풀영상과 고음질 스트리밍을 만나보세요."
        },
        {
            "day": 4,
            "target_track": "04. 오늘은 여기까지 (That's All for Today)",
            "funnel_tier_1_hook": "모든 짐을 혼자 짊어지려 하지 마세요. 오늘은 여기까지만 해도 충분합니다.\n\n(🎬 영상: 잔잔한 야경 쇼츠 클립)",
            "funnel_tier_2_story": "번아웃이 찾아오는 이유는 능력이 부족해서가 아니라, 너무 열심히 살아왔기 때문입니다. 내일의 태양은 내일 다시 떠오르니, 오늘 밤은 마음 놓고 푹 쉬세요.",
            "funnel_tier_3_conversion": "지친 마음에 건네는 쉼표:\n유튜브 풀앨범: https://www.youtube.com/@한걸음씩-r4i"
        },
        {
            "day": 5,
            "target_track": "05. 밥은 먹었니 (Have You Eaten)",
            "funnel_tier_1_hook": "세상에서 가장 평범하지만, 가장 위대한 사랑의 질문: '밥은 먹었니?'",
            "funnel_tier_2_story": "어머니가 건네시던 따뜻한 국 한 그릇. 바쁘다는 핑계로 끼니를 거르는 우리 모두에게 건네는 따뜻한 보살핌의 노래입니다.",
            "funnel_tier_3_conversion": "한걸음씩 정규 1집 수록곡 전곡 스트리밍 중입니다."
        },
        {
            "day": 6,
            "target_track": "06. 식어 가는 차 (Cooling Tea)",
            "funnel_tier_1_hook": "뜨거움이 지나간 자리에 비로소 찾아오는 은은하고 깊은 향기.",
            "funnel_tier_2_story": "열정적인 말보다 묵묵한 배려가 더 깊은 위로가 될 때가 있습니다. 식어도 맛있는 차처럼, 성숙해져 가는 인간관계의 미학.",
            "funnel_tier_3_conversion": "가을과 겨울 사이, 12편의 사색:\n프로필 링크 확인"
        },
        {
            "day": 7,
            "target_track": "12. 내일의 아침 (Tomorrow's Morning)",
            "funnel_tier_1_hook": "어두운 밤이 지나면 어김없이 눈부신 새날이 밝아옵니다.\n\n(🎬 12편 전곡 하이라이트 쇼츠)",
            "funnel_tier_2_story": "시련과 눈물은 지나가고, 우리는 다시 한 걸음씩 나아갈 수 있습니다. 상선약수 33% 나눔 약속과 함께 세상에 희망을 전합니다.",
            "funnel_tier_3_conversion": "한걸음씩 정규 1집 공식 앨범 발매 완료! 전 세계 24개 음원 사이트와 유튜브에서 만나보세요."
        }
    ],
    "global_series_sunone_aon": [
        {
            "day": 1,
            "target_track": "Beacon of Hope (SUN-ONE AON Theme)",
            "funnel_tier_1_hook": "When the world feels overwhelmingly fast, where do you find your stillness?\n\n(🎬 Attached: 04_SHORTS_USAON_BEACON_OF_HOPE_1080x1920.mp4)",
            "funnel_tier_2_story": "In Eastern philosophy, 'Water of Benevolence' (上善若水) flows to the lowest ground, nourishing all living beings without competition. Our anthem carries this exact vibration of quiet strength and clarity.",
            "funnel_tier_3_conversion": "🎧 Experience the full orchestral synthwave journey:\nOfficial YouTube MV: https://www.youtube.com/@SUN-ONEAON\nSpotify / Apple Music worldwide (ISRC: KR-S01-26-V601)\n\n33% of all streaming proceeds are pledged to universal education & global philanthropy."
        },
        {
            "day": 2,
            "target_track": "Ocean of Hope",
            "funnel_tier_1_hook": "A single drop of kindness can ripple into an entire ocean of transformation.",
            "funnel_tier_2_story": "We built SUN-ONE AON on a bedrock promise: technology and music must elevate human dignity. Listen to the sonic texture of modern cinematic soundscapes meeting ancient contemplative wisdom.",
            "funnel_tier_3_conversion": "Stream the master album on all major global streaming platforms."
        },
        {
            "day": 3,
            "target_track": "Official Theme Instrumental #1",
            "funnel_tier_1_hook": "Deep focus mode activated. Zero distractions, pure acoustic flow state.",
            "funnel_tier_2_story": "Crafted for creators, engineers, and thinkers working late into the night. Designed with precise audio geometry to enhance calm mental endurance.",
            "funnel_tier_3_conversion": "Full 1080p high-fidelity audio available on @SUN-ONEAON."
        },
        {
            "day": 4,
            "target_track": "Official Theme Instrumental #2",
            "funnel_tier_1_hook": "Warm analog synths meet cinematic morning energy.",
            "funnel_tier_2_story": "Start your day with purpose. No chaotic tempo, just steady golden frequency driving your next breakthrough.",
            "funnel_tier_3_conversion": "Subscribe to SUN-ONE AON on YouTube."
        },
        {
            "day": 5,
            "target_track": "Between Autumn and Winter (Global Edition)",
            "funnel_tier_1_hook": "12 stories of quiet resilience from Seoul to the world.",
            "funnel_tier_2_story": "The transition of seasons teaches us the art of letting go. Discover the warmth of Korean folk acoustic ballades.",
            "funnel_tier_3_conversion": "Listen on Spotify / Apple Music (UPC 700563848544)."
        },
        {
            "day": 6,
            "target_track": "Unsent Words",
            "funnel_tier_1_hook": "The loudest things we ever say are often in the silence we choose to keep.",
            "funnel_tier_2_story": "A gentle reflection on forgiveness, patience, and mindful presence in a noisy digital age.",
            "funnel_tier_3_conversion": "Full album stream now active."
        },
        {
            "day": 7,
            "target_track": "Universal Philanthropy Anthem",
            "funnel_tier_1_hook": "Music with a mission: 33% of everything we create goes back to those in need.",
            "funnel_tier_2_story": "True wealth is not what you keep, but what flows through you to help others rise. Join the movement.",
            "funnel_tier_3_conversion": "Join our official community: @SUN-ONEAON."
        }
    ]
}

def main():
    THREADS_DATA["viral_hooks_library"] = VIRAL_HOOKS_LIBRARY

    kr_niche = ["막차퇴근길", "위로의음악", "혼자만의시간", "마음의쉼표", "새벽감성글귀"]
    kr_cat = ["어쿠스틱포크", "한국인디음악", "감성플레이리스트", "힐링음악"]
    kr_brand = ["한걸음씩", "상선약수"]

    gl_niche = ["DeepFocusFlow", "CalmCodingVibe", "MindfulTech", "MidnightStudySession"]
    gl_cat = ["SynthwaveSoundscape", "CinematicFocus", "AmbientBeats", "FocusMusic"]
    gl_brand = ["SUNONEAON", "BeaconOfHope"]

    for item in THREADS_DATA["korean_series_hangeoreum"]:
        item["hashtags_3tier"] = generate_3tier_hashtags(kr_niche, kr_cat, kr_brand, total=10)
        item["viral_hook_options"] = {
            "curiosity_gap": VIRAL_HOOKS_LIBRARY["curiosity_gap"][(item["day"] - 1) % len(VIRAL_HOOKS_LIBRARY["curiosity_gap"])],
            "contrarian": VIRAL_HOOKS_LIBRARY["contrarian"][(item["day"] - 1) % len(VIRAL_HOOKS_LIBRARY["contrarian"])],
            "story_opening": VIRAL_HOOKS_LIBRARY["story_opening"][(item["day"] - 1) % len(VIRAL_HOOKS_LIBRARY["story_opening"])]
        }

    for item in THREADS_DATA["global_series_sunone_aon"]:
        item["hashtags_3tier"] = generate_3tier_hashtags(gl_niche, gl_cat, gl_brand, total=10)

    json_path = os.path.join(OUT_DIR, "S1_7DAYS_THREADS_GLOBAL_PACK.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(THREADS_DATA, f, ensure_ascii=False, indent=2)
    print(f"Saved Threads JSON -> {json_path}")

    md_lines = [
        "# 🧵 Threads & Instagram Non-Viral 7-Day Global High-Conversion Funnel Pack",
        "",
        "> **전략:** 26대 바이럴 훅 & 3단 해시태그(Niche 40% + Category 40% + Branded 20%) & 3단 고전환 퍼널(후킹 -> 스토리 -> 직결 링크)",
        "",
        "---",
        "",
        "## Part 1. 한국 본진 [@한걸음씩-r4i] 7일 감성 스레드 타래 원고",
        ""
    ]

    for item in THREADS_DATA["korean_series_hangeoreum"]:
        md_lines.append(f"### [Day {item['day']}] {item['target_track']}")
        md_lines.append(f"**[바이럴 훅 추천 A (Curiosity Gap)]** `{item['viral_hook_options']['curiosity_gap']}`")
        md_lines.append(f"**[바이럴 훅 추천 B (Contrarian)]** `{item['viral_hook_options']['contrarian']}`")
        md_lines.append(f"**[바이럴 훅 추천 C (Story Opening)]** `{item['viral_hook_options']['story_opening']}`\n")
        md_lines.append(f"**[1번째 타래 - 후킹 & 영상 지시]**\n```text\n{item['funnel_tier_1_hook']}\n```\n")
        md_lines.append(f"**[2번째 답글 - 감성 스토리 & 상선약수 철학]**\n```text\n{item['funnel_tier_2_story']}\n```\n")
        md_lines.append(f"**[3번째 답글 - 전환 링크 & CTA]**\n```text\n{item['funnel_tier_3_conversion']}\n```\n")
        md_lines.append(f"**[3단 최적화 해시태그 (40% Niche + 40% Category + 20% Branded)]**\n`{item['hashtags_3tier']['formatted_text']}`\n")
        md_lines.append("---")
        md_lines.append("")

    md_lines.append("## Part 2. 글로벌 [@SUN-ONEAON] 7-Day Deep Focus & Healing Threads Pack")
    md_lines.append("")

    for item in THREADS_DATA["global_series_sunone_aon"]:
        md_lines.append(f"### [Day {item['day']}] {item['target_track']}")
        md_lines.append(f"**[Post 1 - Scroll-Stopping Hook]**\n```text\n{item['funnel_tier_1_hook']}\n```\n")
        md_lines.append(f"**[Reply 2 - Core Philosophy & Depth]**\n```text\n{item['funnel_tier_2_story']}\n```\n")
        md_lines.append(f"**[Reply 3 - Conversion Link & 33% Pledge]**\n```text\n{item['funnel_tier_3_conversion']}\n```\n")
        md_lines.append(f"**[3-Tier Optimized Hashtags]**\n`{item['hashtags_3tier']['formatted_text']}`\n")
        md_lines.append("---")
        md_lines.append("")

    md_path = os.path.join(OUT_DIR, "S1_7DAYS_THREADS_GLOBAL_PACK.md")
    full_md = "\n".join(md_lines)
    h_th_md = s1_humanizer.humanize_text(full_md)["humanized_text"]
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(h_th_md)
    print(f"Saved Threads Markdown -> {md_path}")

if __name__ == "__main__":
    main()


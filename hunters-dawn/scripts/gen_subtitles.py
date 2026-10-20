import os

SRT_ENTRIES = [
    (1, "00:00:00,000", "00:00:16,724", "(휘파람 인트로 / Whistling Intro)\n[바깥세상이 그를 부르는 소리 / Calling from outside]"),
    (2, "00:00:16,724", "00:00:25,000", "어두운 방 안, 멈춰버린 시간\nIn a dim grey room, time has stopped"),
    (3, "00:00:25,000", "00:00:35,000", "창틈으로 흘러든 작은 빛 줄기 하나\nA thin blade of light drifts through the gap"),
    (4, "00:00:35,000", "00:00:45,991", "오래된 기타 위에 살포시 내려앉은 홀씨\nA dandelion seed settles on the dusty guitar"),
    (5, "00:00:45,991", "00:00:54,000", "하지만 난 나의 칼을 뽑아든다 (어쿠스틱 기타를 잡는다)\nBut I draw my sword"),
    (6, "00:00:54,000", "00:01:02,712", "커튼을 젖히자 몰아치는 봄날의 햇살\nSweep open the curtains, sunshine floods in"),
    (7, "00:01:02,712", "00:01:15,000", "사슬을 끊어내고 문밖으로 발을 내딛는다\nBreak the chains and step into the light"),
    (8, "00:01:15,000", "00:01:25,000", "일어나라, 사냥꾼이여! 눈부신 초원 속으로\nRise up, Hunter! Into the sunlit meadow"),
    (9, "00:01:25,000", "00:01:36,000", "슬픔을 추격하며 바람 속을 뛰어오른다\nHunting down the sorrow in the wind"),
    (10, "00:01:36,000", "00:01:46,000", "오직 너만이 이 봄의 주인공이다\nYou are the one"),
    (11, "00:01:46,000", "00:01:56,000", "자전거를 타고 달리는 리드미컬한 시골길\nRiding the old bicycle down the sunny path"),
    (12, "00:01:56,000", "00:02:05,000", "마을 사람들과 나누는 따뜻한 미소\nExchanging warmth with people on the street"),
    (13, "00:02:05,000", "00:02:15,000", "개울물을 차오르며 튀어 오르는 영롱한 빗방울\nSplashing through the stream, droplets scattering"),
    (14, "00:02:15,000", "00:02:25,432", "영혼의 갑옷을 입고 빛을 향해 걷는다\nArmor for your soul, walking into the light"),
    (15, "00:02:25,432", "00:02:35,000", "바람이 불어오는 커다란 벚꽃나무 아래\nUnder the huge blossoming tree"),
    (16, "00:02:35,000", "00:02:45,000", "가슴속에서 반짝이는 다이아몬드를 믿어라\nTrust the diamond in your chest"),
    (17, "00:02:45,000", "00:02:55,511", "눈을 뜨면 마주하는 확신에 찬 평온함\nOpening eyes with calm certainty"),
    (18, "00:02:55,511", "00:03:05,000", "이제 우리는 함께 이 길을 걸어간다\nNow we walk this golden path together"),
    (19, "00:03:05,000", "00:03:15,000", "모두가 어우러져 들려주는 희망의 리듬\nClapping in rhythm, singing under the sky"),
    (20, "00:03:15,000", "00:03:25,000", "사냥꾼의 새벽이 밝아오고 있다\nThe Dawn of the Hunter has arrived"),
    (21, "00:03:25,000", "00:03:30,000", "하늘 높이 휘파람을 불며 응답한다\nWhistling back into the golden sky"),
    (22, "00:03:30,000", "00:03:35,480", "(자유롭게 날아오르는 갈색 새와 민들레 홀씨)\n[The bird and dandelion seed released into light]")
]

def make_srt():
    os.makedirs("04_export", exist_ok=True)
    srt_path = "04_export/subs.srt"
    
    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, start_t, end_t, text in SRT_ENTRIES:
            f.write(f"{idx}\n{start_t} --> {end_t}\n{text}\n\n")

    print(f"Generated {srt_path} with {len(SRT_ENTRIES)} subtitle blocks.")

if __name__ == '__main__':
    make_srt()

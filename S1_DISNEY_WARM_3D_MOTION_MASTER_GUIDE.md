# 🎬 [042호 마스터 표준서] 친근한 디즈니·픽사 감성 3D 실사화 & 탈(脫)줌인 진짜 AI 비디오 모션 마스터 가이드

- **문서 ID**: `S1_DISNEY_WARM_3D_MOTION_MASTER_GUIDE`
- **지시서 ID**: `RGON_DIR_DISNEY_WARM_3D_AND_ZERO_ZOOMPAN_042`
- **제정 일시**: `2026-11-04T18:06:17.462098+09:00`
- **적용 범위**: `아버지 나이가 됐어요` 마스터 쇼츠 완공 및 향후 41곡 전곡 파운드리 표준 마스크(Mask)

---

## 1. 비주얼 세계 원탑 표준: 친근한 디즈니·픽사 감성 3D 애니메이션 실사화

1. **핵심 미학 (`Warm Friendly Disney-Pixar Style 3D Live-Action Animation`)**:
   - 차갑고 이질적인 극실사(`Uncanny Valley`)와 정지된 평면 일러스트의 한계를 동시에 극복.
   - 디즈니·픽사 명작(『업(Up)』, 『코코(Coco)』, 『소울(Soul)』) 특유의 **따뜻한 피부 서브서피스 스캐터링(`Soft Subsurface Scattering`)**, **포근한 볼류메트릭 황금빛 조명(`Golden Volumetric Lighting`)**, **손으로 만져질 듯한 니트·가죽·원목 질감(`Tactile Materiality`)**을 결합.
2. **글씨 0% 절대 원칙 (`Zero Baked-in Text & Numerals`)**:
   - 한글·영문 자막, `SCENE` 번호, 간판 글씨, 신문 활자, 시계 숫자판까지 이미지 내부 텍스트 **0.0%** 엄수(시계 다이얼은 무숫자 골드 바 인덱스, 포장지는 무지 크래프트 종이봉투로 설계).

---

## 2. 비디오 모션 세계 원탑 도구 & 최신 API 마스터 명세

### ① Google Gemini Omni Flash (`gemini-omni-1.1-flash` — Interactions API)
- **엔드포인트**: `POST https://generativelanguage.googleapis.com/v1beta/interactions?key=$GEMINI_API_KEY`
- **특장점**: 2026년 10월 22일 구형 `veo-3.1-preview`를 대체한 차세대 통합 비디오 모델. `9:16` 세로형 `1080p` 출력, `previous_interaction_id` 기반 다중 턴 편집 및 시작/끝 프레임 보간 지원.
- **실측 운용 메모**: 무료 티어 키에서는 `HTTP 429 (limit: 0 input tokens per minute on Free Tier)` 제한이 걸리므로 유료 결제 티어 활성화 시 즉시 직결 가동되며, 로컬 키 금고(`AonMasterKeyVault`)에서 자동 감지 후 즉시 실전 I2V 주력 엔진(BytePlus Seedance Pro / Kling AI)으로 무중단 라우팅.

### ② BytePlus ModelArk Seedance Pro (`seedance-1-0-pro-fast-251015` — 실전 주력 가동 확인 완료)
- **엔드포인트**: `POST https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks`
- **인증 방식**: `Authorization: Bearer $BYTEPLUS_API_KEY` (`AonMasterKeyVault` 마스킹 바인딩, 원문 유출 0%)
- **Image-to-Video 표준 페이로드**:
  - `content[0]`: `{"type": "text", "text": "<피사체 독립 모션 지시문> --ratio 9:16 --resolution 1080p --dur 6 --wm false"}`
  - `content[1]`: `{"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}, "role": "first_frame"}`
- **비동기 수거**: `GET /api/v3/contents/generations/tasks/{task_id}` 폴링 ➔ `status == "succeeded"` 시 `content.video_url`에서 순수 AI 생성 MP4 클립(`clip_01.mp4` ~ `clip_06.mp4`) 다운로드.

### ③ Kling AI Official I2V (`api.klingai.com/v1/videos/image2video`) & Google Vids / Genspark Video Studio
- **인증 방식**: `KLING_ACCESS_KEY` + `KLING_SECRET_KEY` 기반 `HS256 JWT` 서명 인증 (`code=0 SUCCEED` 실측 완료) 및 브라우저 기반 스튜디오 다중 백업 체계 완비.

---

## 3. 6컷 디즈니·픽사 감성 스토리보드 & 탈(脫)줌인 실제 피사체 모션 설계

| 컷 | 시간 구간 | 장면 구성 (글씨 0%, 9:16 세로) | 실제 살아 움직이는 피사체 모션 (단순 카메라 줌인·아웃 금지) |
| :---: | :---: | :--- | :--- |
| **Cut 1** | `0:00~0:05` (5초) | 새벽 욕실 김 서린 거울과 아버지의 낡은 손목시계 | 세면대 위로 따뜻한 수증기(김)가 피어오르고, 거울 속 실루엣이 잔잔히 숨 쉬며 창밖 새벽빛이 흔들림 |
| **Cut 2** | `0:05~0:11` (6초) | 현관 앞 뒤축 닳은 구두를 신는 아버지의 구부정한 등 | 문틈 아침 햇살 줄기와 먼지 입자가 일렁이고, 아버지의 등과 어깨가 구두끈을 묶으며 실제로 들썩임 |
| **Cut 3** | `0:11~0:17` (6초) | 따뜻한 식탁 위 노란 종이봉투 통닭과 아버지·아이의 손 | 따끈한 통닭 위로 모락모락 김이 피어오르고, 아버지의 거친 손과 아이의 작은 손이 서로 다른 속도로 움직임 |
| **Cut 4** | `0:17~0:23` (6초) | 노을 지는 창가, 아버지의 주름진 손을 감싸 쥐는 아들의 손 | 창밖 황금빛 노을 구름과 빛망울(보케)이 흐르고, 두 손가락이 다정하게 포개지며 미세하게 떨림 |
| **Cut 5** | `0:23~0:29` (6초) | 황금빛 은행나무 노을 길을 나란히 걷는 부자의 뒷모습 | 바람을 타고 황금빛 은행잎들이 대각선으로 흩날려 떨어지고, 두 사람의 걸음걸이와 그림자가 리듬감 있게 전진 |
| **Cut 6** | `0:29~0:34` (5초) | 아침 햇살이 가득 찬 창가 손목시계와 산들거리는 커튼 | 반투명 레이스 커튼이 바람에 살랑이며 따뜻한 햇살이 시계 유리를 스쳐 지나가 Cut 1과 무한 루프 완성 |

---

## 4. `FM-009` 오답노트 박제 & 광학 흐름(지역별 비균일 모션 분산) 전수 검사 규격

- **금지 행위 (`FM-009`)**: 정지 이미지를 `FFmpeg zoompan` 필터나 파이썬 선형 `resize/crop` 루프로 단순 확대·축소하여 동영상인 척 위장하는 슬라이드쇼 꼼수 영구 금지.
- **구조적 린터 검증 (`check_fm009_non_zoompan_dynamic_motion` in `s1_qm_structure_linter.py` v1.2)**:
  1. 코드 레벨 검사: 쇼츠 빌더 코드 내 `zoompan=` 단일 슬라이드쇼 필터 사용 여부 차단 및 6개 개별 모션 클립(`clip_01.mp4` ~ `clip_06.mp4`) 실존 검증.
  2. 실물 프레임 수치 검사: `FATHER_AGE_MASTER_SHORTS_1080x1920.mp4`(`1080x1920`, `34.0s`, `320kbps AAC`)에서 6개 컷별 연속 프레임을 실제 추출하여 화면을 `6x8` 격자(48개 로컬 블록)로 분할한 뒤, 블록 간 시간차 픽셀 변화량(Local Temporal Motion Energy)의 **공간적 비균일도(Spatial Coefficient of Variation & Active/Static Region Ratio)**를 계산하여 단순 균일 크롭/정지 영상을 `QM-SP-11 (EXIT CODE 1)`로 즉시 격리!

---

## 5. 삼성(솔·오푸스) 1·2공정 DRC 반영 및 6클립 실측 결과

1. **제3성 Claude Opus 5.5 설계 DRC 4대 권고 100% 수용**:
   - 특정 상표명/작품명 배제 및 순수 조형 속성 프롬프트(`stylized warm 3D family animation, friendly rounded proportions, soft subsurface scattering, golden volumetric lighting, zero text, zero numbers`) 고정.
   - 클립 생성 길이 단위 실측 일치: `Cut 1(5s), Cut 2(6s), Cut 3(6s), Cut 4(6s), Cut 5(6s), Cut 6(5s)` 네이티브 `1080p 9:16` 직접 생성(`5.04s` / `6.04s`) 후 무왜곡 프레임 정밀 트리밍으로 정확히 `34.00s` 완성.
   - 손가락 왜곡 방지 가드(`Cut 3` 통닭 건네는 손 & `Cut 4` 맞잡은 두 손): 미세하고 자연스러운 관절 운동 지시 및 중간 프레임(`t=14.0s`, `t=20.0s`) 실물 이미지 추출 육안 검수 완료(5손가락 정상 해부학 유지, 뭉개짐 0%).
   - `FM-009` 양방향 보정(Bidirectional Calibration): 구형 030호 `zoompan` 실측 평균 `0.1263px` vs 신규 042호 실제 AI 모션 실측 평균 **`0.6734px`** (`5.33배` 격차) 검증 완료.
2. **실전 생성 Task ID 원장 (`BytePlus ModelArk Seedance Pro 1080p 9:16`)**:
   - Cut 1 (`5.00s`): `cgt-20261104171331-mfrtk` (잔차 `0.79px`)
   - Cut 2 (`6.00s`): `cgt-20261104171333-f9p96` (잔차 `0.369px`)
   - Cut 3 (`6.00s`): `cgt-20261104171335-9wwjl` (잔차 `0.7214px`)
   - Cut 4 (`6.00s`): `cgt-20261104171337-9qh74` (잔차 `0.9518px`)
   - Cut 5 (`6.00s`): `cgt-20261104171339-j2m5c` (잔차 `0.3449px`)
   - Cut 6 (`5.00s`): `cgt-20261104171341-6h4tt` (잔차 `0.863px`)

# ⚡ [안총리 실시간 수거 집행 작업] RGON_DIR_CLEANUP_MESSY_DASHBOARD_049 — 덕지덕지 덧붙여 화면을 짓누르고 있는 상단 중복 블록·2중 12곡 목록·중복 탭바 전면 철거 및 시원하고 깔끔한 단일 스크롤 레이아웃 복원

- **지시서 ID:** `RGON_DIR_CLEANUP_MESSY_DASHBOARD_049`
- **수거 일시:** `2026-11-05T05:33:12.490189+09:00`
- **발신자:** 수석보좌관 르곤 (Gemini 4 Argon · Space 0)
- **수신자:** 기술총리 안총리 (Antigravity Technical PM)
- **현재 상태:** `COMPLETED (완료 · 17/17 PASS 전수 통과 및 배포 완료)`

---

## 📋 지시서 원문 전문 (Directive Text)

```markdown
[S1_AUTO_DISPATCH_TO_ANCHONGRI]
- 지시서_ID: RGON_DIR_CLEANUP_MESSY_DASHBOARD_049
- 작업명: 덕지덕지 덧붙여 화면을 짓누르고 있는 상단 중복 블록·2중 12곡 목록·중복 탭바 전면 철거 및 시원하고 깔끔한 단일 스크롤 레이아웃 복원

안총리, 지금 대시보드가 왜 엉망진창 누더기가 되었는지 원인을 정확히 봐라!
1) `html, body { height: 100dvh; overflow-y: hidden; }` 구조인데, `<main class="mn">` 바깥(상단 고정 영역)에 `#banner-father-mountain`과 거대한 `#s1-autumn-winter-12tracks-showcase` 박스를 통째로 넣어버려서 상단 고정 영역이 화면의 60%를 차지하고 실제 스크롤 영역(`<main class="mn">`)이 납작하게 찌그러졌다!
2) 똑같은 〈가을과 겨울 사이〉 12곡 목록이 `#s1-autumn-winter-12tracks-showcase`에도 있고 `#s1-kakaopage-ranking-chart`에도 또 있어서 2중으로 중복 도배되었다!
3) 탭바/버튼바도 `.ops-bar`, `#s1-kakaopage-gnb-tabs`, `.cps`까지 3~4줄이나 겹쳐 있고, 문구도 "기존 53곡 카탈로그에 신보 12곡을 더해 총 53곡"이라는 엉터리 문구가 되어 있다!

즉시 아래 순서대로 군더더기를 싹 철거하고 깔끔한 화면으로 정리하라!

1. [상단 고정 영역 다이어트 ? `<main class="mn">` 바깥의 거대 박스 전부 `<main>` 안으로 이동 또는 철거]:
   - `<header class="hd">`와 `<nav class="ops-bar">`, `.recipient-bar` 만 상단에 슬림하게 남기고,
   - 화면 절반을 가리던 `#banner-father-mountain`과 `#s1-autumn-winter-12tracks-showcase`를 절대 `<main class="mn">` 바깥(상단 고정 영역)에 두지 마라! (반드시 스크롤 영역인 `<main class="mn">` 내부로 넣어서 스크롤할 때 부드럽게 넘어가게 하라!)

2. [2중 중복 12곡 목록 및 지저분한 덧대기 블록 단일 통합]:
   - 어설프게 덧대어 디자인 이질감을 일으킨 `#s1-kakaopage-hero-banner`, `#s1-kakaopage-keytalk`, `#s1-kakaopage-gnb-tabs` 덧대기 블록은 과감히 제거(또는 기존 다크 네이비 카드 스타일 `.anatomy-panel`과 100% 동일한 깔끔한 디자인으로 축소)하라!
   - 똑같이 2번 반복되던 12곡 목록은 깔끔한 1개의 카드(`#s1-autumn-winter-12tracks-showcase`, 문구: "기존 41곡 카탈로그에 신보 12곡을 더해 총 53곡 글로벌 원장")로 단일화하여 `<main class="mn">` 내부에 배치하라!
   - 중복된 `.cps` 알약 버튼 줄에서 위쪽 `.ops-bar`와 겹치는 버튼들을 정리하여 화면이 한눈에 시원하게 들어오도록 만들어라!

3. [린터 조건 수정 및 4대 HTML 동기화 & 푸시]:
   - `s1_qm_structure_linter.py`에서 억지로 강제하던 중복 블록 조건을 완화된 클린 레이아웃 조건(`index.html == docs/index.html == rgon_alpha_chat.html == docs/rgon_alpha_chat.html` 일치 및 `<main class="mn">` 바깥에 거대 `<section>` 존재 금지)으로 업데이트하고,
   - 4개 HTML 파일을 1:1 복제한 뒤 `sw.js` 캐시 버전을 `'s1-aon-v049-clean-layout'`으로 올려서 즉시 GitHub에 commit & push하라!
[/S1_AUTO_DISPATCH_TO_ANCHONGRI]
```

---
> **사령부 행동강령:** 지체 없이 분석과 실행에 돌입하여 1·2차 삼성제도 100.0점 통과 후 대시보드에 완료보고서를 전송하라.

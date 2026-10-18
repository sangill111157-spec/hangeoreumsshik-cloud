# 🎨 Stitch 2.0 Enterprise Design Manual & Vibe System

> **작성 주관**: [CN-403] 디자이너 (Connect AI Cloud Corps)  
> **표준 규격**: Stitch 2.0 Enterprise UX/UI & MCP Compatible Schema  
> **호환성**: Google Antigravity, Next.js, Vanilla CSS Glassmorphism

---

## 1. 🌈 Design Tokens (Design Vibe Matrix)

```json
{
  "colors": {
    "primary": "#4f46e5",
    "primary_glow": "rgba(79, 70, 229, 0.4)",
    "secondary": "#06b6d4",
    "accent": "#ec4899",
    "background_dark": "#0a0f1d",
    "card_glass": "rgba(18, 24, 38, 0.75)",
    "border_subtle": "rgba(255, 255, 255, 0.08)",
    "text_main": "#f8fafc",
    "text_muted": "#94a3b8"
  },
  "typography": {
    "font_family": "'Pretendard', 'Inter', -apple-system, sans-serif",
    "scale": {
      "h1": "2rem",
      "h2": "1.5rem",
      "h3": "1.15rem",
      "body": "0.95rem",
      "caption": "0.75rem"
    }
  },
  "radius": {
    "sm": "6px",
    "md": "12px",
    "lg": "16px",
    "full": "9999px"
  }
}
```

---

## 2. 📱 4대 필수 스크린(Core Screens) 명세

### 1) Main Hero Screen (`screen_hero_01`)
- **목적**: 3초 이내에 사용자 시선을 사로잡는 몰입형 헤더 및 원터치 론칭 영역.
- **컴포넌트**:
  - 네온 엠비언트 백그라운드 & 실시간 터널 상태 뱃지.
  - 원클릭 퀵 액션 그리드: 트렌드 저격, AI 음악 프로듀싱, 꿈의 옷장 스튜디오 직행.

### 2) Detail Screen (`screen_detail_02`)
- **목적**: 개별 프로젝트/영상/코디의 정밀 픽셀 및 파라미터 조작.
- **컴포넌트**:
  - 캔버스 뷰어 (Before/After 2분할 비교 모드 탑재).
  - 마술봉 픽셀 검출 인디케이터 & 실시간 슬라이더 컨트롤.

### 3) Library Screen (`screen_library_03`)
- **목적**: 생성된 음원, 대본, 렌더링된 MP4 비디오 및 지식 위키의 아카이브.
- **컴포넌트**:
  - 카드형 무한 그리드, 태그 필터링(노박/한걸음씩/BOOSTER), 원클릭 다운로드 & 클라우드 동기화.

### 4) Payment Screen (`screen_payment_04`) - 글로벌 & 국내 결제 듀얼 현지화
- **목적**: 1인 AI 기업의 무인 수익화를 위한 결제 게이트웨이.
- **지원 게이트웨이**:
  - 🌍 **PayPal Checkout SDK**: 글로벌 구독 및 달러 결제 지원 (`USD`).
  - 🇰🇷 **토스페이먼츠 (Toss Payments API)**: 간편결제(토스, 카카오페이, 네이버페이) 및 국내 카드 즉시 결제 (`KRW`).

---

## 3. 🛠️ Stitch 2.0 MCP 도구 호환 스키마

```json
{
  "mcp_tools": [
    {
      "name": "stitch_list_projects",
      "description": "Stitch 2.0 프로젝트 목록 및 현재 활성화된 화면 명세를 반환합니다.",
      "parameters": {
        "type": "object",
        "properties": {
          "status": {"type": "string", "enum": ["active", "archived", "all"]}
        }
      }
    },
    {
      "name": "stitch_get_screen",
      "description": "지정된 스크린 ID의 상세 컴포넌트 트리와 스타일 명세를 조회합니다.",
      "parameters": {
        "type": "object",
        "properties": {
          "screen_id": {"type": "string"}
        },
        "required": ["screen_id"]
      }
    }
  ]
}
```

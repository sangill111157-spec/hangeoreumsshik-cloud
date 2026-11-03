# ⚡ S1 AGENT-DESKTOP UNIVERSAL MASTER GUIDE (v1.1.0)
**발행일:** 2026-11-04 (033호 대표님 어명 집행)  
**주체:** 기술총리 안총리 & 만능 참모 아온이 (AON)  
**결재:** Gemini 4 Argon 수석보좌관 르곤 & 이상일 대표님  
**도장:** `STAMP_0_AGENT_DESKTOP_MASTERY`  

---

## 1. 개요 및 설치 검증
- **패키지:** `agent-desktop` (v1.1.0, protocol v2.6)
- **실행 환경:** Windows 11 x86_64, winsta0\default interactive desktop
- **권한 상태:**
  * Accessibility: `granted`
  * Automation: `not_required`
  * Screen Recording: `not_required`
- **지원 서피스(Surfaces):**
  `window`, `focused`, `sheet`, `menu`, `start-menu`, `taskbar`, `system-tray`, `system-tray-overflow`, `action-center`

---

## 2. 4대 핵심 CLI 명령어 체계

### 1) 데스크톱 UI 트리 캡처 (Snapshot)
```powershell
# 데스크톱/앱 전체 얕은 맵 캡처 (컴팩트 스켈레톤)
agent-desktop snapshot --skeleton -i --compact

# 특정 앱(예: Antigravity, Chrome) 지정 캡처
agent-desktop snapshot --app "Chrome" -i --compact

# 특정 UI 서브트리 드릴다운
agent-desktop snapshot --root '@s8f3k2p9:e3' -i --compact
```

### 2) 무마우스 시맨틱 상호작용 (Semantic API)
```powershell
# 고유 ref를 통한 클릭
agent-desktop click '@s8f3k2p9:e12'

# 텍스트 입력 및 단축키
agent-desktop type '@s8f3k2p9:e15' "검색어"
agent-desktop keypress "ctrl+b"
```

### 3) 윈도우 관리 및 레이아웃 제어 (Window Operations)
```powershell
# 실행 중인 윈도우 목록 조회
agent-desktop list-windows

# 윈도우 활성화 및 포커스
agent-desktop focus-window <window_id>

# 윈도우 크기/위치 재배치
agent-desktop move-window <window_id> --x 0 --y 0 --width 768 --height 432
```

---

## 3. 033호 4대 결함 교정 적용 전략
1. **결함 ① (가짜 tkinter 즉각 폐기 & 진짜 Ego-Lite 본체 기상):**
   - 가짜 파이썬 tkinter 데몬 즉시 영구 종료 및 파일 삭제.
   - 실제 Ego-Lite 본체 창 또는 에고라이트 라이브 대시보드를 (0, 432, 1536, 432)에 꽉 채움.
2. **결함 ② (좌상 Chrome Space 0 75% 줌 & 최신 메시지 스크롤):**
   - Chrome Space 0 창에 75% 줌 및 스크롤 끝까지 내려 최신 033호 대화 완전 노출.
3. **결함 ③ (우상 Antigravity IDE Explorer 접기):**
   - `Ctrl+B`를 통해 좌측 파일 트리 사이드바를 접고 안총리 대화창 100% 전면 노출.
4. **결함 ④ (임시 파일 청소):**
   - 91개 임시 스크립트 정리.

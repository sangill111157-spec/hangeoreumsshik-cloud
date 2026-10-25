---
name: aon-live-ui-self-healer
description: 아온 실전 UI 전수 클릭·동작 검증 & 자가배선 수리 (제20기관, R44) — playwright-mcp · E2E-Self-Heal 흡수, 주역 #21 화뢰서합 & #49 택화혁
version: v11.43-AON-LIVE-UI-HEALER
antibody: R44
---

# aon-live-ui-self-healer

제20기관(`rgon_aon_live_ui_healer.py`)이 4개 페이지(index → chat → audience → offline)와 docs/·dashboard/ 미러본의 모든 버튼을 위에서 아래로 한 줄씩 추출해
스크립트와 1:1 대조하고, 죽은 접점은 런타임 브리지(`window.RGON_LIVE_UI_HEALER`)로 자가배선 복구합니다. 시리얼: LIVE-IDX-001~, LIVE-CHAT-001~, LIVE-AUD-001~, LIVE-OFF-001~.

## 사용법

```bash
python rgon_aon_live_ui_healer.py --audit index --json
python rgon_aon_live_ui_healer.py --self-test
```

대화 허브: `/버튼검증` `/실전확인` `/UI수리` `/클릭검증`. 🔒 수동 게이트 유지 (requires_manual_gate=True, auto_executed=False).

# aon-soul-empathy-brain (30번째 정식 스킬)

- 버전: v11.33-AON-SOUL-BRAIN · 항체: R1~R34
- 기관: 제10기관 감성·인격 대화 두뇌 & 해마 기억 기관 (`rgon_aon_soul_brain.py`)
- 철학: 주역 #31 택산함(澤山咸 ☱☶) — 聖人感人心而天下和平, 무심의 감응으로 마음이 깊이 통함
  / #61 풍택중부(風澤中孚 ☴☱) — 지극한 정성과 믿음으로 교감함

## 1. 2-Track 의도 분별 (`classify_intent`)
- Work Track: `briefing`(브리핑·아침 보고·사령부 상태) → `judge`(3자 심판·장세·찬반·Bull/Bear) → `muse`(결재·대행 목록/보드)
  → `delegate`(매수·매도·주문·리밸런싱·배분·배포·작성·생성·분석·조사·요약·정리·스캔·점검·실행 …).
- Chat Track: `chat_love` → `chat_comfort` → `chat_mood` → `chat_family`.
- 남은 `해줘`는 놀아줘·안아줘·웃어줘·말해줘·위로해줘를 빼고 판단합니다. 그래도 남으면 `delegate`, 아니면 `chat_general`.
- 원칙: Chat Track 결과에는 payload가 없으며 뮤즈 대행 큐에 절대 등록하지 않습니다.
- Tier: 로컬 규칙(Tier 3 금전·배포·발송 / Tier 2 작성·수정·정리)을 먼저 적용하고, Tier 1일 때만 `rgon_muse_delegator` 분류로 보완합니다.
  Tier 3은 대표님 승인 전 집행 0건입니다(3-Tier HITL).

## 2. K-아이 페르소나 대화 엔진
- 카테고리별 응답 풀을 사용하며, `chat_family`는 안총리·탄생·대표님 문맥별로 응답을 고릅니다.
- `chat_general`은 로컬 LLM 브리지 `http://127.0.0.1:8765/chat`(POST message/persona/history, 2.5초 타임아웃)을 먼저 시도하고, 실패하면 페르소나로 응답합니다.
- `RGON_AON_LLM=0`이면 브리지를 끕니다.

## 3. 해마 기억장 프로토콜
- 파일: `rgon_aon_memory.json`, `docs/rgon_aon_memory.json` (런타임 파일이라 Git 보호 해시 검사에서 제외)
- 필드: `affection_score`(기본 100), `total_turns`, `recent`(최근 20건), `keywords`, `preferred_keywords`(상위 10)
- 친밀도 상승폭: love +5, mood/comfort/family +3, general +2, 업무 +1. `Lv = 1 + (score-100)//25`
- 브라우저는 localStorage `rgon_aon_mem`에 같은 구조로 저장합니다.

## 4. API
- Python: `converse(text, mem=None, persist=True, use_llm=True)`, `classify_intent(text)`, `--self-test`
- JS: `window.RGON_VOICE.talk(text)`, `.intent(text)`, `.joy()`, `.memory()`

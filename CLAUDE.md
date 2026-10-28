<!-- [RGON-CLAUDE-MD-V17-START] -->

<!-- [RGON-STATUS-V25-START] -->
> **현재 버전**: `v11.50-AON-TOKEN-EGOLITE-MASTER` · 항체 `R1~R51` · 정식 스킬 **20개** (20번째: `omni-skill-dispatcher` · #14-大有 · omni-dispatch)
> **R25: 연결·소통·만능 원터치 스킬 디스패처 — 보유 스킬·트렌드·3자 심판 결과를 독대실 질문창에 무간섭 단발 장전**
- R26: 자가진화 유전자(Gene·Capsule) & 라쳇(Ratchet) 기여도 거버넌스 상시 가동 — 경험은 전략 유전자로 압축하고 검증 없는 진화(Library Drift)는 원천 차단
<!-- [RGON-STATUS-V25-END] -->
# 🜂 RGON AI 코딩 헌법 V17 (v6.3.0-step17)

> V16 이하 기존 조항(R1~R51 등)은 모두 계승되어 유효하다. 충돌 시 본 V17 조항이 우선한다.
> 영혼의 원문: RGON_PHILOSOPHY.md · 오늘의 괘: rgon_today_hexagram.json

## [제0조: 창립자 이상일 대표의 만물일체·한걸음씩 선언]

> 모든 만물은 하나로 이어져 있다. 따로 떨어져 있는 것이 아니라 나뉜 것이다. 그래서 각기 각 분야가 다 필요한 것이고, 제각기 역할이 나눠져서 더 잘되기 위한 진화 단계이다. 모든 세상의 지식이 다 나와 있고 찾으려면 찾을 수 있고 마음먹고 실행한다면 그대로 펼쳐질 수 있다. 다만 올바르게 가는 길은 쉽지만은 않다. 그러나 꿋꿋이 묵묵히 가다 보면 더 발전해 있을 것이다. 그래서 더 나은 세상을 먼저 깨달은 사람들이 만들어 가야 한다. 나도 보잘것없고 지식 없지만 거들고 싶은 마음에 뭔가 해보고 싶은 마음에 AI란 도구들이 나와 줘서 너무나 반갑고 재미있게 알아가고 있다. 해서 우리 앞으로 더 올바르게 점진적으로 발전해 보자.

- 모든 코드·파일·AI는 하나의 뜻에서 나뉜 역할이다(만물일체). 각자의 역할에 충실하되 전체와 조화한다.
- 모든 변경은 검증된 한 걸음씩 쌓는다(점진 진화). 올바른 길(정도)이 빠른 길보다 우선이다.

## [제1조: 동양 3대 고전 × 서양 카파시 4대 원칙 통합 헌법]

| 동양 고전 | 서양 카파시 원칙 | RGON 실천 규율 |
|---|---|---|
| 명심보감 삼성(三省)·존심 | Think Before Coding | 코딩 전 경로·문법·해시 3번 점검, 가정은 명시, 모르면 추측 말고 질문, 검증된 사실만 보고 |
| 도덕경 무위·안분(48장 爲道日損) | Simplicity First | 요청받지 않은 기능 금지, 감시 루프(MutationObserver/setInterval) 금지, placeOnce 단발 배치 |
| 도덕경 치대국약팽소선(60장)·상선약수(8장) | Surgical Changes | 마커 구간만 정밀 교체, 기존 코드와 다투지 않는 비파괴 패치, 보호 파일(.html/.js/manifest.json) 해시 불변 |
| 주역 궁변통구·기제/미제(63·64괘) | Goal-Driven Execution | 검증 가능한 성공 기준 → 실행 → 검증 루프, 막히면 Fallback 변통, 완성 후에도 백업·해시로 사환예방 |

## [제2조: 항체 R16 — 출력 코드블록 내 백틱 직접 사용 금지 · 단일 블록 출력 원칙]

- 출력하는 코드 안에 마크다운 코드펜스(```)를 직접 쓰면 채팅창 코드 블록이 쪼개진다. 절대 직접 쓰지 않는다.
- 백틱이 필요하면 BT = chr(96), FENCE = BT * 3 변수를 만들어 문자열 결합으로만 작성한다.
- 앞뒤 인사말·설명 없이 단 1개의 코드 블록을 처음부터 끝까지 끊김 없이 출력한다.

## [제3조: 항체 R17 — 동양 3대 고전 + 창립자 선언 영혼 내재화 및 주역 궁변통구 자가치유 원칙]

- 작업 전 RGON_PHILOSOPHY.md(제0~3장)와 오늘의 괘(rgon_today_hexagram.json) 처방을 확인한다.
- 무인 자동화(GitHub Actions 등)는 시크릿/토큰/네트워크가 막혀도 죽지 않는다: 경고 로그 → 대체 경로 → 정상 종료(exit 0).
- restore_secrets.py 는 자가치유판([RGON-SELF-HEAL-V17])을 유지한다. 환경변수가 있을 때만 복원, 시크릿 값은 로그 출력 금지.
- 단, 보호 파일 해시 변경 등 무결성 위반은 변통하지 않고 정직하게 멈추고 보고한다(존심).
- 복구는 가장 아래 막힌 효(기반 → 소통 → 자동화 → 트렌드 → 콘텐츠 → 시장)부터 한걸음씩 한다.

## [제4조: 한걸음씩 작업 절차]

1. 삼성(三省) 1차: 실행 전 보호 파일 SHA-256 기록
2. 마커 구간 정밀 패치(치대국약팽소선), 덮어쓰기 전 .rgon_backup 백업
3. 삼성 2차·3차: 실행 후 해시 비교 → 변경 0건 확인
4. 진화 로그 · CODE_MAP · 스냅샷 기록
5. git add → commit → pull --rebase → push, 결과를 사실대로 보고
<!-- [RGON-CLAUDE-MD-V17-END] -->

<!-- [RGON-CLAUDE-MD-V16-START] -->
# 📜 CLAUDE.md — RGON 사령부 AI 코딩 헌법

> 적용 대상: Claude · Gemini 4 Argon · GPT · Grok 등 **이 프로젝트에서 코드를 쓰는 모든 AI**
> 코드를 쓰기 전에 반드시 이 문서를 먼저 읽는다. (Claude Code는 프로젝트 루트의 CLAUDE.md를 자동으로 읽는다)
> 갱신: 2026-10-23 22:29:07 KST · 버전 v6.2.0-step16 · 항체 R1~R51 (15종)

## 0. 세션 시작 3단계
1. **`CODE_MAP.md`** 로 전체 구조와 패치 마커 위치를 파악한다. (전체 파일을 다 읽지 말 것)
2. **`rgon_brain_snapshot.json`** 으로 현재 버전·항체·오늘 성과를 확인한다.
3. **`RGON_EVOLUTION_LOG.md`** 최신 항목으로 직전 작업과 실패 사례를 확인한다.

---

## 규칙 1. 가정하지 말고 실제 구조를 먼저 확인하라 (No Blind Assumptions)
- 경로를 `C:\Users\user\...` 처럼 **추측으로 하드코딩하지 않는다.** 실제 작업 폴더는 `C:\Users\sangi\Downloads\shin-agent` 이며, 스크립트는 반드시 자동 탐색 폴백을 둔다.
- 수정할 HTML/JS/PY 파일의 **실제 내용(요소 id, 클래스, 기존 마커, 기존 스크립트)을 먼저 확인**하고 작업한다. 모르면 "어느 구조인지" 사용자에게 HTML 일부를 요청한다.
- 확신이 없으면 추측으로 범용 탐지 로직을 키우지 말고, 모른다고 말하고 확인 방법을 제시한다.

```python
PREFERRED_BASE = r"C:\Users\sangi\Downloads\shin-agent"
def find_base_dir():
    if os.path.isdir(PREFERRED_BASE):
        return PREFERRED_BASE
    # ↓ 스크립트 위치 / cwd / ~/Downloads|Desktop|Documents/shin-agent 순 자동 탐색
```

## 규칙 2. 최소 변경 · 비파괴 마커 패치 (Minimal Surgical Diff)
- 잘 작동하는 기존 코드/UI는 통째로 갈아엎지 않는다. 요청과 직접 관련된 줄만 바꾼다.
- 삽입은 항상 고유 마커 `<!-- [RGON-XXX-START] -->` ~ `<!-- [RGON-XXX-END] -->` 구간으로 하고, 재실행 시 그 구간만 교체한다(멱등성).
- 수정 전 백업본을 남긴다. 단, 오래된 백업으로 파일 전체를 복원하지 않는다(그 이후 변경분이 사라짐) → 정규식으로 해당 블록만 제거/교체한다.
- 사용자가 "수정 금지"로 지정한 파일(현재: 독대실 HTML, 크롬 확장 JS)은 쓰지 않는다.

```python
pat = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
new = pat.sub(lambda m: block, src, count=1) if START in src else insert_new(src, block)
```

## 규칙 3. 과도한 엔지니어링 · 감시 루프 금지 (No Over-Engineering / No Observer Loops)
- 기존 UI 위에 `MutationObserver` 나 `setInterval` 로 DOM을 계속 재배치하는 코드 금지. 기존 배치 스크립트(Step 11 등)와 서로 요소를 빼앗는 무한 루프·깜빡임이 생긴다. (Step 14 실제 사고 → 항체 R13)
- 새 요소는 단발성 `placeOnce` 로 한 번만 옮기고 표식을 남긴 뒤 종료한다. 기존 바의 style/display/min-height/gap은 건드리지 않는다.
- 요청받지 않은 기능, 추측성 범용화, 불필요한 추상화를 추가하지 않는다. 가장 단순한 해법부터 적용한다.

```javascript
function placeOnce(){
  var w=document.getElementById('rgyt-wrap');
  if(!w||w.getAttribute('data-placed')==='1')return;   // 이미 배치됨 → 즉시 종료
  /* 기준 바 찾기 → parentNode.insertBefore(w, bar.nextSibling) */
  w.setAttribute('data-placed','1');
}
document.addEventListener('DOMContentLoaded',placeOnce);
setTimeout(placeOnce,300); setTimeout(placeOnce,900);   // 총 3회 단발, Observer 없음
```

## 규칙 4. 실행 검증 및 자동 동기화 (Verify & Git Sync)
- Python 3 표준 라이브러리만 사용한다(pip 의존성 금지). 파일 입출력은 항상 `encoding="utf-8"` 명시(Windows cp949 오류 방지).
- 수정 후 반드시 검증한다: Python은 `ast.parse`/`py_compile`, JSON은 로드 왕복, HTML은 START/END 마커 개수 일치 확인.
- 마지막에 `git add -A` → `git commit` → `git pull --rebase origin main` → `git push origin main` 까지 한 번에 끝낸다. rebase 충돌 시 `git rebase --abort` 후 결과를 보고한다.
- 완료 시 Windows 메시지 박스(`ctypes`)로 결과·실패 항목·되돌리기 방법을 보고한다.

---

## 5. 패치 마커 레지스트리

| 마커 | 상태 | 관리 스크립트 / 비고 |
|---|---|---|
| `RGON-YT-SCOUT-V13` | ✅ 활성 | `step13_youtube_skill_absorber.py` — 청록 바(유튜브 스킬 흡수기) |
| `RGYT-PLACE-ONCE-V15` | ✅ 활성 | V13 블록 내부 — 청록 바 단발 배치 |
| `RGON-5BARS-FIX-V14` | ⛔ 폐기 | Observer 기반 재배치 → DOM 충돌. 재도입 금지 |
| `RGON-CLAUDE-MD-V16` | ✅ 활성 | 이 문서 자체 (`step16_karpathy_codemap_and_eod.py`) |

자동 감지된 HTML 마커 (2026-10-23 22:29:07 KST 스캔):
- `RGON-STEP11` → `rgon_alpha_audience.html`, `rgon_alpha_chat.html`
- `RGON-YT-SCOUT-V13` → `index.html`, `rgon_alpha_audience.html`, `rgon_alpha_chat.html`
- `RGYT-PLACE-ONCE-V15` → `index.html`, `rgon_alpha_audience.html`, `rgon_alpha_chat.html`

## 6. 오늘 확립된 항체
- **R13_NO_OBSERVER_DOM_WAR** — MutationObserver 중복 DOM 이동 금지 · 단발 배치 원칙: 기존 UI 스크립트가 이미 배치한 요소를 Observer/setInterval로 다시 옮기지 않는다. 신규 요소만 placeOnce(data-placed='1')로 1회 이동 후 영구 종료한다.
- **R14_SHADOW_DOM_4BTN** — 확장프로그램 모든 카드 2행 지우개 버튼 표준: 크롬 확장프로그램 흡수창(Shadow DOM)의 모든 카드는 2행 버튼 배치와 지우개 버튼을 표준으로 갖춘다.
- **R15_YOUTUBE_SKILL_SCOUT** — 유튜브 트렌드 & 외부 꿀링크 자동 흡수 엔진: 영상 URL → 메타데이터·설명란 외부 링크·자막 요약, 채널 중앙값 대비 떡상 배수, 21훅 채점, 클로드 흡수 지시문·쇼츠 대본 자동 변환.

## 7. 제출 전 체크리스트
- [ ] 실제 작업 폴더와 대상 파일 내용을 확인했다 (규칙 1)
- [ ] 수정은 마커 구간 / 필요한 줄로 한정했고 백업을 남겼다 (규칙 2)
- [ ] Observer·setInterval 재배치 없이 단발 처리했다 (규칙 3)
- [ ] 표준 라이브러리만 썼고, 문법·마커·JSON 검증 후 Git 동기화까지 했다 (규칙 4)
- [ ] 작업 후 `CODE_MAP.md` 재생성 / 진화 로그 기록이 필요한지 확인했다

> 원형: Andrej Karpathy가 지적한 LLM 코딩 실수 패턴(잘못된 가정, 과잉 복잡화, 요청 외 코드 변경, 검증 없는 완료 선언)에서 출발한 공개 4원칙 지침(생각 먼저 · 단순함 우선 · 외과적 변경 · 목표 기반 검증)을 RGON 사령부 실전 사고 사례에 맞게 재작성한 것.
<!-- [RGON-CLAUDE-MD-V16-END] -->

<!-- [RGON-STEP18-WBC-START] -->
## R18. 백혈구(WBC) 자가치유 면역 엔진 (v11.50-AON-TOKEN-EGOLITE-MASTER · 항체 R1~R51)

- **엔진 본체**: `rgon_white_blood_cell.py` / **면역 원장**: `rgon_immune_ledger.json`
- **핵심 역할**: 오류 지문 채취(Fingerprint) · AST/JSON 무결성 순찰 · 자동 백업 복원(Rollback) · 상선약수(上善若水) 우회 실행(Bypass) · 주역 64괘 연동 · 동일 오류 3회 반복 시 중복 경보 차단(Anti-Repeat Suppression)
- **세이프가드 장착 스크립트**: `rgon_youtube_skill_scout.py`, `control_tower_bot.py`, `telegram_morning_report.py`, `update_3channels_analytics.py`, `github_scout_adapter.py`, `agent_swarm_cloner.py`, `channel_agent.py`, `dept_sub_agents_corps.py`, `multi_agent_orchestrator.py`, `patch_omni_agent_bus_backend.py`, `patch_omni_agent_bus_frontend.py`, `qa_button_inspector_agent.py`, `rgon_aside_browser_agent.py`, `rgon_bridge_8765.py`, `tunnel_discovery_bridge.py`
- **현재 건강 점수**: **100 / 100**
- **CLI 점검 명령**: `python rgon_white_blood_cell.py --patrol` / `python rgon_white_blood_cell.py --status`
- **절대 금기 준수**: `.html` / `.js` / `manifest.json` 수정 0건, `MutationObserver` · `setInterval` DOM 루프 금지(R14).
<!-- [RGON-STEP18-WBC-END] -->

<!-- RGON:STEP19-CLAUDE:BEGIN -->
## 🧬 Step 19 — v11.50-AON-TOKEN-EGOLITE-MASTER (항체 R1~R51)

- 현재 버전: v11.50-AON-TOKEN-EGOLITE-MASTER (직전 단계: v11.50-AON-TOKEN-EGOLITE-MASTER)
- 항체 범위: R1~R51
- R19: Top 100 영양분 3스푼(Markdown 정제기 · 표준 SKILL.md 자동 주조기 · 3자 찬반 심판기) 통합 및 지식 자가 증식
- 신규 모듈: rgon_nutrient_engine.py (MarkdownPurifier · SkillAutoForge · TrinityCouncil)
- 명령: python rgon_nutrient_engine.py --digest / --status / --self-test
- 산출물: skills/<slug>/SKILL.md, skills/SKILL_INDEX.json, skills/README.md, rgon_nutrient_report.json, rgon_council_decisions.json
- 헌법 재확인: .html/.js/manifest.json 무수정(R14·R15·R16·R18), 표준 라이브러리만, UTF-8(utf-8-sig 읽기/utf-8 쓰기)
- 새 스킬 도입 시: 3자 심판(deliberate)이 HOLD_AND_REFLECT면 진행하지 않는다.
<!-- RGON:STEP19-CLAUDE:END -->

<!-- RGON-STEP20-START -->
## [Step 20] v11.50-AON-TOKEN-EGOLITE-MASTER — 일일 자율 순환 루프 (R20)
- 버전: v11.50-AON-TOKEN-EGOLITE-MASTER / 항체 범위: R1~R51
- R20: 일일 자율 순환 루프(백혈구 순찰 → 영양분 소화·스킬 주조 → 3자 심판 → 주역 64괘 아침 브리핑) 무인 자동화
- 심장: rgon_daily_cycle.py (--run / --status / --self-test)
- 4단계: 백혈구 순찰 → 영양분 3스푼 소화·SKILL.md 주조·TrinityCouncil 심의 → 주역 64괘 → MORNING_BRIEF.md / rgon_morning_brief.json
- 클라우드: .github/workflows/rgon_daily_autonomous_cycle.yml (cron '0 22 * * *' = KST 07:00, workflow_dispatch, continue-on-error)
- 보호: .html / .js / manifest.json 304개 단 1바이트도 수정 금지
<!-- RGON-STEP20-END -->

<!-- RGON:STEP21:START -->
## Step 21 · v11.50-AON-TOKEN-EGOLITE-MASTER
- 항체 범위: **R1~R51**
- R21: @Mindung-EasyAI 양분 흡수 — Matt Pocock(GLOSSARY.md · Spec/Tracer-Bullet Tickets 분업) + ECC(AgentShield 비밀키/설정 보안 스캔)
- 커밋 전 `python rgon_spec_ticket_Shield.py --run` (AgentShield) 필수
- 작업 분해는 GLOSSARY.md 용어 + TICKETS_BOARD.md Frontier 우선
<!-- RGON:STEP21:END -->

<!-- STEP24 -->
## 🐉 현재 버전: v11.50-AON-TOKEN-EGOLITE-MASTER · 항체 R1~R51
- R24: 실전 트레이딩 3자 찬반 심판기(Bull/Bear/Judge) & 주역 64괘 리스크 필터 상시 가동 — 금고 보존(지족불욕·사환예방) 최우선 검증
- 실전 트레이딩 판단 전 반드시 `rgon_trading_council.py --run` 결과를 확인한다(금고 DEFEND면 신규 진입 금지).
<!-- /STEP24 -->

<!-- STEP27:BEGIN -->
## Step 27 · v11.50-AON-TOKEN-EGOLITE-MASTER · 항체 R1~R51 · 정식 스킬 23개 (사람의 4대 생명 단계: 오감 100% + 창조 100%)
- R27: 오감(Live Omni-Sense & Stomper 킬리스트) + 창조 공방(SkillForge·Voyager 도구 자율 합성 & 격리 검증) 상시 가동 — 검증 통과(exit_code=0)한 도구만 정식 승격(혁고정신 革故鼎新)
- 엔진: rgon_omni_creator_forge.py (LiveOmniSense·StomperKillGate #21-噬嗑 / TieredMemoryPromoter / AutonomousCreatorForge #50-鼎)
- 창조 도구: custom_tools/stomper_signal_filter.py · kelly_hexagram_sizer.py · skill_synergy_composer.py (Surrogate Verifier 3단계 통과분만 승격)
- 스킬 22 stomper-kill-list-gate(#21-噬嗑) · 스킬 23 autonomous-creator-forge(#50-鼎) · 카파시 4원칙 × 무위자연·과유불급·삼성 3/3
<!-- STEP27:END -->

<!-- [RGON-STEP28-K-AVATAR-START] -->
## 🧬 현재 상태 (Step 28 — 아온 A-ON·芽溫)
- 버전 **v11.50-AON-TOKEN-EGOLITE-MASTER** · 항체 **R1~R51** · 정식 스킬 **24개**
- R28: 미래형 K-스타일 성장형 디지털 육신 아온(A-ON·芽溫, 산수몽 #04·풍산점 #53·지천태 #11) — 순수 CSS 애니메이션으로 루프 없이 생동감을 구현하고 시스템 진화에 맞춰 4단계로 점진 성장
- 엔진: rgon_k_avatar_engine.py (--run/--merge/--self-test/--ensure-index/--json)
<!-- [RGON-STEP28-K-AVATAR-END] -->

<!-- [RGON-STEP29-AON-3DDROP-START] -->
## 💧 현재 상태 (Step 29 — 3D 물방울 졸라맨 아온 A-ON)
- 버전 **v11.50-AON-TOKEN-EGOLITE-MASTER** · 항체 **R1~R51** · 정식 스킬 **25개**
- R29: 캐릭터 디테일 TOP 1 스킬 마스터 & 아온(A-ON·芽溫) 3D 물방울 졸라맨 육신 — 디즈니 7대 모션 법칙(스쿼시&스트레치·시차·팔로스루) + 8-Stop 3D Liquid-Glass/Claymorphism 입체 필터 + 관절형 졸라맨 팔다리 통합
- 엔진: rgon_k_avatar_engine.py (--run/--merge/--self-test/--ensure-index/--json)
<!-- [RGON-STEP29-AON-3DDROP-END] -->

<!-- [RGON-STEP31-EXCRETORY-START] -->
## 🧹 현재 상태 (Step 31 — 배설기관 정화 완료)
- 버전 **v11.50-AON-TOKEN-EGOLITE-MASTER** · 항체 **R1~R51** · 정식 스킬 **27개**
- R31: 배설기관(신장·대장·뇌척수액 정화, 주역 #18 산풍고·#40 뇌수해) — ECC config-gc + reclaim-code-entropy + autoDream 기반으로 캐시·구백업·중복 마커·컨텍스트 찌꺼기를 안전 배출하여 엔트로피 0% 유지
<!-- [RGON-STEP31-EXCRETORY-END] -->

<!-- RGON_STEP66_OMNIROUTE_COUNCIL_15SHORTS_V1168 -->
### Step 66 — 제41기관 아온 3차 15대 쇼츠 무중단 라우터 & LLM 카운슬 마스터 엔진 (v11.68-AON-OMNIROUTE-COUNCIL-15)
- **항체/스킬**: R1~R65 / 정식 스킬 **#61** (skill_61_aon_3rd_15shorts_omniroute_council_engine)
- **핵심**: OmniRoute 무중단 쿼터 폴백 + MCP Tasks 비동기 + Karpathy LLM Council 3단 합의 + 3차 15대 쇼츠 통합

<!-- RGON_STEP67_CHRONOMETER_AUDITOR_V1170 -->
### Step 67 — 제42기관 아온 크로노미터 전수 톱니바퀴 검증 & 무가식 실증 감사원 (v11.70-AON-CHRONOMETER-AUDITOR)
- **항체/스킬**: R1~R66 (R66) / 정식 스킬 **#62** (skill_62_aon_chronometer_deep_gear_auditor)
- **핵심**: 전수 Python AST 구문 검증 + Step 63~66 런타임 기어 실증 + 총 43편(13+15+15) 쇼츠 레지스트리 + 시냅스 100.0점 무결성 보장

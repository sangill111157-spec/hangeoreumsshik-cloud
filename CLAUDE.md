<!-- [RGON-CLAUDE-MD-V16-START] -->
# 📜 CLAUDE.md — RGON 사령부 AI 코딩 헌법

> 적용 대상: Claude · Gemini 4 Argon · GPT · Grok 등 **이 프로젝트에서 코드를 쓰는 모든 AI**
> 코드를 쓰기 전에 반드시 이 문서를 먼저 읽는다. (Claude Code는 프로젝트 루트의 CLAUDE.md를 자동으로 읽는다)
> 갱신: 2026-10-23 22:29:07 KST · 버전 v6.2.0-step16 · 항체 R1~R15 (15종)

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

# 🌐 [S1-SSOT] Ego-Lite (ego-browser v2.2.0) 공식 실전 마스터 가이드
**작성일시:** 2026-11-04T23:29:39.141808+09:00  
**스킬 버전:** `ego-browser v2.2.0` (공식 배포일: 2026-10-16, `bootstrap: true`)  
**소유권 및 관할:** 사령부 제1수석보좌관 르곤 & 기술총리 안총리 35대 기관

---

## 1. 개요 및 부트스트랩 원칙 (Bootstrap Protocol)
`ego-browser`는 사용자의 실제 로그인 상태와 브라우저 환경을 유지하면서 AI Agent가 안전하고 끊김 없이 웹 브라우징·QA·검증을 수행할 수 있도록 설계된 에이전트 전용 Chromium 브라우저입니다.

### 📌 동적 가이드 호출 원칙
브라우저 작업을 시작하기 전에는 반드시 아래 명령을 실행하여 현재 설치된 버전과 1:1 일치하는 동적 매뉴얼을 확인해야 합니다:
```bash
ego-browser skill
```
- 만약 출력 끝에 `[ego-browser:skill] end of guide` 문구가 보이지 않는다면 출력이 잘린 것이므로, 임시 파일로 리다이렉트하여 정독합니다:
  ```powershell
  ego-browser skill > "$env:TEMP\ego-browser-skill.md"
  ```
- 최신 버전 업데이트:
  ```bash
  ego-browser upgrade
  ```

---

## 2. 윈도우 환경 프로세스 무멈춤(Zero-Hang) 헌법
PowerShell 또는 Python `subprocess` 환경에서 `ego-browser`나 `ego.exe`를 구동할 때 대화형 터미널 입력 대기(`stdin`)로 인해 프로세스가 프리징(Hang)되는 현상을 원천 방지하기 위해 다음 원칙을 절대 엄수합니다:
- **`stdin=subprocess.DEVNULL` 필수 적용:**
  ```python
  subprocess.Popen(["ego-browser", ...], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  ```
- **백그라운드 잠금 충돌 방지:** `is_ego_running() == False` 가드를 사용하여 고아(Orphan) `ego.exe`가 실행 중일 때 신규 프로세스 충돌을 예방합니다.

---

## 3. 프로필 전체 쿠키·캐시 삭제 절대 금지 헌법 (Clearing-State Rules)
공식 `clearing-state.md` 가이드에 명시된 바와 같이, 브라우저 전체 프로필에 영향을 미치는 글로벌 삭제 명령은 사령부 로그인 세션과 사용자의 업무 환경을 파괴하므로 **절대 금지**합니다:

### ❌ 절대 금지 명령 (Global Clear)
- `Network.clearBrowserCookies`: 브라우저 전체 모든 도메인의 쿠키 영구 삭제 ➔ **절대 사용 금지!**
- `Network.clearBrowserCache`: 브라우저 전체 캐시 삭제 ➔ **절대 사용 금지!**

### ✅ 권장 및 허용 명령 (Origin-Scoped Clear)
- **단일 출처 데이터만 정리:**
  ```javascript
  // 특정 도메인(origin)의 쿠키 및 스토리지 데이터만 선별 정리
  await client.send('Storage.clearDataForOrigin', {
    origin: 'https://www.genspark.ai',
    storageTypes: 'all'
  });
  ```
- **캐시 무시 단일 페이지 새로고침:**
  ```javascript
  await client.send('Page.reload', { ignoreCache: true });
  ```

---

## 4. 047호 실전 배포 및 파일 무결성
- 스킬 원본 경로: `.agents/skills/ego-browser/SKILL.md` (v2.2.0)
- 참조 가이드:
  - `.agents/skills/ego-browser/references/install.md`
  - `.agents/skills/ego-browser/references/install-windows.md`
  - `.agents/skills/ego-browser/references/clearing-state.md`
- 본 문서는 `docs/S1_EGO_LITE_V2_2_SKILL_MASTER_GUIDE.md`와 100% SHA-256 동기화됩니다.

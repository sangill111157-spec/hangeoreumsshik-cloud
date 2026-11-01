---
name: ego-suno-direct-download
description: Complete skill manual for downloading authentic, unlocked Suno AI audio (MP3/WAV) and cover images directly through ego-browser without dummy synthesis or mock files.
metadata:
  version: "1.0.0"
  date: "2026-11-01"
  author: "S1 Imperial Tech Prime Ministry"
---

# 🎵 ego-suno-direct-download: Suno 실물 음원 직수 수집 마스터 스킬북

## 1. 개요 및 목적
이상일 대표님의 최고 어명(2026.11.01)에 따라 가짜 더미 오디오(sine wave) 생성을 원천 차단하고, `ego-browser`를 통해 대표님의 Suno 정품 계정(`sangill111157`)에서 생성된 고음질 V6 실물 음원(`.mp3` / `.wav`)과 고해상도 앨범 아트 커버를 100% 실측으로 직접 다운로드하는 공식 스킬 규격서이다.

---

## 2. 사전 도구 마스터 확인 (Tool Mastery Protocol)
1. **브라우저 환경:** `ego-browser` (Chromium 기반)
2. **세션 상태:** Suno 로그인 세션 유지 (Clerk JWT `__session` 쿠키 유효)
3. **태스크 스페이스:** `Space 17` (또는 활성 Suno Space)
4. **접근 권한:** Song Unlock 권한 보유 계정

---

## 3. Suno 웹 인터페이스 DOM 및 API 아키텍처 실측 분석

### 3.1 Suno REST API 엔드포인트 명세
- **Clip Details API:** `https://studio-api.prod.suno.com/api/clip/<clip_id>`
- **User Feed API:** `https://studio-api.prod.suno.com/api/feed/v2?page=0`
- **인증 헤더:** `Authorization: Bearer <clerk_jwt_token>` (쿠키 `__session`에서 추출)
- **응답 페이로드:** 곡 ID, 제목, 모델명, 가사 메타데이터, 오디오 스트림 CDN 주소

### 3.2 곡 상세 페이지 DOM 구조 (`https://suno.com/song/<clip_id>`)
- **곡 재생 및 툴바:** 곡 헤더 우측 및 하단에 툴바 배치
- **더보기 메뉴 버튼:** `button[aria-label="More options"]`
- **팝오버 메뉴:** `[role="menu"]` 내 `[role="menuitem"]`
- **다운로드 항목:** `[role="menuitem"]` 중 텍스트가 `"Download"`인 요소
- **다운로드 모달 대화상자:** `[role="dialog"]` 또는 `[aria-modal="true"]`
- **포맷 선택 버튼:**
  - `M4A` (Submit button)
  - `MP3` (Submit button, 선택 시 `bg-foreground-primary text-background-primary` 전환)
  - `WAV` (Submit button)
  - `MP4 video asset` (Submit button)
- **최종 다운로드 실행 버튼:** 다이얼로그 내 텍스트가 `"Download"`인 `button` (포맷 미선택 시 `disabled=true`, 포맷 선택 시 `disabled=false` 활성화)

---

## 4. 실전 자동 다운로드 스크립트 템플릿

```javascript
import fs from 'node:fs/promises';
import path from 'node:path';

// 1. Task Space 확보
const task = await takeOverTaskSpace(17);
const page = task.page("p2");

const clipId = "73ba5c00-7d00-43c3-b3c4-28ae873ac59a";
const songUrl = `https://suno.com/song/${clipId}`;

// 2. 곡 상세 페이지 이동
await page.goto(songUrl, { waitUntil: 'load', timeout: 30000 });
await new Promise(r => setTimeout(r, 2500));

// 3. 다운로드 모달 열기
await page.evaluate(async () => {
  // 열려있는 대화상자가 있다면 닫기
  const oldDialog = document.querySelector('[role="dialog"]');
  if (oldDialog) {
    const closeBtn = oldDialog.querySelector('button[aria-label="Close"]');
    if (closeBtn) closeBtn.click();
    await new Promise(r => setTimeout(r, 400));
  }

  // More options 클릭
  const moreBtns = Array.from(document.querySelectorAll('button[aria-label="More options"]'));
  if (moreBtns.length > 0) moreBtns[0].click();
  await new Promise(r => setTimeout(r, 500));

  // Download 메뉴 아이템 클릭
  const dlItem = Array.from(document.querySelectorAll('[role="menuitem"]')).find(
    el => el.innerText && el.innerText.trim() === 'Download'
  );
  if (dlItem) dlItem.click();
  await new Promise(r => setTimeout(r, 800));
});

// 4. 브라우저 다운로드 이벤트 리스너 대기 (중요: 클릭 전 사전 등록)
const downloadPromise = page.waitForEvent("download", { timeout: 45000 });

// 5. 포맷 선택(MP3) 및 다운로드 버튼 클릭
await page.evaluate(async () => {
  const dialog = document.querySelector('[role="dialog"]');
  if (!dialog) return;
  const buttons = Array.from(dialog.querySelectorAll('button'));
  const mp3Btn = buttons.find(b => b.innerText && b.innerText.trim() === 'MP3');
  if (mp3Btn) mp3Btn.click();
  await new Promise(r => setTimeout(r, 400));

  const dlBtn = buttons.find(b => b.innerText && b.innerText.trim() === 'Download');
  if (dlBtn) dlBtn.click();
});

// 6. 다운로드 수신 및 파일 저장
const download = await downloadPromise;
const savePath = "C:/Users/sangi/Downloads/shin-agent/studio_vault/CEO_SUNO_V6_ORIGINALS/sample.mp3";
await download.saveAs(savePath);

// 7. 커버 아트 수집 (page.fetch)
const coverUrl = `https://cdn2.suno.ai/image_${clipId}.jpeg`;
const coverSavePath = "C:/Users/sangi/Downloads/shin-agent/studio_vault/CEO_SUNO_V6_ORIGINALS/sample_cover.jpeg";
await page.fetch(coverUrl, { saveAs: coverSavePath });

// 8. 제어권 반환
await task.handOff();
```

---

## 5. 다운로드 무결성 실측 검증 (ffprobe Quality Verification)

다운로드 완료 후 반드시 `ffprobe`로 실물 파일의 무결성을 검증한다:

```bash
ffprobe -v error -show_entries format=duration,bit_rate:stream=codec_name,channels,sample_rate sample.mp3
```

- **검증 기준:**
  1. `duration`: 대표님 친작 곡 길이와 일치 (최소 120초 이상, 예: 158.0s, 139.8s, 202.36s, 178.8s)
  2. `channels`: 2 (Stereo)
  3. `sample_rate`: 44100Hz 또는 48000Hz
  4. `codec_name`: mp3 (또는 wav)
  5. `bit_rate`: 128kbps 이상 고음질

---

## 6. 마스터링 후처리 파이프라인 (FFmpeg Broadcast Standard)
- 유튜브 및 스트리밍 글로벌 표준: **`-14.0 LUFS`**, 44.1kHz 16-bit WAV 마스터링
- 변환 명령어:
  ```bash
  ffmpeg -i sample.mp3 -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 44100 -ac 2 sample_master_14LUFS.wav
  ```

---

## 7. 스킬북 등록 상태 및 무결성 서명
- **관리 번호:** `SKILL-S1-SUNO-001`
- **적용:** 전 제국 파이프라인(`s1_studio_pipeline.py`, `s1_suno_maestro_agents.py`, `s1_channel_directors.py`, `s1_24h_free_scheduler.py`)
- **승인:** 제1수석보좌관 르곤 & 기술총리 안총리

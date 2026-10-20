# RUNLOG — 사냥꾼의 새벽 (Hunter's Dawn)

## Cumulative Cost Summary
- **Current Total Cost**: $0.00 (Built-in engine & local audio tools used)
- **Budget Threshold**: $50.00 Max (R9 Compliant)

---

## Event Logs

### [2026-07-26 Phase 0 (P0) Initialization & Pipeline Smoke Test]
- **Status**: PASSED (Conditional Approval & Fixes applied)
- **Actions**:
  - Directory structure & `.gitignore`, `.env.example` created.
  - Built-in Nano Banana image engine tested for multi-reference support (`ImagePaths` 3 refs attached).
  - TEST-0 sheet & pose generated (`t0_sheet.png`, `t0_newpose_wide.png`).
  - FaceNet MTCNN & VGGFace2 deep embedding similarity calculated (**T-CU 0.8616 achieved**).
  - ffmpeg concat video chain tested (`t5_concat.mp4`).

### [2026-07-28 Phase 1 (P1-R2) Sound Map Ground Truth & Cut Timecode Finalization]
- **Status**: PASSED & Completed
- **Actions**:
  - v1 18구간 휘파람 오검출 전량 폐기 후, 감독 확정 GROUND TRUTH 사운드 맵으로 2차 전면 교체.
  - 템플릿 3종 (`tpl_whistle.wav`, `tpl_clap.wav`, `tpl_riff.wav`) 및 특성(F0, HNR, Spectral Flatness) 추출.
  - `00_audio/whistle_phrases.json` (0-7s 6악구 분절) 및 `00_audio/accents.json` (박수 5타, 리프① 4타, 리프② 4타 온셋) 생성.
  - 검증용 wav 6종 (`v1_intro` ~ `v6_outro`) `00_audio/verify/` 폴더 내 생성.
  - Sound Map 기반 G1~G7 타임코드 확정 (총 43컷, 185.480s 100% 비트 스냅 일치).
    - **S10 시작점 33.440s 절대 고정**
    - **S13 리프 4타(51.220s~) 싱크**
    - **S19 (78-80s 휘파람) 원경 고정, 립싱크 금지**
    - **S27 (121.250-125.432s) Verse2->Bridge 전환 샷으로 근거 교체 유지**
    - **S29 리프 4타(131.704s~) S28->S29 컷 타격**
    - **S38 주인공 휘파람 응답 (175.598-179.779s)**
  - 5.0초 초과 클립 9개 리스트업 완료.
- **Cost**: $0.00

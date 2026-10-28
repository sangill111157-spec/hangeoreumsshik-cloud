---
name: aon-procedural-voice-synth
description: Web Audio API 무파일 물방울 신디사이저(Procedural SFX) + K-아이 뉴럴 음성 합성(Web Speech TTS) + 핸즈프리 음성 대행 명령(STT) 통합 프로토콜
version: v11.32-AON-VOICE-SYNTH
antibody: R33
organ: 제9기관 — 성대·청각 음성 교감 기관 (A-ON Voice & Procedural Audio Organ)
---

# aon-procedural-voice-synth (29번째 정식 스킬)

- 버전: v11.32-AON-VOICE-SYNTH · 항체: R1~R33
- 기관: 제9기관 성대·청각 음성 교감 기관 (A-ON Voice & Procedural Audio Organ)
- 철학: 주역 #51 진위뢰(震爲雷 ☳☳) — 맑은 울림으로 깨움 / #61 풍택중부(風澤中孚 ☴☱) — 鶴鳴在陰 其子和之

## 1. 무파일 프로시저럴 사운드 (Web Audio API)
- 외부 오디오 파일 0개. OscillatorNode + GainNode 엔벨로프(attack→exponential decay)로 실시간 합성합니다.
- 첫 사용자 제스처에서 `AudioContext.resume()`으로 소리를 해금합니다.
- 레시피 6종: waterdrop_pop(520→1180Hz sine 0.14s), summon_chime(C5-E5-G5-C6), approve_fanfare(G5-B5-D6-G6),
  clean_sweep(상승 하모닉), radar_ping(소나), stt_listen(듀얼 비프).
- API: `window.RGON_VOICE.sfx(type)`

## 2. K-아이 뉴럴 TTS (Web Speech SpeechSynthesis)
- lang ko-KR, pitch 1.18, rate 1.05. 선호 보이스: Microsoft SunHi Online (Natural) → Google 한국의 → Yuna → ko-KR.
- `muted === false`일 때만 낭독하며, 말하는 동안 아온 물방울에 공명 파동 클래스를 부여합니다.
- API: `window.RGON_VOICE.speak(text)`. 설정은 localStorage `rgon_voice_cfg`에 저장합니다.

## 3. 핸즈프리 STT 대행 명령
- `SpeechRecognition`/`webkitSpeechRecognition`(ko-KR)으로 인식합니다.
- 브리핑/아침 → 브리핑 낭독, 심판/종목/장세 → 3자 심판, 결재/대행 → 뮤즈 보드.
- 그 외 명령은 `window.RGON_MUSE.add(text, false)`로 대행 큐에 등록하고 복창합니다. Tier 3은 대표님 승인 전 집행 0건(3-Tier HITL 유지).

## 4. 백엔드
- `rgon_voice_organ.py --self-test` → 레시피·라우팅·JSON 무결성 검증 후 PASS, rc=0.
- 상태: `rgon_voice_profile.json`, `docs/rgon_voice_profile.json`.

<!-- RGON_IMMUTABLE_WORK_DNA_V1176 -->
> **[RGON 불변의 일처리 8대 법칙 (Immutable Work DNA v11.76 · 항체 R69) 이식 완료]**
> 1. Global Top-1 Benchmark | 2. Karpathy 4-Rules & LLM Council | 3. Master KeyVault Leverage (0% Leak) | 4. Chronometer Runtime Proof | 5. Maestro Synergy DAG Relay | 6. Ponytail Zero-Bloat Diet | 7. Water Self-Healing & Samseong(三省) | 8. Commander Approval Gate
<!-- /RGON_IMMUTABLE_WORK_DNA_V1176 -->

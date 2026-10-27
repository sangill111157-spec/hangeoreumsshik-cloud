---
name: aon-gdrive-5tb-organizer
version: v11.61-AON-GDRIVE-5TB-DECIMAL
organ_id: 37
organ_name: "아온 Google One 5TB 초심플 클라우드 아카이브 엔진"
antibody: R61_GDRIVE_5TB_DECIMAL_LOCK
hexagram: "#37 풍화가인(風火家人)"
description: "Google One 5TB Johnny.Decimal × PARA 초심플 무인 자동 정리정돈 및 스마트폰 3초 업로드 클라우드 아카이브 엔진"
category: "cloud-storage-automation"
tags: ["google-one", "5tb", "johnny-decimal", "para", "cloud-storage", "inbox-routing", "sub-accounts"]
---

# ☁️ [스킬 #57] aon-gdrive-5tb-organizer (Google One 5TB 초심플 아카이브 엔진)

> **주역 괘:** `#37 풍화가인(風火家人)` — 바깥의 불과 안의 바람이 어우러져 질서를 바로잡고 평안을 이루는 대길의 괘  
> **스토리지:** Google One 5TB (5,000GB 중 15.91GB 사용, 4,984.09GB / 99.68% 가용)  
> **계정:** `sangill111157@gmail.com` (이상일 대표님)  
> **서브계정:** `99 ROBLGYE (@99ROBLGYE · 미래 대기 채널)`, `이해상 (수석 디자이너)`, `이송효 (가족 보물금고)`

---

## 1. 개요 및 설계 철학

세계 Top 1 파일 정리 표준인 **『Johnny.Decimal (00~06 대분류 + 11~62 중분류, 최대 2단계 제한) × PARA』** 원칙을 적용하여, 대표님께서 이동 중이나 현장에서 스마트폰으로 아무 파일이나 `00_INBOX`에 던져 넣으면 사령부 엔진이 파일명과 확장자를 분석하여 01~06 하위 폴더로 자동 분류·정리하는 무인 클라우드 엔진입니다.

---

## 2. Johnny.Decimal 00~06 디렉터리 트리

```
gdrive_5tb_archive/
├── 00_📥_INBOX_일단여기에넣기/ (스마트폰/PC 무인 투입구, 별표 고정 ⭐)
├── 01_💿_한걸음씩_음원마스터_DistroKid/
│   ├── 11_가을과겨울사이_12곡_20261106/ (UPC 700563848544)
│   ├── 12_잔상_15곡_20261127/ (UPC 700486463268)
│   ├── 13_기발매곡_영혼의무게_모두의응원가/
│   └── 14_미발매_신곡아이디어_보관함/
├── 02_📺_유튜브_4대채널_스튜디오/
│   ├── 21_🌿_한걸음씩_공식MV_쇼츠/ (@한걸음씩-r4i)
│   ├── 22_⚡_부스터플리_운동드라이브_1시간플리/ (@Booster_Playlist)
│   ├── 23_☕_TheCafeHour_카페재즈_라운지/ (@TheCaféHour)
│   └── 24_🎮_99ROBLGYE_미래대기채널/ (@99ROBLGYE)
├── 03_📱_SNS바이럴_틱톡_인스타_스레드/
│   ├── 31_틱톡_부스터플리_숏폼원본/ (@boosterplaylist 2,125명)
│   └── 32_인스타릴스_스레드_페북_공용영상/ (메타 3초 원스톱 배포)
├── 04_📝_건강블로그_connect-ai-shin/
│   ├── 41_블로그_직접찍은사진_텀블러_식단/ (1.5L 텀블러, 식사 루틴)
│   └── 42_블로그_포스팅원고_백업/ (3조 2교대 건강 7대 DNA)
├── 05_📈_엔비디아_퀀트_오토트레이딩/
│   └── 51_트레이딩_수익률리포트_백업/ (KIS 모의투자 $107,246.38)
└── 06_🏛️_RGON사령부_및_가족보물금고/
    ├── 61_RGON사령부_전체코드_일일자동백업/ (37대 기관 57스킬)
    └── 62_👨👧👧_이해상_이송효_가족사진_보물창고/ (공주님 작품·사진)
```

---

## 3. 스마트폰 3초 업로드 법칙

1. 스마트폰 구글 드라이브 앱 실행
2. `00_📥_INBOX_일단여기에넣기` 폴더를 **[별표 추가 ⭐]**
3. 이동 중, 퇴근길, 출근길에 촬영한 사진이나 다운로드한 파일을 `00_INBOX`로 공유/업로드
4. 사령부 제37기관 무인 정렬기(`sort_inbox()`)가 파일명을 인식하여 `YYYY-MM-DD_원본파일명` 형식으로 01~06 폴더에 자동 배치!

---

## 4. CLI 실행 명령

```bash
# 25대 무결성 셀프테스트
python rgon_aon_gdrive_5tb_organizer.py --self-test

# 5TB 스토리지 및 현황 브리핑 출력
python rgon_aon_gdrive_5tb_organizer.py --summary

# 파일명 자동 분류 시뮬레이션
python rgon_aon_gdrive_5tb_organizer.py --classify "가을과겨울사이_마스터_음원.wav"

# 조니 데시멀 전체 트리 조회
python rgon_aon_gdrive_5tb_organizer.py --tree
```

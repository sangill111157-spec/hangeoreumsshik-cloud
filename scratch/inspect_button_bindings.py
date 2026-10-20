import re
from pathlib import Path

index_html = Path("dashboard/index.html").read_text(encoding="utf-8")

buttons_to_check = [
    # 1. 공통 헤더
    ("헤더 OTA 버전 배지", r'id="ota-badge"', r'checkVersionAndUpdate'),
    ("헤더 8대 부처 어전회의 버튼", r'openEmpireCouncilModal', r'function\s+openEmpireCouncilModal'),
    ("어전회의 브리핑 복사 버튼", r'copyCouncilBriefing', r'function\s+copyCouncilBriefing'),
    ("어전회의 텔레그램 전송 버튼", r'sendCouncilToTelegram', r'function\s+sendCouncilToTelegram'),
    ("헤더 보안 설정 버튼", r'switchTab\([\'"]vault[\'"]\)', r'switchTab'),

    # 2. Tab 1 사령부
    ("제0원 주간근무 버튼", r'setWorkShiftMode\([\'"]day[\'"]\)', r'function\s+setWorkShiftMode'),
    ("제0원 야간근무 버튼", r'setWorkShiftMode\([\'"]night[\'"]\)', r'function\s+setWorkShiftMode'),
    ("제0원 휴무일 버튼", r'setWorkShiftMode\([\'"]off[\'"]\)', r'function\s+setWorkShiftMode'),
    ("제0원 디스크 청소 버튼", r'runGeneralAffairsClean', r'function\s+runGeneralAffairsClean'),
    ("제1원 자율법무 감사 버튼", r'runLegalComplianceAudit', r'function\s+runLegalComplianceAudit'),
    ("제2원 4대 분야 선택 버튼군", r'selectScoutCategory', r'function\s+selectScoutCategory'),
    ("제2원 GitHub 보물 답사 시작", r'startGitHubScout', r'function\s+startGitHubScout'),
    ("제2원 맞춤 개조·흡수 하달", r'adoptOpenSource', r'function\s+adoptOpenSource'),
    ("제3원 나눔 후보지 투표", r'voteDonationCandidate', r'function\s+voteDonationCandidate'),
    ("클라우드 4대 발사대 버튼군", r'launchCloudWorkflow', r'function\s+launchCloudWorkflow'),
    ("클라우드 실행기록 새로고침", r'refreshWorkflowStatus', r'function\s+refreshWorkflowStatus'),
    ("제6원 재정 분배표 텔레그램 보고", r'sendFinanceToTelegram', r'function\s+sendFinanceToTelegram'),

    # 3. Tab 2 Suno & 비주얼
    ("Suno 채널 선택 버튼군", r'selectSunoChannel', r'function\s+selectSunoChannel'),
    ("Suno 황금 프롬프트 생성", r'generateSunoPrompt', r'function\s+generateSunoPrompt'),
    ("Suno 프롬프트 복사 & 열기", r'copyStyleAndOpenSuno', r'function\s+copyStyleAndOpenSuno'),
    ("내 PC 음원 목록 새로고침", r'loadSunoFiles', r'function\s+loadSunoFiles'),
    ("내 PC 음원 선택 스트리밍", r'onSunoFileSelected', r'function\s+onSunoFileSelected'),
    ("432Hz 8시간 롱폼&쇼츠 렌더링", r'launchSunoRender', r'function\s+launchSunoRender'),
    ("썸네일 캔버스 새로 그리기", r'drawThumbnailCanvas', r'function\s+drawThumbnailCanvas'),
    ("썸네일 PNG 다운로드", r'downloadThumbnailPng', r'function\s+downloadThumbnailPng'),

    # 4. Tab 3 AI 소통 & OSMU
    ("채팅 4대 프리셋 질문", r'setBrainPrompt', r'function\s+setBrainPrompt'),
    ("음성인식 마이크 토글", r'toggleVoiceRecognition', r'function\s+toggleVoiceRecognition'),
    ("AI 채팅 메시지 전송", r'sendBrainMessage', r'function\s+sendBrainMessage'),
    ("AI 답변 복사", r'copyLastBrainAiResponse', r'function\s+copyLastBrainAiResponse'),
    ("AI 답변 텔레그램 전송", r'sendLastBrainResponseToTelegram', r'function\s+sendLastBrainResponseToTelegram'),
    ("안실장 직통 하달", r'dispatchLastBrainToAgentQueue', r'function\s+dispatchLastBrainToAgentQueue'),
    ("OSMU 블로그+커뮤니티 생성", r'generateOsmuContent', r'function\s+generateOsmuContent'),

    # 5. Tab 4 인성학교 & 인증원
    ("4대 덕목 선택", r'selectVirtue', r'function\s+selectVirtue'),
    ("새 에피소드 생성", r'generateGameEpisode', r'function\s+generateGameEpisode'),
    ("선택지 A/B 클릭", r'pickChoice', r'function\s+pickChoice'),
    ("단독 웹게임 내보내기", r'exportHeartGameHtml', r'function\s+exportHeartGameHtml'),
    ("세 딸 프리셋 선택", r'selectDaughterPreset', r'function\s+selectDaughterPreset'),
    ("인증서 고화질 PNG 저장", r'downloadCertificatePng', r'function\s+downloadCertificatePng'),

    # 6. Tab 5 지혜금고 & 실록
    ("지혜금고 목록 로드", r'loadWisdomLedger', r'function\s+loadWisdomLedger'),
    ("잘한점/오답백신 등록 모달 열기", r'openAddWisdomModal', r'function\s+openAddWisdomModal'),
    ("지혜 실록 즉시 등재", r'submitWisdomEntry', r'function\s+submitWisdomEntry'),
    ("지혜 입력창 닫기", r'closeWisdomInputCard', r'function\s+closeWisdomInputCard'),
    ("기억금고 목록 로드", r'loadMemoryVault', r'function\s+loadMemoryVault'),
    ("보안 설정 저장", r'saveVaultSettings', r'function\s+saveVaultSettings'),
]

print("=== [HTML & JS Button / Handler Binding Inspection] ===")
missing = []
for name, dom_pattern, func_pattern in buttons_to_check:
    has_dom = bool(re.search(dom_pattern, index_html))
    has_func = bool(re.search(func_pattern, index_html))
    status = "OK" if (has_dom and has_func) else "FAIL"
    print(f"[{status}] {name}: DOM={has_dom}, Handler={has_func}")
    if not (has_dom and has_func):
        missing.append((name, has_dom, has_func))

print(f"\nTotal checked: {len(buttons_to_check)}, Missing/Broken: {len(missing)}")

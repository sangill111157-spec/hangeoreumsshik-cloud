# -*- coding: utf-8 -*-
"""
🔭 한걸음씩 AI 제국 : 제2원(미래지향·공존개발팀)
〈글로벌 오픈소스 탐사 & 흡수단 (GitHub Daily Scout & Adapter)〉
선구자들의 오픈소스(GitHub)를 실시간 답사하고 라이선스 안전성을 검증하여,
우리 제국(8H 수면 음악 / 세 딸 인성학교 / 퀀트·NVDA / 경량 사령부)에 맞게 개조·흡수하는 엔진
"""
# [RGON-WBC-GUARD-V18-START]
try:
    import rgon_white_blood_cell as _rgon_wbc
    _rgon_wbc.install_excepthook('github_scout_adapter.py')
except Exception:
    _rgon_wbc = None
# [RGON-WBC-GUARD-V18-END]

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# 4대 핵심 전략 분야별 탐사 검색 쿼리
SCOUT_CATEGORIES = {
    'audio': {
        'name': '🎵 힐링 오디오·FFmpeg',
        'query': 'binaural OR "ambient audio" OR "ffmpeg audio" OR "sleep sound" OR "white noise" stars:>30',
        'focus': '노트북 CPU 무부하 8시간 수면 음악, 바이노럴 비트 합성, FFmpeg 초경량 루프 렌더링'
    },
    'education': {
        'name': '🎓 인성 웹게임·에듀테크',
        'query': '"educational game" OR "kids game" OR "learning game" stars:>40',
        'focus': '이은솔·이송효·이해상을 위한 웹 캔버스 인성 퀴즈, 대화형 도덕/예절 게임, 브라우저 로컬 구동'
    },
    'quant': {
        'name': '📈 퀀트·NVDA 분석',
        'query': '"technical analysis" OR "quant trading" OR "stock analysis" stars:>100',
        'focus': 'NVDA 및 고배당주 차트 보조지표, 볼린저 밴드/RSI 자동 산출, 장시작 전 모바일 텔레그램 알림'
    },
    'agent': {
        'name': '🤖 초경량 AI 자동화',
        'query': '"ai agent" OR "autonomous agent" OR "workflow automation" stars:>100',
        'focus': '단일 파일 실행, 무설치 크론 작업, 저사양 노트북 백그라운드 24시간 무정지 자율 운영'
    }
}

# 안전 상업/개조 라이선스 세트
PERMISSIVE_LICENSES = {
    'mit': '🟢 안전 (MIT - 상업·개조 자유)',
    'apache-2.0': '🟢 안전 (Apache 2.0 - 특허 보호·개조 자유)',
    'bsd-2-clause': '🟢 안전 (BSD 2-Clause - 자유 배포)',
    'bsd-3-clause': '🟢 안전 (BSD 3-Clause - 자유 배포)',
    'isc': '🟢 안전 (ISC - 극도로 관대한 라이선스)',
    'unlicense': '🟢 안전 (퍼블릭 도메인 동등)',
    'cc0-1.0': '🟢 안전 (CC0 - 완전 자유 나눔)'
}

def evaluate_license(license_obj):
    """제1원(자율법무팀) 라이선스 실시간 안전도 판정"""
    if not license_obj:
        return {
            'key': 'none',
            'name': '미명시 (주의)',
            'badge': '⚪ 라이선스 점검 필요',
            'safe_for_adoption': False
        }

    key = (license_obj.get('key') or '').lower()
    name = license_obj.get('name') or key.upper()

    if key in PERMISSIVE_LICENSES:
        return {
            'key': key,
            'name': name,
            'badge': PERMISSIVE_LICENSES[key],
            'safe_for_adoption': True
        }
    elif any(k in key for k in ['gpl', 'agpl', 'lgpl']):
        return {
            'key': key,
            'name': name,
            'badge': '🟡 전염성 라이선스 (코드 직접 결합 금지, 독립 CLI/도구로만 연동 가능)',
            'safe_for_adoption': False
        }
    else:
        return {
            'key': key,
            'name': name,
            'badge': f'🟡 {name} (조건부 검토 필요)',
            'safe_for_adoption': False
        }

def scout_github_repositories(category_key: str = 'audio', limit: int = 3, github_token: str = None) -> dict:
    """GitHub 공식 REST API로 실시간 오픈소스 보물 탐사"""
    if category_key not in SCOUT_CATEGORIES:
        category_key = 'audio'

    cat_info = SCOUT_CATEGORIES[category_key]
    query = cat_info['query']

    encoded_query = urllib.parse.quote(query)
    api_url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&order=desc&per_page={limit}"

    headers = {
        'User-Agent': 'HanGeoreumSShik-Empire-Scout/1.0',
        'Accept': 'application/vnd.github.v3+json'
    }
    token = github_token or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f"Bearer {token}"

    req = urllib.request.Request(api_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            items = data.get('items', [])
            total_count = data.get('total_count', 0)

            results = []
            for item in items:
                lic_eval = evaluate_license(item.get('license'))
                results.append({
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'full_name': item.get('full_name'),
                    'html_url': item.get('html_url'),
                    'description': item.get('description') or '원문 설명이 제공되지 않은 저장소입니다.',
                    'stars': item.get('stargazers_count', 0),
                    'forks': item.get('forks_count', 0),
                    'language': item.get('language') or 'General',
                    'updated_at': (item.get('updated_at') or '')[:10],
                    'license': lic_eval
                })

            return {
                'success': True,
                'category': category_key,
                'category_name': cat_info['name'],
                'category_focus': cat_info['focus'],
                'total_count': total_count,
                'repositories': results
            }
    except Exception as e:
        return {
            'success': False,
            'category': category_key,
            'category_name': cat_info['name'],
            'error': str(e),
            'repositories': []
        }

def build_default_adaptation_plan(repo: dict, category_key: str) -> str:
    """Gemini 연동 불가 시 제2원 기본 맞춤 개조 템플릿"""
    cat_info = SCOUT_CATEGORIES.get(category_key, SCOUT_CATEGORIES['audio'])
    name = repo.get('name', '오픈소스')
    desc = repo.get('description', '')

    if category_key == 'audio':
        return (
            f"💡 [제2원 개조안] '{name}'의 핵심 오디오 처리 로직을 파이썬 단일 모듈로 경량화하여, "
            f"현재 우리 `healing_music_producer.py`의 배경 자연음 및 바이노럴 주파수 생성 단계에 무부하 플러그인으로 합성 연동합니다."
        )
    elif category_key == 'education':
        return (
            f"💡 [제2원 개조안] '{name}'의 대화형 웹 캔버스 인터랙션을 추출하여, "
            f"우리 대시보드 4번 탭(AI 인성학교)에 세 딸(이은솔 수석·이송효 선임·이해상 주니어 자문위원) 전용 '오늘의 미덕 실천 퀴즈 웹게임'으로 브라우저 단독 탑재합니다."
        )
    elif category_key == 'quant':
        return (
            f"💡 [제2원 개조안] '{name}'의 기술적 분석 알고리즘 중 유용한 보조지표를 KIS/NVDA 트레이딩 모듈에 이식하여, "
            f"매일 아침 텔레그램 사령탑 브리핑 시 '오늘의 지표 매매 신호' 항목으로 간결하게 추가 보고합니다."
        )
    else:
        return (
            f"💡 [제2원 개조안] '{name}'의 백그라운드 태스크 관리 방식을 우리 `run_dashboard.py` 및 클라우드 워크플로우에 접목하여, "
            f"노트북 전력 소모를 0에 가깝게 유지하면서 24시간 자율 감시 능력을 한 단계 격상시킵니다."
        )

def generate_adaptation_plan_with_gemini(repo: dict, category_key: str, gemini_caller) -> str:
    """제2원(공존개발팀) Gemini 1.5 Flash를 통한 우리 제국 100% 맞춤 흡수 설계"""
    if not gemini_caller:
        return build_default_adaptation_plan(repo, category_key)

    cat_info = SCOUT_CATEGORIES.get(category_key, SCOUT_CATEGORIES['audio'])
    repo_name = repo.get('full_name', '')
    desc = repo.get('description', '')
    lic_badge = repo.get('license', {}).get('badge', '')

    prompt = (
        f"당신은 '한걸음씩 AI 제국'의 제2원(미래지향·공존개발팀장) 수석 아키텍트입니다.\n"
        f"우리는 전 세계 GitHub 선구자들의 훌륭한 오픈소스 도구를 답사하여, 우리 제국에 맞게 지혜롭게 개조·흡수하고자 합니다.\n\n"
        f"[답사한 오픈소스 정보]\n"
        f"• 저장소: {repo_name}\n"
        f"• 설명: {desc}\n"
        f"• 라이선스: {lic_badge}\n"
        f"• 탐사 분야: {cat_info['name']} (제국 포커스: {cat_info['focus']})\n\n"
        f"[우리 제국의 현재 인프라]\n"
        f"1. 8시간 수면·명상 음악(FFmpeg 초경량 루프, Suno 음원 창고 30곡, 노트북 저전력 가동)\n"
        f"2. 세 딸(이은솔 중3 수석 자문위원, 이송효 중1 선임 자문위원, 이해상 초5 주니어 자문위원)을 위한 올바른 AI 인성학교 & 수료 인증원\n"
        f"3. NVDA 퀀트 트레이딩 분석 & 텔레그램 모바일 원격 관제\n"
        f"4. 8대 부처 통합 사령부(Omni-Nexus) 웹 대시보드\n\n"
        f"[지시사항]\n"
        f"이 오픈소스 기술을 우리 시스템에 어떻게 '맞춤 개조 및 흡수'하면 가장 큰 시너지가 날지,\n"
        f"대표님께 올리는 보고 형식으로 2~3문장의 구체적이고 실현 가능한 [제국 맞춤 개조·흡수 설계안]을 작성해 주세요.\n"
        f"반드시 친절하고 활기찬 한국어로 작성해 주세요."
    )

    try:
        res = gemini_caller(prompt)
        if res and len(res.strip()) > 10:
            return res.strip()
    except Exception:
        pass

    return build_default_adaptation_plan(repo, category_key)

def get_rea_deep_dive_analysis(gemini_caller=None) -> dict:
    """
    🔥 [제2원 특임대 1순위 전략 자산]
    REA (Reverse Engineer Anything - github.com/morluto/rea / rea.tools)
    전 세계 화제(Star 16만~25만 돌파)의 5단계 에이전트 역설계 스킬 & MCP 아키텍처 정밀 분석
    """
    rea_meta = {
        "repo_name": "morluto/rea",
        "title": "REA (Reverse Engineer Anything)",
        "stars": "210,000+",
        "html_url": "https://github.com/morluto/rea",
        "web_url": "https://rea.tools",
        "license_badge": "🟢 안전 (MIT License - 상업적 자유 이용 가능)",
        "summary": "어떤 웹앱, UI, 비즈니스 로직, 오디오 비주얼라이저도 5단계 에이전트 스킬로 분해·역설계하여 완벽한 아키텍처 명세로 환원하는 전 세계 최고 화제의 역공학 프레임워크.",
        "skills_5step": [
            {
                "step": "1단계: 입출력 블랙박스 관찰 (Black-box Observation)",
                "desc": "서비스의 사용자 인터랙션, 네트워크 페이로드, DOM 트리 변형을 실시간 캡처하여 전체 시스템 경계와 입출력 명세 확정."
            },
            {
                "step": "2단계: UI 컴포넌트 계층 트리 분해 (Component Deconstruction)",
                "desc": "시각적 레이아웃을 컨테이너, 레이어, 마이크로 인터랙션 단위로 원자화하여 Vanilla CSS/Canvas 그리드로 매핑."
            },
            {
                "step": "3단계: 상태 흐름 및 반응성 모델링 (State & Flow Modeling)",
                "desc": "이벤트 리스너, 로컬 스토리지, 세션 라이프사이클의 데이터 흐름도를 추출해 무상태(Stateless) 아키텍처로 정위."
            },
            {
                "step": "4단계: 핵심 알고리즘 & 수학 공식 연역 (Algorithmic Deduction)",
                "desc": "비주얼 파티클 수식, 오디오 FFT 주파수 맵, 렌더링 최적화 루프를 순수 수학 공식으로 순수 환원."
            },
            {
                "step": "5단계: 제1원 클린룸 독립 재창조 (Cleanroom Rebuilding)",
                "desc": "외부 원본 코드는 단 1줄도 복제하지 않고, 연역된 공식과 명세만을 바탕으로 우리 제국 스택(Vanilla JS/Python/FFmpeg)으로 100% 독창적 재작성."
            }
        ],
        "strategies_3pillars": [
            {
                "target": "🎓 세 딸(이은솔·이송효·이해상) 인성학교 웹게임 고도화",
                "focus": "인기 웹 미니게임 반응 구조 역설계",
                "detail": "상용 게임들의 실시간 피드백 루프(파티클 축하 효과, 사운드 타이밍, 감정 점수 증감)를 역설계하여, 〈마음 편의점〉 및 인성 밸런스 게임을 상용 인디게임급의 재미와 몰입감으로 업그레이드!"
            },
            {
                "target": "📈 NVDA & 금융 상황판 초고속 최적화",
                "focus": "글로벌 핀테크 가상 스크롤 & 고속 차팅 벤치마킹",
                "detail": "TradingView 등 글로벌 금융 사이트의 DOM 가상화 및 백그라운드 캔버스 차트 렌더링 기법을 분석해, 사령부 대시보드의 데이터 갱신 속도를 0.01초(무부하)로 극대화!"
            },
            {
                "target": "🎵 힐링 오디오·비주얼라이저 파티클 이식",
                "focus": "해외 앰비언트 웹앱 캔버스 물리 이펙트 수식 추출",
                "detail": "해외 최고 인기 수면·휴식 웹앱의 빗방울, 모닥불 불티, 파도 물결 파티클 물리 공식을 연역 추출하여, 우리 썸네일 캔버스와 8시간 힐링 영상 렌더링 엔진에 초경량 이식!"
            }
        ],
        "legal_guideline": "🛡️ [제1원 자율법무팀 무결점 원칙]: 원본 소스코드 직접 복사(Copy-Paste) 원천 금지! 오직 '원리와 수식'만 학습한 뒤 우리 고유의 코드로 100% 클린룸 재창조하여 저작권 리스크 0%를 확립합니다."
    }

    ai_briefing = None
    if gemini_caller:
        prompt = (
            f"당신은 '한걸음씩 AI 제국'의 제2원(글로벌 오픈소스 탐사단장) 수석 아키텍트입니다.\n"
            f"지금 전 세계 GitHub와 유튜브를 뜨겁게 달구고 있는 초특급 오픈소스 'REA (Reverse Engineer Anything - morluto/rea)'를 제국 제1호 핵심 기술로 분석했습니다.\n\n"
            f"[기술 개요]\n"
            f"• 저장소: {rea_meta['repo_name']} (Star {rea_meta['stars']}, MIT 라이선스)\n"
            f"• 핵심: 5단계 에이전트 역설계 스킬 & 클린룸 재창조\n"
            f"• 3대 적용 분야: 세 딸(이은솔·이송효·이해상) 인성학교 웹게임 고도화, NVDA/금융 초고속 상황판 최적화, 힐링 오디오/파티클 비주얼라이저 이식\n"
            f"• 제1원 준법 원칙: 외부 코드 복제 제로, 원리 학습 후 100% 우리만의 독창적 코드로 재창조\n\n"
            f"이상일 대표님께 이 혁신 기술을 보고하는 형식으로, 우리 제국에 가져올 엄청난 시너지와 각오를 2~3문장의 명쾌하고 웅장하며 즐거운 한국어로 브리핑해 주세요!"
        )
        try:
            ai_briefing = gemini_caller(prompt)
        except Exception:
            pass

    rea_meta["ai_briefing"] = ai_briefing or (
        "🚀 이상일 대표님! 전 세계 개발자들을 열광시킨 REA의 '5단계 클린룸 역설계 기법'을 전격 확보했습니다! "
        "제1원 자율법무팀의 철통 보안 아래 외부 코드는 단 한 줄도 베끼지 않고 오직 정밀한 원리와 수학 공식만을 흡수하여, "
        "우리 세 딸(이은솔·이송효·이해상) 인성학교 웹게임과 사령부 퀀트 엔진, 8시간 힐링 파티클 비주얼라이저를 세계 최고 수준으로 즉시 도약시키겠습니다!"
    )

    return {
        "success": True,
        "rea": rea_meta
    }

# 3대 GitHub 슈퍼 트렌드 사전 정의 데이터
SUPER_TREND_PRESETS = {
    'artcraft': {
        'id': 'artcraft',
        'badge': '🔥 쇼츠 #1 (J8Wz2fQ39Rk)',
        'title': 'ArtCraft (storytold/photocraft) — Rust 기반 무료 포토샵·프리미어·모션그래픽 13종 통합 스위트',
        'repo_name': 'storytold/photocraft',
        'youtube_url': 'https://youtu.be/J8Wz2fQ39Rk',
        'stars': '38,500+',
        'license_badge': '🟢 안전 (MIT / Apache 2.0 라이선스)',
        'summary': '어도비(Adobe) 월 정액 구독료를 0원으로 만드는 Rust/WebAssembly 기반 초경량 크리에이티브 13종 스위트. 레이어 편집, 비디오 컷편집, 이펙트 모션을 단일 엔진에서 지원.',
        'key_features': [
            'Rust 언어 기반 고성능 메모리 안전성 및 CPU 무부하 그래픽 처리',
            '포토샵(PSD), 프리미어(비디오 시퀀스), 모션 이펙트 13대 도구 무료 통합',
            'WebAssembly(Wasm) 브라우저 무설치 구동 및 로컬 네이티브 빌드 동시 지원'
        ],
        'empire_absorption': [
            '🎨 [비주얼 스튜디오 연동]: 썸네일 캔버스에 ArtCraft의 Rust 블렌딩 모드 수식을 접목해 포토샵 수준의 고급 필터 효과 구현',
            '🎬 [8시간 렌더러 최적화]: FFmpeg -c copy 연결 전후 타이틀 모션 생성에 접목해 노트북 발열/소음 0dB 보장',
            '💰 [비용 절감 & 프라이버시]: 어도비 유료 구독 없이 100% 독립 로컬 작업 환경 구축'
        ],
        'default_briefing': '👑 이상일 대표님! 유튜브 쇼츠 #1에서 발굴된 ArtCraft는 어도비 13종 프로그램을 완벽 대체하는 괴물급 오픈소스입니다! 우리 힐링 비주얼 캔버스와 8시간 렌더러에 이식하여 구독료 0원, CPU 0%의 최강 미디어 제국을 완성하겠습니다!'
    },
    'ai10': {
        'id': 'ai10',
        'badge': '🏆 쇼츠 #2 (_zuysTgqoF0)',
        'title': '2026 GitHub AI 10선 (민둥이 @Mindung-EasyAI 발굴: Karpathy Skills · MemPalace · Hermes · MS Qlib)',
        'repo_name': 'Mindung-EasyAI/Top10-OpenSource-AI-2026',
        'youtube_url': 'https://youtube.com/shorts/_zuysTgqoF0',
        'stars': '합계 180,000+',
        'license_badge': '🟢 안전 (MIT License 전원 준수)',
        'summary': '2026년 GitHub에서 가장 뜨겁게 폭발한 10대 AI 오픈소스 정수. 안드레이 카파시의 초경량 스킬셋부터 자가학습 에이전트, 뇌 모방 장기 기억, 퀀트 투자까지 총망라.',
        'key_features': [
            'Karpathy Skills (llm.c): 외부 라이브러리 의존성 없는 초경량 C/Python AI 구현의 극치',
            'MemPalace: 인간 기억의 궁전 기법을 모방한 에이전트 영구 장기 기억 보존 기술',
            'Hermes-Agent: 실수 발생 시 스스로 지침을 개정하여 오답을 극복하는 자율 진화 엔진',
            'MS Qlib: 인공지능 기반 주식 퀀트 팩터 발굴 및 고속 백테스팅 프레임워크 (NVDA 분석 최적)'
        ],
        'empire_absorption': [
            '🧠 [안실장 기억 궁전]: 우리 memory_vault.json을 MemPalace 인덱싱 구조로 고도화하여 영구 맥락 기억 보장',
            '🛡️ [지혜실록 자율 백신]: Hermes의 자가교정 알고리즘을 wisdom_ledger.json에 연동하여 실수 원천 차단',
            '📈 [NVDA 퀀트 정밀화]: MS Qlib의 모멘텀/변동성 팩터를 사령부 퀀트 엔진에 이식해 승률 극대화'
        ],
        'default_briefing': '👑 이상일 대표님! 민둥이 쇼츠(_zuysTgqoF0)가 엄선한 2026 GitHub 10선은 우리 제국 시스템에 딱 들어맞는 퍼즐 조각입니다! Karpathy의 경량 철학과 MemPalace의 장기기억, MS Qlib 퀀트를 우리 안실장 두뇌와 NVDA 엔진에 즉시 흡수하겠습니다!'
    },
    'manim': {
        'id': 'manim',
        'badge': '🎬 모션 그래픽 TOP 1',
        'title': 'Manim (3b1b/manim ⭐95.1k) & Motion Canvas (⭐15k) & iart-ai/motion-skills',
        'repo_name': '3b1b/manim',
        'youtube_url': 'https://github.com/3b1b/manim',
        'stars': '95,100+ (MIT)',
        'license_badge': '🟢 안전 (MIT License)',
        'summary': '유튜브 3Blue1Brown이 탄생시킨 전 세계 최고 명성의 프로그래머블 수학·과학 모션 그래픽 엔진 Manim과 브라우저 네이티브 60fps 절차적 애니메이션 툴킷 Motion Canvas.',
        'key_features': [
            '정밀한 수학적 곡선, 베지어 패스, 벡터 필드, 스펙트럼 파동의 절차적 렌더링',
            'Web Canvas / WebGL 60fps 부드러운 하드웨어 가속 인터랙션 지원',
            '글자 하나하나가 살아 숨쉬는 한글 세로 명조체 텍스트 애니메이션 및 나침반 레이더 시각화'
        ],
        'empire_absorption': [
            '🎹 [비주얼 캔버스 60fps LIVE]: 432Hz 황금 오디오 스펙트럼 파형과 시집 세로 명조체 타이핑 모션을 60fps 캔버스에 실시간 구현',
            '🧭 [인성학교 4Q 나침반]: Manim 스타일의 기하학적 네온 펄스 레이더 차트로 4대 덕목(경우·공경·공감·나눔)을 수학적 아름다움으로 표현',
            '📜 [디지털 수료증 특수 효과]: 골드 엠블럼 회전과 빛살 굴절 모션으로 글로벌 위상을 시각적으로 압도'
        ],
        'default_briefing': '👑 이상일 대표님! 9.5만 스타의 전설 Manim과 Motion Canvas 기술을 우리 대시보드 캔버스에 전격 장착했습니다! 432Hz 오디오 파형이 60fps로 요동치고, 대표님의 따뜻한 시구가 한 글자씩 살아 숨쉬며 화면을 채웁니다!'
    }
}

def get_super_trend_preset_analysis(preset_id: str, gemini_caller=None) -> dict:
    """3대 슈퍼 트렌드 프리셋 정밀 분석 데이터 및 Gemini 실시간 브리핑 반환"""
    preset = SUPER_TREND_PRESETS.get(preset_id)
    if not preset:
        preset = SUPER_TREND_PRESETS['artcraft']

    briefing = preset['default_briefing']
    if gemini_caller:
        prompt = (
            f"당신은 '한걸음씩 AI 제국'의 제2원(글로벌 오픈소스 탐사단장) 수석 아키텍트입니다.\n"
            f"리더이신 이상일 대표님께 다음 슈퍼 트렌드 오픈소스에 대한 정밀 분석과 제국 무기화 전략을 보고하십시오.\n\n"
            f"[오픈소스 정보]\n"
            f"• 제목: {preset['title']}\n"
            f"• 배지: {preset['badge']}\n"
            f"• 저장소: {preset['repo_name']} (Star: {preset['stars']})\n"
            f"• 핵심 요약: {preset['summary']}\n"
            f"• 제국 흡수 전략: {', '.join(preset['empire_absorption'])}\n\n"
            f"이상일 대표님과 세 따님(이은솔 수석 자문위원, 이송효 선임 자문위원, 이해상 주니어 자문위원)을 모시는 깍듯하고 유쾌하며 자신감 넘치는 어조로 2~3문장의 브리핑을 작성해 주세요."
        )
        try:
            res = gemini_caller(prompt)
            if res and len(res.strip()) > 10:
                briefing = res.strip()
        except Exception:
            pass

    return {
        'success': True,
        'preset': {
            **preset,
            'ai_briefing': briefing
        }
    }

def run_daily_cloud_scout(out_dir: str = "./cloud_output") -> str:
    """클라우드 일일 자동 답사: 매일 요일별 카테고리 1선 탐사 및 마크다운 리포트 생성"""
    dow = datetime.now().weekday()
    cat_keys = ['audio', 'education', 'quant', 'agent']
    today_cat = cat_keys[dow % len(cat_keys)]

    res = scout_github_repositories(today_cat, limit=1)
    if not res.get('success') or not res.get('repositories'):
        return f"⚠️ 오늘의 오픈소스 탐사 실패: {res.get('error', '결과 없음')}"

    repo = res['repositories'][0]
    cat_info = SCOUT_CATEGORIES[today_cat]
    plan = build_default_adaptation_plan(repo, today_cat)

    md = (
        f"### 🔭 [제2원 특임대] 오늘의 글로벌 오픈소스 답사 1선\n"
        f"• **분야**: {cat_info['name']}\n"
        f"• **보물 저장소**: [{repo['full_name']}]({repo['html_url']}) (★{repo['stars']:,})\n"
        f"• **라이선스**: {repo['license']['badge']}\n"
        f"• **설명**: {repo['description']}\n\n"
        f"{plan}\n"
    )

    try:
        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        (out_path / "daily_scout_report.md").write_text(md, encoding="utf-8")
    except Exception:
        pass

    return md

if __name__ == '__main__':
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if '--daily' in sys.argv:
        report = run_daily_cloud_scout()
        print(report)
    else:
        print("🔭 [제2원: 글로벌 오픈소스 탐사 & 흡수단] 테스트 가동")
        res = scout_github_repositories('quant', limit=2)
        print(f"성공 여부: {res['success']}, 총 검색수: {res.get('total_count')}")
        for r in res.get('repositories', []):
            plan = build_default_adaptation_plan(r, 'quant')
            print(f"\n[{r['full_name']}] ★{r['stars']} | {r['license']['badge']}")
            print(f"설명: {r['description']}")
            print(plan)


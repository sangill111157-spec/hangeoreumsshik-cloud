# -*- coding: utf-8 -*-
"""
🔭 한걸음씩 AI 제국 : 제2원(미래지향·공존개발팀)
〈글로벌 오픈소스 탐사 & 흡수단 (GitHub Daily Scout & Adapter)〉
선구자들의 오픈소스(GitHub)를 실시간 답사하고 라이선스 안전성을 검증하여,
우리 제국(8H 수면 음악 / 세 딸 인성학교 / 퀀트·NVDA / 경량 사령부)에 맞게 개조·흡수하는 엔진
"""

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
        'focus': '수아·윤아·서아를 위한 웹 캔버스 인성 퀴즈, 대화형 도덕/예절 게임, 브라우저 로컬 구동'
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
            f"우리 대시보드 4번 탭(AI 인성학교)에 세 딸(수아·윤아·서아) 전용 '오늘의 미덕 실천 퀴즈 웹게임'으로 브라우저 단독 탑재합니다."
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
        f"2. 세 딸(수아 중3, 윤아 중1, 서아 초5)을 위한 올바른 AI 인성학교 & 수료 인증원\n"
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


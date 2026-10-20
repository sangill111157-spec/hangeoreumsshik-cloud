# -*- coding: utf-8 -*-
"""
sync_blog_to_sheet.py — BLOG AUTOMATION COMMAND CENTER 시트 구축 & 동기화
- Content_Pipeline 탭: 블로그 15편 초안/업로드/발행 현황
- Schedule 탭: 예약 발행 일정 캘린더
- SEO_Audit 탭: 포스트별 품질 점검 결과
- Daily_Work_Log 탭: 작업 이력 로깅
"""
import os, sys, pickle, json, re, glob
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# ── 경로 설정 ──
AUTO = Path(r'C:\Users\sangi\OneDrive\Desktop\hangeoreumsshik\automation')
CONFIG = AUTO / 'config'
TOKEN = CONFIG / 'token.pickle'
DRAFTS = AUTO / 'drafts'

BLOG_SHEET_ID = '1gYDrCuqM2hKQbYyE3cYEZhJZEhrH_Is6tdUhsw-cgaw'

# ── 블로그 콘텐츠 정의 (blogger_scheduler.py 기반) ──
CONTENT_MANIFEST = [
    {"id": "HEALTH_01", "title": "만성피로와 뱃살, 3교대 직장인 식습관 3개월 기록", "category": "건강", "schedule": "2026-07-21"},
    {"id": "HEALTH_02", "title": "허리둘레 36→32, 몸무게 75→68kg — 무엇을 바꿨나", "category": "건강", "schedule": "2026-07-22"},
    {"id": "HEALTH_03", "title": "변비·속쓰림·더부룩함·가스참, 소화 이야기", "category": "건강", "schedule": "2026-07-23"},
    {"id": "HEALTH_04", "title": "교대근무자의 무너진 식사 리듬, 되돌린 방법", "category": "식습관", "schedule": "2026-07-24"},
    {"id": "HEALTH_05", "title": "피부 트러블·비염·발뒤꿈치 각질 — 몸이 보낸 신호", "category": "건강", "schedule": "2026-07-25"},
    {"id": "HEALTH_06", "title": "교대근무자의 수면 관리 — 야간 근무 후 잘 자는 법", "category": "건강", "schedule": "2026-07-26"},
    {"id": "HEALTH_07", "title": "에너지드링크·믹스커피를 줄인 경험과 그 후 변화", "category": "건강", "schedule": "2026-07-28"},
    {"id": "HEALTH_08", "title": "교대근무자가 챙겨 먹기 좋은 간단한 도시락·간식", "category": "식습관", "schedule": "2026-07-29"},
    {"id": "HEALTH_09", "title": "3교대 하면서 병원·건강검진 챙기는 현실적인 방법", "category": "건강", "schedule": "2026-07-31"},
    {"id": "HEALTH_10", "title": "불규칙한 생활 속 스트레스 관리법", "category": "건강", "schedule": "2026-08-01"},
    {"id": "HEALTH_11", "title": "걷기를 습관으로 만든 방법과 3교대 속 실천 팁", "category": "건강", "schedule": "2026-08-03"},
    {"id": "HEALTH_12", "title": "물 많이 마시기, 나만의 루틴 만들기", "category": "건강", "schedule": "2026-08-04"},
    {"id": "HEALTH_13", "title": "3교대 야간근무 전·중·후 식단 루틴", "category": "식습관", "schedule": "2026-08-28"},
    {"id": "HEALTH_14", "title": "3교대 교대근무자를 위한 필수 영양제 조합", "category": "건강", "schedule": "2026-08-29"},
    {"id": "HEALTH_15", "title": "3교대 야간근무 속 감정기복과 무기력 극복법", "category": "건강", "schedule": "2026-08-30"},
    {"id": "WORK_01", "title": "야간·휴일 근로수당 계산 실전 가이드", "category": "노무", "schedule": "2026-08-25"},
    {"id": "WORK_02", "title": "3교대 직장인의 연차 휴가 알차게 쓰는 법", "category": "노무", "schedule": "2026-08-31"},
    {"id": "RETECH_01", "title": "3교대 직장인이 주식(장기 투자)을 시작한 이유", "category": "재테크", "schedule": "2026-07-27"},
    {"id": "RETECH_02", "title": "매일 시세를 못 보는 직장인의 장기 투자 관리 방법", "category": "재테크", "schedule": "2026-07-30"},
    {"id": "RETECH_03", "title": "초보 때 저지른 실수와 거기서 배운 것", "category": "재테크", "schedule": "2026-08-02"},
    {"id": "RETECH_04", "title": "3교대 직장인의 통장 쪼개기와 1,000만 원 비상금 루틴", "category": "재테크", "schedule": "2026-09-01"},
]

# 추가 콘텐츠 (정책 페이지 + AI 파이프라인 글)
EXTRA_CONTENT = [
    {"id": "PAGE_소개", "title": "소개 (About)", "category": "페이지", "schedule": "-"},
    {"id": "PAGE_개인정보", "title": "개인정보처리방침 (Privacy Policy)", "category": "페이지", "schedule": "-"},
    {"id": "PAGE_연락처", "title": "연락처 (Contact)", "category": "페이지", "schedule": "-"},
    {"id": "FINAL_AI자동화", "title": "AI 자동화로 1인기업 블로그 파이프라인 구축", "category": "기술", "schedule": "2026-07-17"},
]


def get_sheets_service():
    with open(TOKEN, 'rb') as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN, 'wb') as f:
            pickle.dump(creds, f)
    return build('sheets', 'v4', credentials=creds).spreadsheets()


def scan_drafts():
    """drafts/ 폴더의 .md 파일 존재 여부를 스캔하여 초안 완료 상태 반환"""
    draft_files = {}
    if DRAFTS.exists():
        for md_file in DRAFTS.glob("*.md"):
            name = md_file.stem
            size = md_file.stat().st_size
            draft_files[name] = {
                "exists": True,
                "size": size,
                "modified": datetime.fromtimestamp(md_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            }
    return draft_files


def get_blogger_status():
    """Blogger API로 포스트 상태 조회 (토큰 유효 시)"""
    SECRETS_DIR = Path(r'C:\Users\sangi\.connectai\secrets')
    try:
        from google.oauth2.credentials import Credentials
        blog_token = SECRETS_DIR / 'token.json'
        blog_creds = Credentials.from_authorized_user_file(
            str(blog_token), ['https://www.googleapis.com/auth/blogger']
        )
        if blog_creds.expired and blog_creds.refresh_token:
            blog_creds.refresh(Request())
        
        blogger = build('blogger', 'v3', credentials=blog_creds)
        BLOG_ID = '5189765270915724664'
        
        posts_map = {}
        for status in ['LIVE', 'SCHEDULED', 'DRAFT']:
            try:
                result = blogger.posts().list(blogId=BLOG_ID, status=[status], maxResults=50).execute()
                for p in result.get('items', []):
                    posts_map[p.get('title', '')] = {
                        "status": status,
                        "published": p.get('published', '')[:16],
                        "url": p.get('url', ''),
                        "labels": p.get('labels', [])
                    }
            except:
                pass
        return posts_map, None
    except Exception as e:
        return {}, str(e)


def ensure_tab_exists(sheets, tab_name, headers):
    """탭이 없으면 생성하고 헤더를 설정"""
    meta = sheets.get(spreadsheetId=BLOG_SHEET_ID).execute()
    existing_tabs = [s['properties']['title'] for s in meta['sheets']]
    
    if tab_name not in existing_tabs:
        sheets.batchUpdate(spreadsheetId=BLOG_SHEET_ID, body={
            "requests": [{"addSheet": {"properties": {"title": tab_name}}}]
        }).execute()
        print(f"  ✅ '{tab_name}' 탭 생성 완료")
    
    # 헤더 설정
    sheets.values().update(
        spreadsheetId=BLOG_SHEET_ID,
        range=f"'{tab_name}'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": [headers]}
    ).execute()


def setup_and_sync():
    """메인 실행: 시트 구축 + 데이터 동기화"""
    print("=" * 70)
    print(f"📋 BLOG AUTOMATION COMMAND CENTER 구축 & 동기화")
    print(f"   시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    sheets = get_sheets_service()
    
    # ── 기존 '시트1' 탭 정리 (Dashboard로 리네임) ──
    print("\n[1/5] 📊 Dashboard 탭 구축...")
    meta = sheets.get(spreadsheetId=BLOG_SHEET_ID).execute()
    existing_tabs = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    
    if '시트1' in existing_tabs and 'Dashboard' not in existing_tabs:
        sheets.batchUpdate(spreadsheetId=BLOG_SHEET_ID, body={
            "requests": [{
                "updateSheetProperties": {
                    "properties": {"sheetId": existing_tabs['시트1'], "title": "Dashboard"},
                    "fields": "title"
                }
            }]
        }).execute()
        print("  ✅ '시트1' → 'Dashboard'로 리네임")
    
    # Dashboard 내용 작성
    dashboard_data = [
        ["📋 BLOG AUTOMATION COMMAND CENTER", "", "", "", "", ""],
        ["", "", "", "", "", ""],
        ["항목", "값", "상세", "", "", ""],
        ["블로그 URL", "https://connect-ai-shin.blogspot.com", "", "", "", ""],
        ["블로그 ID", "5189765270915724664", "", "", "", ""],
        ["총 콘텐츠", f"{len(CONTENT_MANIFEST) + len(EXTRA_CONTENT)}편", f"건강 {sum(1 for c in CONTENT_MANIFEST if c['category']=='건강')} + 식습관 {sum(1 for c in CONTENT_MANIFEST if c['category']=='식습관')} + 재테크 {sum(1 for c in CONTENT_MANIFEST if c['category']=='재테크')} + 기타 {len(EXTRA_CONTENT)}", "", "", ""],
        ["파이프라인 모듈", "", "", "", "", ""],
        ["  D-0", "blogger_write_test.py", "Blogger 쓰기 권한 검증", "", "", ""],
        ["  D-1", "draft_writer.py", "Ollama LLM 기반 초안 생성", "", "", ""],
        ["  D-2", "blogger_upload.py", "검수 완료 → Blogger Draft 업로드", "", "", ""],
        ["  D-3", "blogger_scheduler.py", "예약 발행 일정 관리", "", "", ""],
        ["  D-4", "blogger_health_uploader.py", "건강 카테고리 일괄 업로드", "", "", ""],
        ["  D-5", "audit_blog_gate.py", "전수 검증 (면책문구/금칙표현/이미지)", "", "", ""],
        ["", "", "", "", "", ""],
        ["마지막 동기화", datetime.now().strftime("%Y-%m-%d %H:%M"), "sync_blog_to_sheet.py", "", "", ""],
    ]
    
    try:
        sheets.values().update(
            spreadsheetId=BLOG_SHEET_ID,
            range="'Dashboard'!A1",
            valueInputOption="USER_ENTERED",
            body={"values": dashboard_data}
        ).execute()
    except:
        sheets.values().update(
            spreadsheetId=BLOG_SHEET_ID,
            range="'시트1'!A1",
            valueInputOption="USER_ENTERED",
            body={"values": dashboard_data}
        ).execute()
    print("  ✅ Dashboard 데이터 작성 완료")
    
    # ── Content_Pipeline 탭 ──
    print("\n[2/5] 📝 Content_Pipeline 탭 구축...")
    pipeline_headers = ["#", "ID", "제목", "카테고리", "초안상태", "초안크기(B)", "수정일", "업로드상태", "예약일", "발행상태", "블로그URL"]
    ensure_tab_exists(sheets, "Content_Pipeline", pipeline_headers)
    
    # 초안 스캔
    draft_files = scan_drafts()
    print(f"  📂 drafts/ 폴더 스캔: {len(draft_files)}개 파일 발견")
    
    # Blogger 상태 조회
    blogger_posts, blogger_err = get_blogger_status()
    if blogger_err:
        print(f"  ⚠️ Blogger API 토큰 만료 — 초안 폴더 기반으로만 동기화")
    else:
        print(f"  📝 Blogger API: {len(blogger_posts)}개 포스트 감지")
    
    # 데이터 구성
    all_content = CONTENT_MANIFEST + EXTRA_CONTENT
    pipeline_rows = []
    
    for idx, item in enumerate(all_content, 1):
        cid = item["id"]
        title = item["title"]
        category = item["category"]
        schedule = item["schedule"]
        
        # 초안 상태 확인
        draft_status = "❌ 미작성"
        draft_size = ""
        draft_modified = ""
        
        for fname, finfo in draft_files.items():
            if cid in fname or cid.replace("_", "") in fname.replace("_", ""):
                draft_status = "✅ 완료"
                draft_size = str(finfo["size"])
                draft_modified = finfo["modified"]
                break
        
        # Blogger 발행 상태
        upload_status = "—"
        publish_status = "—"
        blog_url = ""
        
        for btitle, binfo in blogger_posts.items():
            title_words = title[:10]
            if title_words in btitle or btitle[:10] in title:
                if binfo["status"] == "DRAFT":
                    upload_status = "📤 업로드됨(임시)"
                    publish_status = "임시저장"
                elif binfo["status"] == "SCHEDULED":
                    upload_status = "📤 업로드됨"
                    publish_status = f"🕐 예약({binfo['published'][:10]})"
                elif binfo["status"] == "LIVE":
                    upload_status = "📤 업로드됨"
                    publish_status = "✅ 발행완료"
                blog_url = binfo.get("url", "")
                break
        
        # 예약일 기반 추정 (Blogger API 불가 시)
        if blogger_err and schedule != "-":
            try:
                sched_date = datetime.strptime(schedule, "%Y-%m-%d")
                if sched_date < datetime.now():
                    publish_status = "✅ 발행완료 (추정)"
                    upload_status = "📤 업로드됨 (추정)"
                else:
                    publish_status = f"🕐 예약({schedule})"
            except:
                pass
        
        pipeline_rows.append([
            str(idx), cid, title, category,
            draft_status, draft_size, draft_modified,
            upload_status, schedule, publish_status, blog_url
        ])
    
    sheets.values().update(
        spreadsheetId=BLOG_SHEET_ID,
        range="'Content_Pipeline'!A2",
        valueInputOption="USER_ENTERED",
        body={"values": pipeline_rows}
    ).execute()
    print(f"  ✅ Content_Pipeline: {len(pipeline_rows)}행 동기화 완료")
    
    # ── Schedule 탭 ──
    print("\n[3/5] 📅 Schedule 탭 구축...")
    schedule_headers = ["예약일", "요일", "제목", "카테고리", "상태"]
    ensure_tab_exists(sheets, "Schedule", schedule_headers)
    
    scheduled = sorted(
        [c for c in all_content if c["schedule"] != "-"],
        key=lambda x: x["schedule"]
    )
    
    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"]
    schedule_rows = []
    for item in scheduled:
        try:
            d = datetime.strptime(item["schedule"], "%Y-%m-%d")
            wd = weekday_kr[d.weekday()]
            is_past = d < datetime.now()
            status = "✅ 발행완료" if is_past else "🕐 대기"
        except:
            wd = "-"
            status = "-"
        schedule_rows.append([item["schedule"], wd, item["title"], item["category"], status])
    
    sheets.values().update(
        spreadsheetId=BLOG_SHEET_ID,
        range="'Schedule'!A2",
        valueInputOption="USER_ENTERED",
        body={"values": schedule_rows}
    ).execute()
    print(f"  ✅ Schedule: {len(schedule_rows)}행 동기화 완료")
    
    # ── SEO_Audit 탭 ──
    print("\n[4/5] 🔍 SEO_Audit 탭 구축...")
    audit_headers = ["#", "제목", "카테고리", "면책문구", "금칙표현", "이미지상태", "점검일"]
    ensure_tab_exists(sheets, "SEO_Audit", audit_headers)
    
    health_disclaimer_kw = ["의학적", "전문가", "참고", "개인 경험", "의사와 상의", "책임지지 않"]
    invest_disclaimer_kw = ["투자 권유가 아님", "개인의 의견", "투자의 책임", "참고용"]
    forbidden_patterns = [
        r"(완치|치료되었|낫는다)",
        r"(약(을)? 끊|약 대신|약 복용 중단)",
        r"(삼성전자|현대차|테슬라|비트코인)",
        r"(원금 보장|수익률 \d+%|무조건 번다)",
    ]
    
    audit_rows = []
    for idx, item in enumerate(CONTENT_MANIFEST, 1):
        cid = item["id"]
        disclaimer_ok = "—"
        forbidden_ok = "—"
        
        for md_file in DRAFTS.glob("*.md"):
            if cid in md_file.stem:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                
                if item["category"] == "재테크":
                    has_disc = any(k in content for k in invest_disclaimer_kw)
                else:
                    has_disc = any(k in content for k in health_disclaimer_kw)
                disclaimer_ok = "✅ 있음" if has_disc else "⚠️ 누락"
                
                violations = []
                for pat in forbidden_patterns:
                    matches = re.findall(pat, content)
                    if matches:
                        violations.extend([str(m) if isinstance(m, str) else str(m[0]) for m in matches])
                forbidden_ok = "✅ 클린" if not violations else f"⚠️ {', '.join(violations[:3])}"
                break
        
        audit_rows.append([
            str(idx), item["title"], item["category"],
            disclaimer_ok, forbidden_ok, "—", datetime.now().strftime("%Y-%m-%d")
        ])
    
    sheets.values().update(
        spreadsheetId=BLOG_SHEET_ID,
        range="'SEO_Audit'!A2",
        valueInputOption="USER_ENTERED",
        body={"values": audit_rows}
    ).execute()
    print(f"  ✅ SEO_Audit: {len(audit_rows)}행 동기화 완료")
    
    # ── Daily_Work_Log 탭 ──
    print("\n[5/5] 📝 Daily_Work_Log 탭 구축...")
    log_headers = ["날짜", "시간", "실행자", "작업유형", "상세", "결과"]
    ensure_tab_exists(sheets, "Daily_Work_Log", log_headers)
    
    now = datetime.now()
    log_entry = [[
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M"),
        "안실장 자동화봇",
        "시트 초기 구축",
        f"Dashboard + Content_Pipeline({len(pipeline_rows)}편) + Schedule({len(schedule_rows)}편) + SEO_Audit({len(audit_rows)}편) 탭 생성 및 데이터 동기화",
        "✅ 완료"
    ]]
    
    sheets.values().append(
        spreadsheetId=BLOG_SHEET_ID,
        range="'Daily_Work_Log'!A:F",
        valueInputOption="USER_ENTERED",
        body={"values": log_entry}
    ).execute()
    print(f"  ✅ Daily_Work_Log: 작업 이력 기록 완료")
    
    # ── 완료 요약 ──
    print(f"\n{'=' * 70}")
    print(f"🎉 BLOG AUTOMATION COMMAND CENTER 구축 완료!")
    print(f"{'=' * 70}")
    print(f"  📊 Dashboard: 파이프라인 모듈 구조 정리")
    print(f"  📝 Content_Pipeline: {len(pipeline_rows)}편 콘텐츠 현황")
    print(f"  📅 Schedule: {len(schedule_rows)}편 발행 일정")
    print(f"  🔍 SEO_Audit: {len(audit_rows)}편 품질 점검")
    print(f"  📝 Daily_Work_Log: 작업 이력 로깅")
    if blogger_err:
        print(f"\n  ⚠️ Blogger API 토큰 만료 — 재인증 후 정확한 발행 상태 동기화 가능")
        print(f"     실행: python google_blogger_auth.py")
    print(f"\n  시트 URL: https://docs.google.com/spreadsheets/d/{BLOG_SHEET_ID}")


if __name__ == "__main__":
    setup_and_sync()

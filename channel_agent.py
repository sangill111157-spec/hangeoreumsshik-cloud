# ══════════════════════════════════════════════════════════════
#  한걸음씩 채널 매니저 에이전트 v1.0
#  channel_agent.py
#
#  사용법:
#    python channel_agent.py produce     # 다음 대기 에피소드 자동 생산
#    python channel_agent.py analytics   # 전체 EP 성과 수집 → 시트 기록
#    python channel_agent.py status      # 현황 대시보드 출력
#    python channel_agent.py strategy    # AI 전략 분석 + 제안
#    python channel_agent.py schedule    # 스케줄 점검 + 갭 경고
#    python channel_agent.py grade       # 등급 자동 부여 (S/A/B/C)
# ══════════════════════════════════════════════════════════════
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import sys, os, pickle, json, re, subprocess, time
from pathlib import Path
from datetime import datetime, timedelta
from google.auth.transport.requests import Request


# ══════════════════════════════════════════════════════════
#  텔레그램 알림 (Connect-AI 봇 연동)
# ══════════════════════════════════════════════════════════
import urllib.request, urllib.parse

def _load_telegram_config():
    """환경 변수 우선, 없을 시 Connect-AI의 telegram_setup.json에서 봇 토큰/Chat ID 로드"""
    env_token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    env_chat = os.getenv('TELEGRAM_CHAT_ID', '').strip()
    if env_token and env_chat:
        return env_token, env_chat

    tg_path = Path(r'C:\\Users\\sangi\\.connect-ai-brain\\_company\\_agents\\secretary\\tools\\telegram_setup.json')
    if tg_path.exists():
        try:
            cfg = json.loads(tg_path.read_text(encoding='utf-8'))
            return cfg.get('TELEGRAM_BOT_TOKEN', ''), cfg.get('TELEGRAM_CHAT_ID', '')
        except Exception:
            pass
    return '', ''

def send_telegram(message: str, silent: bool = False):
    """텔레그램으로 메시지 전송 (Connect-AI 봇 토큰 재활용)"""
    token, chat_id = _load_telegram_config()
    if not token or not chat_id:
        log("[WARN] 텔레그램 설정 없음 — 알림 건너뜀")
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML',
            'disable_notification': str(silent).lower(),
        }).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        log(f"[WARN] 텔레그램 전송 실패: {e}")
        return False


# ── 경로 설정 (크로스 플랫폼: Linux / Windows 지원) ──
AUTO   = Path(__file__).resolve().parent
TOKEN  = AUTO / 'config' / 'token.pickle'
SHEET_ID = '1mIu1vXu0luRSDNyjE-WkJaz91otX0OvgaBVrJj6rwnY'
PIPELINE_SCRIPT = AUTO / 'novak_master_pipeline.py'

from dotenv import load_dotenv
import os
if (AUTO / 'config' / '.env').exists():
    load_dotenv(AUTO / 'config' / '.env', override=True)
elif (AUTO / '.env').exists():
    load_dotenv(AUTO / '.env', override=True)
GEMINI_KEY = os.getenv('GEMINI_FREE_KEY', os.getenv('GEMINI_API_KEY'))

# ── 인증 ──
def get_creds():
    with open(TOKEN, 'rb') as f:
        creds = pickle.load(f)
    if not creds.valid:
        creds.refresh(Request())
        with open(TOKEN, 'wb') as f:
            pickle.dump(creds, f)
    return creds

def get_sheets():
    import gspread
    creds = get_creds()
    gc = gspread.authorize(creds)
    return gc.open_by_key(SHEET_ID)

def get_youtube():
    from googleapiclient.discovery import build
    creds = get_creds()
    return build('youtube', 'v3', credentials=creds)

def get_gemini():
    from google import genai
    return genai.Client(api_key=GEMINI_KEY)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

# ══════════════════════════════════════════════════════════════
#  1) PRODUCE - 다음 대기 에피소드 자동 생산
# ══════════════════════════════════════════════════════════════
def cmd_produce():
    log("PRODUCE: 시트에서 다음 대기 에피소드 읽는 중...")
    ss = get_sheets()
    pl = ss.worksheet('PIPELINE')
    all_rows = pl.get_all_values()
    header = all_rows[0]
    col = {h: i for i, h in enumerate(header)}

    target = None
    target_row = None
    for idx, row in enumerate(all_rows[1:], start=2):
        if row[col['상태']].strip() == '⏳대기':
            target = row
            target_row = idx
            break

    if not target:
        log("모든 에피소드가 완료되었습니다! PIPELINE 시트에 새 행을 추가하세요.")
        return

    ep       = target[col['EP']].strip()
    quote1   = target[col['명언1줄']].strip()
    quote2   = target[col['명언2줄']].strip()
    sub1     = target[col['후속1줄']].strip()
    sub2     = target[col['후속2줄']].strip()
    title    = target[col['제목']].strip()
    full_q   = target[col['전체명언']].strip()
    tone     = target[col['톤']].strip()
    publish  = target[col['공개일(UTC)']].strip()
    hook     = target[col['후킹문장']].strip() if '후킹문장' in col else title

    log(f"EP{ep} 발견: {quote1} {quote2}")
    log(f"  톤: {tone} | 공개: {publish}")
    log(f"  후킹: {hook}")

    # 상태 업데이트
    pl.update(values=[['🎬생성중']], range_name=f'B{target_row}')

    # 파이프라인 실행
    rule = target[col['편집규칙']].strip() if '편집규칙' in col else ''
    clips_count = 4
    if rule:
        if 'Clip4' not in rule and 'Clip3' not in rule and 'Clip2' in rule:
            clips_count = 2
            log("  -> 편집규칙 감지: 2컷 모드(16초)로 실행합니다.")
        elif 'Clip4' not in rule and 'Clip3' in rule:
            clips_count = 3
            log("  -> 편집규칙 감지: 3컷 모드(24초)로 실행합니다.")
        
    cmd = [
        sys.executable, str(PIPELINE_SCRIPT),
        '--ep', ep, '--quote1', quote1, '--quote2', quote2,
        '--sub1', sub1, '--sub2', sub2, '--title', title,
        '--hook', hook,
        '--full_quote', full_q, '--tone', tone, '--publish', publish,
        '--clips_count', str(clips_count),
        '--skip_upload'
    ]
    if '--skip_veo' in sys.argv:
        cmd.append('--skip_veo')
    
    # 커스텀 프롬프트가 시트에 기재되어 있으면 파이프라인 파라미터로 추가 전달
    if 'Clip1_Prompt' in col and target[col['Clip1_Prompt']].strip():
        cmd.extend(['--clip1_prompt', target[col['Clip1_Prompt']].strip()])
    if 'Clip2_Prompt' in col and target[col['Clip2_Prompt']].strip():
        cmd.extend(['--clip2_prompt', target[col['Clip2_Prompt']].strip()])
    if 'Clip3_Prompt' in col and target[col['Clip3_Prompt']].strip():
        cmd.extend(['--clip3_prompt', target[col['Clip3_Prompt']].strip()])
    if 'Clip4_Prompt' in col and target[col['Clip4_Prompt']].strip():
        cmd.extend(['--clip4_prompt', target[col['Clip4_Prompt']].strip()])

    log(f"파이프라인 실행 중...")
    result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace')
    print(result.stdout)

    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    if result.returncode != 0:
        err = (result.stderr or 'unknown')[-300:]
        log(f"[FAIL] EP{ep} 실패")
        # stdout에서 업로드 성공 여부 확인 (이모지 에러 등 마지막 단계 에러)
        vid_match = re.search(r'https://youtu\.be/([A-Za-z0-9_-]+)', result.stdout)
        if vid_match:
            log(f"  -> 업로드는 성공! (후처리 에러). 완료 처리합니다.")
            video_id = vid_match.group(1)
            video_url = vid_match.group(0)
            updates = [
                {'range': f'B{target_row}', 'values': [['✅완료']]},
                {'range': f'K{target_row}', 'values': [[video_id]]},
                {'range': f'L{target_row}', 'values': [[video_url]]},
                {'range': f'M{target_row}', 'values': [['.40']]},
                {'range': f'N{target_row}', 'values': [['PASS']]},
                {'range': f'O{target_row}', 'values': [[now]]},
                {'range': f'P{target_row}', 'values': [[f'후처리 에러(업로드 성공): {err[:100]}']]},
            ]
            pl.batch_update(updates)
            log(f"EP{ep} 완료! {video_url}")
            # 텔레그램 알림: 부분 성공
            send_telegram(
                f"⚠️ <b>EP{ep} 업로드 성공 (후처리 에러)</b>\n"
                f"📺 {video_url}\n"
                f"🔸 {err[:100]}\n"
                f"⏰ {now}"
            )
        else:
            updates = [
                {'range': f'B{target_row}', 'values': [['❌실패']]},
                {'range': f'O{target_row}', 'values': [[now]]},
                {'range': f'P{target_row}', 'values': [[err[:200]]]},
            ]
            pl.batch_update(updates)
            log(f"EP{ep} 실패. 시트에 에러 기록 완료.")
            # 텔레그램 알림: 실패
            send_telegram(
                f"❌ <b>EP{ep} 생산 실패!</b>\n"
                f"🔴 {err[:150]}\n"
                f"⏰ {now}"
            )
        return

    # 성공
    vid_match = re.search(r'https://youtu\.be/([A-Za-z0-9_-]+)', result.stdout)
    video_id = vid_match.group(1) if vid_match else ''
    video_url = vid_match.group(0) if vid_match else ''
    qc_pass = 'PASS' if 'PASS' in result.stdout else 'CHECK'

    updates = [
        {'range': f'B{target_row}', 'values': [['✅완료']]},
        {'range': f'K{target_row}', 'values': [[video_id]]},
        {'range': f'L{target_row}', 'values': [[video_url]]},
        {'range': f'M{target_row}', 'values': [['.40']]},
        {'range': f'N{target_row}', 'values': [[qc_pass]]},
        {'range': f'O{target_row}', 'values': [[now]]},
    ]
    pl.batch_update(updates)
    log(f"EP{ep} 완료! {video_url}")
    # 텔레그램 알림: 성공
    send_telegram(
        f"✅ <b>EP{ep} 생산 완료!</b>\n"
        f"📺 {video_url}\n"
        f"🎯 QC: {qc_pass} | ⏰ {now}"
    )

# ══════════════════════════════════════════════════════════════
#  2) ANALYTICS - YouTube 성과 수집
# ══════════════════════════════════════════════════════════════
def cmd_analytics():
    log("ANALYTICS: 3개 채널 실시간 트래픽 연동 스크립트 실행 중...")
    script_path = AUTO / "update_3channels_analytics.py"
    cmd = [sys.executable, str(script_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(result.stdout)
    if result.returncode != 0:
        log(f"[ERROR] 3채널 성과 수집 실패: {result.stderr}")
        raise RuntimeError(f"3채널 성과 수집 에러: {result.stderr}")
    log("ANALYTICS: 3채널 실시간 동기화 완료!")

# ══════════════════════════════════════════════════════════════
#  3) STATUS - 현황 대시보드 (YouTube API 실제 상태 교차검증)
# ══════════════════════════════════════════════════════════════
def cmd_status():
    log("STATUS: 채널 현황 로딩 중...")
    ss = get_sheets()
    pl = ss.worksheet('PIPELINE')
    all_rows = pl.get_all_values()
    header = all_rows[0]
    col = {h: i for i, h in enumerate(header)}

    done = []
    waiting = []
    failed = []
    producing = []

    for row in all_rows[1:]:
        status = row[col['상태']].strip()
        ep = row[col['EP']].strip()
        title = row[col['제목']].strip()
        pub = row[col['공개일(UTC)']].strip()
        vid = row[col['영상ID']].strip()
        url = row[col['URL']].strip()
        memo = row[col['메모']].strip() if '메모' in col else ''

        entry = {'ep': ep, 'title': title, 'pub': pub, 'vid': vid, 'url': url, 'memo': memo, 'status': status}

        if '완료' in status:
            done.append(entry)
        elif '대기' in status:
            waiting.append(entry)
        elif '실패' in status:
            failed.append(entry)
        else:
            producing.append(entry)

    # ── YouTube API로 실제 공개 상태 교차검증 ──
    log("STATUS: YouTube API로 실제 공개 상태 교차검증 중...")
    try:
        yt = get_youtube()
        has_vid = [e for e in (done + producing + failed) if e.get('vid')]
        vid_ids = list({e['vid'] for e in has_vid})
        vid_to_ep = {e['vid']: e for e in has_vid if e.get('vid')}

        yt_info = {}
        for i in range(0, len(vid_ids), 50):
            batch = vid_ids[i:i+50]
            resp = yt.videos().list(part='snippet,status,statistics', id=','.join(batch)).execute()
            found = {item['id'] for item in resp.get('items', [])}
            for item in resp.get('items', []):
                s = item['statistics']
                yt_info[item['id']] = {
                    'privacy': item['status'].get('privacyStatus', '?'),
                    'pub_at': item['status'].get('publishAt', ''),
                    'views': int(s.get('viewCount', 0)),
                    'likes': int(s.get('likeCount', 0)),
                    'comments': int(s.get('commentCount', 0)),
                }
            for vid in batch:
                if vid not in found:
                    yt_info[vid] = {'privacy': 'deleted', 'pub_at': '', 'views': 0, 'likes': 0, 'comments': 0}
        yt_ok = True
    except Exception as e:
        log(f"[WARN] YouTube API 교차검증 실패 (시트 데이터만 표시): {e}")
        yt_ok = False
        yt_info = {}

    mismatches = []
    now_str = datetime.now().strftime('%m/%d %H:%M')

    print("\n" + "="*62)
    print("  한걸음씩 채널 현황" + (" [YT API 검증]" if yt_ok else " [시트 데이터]"))
    print("="*62)
    print(f"  완료:{len(done)} | 대기:{len(waiting)} | 생산중:{len(producing)} | 실패:{len(failed)}")

    if done:
        print(f"\n  --- 완료된 에피소드 ---")
        for e in done:
            if yt_ok and e.get('vid') and e['vid'] in yt_info:
                yi = yt_info[e['vid']]
                priv = yi['privacy']
                pub_at = f" (예약:{yi['pub_at'][:10]})" if yi.get('pub_at') else ''
                if priv == 'public':
                    tag = '[PUBLIC]'
                elif priv == 'private':
                    tag = '[PRIVATE]'
                    mismatches.append(f"EP{e['ep']}: 시트=완료 but YT=비공개")
                elif priv == 'deleted':
                    tag = '[DELETED]'
                    mismatches.append(f"EP{e['ep']}: 시트=완료 but YT=삭제됨")
                else:
                    tag = f'[{priv.upper()}]'
                print(f"  EP{e['ep']:>3}: {tag}{pub_at} 조회:{yi['views']:,} 좋아요:{yi['likes']} | {e['title'][:22]}")
            else:
                print(f"  EP{e['ep']:>3}: {e['url'] or '(URL없음)'} | {e['title'][:28]}")

    if producing:
        print(f"\n  --- 생산중/기타 ---")
        for e in producing:
            if yt_ok and e.get('vid') and e['vid'] in yt_info:
                yi = yt_info[e['vid']]
                print(f"  EP{e['ep']:>3}: [{yi['privacy'].upper()}] 조회:{yi['views']} | {e['title'][:25]} | {e['memo'][:30]}")
            else:
                print(f"  EP{e['ep']:>3}: [{e['status']}] | {e['title'][:25]} | {e['memo'][:35]}")

    if failed:
        print(f"\n  --- 실패 (재시도 필요) ---")
        for e in failed:
            print(f"  EP{e['ep']:>3}: {e['title'][:25]} | {e['memo'][:50]}")

    if waiting:
        print(f"\n  --- 대기 중 ---")
        for e in waiting[:5]:
            print(f"  EP{e['ep']:>3}: {e['title'][:25]} | 공개예정: {e['pub'][:10]}")
        if len(waiting) > 5:
            print(f"  ... 외 {len(waiting)-5}개")

    if mismatches:
        print(f"\n  *** 불일치 {len(mismatches)}건 (즉시 확인 필요!) ***")
        for m in mismatches:
            print(f"    ! {m}")
    elif yt_ok:
        print(f"\n  [OK] YouTube 실제 상태 정상 확인 ({now_str})")

    print("\n" + "="*62)

# ══════════════════════════════════════════════════════════════
#  4) STRATEGY - AI 전략 분석
# ══════════════════════════════════════════════════════════════
def cmd_strategy():
    log("STRATEGY: 성과 데이터 수집 + AI 분석 시작...")

    # 먼저 최신 analytics 수집
    cmd_analytics()

    ss = get_sheets()
    pl = ss.worksheet('PIPELINE')
    all_rows = pl.get_all_values()
    header = all_rows[0]
    col = {h: i for i, h in enumerate(header)}

    # 완료 에피소드 데이터 정리
    episodes_data = []
    for row in all_rows[1:]:
        if '완료' in row[col['상태']].strip():
            episodes_data.append({
                'ep': row[col['EP']].strip(),
                'title': row[col['제목']].strip(),
                'quote': row[col['전체명언']].strip(),
                'tone': row[col['톤']].strip(),
                'publish': row[col['공개일(UTC)']].strip(),
                'memo': row[col['메모']].strip() if '메모' in col else '',
            })

    # 대기 에피소드
    waiting_data = []
    for row in all_rows[1:]:
        if '대기' in row[col['상태']].strip():
            waiting_data.append({
                'ep': row[col['EP']].strip(),
                'title': row[col['제목']].strip(),
                'quote': row[col['전체명언']].strip(),
                'tone': row[col['톤']].strip(),
            })

    prompt = f"""당신은 YouTube Shorts 채널 전략 분석가입니다.
채널명: 한걸음씩 (THE SHIN FAMILY)
컨셉: AI로 만든 72세 한국 할아버지 '노박'이 인생 조언을 해주는 쇼츠 채널.
영상 길이: 약 24초, 세로 9:16, 주 3회 업로드 (월/수/금 05:00 KST)

== 완료된 에피소드 ({len(episodes_data)}개) ==
{json.dumps(episodes_data, ensure_ascii=False, indent=2)}

== 대기 중 에피소드 ({len(waiting_data)}개) ==
{json.dumps(waiting_data, ensure_ascii=False, indent=2)}

다음을 분석해주세요:
1. 현재까지 명언 주제의 다양성 평가 (돈, 관계, 자존감, 건강 등 카테고리별 비율)
2. 톤(firm/warm/calm) 배분 분석 및 최적 비율 제안
3. 대기 중 에피소드의 예상 성과 순위 (1위~3위, 이유 포함)
4. 부족한 주제 카테고리와 추가 명언 3개 제안
5. 업로드 스케줄 최적화 제안 (요일/시간대)
6. 채널 성장을 위한 즉시 실행 가능한 액션 3가지

한국어로 답변하세요. 구체적인 숫자와 근거를 제시하세요."""

    log("Gemini에게 전략 분석 요청 중...")
    try:
        gclient = get_gemini()
        r = gclient.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        report_text = r.text
    except Exception as e:
        log(f"[WARN] Gemini 모델 호출 실패 ({e}). 폴백 모델 시도...")
        try:
            r = gclient.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
            )
            report_text = r.text
        except Exception as e2:
            log(f"[ERROR] Gemini 폴백 호출 실패: {e2}")
            report_text = f"전략 분석 실패: API 일시적 과부하 상태입니다 ({e2})"

    print("\n" + "="*60)
    print("  AI 전략 분석 리포트")
    print("="*60)
    print(report_text)
    print("="*60)

# ══════════════════════════════════════════════════════════════
#  5) SCHEDULE - 스케줄 점검
# ══════════════════════════════════════════════════════════════
def cmd_schedule():
    log("SCHEDULE: 스케줄 점검 중...")
    ss = get_sheets()
    pl = ss.worksheet('PIPELINE')
    all_rows = pl.get_all_values()
    header = all_rows[0]
    col = {h: i for i, h in enumerate(header)}

    schedule = []
    for row in all_rows[1:]:
        pub = row[col['공개일(UTC)']].strip()
        if pub:
            try:
                dt = datetime.fromisoformat(pub.replace('Z', '+00:00'))
                schedule.append({
                    'ep': row[col['EP']].strip(),
                    'status': row[col['상태']].strip(),
                    'title': row[col['제목']].strip(),
                    'dt': dt,
                    'pub': pub,
                })
            except:
                pass

    schedule.sort(key=lambda x: x['dt'])

    print("\n" + "="*60)
    print("  업로드 스케줄")
    print("="*60)

    now = datetime.now().astimezone()
    issues = []

    for i, s in enumerate(schedule):
        kst = s['dt'] + timedelta(hours=9)
        day_name = ['월','화','수','목','금','토','일'][kst.weekday()]
        status_icon = '✅' if '완료' in s['status'] else '⏳' if '대기' in s['status'] else '🎬' if '생성' in s['status'] else '❌'
        past = " (공개됨)" if s['dt'] < now else ""
        print(f"  {status_icon} EP{s['ep']}: {kst.strftime('%m/%d')} ({day_name}) {kst.strftime('%H:%M')} KST | {s['title'][:20]}{past}")

        # 갭 체크
        if i > 0:
            gap = (s['dt'] - schedule[i-1]['dt']).days
            if gap > 3:
                issues.append(f"EP{schedule[i-1]['ep']} -> EP{s['ep']} 사이 {gap}일 갭!")
            if gap < 1:
                issues.append(f"EP{schedule[i-1]['ep']}과 EP{s['ep']}가 같은 날!")

        # 대기인데 공개일이 지났으면 경고
        if '대기' in s['status'] and s['dt'] < now:
            issues.append(f"EP{s['ep']}: 공개일 지남! 즉시 생산 필요!")

    if issues:
        print(f"\n  --- 경고 ---")
        for issue in issues:
            print(f"  [!] {issue}")
    else:
        print(f"\n  스케줄 정상!")

    # 남은 콘텐츠 일수
    future = [s for s in schedule if '대기' in s['status'] or '완료' in s['status']]
    if future:
        last = max(s['dt'] for s in future)
        remaining_days = (last - now).days
        print(f"\n  콘텐츠 잔량: {len([s for s in schedule if '대기' in s['status']])}개 대기 | 마지막 공개: {remaining_days}일 후")

    print("="*60)

# ══════════════════════════════════════════════════════════════
#  6) GRADE - 등급 자동 부여
# ══════════════════════════════════════════════════════════════
def cmd_grade():
    log("GRADE: 성과 기반 등급 부여 중...")

    # 먼저 최신 데이터 수집
    cmd_analytics()

    ss = get_sheets()
    pl = ss.worksheet('PIPELINE')
    all_rows = pl.get_all_values()
    header = all_rows[0]
    col = {h: i for i, h in enumerate(header)}

    yt = get_youtube()

    # 완료 에피소드의 성과 조회
    results = []
    for idx, row in enumerate(all_rows[1:], start=2):
        vid = row[col['영상ID']].strip()
        if vid and '완료' in row[col['상태']].strip():
            results.append({'row': idx, 'ep': row[col['EP']].strip(), 'vid': vid})

    if not results:
        log("등급을 매길 영상이 없습니다.")
        return

    # 배치 조회
    vids = [r['vid'] for r in results]
    stats = {}
    for i in range(0, len(vids), 50):
        batch = vids[i:i+50]
        resp = yt.videos().list(part='statistics', id=','.join(batch)).execute()
        for item in resp.get('items', []):
            s = item['statistics']
            views = int(s.get('viewCount', 0))
            likes = int(s.get('likeCount', 0))
            comments = int(s.get('commentCount', 0))
            like_rate = (likes / views * 100) if views > 0 else 0
            stats[item['id']] = {'views': views, 'likes': likes, 'comments': comments, 'like_rate': like_rate}

    # 등급 기준 (GRADE GUIDE 시트 참조)
    #   S: 좋아요율 8%+ 또는 조회수 상위 (완료율 85%+)
    #   A: 좋아요율 5-8% (완료율 70%+)
    #   B: 좋아요율 3-5% (완료율 60-69%)
    #   C: 좋아요율 <3% (완료율 <60%)
    def calc_grade(s):
        lr = s['like_rate']
        if lr >= 8:
            return 'S'
        elif lr >= 5:
            return 'A'
        elif lr >= 3:
            return 'B'
        else:
            return 'C'

    updates = []
    print("\n" + "="*60)
    print("  에피소드 등급표")
    print("="*60)

    for r in results:
        if r['vid'] in stats:
            s = stats[r['vid']]
            grade = calc_grade(s)
            memo = f"[{grade}] 조회:{s['views']} 좋아요:{s['likes']}({s['like_rate']:.1f}%) 댓글:{s['comments']} ({datetime.now().strftime('%m/%d')})"
            updates.append({'range': f'P{r["row"]}', 'values': [[memo]]})
            print(f"  EP{r['ep']}: {grade} | 조회 {s['views']:,} | 좋아요 {s['likes']} ({s['like_rate']:.1f}%) | 댓글 {s['comments']}")

    if updates:
        pl.batch_update(updates)

    print("="*60)
    log("등급 부여 완료!")

# ══════════════════════════════════════════════════════════════
#  자가진단 및 오류 자동 차단 로직 (SOP)
# ══════════════════════════════════════════════════════════════
def self_diagnose_api():
    """Gemini 및 구글 시트, YouTube API 키 유효성을 실행 전 강제 진단"""
    log("🔧 [자가진단] API 키 상태 검증 중...")
    
    # 1. Gemini API 키 테스트
    try:
        from google import genai
        if not GEMINI_KEY:
            raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
            
        gclient = genai.Client(api_key=GEMINI_KEY)
        gclient.models.generate_content(
            model='gemini-2.5-flash',
            contents='test'
        )
        log("  ✅ Gemini API 키 검증 성공")
    except Exception as e:
        err_msg = str(e)
        if "API_KEY_INVALID" in err_msg or "expired" in err_msg.lower() or "400" in err_msg:
            log(f"❌ [치명적 오류] Gemini API 키가 만료되었거나 올바르지 않습니다: {err_msg}")
            flag_path = AUTO / "BLOCKED_BY_ERROR.flag"
            flag_path.write_text(f"Gemini API Key expired or invalid at {datetime.now()}\nError: {err_msg}", encoding='utf-8')
            
            send_telegram(
                f"🚨 <b>안실장 긴급 시스템 장애 경보</b>\n\n"
                f"🔴 <b>장애 원인</b>: Gemini API 키 만료 (`API_KEY_INVALID`)\n"
                f"⚠️ 시스템 안정성을 위해 <b>자동 업로드 및 생산 스케줄러가 즉시 비활성화(Lock)</b>되었습니다.\n\n"
                f"🔧 <b>조치 방법</b>: 구글 AI 스튜디오에서 키를 갱신하여 .env 파일에 업데이트한 후, "
                f"<code>BLOCKED_BY_ERROR.flag</code> 파일을 삭제해 주세요.\n"
                f"⏰ 발생시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            sys.exit(1)
        else:
            log(f"⚠️ [경고] Gemini API 연결 지연 또는 경미한 오류: {err_msg}")
            
    # 2. 구글 시트 & YouTube API 검증
    try:
        get_creds()
        log("  ✅ Google Sheets & YouTube OAuth 토큰 검증 성공")
    except Exception as e:
        log(f"❌ [치명적 오류] Google API 토큰 로드 실패: {e}")
        flag_path = AUTO / "BLOCKED_BY_ERROR.flag"
        flag_path.write_text(f"Google OAuth Token error at {datetime.now()}\nError: {e}", encoding='utf-8')
        
        send_telegram(
            f"🚨 <b>안실장 긴급 시스템 장애 경보</b>\n\n"
            f"🔴 <b>장애 원인</b>: Google OAuth 토큰 만료 또는 갱신 실패\n"
            f"⚠️ <b>자동 스케줄러가 잠금(Lock)</b> 상태로 전환되었습니다.\n\n"
            f"🔧 <b>조치 방법</b>: <code>python reissue_channel_tokens.py</code>를 실행해 주세요.\n"
            f"⏰ 발생시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        sys.exit(1)

# ══════════════════════════════════════════════════════════════
#  MAIN - 명령어 라우터
# ══════════════════════════════════════════════════════════════
COMMANDS = {
    'produce':   cmd_produce,
    'analytics': cmd_analytics,
    'status':    cmd_status,
    'strategy':  cmd_strategy,
    'schedule':  cmd_schedule,
    'grade':     cmd_grade,
}

def main():
    flag_path = AUTO / "BLOCKED_BY_ERROR.flag"
    if flag_path.exists():
        log(f"🛑 [차단됨] 시스템 장애 플래그 파일이 존재하여 기동을 건너뜁니다: {flag_path.name}")
        log("장애 해결 후 플래그 파일을 삭제해 주세요.")
        sys.exit(1)

    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("\n  한걸음씩 채널 매니저 에이전트 v1.0")
        print("  " + "="*40)
        print("  사용법:")
        for cmd, fn in COMMANDS.items():
            doc = fn.__doc__ or ''
            print(f"    python channel_agent.py {cmd:12s}")
        print()
        print("  명령어 설명:")
        print("    produce   : 다음 대기 에피소드 자동 생산 (Veo+편집+업로드+현지화)")
        print("    analytics : YouTube에서 조회수/좋아요/댓글 수집 -> 시트 기록")
        print("    status    : 전체 현황 대시보드 출력")
        print("    strategy  : AI가 성과 분석 + 전략 제안 (Gemini)")
        print("    schedule  : 스케줄 점검, 갭 경고, 남은 콘텐츠 일수")
        print("    grade     : 성과 기반 등급 자동 부여 (S/A/B/C)")
        print()
        sys.exit(0)

    cmd = sys.argv[1]
    
    if cmd in ['produce', 'analytics', 'strategy']:
        self_diagnose_api()
        
    log(f"채널 매니저 에이전트 v1.0 - [{cmd.upper()}] 실행")
    COMMANDS[cmd]()
    log(f"[{cmd.upper()}] 완료!")

if __name__ == '__main__':
    main()

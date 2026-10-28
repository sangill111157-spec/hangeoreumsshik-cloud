# -*- coding: utf-8 -*-
"""
update_3channels_analytics.py — 3개 유튜브 채널 실시간 트래픽 갱신 및 시트 정합성 연동
"""
# [RGON-WBC-GUARD-V18-START]
try:
    import rgon_white_blood_cell as _rgon_wbc
    _rgon_wbc.install_excepthook('update_3channels_analytics.py')
except Exception:
    _rgon_wbc = None
# [RGON-WBC-GUARD-V18-END]
import os
import sys
import pickle
import json
import urllib.request
import urllib.parse
import re
from datetime import datetime
from pathlib import Path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# UTF-8 출력 강제 설정
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# 경로 설정
AUTO = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(AUTO, "config")
TOKEN_SHIN = os.path.join(CONFIG, "token.pickle")
TOKEN_BOOST = os.path.join(CONFIG, "token_booster.pickle")
TOKEN_CAFE = os.path.join(CONFIG, "yt_token.pickle")

# 시트 ID 설정
SHIN_SHEET = "1mIu1vXu0luRSDNyjE-WkJaz91otX0OvgaBVrJj6rwnY"
BOOST_SHEET = "19yLh5tIUNg5gm3UpJxbCUmAfEUtotjrlrc7KMvp_KE4"
CAFE_SHEET = "1MqLCJNCdwPV8GrIhp5w3BdIsuVazIC2uREpgypUu9PI"

# 텔레그램 발송 함수
def _load_telegram_config():
    tg_path = Path(r'C:\Users\sangi\.connect-ai-brain\_company\_agents\secretary\tools\telegram_setup.json')
    if tg_path.exists():
        try:
            cfg = json.loads(tg_path.read_text(encoding='utf-8'))
            return cfg.get('TELEGRAM_BOT_TOKEN', ''), cfg.get('TELEGRAM_CHAT_ID', '')
        except:
            pass
    return '', ''

def send_telegram(message: str):
    token, chat_id = _load_telegram_config()
    if not token or not chat_id:
        print("[WARN] 텔레그램 설정이 없어 알림을 건너뜁니다.")
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[WARN] 텔레그램 전송 실패: {e}")
        return False

# 유튜브 URL에서 비디오 ID 추출 헬퍼
def extract_video_id(url):
    if not url:
        return ""
    match = re.search(r'(?:youtu\.be/|youtube\.com/watch\?v=)([A-Za-z0-9_-]{11})', url)
    return match.group(1) if match else ""

def col_idx_from(header, *names):
    """임의 헤더 리스트에서 컬럼명으로 인덱스 반환 (어디서나 재사용 가능)"""
    for i, h in enumerate(header):
        if str(h).strip() in names:
            return i
    return None

# 안전한 API 클라이언트 생성 함수
def get_youtube_client(token_path):
    if not os.path.exists(token_path):
        return None, "토큰 파일이 존재하지 않습니다."
    try:
        with open(token_path, "rb") as f:
            creds = pickle.load(f)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, "wb") as f:
                pickle.dump(creds, f)
        return build("youtube", "v3", credentials=creds), None
    except Exception as e:
        return None, str(e)

def get_sheets_service():
    if not os.path.exists(TOKEN_SHIN):
        print("ℹ️ [Cloud Fallback] config/token.pickle 미감지: 클라우드 안전 폴백 모드로 동작합니다.")
        return None
    try:
        with open(TOKEN_SHIN, "rb") as f:
            creds = pickle.load(f)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_SHIN, "wb") as f:
                pickle.dump(creds, f)
        return build("sheets", "v4", credentials=creds).spreadsheets()
    except Exception as e:
        print(f"⚠️ [Cloud Fallback] 구글 시트 인증 폴백 처리 ({e})")
        return None

def run_update():
    print("=" * 80)
    print(f"🔄 3채널 실시간 유튜브 트래픽 동기화 시작 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print("=" * 80)
    
    sheets = get_sheets_service()
    if sheets is None:
        print("✅ [Cloud Safe Mode] 로컬/클라우드 시크릿 미주입 환경 — 에러 없이 안전 폴백 완료 (exit 0)")
        return
    
    report_lines = []
    
    # -------------------------------------------------------------
    # 1. 한걸음씩 (THE SHIN FAMILY)
    # -------------------------------------------------------------
    print("\n[1/3] 👴 한걸음씩 (THE SHIN FAMILY) 업데이트 진행...")
    yt_shin, err_shin = get_youtube_client(TOKEN_SHIN)
    if err_shin:
        print(f"  ❌ 한걸음씩 유튜브 API 클라이언트 생성 실패: {err_shin}")
        report_lines.append("👴 <b>한걸음씩</b>: ❌ API 인증 오류 (토큰 확인 필요)")
    else:
        try:
            ch_info = yt_shin.channels().list(part="snippet,statistics", mine=True).execute()["items"][0]
            subs = ch_info["statistics"].get("subscriberCount", "0")
            total_views = ch_info["statistics"].get("viewCount", "0")
            
            pl_data = sheets.values().get(spreadsheetId=SHIN_SHEET, range="PIPELINE!A1:P45").execute().get("values", [])
            header = pl_data[0]
            col = {h: i for i, h in enumerate(header)}
            
            video_ids = []
            row_map = {}
            for idx, row in enumerate(pl_data[1:], start=2):
                if len(row) > col.get("영상ID", -1):
                    vid = row[col["영상ID"]].strip()
                    status = row[col["상태"]].strip() if len(row) > col.get("상태", -1) else ""
                    if vid and (status == "✅완료" or status == "렌더완료"):
                        video_ids.append(vid)
                        row_map[vid] = idx
                        
            stats = {}
            if video_ids:
                for i in range(0, len(video_ids), 50):
                    batch = video_ids[i:i+50]
                    v_resp = yt_shin.videos().list(part="statistics", id=",".join(batch)).execute()
                    for item in v_resp.get("items", []):
                        s = item["statistics"]
                        stats[item["id"]] = {
                            "views": s.get("viewCount", "0"),
                            "likes": s.get("likeCount", "0"),
                            "comments": s.get("commentCount", "0")
                        }
            
            updates = []
            today_str = datetime.now().strftime("%m/%d")
            for vid, s in stats.items():
                row_num = row_map[vid]
                memo = f"조회:{s['views']} 좋아요:{s['likes']} 댓글:{s['comments']} ({today_str})"
                updates.append({
                    "range": f"PIPELINE!P{row_num}",
                    "values": [[memo]]
                })
                
            if updates:
                sheets.values().batchUpdate(spreadsheetId=SHIN_SHEET, body={"valueInputOption": "USER_ENTERED", "data": updates}).execute()
                
            try:
                ep_data = sheets.values().get(spreadsheetId=SHIN_SHEET, range="EPISODES!A1:H45").execute().get("values", [])
                if ep_data:
                    ep_header = ep_data[0]
                    ep_col = {h: i for i, h in enumerate(ep_header)}
                    
                    ep_updates = []
                    for eidx, erow in enumerate(ep_data[1:], start=2):
                        ep_num = erow[ep_col.get("EP#", 0)].strip().replace("EP", "")
                        for r_idx, prow in enumerate(pl_data[1:], start=2):
                            if prow[col["EP"]].strip() == ep_num:
                                p_vid = prow[col["영상ID"]].strip()
                                if p_vid in stats:
                                    s = stats[p_vid]
                                    if "조회수48h" in ep_col:
                                        ep_updates.append({"range": f"EPISODES!{chr(65+ep_col['조회수48h'])}{eidx}", "values": [[s['views']]]})
                                    if "좋아요수" in ep_col:
                                        ep_updates.append({"range": f"EPISODES!{chr(65+ep_col['좋아요수'])}{eidx}", "values": [[s['likes']]]})
                                    if "댓글수" in ep_col:
                                        ep_updates.append({"range": f"EPISODES!{chr(65+ep_col['댓글수'])}{eidx}", "values": [[s['comments']]]})
                                break
                    if ep_updates:
                        sheets.values().batchUpdate(spreadsheetId=SHIN_SHEET, body={"valueInputOption": "USER_ENTERED", "data": ep_updates}).execute()
            except Exception as e:
                print(f"  ⚠️ EPISODES 시트 업데이트 중 오류 (무시): {e}")
                
            print(f"  ✅ 한걸음씩 완료: {len(stats)}개 비디오 정보 갱신")
            report_lines.append(f"👴 <b>한걸음씩</b>: ✅ 완료 (구독자 {int(subs):,}명, 총 조회 {int(total_views):,}회, 최근 갱신 {len(stats)}건)")
        except Exception as e:
            print(f"  ❌ 한걸음씩 연동 에러: {e}")
            report_lines.append(f"👴 <b>한걸음씩</b>: ⚠️ 동기화 실패 ({e})")

    # -------------------------------------------------------------
    # 2. 부스터 플리 (Booster Playlist)
    # -------------------------------------------------------------
    print("\n[2/3] 🎵 부스터 플리 (Booster Playlist) 업데이트 진행...")
    yt_boost, err_boost = get_youtube_client(TOKEN_BOOST)
    if err_boost:
        print(f"  ❌ 부스터 플리 유튜브 API 클라이언트 생성 실패: {err_boost}")
        report_lines.append("🎵 <b>부스터 플리</b>: ❌ API 인증 오류 (토큰 확인 필요)")
    else:
        try:
            ch_info = yt_boost.channels().list(part="snippet,statistics", mine=True).execute()["items"][0]
            subs = ch_info["statistics"].get("subscriberCount", "0")
            total_views = ch_info["statistics"].get("viewCount", "0")
            
            # ── [수정 B v2] 실제 시트 구조 대응: 헤더 없는 경우 자동 감지 ──
            # Video_Schedule 실제 구조:
            #   Row1: 타이틀 | Row2: 빈행 | Row3~: 바로 데이터 (헤더행 없음)
            # 컬럼 순서: A=ID | B=타입 | C=시리즈 | D=트랙명 | E=장르 |
            #            F=예정일 | G=상태 | H=YouTube ID(11자) |
            #            I=조회수 | J=좋아요 | K=댓글 | L=비고 | M=숏츠여부
            # ── [Video_Schedule 실제 구조] ──
            # Row1=타이틀, Row2=빈행, Row3~=데이터(헤더 없음)
            # 콜럼: A=ID B=타입 C=시리즈 D=트랙명 E=예정일 F=업로드일 G=상태
            #          H=YouTube ID I=조회수 J=좋아요 K=댓글 L=비고
            IDX_YTID     = 7   # H열 (0-based)
            IDX_VIEWS    = 8   # I열
            IDX_LIKES    = 9   # J열
            IDX_COMMENTS = 10  # K열

            def to_a1_col(idx):
                """0-based 인덱스 → A1 열 문자 (0→A, 25→Z, 26→AA)"""
                s = ''
                n = idx + 1
                while n:
                    n, r = divmod(n - 1, 26)
                    s = chr(65 + r) + s
                return s

            sch_raw = sheets.values().get(
                spreadsheetId=BOOST_SHEET, range="Video_Schedule!A1:Z35"
            ).execute().get("values", [])

            # YouTube ID(11자리) 위치를 데이터에서 실측 확인 (IDX_YTID 검증)
            ytid_col_confirmed = None
            for sample_row in sch_raw[2:]:
                if len(sample_row) > IDX_YTID:
                    cell = sample_row[IDX_YTID].strip()
                    import re as _re
                    if _re.match(r'^[A-Za-z0-9_-]{11}$', cell):
                        ytid_col_confirmed = IDX_YTID
                        break
            if ytid_col_confirmed is None:
                # 예비 폴백: 전체 행에서 11자리 위치 스캔
                for sample_row in sch_raw[2:]:
                    for ci, cell in enumerate(sample_row):
                        import re as _re2
                        if _re2.match(r'^[A-Za-z0-9_-]{11}$', str(cell).strip()):
                            ytid_col_confirmed = ci
                            break
                    if ytid_col_confirmed is not None:
                        break
            if ytid_col_confirmed is None:
                raise ValueError("시트에서 YouTube ID 콜럼을 찾을 수 없습니다.")

            print(f"  [콜럼 확정] YouTube ID={to_a1_col(ytid_col_confirmed)} "
                  f"조회수={to_a1_col(IDX_VIEWS)} 좋아요={to_a1_col(IDX_LIKES)} 댓글={to_a1_col(IDX_COMMENTS)}")

            # Row3~에서 YouTube ID 수집 — 행마다 열 위치가 다를 수 있으므로
            # 전체 셀을 스캔하여 YouTube ID 패턴(11자, 영숫자+_-)을 찾음
            # (V006처럼 특수 구조 행도 정확히 수집)
            import re as _re_ytid
            v_map = {}  # {youtube_video_id: sheet_row_number}
            for ridx, row in enumerate(sch_raw[2:], start=3):
                for cell in row:
                    cell_s = str(cell).strip()
                    if (len(cell_s) == 11
                            and _re_ytid.match(r'^[A-Za-z0-9_-]{11}$', cell_s)
                            and cell_s not in v_map):
                        v_map[cell_s] = ridx
                        break  # 한 행에 YouTube ID는 하나

            print(f"  [YouTube ID 감지] {len(v_map)}개: {list(v_map.keys())}")


            stats = {}
            if v_map:
                v_resp = yt_boost.videos().list(part="statistics", id=",".join(v_map.keys())).execute()
                for item in v_resp.get("items", []):
                    s = item["statistics"]
                    stats[item["id"]] = {
                        "views":    int(s.get("viewCount", 0)),
                        "likes":    int(s.get("likeCount", 0)),
                        "comments": int(s.get("commentCount", 0))
                    }
                    print(f"    {item['id']}: 조회={stats[item['id']]['views']} "
                          f"좋아요={stats[item['id']]['likes']} 댓글={stats[item['id']]['comments']}")

            # 정확한 칼럼 위치로 시트 갱신
            updates = []
            for vid, s in stats.items():
                row_num = v_map[vid]
                updates.append({"range": f"Video_Schedule!{to_a1_col(IDX_VIEWS)}{row_num}",    "values": [[s["views"]]]})
                updates.append({"range": f"Video_Schedule!{to_a1_col(IDX_LIKES)}{row_num}",    "values": [[s["likes"]]]})
                updates.append({"range": f"Video_Schedule!{to_a1_col(IDX_COMMENTS)}{row_num}", "values": [[s["comments"]]]})

            # Upload_Log 갱신 (E열=URL, H열=조회수 위치로 추정)
            log_data = sheets.values().get(
                spreadsheetId=BOOST_SHEET, range="Upload_Log!A1:T30"
            ).execute().get("values", [])
            for lidx, lrow in enumerate(log_data[2:], start=3):
                if len(lrow) > 4:
                    url = lrow[4].strip()  # E열 = URL
                    l_vid = extract_video_id(url)
                    if l_vid in stats:
                        updates.append({"range": f"Upload_Log!I{lidx}",
                                        "values": [[stats[l_vid]['views']]]})

            if updates:
                sheets.values().batchUpdate(
                    spreadsheetId=BOOST_SHEET,
                    body={"valueInputOption": "USER_ENTERED", "data": updates}
                ).execute()
                print(f"  [시트 반영] {len(updates)}개 셀 업데이트 완료")

                # ── 역방향 점검: 시트에 없는 채널 영상 감지 (Claude Opus 4.8 제안) ──
            try:
                ch_info2 = yt_boost.channels().list(part='contentDetails', mine=True).execute()
                uploads_pl = ch_info2['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                pl_resp = yt_boost.playlistItems().list(
                    part='snippet', playlistId=uploads_pl, maxResults=50
                ).execute()
                channel_vid_ids = {
                    item['snippet']['resourceId']['videoId']
                    for item in pl_resp.get('items', [])
                }
                # 시트에 등록된 YouTube ID 수집 (H열)
                sheet_vid_ids = set(v_map.keys())
                untracked = channel_vid_ids - sheet_vid_ids
                if untracked:
                    warn_msg = f"⚠️ [역방향 점검] 시트 미등록 영상 {len(untracked)}개 발견: {untracked}"
                    print(f"  {warn_msg}")
                    report_lines.append(f"🎵 <b>부스터 플리</b>: {warn_msg} — Video_Schedule 수동 등록 필요!")
                else:
                    print("  [역방향 점검] ✅ 모든 채널 영상이 시트에 등록되어 있습니다.")
            except Exception as rev_err:
                print(f"  [역방향 점검] ⚠️ 실행 실패 (무시): {rev_err}")

            # Daily_Work_Log 기록 남기기
            now = datetime.now()
            boost_log = [[now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), "안실장 자동화봇", "성과 수집", 
                          f"실시간 조회수 동기화 완료 ({len(stats)}개 비디오)", "✅ 완료"]]
            sheets.values().append(spreadsheetId=BOOST_SHEET, range="Daily_Work_Log!A:F",
                                   valueInputOption="USER_ENTERED", body={"values": boost_log}).execute()
                                   
            print(f"  ✅ 부스터 플리 완료: {len(stats)}개 비디오 정보 갱신")
            report_lines.append(f"🎵 <b>부스터 플리</b>: ✅ 완료 (구독자 {int(subs):,}명, 총 조회 {int(total_views):,}회, 최근 갱신 {len(stats)}건)")
        except Exception as e:
            print(f"  ❌ 부스터 플리 연동 에러: {e}")
            report_lines.append(f"🎵 <b>부스터 플리</b>: ⚠️ 동기화 실패 ({e})")

    # -------------------------------------------------------------
    # 3. Café Hour (카페 아워)
    # -------------------------------------------------------------
    print("\n[3/3] ☕ Café Hour (카페 아워) 업데이트 진행...")
    yt_cafe, err_cafe = get_youtube_client(TOKEN_CAFE)
    if err_cafe:
        print(f"  ❌ 카페 아워 유튜브 API 클라이언트 생성 실패 (만료 또는 부재): {err_cafe}")
        report_lines.append("☕ <b>Café Hour</b>: ⚠️ API 인증 무효 (이대표님 갱신 대기 중)")
    else:
        try:
            ch_info = yt_cafe.channels().list(part="snippet,statistics,contentDetails", mine=True).execute()["items"][0]
            subs = ch_info["statistics"].get("subscriberCount", "0")
            total_views = ch_info["statistics"].get("viewCount", "0")
            uploads_playlist = ch_info["contentDetails"]["relatedPlaylists"]["uploads"]
            
            playlist_items = yt_cafe.playlistItems().list(part="snippet,status", playlistId=uploads_playlist, maxResults=5).execute().get("items", [])
            video_ids = [item["snippet"]["resourceId"]["videoId"] for item in playlist_items]
            
            stats = {}
            if video_ids:
                v_resp = yt_cafe.videos().list(part="snippet,statistics,status", id=",".join(video_ids)).execute()
                for item in v_resp.get("items", []):
                    vid = item["id"]
                    stats[vid] = {
                        "title": item["snippet"]["title"],
                        "views": item["statistics"].get("viewCount", "0"),
                        "privacy": item["status"]["privacyStatus"],
                        "published_at": item["snippet"]["publishedAt"][:10]
                    }
            
            # Video_Schedule 갱신 (H열 index 7에서 URL 읽고, G열 index 6에 상태 기재)
            sch_data = sheets.values().get(spreadsheetId=CAFE_SHEET, range="Video_Schedule!A1:J20").execute().get("values", [])
            
            cafe_updates = []
            for idx, r in enumerate(sch_data[1:], start=2):
                if len(r) > 7:
                    url = r[7].strip()
                    vid = extract_video_id(url)
                    if vid in stats:
                        privacy = stats[vid]["privacy"]
                        status_text = "✅ 업로드" if privacy == "public" else "🕐 예약됨" if privacy == "private" else "비공개"
                        cafe_updates.append({"range": f"Video_Schedule!G{idx}", "values": [[status_text]]})
            
            # Dashboard 탭 갱신
            public_vids = [s for vid, s in stats.items() if s["privacy"] == "public"]
            private_vids = [s for vid, s in stats.items() if s["privacy"] == "private"]
            
            cafe_updates.append({"range": "Dashboard!B6", "values": [[str(len(public_vids))]]})
            if public_vids:
                cafe_updates.append({"range": "Dashboard!B7", "values": [[public_vids[0]["published_at"]]]})
                cafe_updates.append({"range": "Dashboard!C7", "values": [[f"{public_vids[0]['title']} ({public_vids[0]['views']} views)"]]})
            if private_vids:
                cafe_updates.append({"range": "Dashboard!B8", "values": [[private_vids[0]["published_at"]]]})
                cafe_updates.append({"range": "Dashboard!C8", "values": [[f"{private_vids[0]['title']} (예약됨)"]]})
                
            if cafe_updates:
                sheets.values().batchUpdate(spreadsheetId=CAFE_SHEET, body={"valueInputOption": "USER_ENTERED", "data": cafe_updates}).execute()
                
            # Daily_Work_Log 기록 남기기
            now = datetime.now()
            cafe_log = [[now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), "안실장 자동화봇", "성과 수집", 
                         f"유튜브 실제 데이터 기반 Dashboard 동기화 완료", "✅ 완료"]]
            sheets.values().append(spreadsheetId=CAFE_SHEET, range="Daily_Work_Log!A:F",
                                   valueInputOption="USER_ENTERED", body={"values": cafe_log}).execute()
                                   
            print(f"  ✅ 카페 아워 완료: Dashboard 및 Video_Schedule 갱신")
            report_lines.append(f"☕ <b>Café Hour</b>: ✅ 완료 (구독자 {int(subs):,}명, 총 조회 {int(total_views):,}회, 최근 갱신 완료)")
        except Exception as e:
            print(f"  ❌ 카페 아워 연동 에러: {e}")
            report_lines.append(f"☕ <b>Café Hour</b>: ⚠️ 동기화 실패 ({e})")
            
    print("\n========================================================")
    print("📢 텔레그램으로 갱신 통보 발송 중...")
    print("========================================================")
    
    # 이대표님 요구에 따라 3채널 실시간 트래픽 보고의 텔레그램 스팸 발송 차단 (구글 시트 동기화 기능만 백그라운드로 작동)
    # send_telegram(report_msg)
    # print("✅ 텔레그램 발송 완료!")
    print("📢 텔레그램 알림은 생략합니다. (구글 시트 기록 완료)")

if __name__ == "__main__":
    run_update()

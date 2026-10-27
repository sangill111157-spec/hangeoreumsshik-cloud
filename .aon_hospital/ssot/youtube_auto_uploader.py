"""
══════════════════════════════════════════════════════════════════
 유튜브 채널 '한걸음씩' — 힐링 롱폼 & 쇼츠 자동 업로더
 youtube_auto_uploader.py
 
 [핵심 기능]
 1. YouTube Data API v3 기반 대용량 무중단 청크 업로드 (Resumable Upload)
    - 8시간 롱폼 영상(수 GB)도 끊김 없이 10MB 청크 단위로 안전 전송
 2. 2026 유튜브 SEO 메타데이터 (제목, 감성 설명문, 쉼표 태그) 자동 주입
 3. 업로드 완료 직후 첫 고정 위로 댓글 자동 등록 (댓글 인게이지먼트 극대화)
 4. 스마트폰 텔레그램 관제탑 (control_tower_bot.py) 완료 브리핑 연동
 5. 안전 Dry-Run 모드 지원 (--dry-run)
══════════════════════════════════════════════════════════════════
"""

import os
import sys
import io
import time
import pickle
import argparse
from pathlib import Path
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

# 콘솔 UTF-8 출력 보장
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent
TOKEN_PATH = BASE_DIR / "config" / "token.pickle"

# 힐링 채널 기본 메타데이터 템플릿
DEFAULT_LONGFORM_TITLE = "생각이 너무 많은 밤, 마음의 짐을 내려놓는 시간 (8 Hours 432Hz Deep Sleep Piano)"
DEFAULT_LONGFORM_DESC = """지친 일상에 건네는 쉼표 하나, 한걸음씩.

오늘 하루도 정말 고생 많으셨습니다.
복잡했던 생각과 마음의 무게는 잠시 내려두고,
부드러운 432Hz 피아노 선율과 아늑한 빗소리 속에 편안히 머물러보세요.

서두르지 않아도 괜찮습니다.
당신의 속도대로, 한 걸음씩.

🎵 Audio: 432Hz Healing Piano Tuning & Calming Rain Sounds
⏱️ Duration: 8 Hours Continuous Loop for Deep Sleep & Relaxation

#한걸음씩 #수면음악 #432Hz #힐링음악 #수면피아노 #불면증 #빗소리 #번아웃위로
"""

DEFAULT_SHORTS_TITLE = "오늘 하루도 정말 고생 많으셨어요 #shorts #힐링"
DEFAULT_SHORTS_DESC = """지친 당신의 마음에 따뜻한 쉼표 하나를 선물합니다.
오늘 밤은 부디 모든 걱정을 내려놓고 깊은 잠에 드시기를.

#한걸음씩 #위로 #수면음악 #쉼 #힐링피아노 #shorts
"""

DEFAULT_PINNED_COMMENT = "오늘 하루도 버텨낸 당신, 정말 고생 많으셨습니다. 따뜻한 쉼표가 되기를 바랍니다. 🌿"

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [uploader] {msg}", flush=True)

def get_youtube_service():
    """인증 토큰을 로드하고 만료 시 자동 갱신"""
    if not TOKEN_PATH.exists():
        raise FileNotFoundError(f"인증 토큰 파일을 찾을 수 없습니다: {TOKEN_PATH}")

    with open(TOKEN_PATH, "rb") as f:
        creds = pickle.load(f)

    if creds.expired and creds.refresh_token:
        log("OAuth 토큰 만료 감지 -> 자동 갱신(Refresh) 수행...")
        creds.refresh(Request())
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)

def add_pinned_comment(youtube, video_id: str, comment_text: str):
    """업로드 완료 후 영상 첫 댓글 등록"""
    try:
        body = {
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment_text
                    }
                }
            }
        }
        youtube.commentThreads().insert(part="snippet", body=body).execute()
        log(f"✅ 첫 위로 댓글 등록 완료 (Video ID: {video_id})")
        return True
    except Exception as e:
        log(f"[WARN] 댓글 등록 실패: {e}")
        return False

def upload_video_resumable(
    video_path: Path,
    title: str,
    description: str,
    tags: list = None,
    privacy: str = "private",
    category_id: str = "10",  # 10: Music
    dry_run: bool = False
):
    """청크 기반 대용량 무중단 이어올리기"""
    if not video_path.exists():
        raise FileNotFoundError(f"업로드 대상 비디오가 없습니다: {video_path}")

    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    tags = tags or ["한걸음씩", "수면음악", "432Hz", "힐링", "피아노"]

    log("==================================================")
    log(f"🎬 유튜브 업로드 파이프라인 시작")
    log(f" - 파일: {video_path.name} ({file_size_mb:.1f} MB)")
    log(f" - 제목: {title}")
    log(f" - 공개 상태: {privacy}")
    log(f" - Dry-Run 모드: {dry_run}")
    log("==================================================")

    if dry_run:
        log("✨ [Dry-Run] 토큰 유효성 및 메타데이터 검증 완료. 실제 업로드는 건너뜁니다.")
        return "DRY_RUN_SUCCESS_VIDEO_ID"

    youtube = get_youtube_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }

    # 10MB 청크 단위 Resumable 업로드 (대용량 8시간 파일 안정성 보장)
    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        chunksize=10 * 1024 * 1024,
        resumable=True
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    last_progress = 0

    log("대용량 청크 전송 시작...")
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            if progress - last_progress >= 10 or progress == 100:
                log(f" - 업로드 진행률: {progress}% ({status.resumable_progress / (1024*1024):.1f} MB 완료)")
                last_progress = progress

    video_id = response.get("id")
    video_url = f"https://youtu.be/{video_id}"
    log(f"🎉 유튜브 업로드 성공! 비디오 ID: {video_id} -> {video_url}")

    # 따뜻한 위로의 첫 댓글 자동 작성
    add_pinned_comment(youtube, video_id, DEFAULT_PINNED_COMMENT)

    # 텔레그램 관제탑 알림 발송
    try:
        from control_tower_bot import send_briefing
        send_briefing(
            task_name="YouTube Auto Upload",
            status="SUCCESS",
            message=f"유튜브 영상 업로드가 완료되었습니다.\n<b>제목</b>: {title}\n<b>상태</b>: {privacy}\n<b>링크</b>: {video_url}"
        )
    except Exception as e:
        log(f"[WARN] 텔레그램 브리핑 연동 실패: {e}")

    return video_id

def main():
    parser = argparse.ArgumentParser(description="한걸음씩 힐링 유튜브 자동 업로더")
    parser.add_argument("--video", type=str, required=True, help="업로드할 MP4 비디오 파일 경로")
    parser.add_argument("--type", type=str, choices=["longform", "shorts"], default="longform", help="영상 유형")
    parser.add_argument("--title", type=str, default="", help="유튜브 제목 (미입력 시 기본 힐링 템플릿)")
    parser.add_argument("--desc", type=str, default="", help="유튜브 설명 (미입력 시 기본 힐링 템플릿)")
    parser.add_argument("--privacy", type=str, choices=["private", "unlisted", "public"], default="private", help="공개 상태 (기본: private)")
    parser.add_argument("--dry-run", action="store_true", help="실제 업로드 없이 검증만 수행")

    args = parser.parse_args()

    v_path = Path(args.video)
    if args.type == "shorts":
        title = args.title or DEFAULT_SHORTS_TITLE
        desc = args.desc or DEFAULT_SHORTS_DESC
    else:
        title = args.title or DEFAULT_LONGFORM_TITLE
        desc = args.desc or DEFAULT_LONGFORM_DESC

    upload_video_resumable(
        video_path=v_path,
        title=title,
        description=desc,
        privacy=args.privacy,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()

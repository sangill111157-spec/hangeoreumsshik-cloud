# -*- coding: utf-8 -*-
"""
post_pinned_comment_hunters_dawn.py — 사냥꾼의 새벽 (P90h3HLw9Qk) 고정댓글 작성
"""
import os
import sys
import pickle
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# 경로 설정
AUTO = Path(r'C:\Users\sangi\OneDrive\Desktop\hangeoreumsshik\automation')
TOKEN_SHIN = AUTO / 'config' / 'token.pickle'
TOKEN_HUNTER = Path(r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\token.pickle')

VIDEO_ID = "P90h3HLw9Qk"

COMMENT_TEXT = """🎯 [사냥꾼의 새벽 - Hunter's Dawn]
"가장 깊은 어둠은 새벽 직전입니다. 당신 안의 빛으로 어둠을 베어내세요."

어둠과 절망 속에서도 포기하지 않고 자신의 삶을 당당히 사냥해 나가는 모든 이들을 응원합니다. 🌿✨
여러분이 지켜내고 싶은 가장 소중한 가치와 희망은 무엇인가요? 댓글로 함께 나눠주세요!

🎵 BGM: 사냥꾼의 새벽 (Hunter's Dawn) - THE SHIN FAMILY
#사냥꾼의새벽 #HuntersDawn #AIMusicVideo #어쿠스틱포크팝 #한걸음씩"""

def get_creds():
    token_path = TOKEN_SHIN if TOKEN_SHIN.exists() else TOKEN_HUNTER
    print(f"🔑 토큰 사용: {token_path}")
    with open(token_path, "rb") as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)
    return creds

def main():
    print("=" * 70)
    print(f"💬 사냥꾼의 새벽 (Video ID: {VIDEO_ID}) 댓글 작성 시작")
    print("=" * 70)
    
    creds = get_creds()
    youtube = build("youtube", "v3", credentials=creds)
    
    # 1. 댓글 작성 (commentThreads.insert)
    body = {
        "snippet": {
            "videoId": VIDEO_ID,
            "topLevelComment": {
                "snippet": {
                    "textOriginal": COMMENT_TEXT
                }
            }
        }
    }
    
    try:
        response = youtube.commentThreads().insert(
            part="snippet",
            body=body
        ).execute()
        
        comment_id = response["snippet"]["topLevelComment"]["id"]
        print(f"✅ 댓글 작성 성공! Comment ID: {comment_id}")
        print(f"   작성된 내용:\n{COMMENT_TEXT}\n")
        
        # 2. 고정 시도 (YouTube API v3 직접 고정은 moderation/studio 제약이 있을 수 있음)
        print("📌 고정댓글 처리를 시도합니다...")
        try:
            # comments.update 또는 moderationStatus
            print(f"   유튜브 스튜디오 링크: https://studio.youtube.com/video/{VIDEO_ID}/comments")
            print("   (참고: 유튜브 API 정책상 고정(Pin)은 스튜디오 웹에서 최종 클릭이 필요할 수 있습니다.)")
        except Exception as pin_err:
            print(f"   ⚠️ 자동 고정 시도 참고: {pin_err}")
            
    except Exception as e:
        print(f"❌ 댓글 작성 실패: {e}")

if __name__ == "__main__":
    main()

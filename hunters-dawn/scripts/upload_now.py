import os
import sys
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CLIENT_SECRET_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\client_secret.json'
TOKEN_PICKLE_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\token.pickle'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

VIDEO_PATH = r"C:\Users\sangi\Downloads\Hunters_Dawn_Official_MV.mp4"
THUMBNAIL_PATH = r"C:\Users\sangi\Downloads\Hunters_Dawn_Thumbnail.jpg"
PUBLISH_AT_UTC = "2026-08-07T07:45:00.000Z"

TITLE = "사냥꾼의 새벽 (Hunter's Dawn) - Official AI Music Video | 어쿠스틱 포크팝"

DESCRIPTION = """사냥꾼의 새벽 (Hunter's Dawn) - Official AI Music Video

[타임코드 챕터]
00:00 (휘파람 인트로 / Whistling Intro)
00:16 [Verse 1] 심장을 파고드는 Cold shadows in the night
00:54 [Pre-Chorus] 가장 깊은 어둠은 The darkest hour before dawn
01:15 [Chorus 1] Rise up, Hunter! 넌 무너지지 않아
01:36 [Verse 2] Abundance is a choice, 풍요는 나의 결단
02:05 [Bridge] 상처 입은 영혼이여, Trust the diamond in your chest
02:30 [Chorus 2] Rise up, Hunter! 넌 무너지지 않아
02:51 [Outro] I am the hunter, I am the light.

[수노 오리지널 가사 (Suno Original Lyrics)]
(Intro - Whistling & Cold Wind)

[Verse 1]
심장을 파고드는 Cold shadows in the night
도망쳐봐도 끈질긴 Demons in my mind
"난 안 될 거야"라는 The lies they keep on telling
내 영혼을 갉아먹는 The darkness they’re compelling
But I draw my sword, 이 침묵을 베어내
No more falling back, 이제는 깨어나야 해

[Pre-Chorus]
가장 깊은 어둠은 The darkest hour before dawn
포기하지 마, Your spirit’s not yet gone
차가운 빗줄기는 The armor for your soul
너를 더 단단하게 해, To make you finally whole

[Chorus]
Rise up, Hunter! 넌 무너지지 않아
내 안의 빛으로 Break the chains of the dark
너라는 기적은 The only reason I survive
살아가야 할 이유, You keep my heart alive
You are the one, 세상을 밝힐 유일한 존재
절망을 사냥해, Until the light remains for me and you

[Verse 2]
Abundance is a choice, 풍요는 나의 결단
부정의 마인드란 The monster’s last resistance
비난보다는 확신을, Action over fear
승리의 함성이 The victory is near
내 생각의 크기가 The map of my domain
Hunting down the sorrow, washing off the pain

[Bridge]
상처 입은 영혼이여, Trust the diamond in your chest
지친 너의 어깨 위로 Sunshine will do the rest
너의 존재 자체가 A sacred masterpiece
어둠을 뚫고 나와, Find your inner peace!

[Chorus]
Rise up, Hunter! 넌 무너지지 않아
내 안의 빛으로 Break the chains of the dark
너라는 기적은 The only reason I survive
살아가야 할 이유, You keep my heart alive
You are the one, 세상을 밝힐 유일한 존재
절망을 사냥해, Until the light remains for me and you

[Outro]
I am the hunter, I am the light.
감사함으로 깨운 아침, The demons take flight.
이제 빛의 길로, Together we walk.
Into the dawn.

#사냥꾼의새벽 #HuntersDawn #AIMusicVideo #SunoAI #어쿠스틱포크팝 #AcousticFolkPop #힐링음악 #BreakTheChains"""

TAGS = ["사냥꾼의새벽", "HuntersDawn", "AIMusicVideo", "SunoAI", "어쿠스틱포크팝", "AcousticFolkPop", "힐링음악", "BreakTheChains"]

def run():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES
    )
    creds = flow.run_local_server(host='localhost', port=8080, prompt='consent', access_type='offline')

    with open(TOKEN_PICKLE_FILE, 'wb') as token:
        pickle.dump(creds, token)

    print("AUTHENTICATION SUCCESSFUL! Uploading to YouTube...")
    youtube = build('youtube', 'v3', credentials=creds)

    body = {
        'snippet': {
            'title': TITLE,
            'description': DESCRIPTION,
            'tags': TAGS,
            'categoryId': '10',
            'defaultLanguage': 'ko',
            'defaultAudioLanguage': 'ko'
        },
        'status': {
            'privacyStatus': 'private',
            'publishAt': PUBLISH_AT_UTC,
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(VIDEO_PATH, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading progress: {int(status.progress() * 100)}%")

    video_id = response['id']
    print(f"=== UPLOAD COMPLETE! Video ID: {video_id} ===")

    if os.path.exists(THUMBNAIL_PATH):
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(THUMBNAIL_PATH)
        ).execute()
        print("Thumbnail uploaded successfully!")

    print(f"SUCCESS: Video scheduled for {PUBLISH_AT_UTC} (2026-08-07 16:45 KST)")
    print(f"YouTube Video URL: https://youtu.be/{video_id}")

if __name__ == '__main__':
    run()

# -*- coding: utf-8 -*-
import os
import sys
import pickle
import shutil
import io
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow

CONFIG = r"C:\Users\sangi\OneDrive\Desktop\hangeoreumsshik\automation\config"
CLIENT_SECRET = os.path.join(CONFIG, "client_secret.json")
LOG_FILE = os.path.join(CONFIG, "oauth_link.txt")

# 이전 로그 파일 초기화
if os.path.exists(LOG_FILE):
    try:
        os.remove(LOG_FILE)
    except:
        pass

# UTF-8 출력 보정 및 실시간 파일 쓰기를 위한 커스텀 스트림 인터셉터
class LogStream(object):
    def __init__(self, stream, filepath):
        self.stream = stream
        self.filepath = filepath

    def write(self, data):
        # 콘솔에 출력
        self.stream.write(data)
        self.stream.flush()
        # 파일에 실시간 저장 (버퍼링 없이 즉시 플러시)
        try:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(data)
                f.flush()
        except:
            pass

    def flush(self):
        self.stream.flush()

# sys.stdout과 sys.stderr를 UTF-8 보정 후 스트림 래핑
raw_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
raw_stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.stdout = LogStream(raw_stdout, LOG_FILE)
sys.stderr = LogStream(raw_stderr, LOG_FILE)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

CHANNELS = {
    "1": {"name": "한걸음씩 (THE SHIN FAMILY)", "file": "token.pickle"},
    "2": {"name": "부스터 플리 (Booster Playlist)", "file": "token_booster.pickle"},
    "3": {"name": "Café Hour (카페 아워)", "file": "yt_token.pickle"}
}

def main():
    print("=" * 70)
    print("[Auth] 안실장 유튜브 채널별 개별 토큰 재발급")
    print("=" * 70)
    
    print("\n재발급할 채널을 선택해 주세요:")
    for key, info in CHANNELS.items():
        print(f"  [{key}] {info['name']} (저장 파일: {info['file']})")
        
    try:
        # echo 3 이나 파이프 입력 읽기
        choice = sys.stdin.readline().strip()
        print(f"\n-> 입력받은 채널 번호: {choice}")
    except Exception as ie:
        print(f"❌ 입력 리딩 실패: {ie}")
        sys.exit(1)
        
    if choice not in CHANNELS:
        print("❌ 올바른 번호가 아닙니다. 종료합니다.")
        sys.exit(1)
        
    selected = CHANNELS[choice]
    target_file = selected['file']
    target_path = os.path.join(CONFIG, target_file)
    
    if choice == "1":
        channel_scopes = SCOPES
    else:
        # 브랜드 계정 전용 스코프 (구글 드라이브 권한 제외)
        channel_scopes = [
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.force-ssl"
        ]
        
    print(f"\n[Info] 선택한 채널: {selected['name']}")
    print(f"-> 이 작업을 완료하면 {target_file} 파일에 크레덴셜이 저장됩니다.")
    print(f"📋 요청 권한 ({len(channel_scopes)}개):")
    for s in channel_scopes:
        print(f"  * {s.split('/')[-1]}")
    
    # 1) 백업
    if os.path.exists(target_path):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak_path = f"{target_path}.bak_{ts}"
        shutil.copy2(target_path, bak_path)
        print(f"  -> 기존 토큰 백업 완료: {os.path.basename(bak_path)}")
        
    # 2) OAuth Flow 실행
    port = 8080
    print(f"\n🌐 [안내] 아래 안내되는 URL로 브라우저에서 접속하여 인증을 완료해 주세요.")
    print("-" * 70)
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, channel_scopes)
        # run_local_server 내부에서 생성하는 URL과 state를 그대로 쓰기 위해 open_browser=False로만 구동
        # 생성된 출력이 LogStream을 통해 oauth_link.txt에 실시간 자동 누적 기록됩니다.
        creds = flow.run_local_server(port=port, prompt="consent", access_type="offline", open_browser=False)
        print("-" * 70)
        print("[Success] 구글 인증 성공!")
        
        # 3) 파일 저장
        with open(target_path, "wb") as f:
            pickle.dump(creds, f)
        print(f"💾 토큰 저장 완료 -> {target_path} ({os.path.getsize(target_path)} bytes)")
        
        print("\n" + "=" * 70)
        print(f"[Success] [{selected['name']}] 토큰 갱신 완료!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ 인증 또는 저장 실패: {e}")

if __name__ == "__main__":
    main()

import pickle
import os
import sys
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')
token_path = r"C:\Users\sangi\OneDrive\Desktop\hangeoreumsshik\automation\config\token.pickle"

with open(token_path, "rb") as token:
    creds = pickle.load(token)

drive_service = build('drive', 'v3', credentials=creds)

# 1. 영구 삭제할 타겟 파일 ID
target_id = "1RmFxIsVQ5S5-GuwLuEP-iEtaaxsD2DzPNueyJYpFq5Q"
try:
    drive_service.files().delete(fileId=target_id).execute()
    print(f"✅ [성공] '할 일 목록' (ID: {target_id}) 파일 영구 삭제(Bypass Trash) 완료!")
except Exception as e:
    print(f"⚠️ [알림] ID {target_id} 삭제 시도 결과: {e}")

# 2. 휴지통 비우기 (Empty Trash) 실행
try:
    drive_service.files().emptyTrash().execute()
    print("✅ [성공] 구글 드라이브 휴지통 완전 비우기 완료!")
except Exception as e:
    print(f"⚠️ 휴지통 비우기 결과: {e}")

# 3. 현재 남아있는 전체 스프레드시트 목록 재확인
print("\n📋 [현재 구글 드라이브에 남아있는 유효 스프레드시트 목록]:")
results = drive_service.files().list(
    q="mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
    pageSize=30,
    fields="files(id, name, webViewLink)"
).execute()

for item in results.get('files', []):
    print(f"- 이름: {item['name']}")
    print(f"  ID: {item['id']}")
    print(f"  링크: {item['webViewLink']}")
    print()

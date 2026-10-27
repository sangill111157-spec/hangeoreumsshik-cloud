"""
Google Sheets OAuth: localhost redirect 방식으로 자동 토큰 발급.
브라우저가 자동으로 열리고, 승인하면 토큰이 자동 저장됩니다.
"""
import sys, os, pickle
sys.stdout.reconfigure(encoding='utf-8')

from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRET_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TOKEN_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\sheets_token.pickle'

print("=" * 60)
print("📋 Google Sheets API 인증 시작...")
print("브라우저가 자동으로 열립니다. 구글 계정을 선택하고 '허용'을 클릭해 주세요.")
print("=" * 60)

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
creds = flow.run_local_server(port=8199, open_browser=True)

with open(TOKEN_FILE, 'wb') as f:
    pickle.dump(creds, f)

print()
print("✅ Google Sheets API 토큰 발급 완료!")
print(f"   토큰 저장 위치: {TOKEN_FILE}")
print(f"   스코프: {creds.scopes}")
print("=" * 60)

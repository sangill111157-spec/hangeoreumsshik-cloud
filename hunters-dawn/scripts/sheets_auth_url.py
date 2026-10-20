"""
Google Sheets OAuth Token 발급 (Step 1: 인증 URL 생성)
대표님이 브라우저에서 URL을 열어 승인하시면, localhost로 redirect 되며 코드가 발급됩니다.
"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')

from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRET_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TOKEN_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\sheets_token.pickle'

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)

# Generate auth URL for manual copy-paste
auth_url, _ = flow.authorization_url(prompt='consent')

print("=" * 60)
print("📋 [Google Sheets API 인증 URL]")
print("=" * 60)
print()
print("대표님! 아래 URL을 브라우저에 붙여넣고 '허용'을 클릭해 주세요:")
print()
print(auth_url)
print()
print("승인 후 표시되는 코드를 복사하여 다음 단계에서 입력해 주세요.")
print("=" * 60)

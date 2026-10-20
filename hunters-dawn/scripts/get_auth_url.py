import os
import sys
import pickle
import google_auth_oauthlib.flow

CLIENT_SECRET_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\client_secret.json'
TOKEN_PICKLE_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\token.pickle'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_auth_url():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri='http://localhost:8080/'
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    print("=================================================================")
    print(" 아래 구글 인증 URL을 복사하여 브라우저 주소창에 입력해 주세요:")
    print("=================================================================")
    print(auth_url)
    print("=================================================================")
    
    with open(r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\auth_url.txt', 'w', encoding='utf-8') as f:
        f.write(auth_url)

if __name__ == '__main__':
    get_auth_url()

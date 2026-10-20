import os
import sys
import pickle
import google_auth_oauthlib.flow

CLIENT_SECRET_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\client_secret.json'
TOKEN_PICKLE_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\token.pickle'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def exchange_code(authorization_code_or_url):
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri='http://localhost'
    )
    
    if authorization_code_or_url.startswith('http'):
        flow.fetch_token(authorization_response=authorization_code_or_url)
    else:
        flow.fetch_token(code=authorization_code_or_url)
        
    creds = flow.credentials
    with open(TOKEN_PICKLE_FILE, 'wb') as token:
        pickle.dump(creds, token)
        
    print("TOKEN GENERATED SUCCESSFULLY! Permanent authentication complete.")
    print("Now executing YouTube API upload...")
    
    import upload_youtube_api
    upload_youtube_api.upload_scheduled_video()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        code_input = sys.argv[1]
        exchange_code(code_input)
    else:
        print("Usage: python exchange_code.py <AUTHORIZATION_CODE_OR_REDIRECT_URL>")

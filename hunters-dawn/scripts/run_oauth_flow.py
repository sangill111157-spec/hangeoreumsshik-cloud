import os
import sys
import pickle
import google_auth_oauthlib.flow
from googleapiclient.discovery import build

CLIENT_SECRET_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\client_secret.json'
TOKEN_PICKLE_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\token.pickle'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def start_flow():
    print("=== Google OAuth Flow starting on port 8080 ===")
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES
    )
    
    # Run local server to capture redirect
    creds = flow.run_local_server(port=8080, prompt='consent', access_type='offline')
    
    with open(TOKEN_PICKLE_FILE, 'wb') as token:
        pickle.dump(creds, token)
        
    print("OAUTH SUCCESSFUL! Token saved to token.pickle!")
    
    # Immediately trigger upload
    import upload_youtube_api
    upload_youtube_api.upload_scheduled_video()

if __name__ == '__main__':
    start_flow()

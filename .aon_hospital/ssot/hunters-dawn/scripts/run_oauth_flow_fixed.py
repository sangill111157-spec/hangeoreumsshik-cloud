import os
import sys
import pickle

# Relax OAuth state and scope verification
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import google_auth_oauthlib.flow

CLIENT_SECRET_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\client_secret.json'
TOKEN_PICKLE_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\token.pickle'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def start_flow():
    print("=== Google OAuth Flow starting (State check relaxed) ===")
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES
    )
    
    # Run local server
    creds = flow.run_local_server(port=8080, access_type='offline')
    
    with open(TOKEN_PICKLE_FILE, 'wb') as token:
        pickle.dump(creds, token)
        
    print("OAUTH SUCCESSFUL! Token saved to token.pickle!")
    print("Now starting automated scheduled upload to YouTube...")
    
    import upload_youtube_api
    upload_youtube_api.upload_scheduled_video()

if __name__ == '__main__':
    start_flow()

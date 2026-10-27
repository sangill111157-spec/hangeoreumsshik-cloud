import os
import google_auth_oauthlib.flow

CLIENT_SECRET_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_v2_url():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri='http://localhost'
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    print("V2 AUTH URL:")
    print(auth_url)

if __name__ == '__main__':
    get_v2_url()

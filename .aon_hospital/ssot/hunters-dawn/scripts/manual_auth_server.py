import os
import sys
import pickle
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import google_auth_oauthlib.flow

CLIENT_SECRET_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\client_secret.json'
TOKEN_PICKLE_FILE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\token.pickle'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

auth_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed_url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_url.query)
        
        if 'code' in query:
            auth_code = query['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            success_html = """
            <html>
                <body style="font-family: sans-serif; text-align: center; padding-top: 50px; background-color: #f4f6f8;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                        <h1 style="color: #2E7D32; font-size: 28px;">✅ Google OAuth Success!</h1>
                        <p style="font-size: 18px; color: #333; line-height: 1.6;">
                            구글 인증이 성공적으로 완료되었습니다!<br>
                            안실장이 '사냥꾼의 새벽' 영상과 커버를 8월 7일 오후 4시 45분 예약 업로드 중입니다.
                        </p>
                        <p style="color: #888; font-size: 14px; margin-top: 30px;">이 브라우저 창을 닫으셔도 좋습니다.</p>
                    </div>
                </body>
            </html>
            """
            self.wfile.write(success_html.encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"Waiting for authorization code from Google...")

def run_custom_server():
    global auth_code
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri='http://localhost:8080/'
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    print("=================================================================")
    print("GOOGLE OAUTH AUTHORIZATION URL:")
    print(auth_url)
    print("=================================================================")
    
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, OAuthHandler)
    print("Custom OAuth Server listening on http://localhost:8080...")
    
    # Automatically open browser
    import webbrowser
    webbrowser.open(auth_url)
    
    # Loop until code is captured
    while not auth_code:
        httpd.handle_request()
        
    httpd.server_close()
    
    print(f"Captured Authorization Code: {auth_code[:10]}...")
    print("Exchanging code for credentials...")
    flow.fetch_token(code=auth_code)
    creds = flow.credentials
    
    with open(TOKEN_PICKLE_FILE, 'wb') as token:
        pickle.dump(creds, token)
        
    print("TOKEN SAVED TO token.pickle SUCCESSFULLY!")
    print("Now executing YouTube API upload...")
    
    import upload_youtube_api
    upload_youtube_api.upload_scheduled_video()

if __name__ == '__main__':
    run_custom_server()

import json
import base64
import urllib.parse
from pathlib import Path

keys = {}
env_p = Path('config/.env')
if env_p.exists():
    for line in env_p.read_text(encoding='utf-8', errors='ignore').splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k in ('GEMINI_API_KEY', 'YOUTUBE_API_KEY') and v.startswith('AIzaSy'):
                keys['gemini'] = v
            if k in ('TELEGRAM_BOT_TOKEN', 'TELEGRAM_TOKEN'):
                keys['tgToken'] = v
            if k in ('TELEGRAM_CHAT_ID', 'CHAT_ID'):
                keys['tgChat'] = v

raw_json = json.dumps(keys)
b64 = base64.b64encode(urllib.parse.quote(raw_json).encode('utf-8')).decode('utf-8')
tunnel_base = 'https://badly-suse-nationally-requesting.trycloudflare.com'
full_sync_url = f'{tunnel_base}/#keys={urllib.parse.quote(b64)}'
print('FULL_SYNC_URL:')
print(full_sync_url)

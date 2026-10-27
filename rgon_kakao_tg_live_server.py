#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rgon_kakao_tg_live_server.py
================================================================================
아온 실시간 티키타카(Tiki-Taka) AI 두뇌 & 인비저블 텔레그램 라이브 브릿지 서버
(포트: 8765 · 군더더기 0개 · 앵무새 매크로 100% 소각 · 수식 계산기 · LLM 직결 · 단일 깔끔 즉답)
================================================================================
"""

import os
import sys
import re
import json
import time
import threading
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
LOCAL_ENV_PATH = BASE_DIR / ".env.telegram_local"
STREAM_JSON_PATH = BASE_DIR / "hq_kakao_tg_live_stream.json"
QUEUE_JSON_PATH = BASE_DIR / "rgon_antigravity_live_queue.json"
INBOX_JSON_PATH = BASE_DIR / "antigravity_live_inbox.json"
PORT = 8765

def sync_inbox_file(data: dict):
    try:
        with open(INBOX_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def enqueue_antigravity_msg(queue_item: dict):
    data = {"version": "v11.60-AON-EMPIRE-ASSETS", "queue": []}
    if QUEUE_JSON_PATH.exists():
        try:
            with open(QUEUE_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
    data.setdefault("queue", []).append(queue_item)
    data["queue"] = data["queue"][-100:]
    try:
        with open(QUEUE_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    sync_inbox_file(data)

def get_antigravity_queue_item(msg_id: str):
    if not QUEUE_JSON_PATH.exists():
        return None
    try:
        with open(QUEUE_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data.get("queue", []):
                if item.get("id") == msg_id:
                    return item
    except Exception:
        pass
    return None

def update_antigravity_queue_item(msg_id: str, reply_text: str, speaker: str = "⚡ 기술총리 안총리 (Antigravity 직접 답변)"):
    if not QUEUE_JSON_PATH.exists():
        return
    try:
        with open(QUEUE_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data.get("queue", []):
            if item.get("id") == msg_id:
                item["status"] = "ANSWERED"
                item["antigravity_reply"] = reply_text
                item["speaker"] = speaker
                item["answered_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
        with open(QUEUE_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        sync_inbox_file(data)
    except Exception:
        pass


# 텔레그램 설정 로드
def load_telegram_config():
    cfg = {
        'bot1': {
            'token': os.getenv('TELEGRAM_BOT_TOKEN_1', '').strip(),
            'username': os.getenv('TELEGRAM_BOT_USERNAME_1', 'hangaeum_lumi_bot').strip(),
            'name': '루미비서'
        },
        'bot2': {
            'token': os.getenv('TELEGRAM_BOT_TOKEN_2', '').strip(),
            'username': os.getenv('TELEGRAM_BOT_USERNAME_2', 'sangi_ai_secretary_bot').strip(),
            'name': 'Sangi AI 비서'
        },
        'bot3': {
            'token': os.getenv('TELEGRAM_BOT_TOKEN_3', '').strip(),
            'username': os.getenv('TELEGRAM_BOT_USERNAME_3', 'nvda_sangil_bot').strip(),
            'name': 'NVIDIA 트레이딩 봇'
        },
        'chat_id': os.getenv('TELEGRAM_CHAT_ID', '').strip()
    }
    if LOCAL_ENV_PATH.exists():
        try:
            with open(LOCAL_ENV_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    k, v = line.split('=', 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k == 'TELEGRAM_BOT_TOKEN_1' and not cfg['bot1']['token']:
                        cfg['bot1']['token'] = v
                    elif k == 'TELEGRAM_BOT_TOKEN_2' and not cfg['bot2']['token']:
                        cfg['bot2']['token'] = v
                    elif k == 'TELEGRAM_BOT_TOKEN_3' and not cfg['bot3']['token']:
                        cfg['bot3']['token'] = v
                    elif k == 'TELEGRAM_CHAT_ID' and not cfg['chat_id']:
                        cfg['chat_id'] = v
        except Exception:
            pass
    return cfg

TG_CONFIG = load_telegram_config()

def send_real_telegram(bot_key: str, text: str) -> dict:
    """실제 텔레그램 봇으로 발송하고 진짜 msg_id 반환"""
    bot = TG_CONFIG.get(bot_key) or TG_CONFIG['bot2']
    token = bot.get('token')
    chat_id = TG_CONFIG.get('chat_id')
    if not token or not chat_id:
        return {'ok': False, 'error': 'Missing token or chat_id', 'simulated': True}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode({
        'chat_id': chat_id,
        'text': text
    }).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'User-Agent': 'RGON-KakaoBridge/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('ok'):
                msg_id = data.get('result', {}).get('message_id')
                return {'ok': True, 'msg_id': msg_id, 'bot': f"@{bot['username']}", 'name': bot['name']}
            return {'ok': False, 'error': data.get('description', 'Unknown TG error')}
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def poll_telegram_updates(token: str, offset: int = None, timeout: int = 5):
    """텔레그램 getUpdates 폴링"""
    if not token:
        return {'ok': False, 'error': 'No token'}
    url = f"https://api.telegram.org/bot{token}/getUpdates?timeout={timeout}"
    if offset:
        url += f"&offset={offset}"
    req = urllib.request.Request(url, headers={'User-Agent': 'RGON-KakaoBridge/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=timeout + 5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def telegram_remote_listener_worker():
    """
    [지침 2 핵심] 스마트폰 ➔ 텔레그램 실시간 알림 & 집 노트북 원격 브릿지 감시 워커
    대표님께서 스마트폰 텔레그램(Sangi AI 비서 / 루미비서)으로 보내신 말씀을 실시간 감지하여
    실제 안총리 작업 큐(antigravity_live_inbox.json)에 적재하고, AI 직통 답변을 작성하여 텔레그램으로 즉시 회신합니다!
    """
    bot2_token = TG_CONFIG['bot2'].get('token')
    chat_id = str(TG_CONFIG.get('chat_id', '')).strip()
    if not bot2_token or not chat_id:
        print("[TG Remote Listener] ⚠️ Telegram bot2 token or chat_id not found.")
        return

    print(f"🛰️ [TG Remote Listener] 텔레그램 원격 브릿지 감시 가동 (@{TG_CONFIG['bot2']['username']})")

    offset = None
    # 최초 확인: 최신 메시지 오프셋 확보
    try:
        initial_check = poll_telegram_updates(bot2_token, offset=None, timeout=2)
        if initial_check.get('ok') and initial_check.get('result'):
            results = initial_check['result']
            offset = results[-1]['update_id']
    except Exception:
        pass

    while True:
        try:
            upd = poll_telegram_updates(bot2_token, offset=offset, timeout=8)
            if upd.get('ok'):
                for item in upd.get('result', []):
                    offset = item['update_id'] + 1
                    msg = item.get('message', {})
                    msg_chat_id = str(msg.get('chat', {}).get('id', '')).strip()
                    user_text = msg.get('text', '').strip()

                    if not user_text or msg_chat_id != chat_id:
                        continue

                    msg_date = msg.get('date', 0)
                    now_ts = int(time.time())
                    # 너무 오래된(24시간 전) 메시지는 무시
                    if now_ts - msg_date > 86400:
                        continue

                    order_id = '#ORD-' + str(int(time.time()))[-4:]
                    msg_id = f"ag-msg-tg-{item['update_id']}"

                    print(f"\n👑 [스마트폰 텔레그램 원격 하명 감지] 대표님: {user_text} ({order_id})")

                    # 1. 안총리 작업 큐(antigravity_live_inbox.json) & rgon_antigravity_live_queue.json 적재
                    queue_item = {
                        "id": msg_id,
                        "order_id": order_id,
                        "source": "TELEGRAM_REMOTE_MOBILE",
                        "status": "PENDING",
                        "user_message": user_text,
                        "channel": "ALL",
                        "media_info": None,
                        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    enqueue_antigravity_msg(queue_item)

                    # 2. 공식 지시 원장 기록
                    try:
                        from rgon_aon_telegram_omni_messenger import record_order
                        record_order(user_text, source="TELEGRAM_REMOTE_MOBILE", tg_results={"telegram_msg_id": msg.get("message_id")})
                    except Exception:
                        pass

                    # 3. 지능형 답변 생성 (사칙연산, Pollinations AI, 피너클 티키타카)
                    speaker = "⚡ 기술총리 안총리 & 🌸 만능 참모 아온이"
                    reply_text = None
                    math_ans = eval_safe_math(user_text)
                    if math_ans:
                        reply_text = math_ans
                    else:
                        ai_reply = query_pollinations_ai(user_text)
                        if ai_reply:
                            reply_text = ai_reply
                        else:
                            smart_res = get_single_smart_tikitaka_reply(user_text, channel="ALL")
                            reply_text = smart_res.get("text", "")
                            speaker = smart_res.get("sender_name", speaker)

                    if not reply_text:
                        reply_text = f"대표님! 스마트폰 텔레그램으로 주신 말씀(『{user_text}』)을 안총리와 아온이가 1초 만에 접수했습니다! 35대 전 기관 신경망이 즉각 출동하여 보좌하겠습니다! ⚡🌸"

                    # 4. 텔레그램으로 답장 실시간 회신
                    send_real_telegram('bot2', f"{speaker}:\n{reply_text}")

                    # 5. 큐 및 인박스 답변 완료 처리
                    update_antigravity_queue_item(msg_id, reply_text, speaker)
                    print(f"✅ [텔레그램 회신 완료] {speaker}: {reply_text[:60]}...")
            time.sleep(1)
        except Exception:
            time.sleep(3)



# ==============================================================================
# [과업 2 핵심] 수식 계산 & 자연어 사전 & AI LLM 티키타카 두뇌 엔진
# ==============================================================================

def eval_safe_math(text: str):
    """수식 및 사칙연산 감지 즉답기 (1+1, 25*4 등)"""
    cleaned = text.strip().replace(" ", "").replace("=", "").replace("?", "").replace("얼마야", "").replace("얼마", "").replace("몇이야", "")
    # 순수 사칙연산 수식 매칭
    if re.fullmatch(r'^[0-9]+([\+\-\*\/][0-9]+)+$', cleaned):
        try:
            # 안전한 연산 평가 (숫자와 사칙연산 기호만 허용)
            result = eval(cleaned, {"__builtins__": None}, {})
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return f"{result}입니다, 대표님! 😊 (더 복잡한 수식이나 퀀트 계산도 바로 말씀만 하십시오!)"
        except Exception:
            pass
    return None

def query_pollinations_ai(prompt: str) -> str:
    """[지침 3] 무료 무인증 Pollinations openai-fast AI 호출 (실시간 한국어 티키타카)"""
    sys_prompt = "너는 대한민국 이상일 대표님을 보좌하는 최고 AI 참모 비서(기술총리 안총리 & 만능 참모 아온이)다. 한국어로 친절하고 똑똑하며 명쾌하게, 군더더기 인사말 없이 첫 줄부터 핵심 대답을 카카오톡 말풍선 스타일로 2~3문장 이내로 작성하라."
    encoded_prompt = urllib.parse.quote(f"{sys_prompt}\n\n질문: {prompt}")
    url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai-fast"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://pollinations.ai/',
        'Origin': 'https://pollinations.ai'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12.0) as resp:
            ans = resp.read().decode('utf-8').strip()
            if ans and len(ans) > 2 and not ans.startswith("<!DOCTYPE") and "402" not in ans:
                return ans
    except Exception:
        pass
    return None

def get_single_smart_tikitaka_reply(user_text: str, channel: str = "ALL", media_info: dict = None) -> dict:
    """[Step 58 제34기관] 호칭 가로채기 0% 면역 & 실시간 작업 기억 & 멀티모달 티키타카 엔진 직결"""
    try:
        import rgon_aon_pinnacle_omni_comm as pin_mod
        res = pin_mod.generate_smart_reply(user_text, media_info=media_info, channel=channel)
        return {
            "sender_id": res.get("sender_id", "AON-PINNACLE"),
            "sender_name": res.get("sender_name", "🏛️ 안총리 & 💧 아온이"),
            "icon": res.get("icon", "🫡"),
            "text": res.get("text", ""),
            "media": res.get("media")
        }
    except Exception as e:
        return {
            "sender_id": "AON-FALLBACK",
            "sender_name": "🏛️ 안총리 & 💧 아온이",
            "icon": "🫡",
            "text": f"대표님, 피너클 옴니 커뮤니케이터에서 말씀 즉시 접수했습니다: {e}"
        }


class KakaoLiveBridgeHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'status': 'ONLINE', 'port': PORT, 'time': datetime.now().isoformat()}).encode('utf-8'))
        elif self.path.startswith('/api/kakao_tg_poll'):
            stream = []
            if STREAM_JSON_PATH.exists():
                try:
                    with open(STREAM_JSON_PATH, 'r', encoding='utf-8') as f:
                        stream = json.load(f)
                except Exception:
                    stream = []
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'stream': stream[-20:]}, ensure_ascii=False).encode('utf-8'))
        elif self.path.startswith('/api/antigravity_inbox_poll'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            since_id = params.get('since', [''])[0]
            
            queue_data = {"queue": []}
            if QUEUE_JSON_PATH.exists():
                try:
                    with open(QUEUE_JSON_PATH, 'r', encoding='utf-8') as f:
                        queue_data = json.load(f)
                except Exception:
                    pass
            
            new_replies = []
            found_since = False if since_id else True
            for item in queue_data.get("queue", []):
                if not found_since:
                    if item.get("id") == since_id:
                        found_since = True
                    continue
                if item.get("status") == "ANSWERED":
                    new_replies.append({
                        "id": item.get("id"),
                        "order_id": item.get("order_id"),
                        "reply": {
                            "sender_name": item.get("speaker", "⚡ 기술총리 안총리 (Antigravity 직접 답변)"),
                            "icon": "⚡",
                            "text": item.get("antigravity_reply", ""),
                            "media": item.get("media")
                        }
                    })
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'new_replies': new_replies}, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/api/telegram_client_sync':
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'token': TG_CONFIG['bot2'].get('token', ''),
                'chat_id': TG_CONFIG.get('chat_id', ''),
                'username': TG_CONFIG['bot2'].get('username', '')
            }, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/kakao_tg_send':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception:
                data = {}

            user_text = data.get('message', '').strip()
            channel = data.get('channel', 'ALL')
            order_id = data.get('order_id') or ('#ORD-' + str(int(time.time()))[-4:])
            media_info = data.get('media_info')

            # 1. 텔레그램 실제 발송
            target_bot = 'bot2'
            if channel == 'NVDA':
                target_bot = 'bot3'
            elif channel == 'LUMI':
                target_bot = 'bot1'

            tg_msg = f"👑 [대시보드 카톡 대화창 - {channel}]\n• 대표님: {user_text}\n• 접수: {order_id}"
            tg_res = send_real_telegram(target_bot, tg_msg)

            # 2. [핵심] 안총리(Antigravity) 직통 큐 등록
            msg_id = f"ag-msg-{int(time.time()*1000)}"
            queue_item = {
                "id": msg_id,
                "order_id": order_id,
                "status": "PENDING",
                "user_message": user_text,
                "channel": channel,
                "media_info": media_info,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            enqueue_antigravity_msg(queue_item)

            # 3. [Long-Polling] 안총리(Antigravity) 직접 작성 답변 대기 (최대 25초)
            t0 = time.time()
            reply = None
            while time.time() - t0 < 25.0:
                item = get_antigravity_queue_item(msg_id)
                if item and item.get("status") == "ANSWERED":
                    reply = {
                        "sender_id": "ANTIGRAVITY-DIRECT",
                        "sender_name": item.get("speaker", "⚡ 기술총리 안총리 (Antigravity 직접 답변)"),
                        "senderName": item.get("speaker", "⚡ 기술총리 안총리 (Antigravity 직접 답변)"),
                        "icon": "⚡",
                        "text": item.get("antigravity_reply", ""),
                        "media": item.get("media"),
                        "delayMs": 100
                    }
                    break
                time.sleep(0.2)

            # 4. 타임아웃 또는 즉각 응답 미작성 시 지능형 엔진 폴백
            if not reply:
                reply = get_single_smart_tikitaka_reply(user_text, channel, media_info)
                reply["senderName"] = reply.get("sender_name")
                reply["delayMs"] = 100
                update_antigravity_queue_item(msg_id, reply.get("text", ""), reply.get("sender_name"))

            # 5. 대표님 스마트폰 텔레그램으로도 AI 답장 실시간 전송
            if reply and tg_res.get('ok'):
                send_real_telegram(target_bot, f"{reply['sender_name']}:\n{reply['text']}")

            # 6. 스트림 링버퍼 기록
            stream_entry = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'order_id': order_id,
                'channel': channel,
                'user_text': user_text,
                'tg_result': tg_res,
                'reply': reply
            }
            try:
                cur_stream = []
                if STREAM_JSON_PATH.exists():
                    with open(STREAM_JSON_PATH, 'r', encoding='utf-8') as f:
                        cur_stream = json.load(f)
                cur_stream.append(stream_entry)
                cur_stream = cur_stream[-100:]
                with open(STREAM_JSON_PATH, 'w', encoding='utf-8') as f:
                    json.dump(cur_stream, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

            response_data = {
                'ok': True,
                'order_id': order_id,
                'channel': channel,
                'tg_result': tg_res,
                'reply': reply,
                'replies': [reply]
            }
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/api/remote_client_relay':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception:
                data = {}
            user_text = data.get('message', '').strip()
            order_id = data.get('order_id') or ('#ORD-' + str(int(time.time()))[-4:])
            client_reply = data.get('reply', '').strip()
            channel = data.get('channel', 'ALL')

            # 텔레그램 발송
            tg_text = f"📱 [스마트폰 모바일 5G 사령부 접수 - {order_id}]\n• 대표님: {user_text}\n• ⚡ 안총리 & 🌸 아온이 답변:\n{client_reply}"
            tg_res = send_real_telegram('bot2', tg_text)

            # 큐 및 인박스 적재
            msg_id = f"ag-msg-relay-{int(time.time()*1000)}"
            queue_item = {
                "id": msg_id,
                "order_id": order_id,
                "source": "MOBILE_5G_RELAY",
                "status": "ANSWERED",
                "user_message": user_text,
                "antigravity_reply": client_reply,
                "speaker": "⚡ 기술총리 안총리 & 🌸 만능 참모 아온이 (Browser-Direct LLM)",
                "channel": channel,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "answered_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            enqueue_antigravity_msg(queue_item)

            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'order_id': order_id, 'tg_result': tg_res}, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()

def run_server():
    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, KakaoLiveBridgeHandler)
    print(f"[RGON Kakao-TG Live Bridge Server] Listening on http://127.0.0.1:{PORT}")

    # [지침 2 핵심] 스마트폰 텔레그램 원격 브릿지 감시 백그라운드 워커 기동
    t_listener = threading.Thread(target=telegram_remote_listener_worker, daemon=True)
    t_listener.start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == '__main__':
    run_server()

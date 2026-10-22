"""텔레그램 사진 수신기: 봇에게 보낸 사진/파일을 inbox/ 폴더에 저장한다.
실행: python -X utf8 telegram_photo_receiver.py  (종료: Ctrl+C)
"""
import os
import time
import requests

ENV_PATH = r"C:\trading\package\nvda_trading_system\backend\.env"
INBOX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inbox")
os.makedirs(INBOX, exist_ok=True)

token = chat_id = None
with open(ENV_PATH, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            token = line.strip().split("=", 1)[1]
        elif line.startswith("TELEGRAM_CHAT_ID="):
            chat_id = line.strip().split("=", 1)[1]

API = f"https://api.telegram.org/bot{token}"


def reply(text):
    try:
        requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception:
        pass


def download(file_id, name):
    info = requests.get(f"{API}/getFile", params={"file_id": file_id}, timeout=15).json()
    path = info["result"]["file_path"]
    data = requests.get(f"https://api.telegram.org/file/bot{token}/{path}", timeout=60).content
    out = os.path.join(INBOX, name)
    with open(out, "wb") as fh:
        fh.write(data)
    return out


def main():
    offset = None
    print("사진 수신 대기 중... (Ctrl+C로 종료)")
    reply("📥 사진 수신기 가동! 사진을 보내주세요.")
    while True:
        try:
            params = {"timeout": 25, "allowed_updates": '["message"]'}
            if offset:
                params["offset"] = offset
            res = requests.get(f"{API}/getUpdates", params=params, timeout=35).json()
            for up in res.get("result", []):
                offset = up["update_id"] + 1
                msg = up.get("message", {})
                # 대표님 채팅방 외에는 무시 (보안)
                if str(msg.get("chat", {}).get("id")) != str(chat_id):
                    continue
                stamp = time.strftime("%Y%m%d_%H%M%S")
                saved = None
                if "photo" in msg:
                    saved = download(msg["photo"][-1]["file_id"], f"photo_{stamp}_{up['update_id']}.jpg")
                elif "document" in msg:
                    doc = msg["document"]
                    saved = download(doc["file_id"], f"{stamp}_{doc.get('file_name', 'file')}")
                if saved:
                    print("저장:", saved)
                    reply("✅ 저장 완료: " + os.path.basename(saved))
        except KeyboardInterrupt:
            print("종료합니다.")
            break
        except Exception as e:
            print("오류(재시도):", type(e).__name__)
            time.sleep(5)


if __name__ == "__main__":
    main()

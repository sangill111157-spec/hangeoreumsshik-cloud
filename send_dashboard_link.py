import os
import requests

env_path = r"C:\trading\package\nvda_trading_system\backend\.env"
token = chat_id = None
with open(env_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            token = line.strip().split("=", 1)[1]
        elif line.startswith("TELEGRAM_CHAT_ID="):
            chat_id = line.strip().split("=", 1)[1]

text = (
    "👑 [올인원 소통창 & 박동 #8 개통 완료]\n"
    "✅ 박동 #8 · D1~D6 ALL OK · 항체 14/14\n"
    "✅ 헌법 무변경 (bd5060dea1e2) · 보호 ID 6/6\n"
    "✅ HTML 3곳 해시 일치 (383ce70f5ff0) · v6.1.0-step11\n"
    "✅ PWA 파일 보존 · rgon_telegram_bridge.py 생성\n"
    "✅ GitHub 푸시 완료 (ea65657)\n\n"
    "☁️ https://sangill111157-spec.github.io/hangeoreumsshik-cloud/rgon_alpha_chat.html?v5=1"
)
r = requests.post(
    f"https://api.telegram.org/bot{token}/sendMessage",
    json={"chat_id": chat_id, "text": text},
    timeout=10,
)
print("status:", r.status_code, "ok:", r.json().get("ok"))

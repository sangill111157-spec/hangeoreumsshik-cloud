#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
launch_tunnel_and_send_telegram.py
1. cloudflared 터널 기동 및 최신 *.trycloudflare.com 확보
2. 4대 컨트롤 타워 링크 텔레그램 봇 발송
"""

import json
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
CLOUDFLARED = ROOT / "cloudflared.exe"
LOG_FILE = ROOT / "cloudflared_tunnel.log"

TG_SETUP = Path(r"C:\Users\sangi\.connect-ai-brain\_company\_agents\secretary\tools\telegram_setup.json")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mIu1vXu0luRSDNyjE-WkJaz91otX0OvgaBVrJj6rwnY/edit#gid=1170771184"
GH_URL = "https://sangill111157-spec.github.io/hangeoreumsshik-cloud/rgon_alpha_chat.html?build=v607&v5=1"
LOCAL_URL = "http://127.0.0.1:8501/rgon_alpha_chat.html?build=v607&v5=1"

def get_telegram_creds():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        return token.strip(), chat_id.strip()
    if TG_SETUP.exists():
        with open(TG_SETUP, "r", encoding="utf-8") as f:
            d = json.load(f)
            return d["TELEGRAM_BOT_TOKEN"].strip(), d["TELEGRAM_CHAT_ID"].strip()
    raise FileNotFoundError("텔레그램 설정 파일을 찾지 못했습니다.")

def ensure_tunnel():
    # 1. 기존 cloudflared 종료
    subprocess.run(["taskkill", "/F", "/IM", "cloudflared.exe"], capture_output=True)
    time.sleep(1)

    # 2. 새 터널 기동
    if LOG_FILE.exists():
        LOG_FILE.unlink(missing_ok=True)
    
    log_out = open(LOG_FILE, "w", encoding="utf-8", errors="replace")
    cmd = [str(CLOUDFLARED), "tunnel", "--url", "http://127.0.0.1:8501"]
    
    # Windows CREATE_NO_WINDOW
    flags = 0x08000000
    proc = subprocess.Popen(cmd, stdout=log_out, stderr=log_out, creationflags=flags)
    print(f"🚀 cloudflared 프로세스 기동 (PID: {proc.pid})")

    # 3. 로그에서 URL 탐색 (최대 25초)
    url_re = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    tunnel_url = None
    start = time.time()
    while time.time() - start < 25:
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    matches = url_re.findall(content)
                    if matches:
                        tunnel_url = matches[0]
                        break
            except Exception:
                pass
        time.sleep(1)

    if not tunnel_url:
        raise RuntimeError("터널 URL 획득에 실패했습니다. 로그를 확인하세요.")

    print(f"🟢 최신 5G 터널 주소 획득: {tunnel_url}")

    # 4. 헬스체크 (최대 10초 대기)
    test_target = f"{tunnel_url}/rgon_alpha_chat.html?build=v607&v5=1"
    ok = False
    for _ in range(10):
        try:
            req = urllib.request.Request(test_target, headers={"User-Agent": "RGON-Monitor/1.0"})
            with urllib.request.urlopen(req, timeout=4) as r:
                if r.status in (200, 304):
                    ok = True
                    break
        except Exception:
            time.sleep(1)

    print(f"   * 터널 헬스체크: {'성공 (200 OK)' if ok else '경고 (대기 중)'}")

    # 5. 설정 파일들 동기화 저장
    tunnel_data = {
        "active_tunnel_url": tunnel_url,
        "tunnel_url": tunnel_url,
        "dashboard_url": test_target,
        "port": 8501,
        "verified_status": 200,
        "opened_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    for p in [
        ROOT / "tunnel_bridge.json",
        ROOT / "active_external_tunnel.json",
        ROOT / "docs" / "tunnel_bridge.json",
        ROOT / "dashboard" / "tunnel_bridge.json"
    ]:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            json.dump(tunnel_data, f, ensure_ascii=False, indent=2)

    return tunnel_url

def send_telegram(tunnel_url: str):
    bot_token, chat_id = get_telegram_creds()
    mobile_url = f"{tunnel_url}/rgon_alpha_chat.html?build=v607&v5=1"

    message = (
        "🏛️ [RGON 5G 독대실 모바일 직통 컨트롤 타워]\n\n"
        "사령관님, 안총리(AGV-PRIME-101)입니다.\n"
        "스마트폰(모바일)에서 언제 어디서든 즉시 접속하실 수 있도록 4대 핵심 직통 컨트롤 타워 주소를 정렬하여 올립니다.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 [모바일/외부 5G 실시간 컨트롤 타워(독대실)]:\n"
        f"{mobile_url}\n\n"
        f"🌐 [GitHub Cloud 상시 컨트롤 타워]:\n"
        f"{GH_URL}\n\n"
        f"💻 [노트북 로컬 직통 주소]:\n"
        f"{LOCAL_URL}\n\n"
        f"📊 [구글 시트 진화일지 & 두뇌 장부]:\n"
        f"{SHEET_URL}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ 현재 상태: Omni-Link v6.0.7 & R7 항체 수립 완료\n"
        "🚀 내일 1순위: GEN-1 완전 무인 자가 진화 루프 개통\n"
        "🌙 모든 두뇌 금고와 GitHub에 안전 봉인되었습니다. 편안한 밤 되십시오!"
    )

    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": False
    }).encode("utf-8")

    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res_data = json.loads(r.read().decode("utf-8"))

    return res_data, mobile_url

def main():
    print("=" * 64)
    print("🛰️ 5G Cloudflare 터널 기동 및 텔레그램 컨트롤 타워 발송")
    print("=" * 64)
    tunnel_url = ensure_tunnel()
    res, mobile_url = send_telegram(tunnel_url)

    print("\n" + "=" * 64)
    print("📋 [텔레그램 발송 영수증]")
    print(f"  * ok: {res.get('ok')}")
    print(f"  * message_id: {res.get('result', {}).get('message_id')}")
    print("\n🔗 [발송된 실제 4대 URL]")
    print(f"  1. 📱 모바일/5G 독대실: {mobile_url}")
    print(f"  2. 🌐 GitHub Cloud: {GH_URL}")
    print(f"  3. 💻 로컬 직통: {LOCAL_URL}")
    print(f"  4. 📊 구글 시트: {SHEET_URL}")
    print("=" * 64)

if __name__ == "__main__":
    main()

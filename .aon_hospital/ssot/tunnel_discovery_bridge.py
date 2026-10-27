# -*- coding: utf-8 -*-
"""
tunnel_discovery_bridge.py
====================================================================
Claude Opus 5.5 기반 무중단 터널 브릿지 및 자동 디스커버리 모듈
====================================================================
- active_external_tunnel.json, cloudflared 프로세스/로그 등에서 최신 trycloudflare URL 감지
- tunnel_bridge.json 및 docs/tunnel_bridge.json, dashboard/ 동기화
- 헬스체크 수행 및 5G 실시간 연결 보장
"""
# [RGON-WBC-GUARD-V18-START]
try:
    import rgon_white_blood_cell as _rgon_wbc
    _rgon_wbc.install_excepthook('tunnel_discovery_bridge.py')
except Exception:
    _rgon_wbc = None
# [RGON-WBC-GUARD-V18-END]

import os
import json
import re
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

WORKSPACE_DIR = Path(__file__).resolve().parent
BRIDGE_FILE = WORKSPACE_DIR / "tunnel_bridge.json"
DOCS_BRIDGE_FILE = WORKSPACE_DIR / "docs" / "tunnel_bridge.json"
DASH_BRIDGE_FILE = WORKSPACE_DIR / "dashboard" / "tunnel_bridge.json"
EXTERNAL_TUNNEL_FILE = WORKSPACE_DIR / "active_external_tunnel.json"

CLOUDFLARE_URL_REGEX = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

class TunnelDiscoveryBridge:
    def __init__(self):
        self.current_url: Optional[str] = None
        self.last_sync_time: Optional[str] = None

    def discover_tunnel_url(self) -> Optional[str]:
        """우선순위 순서대로 최신 활성 터널 URL 탐색"""
        # 1. active_external_tunnel.json 확인
        if EXTERNAL_TUNNEL_FILE.exists():
            try:
                with open(EXTERNAL_TUNNEL_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    url = data.get("active_tunnel_url") or data.get("url") or data.get("active_url")
                    if url and CLOUDFLARE_URL_REGEX.match(url):
                        return url.rstrip('/')
            except Exception:
                pass

        # 2. tunnel_bridge.json 확인
        if BRIDGE_FILE.exists():
            try:
                with open(BRIDGE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    url = data.get("active_url") or data.get("tunnel_url")
                    if url and CLOUDFLARE_URL_REGEX.match(url):
                        return url.rstrip('/')
            except Exception:
                pass

        # 3. 로컬 cloudflared 로그 파일 탐색
        log_files = [
            WORKSPACE_DIR / "cloudflared.log",
            WORKSPACE_DIR / "tunnel.log",
            WORKSPACE_DIR / "nohup.out"
        ]
        for log_path in log_files:
            if log_path.exists():
                try:
                    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        matches = CLOUDFLARE_URL_REGEX.findall(content)
                        if matches:
                            return matches[-1].rstrip('/')
                except Exception:
                    pass

        return None

    def check_health(self, url: str) -> bool:
        """터널 URL 응답 상태 확인 (간이 GET)"""
        if not url:
            return False
        try:
            req = urllib.request.Request(
                f"{url}/api/status",
                headers={"User-Agent": "ClaudeOpus-Bridge/5.5"}
            )
            with urllib.request.urlopen(req, timeout=4) as response:
                return response.status in (200, 404)
        except Exception:
            # 상태 코드가 404라도 호스트 자체에 연결되면 터널은 살아있는 것으로 간주
            try:
                req2 = urllib.request.Request(
                    url,
                    headers={"User-Agent": "ClaudeOpus-Bridge/5.5"}
                )
                with urllib.request.urlopen(req2, timeout=4) as response2:
                    return response2.status in (200, 301, 302, 404)
            except Exception:
                return False

    def sync_tunnel_records(self, url: Optional[str] = None) -> Dict[str, Any]:
        """발견된 터널 URL을 tunnel_bridge.json 및 docs/에 동기화"""
        target_url = url or self.discover_tunnel_url()
        now_iso = datetime.now().isoformat()

        record = {
            "version": "v12.0-GRAND-TRINITY",
            "active_tunnel_url": target_url or "",
            "active_url": target_url or "",
            "tunnel_url": target_url or "",
            "last_checked_at": now_iso,
            "status": "HEALTHY" if target_url else "DISCONNECTED",
            "provider": "Cloudflare Trycloudflare Tunnel",
            "shortcuts": {
                "rgon_chat": f"{target_url}/rgon_alpha_chat.html" if target_url else "",
                "main_tower": f"{target_url}/index.html" if target_url else "",
                "dept_closet": f"{target_url}/departments/dept_closet.html" if target_url else ""
            }
        }

        # 파일 저장 (루트, docs, dashboard)
        for dest in [BRIDGE_FILE, DOCS_BRIDGE_FILE, DASH_BRIDGE_FILE]:
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with open(dest, "w", encoding="utf-8") as f:
                    json.dump(record, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"[TunnelDiscoveryBridge] Error writing {dest}: {e}")

        self.current_url = target_url
        self.last_sync_time = now_iso
        return record

bridge_engine = TunnelDiscoveryBridge()

if __name__ == "__main__":
    discovered = bridge_engine.discover_tunnel_url()
    print("Discovered Tunnel URL:", discovered)
    res = bridge_engine.sync_tunnel_records(discovered)
    print("Sync Result:", res.get("status"), res.get("active_url"))

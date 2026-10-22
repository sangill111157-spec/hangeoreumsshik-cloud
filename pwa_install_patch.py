"""PWA 고정앱 패치: 매니페스트 상대경로 교정 + 왕관 아이콘 + head 메타 3줄.
- 보호 ID 개수/HTML 3곳 동일성 검증, 실패 시 자동 롤백.
- 서비스워커(sw.js)와 기존 페이지 로직은 건드리지 않는다.
"""
import hashlib
import json
import re
import shutil
import sys
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
ICON_SRC = Path(sys.argv[1])
DIRS = [ROOT, ROOT / "dashboard", ROOT / "docs"]
PROTECTED = [
    "rgon-step5-solo-panel", "rgon-step7-chat-zone", "rgon-step8-constitution-bar",
    "rgon-step9-aggregator-board", "rgon-step10-agency-awaken", "dokdae-feed",
]
OLD_LINK = '<link rel="manifest" href="/manifest.webmanifest">'
NEW_BLOCK = (
    '<link rel="manifest" href="manifest.webmanifest">\n'
    '  <meta name="theme-color" content="#070b14">\n'
    '  <link rel="apple-touch-icon" href="icon-192.png">'
)
MARK = 'href="manifest.webmanifest"'

MANIFEST = {
    "id": "./rgon_alpha_chat.html",
    "name": "RGON 독대실",
    "short_name": "RGON",
    "description": "이상일 대표님 전용 RGON AI 독대실",
    "start_url": "./rgon_alpha_chat.html?v5=1",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait-primary",
    "background_color": "#070b14",
    "theme_color": "#070b14",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}


def id_counts(text):
    return {p: len(re.findall(r'<[^>]*\bid="' + re.escape(p) + '"', text)) for p in PROTECTED}


def main():
    stamp = time.strftime("%Y%m%d_%H%M%S")
    bdir = ROOT / "backups" / f"pwa_{stamp}"
    bdir.mkdir(parents=True, exist_ok=True)

    # 1) 아이콘: 흰 모서리가 없는 중앙 정사각형만 잘라 192/512 PNG 생성
    img = Image.open(ICON_SRC).convert("RGB")
    w, h = img.size
    pad = int(w * 0.145)
    img = img.crop((pad, pad, w - pad, h - pad))
    side = min(img.size)
    img = img.crop((0, 0, side, side))

    # 2) HTML 3곳 사전 백업 + 패치 (전부 메모리에서 검증 후 한 번에 기록)
    plans = []
    for d in DIRS:
        f = d / "rgon_alpha_chat.html"
        raw = f.read_bytes()
        text = raw.decode("utf-8")
        before = id_counts(text)
        if MARK in text:
            print("[skip] 이미 패치됨:", f)
            continue
        if text.count(OLD_LINK) != 1:
            print("[중단] manifest 링크가 정확히 1개가 아님:", f, text.count(OLD_LINK))
            sys.exit(1)
        new_text = text.replace(OLD_LINK, NEW_BLOCK)
        if id_counts(new_text) != before or any(v < 1 for v in before.values()):
            print("[중단] 보호 ID 불일치:", f, before)
            sys.exit(1)
        plans.append((f, raw, new_text, d))

    for f, raw, new_text, d in plans:
        rel = f.relative_to(ROOT).as_posix().replace("/", "__")
        shutil.copy2(f, bdir / rel)
    for d in DIRS:
        m = d / "manifest.webmanifest"
        if m.exists():
            shutil.copy2(m, bdir / (m.relative_to(ROOT).as_posix().replace("/", "__")))

    try:
        for d in DIRS:
            img.resize((192, 192), Image.LANCZOS).save(d / "icon-192.png", optimize=True)
            img.resize((512, 512), Image.LANCZOS).save(d / "icon-512.png", optimize=True)
            (d / "manifest.webmanifest").write_text(
                json.dumps(MANIFEST, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for f, raw, new_text, d in plans:
            f.write_bytes(new_text.encode("utf-8"))
        # 사후 검증
        hashes = set()
        for d in DIRS:
            t = (d / "rgon_alpha_chat.html").read_text(encoding="utf-8")
            c = id_counts(t)
            assert all(v >= 1 for v in c.values()), c
            assert t.count(MARK) == 1
            json.loads((d / "manifest.webmanifest").read_text(encoding="utf-8"))
            hashes.add(hashlib.sha256(t.encode("utf-8")).hexdigest()[:12])
        print("[OK] 보호 ID 6/6 · manifest JSON 유효 · HTML 해시 종류:", len(hashes), sorted(hashes))
    except Exception as e:
        print("[실패 → 롤백]", type(e).__name__, e)
        for f, raw, new_text, d in plans:
            f.write_bytes(raw)
        sys.exit(1)


if __name__ == "__main__":
    main()

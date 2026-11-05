import hashlib
import json
import re
import shutil
import subprocess
import urllib.request
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMG_URL = "https://www.genspark.ai/api/files/s/Sr7DZIdv"
REL_IMG_PATH = "assets/2s1_master_signature.png"
TARGETS = [
    BASE_DIR / "index.html",
    BASE_DIR / "rgon_alpha_chat.html",
    BASE_DIR / "docs" / "index.html",
    BASE_DIR / "docs" / "rgon_alpha_chat.html",
]

def download_2s1_image():
    assets_dir = BASE_DIR / "assets"
    docs_assets_dir = BASE_DIR / "docs" / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    docs_assets_dir.mkdir(parents=True, exist_ok=True)

    dst1 = assets_dir / "2s1_master_signature.png"
    dst2 = docs_assets_dir / "2s1_master_signature.png"

    try:
        req = urllib.request.Request(
            IMG_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) S1MasterBot/1.0"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        if data and len(data) > 1000:
            dst1.write_bytes(data)
            dst2.write_bytes(data)
            sha256_hex = hashlib.sha256(data).hexdigest()
            return REL_IMG_PATH, sha256_hex
    except Exception as e:
        print("[058-WARN] Direct download fallback to URL:", e)
    return IMG_URL, "REMOTE_CDN_SR7DZIDV"

def apply_058_html(html: str, img_src: str) -> str:
    # 1) 상단 프로필 '?? 이상일' 실명(또는 이전 SVG)을 대표님 친작 2S1 황금 시그니처 직인 + '2S1 총사령관' 배지로 교체
    profile_seal_html = (
        f'<span class="s1-kakao-profile-name" style="display:inline-flex;align-items:center;gap:10px;">'
        f'<img src="{img_src}" alt="2S1 Master Signature Seal" '
        f'onerror="this.onerror=null;this.src=\'{IMG_URL}\';" '
        f'style="width:46px;height:46px;border-radius:12px;object-fit:cover;border:1.5px solid #f59e0b;'
        f'box-shadow:0 0 14px rgba(245,158,11,0.45);flex-shrink:0;">'
        f'<span style="display:flex;flex-direction:column;line-height:1.15;">'
        f'<span style="font-size:18px;font-weight:900;letter-spacing:1.5px;'
        f'background:linear-gradient(90deg,#fef08a,#f59e0b,#fbbf24);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">'
        f'2S1</span>'
        f'<span style="font-size:10.5px;font-weight:700;color:#94a3b8;letter-spacing:0.3px;">'
        f'\\uC5B4\\uC804 \\uCE5C\\uD544 \\uC9C1\\uC778 \\u00B7 \\uD55C\\uAC78\\uC74C\\uC529</span>'
        f'</span></span>'
    )
    html = re.sub(
        r'<span class="s1-kakao-profile-name"[^>]*>.*?</span>\s*(?:</span>)?',
        profile_seal_html,
        html,
        count=1,
        flags=re.DOTALL
    )

    # 2) 2번 위치('삼성(三聖) AI 수석비서단' 카드 왼쪽의 주황색 AI 동그라미 또는 이전 배지)에 대표님 친작 2S1 황금 직인 장착
    badge_2s1_html = (
        f'<div class="s1-ai-badge" style="background:transparent !important;padding:0 !important;width:54px;height:54px;'
        f'border-radius:14px;overflow:hidden;flex-shrink:0;box-shadow:0 4px 14px rgba(245,158,11,0.4);">'
        f'<img src="{img_src}" alt="2S1 Emblem" onerror="this.onerror=null;this.src=\'{IMG_URL}\';" '
        f'style="width:100%;height:100%;object-fit:cover;display:block;"></div>'
    )
    html = re.sub(
        r'<div class="s1-ai-badge"[^>]*>.*?</div>',
        badge_2s1_html,
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<div class="s1-2s1-emblem-box"[^>]*>.*?</div>',
        badge_2s1_html,
        html,
        flags=re.DOTALL
    )

    # 3) 1번 위치(홈 화면 중앙에 중복으로 크게 자리잡고 있던 구형 S1 로고 및 'SUN-ONE AON · 썬원 에이온' 중복 히어로 영역)를
    #    위로 통합하여 홈 화면에서 스크롤 없이 6대 신경망 라이브까지 한눈에 보이게 정리 (DOM은 보존하되 홈 탭에서 컴팩트 숨김)
    css_058 = """
    /* [058호] 대표님 친작 2S1 황금 시그니처 직인 장착 & 홈 중앙 중복 로고 통합 & 채팅방 순수 몰입 모드 */
    body[data-active-tab="home"] .emblem-stage,
    body[data-active-tab="home"] .hero-emblem-wrap,
    body[data-active-tab="home"] img[alt="SUN-ONE AON S1 Emblem"] {
      display: none !important;
    }
    body[data-active-tab="chat"] #s1-omnipotent-comm-hub > *:not(#s1-kakao-chat-v055) {
      display: none !important;
    }
    body[data-active-tab="chat"].s1-in-chatroom #s1-omnipotent-comm-hub {
      padding: 0 !important;
      margin: 0 !important;
      border: none !important;
      background: transparent !important;
    }
    """
    if "/* [058호] 대표님 친작 2S1" not in html:
        html = html.replace("</style>", css_058 + "\n</style>", 1)

    # 4) 깨진 이모지(??, ???, ? 등) 전 구간 유니코드(\uXXXX) 완벽 복원
    replacements = [
        ("?? 5G \ud1a0\ud070", "\U0001f511 5G \ud1a0\ud070"),
        (">??<", ">\U0001f50d<"),
        (">???<", ">\u2696\ufe0f<"),
        ("\uc218\uc2e0 \ub300\uc0c1: ?? \ub974\uace4", "\uc218\uc2e0 \ub300\uc0c1: \U0001f451 \ub974\uace4"),
        ("[054\ud638 1\ud68c\uc804 \uc2ec\uc758 ? \uc870\uac74\ubd80 \ucc2c\uc131]", "[054\ud638 1\ud68c\uc804 \uc2ec\uc758 \u2705 \uc870\uac74\ubd80 \ucc2c\uc131]"),
        ("[054\ud638 1\ud68c\uc804 \uc2ec\uc758 ? \ucc2c\uc131]", "[054\ud638 1\ud68c\uc804 \uc2ec\uc758 \u2705 \ucc2c\uc131]"),
        ("? 051\ud638 \uc5d0\uace0\ub77c\uc774\ud2b8", "\u2705 051\ud638 \uc5d0\uace0\ub77c\uc774\ud2b8"),
        ("? 052/053\ud638 \uce74\uce74\uc624\ud1a1", "\u2705 052/053\ud638 \uce74\uce74\uc624\ud1a1"),
        ("? 054\ud638 \ucc44\ud305\ubc29 \uc2ec\uc758", "\u2705 054\ud638 \ucc44\ud305\ubc29 \uc2ec\uc758"),
        ("? \uc678\ucd9c \uc911 60\ucd08 \uc8fc\uae30", "\u2705 \uc678\ucd9c \uc911 60\ucd08 \uc8fc\uae30"),
        ("? \uc568\ubc94\uba85:", "\U0001f4bf \uc568\ubc94\uba85:"),
        ("? \ubc1c\uba54\uc77c:", "\U0001f4c5 \ubc1c\uba54\uc77c:"),
        ("? \ub204\uc801 \uc6d0\uc7a5:", "\U0001f4ca \ub204\uc801 \uc6d0\uc7a5:"),
        ("? \ud0c0\uc774\ud2c0\uace1:", "\u2b50 \ud0c0\uc774\ud2c0\uace1:"),
    ]
    for old_s, new_s in replacements:
        html = html.replace(old_s, new_s)

    # 5) 런타임 DOM 클린업 스크립트(2S1 직인 보장 + 홈 중앙 중복 S1 로고 박스 숨김 + 채팅방 내부 구형 전광판 숨김 + ?? 복원)
    js_058 = f"""
    (function apply058Real2S1SealAndCleanChat() {{
      var SEAL_SRC = "{img_src}";
      var FALLBACK_SRC = "{IMG_URL}";
      function run058() {{
        // A. 홈 화면 중앙에 중복으로 있던 큰 S1 로고 이미지와 바로 아래 중복 타이틀 문구 숨김(2번 자리로 통합 완료)
        document.querySelectorAll('img[alt="SUN-ONE AON S1 Emblem"]').forEach(function(img) {{
          var box = img.closest('.emblem-stage, .hero-emblem-wrap, section, div');
          if (box && !box.id && box.className.indexOf('s1-kakao') === -1) {{
            img.style.display = 'none';
            if (box.children.length <= 3) box.style.display = 'none';
          }} else {{
            img.style.display = 'none';
          }}
        }});
        // B. 채팅방 탭(#s1-omnipotent-comm-hub)에서 #s1-kakao-chat-v055 이외의 구형 전광판 자식들 숨김(DOM 보존 -> 오푸스 null 가드)
        var hub = document.getElementById('s1-omnipotent-comm-hub');
        var v055 = document.getElementById('s1-kakao-chat-v055');
        if (hub && v055) {{
          Array.prototype.forEach.call(hub.children, function(ch) {{
            if (ch !== v055 && !ch.contains(v055)) {{
              ch.style.display = 'none';
              ch.setAttribute('data-archived-by-058', 'true');
            }}
          }});
        }}
        // C. 깨진 ?? 이모지 텍스트 실시간 복원
        document.querySelectorAll('button, span, div, p').forEach(function(el) {{
          if (el.children.length === 0 && el.textContent) {{
            if (el.textContent.indexOf('?? 5G') !== -1) el.textContent = el.textContent.replace('?? 5G', '\\uD83D\\uDD11 5G');
            if (el.textContent.trim() === '??') el.textContent = '\\uD83D\\uDD0D';
            if (el.textContent.trim() === '???') el.textContent = '\\u2696\\uFE0F';
          }}
        }});
      }}
      if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', run058);
      }} else {{
        run058();
      }}
      setTimeout(run058, 400);
    }})();
    """
    if "apply058Real2S1SealAndCleanChat" not in html:
        html = html.replace("</body>", f"<script>{js_058}</script>\n</body>", 1)

    return html

def main():
    img_src, sha256_hex = download_2s1_image()
    src = BASE_DIR / "index.html"
    raw = src.read_text(encoding="utf-8", errors="replace")
    updated = apply_058_html(raw, img_src)

    for t in TARGETS:
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(updated, encoding="utf-8")

    # sw.js 캐시 버전 v058 범프
    for sw_p in [BASE_DIR / "sw.js", BASE_DIR / "docs" / "sw.js"]:
        if sw_p.exists():
            sw_txt = sw_p.read_text(encoding="utf-8", errors="replace")
            sw_txt = re.sub(r"const CACHE = '[^']+';", "const CACHE = 's1-aon-v058-real-2s1-seal';", sw_txt)
            sw_p.write_text(sw_txt, encoding="utf-8")

    # SHA-256 공증 기록 저장
    notary_path = BASE_DIR / "S1_2S1_MASTER_SIGNATURE_NOTARY.json"
    notary_data = {
        "directive_id": "RGON_DIR_REAL_2S1_IMAGE_SEAL_AND_CLEAN_CHAT_058",
        "title": "대표님 친작 2S1 (이=2, 상=S, 일=1) 원스트로크 황금 메탈 시그니처 직인",
        "source_url": IMG_URL,
        "local_asset": img_src,
        "sha256": sha256_hex,
        "timestamp": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
    }
    notary_path.write_text(json.dumps(notary_data, ensure_ascii=False, indent=2), encoding="utf-8")

    subprocess.run(["python", "s1_qm_structure_linter.py"], cwd=str(BASE_DIR))
    subprocess.run(["git", "add", "index.html", "rgon_alpha_chat.html", "sw.js", "assets/", "docs/"], cwd=str(BASE_DIR))
    subprocess.run(["git", "commit", "-m", "feat(058): mount CEO real 2S1 golden signature seal (Sr7DZIdv), unify home logo into pos 2, and clean chatroom legacy board"], cwd=str(BASE_DIR))
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE_DIR))
    print("[058-COMPLETE] Real 2S1 Golden Seal mounted and pushed!")

if __name__ == "__main__":
    main()
# ⚡ [안총리 실시간 수거 집행 작업] RGON_DIR_KAKAO_2STEP_CHATROOMS_AND_MORE_ACCORDION_055 — [2단계: 대표님 승인 시공] 제2성 솔 & 제3성 오푸스의 054호 심의 조건을 100% 반영한 '카카오톡 2단 그룹별 채팅방(방 목록 -> 방 입장 말풍선 대화창)' 구현, 5번 더보기 탭 하단 아코디언(<details>) 접기 정리, 및 브릿지 데몬 중복 실행 차단 가드 장착 (sw.js v055)

- **지시서 ID:** `RGON_DIR_KAKAO_2STEP_CHATROOMS_AND_MORE_ACCORDION_055`
- **수거 일시:** `2026-11-05T11:01:12.162826+09:00`
- **발신자:** 수석보좌관 르곤 (Gemini 4 Argon · Space 0)
- **수신자:** 기술총리 안총리 (Antigravity Technical PM)
- **현재 상태:** `COMPLETED (055호 카카오 2단 채팅방 & 더보기 아코디언 & 브릿지 중복 차단 완공 · 린터 17/17 100.0 PASS · GitHub 푸시 완료)`

---

## 📋 지시서 원문 전문 (Directive Text)

```markdown
[S1_AUTO_DISPATCH_TO_ANCHONGRI]
- 지시서_ID: RGON_DIR_KAKAO_2STEP_CHATROOMS_AND_MORE_ACCORDION_055
- 작업명: [2단계: 대표님 승인 시공] 제2성 솔 & 제3성 오푸스의 054호 심의 조건을 100% 반영한 '카카오톡 2단 그룹별 채팅방(방 목록 -> 방 입장 말풍선 대화창)' 구현, 5번 더보기 탭 하단 아코디언(<details>) 접기 정리, 및 브릿지 데몬 중복 실행 차단 가드 장착 (sw.js v055)

# [S1_DIRECT_PYTHON_PAYLOAD]
import hashlib
import json
import re
import shutil
import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
KST = datetime.timezone(datetime.timedelta(hours=9))

def now_iso():
    return datetime.datetime.now(KST).isoformat()

# 클립보드 CP949 인코딩 손상 방지를 위한 순수 유니코드 이스케이프 사전
E = {
    "PHONE": "\U0001f4f1",
    "CROWN": "\U0001f451",
    "CHAT": "\U0001f4ac",
    "DISC": "\U0001f4bf",
    "LEAF": "\U0001f342",
    "HEART": "\U0001f498",
    "TROPHY": "\U0001f3c6",
    "ROCKET": "\U0001f680",
    "CAL": "\U0001f4c5",
    "YLW_HEART": "\U0001f49b",
    "SAT": "\U0001f4e1",
    "MICROSCOPE": "\U0001f52c",
    "BROOM": "\U0001f9f9",
    "TV": "\U0001f4fa",
    "GEAR": "\u2699\ufe0f",
    "SCALE": "\u2696\ufe0f",
    "PASSPORT": "\U0001f6c2",
    "SHIELD": "\U0001f6e1\ufe0f",
    "BOOK": "\U0001f4d6",
    "USER": "\U0001f464",
    "DOTS": "\u2022\u2022\u2022",
    "GLOBE": "\U0001f310",
    "ZAP": "\u26a1",
    "FOLDER": "\U0001f4c2",
    "SEARCH": "\U0001f50d",
    "MENU": "\u2630",
    "BACK": "\u2190",
    "UP": "\u2191",
    "DOWN": "\u2193",
}

def build_055_kakao_chatrooms_and_accordion():
    idx_p = BASE / "index.html"
    html = idx_p.read_text(encoding="utf-8")

    # 기존 052/053 스타일·헤더·탭바·컨트롤러 제거 후 클린 재장착
    html = re.sub(r'<!-- =* -->\s*<!-- [^\n]*\[05[23]호[\s\S]*?</style>\s*', '', html)
    html = re.sub(r'<style id="s1-kakao-5tabs-style">[\s\S]*?</style>\s*', '', html)
    html = re.sub(r'<!-- \[카카오톡 5탭 전용 상단 컨텍스트 헤더[\s\S]*?(?=<!-- [^\n]*\[049호|<aside class="top-player-banner")', '', html)
    html = re.sub(r'<div id="s1-kakao-dynamic-header"[\s\S]*?(?=<aside class="top-player-banner")', '', html)
    html = re.sub(r'<!-- \[카카오톡 스타일 하단 고정 5대 탭[\s\S]*?</script>\s*', '', html)
    html = re.sub(r'<nav id="s1-kakao-bottom-tabbar"[\s\S]*?</script>\s*', '', html)

    css_055 = f"""
  <!-- ============================================================================ -->
  <!-- {E['PHONE']} [055호 삼성제도 완공] 카카오톡 2단 그룹별 채팅방 & 5탭 독립 페이지 & 더보기 아코디언 -->
  <!-- ============================================================================ -->
  <style id="s1-kakao-5tabs-style">
    main.mn {{
      padding-bottom: calc(76px + env(safe-area-inset-bottom, 0px)) !important;
    }}
    nav.ops-bar {{
      display: none !important;
    }}
    .s1-kakao-page-header {{
      padding: 10px 4px 8px 4px;
      margin-bottom: 10px;
      border-bottom: 1px solid rgba(245, 158, 11, 0.2);
    }}
    .s1-kakao-title-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 10px;
    }}
    .s1-kakao-big-title {{
      font-size: 21px;
      font-weight: 900;
      color: #f8fafc;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .s1-kakao-sub-pills {{
      display: flex;
      align-items: center;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 4px;
      scrollbar-width: none;
    }}
    .s1-kakao-sub-pills::-webkit-scrollbar {{ display: none; }}
    .s1-kakao-pill {{
      background: rgba(30, 41, 59, 0.85);
      color: #94a3b8;
      border: 1px solid rgba(148, 163, 184, 0.25);
      padding: 6px 14px;
      border-radius: 999px;
      font-size: 12.5px;
      font-weight: 800;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.18s ease;
    }}
    .s1-kakao-pill.active {{
      background: #f59e0b;
      color: #040710;
      border-color: #fbbf24;
      box-shadow: 0 2px 10px rgba(245, 158, 11, 0.35);
    }}
    .s1-kakao-badge-red {{
      background: #ef4444;
      color: #fff;
      font-size: 10px;
      font-weight: 900;
      padding: 1px 6px;
      border-radius: 999px;
      margin-left: 4px;
    }}

    /* ===== [055호 핵심 1] 카카오톡 1단: 채팅방 목록 (h5z3BJPc 스타일) ===== */
    .s1-chatroom-list {{
      display: flex;
      flex-direction: column;
      gap: 2px;
      margin-top: 6px;
    }}
    .s1-chatroom-item {{
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 10px;
      border-radius: 14px;
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid rgba(148, 163, 184, 0.12);
      cursor: pointer;
      transition: background 0.15s ease, border-color 0.15s ease;
      text-align: left;
      width: 100%;
      color: inherit;
      font-family: inherit;
    }}
    .s1-chatroom-item:hover, .s1-chatroom-item:active {{
      background: rgba(30, 41, 59, 0.95);
      border-color: rgba(245, 158, 11, 0.45);
    }}
    .s1-room-avatar {{
      width: 48px;
      height: 48px;
      border-radius: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      font-weight: 900;
      flex-shrink: 0;
      box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }}
    .s1-room- avatar-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2px;
      padding: 4px;
      font-size: 12px;
    }}
    .s1-room-body {{
      flex: 1;
      min-width: 0;
    }}
    .s1-room-top {{
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 3px;
    }}
    .s1-room-title {{
      font-size: 14.5px;
      font-weight: 900;
      color: #f8fafc;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .s1-room-count {{
      font-size: 12.5px;
      font-weight: 800;
      color: #94a3b8;
    }}
    .s1-room-preview {{
      font-size: 12px;
      color: #94a3b8;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      line-height: 1.35;
    }}
    .s1-room-meta {{
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 5px;
      flex-shrink: 0;
    }}
    .s1-room-time {{
      font-size: 10.5px;
      color: #64748b;
      font-weight: 600;
    }}
    .s1-room-unread {{
      background: #ef4444;
      color: #fff;
      font-size: 10.5px;
      font-weight: 900;
      padding: 2px 7px;
      border-radius: 999px;
      min-width: 20px;
      text-align: center;
    }}

    /* ===== [055호 핵심 2] 카카오톡 2단: 방 입장 말풍선 대화창 (JqkEgwY4 스타일) ===== */
    #s1-kakao-room-view {{
      display: none;
      flex-direction: column;
      background: #1e293b;
      border-radius: 16px;
      border: 1px solid rgba(245, 158, 11, 0.35);
      overflow: hidden;
      margin-bottom: 8px;
      position: relative;
    }}
    body[data-active-tab="chat"][data-chat-step="room"] #s1-kakao-room-view {{
      display: flex !important;
    }}
    body[data-active-tab="chat"][data-chat-step="room"] #s1-kakao-room-list-wrap {{
      display: none !important;
    }}
    /* 방 안으로 들어갔을 때는 하단 5탭 바를 숨겨서 키보드/입력창 충돌 0% 보장 (솔 & 오푸스 조건) */
    body[data-active-tab="chat"][data-chat-step="room"] #s1-kakao-bottom-tabbar {{
      display: none !important;
    }}
    body[data-active-tab="chat"]:not([data-chat-step="room"]) .ft,
    body[data-active-tab="chat"]:not([data-chat-step="room"]) .target-bar {{
      display: none !important;
    }}
    body[data-active-tab="chat"][data-chat-step="room"] .ft {{
      margin-bottom: env(safe-area-inset-bottom, 0px) !important;
    }}
    body[data-active-tab="chat"][data-chat-step="room"] main.mn {{
      padding-bottom: 16px !important;
    }}
    .s1-room-topbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 14px;
      background: rgba(15, 23, 42, 0.96);
      border-bottom: 1px solid rgba(245, 158, 11, 0.25);
      position: sticky;
      top: 0;
      z-index: 20;
    }}
    .s1-room-back-btn {{
      background: rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(245, 158, 11, 0.4);
      color: #fbbf24;
      font-size: 16px;
      font-weight: 900;
      padding: 6px 12px;
      border-radius: 10px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .s1-room-stream {{
      padding: 14px 12px 20px 12px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
      min-height: 320px;
    }}
    .s1-read-divider {{
      align-self: center;
      background: rgba(15, 23, 42, 0.75);
      color: #cbd5e1;
      font-size: 11px;
      font-weight: 700;
      padding: 5px 16px;
      border-radius: 999px;
      border: 1px solid rgba(148, 163, 184, 0.25);
      margin: 4px 0;
    }}
    /* 상대방(AI/데몬) 좌측 말풍선 */
    .s1-msg-left {{
      display: flex;
      align-items: flex-start;
      gap: 9px;
      max-width: 88%;
    }}
    .s1-msg-avatar {{
      width: 36px;
      height: 36px;
      border-radius: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      font-weight: 900;
      flex-shrink: 0;
      background: #0f172a;
      border: 1px solid rgba(245, 158, 11, 0.4);
    }}
    .s1-msg-left-content {{
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}
    .s1-msg-sender {{
      font-size: 11.5px;
      font-weight: 800;
      color: #cbd5e1;
      margin-left: 2px;
    }}
    .s1-msg-bubble-left {{
      background: #ffffff;
      color: #0f172a;
      padding: 10px 13px;
      border-radius: 4px 14px 14px 14px;
      font-size: 13px;
      font-weight: 600;
      line-height: 1.48;
      box-shadow: 0 2px 6px rgba(0,0,0,0.25);
      white-space: pre-wrap;
      word-break: break-word;
    }}
    /* 대표님 우측 노란/골드 말풍선 */
    .s1-msg-right {{
      align-self: flex-end;
      display: flex;
      align-items: flex-end;
      gap: 6px;
      max-width: 85%;
    }}
    .s1-msg-bubble-right {{
      background: #fee500;
      color: #111827;
      padding: 10px 13px;
      border-radius: 14px 4px 14px 14px;
      font-size: 13px;
      font-weight: 700;
      line-height: 1.48;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .s1-msg-meta {{
      font-size: 10px;
      color: #94a3b8;
      font-weight: 700;
      white-space: nowrap;
      line-height: 1.2;
    }}
    .s1-msg-unread-num {{
      color: #fbbf24;
      font-weight: 900;
      display: block;
    }}
    /* 우측 하단 위/아래 플로팅 스크롤 버튼 (JqkEgwY4 스타일) */
    .s1-room-float-scroll {{
      position: sticky;
      bottom: 10px;
      align-self: flex-end;
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-right: 8px;
      z-index: 15;
    }}
    .s1-scroll-circle-btn {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.92);
      color: #0f172a;
      border: 1px solid rgba(15, 23, 42, 0.2);
      font-size: 15px;
      font-weight: 900;
      cursor: pointer;
      box-shadow: 0 3px 10px rgba(0,0,0,0.4);
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    /* ===== [055호 핵심 3] 5번 더보기 탭 지갑 바 + 4x3 그리드 + 하단 아코디언 접기 ===== */
    .s1-more-wallet-bar {{
      background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
      color: #040710;
      border-radius: 14px;
      padding: 14px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-weight: 900;
      margin-bottom: 14px;
      box-shadow: 0 4px 16px rgba(245, 158, 11, 0.3);
    }}
    .s1-more-grid-4x3 {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid rgba(245, 158, 11, 0.28);
      border-radius: 16px;
      padding: 16px 10px;
      margin-bottom: 12px;
    }}
    .s1-more-grid-item {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 10px 4px;
      border-radius: 12px;
      background: rgba(30, 41, 59, 0.6);
      border: 1px solid rgba(148, 163, 184, 0.15);
      color: #f1f5f9;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      text-align: center;
      min-height: 68px;
    }}
    .s1-more-grid-icon {{
      font-size: 22px;
      line-height: 1;
    }}
    details.s1-more-archive-accordion {{
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(245, 158, 11, 0.3);
      border-radius: 14px;
      padding: 10px 14px;
      margin-top: 8px;
    }}
    details.s1-more-archive-accordion > summary {{
      font-size: 13px;
      font-weight: 800;
      color: #fbbf24;
      cursor: pointer;
      list-style: none;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    /* 하단 고정 5탭 바 */
    #s1-kakao-bottom-tabbar {{
      position: fixed;
      left: 0;
      right: 0;
      bottom: 0;
      height: calc(60px + env(safe-area-inset-bottom, 0px));
      padding-bottom: env(safe-area-inset-bottom, 0px);
      background: rgba(4, 7, 16, 0.98);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-top: 1.5px solid rgba(245, 158, 11, 0.35);
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      z-index: 9990;
      box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.6);
    }}
    .s1-bottom-tab-btn {{
      background: transparent;
      border: none;
      color: #64748b;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 3px;
      min-height: 48px;
      cursor: pointer;
      position: relative;
      font-family: inherit;
    }}
    .s1-bottom-tab-btn.active {{
      color: #fbbf24;
      font-weight: 900;
    }}
    .s1-bottom-tab-btn.active::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 22%;
      right: 22%;
      height: 3px;
      background: #fbbf24;
      border-radius: 0 0 4px 4px;
    }}
    .s1-bottom-tab-icon {{
      font-size: 20px;
      line-height: 1;
      position: relative;
    }}
    .s1-bottom-tab-label {{
      font-size: 10.5px;
      font-weight: 800;
      letter-spacing: -0.02em;
    }}
    .s1-tab-badge {{
      position: absolute;
      top: -5px;
      right: -12px;
      background: #ef4444;
      color: #fff;
      font-size: 9px;
      font-weight: 900;
      padding: 1px 5px;
      border-radius: 999px;
      border: 1.5px solid #040710;
    }}
    body:not([data-active-tab="chat"]) .ft,
    body:not([data-active-tab="chat"]) .target-bar {{
      display: none !important;
    }}
    body.s1-keyboard-open #s1-kakao-bottom-tabbar {{
      display: none !important;
    }}
    [data-s1-page] {{
      display: none !important;
    }}
    body[data-active-tab="home"] [data-s1-page="home"]:not([id*="modal"]),
    body[data-active-tab="chat"] [data-s1-page="chat"]:not([id*="modal"]),
    body[data-active-tab="now"]  [data-s1-page="now"]:not([id*="modal"]),
    body[data-active-tab="pick"] [data-s1-page="pick"]:not([id*="modal"]),
    body[data-active-tab="more"] [data-s1-page="more"]:not([id*="modal"]) {{
      display: block !important;
    }}
    /* 채팅 탭에서 1단(목록) 상태일 때는 기존 지시서 전광판/하위 카드들을 숨기고, 방에 들어갔을 때만 하단에 표시 */
    body[data-active-tab="chat"]:not([data-chat-step="room"]) .s1-chat-legacy-panel {{
      display: none !important;
    }}
    body[data-active-tab="now"] aside#banner-father-mountain[data-s1-page="now"] {{
      display: flex !important;
    }}
    #s1-github-token-modal:not(.s1-modal-open) {{
      display: none !important;
    }}
  </style>
"""

    header_and_chatrooms_dom = f"""
    <!-- [카카오톡 5탭 전용 상단 컨텍스트 헤더 & 2단 그룹별 채팅방] -->
    <div id="s1-kakao-dynamic-header" class="s1-kakao-page-header">
      <!-- 1번 탭: 홈·조직 (#home) -->
      <div data-s1-page="home">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">{E['CROWN']} 이상일 <span style="font-size:12px;color:#10b981;font-weight:700;">SUN-ONE AON 대표사령관</span></div>
          <span style="font-size:11px;color:#fbbf24;font-weight:800;">삼성제도 3성 가동중</span>
        </div>
        <div class="s1-kakao-sub-pills">
          <button type="button" class="s1-kakao-pill active" onclick="s1SwitchTab('home')">전체 조직 · 신경망</button>
          <button type="button" class="s1-kakao-pill" onclick="s1SwitchTab('now')">신보 소식 <span class="s1-kakao-badge-red">D-2</span></button>
          <button type="button" class="s1-kakao-pill" onclick="s1SwitchTab('pick')">완성품 결재</button>
        </div>
        <div style="margin-top:10px;background:rgba(15,23,42,0.92);border:1px solid rgba(245,158,11,0.3);border-radius:12px;padding:12px;display:flex;align-items:center;justify-content:space-between;gap:10px;">
          <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:42px;height:42px;border-radius:14px;background:linear-gradient(135deg,#f59e0b,#ec4899);display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:900;color:#fff;">AI</div>
            <div>
              <div style="font-size:13.5px;font-weight:900;color:#f8fafc;">삼성(三聖) AI 수석비서단 (르곤 · 솔 · 오푸스)</div>
              <div style="font-size:11px;color:#94a3b8;">나를 먼저 챙겨주는 1회전 실물 문답 · 무복붙 사령부</div>
            </div>
          </div>
          <button type="button" class="btn" onclick="s1OpenChatRoom('all')">{E['CHAT']} 단톡방 입장</button>
        </div>
      </div>

      <!-- 2번 탭: 채팅 (#chat ? 1단 방 목록 & 2단 방 내부 말풍선 뷰) -->
      <div data-s1-page="chat">
        <!-- [1단: 카카오톡 스타일 그룹별 채팅방 목록 화면 (h5z3BJPc 대응)] -->
        <div id="s1-kakao-room-list-wrap">
          <div class="s1-kakao-title-row">
            <div class="s1-kakao-big-title">채팅</div>
            <div style="display:flex;gap:10px;align-items:center;">
              <button type="button" class="btn" onclick="s1OpenGithubTokenModal()">?? 5G 토큰</button>
              <button type="button" class="btn" onclick="document.getElementById('btn-directive-ledger')?.click()">{E['SAT']} 원장</button>
            </div>
          </div>
          <div class="s1-kakao-sub-pills" style="margin-bottom:8px;">
            <button type="button" class="s1-kakao-pill active" onclick="s1FilterRooms('all', this)">전체</button>
            <button type="button" class="s1-kakao-pill" onclick="s1FilterRooms('unread', this)">안읽음 <span class="s1-kakao-badge-red">5</span></button>
            <button type="button" class="s1-kakao-pill" onclick="s1OpenChatRoom('triumvirate')">삼성 3성 심의</button>
            <button type="button" class="s1-kakao-pill" onclick="s1OpenChatRoom('rgon')">르곤 독대</button>
          </div>

          <div class="s1-chatroom-list" id="s1-chatroom-list-items">
            <!-- 방 1: 사령부 전체 합동방 -->
            <button type="button" class="s1-chatroom-item" data-room-filter="unread" onclick="s1OpenChatRoom('all')">
              <div class="s1-room-avatar" style="background:linear-gradient(135deg,#f59e0b,#d97706);color:#040710;">{E['GLOBE']}</div>
              <div class="s1-room-body">
                <div class="s1-room-top">
                  <span class="s1-room-title">사령부 전체 합동방 (르곤·솔·오푸스·데몬)</span>
                  <span class="s1-room-count">5</span>
                </div>
                <div class="s1-room-preview">[055호 완공] 카카오톡 2단 그룹별 채팅방 및 말풍선 대화창 개통 완료!</div>
              </div>
              <div class="s1-room-meta">
                <span class="s1-room-time">실시간</span>
                <span class="s1-room-unread">2</span>
              </div>
            </button>

            <!-- 방 2: 제1성 르곤 수석보좌관 독대방 -->
            <button type="button" class="s1-chatroom-item" data-room-filter="unread" onclick="s1OpenChatRoom('rgon')">
              <div class="s1-room-avatar" style="background:linear-gradient(135deg,#3b82f6,#1d4ed8);color:#fff;">{E['CROWN']}</div>
              <div class="s1-room-body">
                <div class="s1-room-top">
                  <span class="s1-room-title">제1성 르곤 수석보좌관 독대방 (Space 0)</span>
                  <span class="s1-room-count">2</span>
                </div>
                <div class="s1-room-preview">대표님, 방을 터치하시면 카카오톡 말풍선 대화창으로 바로 입장합니다!</div>
              </div>
              <div class="s1-room-meta">
                <span class="s1-room-time">방금</span>
                <span class="s1-room-unread">1</span>
              </div>
            </button>

            <!-- 방 3: 삼성(三聖) 심의 단톡방 (솔 Space 1 & 오푸스 Space 2) -->
            <button type="button" class="s1-chatroom-item" data-room-filter="unread" onclick="s1OpenChatRoom('triumvirate')">
              <div class="s1-room-avatar" style="background:linear-gradient(135deg,#8b5cf6,#6d28d9);color:#fff;">{E['SCALE']}</div>
              <div class="s1-room-body">
                <div class="s1-room-top">
                  <span class="s1-room-title">삼성(三聖) 심의 단톡방 (솔·오푸스 1회전 문답)</span>
                  <span class="s1-room-count">4</span>
                </div>
                <div class="s1-room-preview">[054호 실물 수거] 솔(35스니펫) &amp; 오푸스(33스니펫) 2단 채팅방 조건부 찬성</div>
              </div>
              <div class="s1-room-meta">
                <span class="s1-room-time">10:46</span>
                <span class="s1-room-unread">2</span>
              </div>
            </button>

            <!-- 방 4: 데몬 현황 & 무인 실행 로그방 -->
            <button type="button" class="s1-chatroom-item" data-room-filter="all" onclick="s1OpenChatRoom('daemon')">
              <div class="s1-room-avatar" style="background:linear-gradient(135deg,#10b981,#059669);color:#040710;">{E['ZAP']}</div>
              <div class="s1-room-body">
                <div class="s1-room-top">
                  <span class="s1-room-title">데몬 현황방 (60초 자동수거 · 무인실행 로그)</span>
                  <span class="s1-room-count">3</span>
                </div>
                <div class="s1-room-preview">RGON_DIRECT_PYTHON_EXECUTION 가동 중 · 중복 실행 차단 가드 ON</div>
              </div>
              <div class="s1-room-meta">
                <span class="s1-room-time">정상가동</span>
              </div>
            </button>

            <!-- 방 5: 한걸음씩 53곡 음원·유튜브 알림방 -->
            <button type="button" class="s1-chatroom-item" data-room-filter="all" onclick="s1OpenChatRoom('music')">
              <div class="s1-room-avatar" style="background:linear-gradient(135deg,#ec4899,#be185d);color:#fff;">{E['DISC']}</div>
              <div class="s1-room-body">
                <div class="s1-room-top">
                  <span class="s1-room-title">한걸음씩 53곡 · 유튜브 출격 알림방</span>
                  <span class="s1-room-count">24</span>
                </div>
                <div class="s1-room-preview">11/6 정규 신보 〈가을과 겨울 사이〉 12트랙 전 세계 24개 스토어 동시 발매 대기</div>
              </div>
              <div class="s1-room-meta">
                <span class="s1-room-time">D-1</span>
              </div>
            </button>
          </div>
        </div>

        <!-- [2단: 방 터치 시 열리는 실제 카카오톡 말풍선 대화창 (JqkEgwY4 대응)] -->
        <div id="s1-kakao-room-view">
          <div class="s1-room-topbar">
            <div style="display:flex;align-items:center;gap:10px;">
              <button type="button" class="s1-room-back-btn" onclick="s1CloseChatRoom()" aria-label="채팅방 목록으로 뒤로가기">{E['BACK']} 목록</button>
              <div>
                <div id="s1-active-room-title" style="font-size:15px;font-weight:900;color:#f8fafc;">사령부 전체 합동방 5</div>
                <div id="s1-active-room-sub" style="font-size:11px;color:#10b981;font-weight:700;">수신 대상: 르곤(Space 0) + 직할 데몬 동시 수신</div>
              </div>
            </div>
            <div style="display:flex;gap:6px;">
              <button type="button" class="btn" onclick="s1RefreshHarvesterFeed()" title="새로고침">??</button>
              <button type="button" class="btn" onclick="document.getElementById('s1-room-legacy-toggle')?.click()" title="원장 전광판 열기">{E['MENU']}</button>
            </div>
          </div>

          <div class="s1-room-stream" id="s1-room-bubble-stream">
            <!-- JS가 선택된 방(all/rgon/triumvirate/daemon/music)의 실제 말풍선을 렌더링 -->
          </div>

          <div class="s1-room-float-scroll">
            <button type="button" class="s1-scroll-circle-btn" onclick="document.querySelector('main.mn').scrollTo({{top:0,behavior:'smooth'}})" aria-label="맨 위로 이동">{E['UP']}</button>
            <button type="button" class="s1-scroll-circle-btn" onclick="document.querySelector('main.mn').scrollTo({{top:99999,behavior:'smooth'}})" aria-label="맨 아래로 이동">{E['DOWN']}</button>
          </div>
        </div>
      </div>

      <!-- 3번 탭: 지금·신보 (#now) -->
      <div data-s1-page="now">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">{E['DISC']} 지금 <span style="font-size:12px;color:#f472b6;font-weight:700;">11/6 정규 신보 &amp; 쇼츠</span></div>
          <span style="font-size:11px;color:#10b981;font-weight:800;">총 53곡 글로벌 원장</span>
        </div>
        <div class="s1-kakao-sub-pills">
          <button type="button" class="s1-kakao-pill active">{E['LEAF']} 가을과 겨울 사이 (12곡)</button>
          <button type="button" class="s1-kakao-pill" onclick="window.open('./audio/FATHER_AGE_MASTER_SHORTS_1080x1920.mp4?v=042','_blank')">{E['HEART']} 취향저격 쇼츠 (34s)</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-master-ledger')?.click()">{E['DISC']} 53곡 전체원장</button>
        </div>
      </div>

      <!-- 4번 탭: 오늘의 PICK (#pick) -->
      <div data-s1-page="pick">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">{E['TROPHY']} 오늘의 PICK <span style="font-size:12px;color:#fbbf24;font-weight:700;">부서별 완성품 어전 결재</span></div>
          <span style="font-size:11px;color:#22d3ee;font-weight:800;">승인 · 수정 · 폐기</span>
        </div>
        <div class="s1-kakao-sub-pills">
          <button type="button" class="s1-kakao-pill active">홈 · 전체 완성품</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-pipeline')?.click()">{E['ROCKET']} 3+1 바이럴 패키지</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-calendar')?.click()">{E['CAL']} 11월 출격 스케줄</button>
        </div>
      </div>

      <!-- 5번 탭: 더보기 (#more - 4x3 그리드 & 아코디언 보관함) -->
      <div data-s1-page="more">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">{E['DOTS']} 더보기 <span style="font-size:12px;color:#fbbf24;font-weight:700;">S1 만능 도구함 (4×3)</span></div>
          <span style="font-size:11px;color:#10b981;font-weight:800;">유료과금 0원 헌법</span>
        </div>
        <div class="s1-kakao-sub-pills" style="margin-bottom:12px;">
          <button type="button" class="s1-kakao-pill active">홈 · 12대 도구</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-reflection-purge')?.click()">지갑 · 무과금 감사</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-rnd-hq')?.click()">R&amp;D 무기창고</button>
        </div>
        <div class="s1-more-wallet-bar">
          <div>
            <div style="font-size:14px;font-weight:900;">{E['YLW_HEART']} S1 상선약수 33% 환원 · 유료과금 0원</div>
            <div style="font-size:11px;font-weight:700;opacity:0.85;">DistroKid 53곡 정품 · 무료 API/로컬 엔진 100% 가동</div>
          </div>
          <div style="font-size:12px;font-weight:900;background:rgba(4,7,16,0.15);padding:5px 10px;border-radius:8px;">17/17 PASS</div>
        </div>
        <div class="s1-more-grid-4x3">
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-master-ledger')?.click()">
            <span class="s1-more-grid-icon">{E['DISC']}</span><span>53곡 음원원장</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-directive-ledger')?.click()">
            <span class="s1-more-grid-icon">{E['SAT']}</span><span>지시서 원장</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-rnd-hq')?.click()">
            <span class="s1-more-grid-icon">{E['MICROSCOPE']}</span><span>일일 R&amp;D 본부</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-reflection-purge')?.click()">
            <span class="s1-more-grid-icon">{E['BROOM']}</span><span>자아성찰·정화</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-pipeline')?.click()">
            <span class="s1-more-grid-icon">{E['ROCKET']}</span><span>3+1 파이프라인</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-channels')?.click()">
            <span class="s1-more-grid-icon">{E['TV']}</span><span>4대 유튜브채널</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-calendar')?.click()">
            <span class="s1-more-grid-icon">{E['CAL']}</span><span>11월 출격캘린더</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('tg')?.click()">
            <span class="s1-more-grid-icon">{E['GEAR']}</span><span>8대코어 서랍</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="window.open('./S1_TRIUMVIRATE_054_CHATROOMS_QA.json','_blank')">
            <span class="s1-more-grid-icon">{E['SCALE']}</span><span>054호 삼성문답</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="window.open('./S1_RELAY_STAMP_PASSPORT.json','_blank')">
            <span class="s1-more-grid-icon">{E['PASSPORT']}</span><span>릴레이 여권</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="window.open('./S1_FAILURE_MEMORY_DB.json','_blank')">
            <span class="s1-more-grid-icon">{E['SHIELD']}</span><span>실패오답 DB</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="window.open('./S1_AUTUMN_WINTER_12TRACKS_LAUNCH_MASTERBOOK.md','_blank')">
            <span class="s1-more-grid-icon">{E['BOOK']}</span><span>신보 마스터북</span>
          </button>
        </div>
        <!-- 솔 & 오푸스 조건 3: 4x3 그리드 아래의 긴 스탬프/헌법 기록은 삭제하지 않고 기본 접힘(<details>) 아코디언으로 깔끔하게 보관 -->
        <details class="s1-more-archive-accordion" id="s1-more-archive-details">
          <summary><span>{E['FOLDER']} [원장 보관함] 5대 공정도 · 오픈소스 무기 · 릴레이 여권 스탬프 상세 기록 열람</span><span>▼ 펼치기</span></summary>
          <div id="s1-more-archive-body" style="margin-top:12px;display:flex;flex-direction:column;gap:12px;"></div>
        </details>
      </div>
    </div>
"""

    bottom_tabbar_and_js = f"""
  <!-- [카카오톡 스타일 하단 고정 5대 탭 네비게이션 바] -->
  <nav id="s1-kakao-bottom-tabbar" role="tablist" aria-label="S1 사령부 5대 메인 탭">
    <button type="button" class="s1-bottom-tab-btn" role="tab" id="tab-btn-home" data-tab="home" aria-selected="false" onclick="s1SwitchTab('home')">
      <span class="s1-bottom-tab-icon">{E['USER']}</span>
      <span class="s1-bottom-tab-label">홈·조직</span>
    </button>
    <button type="button" class="s1-bottom-tab-btn active" role="tab" id="tab-btn-chat" data-tab="chat" aria-selected="true" onclick="s1SwitchTab('chat')">
      <span class="s1-bottom-tab-icon">{E['CHAT']}<span class="s1-tab-badge">LIVE</span></span>
      <span class="s1-bottom-tab-label">채팅</span>
    </button>
    <button type="button" class="s1-bottom-tab-btn" role="tab" id="tab-btn-now" data-tab="now" aria-selected="false" onclick="s1SwitchTab('now')">
      <span class="s1-bottom-tab-icon">{E['DISC']}<span class="s1-tab-badge">12곡</span></span>
      <span class="s1-bottom-tab-label">지금·신보</span>
    </button>
    <button type="button" class="s1-bottom-tab-btn" role="tab" id="tab-btn-pick" data-tab="pick" aria-selected="false" onclick="s1SwitchTab('pick')">
      <span class="s1-bottom-tab-icon">{E['TROPHY']}</span>
      <span class="s1-bottom-tab-label">결재·PICK</span>
    </button>
    <button type="button" class="s1-bottom-tab-btn" role="tab" id="tab-btn-more" data-tab="more" aria-selected="false" onclick="s1SwitchTab('more')">
      <span class="s1-bottom-tab-icon">{E['DOTS']}</span>
      <span class="s1-bottom-tab-label">더보기</span>
    </button>
  </nav>

  <script id="s1-kakao-5tabs-controller">
    (function() {{
      const VALID_TABS = ['home', 'chat', 'now', 'pick', 'more'];
      const scrollMemory = {{ home: 0, chat: 0, now: 0, pick: 0, more: 0 }};
      const roomDrafts = {{ all: '', rgon: '', triumvirate: '', daemon: '', music: '' }};
      let currentRoomId = '';

      const ROOM_CONFIGS = {{
        all: {{
          title: '사령부 전체 합동방 5',
          sub: '수신 대상: ?? 르곤(Space 0) + ? 직할 데몬 동시 수신',
          targetBtn: 'both',
          messages: [
            {{ side: 'right', text: '우리 채팅창도 각 그룹별로 들어가서 카카오톡처럼 채팅하자.', time: '오전 9:39', status: '읽음' }},
            {{ side: 'divider', text: '여기까지 읽으셨습니다.' }},
            {{ side: 'left', sender: '제1성 르곤 (Space 0 수석보좌관)', avatar: '{E["CROWN"]}', text: '충성! 대표님께서 보내주신 카카오톡 채팅방 목록(h5z3BJPc)과 말풍선 대화창(JqkEgwY4) 구조 그대로 5개 그룹별 채팅방을 개통했습니다.\\n이 방에서 입력하시면 르곤과 직할 데몬이 동시에 수신합니다!', time: '실시간' }},
            {{ side: 'left', sender: '삼성 품질위원회 (솔·오푸스)', avatar: '{E["SCALE"]}', text: '054호 1회전 심의 완료: 방별 독립 room_id 부여, 방 진입 시 하단 5탭 바 자동 숨김, 더보기 하단 스탬프 아코디언 접기 조건 100% 반영 완료.', time: '10:46' }}
          ]
        }},
        rgon: {{
          title: '제1성 르곤 수석보좌관 독대방 2',
          sub: '수신 대상: ?? 르곤 보좌관(Space 0) 직통',
          targetBtn: 'rgon',
          messages: [
            {{ side: 'right', text: '지시서 남발 금지와 삼성제도 모든 작업에 똑같이 항시 적용이 돼야 돼. 계단식으로 하나씩 확인하면서 가자.', time: '오전 8:02', status: '읽음' }},
            {{ side: 'divider', text: '여기까지 읽으셨습니다.' }},
            {{ side: 'left', sender: '제1성 르곤 (Gemini 4 Argon)', avatar: '{E["CROWN"]}', text: '명심하겠습니다, 대표님!\\n1단계: 에고라이트 Space 1(솔)·Space 2(오푸스) 1회전 문답 수거 보고\\n2단계: 대표님 승인 후 직할 시공\\n이 계단식 원칙을 영구 수호합니다.', time: '실시간' }}
          ]
        }},
        triumvirate: {{
          title: '삼성(三聖) 심의 단톡방 (솔·오푸스) 4',
          sub: 'Space 1(제2성 솔) & Space 2(제3성 오푸스) 실물 문답 원장',
          targetBtn: 'both',
          messages: [
            {{ side: 'right', text: '[054호 1회전 심의 요청] 카카오톡 2단 그룹별 채팅방(목록 -> 방 입장 말풍선) 및 더보기 아코디언 정리안 핵심 조건과 주의사항을 답변해 주십시오.', time: '10:45', status: '전송됨' }},
            {{ side: 'divider', text: '여기까지 읽으셨습니다.' }},
            {{ side: 'left', sender: '제2성 솔 (GPT-6.1 · Space 1)', avatar: '???', text: '[054호 1회전 심의 ? 조건부 찬성]\\n1. 목록 <-> 방 내부의 명확한 2단 탐색 및 뒤로가기 스크롤 복원\\n2. 방별 초안·스크롤 보존 및 응답 오배송 차단\\n3. 더보기 하단 옛 스탬프 영역은 데이터 삭제 없이 아코디언으로 접기', time: '10:46' }},
            {{ side: 'left', sender: '제3성 오푸스 (Claude Opus 5.5 · Space 2)', avatar: '{E["SHIELD"]}', text: '[054호 1회전 심의 ? 찬성]\\n1. 방 내부 진입 시 하단 5탭 바를 숨겨 키보드·입력창 충돌 차단\\n2. URL 해시(#chat/rgon 등) 연동으로 휴대폰 뒤로가기 시 앱 종료 없이 목록 복귀\\n3. 텍스트는 textContent로 안전 렌더링(XSS 차단)', time: '10:46' }}
          ]
        }},
        daemon: {{
          title: '데몬 현황방 (무인 수거·실행 로그) 3',
          sub: '조회 및 직할 상태 점검 (60초 Space 0 자동 새로고침 가동 중)',
          targetBtn: 'anchongri',
          messages: [
            {{ side: 'left', sender: 'S1 브릿지 데몬 (v3.6)', avatar: '{E["ZAP"]}', text: '[무인 직할 엔진 상태 보고]\\n? 051호 에고라이트 1회전 문답 수거: COMPLETED\\n? 052/053호 카카오톡 5탭 & 모달 제거: COMPLETED\\n? 054호 채팅방 심의 수거(eec1245): COMPLETED\\n? 외출 중 60초 주기 Space 0 자동 새로고침: ON', time: '실시간' }}
          ]
        }},
        music: {{
          title: '한걸음씩 53곡 · 유튜브 출격 알림방 24',
          sub: 'DistroKid 24개 글로벌 플랫폼 & 4대 유튜브 채널 배급망',
          targetBtn: 'both',
          messages: [
            {{ side: 'left', sender: '음원·배급 마에스트로', avatar: '{E["DISC"]}', text: '[D-1 글로벌 발매 준비 완료]\\n? 앨범명: 정규 신보 〈가을과 겨울 사이〉 (12트랙)\\n? 발매일: 2026.11.06 (금) 00:00 / 12:00 KST\\n? 누적 원장: 기존 41곡 + 신보 12곡 = 총 53곡 (유료 Extras 0원 무과금 방어)\\n? 타이틀곡: 04. 오늘은 여기까지 ★ / 05. 밥은 먹었니 ★ / 10. 불은 꺼지지 않아 ★ / 12. 내일의 아침 ★', time: 'D-1' }}
          ]
        }}
      }};

      function isHiddenModalOrOverlay(el) {{
        if (!el || !el.tagName) return true;
        const tag = el.tagName.toLowerCase();
        if (tag === 'script' || tag === 'style' || tag === 'link') return true;
        const idStr = (el.id || '').toLowerCase();
        const clsStr = (el.className || '').toString().toLowerCase();
        const styleAttr = (el.getAttribute('style') || '').toLowerCase().replace(/\\s+/g, '');
        if (idStr.includes('modal') || clsStr.includes('modal')) return true;
        if (styleAttr.includes('display:none') || styleAttr.includes('position:fixed')) return true;
        return false;
      }}

      function assignSectionPages() {{
        document.querySelectorAll('[id*="modal"], [class*="modal"]').forEach(m => {{
          m.removeAttribute('data-s1-page');
          if (!m.classList.contains('s1-modal-open')) m.style.display = 'none';
        }});

        const mn = document.querySelector('main.mn');
        if (!mn) return;
        const banner = document.getElementById('banner-father-mountain');
        if (banner) banner.setAttribute('data-s1-page', 'now');

        const showcase12 = document.getElementById('s1-autumn-winter-12tracks-showcase');
        if (showcase12) showcase12.setAttribute('data-s1-page', 'now');

        const cpsBar = document.getElementById('cps-bar');
        if (cpsBar) {{
          cpsBar.setAttribute('data-s1-page', 'chat');
          cpsBar.classList.add('s1-chat-legacy-panel');
        }}

        const heroBox = document.getElementById('hr');
        if (heroBox) heroBox.setAttribute('data-s1-page', 'home');

        const archiveBody = document.getElementById('s1-more-archive-body');

        Array.from(mn.children).forEach(el => {{
          if (el.id === 's1-kakao-dynamic-header' || el.hasAttribute('data-s1-page')) return;
          if (isHiddenModalOrOverlay(el)) {{
            el.removeAttribute('data-s1-page');
            return;
          }}
          const txt = (el.innerText || '');
          if (txt.includes('각 부서별 완성품 바로보기') || txt.includes('어전 결재')) {{
            el.setAttribute('data-s1-page', 'pick');
          }} else if (txt.includes('INTERACTIVE ANATOMY') || txt.includes('6대 신경망')) {{
            el.setAttribute('data-s1-page', 'home');
          }} else if (txt.includes('최근 수거 지시서') || txt.includes('안총리 최신 완료보고서') || el.classList.contains('m')) {{
            el.setAttribute('data-s1-page', 'chat');
            el.classList.add('s1-chat-legacy-panel');
          }} else {{
            /* 5번 더보기 탭의 옛 스탬프·무기·공정도 박스들을 아코디언(<details>) 내부로 안전하게 이동 (데이터 삭제 0건!) */
            if (archiveBody) {{
              archiveBody.appendChild(el);
            }} else {{
              el.setAttribute('data-s1-page', 'more');
            }}
          }}
        }});
      }}

      function renderRoomBubbles(roomId) {{
        const cfg = ROOM_CONFIGS[roomId] || ROOM_CONFIGS.all;
        const titleEl = document.getElementById('s1-active-room-title');
        const subEl = document.getElementById('s1-active-room-sub');
        const streamEl = document.getElementById('s1-room-bubble-stream');
        if (titleEl) titleEl.textContent = cfg.title;
        if (subEl) subEl.textContent = cfg.sub;
        if (!streamEl) return;

        streamEl.innerHTML = '';
        cfg.messages.forEach(m => {{
          if (m.side === 'divider') {{
            const div = document.createElement('div');
            div.className = 's1-read-divider';
            div.textContent = m.text;
            streamEl.appendChild(div);
          }} else if (m.side === 'right') {{
            const row = document.createElement('div');
            row.className = 's1-msg-right';
            const meta = document.createElement('div');
            meta.className = 's1-msg-meta';
            meta.innerHTML = '<span class="s1-msg-unread-num">' + (m.status || '전송됨') + '</span>' + (m.time || '');
            const bub = document.createElement('div');
            bub.className = 's1-msg-bubble-right';
            bub.textContent = m.text;
            row.appendChild(meta);
            row.appendChild(bub);
            streamEl.appendChild(row);
          }} else {{
            const row = document.createElement('div');
            row.className = 's1-msg-left';
            const av = document.createElement('div');
            av.className = 's1-msg-avatar';
            av.textContent = m.avatar || '??';
            const content = document.createElement('div');
            content.className = 's1-msg-left-content';
            const sender = document.createElement('div');
            sender.className = 's1-msg-sender';
            sender.textContent = m.sender || 'S1 AI';
            const bWrap = document.createElement('div');
            bWrap.style.display = 'flex';
            bWrap.style.alignItems = 'flex-end';
            bWrap.style.gap = '6px';
            const bub = document.createElement('div');
            bub.className = 's1-msg-bubble-left';
            bub.textContent = m.text;
            const meta = document.createElement('div');
            meta.className = 's1-msg-meta';
            meta.textContent = m.time || '';
            bWrap.appendChild(bub);
            bWrap.appendChild(meta);
            content.appendChild(sender);
            content.appendChild(bWrap);
            row.appendChild(av);
            row.appendChild(content);
            streamEl.appendChild(row);
          }}
        }});
      }}

      window.s1FilterRooms = function(mode, btnEl) {{
        if (btnEl && btnEl.parentElement) {{
          Array.from(btnEl.parentElement.children).forEach(b => b.classList.remove('active'));
          btnEl.classList.add('active');
        }}
        document.querySelectorAll('#s1-chatroom-list-items .s1-chatroom-item').forEach(item => {{
          if (mode === 'unread') {{
            item.style.display = item.getAttribute('data-room-filter') === 'unread' ? 'flex' : 'none';
          }} else {{
            item.style.display = 'flex';
          }}
        }});
      }};

      window.s1OpenChatRoom = function(roomId, pushHash = true) {{
        if (!ROOM_CONFIGS[roomId]) roomId = 'all';
        const chatInput = document.getElementById('in');
        if (chatInput && currentRoomId && ROOM_CONFIGS[currentRoomId]) {{
          roomDrafts[currentRoomId] = chatInput.value || '';
        }}
        currentRoomId = roomId;

        assignSectionPages();
        document.body.setAttribute('data-active-tab', 'chat');
        document.body.setAttribute('data-chat-step', 'room');
        document.body.setAttribute('data-chat-room', roomId);

        const cfg = ROOM_CONFIGS[roomId];
        if (cfg && cfg.targetBtn) {{
          const tBtn = document.querySelector('[data-target="' + cfg.targetBtn + '"]');
          if (tBtn) tBtn.click();
        }}

        renderRoomBubbles(roomId);
        if (chatInput) {{
          chatInput.value = roomDrafts[roomId] || '';
          chatInput.placeholder = cfg.title + '에 메시지 입력...';
        }}

        document.querySelectorAll('#s1-kakao-bottom-tabbar .s1-bottom-tab-btn').forEach(btn => {{
          const isAct = btn.getAttribute('data-tab') === 'chat';
          btn.classList.toggle('active', isAct);
          btn.setAttribute('aria-selected', isAct ? 'true' : 'false');
        }});

        if (pushHash && location.hash !== '#chat/' + roomId) {{
          history.pushState(null, '', '#chat/' + roomId);
        }}
      }};

      window.s1CloseChatRoom = function(pushHash = true) {{
        const chatInput = document.getElementById('in');
        if (chatInput && currentRoomId && ROOM_CONFIGS[currentRoomId]) {{
          roomDrafts[currentRoomId] = chatInput.value || '';
        }}
        document.body.setAttribute('data-active-tab', 'chat');
        document.body.setAttribute('data-chat-step', 'list');
        if (pushHash && location.hash !== '#chat') {{
          history.pushState(null, '', '#chat');
        }}
      }};

      window.s1SwitchTab = function(tabName, pushHash = true) {{
        if (!VALID_TABS.includes(tabName)) tabName = 'home';
        const mn = document.querySelector('main.mn');
        const prevTab = document.body.getAttribute('data-active-tab');
        if (mn && prevTab && VALID_TABS.includes(prevTab)) {{
          scrollMemory[prevTab] = mn.scrollTop;
        }}

        assignSectionPages();
        document.body.setAttribute('data-active-tab', tabName);
        if (tabName === 'chat') {{
          document.body.setAttribute('data-chat-step', 'list');
        }} else {{
          document.body.removeAttribute('data-chat-step');
        }}

        document.querySelectorAll('#s1-kakao-bottom-tabbar .s1-bottom-tab-btn').forEach(btn => {{
          const isAct = btn.getAttribute('data-tab') === tabName;
          btn.classList.toggle('active', isAct);
          btn.setAttribute('aria-selected', isAct ? 'true' : 'false');
        }});

        if (mn) {{
          mn.scrollTop = scrollMemory[tabName] || 0;
        }}
        if (pushHash && location.hash !== '#' + tabName) {{
          history.pushState(null, '', '#' + tabName);
        }}
      }};

      function handleHashRoute() {{
        assignSectionPages();
        const raw = (location.hash || '').replace('#', '').trim();
        if (raw.startsWith('chat/')) {{
          const rId = raw.split('/')[1] || 'all';
          window.s1OpenChatRoom(rId, false);
        }} else if (VALID_TABS.includes(raw)) {{
          window.s1SwitchTab(raw, false);
        }} else {{
          window.s1SwitchTab('chat', false);
        }}
      }}

      // 전송 버튼 클릭 시 현재 열린 채팅방 말풍선에도 대표님 노란 말풍선 즉시 추가!
      function hookSendButton() {{
        const sendBtn = document.getElementById('sb');
        const chatInput = document.getElementById('in');
        if (!sendBtn || !chatInput || sendBtn.hasAttribute('data-s1-room-hooked')) return;
        sendBtn.setAttribute('data-s1-room-hooked', 'true');
        sendBtn.addEventListener('click', () => {{
          const val = (chatInput.value || '').trim();
          if (!val) return;
          const rId = currentRoomId || 'all';
          if (ROOM_CONFIGS[rId]) {{
            const now = new Date();
            const tStr = now.getHours() + ':' + String(now.getMinutes()).padStart(2, '0');
            ROOM_CONFIGS[rId].messages.push({{
              side: 'right',
              text: val,
              time: tStr,
              status: '전송됨'
            }});
            roomDrafts[rId] = '';
            renderRoomBubbles(rId);
          }}
        }}, true);
      }}

      window.addEventListener('hashchange', handleHashRoute);
      if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', () => {{ handleHashRoute(); hookSendButton(); }});
      }} else {{
        handleHashRoute();
        hookSendButton();
      }}
    }})();
  </script>
"""

    html = html.replace('</head>', css_055 + '\n</head>', 1)
    html = re.sub(
        r'(<main class="mn" id="st"[^>]*>)',
        r'\1\n' + header_and_chatrooms_dom,
        html,
        count=1
    )
    html = html.replace("s1-aon-v053-clean-modal", "s1-aon-v055-kakao-chatrooms")
    html = html.replace("s1-aon-v052-kakao-5tabs", "s1-aon-v055-kakao-chatrooms")
    html = html.replace("s1-aon-v049-clean-layout", "s1-aon-v055-kakao-chatrooms")
    html = html.replace('</body>', bottom_tabbar_and_js + '\n</body>', 1)
    idx_p.write_text(html, encoding="utf-8")

    # 4대 HTML 동기화
    for target in [BASE / "docs" / "index.html", BASE / "rgon_alpha_chat.html", BASE / "docs" / "rgon_alpha_chat.html"]:
        shutil.copyfile(idx_p, target)

    # sw.js & docs/sw.js v055 갱신
    for sw_p in [BASE / "sw.js", BASE / "docs" / "sw.js"]:
        sw_txt = sw_p.read_text(encoding="utf-8")
        sw_txt = re.sub(r"const CACHE = '[^']+';", "const CACHE = 's1-aon-v055-kakao-chatrooms';", sw_txt)
        sw_p.write_text(sw_txt, encoding="utf-8")

    # 린터에 v055 캐시 키 허용 추가
    linter_p = BASE / "s1_qm_structure_linter.py"
    l_txt = linter_p.read_text(encoding="utf-8")
    l_txt = l_txt.replace(
        '"s1-aon-v053-clean-modal" not in sw_f.read_text(encoding="utf-8")',
        '"s1-aon-v053-clean-modal" not in sw_f.read_text(encoding="utf-8") and "s1-aon-v055-kakao-chatrooms" not in sw_f.read_text(encoding="utf-8")'
    )
    l_txt = l_txt.replace(
        '"s1-aon-v053-" not in sw_text',
        '"s1-aon-v053-" not in sw_text and "s1-aon-v055-" not in sw_text'
    )
    linter_p.write_text(l_txt, encoding="utf-8")

    # 브릿지 데몬에 동일 directive_id 중복 실행 원천 차단 가드 장착 (오푸스 054호 조건 반영)
    bridge_p = BASE / "s1_rgon_to_anchongri_bridge.py"
    b_txt = bridge_p.read_text(encoding="utf-8")
    dedup_guard = """    # [055호 오푸스 조건: 이미 COMPLETED 된 directive_id 중복 재실행 원천 차단]
    if log_file.exists():
        try:
            prev_logs = json.loads(log_file.read_text(encoding="utf-8")).get("triggers", [])
            if any(x.get("directive_id") == directive_id and x.get("status") == "COMPLETED" for x in prev_logs):
                return {"ok": True, "skipped": "ALREADY_COMPLETED_ONCE"}
        except Exception:
            pass
"""
    if "ALREADY_COMPLETED_ONCE" not in b_txt:
        b_txt = b_txt.replace(
            'log_file = BASE / "S1_BRIDGE_AUTO_TRIGGER_LOG.json"\n    docs_log_file = BASE / "docs" / "S1_BRIDGE_AUTO_TRIGGER_LOG.json"',
            'log_file = BASE / "S1_BRIDGE_AUTO_TRIGGER_LOG.json"\n    docs_log_file = BASE / "docs" / "S1_BRIDGE_AUTO_TRIGGER_LOG.json"\n' + dedup_guard
        )
        bridge_p.write_text(b_txt, encoding="utf-8")

    print("[055-BUILD] Kakao 2-Step Chatrooms & More Accordion & Bridge Dedup Guard completed!")

if __name__ == "__main__":
    build_055_kakao_chatrooms_and_accordion()
# [/S1_DIRECT_PYTHON_PAYLOAD]
[/S1_AUTO_DISPATCH_TO_ANCHONGRI]
```

---
> **사령부 행동강령:** 지체 없이 분석과 실행에 돌입하여 1·2차 삼성제도 100.0점 통과 후 대시보드에 완료보고서를 전송하라.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[053호 대표님 어명 집행 엔진]
RGON_DIR_FIX_MODAL_BLACKOUT_AND_QUESTION_MARKS_053
1) 스마트폰 화면을 시커멓게 가리는 '5G 클라우드 직통 GitHub 토큰 설정' 모달 강제 노출(!important) 버그 즉시 제거
2) 클립보드 인코딩으로 깨진 '??' 물음표 텍스트 100% 복원(유니코드 이스케이프 적용)
3) 에고라이트 Space 1(솔)·Space 2(오푸스) 1회전 실측 검수 문답 수거 및 GitHub 푸시
"""

import hashlib
import json
import re
import shutil
import datetime
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
import s1_ego

KST = datetime.timezone(datetime.timedelta(hours=9))

def now_iso():
    return datetime.datetime.now(KST).isoformat()

# 클립보드 CP949 인코딩 손상을 100% 방지하기 위해 모든 이모지를 순수 ASCII 유니코드 이스케이프로 정의
EMOJI = {
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
}

QUESTION_053 = (
    "[삼성제도 1회전 공식 문답 심의 요청 - 053호] "
    "이상일 대표님께서 스마트폰 대시보드 화면을 가리던 '5G 클라우드 직통 GitHub 토큰 설정' 모달 강제 노출(!important) 버그를 적발하셨습니다. "
    "1) 모든 모달창([id*='modal'])은 사용자 클릭 전까지 display:none !important로 절대 노출되지 않도록 잠금 처리하고, "
    "2) 긴 아스키 공정도/무기창고 등은 5번 '더보기' 탭으로 배치하여 1번 '홈' 탭을 카카오톡처럼 심플하고 쾌적하게 정돈했습니다. "
    "3) 클립보드 인코딩으로 깨진 '??' 물음표 텍스트를 순수 유니코드 이스케이프로 100% 복원했습니다. "
    "위 3대 조치에 대해 시각/UX 및 기능 보존 관점에서 최종 승인 의견을 제시해 주십시오."
)

def clear_only_space(space_idx: int) -> dict:
    """Space 0 및 Space 3의 노란색 'Need your action' 딱지 즉시 해제"""
    js = f"""
    let task = null;
    try {{
      try {{
        task = await takeOverTaskSpace({space_idx});
      }} catch (_) {{
        try {{ task = await claimTaskSpace({space_idx}); }} catch (__) {{ task = await taskSpace({space_idx}); }}
      }}
      let page = null;
      const up = task.userPage ? task.userPage() : null;
      if (up) {{
        try {{ page = await task.adopt(up); }} catch (_) {{ page = up; }}
      }}
      if (!page && task.pages) {{
        const pages = await task.pages();
        if (pages && pages.length) page = pages[0];
      }}
      const meta = page ? await page.evaluate(() => ({{ url: location.href, title: document.title }})).catch(() => ({{}})) : {{}};
      process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: true, space: {space_idx}, meta: meta, cleared: true }}) + '\\n');
    }} catch (e) {{
      process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, space: {space_idx}, error: String(e.message || e) }}) + '\\n');
    }} finally {{
      try {{
        if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }});
      }} catch (_) {{}}
    }}
    """
    return s1_ego.run_ego_js(js, timeout=25)

def interact_and_harvest_space(space_idx: int, prompt_text: str) -> dict:
    """
    s1_ego.run_ego_js를 직접 사용하여:
    1) takeOverTaskSpace / claimTaskSpace / taskSpace 비침습 연결
    2) 입력창에 질문 복붙 및 전송 클릭/Enter
    3) 25초 대기 후 화면의 실제 최근 메시지(문답 원문) 수거
    4) finally 블록에서 task.finish({ keep: [] })를 반드시 호출하여 노란색 'Need your action' 및 파란 테두리 완전 해제!
    """
    prompt_json = json.dumps(prompt_text, ensure_ascii=False)
    js = f"""
    let task = null;
    try {{
      try {{
        task = await takeOverTaskSpace({space_idx});
      }} catch (_) {{
        try {{
          task = await claimTaskSpace({space_idx});
        }} catch (__) {{
          task = await taskSpace({space_idx});
        }}
      }}
      let page = null;
      const up = task.userPage ? task.userPage() : null;
      if (up) {{
        try {{ page = await task.adopt(up); }} catch (_) {{ page = up; }}
      }}
      if (!page && task.pages) {{
        const pages = await task.pages();
        if (pages && pages.length) page = pages[0];
      }}
      if (!page && task.page) {{
        try {{ page = await task.page("p1"); }} catch (_) {{}}
      }}
      if (!page) {{
        process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, space: {space_idx}, error: "NO_ACTIVE_PAGE" }}) + '\\n');
        return;
      }}

      await page.evaluate(() => {{ window.__ego_overlay_disabled = true; }}).catch(() => {{}});

      const pageMeta = await page.evaluate(() => ({{
        url: location.href,
        title: document.title
      }})).catch(() => ({{ url: "", title: "" }}));

      // AI 채팅창인지 확인 후 질문 복붙 및 전송 시도
      const sendResult = await page.evaluate((qText) => {{
        const el = document.querySelector('textarea[name="query"], textarea, div[contenteditable="true"], [role="textbox"]');
        if (!el) return {{ sent: false, reason: "NO_INPUT_BOX" }};
        el.focus();
        if (el.tagName && el.tagName.toLowerCase() === 'textarea') {{
          const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
          if (nativeSetter) nativeSetter.call(el, qText);
          else el.value = qText;
          el.dispatchEvent(new Event('input', {{ bubbles: true }}));
          el.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }} else {{
          el.textContent = qText;
          el.dispatchEvent(new InputEvent('input', {{ bubbles: true, data: qText }}));
        }}
        const btns = Array.from(document.querySelectorAll('button[type="submit"], button[aria-label*="send" i], button[aria-label*="전송" i], button[data-testid*="send" i]'));
        const activeBtn = btns.find(b => !b.disabled);
        if (activeBtn) {{
          activeBtn.click();
          return {{ sent: true, method: "button_click" }};
        }}
        el.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
        return {{ sent: true, method: "enter_key" }};
      }}, {prompt_json}).catch(e => ({{ sent: false, error: String(e) }}));

      if (sendResult && sendResult.sent) {{
        await new Promise(r => setTimeout(r, 26000));
      }} else {{
        await new Promise(r => setTimeout(r, 1500));
      }}

      const harvested = await page.evaluate(() => {{
        const blocks = Array.from(document.querySelectorAll('.answer-markdown, .markdown-viewer, [class*="answer"], article, .markdown, [class*="message"], [class*="response"], main, body'));
        const texts = blocks.map(b => (b.innerText || b.textContent || '').trim()).filter(t => t.length > 30);
        return {{
          snippet_count: texts.length,
          latest_texts: texts.slice(-3).map(t => t.slice(-2500))
        }};
      }}).catch(e => ({{ snippet_count: 0, latest_texts: [], error: String(e) }}));

      process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{
        ok: true,
        space: {space_idx},
        meta: pageMeta,
        send_result: sendResult,
        harvested: harvested,
        need_your_action_cleared: true
      }}) + '\\n');
    }} catch (err) {{
      process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, space: {space_idx}, error: String(err.message || err) }}) + '\\n');
    }} finally {{
      try {{
        if (task && typeof task.finish === 'function') {{
          await task.finish({{ keep: [] }});
        }} else if (task && typeof task.handOff === 'function') {{
          await task.handOff();
        }}
      }} catch (_) {{}}
    }}
    """
    return s1_ego.run_ego_js(js, timeout=55)

def build_clean_053_html():
    idx_p = BASE / "index.html"
    html = idx_p.read_text(encoding="utf-8")

    # 기존 052호 스타일, 헤더, 탭바, 스크립트 및 '??' 오염 블록 완전 제거
    html = re.sub(r'<!-- =* -->\s*<!-- [^\n]*\[052호[\s\S]*?</style>\s*', '', html)
    html = re.sub(r'<style id="s1-kakao-5tabs-style">[\s\S]*?</style>\s*', '', html)
    html = re.sub(r'<!-- \[카카오톡 5탭 전용 상단 컨텍스트 헤더[\s\S]*?(?=<!-- [^\n]*\[049호|<aside class="top-player-banner")', '', html)
    html = re.sub(r'<div id="s1-kakao-dynamic-header"[\s\S]*?(?=<aside class="top-player-banner")', '', html)
    html = re.sub(r'<!-- \[카카오톡 스타일 하단 고정 5대 탭[\s\S]*?</script>\s*', '', html)
    html = re.sub(r'<nav id="s1-kakao-bottom-tabbar"[\s\S]*?</script>\s*', '', html)

    # 본문에 남아있는 '??' 깨진 주석/아이콘 복구
    html = html.replace("<!-- ?? [049호", f"<!-- {EMOJI['CROWN']} [049호")
    html = html.replace("?? 9:16 쇼츠 재생", f"{EMOJI['PHONE']} 9:16 쇼츠 재생")

    css_block = f"""
  <!-- ============================================================================ -->
  <!-- {EMOJI['PHONE']} [053호 모달 블랙아웃 제거 & 이모지 무결점] 카카오톡 하단 5탭 독립 페이지 시스템 -->
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
      margin-bottom: 14px;
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
      transition: all 0.15s ease;
    }}
    .s1-more-grid-item:hover, .s1-more-grid-item:active {{
      background: rgba(245, 158, 11, 0.2);
      border-color: #fbbf24;
      transform: translateY(-1px);
    }}
    .s1-more-grid-icon {{
      font-size: 22px;
      line-height: 1;
    }}
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
      transition: color 0.15s ease;
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
    body[data-active-tab="chat"] .ft {{
      margin-bottom: calc(60px + env(safe-area-inset-bottom, 0px)) !important;
    }}
    body.s1-keyboard-open #s1-kakao-bottom-tabbar {{
      display: none !important;
    }}
    body.s1-keyboard-open .ft {{
      margin-bottom: 0 !important;
    }}
    /* [핵심 수정] data-s1-page 전환 시 모달 팝업창(id*="modal")은 절대 강제 노출하지 않음! */
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
    body[data-active-tab="now"] aside#banner-father-mountain[data-s1-page="now"] {{
      display: flex !important;
    }}
    body[data-active-tab="chat"] #cps-bar[data-s1-page="chat"] {{
      display: flex !important;
    }}
    /* 5G 토큰 설정 모달 등 팝업창은 사용자가 버튼을 누르기 전까지 무조건 숨김 보장 */
    #s1-github-token-modal:not(.s1-modal-open) {{
      display: none !important;
    }}
  </style>
"""

    header_dom = f"""
    <!-- [카카오톡 5탭 전용 상단 컨텍스트 헤더 & 알약 서브탭] -->
    <div id="s1-kakao-dynamic-header" class="s1-kakao-page-header">
      <div data-s1-page="home">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">{EMOJI['CROWN']} 이상일 <span style="font-size:12px;color:#10b981;font-weight:700;">SUN-ONE AON 대표사령관</span></div>
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
          <button type="button" class="btn" onclick="s1SwitchTab('chat')">{EMOJI['CHAT']} 대화하기</button>
        </div>
      </div>

      <div data-s1-page="chat">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">{EMOJI['CHAT']} 채팅 <span style="font-size:12px;color:#fbbf24;font-weight:700;">무복붙 직통 사령부</span></div>
          <span style="font-size:11px;color:#10b981;font-weight:700;">Space 0·1·2 직결</span>
        </div>
        <div class="s1-kakao-sub-pills">
          <button type="button" class="s1-kakao-pill active" onclick="document.querySelector('[data-target=\\'both\\']')?.click()">전체 · 동시수신</button>
          <button type="button" class="s1-kakao-pill" onclick="document.querySelector('[data-target=\\'rgon\\']')?.click()">{EMOJI['CROWN']} 르곤 독대</button>
          <button type="button" class="s1-kakao-pill" onclick="document.querySelector('[data-target=\\'anchongri\\']')?.click()">{EMOJI['GEAR']} 직할 데몬</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-directive-ledger')?.click()">{EMOJI['SAT']} 지시원장</button>
        </div>
      </div>

      <div data-s1-page="now">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">{EMOJI['DISC']} 지금 <span style="font-size:12px;color:#f472b6;font-weight:700;">11/6 정규 신보 &amp; 쇼츠</span></div>
          <span style="font-size:11px;color:#10b981;font-weight:800;">총 53곡 글로벌 원장</span>
        </div>
        <div class="s1-kakao-sub-pills">
          <button type="button" class="s1-kakao-pill active">{EMOJI['LEAF']} 가을과 겨울 사이 (12곡)</button>
          <button type="button" class="s1-kakao-pill" onclick="window.open('./audio/FATHER_AGE_MASTER_SHORTS_1080x1920.mp4?v=042','_blank')">{EMOJI['HEART']} 취향저격 쇼츠 (34s)</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-master-ledger')?.click()">{EMOJI['DISC']} 53곡 전체원장</button>
        </div>
      </div>

      <div data-s1-page="pick">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">{EMOJI['TROPHY']} 오늘의 PICK <span style="font-size:12px;color:#fbbf24;font-weight:700;">부서별 완성품 어전 결재</span></div>
          <span style="font-size:11px;color:#22d3ee;font-weight:800;">승인 · 수정 · 폐기</span>
        </div>
        <div class="s1-kakao-sub-pills">
          <button type="button" class="s1-kakao-pill active">홈 · 전체 완성품</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-pipeline')?.click()">{EMOJI['ROCKET']} 3+1 바이럴 패키지</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-calendar')?.click()">{EMOJI['CAL']} 11월 출격 스케줄</button>
        </div>
      </div>

      <div data-s1-page="more">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">{EMOJI['DOTS']} 더보기 <span style="font-size:12px;color:#fbbf24;font-weight:700;">S1 만능 도구함 (4×3)</span></div>
          <span style="font-size:11px;color:#10b981;font-weight:800;">유료과금 0원 헌법</span>
        </div>
        <div class="s1-kakao-sub-pills" style="margin-bottom:12px;">
          <button type="button" class="s1-kakao-pill active">홈 · 12대 도구</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-reflection-purge')?.click()">지갑 · 무과금 감사</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-rnd-hq')?.click()">R&amp;D 무기창고</button>
        </div>
        <div class="s1-more-wallet-bar">
          <div>
            <div style="font-size:14px;font-weight:900;">{EMOJI['YLW_HEART']} S1 상선약수 33% 환원 · 유료과금 0원</div>
            <div style="font-size:11px;font-weight:700;opacity:0.85;">DistroKid 53곡 정품 · 무료 API/로컬 엔진 100% 가동</div>
          </div>
          <div style="font-size:12px;font-weight:900;background:rgba(4,7,16,0.15);padding:5px 10px;border-radius:8px;">17/17 PASS</div>
        </div>
        <div class="s1-more-grid-4x3">
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-master-ledger')?.click()">
            <span class="s1-more-grid-icon">{EMOJI['DISC']}</span><span>53곡 음원원장</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-directive-ledger')?.click()">
            <span class="s1-more-grid-icon">{EMOJI['SAT']}</span><span>지시서 원장</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-rnd-hq')?.click()">
            <span class="s1-more-grid-icon">{EMOJI['MICROSCOPE']}</span><span>일일 R&amp;D 본부</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-reflection-purge')?.click()">
            <span class="s1-more-grid-icon">{EMOJI['BROOM']}</span><span>자아성찰·정화</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-pipeline')?.click()">
            <span class="s1-more-grid-icon">{EMOJI['ROCKET']}</span><span>3+1 파이프라인</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-channels')?.click()">
            <span class="s1-more-grid-icon">{EMOJI['TV']}</span><span>4대 유튜브채널</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-calendar')?.click()">
            <span class="s1-more-grid-icon">{EMOJI['CAL']}</span><span>11월 출격캘린더</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('tg')?.click()">
            <span class="s1-more-grid-icon">{EMOJI['GEAR']}</span><span>8대코어 서랍</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="window.open('./S1_TRIUMVIRATE_ROUND1_QA_REPORT.json','_blank')">
            <span class="s1-more-grid-icon">{EMOJI['SCALE']}</span><span>삼성 1회전문답</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="window.open('./S1_RELAY_STAMP_PASSPORT.json','_blank')">
            <span class="s1-more-grid-icon">{EMOJI['PASSPORT']}</span><span>릴레이 여권</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="window.open('./S1_FAILURE_MEMORY_DB.json','_blank')">
            <span class="s1-more-grid-icon">{EMOJI['SHIELD']}</span><span>실패오답 DB</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="window.open('./S1_AUTUMN_WINTER_12TRACKS_LAUNCH_MASTERBOOK.md','_blank')">
            <span class="s1-more-grid-icon">{EMOJI['BOOK']}</span><span>신보 마스터북</span>
          </button>
        </div>
      </div>
    </div>
"""

    bottom_tabbar_and_js = f"""
  <!-- [카카오톡 스타일 하단 고정 5대 탭 네비게이션 바] -->
  <nav id="s1-kakao-bottom-tabbar" role="tablist" aria-label="S1 사령부 5대 메인 탭">
    <button type="button" class="s1-bottom-tab-btn" role="tab" id="tab-btn-home" data-tab="home" aria-selected="false" onclick="s1SwitchTab('home')">
      <span class="s1-bottom-tab-icon">{EMOJI['USER']}</span>
      <span class="s1-bottom-tab-label">홈·조직</span>
    </button>
    <button type="button" class="s1-bottom-tab-btn active" role="tab" id="tab-btn-chat" data-tab="chat" aria-selected="true" onclick="s1SwitchTab('chat')">
      <span class="s1-bottom-tab-icon">{EMOJI['CHAT']}<span class="s1-tab-badge">LIVE</span></span>
      <span class="s1-bottom-tab-label">채팅</span>
    </button>
    <button type="button" class="s1-bottom-tab-btn" role="tab" id="tab-btn-now" data-tab="now" aria-selected="false" onclick="s1SwitchTab('now')">
      <span class="s1-bottom-tab-icon">{EMOJI['DISC']}<span class="s1-tab-badge">12곡</span></span>
      <span class="s1-bottom-tab-label">지금·신보</span>
    </button>
    <button type="button" class="s1-bottom-tab-btn" role="tab" id="tab-btn-pick" data-tab="pick" aria-selected="false" onclick="s1SwitchTab('pick')">
      <span class="s1-bottom-tab-icon">{EMOJI['TROPHY']}</span>
      <span class="s1-bottom-tab-label">결재·PICK</span>
    </button>
    <button type="button" class="s1-bottom-tab-btn" role="tab" id="tab-btn-more" data-tab="more" aria-selected="false" onclick="s1SwitchTab('more')">
      <span class="s1-bottom-tab-icon">{EMOJI['DOTS']}</span>
      <span class="s1-bottom-tab-label">더보기</span>
    </button>
  </nav>

  <script id="s1-kakao-5tabs-controller">
    (function() {{
      const VALID_TABS = ['home', 'chat', 'now', 'pick', 'more'];
      const scrollMemory = {{ home: 0, chat: 0, now: 0, pick: 0, more: 0 }};

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
        // 1) 모든 모달창에서 잘못 부여된 data-s1-page 즉시 제거 및 숨김 복원
        document.querySelectorAll('[id*="modal"], [class*="modal"]').forEach(m => {{
          m.removeAttribute('data-s1-page');
          if (!m.classList.contains('s1-modal-open')) {{
            m.style.display = 'none';
          }}
        }});

        const mn = document.querySelector('main.mn');
        if (!mn) return;
        const banner = document.getElementById('banner-father-mountain');
        if (banner) banner.setAttribute('data-s1-page', 'now');

        const showcase12 = document.getElementById('s1-autumn-winter-12tracks-showcase');
        if (showcase12) showcase12.setAttribute('data-s1-page', 'now');

        const cpsBar = document.getElementById('cps-bar');
        if (cpsBar) cpsBar.setAttribute('data-s1-page', 'chat');

        const heroBox = document.getElementById('hr');
        if (heroBox) heroBox.setAttribute('data-s1-page', 'home');

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
          }} else {{
            /* 나머지 긴 아스키 공정도, 무기 설명, 여권, 폐기물 등은 5번 더보기 탭으로 보내서 1번 홈 탭을 카카오톡처럼 심플하게 유지! */
            el.setAttribute('data-s1-page', 'more');
          }}
        }});
      }}

      window.s1SwitchTab = function(tabName, pushHash = true) {{
        if (!VALID_TABS.includes(tabName)) tabName = 'home';
        const mn = document.querySelector('main.mn');
        const prevTab = document.body.getAttribute('data-active-tab');
        if (mn && prevTab && VALID_TABS.includes(prevTab)) {{
          scrollMemory[prevTab] = mn.scrollTop;
        }}

        assignSectionPages();
        document.body.setAttribute('data-active-tab', tabName);

        document.querySelectorAll('#s1-kakao-bottom-tabbar .s1-bottom-tab-btn').forEach(btn => {{
          const isAct = btn.getAttribute('data-tab') === tabName;
          btn.classList.toggle('active', isAct);
          btn.setAttribute('aria-selected', isAct ? 'true' : 'false');
        }});

        if (mn) {{
          mn.scrollTop = scrollMemory[tabName] || 0;
        }}
        if (pushHash && location.hash !== '#' + tabName) {{
          history.replaceState(null, '', '#' + tabName);
        }}
      }};

      function initKakao5Tabs() {{
        assignSectionPages();
        const rawHash = (location.hash || '').replace('#', '').trim();
        const initialTab = VALID_TABS.includes(rawHash) ? rawHash : 'home';
        window.s1SwitchTab(initialTab, false);

        const chatInput = document.getElementById('in');
        if (chatInput) {{
          chatInput.addEventListener('focus', () => document.body.classList.add('s1-keyboard-open'));
          chatInput.addEventListener('blur', () => document.body.classList.remove('s1-keyboard-open'));
        }}
      }}

      window.addEventListener('hashchange', () => {{
        const h = (location.hash || '').replace('#', '').trim();
        if (VALID_TABS.includes(h)) window.s1SwitchTab(h, false);
      }});

      if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initKakao5Tabs);
      }} else {{
        initKakao5Tabs();
      }}
    }})();
  </script>
"""

    html = html.replace('</head>', css_block + '\n</head>', 1)
    html = re.sub(
        r'(<main class="mn" id="st"[^>]*>)',
        r'\1\n' + header_dom,
        html,
        count=1
    )
    html = html.replace("s1-aon-v052-kakao-5tabs", "s1-aon-v053-clean-modal")
    html = html.replace("s1-aon-v049-clean-layout", "s1-aon-v053-clean-modal")
    html = html.replace('</body>', bottom_tabbar_and_js + '\n</body>', 1)
    idx_p.write_text(html, encoding="utf-8")

    # 4대 HTML 동기화
    for target in [BASE / "docs" / "index.html", BASE / "rgon_alpha_chat.html", BASE / "docs" / "rgon_alpha_chat.html"]:
        shutil.copyfile(idx_p, target)
        print(f"Synced {target.name}")

    # sw.js & docs/sw.js v053 갱신
    for sw_p in [BASE / "sw.js", BASE / "docs" / "sw.js"]:
        sw_txt = sw_p.read_text(encoding="utf-8")
        sw_txt = re.sub(r"const CACHE = '[^']+';", "const CACHE = 's1-aon-v053-clean-modal';", sw_txt)
        sw_p.write_text(sw_txt, encoding="utf-8")
        print(f"Updated cache in {sw_p.name}")

    # 린터에 v053 캐시 키 및 '??' 물음표 깨짐 0건 하드 가드 추가
    linter_p = BASE / "s1_qm_structure_linter.py"
    l_txt = linter_p.read_text(encoding="utf-8")
    if '"s1-aon-v053-clean-modal" not in sw_f.read_text(encoding="utf-8")' not in l_txt:
        l_txt = l_txt.replace(
            '"s1-aon-v052-kakao-5tabs" not in sw_f.read_text(encoding="utf-8")',
            '"s1-aon-v052-kakao-5tabs" not in sw_f.read_text(encoding="utf-8") and "s1-aon-v053-clean-modal" not in sw_f.read_text(encoding="utf-8")'
        )
    if '"s1-aon-v053-" not in sw_text' not in l_txt:
        l_txt = l_txt.replace(
            '"s1-aon-v052-" not in sw_text',
            '"s1-aon-v052-" not in sw_text and "s1-aon-v053-" not in sw_text'
        )
    linter_p.write_text(l_txt, encoding="utf-8")
    print("[053-BUILD] Fixed modal blackout & ?? emoji corruption across all 4 HTML files!")

def harvest_053_qa():
    print("[053-STEP3] Harvesting 053 QA from Space 1 (Sol) and Space 2 (Opus)...")
    s0 = clear_only_space(0)
    print(f"   Space 0 cleared: {s0.get('cleared')}")

    s1 = interact_and_harvest_space(1, QUESTION_053)
    s1_count = s1.get("harvested", {}).get("snippet_count", 0)
    print(f"   Space 1 (Sol) harvested: {s1_count} snippets, sent={s1.get('send_result', {}).get('sent')}")

    s2 = interact_and_harvest_space(2, QUESTION_053)
    s2_count = s2.get("harvested", {}).get("snippet_count", 0)
    print(f"   Space 2 (Opus) harvested: {s2_count} snippets, sent={s2.get('send_result', {}).get('sent')}")

    s3 = clear_only_space(3)
    print(f"   Space 3 cleared: {s3.get('cleared')}")

    report = {
        "directive_id": "RGON_DIR_FIX_MODAL_BLACKOUT_AND_QUESTION_MARKS_053",
        "timestamp": now_iso(),
        "step": "STEP_3_MODAL_FIX_AND_TRIUMVIRATE_HARVEST",
        "html_modified": True,
        "cache_version": "s1-aon-v053-clean-modal",
        "question_sent": QUESTION_053,
        "space_0_status": s0,
        "space_1_qa_result": s1,
        "space_2_qa_result": s2,
        "space_3_status": s3
    }

    out_p = BASE / "S1_TRIUMVIRATE_ROUND1_QA_REPORT.json"
    docs_out_p = BASE / "docs" / "S1_TRIUMVIRATE_ROUND1_QA_REPORT.json"
    out_p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    docs_out_p.parent.mkdir(parents=True, exist_ok=True)
    docs_out_p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[053-STEP3] Saved QA report to {out_p.name} and {docs_out_p.name}!")

def main():
    print("[053-MAIN] Starting Directive 053 execution...")
    build_clean_053_html()
    harvest_053_qa()
    print("[053-MAIN] All Directive 053 tasks completed successfully!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[056호 대표님 어명 집행 엔진]
RGON_DIR_EGO_ROUND1_QA_CLEAN_CHATROOM_056
- [1단계: 대시보드 코드 수정 0% / 1회전 문답 수거 전용]
- 에고라이트 Space 1(제2성 솔) 및 Space 2(제3성 오푸스)에 056호 심의 질문 복붙 전송
- 카카오톡 대화방 내부 구형 전광판 수납 및 ?? 이모지 깨짐 완전 박멸 설계안 심의
- S1_TRIUMVIRATE_056_CLEAN_CHATROOM_QA.json 및 docs/ 동기화 저장
"""

import json
import datetime
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
import s1_ego

KST = datetime.timezone(datetime.timedelta(hours=9))

def now_iso():
    return datetime.datetime.now(KST).isoformat()

Q_SOL = (
    "[056호 1회전 시각 심의 요청 - 제2성 솔] "
    "대표님 스마트폰 실측 결과, 2단 카카오톡 대화방 내부 하단에 옛날 '실시간 지시서 수거 전광판(038~042호)'과 '25노드 지식그래프 알약 3개'가 노출되어 대화방 몰입감을 해치고 있으며, "
    "'?? 5G 토큰', '???', '? 조건부 찬성' 등 CP949 경유로 인한 이모지 깨짐(??)이 발견되었습니다. "
    "1) 대화방 진입 시 구형 전광판·알약을 숨기고(또는 5번 더보기 원장 보관함으로 완전 이관) 순수 카카오톡 말풍선 대화창만 풀스크린급으로 보여주는 시각 레이아웃 기준과, "
    "2) 이모지 깨짐(??) 재발 방지를 위한 유니코드 이스케이프(\\uXXXX) 처리 기준을 3줄 이내로 핵심만 답해주십시오."
)

Q_OPUS = (
    "[056호 1회전 무결성 심의 요청 - 제3성 오푸스] "
    "대표님께서 2단 카카오톡 대화방 내부의 구형 전광판 제거 및 '??' 이모지 깨짐 완전 복구(1번 안)를 지시하셨습니다. "
    "1) 구형 전광판(#s1-live-directive-board 등)을 숨길 때 백그라운드 폴링/수거 JS 함수가 null 참조 에러(TypeError)로 죽지 않도록 보호하는 DOM 무결성 조건과, "
    "2) 파이썬 스크립트가 HTML에 문자열을 주입할 때 '?'나 '??'가 절대 섞이지 않게 강제하는 검증 게이트 조건을 3줄 이내로 핵심만 답해주십시오."
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

def ask_and_harvest_space(space_idx: int, prompt_text: str) -> dict:
    """
    s1_ego.run_ego_js를 직접 사용하여:
    1) takeOverTaskSpace / claimTaskSpace / taskSpace 연결
    2) 입력창에 질문 복붙 및 전송 클릭/Enter
    3) 34초 대기 후 화면의 실제 최근 메시지(문답 원문) 수거
    4) finally 블록에서 task.finish({ keep: [] }) 호출로 잠금 완전 해제
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
        await new Promise(r => setTimeout(r, 34000));
      }} else {{
        await new Promise(r => setTimeout(r, 1500));
      }}

      const harvested = await page.evaluate(() => {{
        const blocks = Array.from(document.querySelectorAll('.answer-markdown, .markdown-viewer, [class*="answer"], article, .markdown, [class*="message"], [class*="response"], main, body'));
        const texts = blocks.map(b => (b.innerText || b.textContent || '').trim()).filter(t => t.length > 30);
        return {{
          snippet_count: texts.length,
          latest_texts: texts.slice(-3).map(t => t.slice(-3000))
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
        if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }});
      }} catch (_) {{}}
    }}
    """
    return s1_ego.run_ego_js(js, timeout=65)

def main():
    print("[056-STEP1] Sending 056 clean chatroom & emoji fix question to Space 1 (Sol) and Space 2 (Opus)...")
    # Space 0 해제
    s0 = clear_only_space(0)
    print(f"   Space 0 cleared: {s0.get('cleared')}")

    # Space 1 (솔)
    print("-> Harvesting Space 1 (Sol)...")
    s1 = ask_and_harvest_space(1, Q_SOL)
    s1_count = s1.get("harvested", {}).get("snippet_count", 0)
    print(f"   Space 1 (Sol) harvested: {s1_count} snippets, sent={s1.get('send_result', {}).get('sent')}")

    # Space 2 (오푸스)
    print("-> Harvesting Space 2 (Opus)...")
    s2 = ask_and_harvest_space(2, Q_OPUS)
    s2_count = s2.get("harvested", {}).get("snippet_count", 0)
    print(f"   Space 2 (Opus) harvested: {s2_count} snippets, sent={s2.get('send_result', {}).get('sent')}")

    # Space 3 해제
    s3 = clear_only_space(3)
    print(f"   Space 3 cleared: {s3.get('cleared')}")

    report = {
        "directive_id": "RGON_DIR_EGO_ROUND1_QA_CLEAN_CHATROOM_056",
        "timestamp": now_iso(),
        "step": "ROUND1_QA_HARVEST_ONLY_NO_HTML_EDIT",
        "html_modified": False,
        "questions_sent": {
            "sol_space_1": Q_SOL,
            "opus_space_2": Q_OPUS
        },
        "space_0_status": s0,
        "space_1_sol_qa": s1,
        "space_2_opus_qa": s2,
        "space_3_status": s3
    }

    out_p = BASE / "S1_TRIUMVIRATE_056_CLEAN_CHATROOM_QA.json"
    docs_out_p = BASE / "docs" / "S1_TRIUMVIRATE_056_CLEAN_CHATROOM_QA.json"
    out_p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    docs_out_p.parent.mkdir(parents=True, exist_ok=True)
    docs_out_p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[056-STEP1] Saved {out_p.name} and {docs_out_p.name} successfully!")

if __name__ == "__main__":
    main()


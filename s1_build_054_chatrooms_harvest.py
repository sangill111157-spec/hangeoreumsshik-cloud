#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[054호 대표님 어명 집행 엔진]
RGON_DIR_EGO_ROUND1_QA_CHATROOMS_054
- [1단계: 코드 수정 절대 금지]
- 에고라이트 Space 1(제2성 솔) 및 Space 2(제3성 오푸스)에 054호 심의 질문 복붙 전송
- 카카오톡 그룹별 채팅방 목록 -> 방 입장 말풍선 대화창 2단 전환 및 5번 더보기 탭 하단 중복 스탬프 정리안 1회전 문답 수거
- S1_TRIUMVIRATE_054_CHATROOMS_QA.json 및 docs/ 동기화 저장
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

QUESTION_054 = (
    "[삼성제도 1회전 공식 문답 심의 요청 - 054호] "
    "이상일 대표님께서 실제 카카오톡 캡처 2장(1. 채팅방 목록 화면, 2. '가공2반 알림방' 내부로 들어간 노란색/흰색 말풍선 대화 화면)을 보내주시며 "
    "'우리 채팅창도 각 그룹별로 들어가서 카카오톡처럼 채팅'하라고 하명하셨습니다. "
    "이에 2번(채팅) 탭을 [1단: 그룹별 채팅방 목록(전체 합동방 / 르곤 독대방 / 삼성 3성 심의방 / 직할 데몬 실행방 / 53곡 음원·유튜브 알림방)]과 "
    "[2단: 방 터치 시 진입하는 카카오톡 말풍선 대화창(좌상단 '<- 뒤로가기' 헤더, 대표님 우측 노란 말풍선 #FEE500, AI/데몬 좌측 프로필+말풍선, '여기까지 읽으셨습니다' 배지, 우측 하단 위/아래 스크롤 버튼, 하단 '+ / 메시지 입력 / 전송' 바)]의 2단 구조로 개편하고, "
    "아울러 5번(더보기) 탭의 4x3 그리드 아래에 길게 늘어져 있던 옛날 중복 스탬프 박스를 접기(아코디언)로 정리하고자 합니다. "
    "1) 시각/UX 관점(제2성 솔)과 무결성/기존 전송·수거 기능 보존 관점(제3성 오푸스)에서 반드시 지켜야 할 핵심 설계 조건 3가지와, "
    "2) 절대 범해서는 안 될 실패 요인(반박/주의사항)을 답변해 주십시오."
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
    1) takeOverTaskSpace / claimTaskSpace / taskSpace 비침습 연결
    2) 입력창에 질문 복붙 및 전송 클릭/Enter
    3) 34초 대기 후 화면의 실제 최근 메시지(문답 원문) 수거
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
    print("[054-STEP1] Sending 054 question to Space 1 (Sol) and Space 2 (Opus) without editing HTML...")
    # Space 0 해제
    s0 = clear_only_space(0)
    print(f"   Space 0 cleared: {s0.get('cleared')}")

    # Space 1 (솔)
    print("-> Harvesting Space 1 (Sol)...")
    s1 = ask_and_harvest_space(1, QUESTION_054)
    s1_count = s1.get("harvested", {}).get("snippet_count", 0)
    print(f"   Space 1 (Sol) harvested: {s1_count} snippets, sent={s1.get('send_result', {}).get('sent')}")

    # Space 2 (오푸스)
    print("-> Harvesting Space 2 (Opus)...")
    s2 = ask_and_harvest_space(2, QUESTION_054)
    s2_count = s2.get("harvested", {}).get("snippet_count", 0)
    print(f"   Space 2 (Opus) harvested: {s2_count} snippets, sent={s2.get('send_result', {}).get('sent')}")

    # Space 3 해제
    s3 = clear_only_space(3)
    print(f"   Space 3 cleared: {s3.get('cleared')}")

    report = {
        "directive_id": "RGON_DIR_EGO_ROUND1_QA_CHATROOMS_054",
        "timestamp": now_iso(),
        "step": "ROUND1_QA_HARVEST_ONLY_NO_HTML_EDIT",
        "html_modified": False,
        "question_sent": QUESTION_054,
        "space_0_status": s0,
        "space_1_sol_qa": s1,
        "space_2_opus_qa": s2,
        "space_3_status": s3
    }

    out_p = BASE / "S1_TRIUMVIRATE_054_CHATROOMS_QA.json"
    docs_out_p = BASE / "docs" / "S1_TRIUMVIRATE_054_CHATROOMS_QA.json"
    out_p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    docs_out_p.parent.mkdir(parents=True, exist_ok=True)
    docs_out_p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[054-STEP1] Saved {out_p.name} and {docs_out_p.name} successfully!")

if __name__ == "__main__":
    main()


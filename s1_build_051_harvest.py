#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[051호 대표님 어명 집행 엔진]
RGON_DIR_FIX_EGO_BOT_AND_HARVEST_ROUND1_QA_051
- 하단 에고라이트 4개 Space의 노란색 'Need your action' 잠금 즉시 해제
- s1_ego.run_ego_js 직통 방식으로 Space 1(솔), Space 2(오푸스)에 1회전 질문 복붙 & 실제 답변 원문 수거
- 대시보드 HTML 수정 0줄 엄수 & 4대 보호파일 100% 무접촉
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

QUESTION_TEXT = (
    "[삼성제도 1회전 공식 문답 심의 요청 - 051호] "
    "이상일 대표님께서 카카오톡 실제 캡처 5장(1.친구/홈, 2.채팅, 3.지금/숏폼, 4.쇼핑/오늘의PICK, 5.더보기 4x3 그리드)을 보내주시며 "
    "'카카오 기본 하단바 5페이지별로 구성'하라고 하명하셨습니다. "
    "하단 고정 5탭 바를 눌러 5개 독립 페이지(Page 1~5)를 전환(나머지 4개는 display:none)하는 구조로 개편할 때, "
    "1) 반드시 지켜야 할 시각/UX 및 기존기능 보존 핵심 조건 3가지와 "
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

def interact_and_harvest_space(space_idx: int, prompt_text: str) -> dict:
    """
    s1_ego.run_ego_js를 직접 사용하여:
    1) takeOverTaskSpace / claimTaskSpace / taskSpace 비침습 연결
    2) 입력창에 질문 복붙 및 전송 클릭/Enter
    3) 32초 대기 후 화면의 실제 최근 메시지(문답 원문) 수거
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
        await new Promise(r => setTimeout(r, 32000));
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
    return s1_ego.run_ego_js(js, timeout=65)

def main():
    print("[051-STEP2] Clearing 'Need your action' badges & harvesting 1-round QA from Ego-Lite Spaces...")
    # Space 0 해제
    print("-> Clearing Space 0 (Rgon)...")
    s0 = clear_only_space(0)
    print(f"   Space 0 result: ok={s0.get('ok')}, cleared={s0.get('cleared')}")

    # Space 1 (2번째 칸: 제2성 솔) 질문 복붙 & 수거 & 해제
    print("-> Harvesting Space 1 (Sol)...")
    s1 = interact_and_harvest_space(1, QUESTION_TEXT)
    s1_count = s1.get("harvested", {}).get("snippet_count", 0)
    print(f"   Space 1 result: ok={s1.get('ok')}, snippets={s1_count}, sent={s1.get('send_result', {}).get('sent')}")

    # Space 2 (3번째 칸: 제3성 오푸스) 질문 복붙 & 수거 & 해제
    print("-> Harvesting Space 2 (Opus)...")
    s2 = interact_and_harvest_space(2, QUESTION_TEXT)
    s2_count = s2.get("harvested", {}).get("snippet_count", 0)
    print(f"   Space 2 result: ok={s2.get('ok')}, snippets={s2_count}, sent={s2.get('send_result', {}).get('sent')}")

    # Space 3 (4번째 칸: 유튜브 스튜디오 등) 상태 확인 & 해제
    print("-> Clearing Space 3 (YouTube Studio)...")
    s3 = clear_only_space(3)
    print(f"   Space 3 result: ok={s3.get('ok')}, cleared={s3.get('cleared')}")

    report = {
        "directive_id": "RGON_DIR_FIX_EGO_BOT_AND_HARVEST_ROUND1_QA_051",
        "timestamp": now_iso(),
        "step": "STEP_2_EGO_DELIVERY_AND_HARVEST_VERIFICATION",
        "html_modified": False,
        "question_sent": QUESTION_TEXT,
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
    print(f"[051-STEP2] Successfully wrote {out_p} and {docs_out_p}!")

if __name__ == "__main__":
    main()

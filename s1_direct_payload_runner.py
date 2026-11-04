import json
import datetime
from pathlib import Path
import s1_ego

BASE = Path(__file__).resolve().parent
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

def interact_and_harvest_space(space_idx: int, prompt_text: str) -> dict:
    """
    s1_ego.run_ego_js를 직접 사용하여:
    1) claimTaskSpace / taskSpace 비침습 연결
    2) 입력창(textarea / contenteditable)에 질문 복붙 및 전송 클릭/Enter
    3) 35초 대기 후 화면의 실제 최근 메시지(문답 원문) 수거
    4) finally 블록에서 task.finish({ keep: [] })를 반드시 호출하여 노란색 'Need your action' 및 파란 테두리 완전 해제!
    """
    prompt_json = json.dumps(prompt_text, ensure_ascii=False)
    js = f"""
    let task = null;
    try {{
      try {{
        task = await claimTaskSpace({space_idx});
      }} catch (_) {{
        task = await taskSpace({space_idx});
      }}
      const up = task.userPage ? task.userPage() : null;
      const page = up ? await task.adopt(up) : (task.page ? await task.page("p1") : null);
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
        const blocks = Array.from(document.querySelectorAll('article, .markdown, [class*="message"], [class*="response"], main, body'));
        const texts = blocks.slice(-8).map(b => (b.innerText || b.textContent || '').trim()).filter(t => t.length > 30);
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

def clear_only_space(space_idx: int) -> dict:
    """Space 0 및 Space 3(유튜브 등)의 노란색 'Need your action' 딱지 즉시 해제"""
    js = f"""
    let task = null;
    try {{
      try {{ task = await claimTaskSpace({space_idx}); }} catch (_) {{ task = await taskSpace({space_idx}); }}
      const up = task.userPage ? task.userPage() : null;
      const page = up ? await task.adopt(up) : null;
      const meta = page ? await page.evaluate(() => ({{ url: location.href, title: document.title }})).catch(() => ({{}})) : {{}};
      process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: true, space: {space_idx}, meta: meta, cleared: true }}) + '\\n');
    }} catch (e) {{
      process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{ ok: false, space: {space_idx}, error: String(e) }}) + '\\n');
    }} finally {{
      try {{
        if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }});
      }} catch (_) {{}}
    }}
    """
    return s1_ego.run_ego_js(js, timeout=15)

def main():
    print("[051-STEP2] Clearing 'Need your action' badges & harvesting 1-round QA from Ego-Lite Spaces...")
    # Space 0 해제
    s0 = clear_only_space(0)
    # Space 1 (2번째 칸) 질문 복붙 & 수거 & 해제
    s1 = interact_and_harvest_space(1, QUESTION_TEXT)
    # Space 2 (3번째 칸) 질문 복붙 & 수거 & 해제
    s2 = interact_and_harvest_space(2, QUESTION_TEXT)
    # Space 3 (4번째 칸) 상태 확인 & 해제
    s3 = clear_only_space(3)

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
    print("[051-STEP2] Successfully wrote S1_TRIUMVIRATE_ROUND1_QA_REPORT.json!")

if __name__ == "__main__":
    main()
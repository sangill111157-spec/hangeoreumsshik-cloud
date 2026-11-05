import json
import datetime
from pathlib import Path
import s1_ego

BASE = Path(__file__).resolve().parent
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

def ask_and_harvest_space(space_idx: int, prompt_text: str) -> dict:
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
        const blocks = Array.from(document.querySelectorAll('article, .markdown, [class*="message"], [class*="response"], main, body'));
        const texts = blocks.slice(-8).map(b => (b.innerText || b.textContent || '').trim()).filter(t => t.length > 30);
        return {{
          snippet_count: texts.length,
          latest_texts: texts.slice(-3).map(t => t.slice(-2800))
        }};
      }}).catch(e => ({{ snippet_count: 0, latest_texts: [], error: String(e) }}));

      process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({{
        ok: true,
        space: {space_idx},
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
    return s1_ego.run_ego_js(js, timeout=60)

def main():
    print("[054-STEP1] Sending 054 question to Space 1 (Sol) and Space 2 (Opus) without editing HTML...")
    s1 = ask_and_harvest_space(1, QUESTION_054)
    s2 = ask_and_harvest_space(2, QUESTION_054)

    report = {
        "directive_id": "RGON_DIR_EGO_ROUND1_QA_CHATROOMS_054",
        "timestamp": now_iso(),
        "step": "ROUND1_QA_HARVEST_ONLY_NO_HTML_EDIT",
        "html_modified": False,
        "question_sent": QUESTION_054,
        "space_1_sol_qa": s1,
        "space_2_opus_qa": s2
    }

    out_p = BASE / "S1_TRIUMVIRATE_054_CHATROOMS_QA.json"
    docs_out_p = BASE / "docs" / "S1_TRIUMVIRATE_054_CHATROOMS_QA.json"
    out_p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    docs_out_p.parent.mkdir(parents=True, exist_ok=True)
    docs_out_p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[054-STEP1] Saved S1_TRIUMVIRATE_054_CHATROOMS_QA.json successfully!")

if __name__ == "__main__":
    main()
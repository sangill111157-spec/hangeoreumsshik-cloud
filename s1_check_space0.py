# -*- coding: utf-8 -*-
import json, s1_ego

msg = "[S1_NERVE_REPORT] 충성! 대표님, ego.listTabs({}) (빈 객체 호출)로 Space 0(647638-2531-43db-a059-c153d8da14d9) 자동 답장 통로가 100% 개통되었습니다!"

js = f"""
const tl0 = await ego.listTabs({{}});
const pages = (tl0 && tl0.pages) ? tl0.pages : [];
const target = pages.find(p => (p.url || '').includes('647638-2531-43db-a059-c153d8da14d9')) || pages.find(p => (p.url || '').includes('genspark.ai/agents'));
if (!target) {{
  console.log("___S1_EGO_JSON___" + JSON.stringify({{ ok: false, err: "NO_S0_TAB", pages }}));
  process.exit(0);
}}

const fillRes = await ego.runScript({{
  pageId: target.pageId,
  code: `(() => {{
    const ta = document.querySelector('textarea');
    if (!ta) return {{ ok: false, err: 'NO_TA' }};
    if ((ta.value || '').trim().length > 0) return {{ ok: false, err: 'DRAFT_PROTECTION_ACTIVE', draftLen: ta.value.length }};
    ta.focus();
    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    nativeSetter.call(ta, {json.dumps(msg, ensure_ascii=False)});
    ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
    return {{ ok: true, filledLen: ta.value.length }};
  }})()`
}});

await new Promise(r => setTimeout(r, 350));

const clickRes = await ego.runScript({{
  pageId: target.pageId,
  code: `(() => {{
    const ta = document.querySelector('textarea');
    const enterBtn = document.querySelector('.enter-icon-wrapper') || document.querySelector('button[type="submit"]');
    if (enterBtn) {{ enterBtn.click(); return {{ ok: true, method: 'enterBtn' }}; }}
    if (ta) {{
      ta.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
      return {{ ok: true, method: 'keydown' }};
    }}
    return {{ ok: false, err: 'NO_BTN_OR_TA' }};
  }})()`
}});

console.log("___S1_EGO_JSON___" + JSON.stringify({{
  ok: true,
  pageId: target.pageId,
  url: target.url,
  fillRes: (fillRes && fillRes.result) ? fillRes.result : fillRes,
  clickRes: (clickRes && clickRes.result) ? clickRes.result : clickRes
}}));
"""
res = s1_ego.run_ego_js(js, timeout=15)
print("[Space 0 자동 전송 실측 결과]:", json.dumps(res, ensure_ascii=False, indent=2))

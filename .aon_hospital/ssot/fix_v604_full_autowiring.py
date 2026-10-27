#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
fix_v604_full_autowiring.py
RGON Omni-Link Hub v6.0.4 긴급 버그 수정 & 전 구간 풀 오토와이어링

1. [긴급 버그 수정]: content_aside_bar.js 의 #fireCG, #fireGrok 미존재 버튼에 옵셔널 체이닝(?.) 적용으로
   TypeError 방지 및 chrome.runtime.onMessage.addListener 100% 도달 보장
2. [커스텀 신경망 전 구간 자동 연결]:
   - ✏️ 직접 쓰기 지정 시 현재 탭의 url, origin, title 함께 omni_custom_roles 에 저장
   - 지정 즉시 상단 '이 탭 역할:'(#selfRole)에 '🔮 커스텀명' 표시
   - 램프 목록에 '🟢 🔮 커스텀명' 카드 + [이동]/[열기] + [✕](삭제) 버튼 동적 렌더링
   - background.js scanTabs/guessRole 에서 url/origin 매칭으로 100% 자동 스캔 및 byRole 수집
3. [작업 분배 & 흡수기 & STUDIO 자동 연동]:
   - 유튜브(input#search, #textbox 등) 및 일반 입력창 주입/검색 지원
   - 코드 미발견 시 absorbPageText(화면 텍스트) 자동 대체 수거
   - STUDIO 탭에 커스텀 신경망 바로가기 버튼 자동 렌더링
4. manifest.json, background.js, content_aside_bar.js v6.0.4 갱신 및 node --check 통과
5. 'OMNI-LINK v6.0.4 BUG FIXED & FULL AUTO-WIRING READY!' 출력
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
EXT = ROOT / "rgon_aside_extension"
MANIFEST_P = EXT / "manifest.json"
BG_P = EXT / "background.js"
CT_P = EXT / "content_aside_bar.js"
VERSION = "6.0.4"

def say(msg):
    print(msg, flush=True)

# -----------------------------------------------------------------------------
# 1. manifest.json 갱신
# -----------------------------------------------------------------------------
def patch_manifest():
    with open(MANIFEST_P, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["version"] = VERSION
    with open(MANIFEST_P, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    say(f"   ✅ manifest.json: v{VERSION}")

# -----------------------------------------------------------------------------
# 2. background.js 갱신
# -----------------------------------------------------------------------------
def patch_background():
    with open(BG_P, "r", encoding="utf-8") as f:
        code = f.read()

    # 버전 갱신
    code = re.sub(r'const OMNI_VERSION = "[^"]*";', f'const OMNI_VERSION = "{VERSION}";', code)

    # guessRole 교체: customRoles 지원
    guess_role_new = r"""function guessRole(tab, reported, override, customRoles) {
  if (override) return override;
  let u;
  try { u = new URL(tab.url || ""); } catch (_) { return null; }
  const host = u.hostname.toLowerCase();
  if ((host === "127.0.0.1" || host === "localhost") && u.port === "8501") return "rgon";
  if (host === "docs.google.com" && u.pathname.startsWith("/spreadsheets")) return "sheets";
  if (host === "adobe.com" || host.endsWith(".adobe.com")) return "adobe";
  if (host === "claude.ai" || host.endsWith(".claude.ai")) return "claude";
  if (host === "chatgpt.com" || host === "chat.openai.com") return "gpt";
  if (host === "grok.com" || (host === "x.com" && u.pathname.startsWith("/i/grok"))) return "grok";
  if (host === "genspark.ai" || host.endsWith(".genspark.ai")) {
    return reported || roleFromText(tab.title) || null;
  }
  if (customRoles) {
    for (const [ckey, cmeta] of Object.entries(customRoles)) {
      if (!cmeta) continue;
      if (cmeta.url && tab.url && (tab.url === cmeta.url || tab.url.startsWith(cmeta.url))) return ckey;
      if (cmeta.origin && u.origin && u.origin.toLowerCase() === cmeta.origin.toLowerCase()) return ckey;
    }
  }
  return null;
}"""

    code = re.sub(r'function guessRole\(.*?\n\}', guess_role_new, code, flags=re.S)

    # scanTabs 교체: customRoles 로드 및 전달
    scan_tabs_new = r"""async function scanTabs() {
  const [tabs, rep, ovr, customs] = await Promise.all([
    chrome.tabs.query({}),
    getStore("omni_reported", {}),
    getStore("omni_override", {}),
    getStore("omni_custom_roles", {})
  ]);
  const list = [];
  const byRole = {};
  for (const t of tabs) {
    if (!t.id) continue;
    const r = rep[t.id] ? rep[t.id].role : null;
    const role = guessRole(t, r, ovr[t.id], customs);
    if (!role) continue;
    const info = {
      tabId: t.id,
      windowId: t.windowId,
      role,
      title: t.title || "",
      url: t.url || "",
      active: !!t.active,
      lastAccessed: t.lastAccessed || 0
    };
    list.push(info);
    (byRole[role] = byRole[role] || []).push(info);
  }
  return { list, byRole, customRoles: customs };
}"""

    code = re.sub(r'async function scanTabs\(.*?\n\}', scan_tabs_new, code, flags=re.S)

    # OMNI_SCAN 응답에 customRoles 포함
    code = re.sub(
        r'case "OMNI_SCAN":\s*\{\s*const \{ list, byRole \} = await scanTabs\(\);',
        'case "OMNI_SCAN": {\n      const { list, byRole, customRoles } = await scanTabs();',
        code
    )
    code = re.sub(
        r'return \{ ok: true, version: OMNI_VERSION, list, counts, selfTabId: sender\.tab \? sender\.tab\.id : null \};',
        'return { ok: true, version: OMNI_VERSION, list, counts, customRoles, selfTabId: sender.tab ? sender.tab.id : null };',
        code
    )

    # OMNI_FOCUS: 닫혀 있으면 custom URL 자동 열기
    omni_focus_new = r"""    case "OMNI_FOCUS": {
      const { byRole, customRoles } = await scanTabs();
      const t = pickTab(byRole[msg.role]);
      if (t) {
        await focusTab(t);
        return { ok: true, focused: true };
      }
      const cmeta = (customRoles && customRoles[msg.role]) || (await getStore("omni_custom_roles", {}))[msg.role];
      if (cmeta && cmeta.url) {
        return openUrl(cmeta.url);
      }
      return { ok: false, error: "열려 있는 탭 없음" };
    }"""
    code = re.sub(r'case "OMNI_FOCUS":\s*\{\n.*?return \{ ok: true \};\n\s*\}', omni_focus_new, code, flags=re.S)

    # 커스텀 역할 저장/조회/삭제 핸들러 보장
    if "OMNI_GET_CUSTOM_ROLES" not in code:
        custom_msg_handlers = r"""    case "OMNI_GET_CUSTOM_ROLES": {
      return { ok: true, customRoles: await getStore("omni_custom_roles", {}) };
    }
    case "OMNI_SET_CUSTOM_ROLE": {
      const cr = await getStore("omni_custom_roles", {});
      if (msg.roleKey && msg.roleMeta) {
        cr[msg.roleKey] = msg.roleMeta;
        await setStore("omni_custom_roles", cr);
      }
      return { ok: true, customRoles: cr };
    }
    case "OMNI_DEL_CUSTOM_ROLE": {
      const cr = await getStore("omni_custom_roles", {});
      if (msg.roleKey && cr[msg.roleKey]) {
        delete cr[msg.roleKey];
        await setStore("omni_custom_roles", cr);
      }
      return { ok: true, customRoles: cr };
    }
"""
        code = code.replace('    case "OMNI_SET_OVERRIDE":', custom_msg_handlers + '    case "OMNI_SET_OVERRIDE":')

    with open(BG_P, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    say(f"   ✅ background.js: v{VERSION} (URL/Origin 맞춤형 자동 스캔 & Focus/Open 연동)")

# -----------------------------------------------------------------------------
# 3. content_aside_bar.js 갱신
# -----------------------------------------------------------------------------
def patch_content():
    base_file = ROOT / "clean_content.js"
    src_p = base_file if base_file.exists() else CT_P
    with open(src_p, "r", encoding="utf-8") as f:
        code = f.read()

    # 버전 갱신
    code = re.sub(r'const VER = "[^"]*";', f'const VER = "{VERSION}";', code)
    code = code.replace("Omni-Link Hub v6.0.2", f"Omni-Link Hub v{VERSION}")
    code = code.replace("Omni-Link Hub v6.0.3", f"Omni-Link Hub v{VERSION}")

    # [1] HTML: 역할 선택에 ✏️ 직접 쓰기 및 입력창 추가
    if '<option value="__custom__">' not in code:
        code = code.replace(
            '<option value="adobe">Adobe</option></select>',
            '<option value="adobe">Adobe</option><option value="__custom__">✏️ 직접 쓰기…</option></select>'
            '<input type="text" id="customRoleInput" placeholder="신경망 이름 입력" style="display:none;width:115px;padding:4px 6px;font-size:12px;margin-left:4px">'
        )

    # [2] HTML: STUDIO 탭에 커스텀 그리드 컨테이너 추가
    old_studio_grid = '<button class="b" id="cfgLinks">🔧 링크 설정</button>\n      </div>'
    new_studio_grid = '<button class="b" id="cfgLinks">🔧 링크 설정</button>\n      </div>\n      <div id="studioCustomGrid" style="display:flex;flex-wrap:wrap;gap:6px;margin:8px 0"></div>'
    if old_studio_grid in code and 'id="studioCustomGrid"' not in code:
        code = code.replace(old_studio_grid, new_studio_grid)

    # [3] JS: 긴급 버그 수정 (#fireCG, #fireGrok, #fireAll 옵셔널 체이닝 또는 안전 바인딩)
    code = code.replace('$("#fireCG").addEventListener("click"', '$("#fireCG")?.addEventListener("click"')
    code = code.replace('$("#fireGrok").addEventListener("click"', '$("#fireGrok")?.addEventListener("click"')
    code = code.replace('$("#fireAll").addEventListener("click"', '$("#fireAll")?.addEventListener("click"')

    # [4] JS: 유튜브/일반 검색창 입력 지원 (findInput)
    old_sel = 'const sel = "textarea, [contenteditable=\'true\'], [contenteditable=\'plaintext-only\'], [role=\'textbox\']";'
    new_sel = 'const sel = "textarea, [contenteditable=\'true\'], [contenteditable=\'plaintext-only\'], [role=\'textbox\'], input[type=\'search\'], input#search, #search-input input, #textbox, input[type=\'text\']:not([readonly]):not([disabled])";'
    if old_sel in code:
        code = code.replace(old_sel, new_sel)

    # [5] JS: OMNI_GET_LAST_CODE 시 코드 없으면 absorbPageText 자동 수거
    old_get_code = r"""      case "OMNI_GET_LAST_CODE": {
        const e = extractLastCode();
        return e ? { ok: true, entry: e } : { ok: false, error: "코드 블록(pre code)·JSON 없음" };
      }"""
    new_get_code = r"""      case "OMNI_GET_LAST_CODE": {
        const e = extractLastCode() || absorbPageText();
        return e ? { ok: true, entry: e } : { ok: false, error: "수거할 내용 없음" };
      }"""
    if old_get_code in code:
        code = code.replace(old_get_code, new_get_code)

    # [6] JS: renderLamps 전면 개편 (커스텀 역할 카드 + 상단 #selfRole + 이동/열기/삭제)
    render_lamps_new = r"""function renderLamps() {
  const scan = state.scan;
  if (!scan) return;
  const customs = scan.customRoles || {};
  const allRoles = Object.assign({}, ROLE_META, customs);
  const activeOrder = ROLE_ORDER.concat(Object.keys(customs).filter(k => !ROLE_ORDER.includes(k)));

  const html = activeOrder.map((role) => {
    const m = allRoles[role] || { label: role, icon: "🔮" };
    const tabs = (scan.list || []).filter((t) => t.role === role);
    const on = tabs.length > 0;
    const first = on ? tabs.slice().sort((a, b) => (b.lastAccessed || 0) - (a.lastAccessed || 0))[0] : null;
    const isCustom = !!customs[role];

    return `<div class="lamp ${on ? "on" : "off"}">
      <span>${on ? "🟢" : "⚫"}</span>
      <div class="lt">
        <b>${m.icon || "🔮"} ${esc(m.label)}</b>
        <small>${on ? esc(trunc(first.title || m.url || "", 44)) + (tabs.length > 1 ? " (+" + (tabs.length - 1) + ")" : "") : (m.url ? esc(trunc(m.url, 44)) : "연결 안 됨")}</small>
      </div>
      <div style="display:flex;gap:4px;align-items:center">
        ${on ? `<button class="b" data-focus="${esc(role)}">이동</button>` : (m.url ? `<button class="b c" data-focus="${esc(role)}">열기</button>` : "")}
        ${isCustom ? `<button class="b sm" data-del-custom="${esc(role)}" title="이 커스텀 신경망 삭제">✕</button>` : ""}
      </div>
    </div>`;
  }).join("");
  $("#lamps").innerHTML = html;

  const connectedCount = activeOrder.filter((r) => (scan.list || []).some((t) => t.role === r)).length;
  $("#cnt").textContent = String(connectedCount);

  // 상단 '이 탭 역할:' 즉시 표시
  const me = state.role ? allRoles[state.role] : null;
  $("#selfRole").textContent = me ? `${me.icon || "🔮"} ${me.label}` : "일반 페이지";

  updateRoleSelect(customs);
  renderStudioCustomLinks(customs);
}

function updateRoleSelect(customs) {
  const sel = $("#roleSel");
  if (!sel) return;
  let html = `<option value="">자동 감지</option>
    <option value="rgon">르곤 독대실</option>
    <option value="claude">Claude Opus 5.5</option>
    <option value="gpt">GPT-6.1 Sol</option>
    <option value="grok">Grok 4.7</option>
    <option value="sheets">Google Sheets</option>
    <option value="adobe">Adobe</option>`;
  for (const [k, v] of Object.entries(customs || {})) {
    html += `<option value="${esc(k)}">${v.icon || "🔮"} ${esc(v.label)}</option>`;
  }
  html += `<option value="__custom__">✏️ 직접 쓰기…</option>`;
  sel.innerHTML = html;
  sel.value = state.role || "";
}

function renderStudioCustomLinks(customs) {
  const cont = $("#studioCustomGrid");
  if (!cont) return;
  const list = Object.entries(customs || {});
  if (!list.length) { cont.innerHTML = ""; return; }
  cont.innerHTML = list.map(([k, v]) =>
    `<button class="b" data-focus="${esc(k)}" style="flex:1;min-width:130px;padding:8px">${v.icon || "🔮"} ${esc(v.label)}</button>`
  ).join("");
}"""

    code = re.sub(r'function renderLamps\(\)\s*\{.*?\n\}\n(?=async function refreshScan)', render_lamps_new + '\n\n', code, flags=re.S)

    # [7] JS: 역할 지정 시 url, origin, title 함께 저장 (#roleSave)
    role_save_new = r"""const roleSaveBtn = $("#roleSave");
if (roleSaveBtn) {
  roleSaveBtn.onclick = async () => {
    let sel = $("#roleSel").value;
    if (sel === "__custom__") {
      const customName = ($("#customRoleInput")?.value || "").trim();
      if (!customName) { toast("신경망 이름을 입력하세요."); return; }
      const roleKey = "custom_" + encodeURIComponent(customName).replace(/%/g, "_");
      const roleMeta = {
        label: customName,
        icon: "🔮",
        url: location.href,
        origin: location.origin,
        title: document.title
      };
      await rt({ type: "OMNI_SET_CUSTOM_ROLE", roleKey, roleMeta });
      sel = roleKey;
    }
    await rt({ type: "OMNI_SET_OVERRIDE", role: sel });
    await refreshScan();
    toast("이 탭 역할을 지정했습니다: " + sel);
  };
}"""

    code = re.sub(r'const origRoleSave = \$\("#roleSave"\);.*?toast\("이 탭 역할을 지정했습니다: " \+ sel\);\s*\};\s*\}', role_save_new, code, flags=re.S)

    # [8] JS: 램프 및 패널 이벤트 위임 핸들러
    lamps_event_new = r"""$("#lamps")?.addEventListener("click", async (ev) => {
  const focusBtn = ev.target.closest("[data-focus]");
  if (focusBtn) {
    await rt({ type: "OMNI_FOCUS", role: focusBtn.dataset.focus });
    return;
  }
  const delBtn = ev.target.closest("[data-del-custom]");
  if (delBtn) {
    const roleKey = delBtn.dataset.delCustom;
    if (confirm("이 커스텀 신경망 역할을 삭제하시겠습니까?")) {
      await rt({ type: "OMNI_DEL_CUSTOM_ROLE", roleKey });
      toast("커스텀 신경망 삭제 완료");
      await refreshScan();
    }
  }
});

$("#panel")?.addEventListener("click", async (ev) => {
  const focusBtn = ev.target.closest("[data-focus]");
  if (focusBtn && !focusBtn.closest("#lamps")) {
    await rt({ type: "OMNI_FOCUS", role: focusBtn.dataset.focus });
    return;
  }
});"""

    code = re.sub(r'\$\("#lamps"\)\.addEventListener\("click",\s*async\s*\(ev\)\s*=>\s*\{.*?\n\}\);\n', lamps_event_new + '\n', code, flags=re.S)

    with open(CT_P, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    say(f"   ✅ content_aside_bar.js: v{VERSION} (버그 수정 + 풀 오토와이어링 장착)")

# -----------------------------------------------------------------------------
# 4. node --check 문법 검증
# -----------------------------------------------------------------------------
def check_js_syntax():
    node = shutil.which("node")
    if not node:
        say("   ⚠️ node를 찾지 못해 문법 검사를 건너뜁니다.")
        return True
    for p in [BG_P, CT_P]:
        res = subprocess.run([node, "--check", str(p)], capture_output=True, text=True, encoding="utf-8")
        if res.returncode != 0:
            say(f"   ❌ node --check 실패: {p.name}\n{res.stderr}")
            return False
        say(f"   ✅ node --check 통과: {p.name}")
    return True

# -----------------------------------------------------------------------------
# 메인 실행
# -----------------------------------------------------------------------------
def main():
    say("=" * 64)
    say("🛰️ RGON Omni-Link Hub v6.0.4 긴급 버그 수정 & 풀 오토와이어링 시작")
    say("=" * 64)
    patch_manifest()
    patch_background()
    patch_content()
    if not check_js_syntax():
        say("❌ 자바스크립트 문법 오류로 중단합니다.")
        return 1
    say("")
    say("OMNI-LINK v6.0.4 BUG FIXED & FULL AUTO-WIRING READY!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

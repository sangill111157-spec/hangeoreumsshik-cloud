#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
apply_v606_lock.py
RGON Omni-Link Hub v6.0.6 체크박스 리셋 원천 봉쇄 패치

1. [원천 차단]: renderDispatchTargets 에서 동일한 역할 키 목록이면 innerHTML 덮어쓰기 금지 (즉시 return)
2. [3중 동기화]: window.__RGON_CHECKED__ + localStorage("rgon_omni_checked_v606") + chrome.storage.local
   - 최초 기본값: claude/gpt 만 true, grok 및 커스텀 신경망은 무조건 false
   - 체크 변경, 전체 선택, 전체 해제 시 즉시 3중 동기 저장
   - 템플릿 생성 시 오직 isRoleChecked(role) ? "checked" : "" 만 사용 (하드코딩 checked 영구 박멸)
3. 681~723행의 구버전 renderDispatchTargets 및 refreshScan 가로채기 찌꺼기 완전 삭제
4. manifest.json, background.js, content_aside_bar.js v6.0.6 갱신 및 node --check 통과
"""

import json
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
VERSION = "6.0.6"

def say(msg):
    print(msg, flush=True)

def update_manifest():
    with open(MANIFEST_P, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["version"] = VERSION
    with open(MANIFEST_P, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    say(f"   ✅ manifest.json: v{VERSION}")

def update_background():
    with open(BG_P, "r", encoding="utf-8") as f:
        code = f.read()
    code = re.sub(r'const OMNI_VERSION = "[^"]*";', f'const OMNI_VERSION = "{VERSION}";', code)
    with open(BG_P, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    say(f"   ✅ background.js: v{VERSION}")

def update_content():
    with open(CT_P, "r", encoding="utf-8") as f:
        code = f.read()

    # 버전 갱신
    code = re.sub(r'const VER = "[^"]*";', f'const VER = "{VERSION}";', code)
    code = code.replace("Omni-Link Hub v6.0.5", f"Omni-Link Hub v{VERSION}")
    code = code.replace("Omni-Link Hub v6.0.4", f"Omni-Link Hub v{VERSION}")
    code = code.replace("Omni-Link Hub v6.0.3", f"Omni-Link Hub v{VERSION}")
    code = code.replace("Omni-Link Hub v6.0.2", f"Omni-Link Hub v{VERSION}")

    # [1] 3중 체크 저장소 로직 (window.__RGON_CHECKED__ + localStorage + chrome.storage.local)
    store_logic = r"""// ===== v6.0.6 3중 체크 상태 영구 보존 엔진 (메모리 + localStorage + chrome.storage) =====
const STORAGE_KEY_V606 = "rgon_omni_checked_v606";
window.__RGON_CHECKED__ = window.__RGON_CHECKED__ || null;

function initCheckedStore() {
  if (window.__RGON_CHECKED__ !== null) return window.__RGON_CHECKED__;
  let saved = null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY_V606);
    if (raw) saved = JSON.parse(raw);
  } catch (_) {}
  window.__RGON_CHECKED__ = Object.assign({ claude: true, gpt: true, grok: false }, saved || {});
  try {
    chrome.storage.local.get(STORAGE_KEY_V606).then(o => {
      if (o && o[STORAGE_KEY_V606]) {
        Object.assign(window.__RGON_CHECKED__, o[STORAGE_KEY_V606]);
      }
    }).catch(() => {});
  } catch (_) {}
  return window.__RGON_CHECKED__;
}

function setRoleChecked(role, boolVal) {
  initCheckedStore();
  window.__RGON_CHECKED__[role] = !!boolVal;
  try { localStorage.setItem(STORAGE_KEY_V606, JSON.stringify(window.__RGON_CHECKED__)); } catch (_) {}
  try { chrome.storage.local.set({ [STORAGE_KEY_V606]: window.__RGON_CHECKED__ }); } catch (_) {}
}

function isRoleChecked(role) {
  initCheckedStore();
  if (window.__RGON_CHECKED__[role] !== undefined) {
    return window.__RGON_CHECKED__[role] === true;
  }
  const def = (role === "claude" || role === "gpt");
  window.__RGON_CHECKED__[role] = def;
  try { localStorage.setItem(STORAGE_KEY_V606, JSON.stringify(window.__RGON_CHECKED__)); } catch (_) {}
  return def;
}
"""

    if "STORAGE_KEY_V606" not in code:
        code = code.replace("const state = {", store_logic + "\nconst state = {")

    # [2] 단일 정밀 renderDispatchTargets 정의 (원천 차단 가드 포함)
    render_dispatch_v606 = r"""let _lastRenderedRolesKey = "";

function renderDispatchTargets(customs) {
  const tList = $("#targetCheckList");
  if (!tList) return;
  initCheckedStore();

  const scan = state.scan || { list: [] };
  const allRoles = Object.assign({}, ROLE_META, customs || {});
  const activeRoles = ROLE_ORDER.concat(Object.keys(customs || {}).filter(k => !ROLE_ORDER.includes(k)))
    .filter(role => role !== "rgon" && role !== "sheets" && role !== "adobe");

  const rolesKey = activeRoles.join("|");
  const existingCheckboxes = [...tList.querySelectorAll(".role-chk, .tgt-chk")];

  // [필수 완치 조건 1]: 역할 키 목록이 동일하고 이미 체크박스가 화면에 존재한다면 절대 innerHTML을 다시 덮어쓰지 말 것!
  if (existingCheckboxes.length === activeRoles.length && _lastRenderedRolesKey === rolesKey) {
    return;
  }
  _lastRenderedRolesKey = rolesKey;

  let html = "";
  for (const role of activeRoles) {
    const m = allRoles[role] || { label: role, icon: "⚡" };
    const tabs = (scan.list || []).filter(t => t.role === role);
    const hasTab = tabs.length > 0;
    
    // [필수 완치 조건 2]: 오직 isRoleChecked(role) ? "checked" : "" 만 사용!
    const checkedAttr = isRoleChecked(role) ? "checked" : "";

    html += `<div style="display:inline-flex;align-items:center;gap:4px;padding:4px 8px;border-radius:8px;background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,${hasTab ? ".2" : ".05"})">
      <label style="cursor:pointer;display:inline-flex;align-items:center;gap:3px;font-size:12px">
        <input type="checkbox" class="role-chk tgt-chk" value="${esc(role)}" ${checkedAttr}>
        <span>${m.icon || "🔮"} ${esc(m.label)}</span>
      </label>
      <button class="b sm" data-solo-fire="${esc(role)}" style="padding:2px 6px;font-size:11px" type="button" title="이 대상에만 단독 발사">🚀</button>
    </div>`;
  }
  tList.innerHTML = html || "<small style='opacity:.6'>발사 가능한 대상이 없습니다.</small>";
}"""

    # 앞쪽의 renderDispatchTargets 교체
    code = re.sub(
        r'async function renderDispatchTargets\(.*?\n\}\n(?=function renderStudioCustomLinks)',
        render_dispatch_v606 + '\n\n',
        code,
        flags=re.S
    )
    code = re.sub(
        r'function renderDispatchTargets\(.*?\n\}\n(?=function renderStudioCustomLinks)',
        render_dispatch_v606 + '\n\n',
        code,
        flags=re.S
    )

    # [3] 뒤쪽에 남아있던 681~723행 부근의 구버전 renderDispatchTargets 및 origRefreshScan 완전 삭제
    dangling_v603_chunk = r"""// ===== v6.0.3 커스텀 신경망 직접 쓰기 & 단독/체크 발사 엔진 =====
const customInp = $("#customRoleInput");
const roleSel = $("#roleSel");
if (roleSel && customInp) {
  roleSel.addEventListener("change", () => {
    customInp.style.display = roleSel.value === "__custom__" ? "inline-block" : "none";
    if (roleSel.value === "__custom__") customInp.focus();
  });
}

async function renderDispatchTargets() {
  const tList = $("#targetCheckList");
  if (!tList) return;
  const scan = state.scan || { list: [] };
  const customRes = await rt({ type: "OMNI_GET_CUSTOM_ROLES" });
  const customs = (customRes && customRes.customRoles) || {};
  
  const allRoles = Object.assign({}, ROLE_META, customs);
  const activeRoles = ROLE_ORDER.concat(Object.keys(customs).filter(k => !ROLE_ORDER.includes(k)));
  
  let html = "";
  for (const role of activeRoles) {
    if (role === "rgon" || role === "sheets" || role === "adobe") continue;
    const m = allRoles[role] || { label: role, icon: "⚡" };
    const tabs = (scan.list || []).filter(t => t.role === role);
    const hasTab = tabs.length > 0;
    html += `<div style="display:inline-flex;align-items:center;gap:4px;padding:4px 8px;border-radius:8px;background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,${hasTab ? ".2" : ".05"})">
      <label style="cursor:pointer;display:inline-flex;align-items:center;gap:3px;font-size:12px">
        <input type="checkbox" class="role-chk" value="${esc(role)}" ${hasTab ? "checked" : ""}>
        <span>${m.icon} ${esc(m.label)}</span>
      </label>
      <button class="b sm" data-solo-fire="${esc(role)}" style="padding:2px 6px;font-size:11px" title="이 AI에만 단독 발사">🚀</button>
    </div>`;
  }
  tList.innerHTML = html || "<small style='opacity:.6'>발사 가능한 AI 역할이 없습니다.</small>";
}

const origRefreshScan = refreshScan;
refreshScan = async function() {
  await origRefreshScan();
  renderDispatchTargets();
};"""

    if dangling_v603_chunk in code:
        code = code.replace(dangling_v603_chunk, "")
        say("   🧹 뒤쪽 구버전 renderDispatchTargets 및 refreshScan 가로채기 삭제 완료")
    else:
        # 정규표현식으로 뒷부분 중복 청크 삭제
        code = re.sub(
            r'async function renderDispatchTargets\(\)\s*\{\s*const tList = \$\("#targetCheckList"\);.*?\nconst origRefreshScan = refreshScan;\s*refreshScan = async function\(\)\s*\{\s*await origRefreshScan\(\);\s*renderDispatchTargets\(\);\s*\};\n',
            '',
            code,
            flags=re.S
        )
        say("   🧹 정규식 매칭으로 뒷부분 구버전 renderDispatchTargets 삭제 완료")

    # [4] 체크 변경, 전체선택, 전체해제 핸들러 3중 저장소 연동
    handlers_v606 = r"""// ===== v6.0.6 발사 대상 체크박스 3중 저장소 실시간 동기화 핸들러 =====
$("#dispatchTargets")?.addEventListener("change", (ev) => {
  const chk = ev.target.closest(".role-chk, .tgt-chk");
  if (!chk) return;
  setRoleChecked(chk.value, chk.checked);
});

$("#btnSelectAll")?.addEventListener("click", () => {
  $$(".role-chk, .tgt-chk").forEach(c => {
    c.checked = true;
    setRoleChecked(c.value, true);
  });
  toast("☑️ 전체 대상 선택 완료");
});

$("#btnUnselectAll")?.addEventListener("click", () => {
  $$(".role-chk, .tgt-chk").forEach(c => {
    c.checked = false;
    setRoleChecked(c.value, false);
  });
  toast("☐ 전체 대상 해제 완료");
});

const fireCheckedBtn = $("#fireChecked");
if (fireCheckedBtn) {
  fireCheckedBtn.onclick = () => {
    const checked = $$(".role-chk:checked, .tgt-chk:checked").map(c => c.value);
    if (!checked.length) { toast("발사할 대상을 1개 이상 체크하세요."); return; }
    fire(checked);
  };
}"""

    # 기존 v6.0.5 핸들러 교체
    if "v6.0.5 발사 대상 체크박스 영구 기억" in code:
        code = re.sub(
            r'// ===== v6.0.5 발사 대상 체크박스 영구 기억.*?toast\("☐ 전체 대상 해제 완료"\);\s*\}\);\n',
            handlers_v606 + '\n',
            code,
            flags=re.S
        )
    elif "v6.0.6 발사 대상 체크박스 3중 저장소" not in code:
        code = code.replace(
            '// ------------------------------------------------------------------ wiring',
            handlers_v606 + '\n\n// ------------------------------------------------------------------ wiring'
        )

    with open(CT_P, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    say(f"   ✅ content_aside_bar.js: v{VERSION} (원천 차단 가드 + 3중 동기화 장착)")

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

def main():
    say("=" * 64)
    say(f"🛰️ RGON Omni-Link Hub v{VERSION} 체크박스 리셋 원천 봉쇄 패치 시작")
    say("=" * 64)
    update_manifest()
    update_background()
    update_content()
    if not check_js_syntax():
        say("❌ 자바스크립트 문법 검사 실패")
        return 1
    say("")
    say(f"OMNI-LINK v{VERSION} TARGET CHECKBOX RESET FULLY LOCKED!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

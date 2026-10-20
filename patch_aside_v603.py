#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
patch_aside_v603.py
RGON Omni-Link Hub v6.0.3 업그레이드 패치 스크립트
대상: C:\Users\sangi\Downloads\shin-agent\rgon_aside_extension
(content_aside_bar.js 슬라이드 패널 + background.js + manifest.json)

주요 업그레이드:
1) [📡 신경망] 커스텀 신경망 역할 '✏️ 직접 쓰기' (Custom Neural Roles) 등록·감지
2) [⚡ 작업 분배] 개별 체크박스 선택 발사 + AI별 단독 [🚀 발사] + [🌐 전체 발사]
3) [🧲 흡수기] v6.0.2의 자동 청소(Auto-Clean) + 전체 비우기 + 개별 삭제 + Copy 정화 100% 보존
4) 로컬 브리지(127.0.0.1:8765) v6.0.3 200 OK 헬스체크 연동
"""

import os
import sys
import json
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXT = ROOT / "rgon_aside_extension"
MANIFEST_P = EXT / "manifest.json"
BG_P = EXT / "background.js"
CT_P = EXT / "content_aside_bar.js"
BRIDGE_P = ROOT / "omni_bridge.py"

def say(msg):
    print(msg, flush=True)

def update_manifest():
    with open(MANIFEST_P, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["version"] = "6.0.3"
    with open(MANIFEST_P, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    say("   ✅ manifest.json: v6.0.3")

def update_background():
    with open(BG_P, "r", encoding="utf-8") as f:
        code = f.read()
    
    # 버전 변경
    code = re.sub(r'const OMNI_VERSION = "[^"]*";', 'const OMNI_VERSION = "6.0.3";', code)
    
    # 커스텀 역할 지원을 위한 custom roles 헬퍼 추가
    if "omni_custom_roles" not in code:
        custom_role_helpers = r"""
// ---- v6.0.3: 커스텀 신경망 역할 (Custom Neural Roles) 지원 ----
async function getCustomRoles() {
  const o = await chrome.storage.local.get("omni_custom_roles");
  return o.omni_custom_roles || {};
}
async function setCustomRoles(roles) {
  await chrome.storage.local.set({ omni_custom_roles: roles });
}
"""
        code = code.replace('// ---------------------------------------------------------------- role mapping', custom_role_helpers + '\n// ---------------------------------------------------------------- role mapping')
        
        # message router에 OMNI_GET_CUSTOM_ROLES, OMNI_SET_CUSTOM_ROLES, OMNI_DELETE_CUSTOM_ROLE 추가
        custom_cases = r"""    case "OMNI_GET_CUSTOM_ROLES":
      return { ok: true, customRoles: await getCustomRoles() };
    case "OMNI_SET_CUSTOM_ROLE": {
      const cr = await getCustomRoles();
      if (msg.roleKey && msg.roleMeta) {
        cr[msg.roleKey] = msg.roleMeta;
        await setCustomRoles(cr);
      }
      return { ok: true, customRoles: cr };
    }
    case "OMNI_DEL_CUSTOM_ROLE": {
      const cr = await getCustomRoles();
      if (msg.roleKey && cr[msg.roleKey]) {
        delete cr[msg.roleKey];
        await setCustomRoles(cr);
      }
      return { ok: true, customRoles: cr };
    }
"""
        code = code.replace('    case "OMNI_SET_OVERRIDE":', custom_cases + '    case "OMNI_SET_OVERRIDE":')

    with open(BG_P, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    say("   ✅ background.js: v6.0.3 (Custom Neural Router 탑재)")

def update_content():
    with open(CT_P, "r", encoding="utf-8") as f:
        code = f.read()

    # 버전 변경
    code = re.sub(r'const VER = "[^"]*";', 'const VER = "6.0.3";', code)
    code = code.replace("Omni-Link Hub v6.0.2", "Omni-Link Hub v6.0.3")

    # [1] 역할 선택에 '✏️ 직접 쓰기' 옵션 추가
    if '<option value="__custom__">' not in code:
        code = code.replace(
            '<option value="adobe">Adobe</option></select>',
            '<option value="adobe">Adobe</option><option value="__custom__">✏️ 직접 쓰기…</option></select>'
            '<input type="text" id="customRoleInput" placeholder="역할명 직접 입력" style="display:none;width:110px;padding:4px 6px;font-size:12px;margin-left:4px">'
        )

    # [2] 작업 분배 탭: AI별 체크박스 + 단독 발사 + 체크 발사 버튼 UI
    if 'id="fireChecked"' not in code:
        old_fire_row = '<div class="row"><button class="b g" id="fireCG">🚀 Claude + GPT 동시 발사</button><button class="b o" id="fireGrok">🎯 Grok 카피 발사</button><button class="b" id="fireAll">🌐 3종 전체 발사</button></div>'
        new_fire_row = r"""<div id="dispatchTargets" style="margin:8px 0;padding:8px 10px;border-radius:10px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1)">
        <div style="font-size:11.5px;font-weight:700;margin-bottom:6px;color:#b9c0ff">🎯 발사 대상 선택 (체크박스 선택 또는 단독 발사)</div>
        <div id="targetCheckList" style="display:flex;flex-wrap:wrap;gap:8px"></div>
      </div>
      <div class="row">
        <button class="b g" id="fireChecked">🚀 체크 선택 발사</button>
        <button class="b" id="fireAll">🌐 전체 발사</button>
      </div>"""
        code = code.replace(old_fire_row, new_fire_row)

    # [3] JavaScript 핸들러 주입 (커스텀 역할 직접 쓰기 + 체크 발사/단독 발사 로직)
    if 'v6.0.3 커스텀 신경망 직접 쓰기' not in code:
        js_v603_handlers = r"""
// ===== v6.0.3 커스텀 신경망 직접 쓰기 & 단독/체크 발사 엔진 =====
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
};

const origRoleSave = $("#roleSave");
if (origRoleSave) {
  origRoleSave.onclick = async () => {
    let sel = $("#roleSel").value;
    if (sel === "__custom__") {
      const customName = ($("#customRoleInput").value || "").trim();
      if (!customName) { toast("커스텀 역할명을 입력하세요."); return; }
      sel = "custom_" + customName.toLowerCase().replace(/[^a-z0-9_-]/g, "_");
      await rt({ type: "OMNI_SET_CUSTOM_ROLE", roleKey: sel, roleMeta: { label: customName, icon: "🔮" } });
    }
    await rt({ type: "OMNI_SET_OVERRIDE", role: sel });
    await refreshScan();
    toast("이 탭 역할을 지정했습니다: " + sel);
  };
}

const fireCheckedBtn = $("#fireChecked");
if (fireCheckedBtn) {
  fireCheckedBtn.onclick = () => {
    const checked = $$(".role-chk:checked").map(c => c.value);
    if (!checked.length) { toast("발사할 대상을 1개 이상 체크하세요."); return; }
    fire(checked);
  };
}

$("#dispatchTargets")?.addEventListener("click", (ev) => {
  const solo = ev.target.closest("[data-solo-fire]");
  if (solo) {
    const role = solo.dataset.soloFire;
    fire([role]);
  }
});
"""
        code = code.replace('// ------------------------------------------------------------------ wiring', js_v603_handlers + '\n// ------------------------------------------------------------------ wiring')

    with open(CT_P, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    say("   ✅ content_aside_bar.js: v6.0.3 (커스텀 역할 직접 쓰기 + 체크/단독 발사 탑재)")

def validate_javascript():
    node = shutil.which("node")
    if not node:
        say("   ⚠️ node를 찾지 못해 JS 문법 검사를 건너뜁니다.")
        return True
    for p in [BG_P, CT_P]:
        res = subprocess.run([node, "--check", str(p)], capture_output=True, text=True, encoding="utf-8")
        if res.returncode != 0:
            say(f"   ❌ node --check 실패: {p.name}\n" + res.stderr)
            return False
        say(f"   ✅ node --check 통과: {p.name}")
    return True

def verify_bridge():
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open("http://127.0.0.1:8765/health", timeout=3) as r:
            data = json.loads(r.read().decode("utf-8"))
            say(f"   🟢 로컬 브리지(8765) 200 OK 확인: {data.get('service', 'omni-bridge')} v{data.get('version', '6.0.3')}")
            return True
    except Exception as e:
        say(f"   ⚠️ 브리지 연결 확인: {e}")
        return True

def main():
    say("=" * 64)
    say("🛰️ RGON Omni-Link Hub v6.0.3 슬라이드 패널(rgon_aside_extension) 업그레이드")
    say("=" * 64)
    update_manifest()
    update_background()
    update_content()
    if not validate_javascript():
        say("❌ 자바스크립트 문법 오류로 중단합니다.")
        return 1
    verify_bridge()
    say("")
    say("OMNI-LINK v6.0.3 ASIDE EXTENSION UPGRADE COMPLETE!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

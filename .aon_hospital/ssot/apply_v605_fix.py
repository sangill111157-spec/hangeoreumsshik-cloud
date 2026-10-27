#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
apply_v605_fix.py
RGON Omni-Link Hub v6.0.5 업그레이드
1) [⚡ 작업 분배] 발사 대상 체크박스 자동 되살아남 버그 완치
   - state.targetChecked 메모리 및 chrome.storage.local (omni_target_checked) 연동
   - refreshScan 시 무조건 checked 금지 -> 저장된 값 복원 및 DOM 불필요 재렌더링 방지
   - 기본값: claude/gpt 만 true, grok/커스텀 신경망은 false
   - [☑️ 전체 선택] / [☐ 전체 해제] 버튼 탑재
2) manifest.json, background.js, content_aside_bar.js v6.0.5 갱신
3) node --check 문법 검증
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
EXT = ROOT / "rgon_aside_extension"
MANIFEST_P = EXT / "manifest.json"
BG_P = EXT / "background.js"
CT_P = EXT / "content_aside_bar.js"
VERSION = "6.0.5"

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
    code = code.replace("Omni-Link Hub v6.0.4", f"Omni-Link Hub v{VERSION}")
    code = code.replace("Omni-Link Hub v6.0.3", f"Omni-Link Hub v{VERSION}")
    code = code.replace("Omni-Link Hub v6.0.2", f"Omni-Link Hub v{VERSION}")

    # state에 targetChecked 초기화
    if "targetChecked:" not in code:
        code = code.replace(
            "const state = {",
            "const state = { targetChecked: { claude: true, gpt: true, grok: false }, _lastTgtKey: '',"
        )

    # HTML: [☑️ 전체 선택] / [☐ 전체 해제] 버튼 탑재
    old_tgt_header = r'<div style="font-size:11.5px;font-weight:700;margin-bottom:6px;color:#b9c0ff">🎯 발사 대상 선택 (체크박스 선택 또는 단독 발사)</div>'
    new_tgt_header = r"""<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <div style="font-size:11.5px;font-weight:700;color:#b9c0ff">🎯 발사 대상 선택 (체크박스 선택 또는 단독 발사)</div>
        <div style="display:flex;gap:4px">
          <button class="b sm" id="btnSelectAll" style="padding:2px 6px;font-size:11px" type="button">☑️ 전체 선택</button>
          <button class="b sm" id="btnUnselectAll" style="padding:2px 6px;font-size:11px" type="button">☐ 전체 해제</button>
        </div>
      </div>"""
    if old_tgt_header in code:
        code = code.replace(old_tgt_header, new_tgt_header)

    # renderDispatchTargets 개편: 저장된 상태 유지 및 DOM 재사용
    render_dispatch_v605 = r"""async function renderDispatchTargets(customs) {
  const tList = $("#targetCheckList");
  if (!tList) return;
  const scan = state.scan || { list: [] };
  const allRoles = Object.assign({}, ROLE_META, customs || {});
  const activeRoles = ROLE_ORDER.concat(Object.keys(customs || {}).filter(k => !ROLE_ORDER.includes(k)))
    .filter(role => role !== "rgon" && role !== "sheets" && role !== "adobe");

  // 역할 구성 키 비교
  const currentKey = activeRoles.join("|");
  const existingInputs = [...tList.querySelectorAll(".role-chk")];

  if (existingInputs.length === activeRoles.length && state._lastTgtKey === currentKey) {
    // DOM이 이미 존재하면 innerHTML을 덮어쓰지 않고 checked 상태만 동기화
    for (const inp of existingInputs) {
      const r = inp.value;
      if (state.targetChecked[r] !== undefined) {
        inp.checked = !!state.targetChecked[r];
      }
    }
    return;
  }
  state._lastTgtKey = currentKey;

  let html = "";
  for (const role of activeRoles) {
    const m = allRoles[role] || { label: role, icon: "⚡" };
    const tabs = (scan.list || []).filter(t => t.role === role);
    const hasTab = tabs.length > 0;
    
    // 저장된 설정 복원: 없으면 기본값 (claude, gpt만 true, grok/커스텀은 false)
    let isChecked = false;
    if (state.targetChecked && state.targetChecked[role] !== undefined) {
      isChecked = !!state.targetChecked[role];
    } else {
      isChecked = (role === "claude" || role === "gpt");
      state.targetChecked[role] = isChecked;
    }

    html += `<div style="display:inline-flex;align-items:center;gap:4px;padding:4px 8px;border-radius:8px;background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,${hasTab ? ".2" : ".05"})">
      <label style="cursor:pointer;display:inline-flex;align-items:center;gap:3px;font-size:12px">
        <input type="checkbox" class="role-chk" value="${esc(role)}" ${isChecked ? "checked" : ""}>
        <span>${m.icon || "🔮"} ${esc(m.label)}</span>
      </label>
      <button class="b sm" data-solo-fire="${esc(role)}" style="padding:2px 6px;font-size:11px" type="button" title="이 대상에만 단독 발사">🚀</button>
    </div>`;
  }
  tList.innerHTML = html || "<small style='opacity:.6'>발사 가능한 대상이 없습니다.</small>";
}"""

    code = re.sub(r'function renderDispatchTargets\(.*?\n\}\n(?=function renderStudioCustomLinks)', render_dispatch_v605 + '\n\n', code, flags=re.S)

    # 체크박스 변경 및 전체선택/해제 핸들러 탑재
    dispatch_handlers_v605 = r"""// ===== v6.0.5 발사 대상 체크박스 영구 기억 및 전체선택/해제 핸들러 =====
try {
  chrome.storage.local.get("omni_target_checked").then(o => {
    if (o && o.omni_target_checked) {
      state.targetChecked = Object.assign({ claude: true, gpt: true, grok: false }, o.omni_target_checked);
    }
  }).catch(() => {});
} catch (_) {}

$("#dispatchTargets")?.addEventListener("change", (ev) => {
  const chk = ev.target.closest(".role-chk");
  if (!chk) return;
  state.targetChecked[chk.value] = chk.checked;
  try {
    chrome.storage.local.set({ omni_target_checked: state.targetChecked });
  } catch (_) {}
});

$("#btnSelectAll")?.addEventListener("click", () => {
  $$(".role-chk").forEach(c => {
    c.checked = true;
    state.targetChecked[c.value] = true;
  });
  try { chrome.storage.local.set({ omni_target_checked: state.targetChecked }); } catch (_) {}
  toast("☑️ 전체 대상 선택 완료");
});

$("#btnUnselectAll")?.addEventListener("click", () => {
  $$(".role-chk").forEach(c => {
    c.checked = false;
    state.targetChecked[c.value] = false;
  });
  try { chrome.storage.local.set({ omni_target_checked: state.targetChecked }); } catch (_) {}
  toast("☐ 전체 대상 해제 완료");
});
"""

    if "v6.0.5 발사 대상 체크박스 영구 기억" not in code:
        code = code.replace(
            '// ------------------------------------------------------------------ wiring',
            dispatch_handlers_v605 + '\n\n// ------------------------------------------------------------------ wiring'
        )

    with open(CT_P, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    say(f"   ✅ content_aside_bar.js: v{VERSION} (체크박스 자동 되살아남 버그 완치 + 전체선택/해제 탑재)")

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
    say(f"🛰️ RGON Omni-Link Hub v{VERSION} 체크박스 영구 기억 패치 시작")
    say("=" * 64)
    update_manifest()
    update_background()
    update_content()
    if not check_js_syntax():
        say("❌ 자바스크립트 문법 검사 실패")
        return 1
    say("")
    say(f"OMNI-LINK v{VERSION} CHECKBOX PERSISTENCE & AUTO-REVIVAL BUG FIXED!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

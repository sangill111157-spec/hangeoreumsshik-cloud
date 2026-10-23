#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step9_pinpoint_fix_bar3.py
기존에 잘 작동하는 상단 7버튼/5버튼 및 2번·1번·0번 바는 100% 그대로 유지하고,
깜빡임을 일으킨 STEP8만 제거한 뒤 '3번 바(르곤-알파 실시간 브리핑 전문)'만
충돌 없는 독립 브리핑 바로 깔끔하게 개통합니다.
"""
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:/Users/sangi/Downloads/shin-agent")
if not ROOT.is_dir():
    ROOT = Path.cwd()

TARGETS = [
    "rgon_alpha_chat.html",
    "dashboard/rgon_alpha_chat.html",
    "docs/rgon_alpha_chat.html",
    "rgon_alpha_audience.html",
]

STEP8_RE = re.compile(r"<!--\s*STEP8_BEGIN\s*-->.*?<!--\s*STEP8_END\s*-->\s*", re.S)
FIX3_START = "<!-- === [RGON-BAR3-STABLE-START] === -->"
FIX3_END = "<!-- === [RGON-BAR3-STABLE-END] === -->"
FIX3_RE = re.compile(re.escape(FIX3_START) + r".*?" + re.escape(FIX3_END) + r"\s*", re.S)

INJECT_CODE = """<!-- === [RGON-BAR3-STABLE-START] === -->
<style id="rgon-bar3-stable-style">
  /* 기존에 깜빡이던 구형 3번 details는 숨기고, 똑같은 디자인의 무충돌 새 3번 바를 표시 */
  details.s7-bar[data-s7="3"]:not(#rgon-stable-bar3) {
    display: none !important;
  }
  /* 상단 잔여 1번/2번 중복 탭 및 하단 빈 원형 잔여물 숨김 */
  .rgons6-tabs, #rgons6-tabs, [data-rgons6-tabs] {
    display: none !important;
  }
  #rgon-stable-bar3 {
    margin: 8px 0;
    border: 1.5px solid #10b981;
    border-radius: 12px;
    background: rgba(6, 38, 28, 0.92);
    color: #ecfdf5;
    overflow: hidden;
  }
  #rgon-stable-bar3 > summary {
    list-style: none;
    cursor: pointer;
    padding: 13px 16px;
    font-size: 14px;
    font-weight: 800;
    color: #d1fae5;
    display: flex;
    align-items: center;
    gap: 8px;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
  }
  #rgon-stable-bar3 > summary::-webkit-details-marker { display: none; }
  #rgon-stable-bar3 > summary::before {
    content: "▶";
    font-size: 12px;
    color: #34d399;
    transition: transform 0.15s ease;
  }
  #rgon-stable-bar3[open] > summary::before {
    content: "▼";
  }
  #rgon-stable-bar3[open] > summary {
    border-bottom: 1px solid rgba(16, 185, 129, 0.35);
    background: rgba(4, 47, 34, 0.98);
  }
  #rgon-stable-bar3-body {
    padding: 12px 14px;
    max-height: 68dvh;
    overflow-y: auto;
    font-size: 13px;
    line-height: 1.6;
    background: rgba(9, 20, 28, 0.96);
    color: #e2e8f0;
  }
  #rgon-stable-bar3-tools {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 10px;
  }
  #rgon-stable-bar3-tools button {
    padding: 6px 11px;
    border-radius: 8px;
    border: 1px solid rgba(52, 211, 153, 0.45);
    background: rgba(16, 185, 129, 0.18);
    color: #ecfdf5;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
  }
  #rgon-stable-bar3-pre {
    white-space: pre-wrap;
    word-break: break-word;
    margin: 0;
    font-family: inherit;
  }
</style>
<script id="rgon-bar3-stable-script">
(function(){
  "use strict";
  if (window.__rgonStableBar3Loaded) return;
  window.__rgonStableBar3Loaded = true;

  function fetchJson(url) {
    return fetch(url + "?t=" + Date.now(), {cache: "no-store"})
      .then(function(r){ return r.ok ? r.json() : null; })
      .catch(function(){ return null; });
  }

  function formatBriefing(snap, evo, fallbackText) {
    var lines = [];
    lines.push("🛰️ [르곤-알파 실시간 브리핑 전문]");
    lines.push("━━━━━━━━━━━━━━━━━━━━━━");
    lines.push("🕒 조회 시각: " + new Date().toLocaleString("ko-KR"));
    if (snap && typeof snap === "object") {
      if (snap.updated_at || snap.timestamp || snap.last_sync) {
        lines.push("🔄 최신 동기화: " + (snap.updated_at || snap.timestamp || snap.last_sync));
      }
      if (snap.version || snap.brain_version) {
        lines.push("🧠 두뇌 버전: " + (snap.version || snap.brain_version));
      }
      if (snap.pulse_count !== undefined) {
        lines.push("💓 누적 박동 수: #" + snap.pulse_count);
      }
      lines.push("\n📊 [핵심 스냅샷 현황]");
      Object.keys(snap).slice(0, 18).forEach(function(k){
        var v = snap[k];
        if (v !== null && typeof v === "object") {
          lines.push("• " + k + ": " + JSON.stringify(v).slice(0, 180));
        } else {
          lines.push("• " + k + ": " + String(v));
        }
      });
    }
    if (evo && typeof evo === "object") {
      lines.push("\n🧬 [자율진화 & 항체 기억]");
      Object.keys(evo).slice(0, 12).forEach(function(k){
        var v = evo[k];
        if (Array.isArray(v)) {
          lines.push("• " + k + " (" + v.length + "건): " + JSON.stringify(v[v.length - 1] || "").slice(0, 180));
        } else if (v !== null && typeof v === "object") {
          lines.push("• " + k + ": " + JSON.stringify(v).slice(0, 180));
        } else {
          lines.push("• " + k + ": " + String(v));
        }
      });
    }
    if (fallbackText && fallbackText.length > 20) {
      lines.push("\n📋 [본체 브리핑 원문]");
      lines.push(fallbackText);
    }
    return lines.join("\n");
  }

  function loadStableBriefing() {
    var pre = document.getElementById("rgon-stable-bar3-pre");
    if (!pre) return;
    var oldBar3 = document.querySelector('details.s7-bar[data-s7="3"]:not(#rgon-stable-bar3)');
    var fbText = "";
    if (oldBar3) {
      var clone = oldBar3.cloneNode(true);
      var s = clone.querySelector("summary");
      if (s) s.remove();
      fbText = (clone.innerText || clone.textContent || "").trim();
    }
    pre.textContent = "⏳ 실시간 브리핑 데이터를 불러오는 중입니다...";
    Promise.all([
      fetchJson("./rgon_brain_snapshot.json"),
      fetchJson("./evolution_memory.json")
    ]).then(function(res){
      pre.textContent = formatBriefing(res[0], res[1], fbText);
    });
  }

  function mountStableBar3() {
    if (document.getElementById("rgon-stable-bar3")) return;
    var oldBar3 = document.querySelector('details.s7-bar[data-s7="3"]');
    var bar2 = document.querySelector('details.s7-bar[data-s7="2"]');
    var anchor = oldBar3 || bar2;
    if (!anchor || !anchor.parentNode) return;

    var det = document.createElement("details");
    det.id = "rgon-stable-bar3";
    det.innerHTML =
      '<summary>🛰️ 르곤-알파 실시간 브리핑 전문 (자동)</summary>' +
      '<div id="rgon-stable-bar3-body">' +
        '<div id="rgon-stable-bar3-tools">' +
          '<button type="button" id="rgon-sb3-refresh">🔄 새로고침</button>' +
          '<button type="button" id="rgon-sb3-copy">📋 전문 복사</button>' +
          '<button type="button" id="rgon-sb3-tts">🔊 음성 듣기/정지</button>' +
        '</div>' +
        '<pre id="rgon-stable-bar3-pre">바를 열면 실시간 브리핑이 표시됩니다.</pre>' +
      '</div>';

    anchor.parentNode.insertBefore(det, anchor);

    det.addEventListener("toggle", function(){
      if (det.open) {
        /* 3번 바가 열리면 나머지 2, 1, 0번 바는 자동으로 닫아 화면 겹침 방지 */
        document.querySelectorAll('details.s7-bar[data-s7="2"], details.s7-bar[data-s7="1"], details.s7-bar[data-s7="0"]').forEach(function(other){
          other.open = false;
          other.removeAttribute("open");
        });
        loadStableBriefing();
      }
    });

    /* 다른 바(2, 1, 0)를 열면 이 3번 바도 자동으로 닫히게 연동 */
    document.querySelectorAll('details.s7-bar[data-s7="2"], details.s7-bar[data-s7="1"], details.s7-bar[data-s7="0"]').forEach(function(other){
      other.addEventListener("toggle", function(){
        if (other.open && det.open) {
          det.open = false;
        }
      });
    });

    /* 상단 갈색 [📋 브리핑] 버튼을 누르면 이 3번 바가 즉시 열리도록 연결 */
    document.addEventListener("click", function(e){
      var btn = e.target && e.target.closest ? e.target.closest("button") : null;
      if (!btn) return;
      var txt = (btn.textContent || "").trim();
      if (txt === "📋 브리핑" || btn.getAttribute("data-rgons4-act") === "brief") {
        e.preventDefault();
        e.stopPropagation();
        det.open = !det.open;
        if (det.open) loadStableBriefing();
      }
    }, true);

    document.getElementById("rgon-sb3-refresh").addEventListener("click", function(){
      loadStableBriefing();
    });
    document.getElementById("rgon-sb3-copy").addEventListener("click", function(){
      var t = document.getElementById("rgon-stable-bar3-pre").textContent || "";
      if (navigator.clipboard) navigator.clipboard.writeText(t);
    });
    document.getElementById("rgon-sb3-tts").addEventListener("click", function(){
      if (!window.speechSynthesis) return;
      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        return;
      }
      var t = document.getElementById("rgon-stable-bar3-pre").textContent || "";
      var u = new SpeechSynthesisUtterance(t.slice(0, 1500));
      u.lang = "ko-KR";
      window.speechSynthesis.speak(u);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function(){ setTimeout(mountStableBar3, 150); });
  } else {
    setTimeout(mountStableBar3, 150);
  }
})();
</script>
<!-- === [RGON-BAR3-STABLE-END] === -->
"""

def main():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"■ [핀셋 수리] 기존 2·1·0번 바 완벽 보존 + 3번 브리핑 바 깜빡임 제거 시작 (루트: {ROOT})")
    patched = 0
    for rel in TARGETS:
        p = ROOT / rel
        if not p.is_file():
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        bak = p.with_name(f"{p.name}.bak_{stamp}")
        shutil.copy2(p, bak)

        cleaned = STEP8_RE.sub("", raw)
        cleaned = FIX3_RE.sub("", cleaned)

        if "</body>" in cleaned:
            idx = cleaned.rfind("</body>")
            updated = cleaned[:idx] + "\n" + INJECT_CODE + "\n" + cleaned[idx:]
        else:
            updated = cleaned + "\n" + INJECT_CODE

        p.write_text(updated, encoding="utf-8")
        print(f"  ✔ 패치 완료: {rel}")
        patched += 1

    if patched:
        subprocess.run(["git", "add", "-A"], cwd=str(ROOT), check=False)
        subprocess.run(["git", "commit", "-m", "fix(ui): replace flickering bar3 with stable independent briefing bar"], cwd=str(ROOT), check=False)
        subprocess.run(["git", "pull", "--rebase", "-X", "ours", "origin", "main"], cwd=str(ROOT), check=False)
        r = subprocess.run(["git", "push", "origin", "main"], cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode == 0:
            print("☁️ [GitHub 클라우드 푸시 100% 완료!]")
        else:
            print("⚠️ Git push 결과:", r.stdout, r.stderr)

if __name__ == "__main__":
    sys.exit(main())

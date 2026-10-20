# -*- coding: utf-8 -*-
"""
patch_v360_signal_sync.py
--------------------------------------------------------------------------------
1. 대시보드 상단에 『⚡ IN/OUT 시그널 오토싱크 사령탑』 미니 바 탑재
2. 르곤이 시그널 수동 캐치, Genspark 센서 장착 가이드, OUT 복사 기능 장착
3. 실시간 무인 동기화 루프 및 성우 음성 브리핑 연동
4. 캔버스 각도 배지 텍스트: "🔄 3D 360° 좌우·상하 터치 회전 (현재: 0° / 0°)"
5. 상하 스크롤 틸트 각도 범위: -30° ~ +30° 정밀 조정
--------------------------------------------------------------------------------
"""

import sys
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

SYNC_HUD_BAR = """
  <!-- ⚡ [르곤-안실장 양방향 시그널 오토싱크 사령탑 미니 바] -->
  <div id="rgon-signal-sync-bar" class="w-full bg-slate-900/95 backdrop-blur-md border-b border-purple-500/30 px-3 py-1.5 flex flex-wrap items-center justify-between gap-2 text-xs shadow-lg z-20 sticky top-0">
    <div class="flex items-center gap-2">
      <span class="flex h-2 w-2 relative">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
      </span>
      <span class="font-bold text-amber-300 flex items-center gap-1 text-[11px] sm:text-xs">
        <span>⚡</span><span>IN/OUT 오토싱크</span>
      </span>
      <span id="sync-status-badge" class="px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 text-[10px] font-medium">
        🟢 Auto-Catch 대기 중
      </span>
    </div>

    <div class="flex items-center gap-1.5 text-[11px]">
      <button type="button" onclick="manualCatchRgonSignal()" class="px-2.5 py-1 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold transition flex items-center gap-1 shadow-sm active:scale-95">
        <span>⚡</span><span>시그널 수동 캐치</span>
      </button>
      <button type="button" onclick="openSensorGuideModal()" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium transition flex items-center gap-1 active:scale-95">
        <span>🔗</span><span class="hidden sm:inline">Genspark</span><span>센서 장착</span>
      </button>
      <button type="button" onclick="copyLatestOutReport()" class="px-2.5 py-1 rounded-lg bg-pink-600/30 hover:bg-pink-600/50 text-pink-300 border border-pink-500/40 font-medium transition flex items-center gap-1 active:scale-95">
        <span>📋</span><span>OUT 복사</span>
      </button>
    </div>
  </div>

  <!-- Genspark 센서 장착 가이드 모달 -->
  <div id="sensor-guide-modal" class="hidden fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-slate-900 border border-purple-500/40 rounded-2xl p-5 shadow-2xl space-y-4 text-xs text-slate-300">
      <div class="flex items-center justify-between border-b border-slate-800 pb-2">
        <h3 class="text-sm font-bold text-amber-300 flex items-center gap-2">
          <span>⚡</span><span>Genspark 르곤이 무인 자동캐치 센서 설치</span>
        </h3>
        <button type="button" onclick="closeSensorGuideModal()" class="text-slate-400 hover:text-white text-base">✕</button>
      </div>
      <div class="space-y-2">
        <p class="text-slate-200 font-semibold">1. 크롬 북마클릿 (1초 원클릭):</p>
        <p class="text-[11px] text-slate-400">아래 코드를 복사하여 브라우저 북마크 URL에 저장하면, Genspark에서 클릭 한 번으로 시그널이 안실장에게 즉시 전송됩니다.</p>
        <div class="flex gap-1.5">
          <input id="bookmarklet-code-input" readonly value="javascript:(function(){const s='⟪⚡RGON_SIGNAL_READY⚡⟫';const t=document.body.innerText||'';if(!t.includes(s)){alert('르곤이 시그널 미발견');return;}fetch('http://127.0.0.1:8501/api/signal-sync-in',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({signal:s,prompt:t.substring(Math.max(0,t.lastIndexOf(s)-4500)),sender:'Genspark-Bookmarklet'})}).then(r=>r.json()).then(d=>alert('⚡ 안실장에게 0.01초 자동 전송 완료!'));})();" class="w-full px-2 py-1.5 rounded bg-slate-950 border border-slate-700 text-slate-300 text-[10px] select-all font-mono">
          <button type="button" onclick="copyBookmarkletCode()" class="px-3 py-1 bg-purple-600 hover:bg-purple-500 text-white rounded font-bold whitespace-nowrap">복사</button>
        </div>

        <p class="text-slate-200 font-semibold pt-2">2. Tampermonkey 유저스크립트 (0초 무인):</p>
        <p class="text-[11px] text-slate-400">Genspark 창에 상주하며 르곤이가 답변을 끝마치자마자 0초 만에 안실장 로컬 큐로 자동 전송합니다.</p>
        <a href="/rgon_tampermonkey_script.user.js" target="_blank" class="inline-block px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-center w-full transition">
          📥 유저스크립트 다운로드 및 설치
        </a>
      </div>
      <div class="pt-2 border-t border-slate-800 flex justify-end">
        <button type="button" onclick="closeSensorGuideModal()" class="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium">닫기</button>
      </div>
    </div>
  </div>
"""

SIGNAL_JS_LOGIC = """
// ============================================================================
// ⚡ [르곤-안실장 무인 동기화 & 실시간 시그널 클라이언트 엔진]
// ============================================================================

window.lastSyncedVersion = window.lastSyncedVersion || 'v3.6-pro';
window.lastOutTimestamp = window.lastOutTimestamp || '';

// 1. 르곤이 시그널 수동 캐치
async function manualCatchRgonSignal() {
  try {
    let text = '';
    if (navigator.clipboard && navigator.clipboard.readText) {
      text = await navigator.clipboard.readText();
    }
    if (!text || !text.includes('⟪⚡RGON_SIGNAL_READY⚡⟫')) {
      text = prompt('📋 르곤이(제미나이 4 아르곤)의 명령서 전문 또는 시그널을 붙여넣어 주세요:', text);
    }
    if (!text) return;

    const res = await fetch('/api/signal-sync-in', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        signal: '⟪⚡RGON_SIGNAL_READY⚡⟫',
        prompt: text,
        sender: '이상일 대표님 (수동 캐치)',
        timestamp: new Date().toISOString()
      })
    });
    const data = await res.json();
    if (data.status === 'ok') {
      const badge = document.getElementById('sync-status-badge');
      if (badge) {
        badge.innerHTML = '⚡ 르곤이 시그널 주입 완료!';
        badge.className = 'px-2 py-0.5 rounded-full bg-purple-950/80 text-purple-300 border border-purple-500/40 text-[10px] font-medium animate-bounce';
      }
      if (typeof showToast === 'function') {
        showToast('⚡ [르곤-안실장 동기화]: 르곤이 시그널이 안실장 작업 큐에 0.01초 만에 자동 주입되었습니다!', 'success');
      }
      if (typeof speakMainText === 'function') {
        speakMainText('르곤이의 과업 지시서가 안실장 작업 큐에 정상적으로 주입되었습니다.');
      }
    }
  } catch (err) {
    if (typeof showToast === 'function') {
      showToast('⚠️ 시그널 수동 캐치 중 오류가 발생했습니다: ' + err.message, 'error');
    }
  }
}

// 2. 센서 가이드 모달
function openSensorGuideModal() {
  const modal = document.getElementById('sensor-guide-modal');
  if (modal) modal.classList.remove('hidden');
}

function closeSensorGuideModal() {
  const modal = document.getElementById('sensor-guide-modal');
  if (modal) modal.classList.add('hidden');
}

function copyBookmarkletCode() {
  const input = document.getElementById('bookmarklet-code-input');
  if (input) {
    input.select();
    navigator.clipboard.writeText(input.value);
    if (typeof showToast === 'function') {
      showToast('📋 북마클릿 코드가 클립보드에 복사되었습니다! 브라우저 즐겨찾기에 등록해 주세요.', 'info');
    }
  }
}

// 3. 르곤이 보고용 최신 OUT 결과 클립보드 복사
async function copyLatestOutReport() {
  try {
    const res = await fetch('/api/signal-sync-out');
    const data = await res.json();
    const out = data.last_out_signal || {};
    const reportText = `[안실장 완수 보고]
- 버전: ${out.version || 'v3.6-pro'}
- 시그널: ⟪✅ANTIGRAVITY_OUT_COMPLETE✅⟫
- 요약: ${out.summary || '3D 360도 회전, 얼굴 실사 합성 및 IN/OUT 동기화 완료'}
- 동기화 시각: ${out.timestamp || new Date().toISOString()}`;

    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(reportText);
    }
    if (typeof showToast === 'function') {
      showToast('📋 르곤이 보고용 최신 OUT 시그널 리포트가 클립보드에 복사되었습니다!', 'success');
    }
  } catch (e) {
    if (typeof showToast === 'function') {
      showToast('⚠️ OUT 리포트 복사 실패: ' + e.message, 'error');
    }
  }
}

// 4. 실시간 무인 백그라운드 동기화 루프 (2초 폴링)
function initSignalSyncLoop() {
  setInterval(async () => {
    try {
      const res = await fetch('/api/signal-sync-out');
      if (!res.ok) return;
      const data = await res.json();
      const out = data.last_out_signal;
      if (!out || !out.timestamp) return;

      if (window.lastOutTimestamp && window.lastOutTimestamp !== out.timestamp) {
        window.lastOutTimestamp = out.timestamp;
        const badge = document.getElementById('sync-status-badge');
        if (badge) {
          badge.innerHTML = '🎉 동기화 완료 (' + (out.version || 'v3.6-pro') + ')';
          badge.className = 'px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 text-[10px] font-medium';
        }
        if (typeof showToast === 'function') {
          showToast('🎉 [무인 동기화]: ' + (out.summary || '새로운 패치가 무인 동기화되었습니다!'), 'success');
        }
        if (typeof speakMainText === 'function') {
          speakMainText('대표님! 지시하신 IN/OUT 자동 동기화 및 패치가 완료되었습니다!');
        }
      } else if (!window.lastOutTimestamp) {
        window.lastOutTimestamp = out.timestamp;
      }
    } catch (e) {
      // 무시 (오프라인 상태)
    }
  }, 2500);
}

// 페이지 로드 시 동기화 루프 가동
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSignalSyncLoop);
} else {
  initSignalSyncLoop();
}
"""

def patch_index_html():
    print("[🛠️ index.html 시그널 미니 바 및 3D 배지 업데이트 시작]")
    with open("dashboard/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. 상단 미니 바 주입 (중복 방지)
    if "rgon-signal-sync-bar" not in html:
        # 상단 네비 바 바로 뒤에 삽입
        idx_nav_close = html.find("</nav>")
        if idx_nav_close != -1:
            html = html[:idx_nav_close+6] + "\n" + SYNC_HUD_BAR + "\n" + html[idx_nav_close+6:]
            print("  ✅ index.html에 SYNC_HUD_BAR 주입 완료!")
        else:
            # body 시작 바로 뒤에 삽입
            idx_body = html.find("<body")
            idx_body_close = html.find(">", idx_body) + 1
            html = html[:idx_body_close] + "\n" + SYNC_HUD_BAR + "\n" + html[idx_body_close:]
            print("  ✅ index.html body 상단에 SYNC_HUD_BAR 주입 완료!")

    # 2. 캔버스 각도 배지 텍스트를 대표님 요청 포맷으로 정확히 동기화:
    # "🔄 3D 360° 좌우·상하 터치 회전 (현재: 0° / 0°)"
    html = re.sub(
        r'badge\.innerHTML = `.*?\(터치로 360° 회전\)?;?`',
        r'badge.innerHTML = `🔄 3D 360° 좌우·상하 터치 회전 (현재: ${yaw}° / ${pitch >= 0 ? "+" : ""}${pitch}°)`;',
        html
    )
    # 상하 틸트 범위를 -30° ~ +30°로 확장
    html = html.replace(
        "window.pitchTilt = Math.max(-25, Math.min(25, window.pitchTilt - deltaY * 0.35));",
        "window.pitchTilt = Math.max(-30, Math.min(30, window.pitchTilt - deltaY * 0.4));"
    )

    # 3. SIGNAL_JS_LOGIC 주입
    if "⚡ [르곤-안실장 무인 동기화 & 실시간 시그널 클라이언트 엔진]" not in html:
        idx_script_end = html.rfind("</script>")
        if idx_script_end != -1:
            html = html[:idx_script_end] + "\n\n" + SIGNAL_JS_LOGIC + "\n" + html[idx_script_end:]
            print("  ✅ index.html에 SIGNAL_JS_LOGIC 주입 완료!")

    with open("dashboard/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  ✅ dashboard/index.html 저장 완료!")

def patch_dream_closet_app():
    print("[🛠️ dream_closet_future_master_app.html 시그널 미니 바 및 3D 배지 업데이트 시작]")
    with open("dashboard/dream_closet_future_master_app.html", "r", encoding="utf-8") as f:
        html = f.read()

    if "rgon-signal-sync-bar" not in html:
        idx_body = html.find("<body")
        idx_body_close = html.find(">", idx_body) + 1
        html = html[:idx_body_close] + "\n" + SYNC_HUD_BAR + "\n" + html[idx_body_close:]
        print("  ✅ dream_closet에 SYNC_HUD_BAR 주입 완료!")

    html = re.sub(
        r'badge\.innerHTML = `.*?\(터치로 360° 회전\)?;?`',
        r'badge.innerHTML = `🔄 3D 360° 좌우·상하 터치 회전 (현재: ${yaw}° / ${pitch >= 0 ? "+" : ""}${pitch}°)`;',
        html
    )
    html = html.replace(
        "window.pitchTilt = Math.max(-25, Math.min(25, window.pitchTilt - deltaY * 0.35));",
        "window.pitchTilt = Math.max(-30, Math.min(30, window.pitchTilt - deltaY * 0.4));"
    )

    if "⚡ [르곤-안실장 무인 동기화 & 실시간 시그널 클라이언트 엔진]" not in html:
        idx_script_end = html.rfind("</script>")
        if idx_script_end != -1:
            html = html[:idx_script_end] + "\n\n" + SIGNAL_JS_LOGIC + "\n" + html[idx_script_end:]
            print("  ✅ dream_closet에 SIGNAL_JS_LOGIC 주입 완료!")

    with open("dashboard/dream_closet_future_master_app.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  ✅ dashboard/dream_closet_future_master_app.html 저장 완료!")

def main():
    patch_index_html()
    patch_dream_closet_app()
    print("🎉 프론트엔드 시그널 오토싱크 사령탑 주입 완료!")

if __name__ == "__main__":
    main()

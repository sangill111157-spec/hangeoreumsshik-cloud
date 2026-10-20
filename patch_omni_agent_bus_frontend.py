# -*- coding: utf-8 -*-
"""
patch_omni_agent_bus_frontend.py
--------------------------------------------------------------------------------
dashboard/index.html 및 dashboard/dream_closet_future_master_app.html에
1. 👑 이상일 대표님 전용 통합 명령 하달창 (Master Command Console)
2. 📺 실시간 AI 교신 라이브 모니터 (Live Inter-Agent Feed)
3. ➕ 신규 AI 고유번호 발급 모달
4. 캔버스 하단 배지 텍스트: "🔄 3D 360° 터치 회전 (좌우: 0° · 상하: 0°)"
--------------------------------------------------------------------------------
"""

import sys
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

OMNI_BUS_UI_MARKUP = """
    <!-- 🌐 [만능 멀티-AI 실시간 교신 관제탑: Master Inter-Agent Mission Console] -->
    <div id="omni-agent-bus-panel" class="w-full rounded-2xl bg-slate-900/90 backdrop-blur-xl border border-purple-500/40 p-3 sm:p-5 shadow-2xl space-y-4 mb-6">
      
      <!-- 상단 헤더: 사령관 명패 및 AI 레지스트리 상태 바 -->
      <div class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div class="flex items-center gap-2">
          <span class="p-2 rounded-xl bg-gradient-to-tr from-amber-500 to-purple-600 text-white shadow-lg text-lg">👑</span>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-sm sm:text-base font-extrabold text-white tracking-tight">
                만능 멀티-AI 실시간 교신 관제탑
              </h2>
              <span class="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold">
                COMMANDER-000 직속
              </span>
            </div>
            <p class="text-[11px] text-slate-400">
              이상일 대표님 ➔ 전 세계 AI (르곤이 1·2호, 안실장, ChatGPT, Claude, QA감사관) 실시간 지휘
            </p>
          </div>
        </div>

        <div class="flex items-center gap-1.5 text-xs">
          <button type="button" onclick="openNewAgentModal()" class="px-2.5 py-1.5 rounded-xl bg-purple-600/30 hover:bg-purple-600/50 text-purple-300 border border-purple-500/40 font-bold transition flex items-center gap-1 shadow-sm active:scale-95">
            <span>➕</span><span>새 AI 등록</span>
          </button>
          <button type="button" onclick="refreshOmniAgentBus()" class="px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 font-medium transition flex items-center gap-1 active:scale-95">
            <span>🔄</span><span>피드 새로고침</span>
          </button>
        </div>
      </div>

      <!-- 에이전트 고유번호 레지스트리 칩 (Active Agent Badges) -->
      <div id="omni-agent-registry-chips" class="flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px] no-scrollbar">
        <!-- JS로 동적 렌더링 -->
      </div>

      <!-- 👑 대표님 전용 통합 명령 하달창 (Master Command Console) -->
      <div class="rounded-xl bg-slate-950/80 border border-purple-500/30 p-3 sm:p-4 space-y-3">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="flex items-center gap-2">
            <span class="text-amber-400 font-bold text-xs flex items-center gap-1">
              <span>🎯</span><span>수신 에이전트:</span>
            </span>
            <select id="cmd-target-agent-select" class="bg-slate-900 border border-slate-700 text-slate-200 rounded-lg px-2.5 py-1 text-xs font-semibold focus:outline-none focus:border-purple-500">
              <option value="ALL">📡 전체 AI 동시 하달 (Broadcast ALL)</option>
              <option value="RGON-001">🧠 [RGON-001] 르곤이 1호 (Gemini 4 Argon 수석설계)</option>
              <option value="RGON-002">🧠 [RGON-002] 르곤이 2호 (Gemini 4 Argon 특임분신)</option>
              <option value="AGV-101" selected>🤖 [AGV-101] 안실장 (Antigravity 수석실행)</option>
              <option value="GPT-201">🌐 [GPT-201] ChatGPT (OpenAI 크리에이티브)</option>
              <option value="CLD-301">🎨 [CLD-301] Claude (정밀 아키텍처)</option>
              <option value="QA-901">🕵️‍♂️ [QA-901] QA 감사관 (독립 검수)</option>
            </select>
          </div>

          <div class="flex items-center gap-1 text-[11px]">
            <button type="button" onclick="manualCatchRgonSignal()" class="px-2.5 py-1 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/40 font-semibold transition flex items-center gap-1">
              <span>📋</span><span>르곤이 시그널 1초 캐치 (IN)</span>
            </button>
            <button type="button" onclick="copyLatestOutReport()" class="px-2.5 py-1 rounded-lg bg-pink-600/30 hover:bg-pink-600/50 text-pink-300 border border-pink-500/40 font-semibold transition flex items-center gap-1">
              <span>📋</span><span>안실장 OUT 복사</span>
            </button>
          </div>
        </div>

        <!-- 명령 텍스트 입력창 & 마이크 -->
        <div class="relative">
          <textarea id="cmd-broadcast-input" rows="2" placeholder="👑 [COMMANDER-000] 이상일 대표님의 마스터 명령을 입력하세요... (예: 르곤이 설계안 검토 후 안실장 배포 실행하라)" class="w-full px-3 py-2 pr-12 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-400 transition resize-none"></textarea>
          <button type="button" onclick="toggleOmniVoiceMic()" id="btn-omni-mic" class="absolute right-2 top-2 p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-amber-400 border border-slate-700 transition" title="음성 명령 입력">
            <span>🎙️</span>
          </button>
        </div>

        <div class="flex items-center justify-between gap-2">
          <span class="text-[10px] text-slate-500">
            ⚡ 하달 즉시 고유 메시지 ID 부여 및 NEXT_TASK_FOR_ANTIGRAVITY.md / 버스에 0.01초 자동 주입
          </span>
          <button type="button" onclick="dispatchCommanderOrder()" class="px-4 py-1.5 rounded-xl bg-gradient-to-r from-amber-500 via-purple-600 to-indigo-600 hover:from-amber-400 hover:to-indigo-500 text-white font-extrabold text-xs transition shadow-lg shadow-purple-500/20 flex items-center gap-1.5 active:scale-95">
            <span>🚀</span><span>명령 하달 (IN)</span>
          </button>
        </div>
      </div>

      <!-- 📺 실시간 AI 교신 라이브 모니터 (Live Inter-Agent Feed) -->
      <div class="space-y-2">
        <div class="flex items-center justify-between text-xs px-1">
          <div class="flex items-center gap-2 font-bold text-slate-300">
            <span class="flex h-2 w-2 relative">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>📡 실시간 AI 교신 라이브 피드</span>
            <span id="omni-msg-count-badge" class="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px]">4건</span>
          </div>
          <span class="text-[11px] text-slate-500">2초 무인 자동 갱신</span>
        </div>

        <div id="omni-inter-agent-feed-box" class="h-60 overflow-y-auto space-y-2 p-2.5 rounded-xl bg-slate-950/90 border border-slate-800/80 font-sans text-xs">
          <!-- 메시지 타임라인 렌더링 -->
        </div>
      </div>
    </div>

    <!-- ➕ 신규 AI 고유번호 발급 모달 -->
    <div id="register-agent-modal" class="hidden fixed inset-0 bg-slate-950/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-sm bg-slate-900 border border-purple-500/40 rounded-2xl p-5 shadow-2xl space-y-4 text-xs text-slate-200">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2">
          <h3 class="text-sm font-bold text-amber-300 flex items-center gap-1.5">
            <span>➕</span><span>신규 AI 에이전트 고유번호 발급</span>
          </h3>
          <button type="button" onclick="closeNewAgentModal()" class="text-slate-400 hover:text-white text-base">✕</button>
        </div>

        <div class="space-y-2.5">
          <div>
            <label class="block text-[11px] font-semibold text-slate-400 mb-1">고유번호 (Agent ID)</label>
            <input id="new-agent-id-input" placeholder="예: RGON-003, GPT-202" class="w-full px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-white font-mono uppercase">
          </div>
          <div>
            <label class="block text-[11px] font-semibold text-slate-400 mb-1">에이전트 이름</label>
            <input id="new-agent-name-input" placeholder="예: 르곤이 3호, Auto-Claude" class="w-full px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-white">
          </div>
          <div>
            <label class="block text-[11px] font-semibold text-slate-400 mb-1">담당 역할 / 임무</label>
            <input id="new-agent-role-input" placeholder="예: 글로벌 마케팅, 비전 분석" class="w-full px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-white">
          </div>
          <div class="flex gap-2">
            <div class="w-1/2">
              <label class="block text-[11px] font-semibold text-slate-400 mb-1">아이콘 이모지</label>
              <input id="new-agent-icon-input" value="🤖" class="w-full px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-white text-center">
            </div>
            <div class="w-1/2">
              <label class="block text-[11px] font-semibold text-slate-400 mb-1">대표 색상</label>
              <input id="new-agent-color-input" type="color" value="#8b5cf6" class="w-full h-8 rounded-lg bg-slate-950 border border-slate-700 cursor-pointer p-0.5">
            </div>
          </div>
        </div>

        <div class="pt-2 border-t border-slate-800 flex justify-end gap-2">
          <button type="button" onclick="closeNewAgentModal()" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 font-medium">취소</button>
          <button type="button" onclick="submitRegisterNewAgent()" class="px-4 py-1.5 bg-purple-600 hover:bg-purple-500 rounded-lg text-white font-bold">발급 등록</button>
        </div>
      </div>
    </div>
"""

OMNI_BUS_JS_LOGIC = """
// ============================================================================
// 🌐 [Omni Multi-AI Inter-Agent Bus: 실시간 다자간 AI 교신 엔진]
// ============================================================================

window.omniAgentsRegistry = [];
window.omniMessagesHistory = [];
window.lastRenderedMsgId = '';

// 1. 버스 데이터 동기화 & 렌더링
async function refreshOmniAgentBus() {
  try {
    const res = await fetch('/api/omni-agent-bus');
    if (!res.ok) return;
    const data = await res.json();
    window.omniAgentsRegistry = data.registry || [];
    window.omniMessagesHistory = data.messages || [];

    renderAgentRegistryChips();
    renderInterAgentFeed();
  } catch (err) {
    console.warn('⚠️ Omni Agent Bus fetch error:', err);
  }
}

// 2. 에이전트 칩 렌더링
function renderAgentRegistryChips() {
  const container = document.getElementById('omni-agent-registry-chips');
  if (!container) return;

  container.innerHTML = window.omniAgentsRegistry.map(a => `
    <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-slate-200 whitespace-nowrap shadow-sm">
      <span>${a.icon || '🤖'}</span>
      <strong style="color: ${a.color || '#38bdf8'}">${a.id}</strong>
      <span class="text-slate-400">(${a.name})</span>
    </span>
  `).join('');
}

// 3. 실시간 교신 피드 렌더링
function renderInterAgentFeed() {
  const box = document.getElementById('omni-inter-agent-feed-box');
  const countBadge = document.getElementById('omni-msg-count-badge');
  if (!box) return;

  if (countBadge) {
    countBadge.innerText = `${window.omniMessagesHistory.length}건`;
  }

  const msgs = window.omniMessagesHistory;
  if (!msgs || msgs.length === 0) {
    box.innerHTML = '<div class="text-slate-500 text-center py-6">교신 기록이 없습니다. 대표님 명령을 하달하세요.</div>';
    return;
  }

  box.innerHTML = msgs.map(m => {
    const isCommander = m.from === 'COMMANDER-000';
    const isSignalIn = m.type === 'SIGNAL_IN' || (m.content && m.content.includes('RGON_SIGNAL_READY'));
    const isSignalOut = m.type === 'SIGNAL_OUT' || (m.content && m.content.includes('ANTIGRAVITY_OUT_COMPLETE'));

    let borderCol = 'border-slate-800';
    let bgCol = 'bg-slate-900/60';
    if (isCommander) { borderCol = 'border-amber-500/40'; bgCol = 'bg-amber-950/20'; }
    if (isSignalIn) { borderCol = 'border-purple-500/40'; bgCol = 'bg-purple-950/20'; }
    if (isSignalOut) { borderCol = 'border-emerald-500/40'; bgCol = 'bg-emerald-950/20'; }

    return `
      <div class="p-2.5 rounded-lg border ${borderCol} ${bgCol} space-y-1 transition hover:bg-slate-900/80">
        <div class="flex items-center justify-between text-[11px]">
          <div class="flex items-center gap-1.5 flex-wrap">
            <span class="px-2 py-0.5 rounded font-mono font-bold bg-slate-800 text-amber-300">
              [${m.from}] ➔ [${m.to}]
            </span>
            <span class="text-slate-500 font-mono text-[10px]">${m.timestamp}</span>
            <span class="text-slate-600 text-[10px] font-mono">${m.msg_id}</span>
          </div>
          <button type="button" onclick="navigator.clipboard.writeText('${(m.content||'').replace(/'/g, "\\'")}'); showToast('📋 교신 내용이 복사되었습니다!', 'info');" class="text-slate-400 hover:text-white text-[10px]">
            복사
          </button>
        </div>
        <div class="text-slate-200 text-xs whitespace-pre-wrap leading-relaxed">${m.content}</div>
      </div>
    `;
  }).join('');

  // 스크롤 아래로
  box.scrollTop = box.scrollHeight;
}

// 4. 대표님 명령 하달 (IN)
async function dispatchCommanderOrder() {
  const input = document.getElementById('cmd-broadcast-input');
  const targetSelect = document.getElementById('cmd-target-agent-select');
  if (!input) return;

  const content = input.value.trim();
  if (!content) {
    if (typeof showToast === 'function') showToast('⚠️ 명령 내용을 입력해 주세요!', 'warning');
    return;
  }

  const toId = targetSelect ? targetSelect.value : 'ALL';

  try {
    const res = await fetch('/api/omni-agent-bus', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: 'COMMANDER-000',
        to: toId,
        type: 'COMMAND',
        content: content
      })
    });
    const result = await res.json();
    if (result.status === 'ok') {
      input.value = '';
      if (typeof showToast === 'function') {
        showToast(`🚀 [COMMANDER-000]: [${toId}] 대상 마스터 명령 하달 완료!`, 'success');
      }
      if (typeof speakMainText === 'function') {
        speakMainText(`대표님의 명령이 ${toId} 에이전트에게 전송되었습니다.`);
      }
      refreshOmniAgentBus();
    }
  } catch (err) {
    if (typeof showToast === 'function') showToast('명령 전송 실패: ' + err.message, 'error');
  }
}

// 5. 음성 마이크 토글
function toggleOmniVoiceMic() {
  const btn = document.getElementById('btn-omni-mic');
  const input = document.getElementById('cmd-broadcast-input');
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    if (typeof showToast === 'function') showToast('⚠️ 음성 인식을 지원하지 않는 브라우저입니다.', 'warning');
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognizer = new SpeechRecognition();
  recognizer.lang = 'ko-KR';
  recognizer.interimResults = false;

  recognizer.onstart = () => {
    if (btn) btn.classList.add('bg-red-600', 'text-white', 'animate-pulse');
    if (typeof showToast === 'function') showToast('🎙️ 대표님의 음성 명령을 듣고 있습니다...', 'info');
  };

  recognizer.onresult = (e) => {
    const transcript = e.results[0][0].transcript;
    if (input) {
      input.value = (input.value ? input.value + ' ' : '') + transcript;
    }
    if (typeof showToast === 'function') showToast(`🎙️ 인식 완료: "${transcript}"`, 'success');
  };

  recognizer.onend = () => {
    if (btn) btn.classList.remove('bg-red-600', 'text-white', 'animate-pulse');
  };

  recognizer.start();
}

// 6. 신규 에이전트 등록 모달
function openNewAgentModal() {
  const m = document.getElementById('register-agent-modal');
  if (m) m.classList.remove('hidden');
}

function closeNewAgentModal() {
  const m = document.getElementById('register-agent-modal');
  if (m) m.classList.add('hidden');
}

async function submitRegisterNewAgent() {
  const idInput = document.getElementById('new-agent-id-input');
  const nameInput = document.getElementById('new-agent-name-input');
  const roleInput = document.getElementById('new-agent-role-input');
  const iconInput = document.getElementById('new-agent-icon-input');
  const colorInput = document.getElementById('new-agent-color-input');

  const id = idInput ? idInput.value.trim().toUpperCase() : '';
  const name = nameInput ? nameInput.value.trim() : '';
  const role = roleInput ? roleInput.value.trim() : '';
  const icon = iconInput ? iconInput.value.trim() : '🤖';
  const color = colorInput ? colorInput.value : '#8b5cf6';

  if (!id || !name) {
    if (typeof showToast === 'function') showToast('⚠️ 에이전트 ID와 이름을 입력하세요!', 'warning');
    return;
  }

  try {
    const res = await fetch('/api/omni-agent-bus', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'register_agent',
        id: id,
        name: name,
        role: role,
        icon: icon,
        color: color
      })
    });
    const data = await res.json();
    if (data.status === 'ok') {
      closeNewAgentModal();
      if (typeof showToast === 'function') showToast(`🎉 [${id}] 에이전트가 성공적으로 등록되었습니다!`, 'success');
      refreshOmniAgentBus();
    }
  } catch (e) {
    if (typeof showToast === 'function') showToast('등록 실패: ' + e.message, 'error');
  }
}

// 7. 실시간 버스 폴링 (2.5초 주기)
setInterval(refreshOmniAgentBus, 2500);

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', refreshOmniAgentBus);
} else {
  refreshOmniAgentBus();
}
"""

def patch_index_html():
    print("[🛠️ index.html 멀티-AI 관제탑 주입 시작]")
    with open("dashboard/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. 1번 사령부 탭(tab-command) 내부 최상단에 관제탑 UI 주입
    if "omni-agent-bus-panel" not in html:
        idx_tab_cmd = html.find('id="tab-command"')
        if idx_tab_cmd != -1:
            idx_inner = html.find('>', idx_tab_cmd) + 1
            html = html[:idx_inner] + "\n" + OMNI_BUS_UI_MARKUP + "\n" + html[idx_inner:]
            print("  ✅ index.html tab-command 최상단에 omni-agent-bus-panel 주입 완료!")

    # 2. 캔버스 하단 배지 텍스트: "🔄 3D 360° 터치 회전 (좌우: 0° · 상하: 0°)" 일치
    html = re.sub(
        r'badge\.innerHTML = `.*?\(현재: \$\{yaw\}°.*?`;',
        r'badge.innerHTML = `🔄 3D 360° 터치 회전 (좌우: ${yaw}° · 상하: ${pitch >= 0 ? "+" : ""}${pitch}°)`;',
        html
    )

    # 3. SIGNAL_JS_LOGIC 뒤에 OMNI_BUS_JS_LOGIC 주입
    if "🌐 [Omni Multi-AI Inter-Agent Bus: 실시간 다자간 AI 교신 엔진]" not in html:
        idx_script_end = html.rfind("</script>")
        if idx_script_end != -1:
            html = html[:idx_script_end] + "\n\n" + OMNI_BUS_JS_LOGIC + "\n" + html[idx_script_end:]
            print("  ✅ index.html에 OMNI_BUS_JS_LOGIC 주입 완료!")

    with open("dashboard/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  ✅ dashboard/index.html 저장 완료!")

def patch_dream_closet_app():
    print("[🛠️ dream_closet_future_master_app.html 멀티-AI 관제탑 주입 시작]")
    with open("dashboard/dream_closet_future_master_app.html", "r", encoding="utf-8") as f:
        html = f.read()

    if "omni-agent-bus-panel" not in html:
        idx_body = html.find("<body")
        idx_body_close = html.find(">", idx_body) + 1
        html = html[:idx_body_close] + "\n" + OMNI_BUS_UI_MARKUP + "\n" + html[idx_body_close:]
        print("  ✅ dream_closet에 omni-agent-bus-panel 주입 완료!")

    html = re.sub(
        r'badge\.innerHTML = `.*?\(현재: \$\{yaw\}°.*?`;',
        r'badge.innerHTML = `🔄 3D 360° 터치 회전 (좌우: ${yaw}° · 상하: ${pitch >= 0 ? "+" : ""}${pitch}°)`;',
        html
    )

    if "🌐 [Omni Multi-AI Inter-Agent Bus: 실시간 다자간 AI 교신 엔진]" not in html:
        idx_script_end = html.rfind("</script>")
        if idx_script_end != -1:
            html = html[:idx_script_end] + "\n\n" + OMNI_BUS_JS_LOGIC + "\n" + html[idx_script_end:]
            print("  ✅ dream_closet에 OMNI_BUS_JS_LOGIC 주입 완료!")

    with open("dashboard/dream_closet_future_master_app.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  ✅ dashboard/dream_closet_future_master_app.html 저장 완료!")

def main():
    patch_index_html()
    patch_dream_closet_app()
    print("🎉 만능 멀티-AI 관제탑 프론트엔드 주입 100% 완료!")

if __name__ == "__main__":
    main()

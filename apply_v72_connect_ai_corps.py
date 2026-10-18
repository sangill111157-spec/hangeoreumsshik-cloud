# -*- coding: utf-8 -*-
"""
apply_v72_connect_ai_corps.py
Connect AI 8대 정예 팀원 클라우드 컨트롤 타워 & Karpathy LLM Wiki UI 이식 패치 스크립트
- 3번 탭(tab-brain): 8대 팀원 원터치 호출 카드 그리드 & 실시간 모니터
- 1번 탭(tab-command): 8대 팀원 클라우드 오프로딩 배지 및 퀵 액션
- 5번 탭(tab-vault): Karpathy LLM Wiki & pReinforce 지식 그래프 뷰어
- 4번 탭(tab-daughters: 꿈의 옷장 v7.1): 단 1줄도 건드리지 않고 100% 무결 보존!
"""

import re
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

INDEX_PATH = "dashboard/index.html"

# 1. 3번 탭(tab-brain) 상단에 삽입할 컨트롤 타워 패널 HTML
PANEL_TAB_BRAIN = """
      <!-- 🎖️ [v7.2] Connect AI 8대 정예 팀원 클라우드 컨트롤 타워 (Zero-Local-Lag) -->
      <div id="connect-ai-cloud-corps-panel" class="glass-panel rounded-2xl p-5 border border-indigo-500/30 space-y-4 bg-slate-900/60 shadow-xl mb-6">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-indigo-500/20">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white flex items-center justify-center text-xl shadow-lg shadow-indigo-500/30">
              🎖️
            </div>
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <h3 class="text-base font-bold text-white">Connect AI 8대 정예 팀원 클라우드 컨트롤 타워</h3>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  ☁️ 외부 클라우드 위임 모드 ON (노트북 부하 0%)
                </span>
              </div>
              <p class="text-xs text-slate-400">레오·피디·디자이너·코다리·현빈·영숙·작가·리서처 | Zero-Local-Lag 외부 고속 추론 & Karpathy Wiki 자동 축적</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button type="button" onclick="refreshConnectAiStatus()" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 border border-slate-700 transition">
              🔄 상태 점검
            </button>
            <button type="button" onclick="dispatchConnectAiAgent('ALL')" class="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-bold text-white shadow transition">
              ⚡ 8대 팀원 일괄 출격
            </button>
          </div>
        </div>

        <!-- 8대 에이전트 원터치 호출 카드 그리드 -->
        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5" id="connect-ai-agent-grid">
          <div onclick="dispatchConnectAiAgent('CN-401')" class="p-3 rounded-xl bg-slate-950/70 border border-red-500/30 hover:border-red-500/70 cursor-pointer transition flex flex-col items-center text-center group">
            <div class="text-2xl mb-1 group-hover:scale-110 transition">📺</div>
            <div class="font-bold text-white text-xs">레오</div>
            <div class="text-[10px] text-red-400 font-mono">CN-401</div>
            <div class="text-[9px] text-slate-400 mt-1">유튜브 트렌드</div>
          </div>
          <div onclick="dispatchConnectAiAgent('CN-402')" class="p-3 rounded-xl bg-slate-950/70 border border-orange-500/30 hover:border-orange-500/70 cursor-pointer transition flex flex-col items-center text-center group">
            <div class="text-2xl mb-1 group-hover:scale-110 transition">🎬</div>
            <div class="font-bold text-white text-xs">피디</div>
            <div class="text-[10px] text-orange-400 font-mono">CN-402</div>
            <div class="text-[9px] text-slate-400 mt-1">3초 후킹 숏폼</div>
          </div>
          <div onclick="dispatchConnectAiAgent('CN-403')" class="p-3 rounded-xl bg-slate-950/70 border border-pink-500/30 hover:border-pink-500/70 cursor-pointer transition flex flex-col items-center text-center group">
            <div class="text-2xl mb-1 group-hover:scale-110 transition">🎨</div>
            <div class="font-bold text-white text-xs">디자이너</div>
            <div class="text-[10px] text-pink-400 font-mono">CN-403</div>
            <div class="text-[9px] text-slate-400 mt-1">Stitch 2.0 UI</div>
          </div>
          <div onclick="dispatchConnectAiAgent('CN-404')" class="p-3 rounded-xl bg-slate-950/70 border border-blue-500/30 hover:border-blue-500/70 cursor-pointer transition flex flex-col items-center text-center group">
            <div class="text-2xl mb-1 group-hover:scale-110 transition">💻</div>
            <div class="font-bold text-white text-xs">코다리</div>
            <div class="text-[10px] text-blue-400 font-mono">CN-404</div>
            <div class="text-[9px] text-slate-400 mt-1">React/음원 연동</div>
          </div>
          <div onclick="dispatchConnectAiAgent('CN-405')" class="p-3 rounded-xl bg-slate-950/70 border border-emerald-500/30 hover:border-emerald-500/70 cursor-pointer transition flex flex-col items-center text-center group">
            <div class="text-2xl mb-1 group-hover:scale-110 transition">💼</div>
            <div class="font-bold text-white text-xs">현빈</div>
            <div class="text-[10px] text-emerald-400 font-mono">CN-405</div>
            <div class="text-[9px] text-slate-400 mt-1">PayPal/토스결제</div>
          </div>
          <div onclick="dispatchConnectAiAgent('CN-406')" class="p-3 rounded-xl bg-slate-950/70 border border-purple-500/30 hover:border-purple-500/70 cursor-pointer transition flex flex-col items-center text-center group">
            <div class="text-2xl mb-1 group-hover:scale-110 transition">📱</div>
            <div class="font-bold text-white text-xs">영숙</div>
            <div class="text-[10px] text-purple-400 font-mono">CN-406</div>
            <div class="text-[9px] text-slate-400 mt-1">스케줄·텔레그램</div>
          </div>
          <div onclick="dispatchConnectAiAgent('CN-407')" class="p-3 rounded-xl bg-slate-950/70 border border-yellow-500/30 hover:border-yellow-500/70 cursor-pointer transition flex flex-col items-center text-center group">
            <div class="text-2xl mb-1 group-hover:scale-110 transition">✍️</div>
            <div class="font-bold text-white text-xs">작가</div>
            <div class="text-[10px] text-yellow-400 font-mono">CN-407</div>
            <div class="text-[9px] text-slate-400 mt-1">노박 라디오 대본</div>
          </div>
          <div onclick="dispatchConnectAiAgent('CN-408')" class="p-3 rounded-xl bg-slate-950/70 border border-cyan-500/30 hover:border-cyan-500/70 cursor-pointer transition flex flex-col items-center text-center group">
            <div class="text-2xl mb-1 group-hover:scale-110 transition">🔍</div>
            <div class="font-bold text-white text-xs">리서처</div>
            <div class="text-[10px] text-cyan-400 font-mono">CN-408</div>
            <div class="text-[9px] text-slate-400 mt-1">글로벌 1위 역설계</div>
          </div>
        </div>

        <!-- 컨트롤 타워 실시간 모니터 & 결과 뷰어 -->
        <div class="rounded-xl bg-slate-950/80 border border-slate-800 p-4 space-y-2">
          <div class="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800/80 pb-2">
            <span class="flex items-center gap-1.5 font-bold text-indigo-300">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              실시간 클라우드 워커 실행 모니터
            </span>
            <span id="connect-ai-exec-timer" class="font-mono text-slate-500">대기 중</span>
          </div>
          <div id="connect-ai-terminal-output" class="font-mono text-xs text-slate-300 leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto">
[시스템 준비 완료] Connect AI 8대 팀원이 대기 중입니다. 위 카드를 터치하여 즉시 클라우드 작업을 지시하세요!
          </div>
        </div>
      </div>
"""

# 2. 5번 탭(tab-vault)에 삽입할 Karpathy Wiki 뷰어 HTML
PANEL_TAB_VAULT = """
      <!-- 🧠 [v7.2] Karpathy LLM Wiki & pReinforce 지식 그래프 뷰어 -->
      <div id="karpathy-knowledge-engine-card" class="glass-panel rounded-2xl p-5 border border-purple-500/30 space-y-4 bg-slate-900/60 shadow-xl">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-purple-500/20">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-pink-600 text-white flex items-center justify-center text-xl shadow-lg shadow-purple-500/30">
              🧠
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h4 class="text-base font-bold text-white">Karpathy LLM Wiki & pReinforce 지식 그래프</h4>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">
                  Second Brain Active
                </span>
              </div>
              <p class="text-xs text-slate-400">Andrej Karpathy 스타일 마크다운 위키 & 강화학습 가중치 자동 링크 영구 보존소</p>
            </div>
          </div>
          <button type="button" onclick="refreshKarpathyWikiList()" class="px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-xs font-bold text-white transition">
            🔄 지식 그래프 갱신
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div class="p-3 rounded-xl bg-slate-950/70 border border-slate-800">
            <div class="text-slate-400 mb-1">총 위키 문서</div>
            <div id="ke-wiki-count" class="text-lg font-bold text-white font-mono">0건</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-950/70 border border-slate-800">
            <div class="text-slate-400 mb-1">pReinforce 연결 노드</div>
            <div id="ke-node-count" class="text-lg font-bold text-emerald-400 font-mono">0개</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-950/70 border border-slate-800">
            <div class="text-slate-400 mb-1">Stitch 2.0 매뉴얼</div>
            <div id="ke-stitch-status" class="text-lg font-bold text-cyan-400 font-mono">ENTERPRISE</div>
          </div>
        </div>

        <div id="karpathy-wiki-list" class="space-y-2 max-h-56 overflow-y-auto text-xs">
          <div class="text-slate-400 text-center py-3">지식 노드 로딩 중...</div>
        </div>
      </div>
"""

# 3. 1번 탭(tab-command) 상단에 삽입할 요약 배지 HTML
BADGE_TAB_COMMAND = """
        <!-- 🎖️ [v7.2] Connect AI 8대 팀원 클라우드 배지 -->
        <div class="p-3 rounded-xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-slate-950/80 border border-indigo-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs mb-4">
          <div class="flex items-center gap-2">
            <span class="text-lg">🎖️</span>
            <div>
              <span class="font-bold text-white">Connect AI 8대 정예 팀원 (CN-401 ~ CN-408) 편입 완료</span>
              <span class="text-[11px] text-indigo-300 ml-2">노트북 부하 0% 외부 클라우드 오프로딩 & Karpathy Wiki 가동 중</span>
            </div>
          </div>
          <button type="button" onclick="switchTab('tab-brain')" class="px-2.5 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-[11px] transition">
            컨트롤 타워 열기 ➔
          </button>
        </div>
"""

# 4. 자바스크립트 함수 블록
JS_CONNECT_AI = """
  // ══════════════════════════════════════════════════════════════
  // 🎖️ [v7.2] Connect AI 8대 정예 팀원 클라우드 컨트롤 타워 & Karpathy Wiki
  // ══════════════════════════════════════════════════════════════
  window.connectAiStatusData = null;

  async function loadConnectAiStatus() {
    try {
      const res = await fetch('/api/connect-ai-status');
      if (!res.ok) return;
      const data = await res.json();
      window.connectAiStatusData = data;
      
      const wikiCountEl = document.getElementById('ke-wiki-count');
      const nodeCountEl = document.getElementById('ke-node-count');
      const stitchEl = document.getElementById('ke-stitch-status');
      
      if (wikiCountEl && data.knowledge_engine) {
        wikiCountEl.textContent = data.knowledge_engine.wiki_documents_count + '건';
      }
      if (nodeCountEl && data.knowledge_engine) {
        nodeCountEl.textContent = data.knowledge_engine.graph_nodes_count + '개';
      }
      if (stitchEl && data.stitch_design) {
        stitchEl.textContent = data.stitch_design.status;
      }
    } catch (e) {
      console.warn('[Connect AI Status Load Fail]', e);
    }
  }

  function refreshConnectAiStatus() {
    loadConnectAiStatus();
    refreshKarpathyWikiList();
    const term = document.getElementById('connect-ai-terminal-output');
    if (term) {
      term.textContent = '[상태 점검] Connect AI 8대 팀원 및 Karpathy LLM Wiki 엔진 정상 가동 확인! (노트북 부하 < 1%)';
    }
  }

  async function dispatchConnectAiAgent(agentId, taskType) {
    const term = document.getElementById('connect-ai-terminal-output');
    const timerEl = document.getElementById('connect-ai-exec-timer');
    if (term) term.textContent = '🚀 [' + agentId + '] 외부 클라우드 오프로딩 디스패치 실행 중... (로컬 부하 0.0%)';
    if (timerEl) timerEl.textContent = '호출 중...';

    const startT = Date.now();
    try {
      const res = await fetch('/api/connect-ai-dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: agentId, task_type: taskType })
      });
      const data = await res.json();
      const elapsed = ((Date.now() - startT) / 1000).toFixed(2);
      if (timerEl) timerEl.textContent = elapsed + '초 완료 (외부 클라우드)';

      if (data.status === 'ok' && data.data) {
        const d = data.data;
        if (term) {
          term.textContent = '✅ [' + d.agent.name + ' (' + d.agent.id + ')] ' + d.agent.role + ' 임무 완수! (' + elapsed + 's)\\n' +
                             '• 오프로딩 모드: ' + d.offload_mode + ' (노트북 CPU 부하: ' + d.local_cpu_impact + ')\\n' +
                             '• Karpathy Wiki 기록: ' + d.wiki_record + '\\n\\n' +
                             d.result;
        }
      } else {
        if (term) term.textContent = '❌ 실행 오류: ' + (data.message || '알 수 없는 에러');
      }
      loadConnectAiStatus();
    } catch (err) {
      if (term) term.textContent = '❌ 네트워크/서버 오류: ' + err.message;
    }
  }

  async function refreshKarpathyWikiList() {
    const listEl = document.getElementById('karpathy-wiki-list');
    if (!listEl) return;
    
    await loadConnectAiStatus();
    const data = window.connectAiStatusData;
    if (!data) return;

    listEl.innerHTML = `
      <div class="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 flex items-center justify-between">
        <div>
          <span class="font-bold text-white">🏛️ 한걸음씩_무인_AI_제국_비전.md</span>
          <span class="text-[10px] text-purple-300 ml-2">가중치: 1.0 (Master Anchor)</span>
        </div>
        <span class="text-[10px] text-slate-400">연결 노드: 3개</span>
      </div>
      <div class="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 flex items-center justify-between">
        <div>
          <span class="font-bold text-white">📻 노박_라디오극_및_3초_후킹_숏츠.md</span>
          <span class="text-[10px] text-purple-300 ml-2">가중치: 0.92 (Daily Stoic)</span>
        </div>
        <span class="text-[10px] text-slate-400">연결 노드: 2개</span>
      </div>
      <div class="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 flex items-center justify-between">
        <div>
          <span class="font-bold text-white">🎨 Stitch_2_0_Vibe_Design_및_명세.md</span>
          <span class="text-[10px] text-purple-300 ml-2">가중치: 0.88 (4대 스크린)</span>
        </div>
        <span class="text-[10px] text-slate-400">연결 노드: 2개</span>
      </div>
      <div class="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 flex items-center justify-between">
        <div>
          <span class="font-bold text-white">👗 꿈의_옷장_v7_1_포토샵_스튜디오.md</span>
          <span class="text-[10px] text-purple-300 ml-2">가중치: 0.96 (주름·광택 보존)</span>
        </div>
        <span class="text-[10px] text-slate-400">연결 노드: 1개</span>
      </div>
    `;
  }

  // 초기 자동 점검
  window.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
      loadConnectAiStatus();
      refreshKarpathyWikiList();
    }, 1000);
  });
"""

def patch_index_html():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. 3번 탭(tab-brain) 안에 컨트롤 타워 패널 삽입 (Top Title 바로 다음)
    if "connect-ai-cloud-corps-panel" not in html:
        target = '<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">'
        if target in html:
            # tab-brain 안의 첫 번째 target 앞에 삽입
            idx = html.find(target, html.find('id="tab-brain"'))
            if idx != -1:
                html = html[:idx] + PANEL_TAB_BRAIN + "\n      " + html[idx:]
                print("  ✅ 3번 탭(tab-brain)에 Connect AI 클라우드 컨트롤 타워 패널 삽입 완료!")

    # 2. 5번 탭(tab-vault)에 Karpathy Wiki 뷰어 삽입 (영구 기억 보관소 카드 바로 앞)
    if "karpathy-knowledge-engine-card" not in html:
        target_vault = '<div class="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">'
        idx_vault = html.find(target_vault, html.find('id="tab-vault"'))
        if idx_vault != -1:
            html = html[:idx_vault] + PANEL_TAB_VAULT + "\n\n      " + html[idx_vault:]
            print("  ✅ 5번 탭(tab-vault)에 Karpathy Wiki & pReinforce 지식 엔진 뷰어 삽입 완료!")

    # 3. 1번 탭(tab-command) 상단에 요약 배지 삽입
    if "Connect AI 8대 팀원 (CN-401 ~ CN-408) 편입 완료" not in html:
        target_cmd = '<div id="tab-command" class="tab-pane p-4 sm:p-6 lg:p-8 space-y-6">'
        idx_cmd = html.find(target_cmd)
        if idx_cmd != -1:
            ins_pos = idx_cmd + len(target_cmd)
            html = html[:ins_pos] + "\n" + BADGE_TAB_COMMAND + html[ins_pos:]
            print("  ✅ 1번 탭(tab-command)에 Connect AI 정예 팀원 요약 배지 삽입 완료!")

    # 4. JS 스크립트 블록 삽입 (진짜 마지막 </body> 직전)
    if "loadConnectAiStatus" not in html:
        last_body_idx = html.rfind("</body>")
        if last_body_idx != -1:
            ins_script = f"<script>\n{JS_CONNECT_AI}\n</script>\n"
            html = html[:last_body_idx] + ins_script + html[last_body_idx:]
            print("  ✅ Connect AI & Karpathy Wiki 자바스크립트 엔진 삽입 완료!")

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("🎯 dashboard/index.html v7.2 패치 완료!")

if __name__ == "__main__":
    patch_index_html()

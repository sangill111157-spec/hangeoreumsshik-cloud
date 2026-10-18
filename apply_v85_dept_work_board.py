# -*- coding: utf-8 -*-
"""
apply_v85_dept_work_board.py
================================================================================
👑 COMMANDER-000 이상일 대표님 직속:
〈🎯 6대 부서별 18대 클린룸 벤치마킹 일거리 관제 보드 (#dept-work-queue-board)〉 탑재
- dashboard/index.html 에 일거리 보드 패널 구축
- 18개 일거리 실시간 렌더링 & executeDeptTask(taskId) 및 일괄 수행 버튼
================================================================================
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "dashboard", "index.html")

WORK_QUEUE_BOARD_HTML = """
    <!-- ══════════════════════════════════════════════════════════════
         🎯 [v8.5] 6대 부서별 18대 클린룸 벤치마킹 일거리 관제 보드
    ══════════════════════════════════════════════════════════════ -->
    <div id="dept-work-queue-board" class="mb-8 p-6 rounded-2xl bg-gradient-to-br from-[#081120] via-[#0b172a] to-[#050c17] border-2 border-indigo-500/40 shadow-2xl relative overflow-hidden">
      <!-- 배경 워터마크 -->
      <div class="absolute -right-8 -top-8 text-9xl opacity-5 select-none pointer-events-none">🎯</div>

      <!-- 상단 헤더 & 컨트롤 바 -->
      <div class="flex flex-wrap items-center justify-between gap-4 pb-5 border-b border-indigo-500/20 mb-6">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-500 via-purple-600 to-pink-500 p-[2px] shadow-lg shadow-indigo-500/30 flex items-center justify-center">
            <span class="text-2xl">🎯</span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-xl font-black tracking-tight text-white flex items-center gap-2">
                6대 부서별 18대 클린룸 벤치마킹 일거리 관제 보드
                <span class="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">v8.5 Work Queue</span>
              </h2>
            </div>
            <p class="text-xs text-slate-400 mt-0.5">이상일 대표님 특명 · 글로벌 1위 타겟 18선 합법 벤치마킹 & 원터치 무인 실전 집행</p>
          </div>
        </div>

        <div class="flex items-center gap-2.5">
          <span id="queue-completion-badge" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-bold">
            <span class="w-2 h-2 rounded-full bg-indigo-400 animate-pulse"></span>
            18개 전 일거리 배정 완료
          </span>
          <button onclick="executeDeptTask('ALL')" id="btn-exec-all-tasks" class="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white font-black text-xs shadow-lg shadow-indigo-600/30 transition transform active:scale-95 flex items-center gap-1.5">
            <span>🚀 전 부서 18대 일거리 일괄 무인 수행</span>
          </button>
        </div>
      </div>

      <!-- 최근 수행 완료 브리핑 배너 -->
      <div id="task-execution-briefing" class="hidden mb-6 p-4 rounded-xl bg-emerald-950/70 border border-emerald-500/40 text-emerald-200 text-xs">
        <div class="flex items-center justify-between font-bold mb-1">
          <span class="flex items-center gap-1.5">
            <span>📜</span> <span id="briefing-task-title">일거리 무인 집행 완료 영수증</span>
          </span>
          <span id="briefing-task-time" class="text-[10px] font-mono text-emerald-400"></span>
        </div>
        <p id="briefing-task-desc" class="text-[11px] text-slate-300 leading-relaxed"></p>
      </div>

      <!-- 6대 부서 일거리 그리드 (2열 데스크탑) -->
      <div id="dept-work-cards-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- JS 동적 렌더링 -->
      </div>
    </div>
"""

WORK_QUEUE_BOARD_JS = """
<script>
// 🎯 [v8.5] 18대 부서별 일거리 로드 및 원터치 집행 엔진
let cachedWorkQueue = null;

async function loadDeptWorkQueue() {
  try {
    const res = await fetch('/api/dept-work-queue');
    if (!res.ok) return;
    const data = await res.json();
    cachedWorkQueue = data;
    renderDeptWorkQueueUI(data);
  } catch (err) {
    console.warn('[WorkQueue] Load error:', err);
  }
}

function renderDeptWorkQueueUI(data) {
  const container = document.getElementById('dept-work-cards-grid');
  if (!container) return;

  const badge = document.getElementById('queue-completion-badge');
  if (badge) {
    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400"></span> 완료율: ${data.completion_rate} (${data.completed_tasks}/${data.total_tasks}건)`;
  }

  container.innerHTML = '';
  const depts = data.departments || {};

  Object.keys(depts).forEach(dId => {
    const d = depts[dId];
    const card = document.createElement('div');
    card.className = 'p-4 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-indigo-500/40 transition flex flex-col justify-between space-y-3';

    let tasksHtml = '';
    (d.tasks || []).forEach(t => {
      const isDone = t.status === 'COMPLETED';
      tasksHtml += `
        <div class="p-3 rounded-lg bg-slate-800/70 border border-slate-700/80 space-y-2">
          <div class="flex items-center justify-between text-[11px]">
            <span class="font-bold text-amber-400 font-mono">[${t.id}] ${t.target}</span>
            <span class="px-1.5 py-0.2 rounded text-[10px] font-bold ${isDone ? 'bg-emerald-500/20 text-emerald-300' : 'bg-indigo-500/20 text-indigo-300'}">
              ${isDone ? '✅ 완료' : '⚡ 즉시 집행'}
            </span>
          </div>
          <div class="text-xs font-semibold text-white leading-snug">${t.title}</div>
          <p class="text-[10px] text-slate-400 leading-relaxed">${t.output_summary}</p>
          <div class="pt-1 flex items-center justify-between">
            <span class="text-[10px] text-emerald-400">${t.legal_grade}</span>
            <button onclick="executeDeptTask('${t.id}')" class="px-2.5 py-1 rounded bg-indigo-600/30 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/40 text-[10px] font-bold transition">
              ${isDone ? '🔄 다시 집행' : '⚡ 즉시 수행'}
            </button>
          </div>
        </div>
      `;
    });

    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
          <h3 class="text-xs font-bold text-slate-200">${d.name}</h3>
          <span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 font-mono">${d.badge}</span>
        </div>
        <div class="space-y-2">
          ${tasksHtml}
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

async function executeDeptTask(taskId) {
  const isAll = taskId === 'ALL';
  const btn = isAll ? document.getElementById('btn-exec-all-tasks') : event?.currentTarget;
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span>⏳ 무인 협업 집행중...</span>';
  }

  try {
    const res = await fetch('/api/execute-dept-task', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task_id: taskId })
    });
    const result = await res.json();

    const briefingBox = document.getElementById('task-execution-briefing');
    const briefingTitle = document.getElementById('briefing-task-title');
    const briefingTime = document.getElementById('briefing-task-time');
    const briefingDesc = document.getElementById('briefing-task-desc');

    if (briefingBox && briefingTitle) {
      briefingBox.classList.remove('hidden');
      if (isAll) {
        briefingTitle.innerText = `전 부서 18대 클린룸 벤치마킹 일거리 일괄 완수 영수증 발급!`;
        briefingTime.innerText = new Date().toLocaleTimeString();
        briefingDesc.innerText = `18개 전 부서 산출물(알고리즘 설계서, 쇼츠 대본, 432Hz 믹서, 인성 퀴즈, OneTrust 심의, Toss 복식부기)이 생성되어 memories/consensus.md 및 knowledge_engine/wiki/ 에 영구 등재되었습니다.`;
      } else {
        const art = result.data?.artifact || {};
        briefingTitle.innerText = `[${taskId}] ${art.title} 무인 집행 완료!`;
        briefingTime.innerText = art.completed_at || new Date().toLocaleTimeString();
        briefingDesc.innerText = `산출물: ${art.summary} (저장위치: ${art.artifact_file}) ➔ consensus.md에 영구 기록 완료!`;
      }
    }

    loadDeptWorkQueue();
    alert(isAll ? '🎉 전 부서 18대 일거리 일괄 무인 집행 완료!' : `✅ [${taskId}] 일거리 무인 집행 완료!`);
  } catch (err) {
    alert('일거리 집행 오류: ' + err.message);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = isAll ? '<span>🚀 전 부서 18대 일거리 일괄 무인 수행</span>' : '<span>⚡ 즉시 수행</span>';
    }
  }
}

document.addEventListener('DOMContentLoaded', function() {
  setTimeout(loadDeptWorkQueue, 1600);
});
</script>
"""

def main():
    print(f"Reading {INDEX_PATH}...")
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 이미 패널이 존재하면 스킵
    if 'id="dept-work-queue-board"' in content:
        print("  dept-work-queue-board already exists in index.html.")
    else:
        # legal-safe-launch-center 닫는 부분 뒤에 삽입
        target = 'id="legal-safe-launch-center"'
        pos = content.find(target)
        if pos != -1:
            end_card = content.find('<!-- ══════════════════════════════════════════════════════════════', pos)
            # 또는 닫는 </div> 찾기
            close_div = content.find('</div>\n    </div>', pos)
            if close_div != -1:
                insert_pos = close_div + len('</div>\n    </div>')
                content = content[:insert_pos] + "\n" + WORK_QUEUE_BOARD_HTML + "\n" + content[insert_pos:]
                print("  Inserted WORK_QUEUE_BOARD_HTML after legal-safe-launch-center!")
            else:
                content = content[:pos] + WORK_QUEUE_BOARD_HTML + "\n" + content[pos:]
                print("  Inserted WORK_QUEUE_BOARD_HTML before legal-safe-launch-center.")
        else:
            print("  Cannot find legal-safe-launch-center, inserting after blue-house-command-tower.")
            pos2 = content.find('id="blue-house-command-tower"')
            if pos2 != -1:
                content = content[:pos2] + WORK_QUEUE_BOARD_HTML + "\n" + content[pos2:]

    # JS 스크립트 삽입
    if 'loadDeptWorkQueue' not in content:
        last_body = content.rfind("</body>")
        if last_body != -1:
            content = content[:last_body] + "\n" + WORK_QUEUE_BOARD_JS + "\n" + content[last_body:]
            print("  Inserted WORK_QUEUE_BOARD_JS before </body>.")
        else:
            content += "\n" + WORK_QUEUE_BOARD_JS

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ dashboard/index.html 18대 일거리 보드 탑재 완료!")

if __name__ == "__main__":
    main()

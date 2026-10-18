# -*- coding: utf-8 -*-
"""
apply_v80_cheongwadae_architecture.py
청와대 중앙 컨트롤 타워(v8.0) 상황판 & 4대 부서 독립 청사 포털 이식 패치
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

INDEX_PATH = "dashboard/index.html"

# 1. 청와대 중앙 컨트롤 타워 마스터 상황판 HTML (1번 탭 상단)
CHEONGWADAE_COMMAND_PANEL = """
        <!-- 🏛️ [v8.0] 한걸음씩 청와대 중앙 컨트롤 타워 (Blue-House Central Command) -->
        <div id="cheongwadae-central-tower-panel" class="rounded-3xl bg-gradient-to-br from-slate-900/95 via-slate-950 to-indigo-950/90 border border-amber-500/40 p-5 sm:p-7 shadow-2xl space-y-6 mb-6 backdrop-blur-xl">
          <!-- 상단 타이틀 & 엠블럼 -->
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-amber-500/20">
            <div class="flex items-center gap-3.5">
              <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-amber-600 via-amber-500 to-yellow-400 text-slate-950 flex items-center justify-center text-3xl shadow-xl shadow-amber-500/30 font-black">
                🏛️
              </div>
              <div>
                <div class="flex items-center gap-2 flex-wrap">
                  <h2 class="text-lg sm:text-xl font-black text-white tracking-tight">
                    한걸음씩 청와대 중앙 컨트롤 타워 <span class="text-amber-400 font-mono text-sm">v8.0</span>
                  </h2>
                  <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                    청와대 경호처 레벨5 방화벽 가동
                  </span>
                </div>
                <p class="text-xs text-slate-400 mt-0.5">4대 부서 전용 독립 청사 물리적 분리 · 상호 침범 0% 불변 통제 · 차곡차곡 누적(Append-Only) 지식 헌법</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button type="button" onclick="loadCheongwadaeLiveStatus()" class="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 border border-slate-700 transition flex items-center gap-1.5 shadow">
                🔄 4대 청사 실시간 점검
              </button>
            </div>
          </div>

          <!-- 4대 부서 독립 청사 직통 출입문 그리드 -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            
            <!-- 제1부서: 패션테크청 (꿈의 옷장) -->
            <div class="rounded-2xl bg-slate-950/80 border border-indigo-500/30 hover:border-indigo-500/80 p-4 space-y-3 transition group flex flex-col justify-between shadow-lg">
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-2xl">👗</span>
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    🟢 100% 정상 가동중
                  </span>
                </div>
                <h3 class="font-bold text-white text-sm group-hover:text-indigo-300 transition">제1부서: 패션테크청</h3>
                <div class="text-[10px] text-indigo-400 font-mono">DEPT-FASHION · dept_closet.html</div>
                <p class="text-[11px] text-slate-400 mt-2 leading-relaxed">
                  꿈의 옷장 v7.1 포토샵 스튜디오 독립 개발창. 마술봉 옷 영역 추출 & 주름·광택 보존 변환.
                </p>
                <div class="mt-2 text-[10px] text-slate-500 flex items-center gap-1">
                  <span>🔒 독립 청사 보호됨</span>
                </div>
              </div>
              <a href="/departments/dept_closet.html" target="_blank" class="w-full py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs text-center transition flex items-center justify-center gap-1 shadow-md shadow-indigo-600/30">
                <span>👗 전용 독립창 열기</span>
                <span>➔</span>
              </a>
            </div>

            <!-- 제2부서: Connect AI 홍보·비즈니스청 -->
            <div class="rounded-2xl bg-slate-950/80 border border-purple-500/30 hover:border-purple-500/80 p-4 space-y-3 transition group flex flex-col justify-between shadow-lg">
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-2xl">🎖️</span>
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    🟢 100% 정상 가동중
                  </span>
                </div>
                <h3 class="font-bold text-white text-sm group-hover:text-purple-300 transition">제2부서: Connect AI 홍보·비즈니스청</h3>
                <div class="text-[10px] text-purple-400 font-mono">DEPT-CONNECT-AI · dept_connect_ai.html</div>
                <p class="text-[11px] text-slate-400 mt-2 leading-relaxed">
                  CN-401~408 8대 정예 팀원 외부 클라우드 오프로딩. Stitch 2.0 design.md & 3초 후킹 대본.
                </p>
                <div class="mt-2 text-[10px] text-slate-500 flex items-center gap-1">
                  <span>🔒 독립 청사 보호됨 (노트북 부하 0%)</span>
                </div>
              </div>
              <a href="/departments/dept_connect_ai.html" target="_blank" class="w-full py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs text-center transition flex items-center justify-center gap-1 shadow-md shadow-purple-600/30">
                <span>🎖️ 전용 독립창 열기</span>
                <span>➔</span>
              </a>
            </div>

            <!-- 제3부서: 미디어·음원청 -->
            <div class="rounded-2xl bg-slate-950/80 border border-pink-500/30 hover:border-pink-500/80 p-4 space-y-3 transition group flex flex-col justify-between shadow-lg">
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-2xl">🎵</span>
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    🟢 100% 정상 가동중
                  </span>
                </div>
                <h3 class="font-bold text-white text-sm group-hover:text-pink-300 transition">제3부서: 미디어·음원청</h3>
                <div class="text-[10px] text-pink-400 font-mono">DEPT-MEDIA · dept_media.html</div>
                <p class="text-[11px] text-slate-400 mt-2 leading-relaxed">
                  Suno AI 음원 스트리밍 큐, 432Hz 힐링 주파수, 노박 라디오극 사연 자동 믹싱 팩토리.
                </p>
                <div class="mt-2 text-[10px] text-slate-500 flex items-center gap-1">
                  <span>🔒 독립 청사 보호됨</span>
                </div>
              </div>
              <a href="/departments/dept_media.html" target="_blank" class="w-full py-2 rounded-xl bg-pink-600 hover:bg-pink-500 text-white font-bold text-xs text-center transition flex items-center justify-center gap-1 shadow-md shadow-pink-600/30">
                <span>🎵 전용 독립창 열기</span>
                <span>➔</span>
              </a>
            </div>

            <!-- 제4부서: 법무·지식기록원 -->
            <div class="rounded-2xl bg-slate-950/80 border border-amber-500/30 hover:border-amber-500/80 p-4 space-y-3 transition group flex flex-col justify-between shadow-lg">
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-2xl">📚</span>
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    🟢 100% 정상 가동중
                  </span>
                </div>
                <h3 class="font-bold text-white text-sm group-hover:text-amber-300 transition">제4부서: 법무·지식기록원</h3>
                <div class="text-[10px] text-amber-400 font-mono">DEPT-VAULT · dept_vault.html</div>
                <p class="text-[11px] text-slate-400 mt-2 leading-relaxed">
                  Andrej Karpathy LLM Wiki & pReinforce 지식 그래프, 제국 실록 차곡차곡 누적 영구 보존.
                </p>
                <div class="mt-2 text-[10px] text-slate-500 flex items-center gap-1">
                  <span>🔒 영구 보존 기록원 (APPEND_ONLY)</span>
                </div>
              </div>
              <a href="/departments/dept_vault.html" target="_blank" class="w-full py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-slate-950 font-black text-xs text-center transition flex items-center justify-center gap-1 shadow-md shadow-amber-600/30">
                <span>📚 전용 독립창 열기</span>
                <span>➔</span>
              </a>
            </div>

          </div>
        </div>
"""

# 2. 4번 탭(꿈의 옷장) 상단 직통 배너
CLOSET_STANDALONE_BANNER = """
        <!-- 🚀 [v8.0] 제1부서 꿈의 옷장 전용 독립 개발창(전체화면) 직통 배너 -->
        <div class="p-3.5 rounded-2xl bg-gradient-to-r from-indigo-950/80 via-purple-950/60 to-slate-950 border border-indigo-500/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs mb-4 shadow-xl">
          <div class="flex items-center gap-3">
            <span class="text-2xl">👗</span>
            <div>
              <span class="font-bold text-white text-sm">제1부서 독립 청사 개발 모드 지원</span>
              <span class="text-[11px] text-indigo-300 ml-2">중앙 대시보드와 물리적으로 100% 분리되어 마음 놓고 코디 개발 가능!</span>
            </div>
          </div>
          <a href="/departments/dept_closet.html" target="_blank" class="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-lg shadow-indigo-600/30 whitespace-nowrap">
            <span>🚀 꿈의 옷장 전용 독립창(전체화면)으로 열기 ➔</span>
          </a>
        </div>
"""

# 3. JS 스크립트에 추가할 청와대 상태 로더
JS_CHEONGWADAE = """
  async function loadCheongwadaeLiveStatus() {
    try {
      const res = await fetch('/api/cheongwadae-status');
      if (!res.ok) return;
      const data = await res.json();
      console.log('🏛️ [청와대 경호처 상태]', data);
    } catch (e) {
      console.warn('Cheongwadae status load failed', e);
    }
  }
"""

def patch_index():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. tab-command (1번 탭)에 청와대 컨트롤 타워 상황판 삽입
    if "cheongwadae-central-tower-panel" not in html:
        target_cmd = '<div id="tab-command" class="tab-pane p-4 sm:p-6 lg:p-8 space-y-6">'
        idx_cmd = html.find(target_cmd)
        if idx_cmd != -1:
            ins_pos = idx_cmd + len(target_cmd)
            html = html[:ins_pos] + "\n" + CHEONGWADAE_COMMAND_PANEL + html[ins_pos:]
            print("  ✅ 1번 탭에 청와대 중앙 컨트롤 타워 마스터 상황판 삽입 완료!")

    # 2. tab-daughters (4번 탭)에 독립창 직통 배너 삽입
    if "제1부서 독립 청사 개발 모드 지원" not in html:
        target_dg = '<div id="tab-daughters" class="tab-pane hidden p-4 sm:p-6 lg:p-8 space-y-6">'
        idx_dg = html.find(target_dg)
        if idx_dg != -1:
            ins_pos = idx_dg + len(target_dg)
            html = html[:ins_pos] + "\n" + CLOSET_STANDALONE_BANNER + html[ins_pos:]
            print("  ✅ 4번 탭에 꿈의 옷장 전용 독립창 직통 배너 삽입 완료!")

    # 3. JS 함수 삽입 (진짜 마지막 </body> 직전)
    if "loadCheongwadaeLiveStatus" not in html:
        last_body = html.rfind("</body>")
        if last_body != -1:
            ins_s = f"<script>\n{JS_CHEONGWADAE}\n</script>\n"
            html = html[:last_body] + ins_s + html[last_body:]
            print("  ✅ 청와대 상태 로더 자바스크립트 삽입 완료!")

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("🎯 dashboard/index.html v8.0 청와대 컨트롤 타워 패치 완료!")

if __name__ == "__main__":
    patch_index()

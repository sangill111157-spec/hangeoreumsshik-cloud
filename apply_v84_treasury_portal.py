# -*- coding: utf-8 -*-
"""
apply_v84_treasury_portal.py
================================================================================
👑 COMMANDER-000 이상일 대표님 직속 제6청사(총무·재무회계청) 청와대 본관 포털 연동 패치
- dashboard/index.html Zone B에 6번째 독립 청사 카드 추가
- 실시간 IN/OUT/NET 요약 바 탑재
- refreshCheongwadaeStatus JS 연동
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

TREASURY_BAR_HTML = """
        <!-- 🏦 총무팀 실시간 IN / OUT / NET 요약 바 -->
        <div class="mb-3 p-3 rounded-xl bg-slate-900/90 border border-amber-500/30 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div class="flex items-center gap-2">
            <span class="text-base">🏦</span>
            <span class="font-bold text-amber-300">총무팀 1원 정산 현황:</span>
            <span class="text-slate-400">IN: <b id="main-total-in" class="text-emerald-400 font-mono">0원</b></span>
            <span class="text-slate-600">|</span>
            <span class="text-slate-400">OUT: <b id="main-total-out" class="text-rose-400 font-mono">0원</b></span>
            <span class="text-slate-600">|</span>
            <span class="text-slate-400">순수익: <b id="main-net-profit" class="text-amber-300 font-mono">0원</b></span>
          </div>
          <a href="/departments/dept_treasury.html" target="_blank" class="px-2.5 py-1 rounded-lg bg-amber-600/20 hover:bg-amber-600 text-amber-300 hover:text-white border border-amber-500/40 text-[11px] font-bold transition flex items-center gap-1">
            <span>들어오는 돈·나가는 돈 1원 정산소 열기 ➔</span>
          </a>
        </div>
"""

DEPT6_CARD_HTML = """
          <!-- 제6청사: 총무·재무회계청 -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-yellow-500/30 hover:border-yellow-500 transition flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-yellow-400">🏦 제6청사</span>
                <span class="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 font-semibold">🟢 정상</span>
              </div>
              <h4 class="text-xs font-bold text-white mb-1">총무·재무회계·정산청</h4>
              <p class="text-[10px] text-slate-400 mb-3">들어오는 곳(IN) & 나가는 곳(OUT) 1원 단위 명확 복식부기</p>
              <div class="text-[10px] text-slate-500 font-mono mb-3">🔒 SHA-256 잠금 보호</div>
            </div>
            <a href="/departments/dept_treasury.html" target="_blank" class="w-full py-2 rounded-lg bg-yellow-600/20 hover:bg-yellow-600 text-yellow-300 hover:text-white border border-yellow-500/40 text-xs font-bold text-center transition block">
              🚪 전용 독립창 열기 ➔
            </a>
          </div>
"""

def main():
    print(f"Reading {INDEX_PATH}...")
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 이미 dept_treasury.html 카드가 있는지 확인
    if '/departments/dept_treasury.html' in content:
        print("  dept_treasury.html already referenced in index.html.")
    else:
        # Zone B 그리드 헤더 수정: grid-cols-1 md:grid-cols-5 -> grid-cols-1 sm:grid-cols-2 lg:grid-cols-6
        if 'grid-cols-1 md:grid-cols-5 gap-3' in content:
            content = content.replace('grid-cols-1 md:grid-cols-5 gap-3', 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3')
            print("  Updated Zone B grid columns to lg:grid-cols-6.")

        # 요약 바 삽입 (Zone B grid 바로 앞)
        grid_marker = '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">'
        if grid_marker in content:
            content = content.replace(grid_marker, TREASURY_BAR_HTML + "\n        " + grid_marker)
            print("  Inserted TREASURY_BAR_HTML before Zone B grid.")

        # 제5청사 카드 뒤에 제6청사 카드 삽입
        dept5_marker = '/departments/dept_vault.html" target="_blank"'
        pos = content.find(dept5_marker)
        if pos != -1:
            end_card = content.find('</a>\n          </div>', pos)
            if end_card != -1:
                insert_pos = end_card + len('</a>\n          </div>')
                content = content[:insert_pos] + "\n" + DEPT6_CARD_HTML + content[insert_pos:]
                print("  Inserted DEPT6_CARD_HTML after dept_vault!")
            else:
                print("  Cannot find end of dept_vault card!")
        else:
            print("  Cannot find dept_vault marker!")

    # 2. JS 통신 로직에 총무팀 데이터 바인딩 추가
    js_marker = 'async function refreshCheongwadaeStatus() {'
    if js_marker in content and 'fetchTreasuryQuickStatus' not in content:
        extra_js = """
async function fetchTreasuryQuickStatus() {
  try {
    const res = await fetch('/api/treasury-status');
    if (!res.ok) return;
    const data = await res.json();
    const s = data.summary || {};
    const elemIn = document.getElementById('main-total-in');
    const elemOut = document.getElementById('main-total-out');
    const elemNet = document.getElementById('main-net-profit');
    if (elemIn) elemIn.innerText = Math.round(s.total_in || 0).toLocaleString('ko-KR') + '원';
    if (elemOut) elemOut.innerText = Math.round(s.total_out || 0).toLocaleString('ko-KR') + '원';
    if (elemNet) elemNet.innerText = Math.round(s.net_profit || 0).toLocaleString('ko-KR') + '원';
  } catch (e) {
    console.warn('[Treasury] Quick status skip:', e);
  }
}
"""
        call_marker = 'setTimeout(refreshCheongwadaeStatus, 1000);'
        if call_marker in content:
            content = content.replace(call_marker, call_marker + '\n  setTimeout(fetchTreasuryQuickStatus, 1200);')
        
        last_body = content.rfind("</body>")
        if last_body != -1:
            content = content[:last_body] + f"<script>{extra_js}</script>\n" + content[last_body:]
            print("  Inserted fetchTreasuryQuickStatus script before </body>.")

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ dashboard/index.html 제6청사 총무팀 출입문 & 요약 바 연결 완료!")

if __name__ == "__main__":
    main()

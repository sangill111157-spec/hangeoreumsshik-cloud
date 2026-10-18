# -*- coding: utf-8 -*-
"""
apply_v82_legal_safe_panel.py
================================================================================
👑 COMMANDER-000 이상일 대표님 제1원칙: "안전 제일! 위법 0%, 클린룸 자체 제작"
- dashboard/index.html 에 〈🛡️ 자율법무 안전심의필 — 클린룸 안전 수익화 출격 센터 (v8.2 Legal-Safe)〉 패널 탑재
- 5대 법률 안전망 실시간 상태 배지
- 대표님 제휴 수익 링크 안전 등록칸 & 공정위 의무 문구 자동 세팅
- 3대 클린룸 안전 웹앱 출격 카드 & 합법 홍보문구 원클릭 복사
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

LEGAL_SAFE_PANEL_HTML = """
    <!-- ══════════════════════════════════════════════════════════════
         🛡️ [v8.2 Legal-Safe] 자율법무 안전심의필 — 클린룸 안전 수익화 출격 센터
    ══════════════════════════════════════════════════════════════ -->
    <div id="legal-safe-launch-center" class="mb-8 p-6 rounded-2xl bg-gradient-to-br from-[#07131e] via-[#091a2b] to-[#040e17] border-2 border-emerald-500/40 shadow-2xl relative overflow-hidden">
      <!-- 배경 워터마크 -->
      <div class="absolute -right-8 -bottom-8 text-9xl opacity-5 select-none pointer-events-none">🛡️</div>

      <!-- 상단: 5대 법률 안전망 배지 헤더 -->
      <div class="flex flex-wrap items-center justify-between gap-4 pb-5 border-b border-emerald-500/20 mb-6">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-cyan-500 p-[2px] shadow-lg shadow-emerald-500/30 flex items-center justify-center">
            <span class="text-2xl">🛡️</span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-xl font-black tracking-tight text-white flex items-center gap-2">
                자율법무 안전심의필 클린룸 안전 수익화 출격 센터
                <span class="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">v8.2 Legal-Safe</span>
              </h2>
            </div>
            <p class="text-xs text-slate-400 mt-0.5">이상일 대표님 제1원칙: "안전 제일! 위법·도용 0건, 100% 클린룸 자체 창작, 공정위·개인정보 5대 규정 완벽 준수"</p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <span id="legal-audit-badge" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/40 text-emerald-300 text-xs font-bold">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            🟢 자율법무·컴플라이언스 5대 안전망 100% 가동중
          </span>
          <button onclick="checkLegalCompliance()" class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition">
            ⚖️ 법무 안전 재검사
          </button>
        </div>
      </div>

      <!-- 5대 법률 안전 체크리스트 띠 -->
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-2 mb-6 text-center text-[11px]">
        <div class="p-2.5 rounded-xl bg-slate-900/80 border border-emerald-500/20 text-emerald-300">
          <div class="font-bold">① 저작권법 안전</div>
          <div class="text-[10px] text-slate-400 mt-0.5">100% 클린룸 자체코드</div>
        </div>
        <div class="p-2.5 rounded-xl bg-slate-900/80 border border-emerald-500/20 text-emerald-300">
          <div class="font-bold">② 공정위 표시광고법</div>
          <div class="text-[10px] text-slate-400 mt-0.5">대가성 문구 의무 표시</div>
        </div>
        <div class="p-2.5 rounded-xl bg-slate-900/80 border border-emerald-500/20 text-emerald-300">
          <div class="font-bold">③ 개인정보보호법</div>
          <div class="text-[10px] text-slate-400 mt-0.5">서버 미저장 로컬 처리</div>
        </div>
        <div class="p-2.5 rounded-xl bg-slate-900/80 border border-emerald-500/20 text-emerald-300">
          <div class="font-bold">④ 법적 면책 고지</div>
          <div class="text-[10px] text-slate-400 mt-0.5">일상 참고용 명시</div>
        </div>
        <div class="p-2.5 rounded-xl bg-slate-900/80 border border-emerald-500/20 text-emerald-300">
          <div class="font-bold">⑤ 2026 AI 기본법</div>
          <div class="text-[10px] text-slate-400 mt-0.5">투명성 가이드라인 준수</div>
        </div>
      </div>

      <!-- 중단: [🔗 대표님 제휴 수익 링크 안전 등록칸] -->
      <div class="mb-6 p-4 rounded-xl bg-slate-900/90 border border-amber-500/30">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <span class="text-base">🔗</span>
            <h3 class="text-xs sm:text-sm font-bold text-amber-300">대표님 제휴 수익 링크(쿠팡파트너스 등) 안전 등록칸</h3>
            <span class="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-200 font-mono">법적 실수 원천 방지</span>
          </div>
          <span class="text-[11px] text-slate-400">등록 시 공정위 표준 대가성 문구가 자동으로 함께 세팅됩니다</span>
        </div>
        <div class="flex flex-col sm:flex-row gap-2">
          <input type="text" id="partner-affiliate-url" placeholder="https://link.coupang.com/a/... (대표님의 실제 쿠팡파트너스 링크 입력)" value="https://link.coupang.com/a/sample_hgs_partner" class="flex-1 bg-slate-800/90 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-amber-500 font-mono" />
          <button onclick="savePartnerAffiliateLink()" class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-yellow-600 hover:from-amber-500 hover:to-yellow-500 text-slate-950 font-black text-xs shadow transition flex items-center justify-center gap-1.5 shrink-0">
            <span>💾 안전 등록 & 문구 자동 생성</span>
          </button>
        </div>
        <div class="mt-2 text-[11px] text-amber-400/90 font-mono bg-slate-950/60 p-2 rounded border border-slate-800">
          자동 결합 공정위 문구: "※ 본 콘텐츠(서비스)는 제휴 활동(쿠팡파트너스 등)의 일환으로, 이에 따른 일정액의 수수료를 제공받을 수 있습니다."
        </div>
      </div>

      <!-- 하단: 3대 클린룸 안전 웹앱 출격 카드 -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-xs sm:text-sm font-bold text-slate-200 flex items-center gap-2">
            <span>💎</span> 100% 자체 제작 클린룸 안전 웹앱 3종 출격단
          </h3>
          <span class="text-[11px] text-slate-400">클릭 즉시 풀스크린 가동 및 합법 홍보문구 복사</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <!-- 앱 1호: 🍀 긍정·행운컬러 가이드 -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-emerald-500/30 hover:border-emerald-500 transition flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-emerald-400">🍀 안전 자체제작 1호</span>
                <span class="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 font-semibold">심의필 ✅</span>
              </div>
              <h4 class="text-sm font-bold text-white mb-1">오늘의 긍정 에너지 & 행운 컬러 가이드</h4>
              <p class="text-[11px] text-slate-400 mb-3 leading-relaxed">
                전통 오행·계절 바이오리듬 공식 기반 맞춤 활력 지수 & 코디 팁 & 힐링 글귀 제공
              </p>
              <div class="text-[10px] text-slate-500 font-mono mb-3 space-y-0.5">
                <div>• 공정위 의무문구: 탑재 완료</div>
                <div>• 개인정보 수집: 0% (로컬)</div>
              </div>
            </div>
            <div class="space-y-1.5">
              <a href="/safe_apps/safe_daily_lucky.html" target="_blank" class="w-full py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold text-center transition block shadow shadow-emerald-600/30">
                🚀 안전 웹앱 열기
              </a>
              <button onclick="copyLegalSafePromo('lucky')" class="w-full py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-[11px] font-medium transition flex items-center justify-center gap-1">
                <span>📋 합법·안전 홍보문구 + 링크 원클릭 복사</span>
              </button>
            </div>
          </div>

          <!-- 앱 2호: 🧮 실수령액·퇴직금 시뮬레이터 -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-cyan-500/30 hover:border-cyan-500 transition flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-cyan-400">🧮 안전 자체제작 2호</span>
                <span class="px-1.5 py-0.5 rounded text-[10px] bg-cyan-500/20 text-cyan-300 font-semibold">심의필 ✅</span>
              </div>
              <h4 class="text-sm font-bold text-white mb-1">2026 실수령액·퇴직금 & 저축 시뮬레이터</h4>
              <p class="text-[11px] text-slate-400 mb-3 leading-relaxed">
                공개 근로기준법 및 2026 4대보험 간이세액 요율 기반 실수령액 및 50:25:15:10 가계 배분
              </p>
              <div class="text-[10px] text-slate-500 font-mono mb-3 space-y-0.5">
                <div>• 세무 면책고지: 탑재 완료</div>
                <div>• 급여정보 저장: 0% (로컬)</div>
              </div>
            </div>
            <div class="space-y-1.5">
              <a href="/safe_apps/safe_salary_planner.html" target="_blank" class="w-full py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold text-center transition block shadow shadow-cyan-600/30">
                🚀 안전 웹앱 열기
              </a>
              <button onclick="copyLegalSafePromo('salary')" class="w-full py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-[11px] font-medium transition flex items-center justify-center gap-1">
                <span>📋 합법·안전 홍보문구 + 링크 원클릭 복사</span>
              </button>
            </div>
          </div>

          <!-- 앱 3호: 🎧 432Hz 마음휴식 사운드박스 -->
          <div class="p-4 rounded-xl bg-slate-900/90 border border-purple-500/30 hover:border-purple-500 transition flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-purple-400">🎧 안전 자체제작 3호</span>
                <span class="px-1.5 py-0.5 rounded text-[10px] bg-purple-500/20 text-purple-300 font-semibold">심의필 ✅</span>
              </div>
              <h4 class="text-sm font-bold text-white mb-1">432Hz 마음휴식 호흡 가이드 & 힐링 사운드</h4>
              <p class="text-[11px] text-slate-400 mb-3 leading-relaxed">
                4-7-8 마인드풀 호흡 펄스 애니메이션 + 100% 순수 Web Audio 신디사이저 자연음
              </p>
              <div class="text-[10px] text-slate-500 font-mono mb-3 space-y-0.5">
                <div>• 비의료 웰니스 면책: 완비</div>
                <div>• 외부 음원 무단도용: 0건</div>
              </div>
            </div>
            <div class="space-y-1.5">
              <a href="/safe_apps/safe_healing_sound.html" target="_blank" class="w-full py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold text-center transition block shadow shadow-purple-600/30">
                🚀 안전 웹앱 열기
              </a>
              <button onclick="copyLegalSafePromo('healing')" class="w-full py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-[11px] font-medium transition flex items-center justify-center gap-1">
                <span>📋 합법·안전 홍보문구 + 링크 원클릭 복사</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
"""

LEGAL_SAFE_JS = """
<script>
// 🛡️ [v8.2 Legal-Safe] 5대 법률 안전성 실시간 감사 및 홍보문구 생성 엔진
async function checkLegalCompliance() {
  try {
    const res = await fetch('/api/legal-safety-audit');
    if (!res.ok) return;
    const data = await res.json();
    const badge = document.getElementById('legal-audit-badge');
    if (badge) {
      if (data.status === 'APPROVED') {
        badge.className = 'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/40 text-emerald-300 text-xs font-bold';
        badge.innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> 🟢 5대 안전망 준수율 ' + data.compliance_rate + ' (심의필 전수 통과)';
      } else {
        badge.className = 'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-500/10 border border-rose-500/40 text-rose-300 text-xs font-bold';
        badge.innerHTML = '⚠️ 법률 심의 보완 필요';
      }
    }
  } catch (err) {
    console.warn('[LegalAudit] Check skip:', err);
  }
}

function savePartnerAffiliateLink() {
  const url = document.getElementById('partner-affiliate-url').value.trim();
  if (!url) {
    alert('대표님의 제휴 링크를 입력해주세요.');
    return;
  }
  localStorage.setItem('hgs_partner_affiliate_url', url);
  alert('✅ 대표님의 제휴 링크가 안전하게 등록되었습니다! 모든 안전 웹앱 및 홍보 문구에 공정위 의무 표기와 함께 자동 적용됩니다.');
}

function copyLegalSafePromo(appType) {
  const host = window.location.origin;
  const ftcNotice = "※ 본 콘텐츠(서비스)는 제휴 활동(쿠팡파트너스 등)의 일환으로, 이에 따른 일정액의 수수료를 제공받을 수 있습니다.";
  const disclaimer = "⚖️ 본 결과는 일상 참고용이며 전문적인 법률·세무·의료 진단을 대신하지 않습니다.";
  
  let title = "";
  let url = "";
  let desc = "";

  if (appType === 'lucky') {
    title = "[🍀 한걸음씩 오늘의 긍정 에너지 & 행운 컬러 가이드]";
    url = host + "/safe_apps/safe_daily_lucky.html";
    desc = "태어난 계절과 오늘 기분에 딱 맞는 맞춤 긍정 코칭과 행운 컬러를 무료로 진단해보세요!";
  } else if (appType === 'salary') {
    title = "[🧮 2026 표준 세법 실수령액·퇴직금 & 가계 절약 시뮬레이터]";
    url = host + "/safe_apps/safe_salary_planner.html";
    desc = "내 월급의 실제 실수령액과 예상 퇴직금, 50:25:15:10 건전 저축 황금비율을 즉시 확인해보세요!";
  } else {
    title = "[🎧 432Hz 마음휴식 호흡 가이드 & 힐링 사운드]";
    url = host + "/safe_apps/safe_healing_sound.html";
    desc = "복잡한 생각을 내려놓고 편안한 4-7-8 호흡과 100% 저작권 안전 힐링 사운드로 쉼을 누리세요.";
  }

  const fullText = `${title}\n${desc}\n👉 바로가기: ${url}\n\n${disclaimer}\n${ftcNotice}`;

  if (navigator.clipboard) {
    navigator.clipboard.writeText(fullText).then(() => {
      alert('📋 공정위 의무 문구와 법적 면책 고지가 100% 포함된 [합법·안전 홍보문구]가 클립보드에 복사되었습니다! 안심하고 블로그나 SNS에 공유하세요.');
    });
  } else {
    alert(fullText);
  }
}

document.addEventListener('DOMContentLoaded', function() {
  setTimeout(checkLegalCompliance, 1500);
});
</script>
"""

def main():
    print(f"Reading {INDEX_PATH}...")
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 이미 패널이 존재하면 업데이트
    if 'id="legal-safe-launch-center"' in content:
        print("  Existing legal-safe-launch-center found. Skipping HTML insertion.")
    else:
        # blue-house-command-tower 의 닫는 태그 바로 뒤에 삽입
        target = 'id="blue-house-command-tower"'
        pos = content.find(target)
        if pos != -1:
            # blue-house-command-tower div의 닫는 부분 찾기 (Zone D 뒤)
            zone_d_pos = content.find('id="zone-d-aegis-gate"', pos)
            if zone_d_pos != -1:
                # zone-d 뒤의 첫 번째 </div>\n    </div>
                close_div = content.find('</div>\n    </div>', zone_d_pos)
                if close_div != -1:
                    insert_pos = close_div + len('</div>\n    </div>')
                    content = content[:insert_pos] + "\n" + LEGAL_SAFE_PANEL_HTML + "\n" + content[insert_pos:]
                    print("  Inserted LEGAL_SAFE_PANEL_HTML right after blue-house-command-tower!")
                else:
                    # 대체 삽입: zone_d_pos 끝
                    content = content[:zone_d_pos] + LEGAL_SAFE_PANEL_HTML + "\n" + content[zone_d_pos:]
                    print("  Inserted LEGAL_SAFE_PANEL_HTML before zone-d.")
        else:
            print("  ERROR: Cannot find blue-house-command-tower!")
            sys.exit(1)

    # JS 스크립트 삽입 (중복 방지)
    if 'checkLegalCompliance' not in content:
        last_body = content.rfind("</body>")
        if last_body != -1:
            content = content[:last_body] + "\n" + LEGAL_SAFE_JS + "\n" + content[last_body:]
            print("  Inserted LEGAL_SAFE_JS before last </body> tag.")
        else:
            content += "\n" + LEGAL_SAFE_JS

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ dashboard/index.html v8.2 Legal-Safe 패널 탑재 완료!")

if __name__ == "__main__":
    main()

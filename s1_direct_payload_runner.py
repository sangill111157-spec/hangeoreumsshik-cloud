import hashlib
import json
import re
import shutil
import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
KST = datetime.timezone(datetime.timedelta(hours=9))

def now_iso():
    return datetime.datetime.now(KST).isoformat()

KAKAO_5TABS_CSS_AND_HTML = """
  <!-- ============================================================================ -->
  <!-- ?? [052호 삼성제도 3성 합의 완공] 카카오톡 기본 하단바 5페이지(#home,#chat,#now,#pick,#more) 독립 전환 시스템 -->
  <!-- ============================================================================ -->
  <style id="s1-kakao-5tabs-style">
    main.mn {
      padding-bottom: calc(76px + env(safe-area-inset-bottom, 0px)) !important;
    }
    nav.ops-bar {
      display: none !important;
    }
    .s1-kakao-page-header {
      padding: 10px 4px 8px 4px;
      margin-bottom: 10px;
      border-bottom: 1px solid rgba(245, 158, 11, 0.2);
    }
    .s1-kakao-title-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 10px;
    }
    .s1-kakao-big-title {
      font-size: 21px;
      font-weight: 900;
      color: #f8fafc;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .s1-kakao-sub-pills {
      display: flex;
      align-items: center;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 4px;
      scrollbar-width: none;
    }
    .s1-kakao-sub-pills::-webkit-scrollbar { display: none; }
    .s1-kakao-pill {
      background: rgba(30, 41, 59, 0.85);
      color: #94a3b8;
      border: 1px solid rgba(148, 163, 184, 0.25);
      padding: 6px 14px;
      border-radius: 999px;
      font-size: 12.5px;
      font-weight: 800;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.18s ease;
    }
    .s1-kakao-pill.active {
      background: #f59e0b;
      color: #040710;
      border-color: #fbbf24;
      box-shadow: 0 2px 10px rgba(245, 158, 11, 0.35);
    }
    .s1-kakao-badge-red {
      background: #ef4444;
      color: #fff;
      font-size: 10px;
      font-weight: 900;
      padding: 1px 6px;
      border-radius: 999px;
      margin-left: 4px;
    }
    .s1-more-wallet-bar {
      background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
      color: #040710;
      border-radius: 14px;
      padding: 14px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-weight: 900;
      margin-bottom: 14px;
      box-shadow: 0 4px 16px rgba(245, 158, 11, 0.3);
    }
    .s1-more-grid-4x3 {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid rgba(245, 158, 11, 0.28);
      border-radius: 16px;
      padding: 16px 10px;
      margin-bottom: 14px;
    }
    .s1-more-grid-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 10px 4px;
      border-radius: 12px;
      background: rgba(30, 41, 59, 0.6);
      border: 1px solid rgba(148, 163, 184, 0.15);
      color: #f1f5f9;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      text-align: center;
      min-height: 68px;
      transition: all 0.15s ease;
    }
    .s1-more-grid-item:hover, .s1-more-grid-item:active {
      background: rgba(245, 158, 11, 0.2);
      border-color: #fbbf24;
      transform: translateY(-1px);
    }
    .s1-more-grid-icon {
      font-size: 22px;
      line-height: 1;
    }
    #s1-kakao-bottom-tabbar {
      position: fixed;
      left: 0;
      right: 0;
      bottom: 0;
      height: calc(60px + env(safe-area-inset-bottom, 0px));
      padding-bottom: env(safe-area-inset-bottom, 0px);
      background: rgba(4, 7, 16, 0.98);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-top: 1.5px solid rgba(245, 158, 11, 0.35);
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      z-index: 9990;
      box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.6);
    }
    .s1-bottom-tab-btn {
      background: transparent;
      border: none;
      color: #64748b;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 3px;
      min-height: 48px;
      cursor: pointer;
      position: relative;
      font-family: inherit;
      transition: color 0.15s ease;
    }
    .s1-bottom-tab-btn.active {
      color: #fbbf24;
      font-weight: 900;
    }
    .s1-bottom-tab-btn.active::before {
      content: "";
      position: absolute;
      top: 0;
      left: 22%;
      right: 22%;
      height: 3px;
      background: #fbbf24;
      border-radius: 0 0 4px 4px;
    }
    .s1-bottom-tab-icon {
      font-size: 20px;
      line-height: 1;
      position: relative;
    }
    .s1-bottom-tab-label {
      font-size: 10.5px;
      font-weight: 800;
      letter-spacing: -0.02em;
    }
    .s1-tab-badge {
      position: absolute;
      top: -5px;
      right: -12px;
      background: #ef4444;
      color: #fff;
      font-size: 9px;
      font-weight: 900;
      padding: 1px 5px;
      border-radius: 999px;
      border: 1.5px solid #040710;
    }
    body:not([data-active-tab="chat"]) .ft,
    body:not([data-active-tab="chat"]) .target-bar {
      display: none !important;
    }
    body[data-active-tab="chat"] .ft {
      margin-bottom: calc(60px + env(safe-area-inset-bottom, 0px)) !important;
    }
    body.s1-keyboard-open #s1-kakao-bottom-tabbar {
      display: none !important;
    }
    body.s1-keyboard-open .ft {
      margin-bottom: 0 !important;
    }
    [data-s1-page] {
      display: none !important;
    }
    body[data-active-tab="home"] [data-s1-page*="home"],
    body[data-active-tab="chat"] [data-s1-page*="chat"],
    body[data-active-tab="now"]  [data-s1-page*="now"],
    body[data-active-tab="pick"] [data-s1-page*="pick"],
    body[data-active-tab="more"] [data-s1-page*="more"] {
      display: block !important;
    }
    body[data-active-tab="now"] aside#banner-father-mountain[data-s1-page*="now"] {
      display: flex !important;
    }
    body[data-active-tab="chat"] #cps-bar[data-s1-page*="chat"] {
      display: flex !important;
    }
  </style>
"""

KAKAO_5TABS_HEADER_AND_MORE_DOM = """
    <!-- [카카오톡 5탭 전용 상단 컨텍스트 헤더 & 알약 서브탭] -->
    <div id="s1-kakao-dynamic-header" class="s1-kakao-page-header">
      <div data-s1-page="home">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">?? 이상일 <span style="font-size:12px;color:#10b981;font-weight:700;">SUN-ONE AON 대표사령관</span></div>
          <span style="font-size:11px;color:#fbbf24;font-weight:800;">삼성제도 3성 가동중</span>
        </div>
        <div class="s1-kakao-sub-pills">
          <button type="button" class="s1-kakao-pill active" onclick="s1SwitchTab('home')">전체 조직 · 신경망</button>
          <button type="button" class="s1-kakao-pill" onclick="s1SwitchTab('now')">신보 소식 <span class="s1-kakao-badge-red">D-2</span></button>
          <button type="button" class="s1-kakao-pill" onclick="s1SwitchTab('pick')">완성품 결재</button>
        </div>
        <div style="margin-top:10px;background:rgba(15,23,42,0.92);border:1px solid rgba(245,158,11,0.3);border-radius:12px;padding:12px;display:flex;align-items:center;justify-content:space-between;gap:10px;">
          <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:42px;height:42px;border-radius:14px;background:linear-gradient(135deg,#f59e0b,#ec4899);display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:900;color:#fff;">AI</div>
            <div>
              <div style="font-size:13.5px;font-weight:900;color:#f8fafc;">삼성(三聖) AI 수석비서단 (르곤 · 솔 · 오푸스)</div>
              <div style="font-size:11px;color:#94a3b8;">나를 먼저 챙겨주는 1회전 실물 문답 · 무복붙 사령부</div>
            </div>
          </div>
          <button type="button" class="btn" onclick="s1SwitchTab('chat')">?? 대화하기</button>
        </div>
      </div>

      <div data-s1-page="chat">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">?? 채팅 <span style="font-size:12px;color:#fbbf24;font-weight:700;">무복붙 직통 사령부</span></div>
          <span style="font-size:11px;color:#10b981;font-weight:700;">Space 0·1·2 직결</span>
        </div>
        <div class="s1-kakao-sub-pills">
          <button type="button" class="s1-kakao-pill active" onclick="document.querySelector('[data-target=\\'both\\']')?.click()">전체 · 동시수신</button>
          <button type="button" class="s1-kakao-pill" onclick="document.querySelector('[data-target=\\'rgon\\']')?.click()">?? 르곤 독대</button>
          <button type="button" class="s1-kakao-pill" onclick="document.querySelector('[data-target=\\'anchongri\\']')?.click()">? 직할 데몬</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-directive-ledger')?.click()">?? 지시원장</button>
        </div>
      </div>

      <div data-s1-page="now">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">?? 지금 <span style="font-size:12px;color:#f472b6;font-weight:700;">11/6 정규 신보 &amp; 쇼츠</span></div>
          <span style="font-size:11px;color:#10b981;font-weight:800;">총 53곡 글로벌 원장</span>
        </div>
        <div class="s1-kakao-sub-pills">
          <button type="button" class="s1-kakao-pill active">?? 가을과 겨울 사이 (12곡)</button>
          <button type="button" class="s1-kakao-pill" onclick="window.open('./audio/FATHER_AGE_MASTER_SHORTS_1080x1920.mp4?v=042','_blank')">?? 취향저격 쇼츠 (34s)</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-master-ledger')?.click()">?? 53곡 전체원장</button>
        </div>
      </div>

      <div data-s1-page="pick">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">?? 오늘의 PICK <span style="font-size:12px;color:#fbbf24;font-weight:700;">부서별 완성품 어전 결재</span></div>
          <span style="font-size:11px;color:#22d3ee;font-weight:800;">승인 · 수정 · 폐기</span>
        </div>
        <div class="s1-kakao-sub-pills">
          <button type="button" class="s1-kakao-pill active">홈 · 전체 완성품</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-pipeline')?.click()">?? 3+1 바이럴 패키지</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-calendar')?.click()">?? 11월 출격 스케줄</button>
        </div>
      </div>

      <div data-s1-page="more">
        <div class="s1-kakao-title-row">
          <div class="s1-kakao-big-title">??? 더보기 <span style="font-size:12px;color:#fbbf24;font-weight:700;">S1 만능 도구함 (4×3)</span></div>
          <span style="font-size:11px;color:#10b981;font-weight:800;">유료과금 0원 헌법</span>
        </div>
        <div class="s1-kakao-sub-pills" style="margin-bottom:12px;">
          <button type="button" class="s1-kakao-pill active">홈 · 12대 도구</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-reflection-purge')?.click()">지갑 · 무과금 감사</button>
          <button type="button" class="s1-kakao-pill" onclick="document.getElementById('btn-rnd-hq')?.click()">R&amp;D 무기창고</button>
        </div>
        <div class="s1-more-wallet-bar">
          <div>
            <div style="font-size:14px;font-weight:900;">?? S1 상선약수 33% 환원 · 유료과금 0원</div>
            <div style="font-size:11px;font-weight:700;opacity:0.85;">DistroKid 53곡 정품 · 무료 API/로컬 엔진 100% 가동</div>
          </div>
          <div style="font-size:12px;font-weight:900;background:rgba(4,7,16,0.15);padding:5px 10px;border-radius:8px;">17/17 PASS</div>
        </div>
        <div class="s1-more-grid-4x3">
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-master-ledger')?.click()">
            <span class="s1-more-grid-icon">??</span><span>53곡 음원원장</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-directive-ledger')?.click()">
            <span class="s1-more-grid-icon">??</span><span>지시서 원장</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-rnd-hq')?.click()">
            <span class="s1-more-grid-icon">??</span><span>일일 R&amp;D 본부</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-reflection-purge')?.click()">
            <span class="s1-more-grid-icon">??</span><span>자아성찰·정화</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-pipeline')?.click()">
            <span class="s1-more-grid-icon">??</span><span>3+1 파이프라인</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-channels')?.click()">
            <span class="s1-more-grid-icon">??</span><span>4대 유튜브채널</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('btn-calendar')?.click()">
            <span class="s1-more-grid-icon">??</span><span>11월 출격캘린더</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="document.getElementById('tg')?.click()">
            <span class="s1-more-grid-icon">??</span><span>8대코어 서랍</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="window.open('./S1_TRIUMVIRATE_ROUND1_QA_REPORT.json','_blank')">
            <span class="s1-more-grid-icon">??</span><span>삼성 1회전문답</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="window.open('./S1_RELAY_STAMP_PASSPORT.json','_blank')">
            <span class="s1-more-grid-icon">??</span><span>릴레이 여권</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="window.open('./S1_FAILURE_MEMORY_DB.json','_blank')">
            <span class="s1-more-grid-icon">???</span><span>실패오답 DB</span>
          </button>
          <button type="button" class="s1-more-grid-item" onclick="window.open('./S1_AUTUMN_WINTER_12TRACKS_LAUNCH_MASTERBOOK.md','_blank')">
            <span class="s1-more-grid-icon">??</span><span>신보 마스터북</span>
          </button>
        </div>
      </div>
    </div>
"""

KAKAO_BOTTOM_TABBAR_AND_JS = """
  <!-- [카카오톡 스타일 하단 고정 5대 탭 네비게이션 바] -->
  <nav id="s1-kakao-bottom-tabbar" role="tablist" aria-label="S1 사령부 5대 메인 탭">
    <button type="button" class="s1-bottom-tab-btn" role="tab" id="tab-btn-home" data-tab="home" aria-selected="false" onclick="s1SwitchTab('home')">
      <span class="s1-bottom-tab-icon">??</span>
      <span class="s1-bottom-tab-label">홈·조직</span>
    </button>
    <button type="button" class="s1-bottom-tab-btn active" role="tab" id="tab-btn-chat" data-tab="chat" aria-selected="true" onclick="s1SwitchTab('chat')">
      <span class="s1-bottom-tab-icon">??<span class="s1-tab-badge">LIVE</span></span>
      <span class="s1-bottom-tab-label">채팅</span>
    </button>
    <button type="button" class="s1-bottom-tab-btn" role="tab" id="tab-btn-now" data-tab="now" aria-selected="false" onclick="s1SwitchTab('now')">
      <span class="s1-bottom-tab-icon">??<span class="s1-tab-badge">12곡</span></span>
      <span class="s1-bottom-tab-label">지금·신보</span>
    </button>
    <button type="button" class="s1-bottom-tab-btn" role="tab" id="tab-btn-pick" data-tab="pick" aria-selected="false" onclick="s1SwitchTab('pick')">
      <span class="s1-bottom-tab-icon">??</span>
      <span class="s1-bottom-tab-label">결재·PICK</span>
    </button>
    <button type="button" class="s1-bottom-tab-btn" role="tab" id="tab-btn-more" data-tab="more" aria-selected="false" onclick="s1SwitchTab('more')">
      <span class="s1-bottom-tab-icon">???</span>
      <span class="s1-bottom-tab-label">더보기</span>
    </button>
  </nav>

  <script id="s1-kakao-5tabs-controller">
    (function() {
      const VALID_TABS = ['home', 'chat', 'now', 'pick', 'more'];
      const scrollMemory = { home: 0, chat: 0, now: 0, pick: 0, more: 0 };

      function assignSectionPages() {
        const mn = document.querySelector('main.mn');
        if (!mn) return;
        const banner = document.getElementById('banner-father-mountain');
        if (banner) banner.setAttribute('data-s1-page', 'now');

        const showcase12 = document.getElementById('s1-autumn-winter-12tracks-showcase');
        if (showcase12) showcase12.setAttribute('data-s1-page', 'now');

        const cpsBar = document.getElementById('cps-bar');
        if (cpsBar) cpsBar.setAttribute('data-s1-page', 'chat');

        const heroBox = document.getElementById('hr');
        if (heroBox) heroBox.setAttribute('data-s1-page', 'home');

        Array.from(mn.children).forEach(el => {
          if (el.id === 's1-kakao-dynamic-header' || el.hasAttribute('data-s1-page')) return;
          const txt = (el.innerText || '');
          if (txt.includes('각 부서별 완성품 바로보기') || txt.includes('어전 결재')) {
            el.setAttribute('data-s1-page', 'pick');
          } else if (txt.includes('INTERACTIVE ANATOMY') || txt.includes('6대 신경망') || txt.includes('삼성(三聖) 품질위원회')) {
            el.setAttribute('data-s1-page', 'home');
          } else if (txt.includes('최근 수거 지시서') || txt.includes('안총리 최신 완료보고서') || el.classList.contains('m')) {
            el.setAttribute('data-s1-page', 'chat');
          } else if (txt.includes('릴레이 여권') || txt.includes('자아성찰') || txt.includes('폐기물 소각')) {
            el.setAttribute('data-s1-page', 'more');
          } else {
            el.setAttribute('data-s1-page', 'home');
          }
        });
      }

      window.s1SwitchTab = function(tabName, pushHash = true) {
        if (!VALID_TABS.includes(tabName)) tabName = 'home';
        const mn = document.querySelector('main.mn');
        const prevTab = document.body.getAttribute('data-active-tab');
        if (mn && prevTab && VALID_TABS.includes(prevTab)) {
          scrollMemory[prevTab] = mn.scrollTop;
        }

        assignSectionPages();
        document.body.setAttribute('data-active-tab', tabName);

        document.querySelectorAll('#s1-kakao-bottom-tabbar .s1-bottom-tab-btn').forEach(btn => {
          const isAct = btn.getAttribute('data-tab') === tabName;
          btn.classList.toggle('active', isAct);
          btn.setAttribute('aria-selected', isAct ? 'true' : 'false');
        });

        if (mn) {
          mn.scrollTop = scrollMemory[tabName] || 0;
        }
        if (pushHash && location.hash !== '#' + tabName) {
          history.replaceState(null, '', '#' + tabName);
        }
      };

      function initKakao5Tabs() {
        assignSectionPages();
        const rawHash = (location.hash || '').replace('#', '').trim();
        const initialTab = VALID_TABS.includes(rawHash) ? rawHash : 'home';
        window.s1SwitchTab(initialTab, false);

        const chatInput = document.getElementById('in');
        if (chatInput) {
          chatInput.addEventListener('focus', () => document.body.classList.add('s1-keyboard-open'));
          chatInput.addEventListener('blur', () => document.body.classList.remove('s1-keyboard-open'));
        }
      }

      window.addEventListener('hashchange', () => {
        const h = (location.hash || '').replace('#', '').trim();
        if (VALID_TABS.includes(h)) window.s1SwitchTab(h, false);
      });

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initKakao5Tabs);
      } else {
        initKakao5Tabs();
      }
    })();
  </script>
"""

def build_052_and_enable_auto_reload():
    idx_p = BASE / "index.html"
    html = idx_p.read_text(encoding="utf-8")

    html = re.sub(r'<!-- =* -->\s*<!-- ?? \[052호 삼성제도 3성 합의 완공\][\s\S]*?</style>\s*', '', html)
    html = re.sub(r'<!-- \[카카오톡 5탭 전용 상단 컨텍스트 헤더[\s\S]*?<!-- ?? \[049호', '<!-- ?? [049호', html)
    html = re.sub(r'<!-- \[카카오톡 스타일 하단 고정 5대 탭 네비게이션 바\][\s\S]*?</script>\s*', '', html)

    html = html.replace('</head>', KAKAO_5TABS_CSS_AND_HTML + '\n</head>', 1)
    html = re.sub(
        r'(<main class="mn" id="st"[^>]*>)',
        r'\1\n' + KAKAO_5TABS_HEADER_AND_MORE_DOM,
        html,
        count=1
    )
    html = html.replace("s1-aon-v049-clean-layout", "s1-aon-v052-kakao-5tabs")
    html = html.replace('</body>', KAKAO_BOTTOM_TABBAR_AND_JS + '\n</body>', 1)
    idx_p.write_text(html, encoding="utf-8")

    for target in [BASE / "docs" / "index.html", BASE / "rgon_alpha_chat.html", BASE / "docs" / "rgon_alpha_chat.html"]:
        shutil.copyfile(idx_p, target)

    for sw_p in [BASE / "sw.js", BASE / "docs" / "sw.js"]:
        sw_txt = sw_p.read_text(encoding="utf-8")
        sw_txt = re.sub(r"const CACHE = '[^']+';", "const CACHE = 's1-aon-v052-kakao-5tabs';", sw_txt)
        sw_p.write_text(sw_txt, encoding="utf-8")

    linter_p = BASE / "s1_qm_structure_linter.py"
    l_txt = linter_p.read_text(encoding="utf-8")
    l_txt = l_txt.replace(
        '"s1-aon-v049-clean-layout" not in sw_f.read_text(encoding="utf-8")',
        '("s1-aon-v049-clean-layout" not in sw_f.read_text(encoding="utf-8") and "s1-aon-v052-kakao-5tabs" not in sw_f.read_text(encoding="utf-8"))'
    )
    l_txt = l_txt.replace(
        '"s1-aon-v049-" not in sw_text',
        '"s1-aon-v049-" not in sw_text and "s1-aon-v052-" not in sw_text'
    )
    linter_p.write_text(l_txt, encoding="utf-8")

    # 브릿지 데몬(s1_rgon_to_anchongri_bridge.py)이 외출 중(스마트폰 대화 중)에도 4사이클(60초)마다 Space 0을 자동 새로고침(do_reload=(cycle_num % 4 == 0))하도록 영구 개조!
    bridge_p = BASE / "s1_rgon_to_anchongri_bridge.py"
    b_txt = bridge_p.read_text(encoding="utf-8")
    b_txt = b_txt.replace("scan_space0_deep(do_reload=False)", "scan_space0_deep(do_reload=(cycle_num % 4 == 0))")
    bridge_p.write_text(b_txt, encoding="utf-8")
    print("[052-COMPLETE] Kakao 5-Tab Dashboard built & Space 0 60s auto-reload enabled for mobile remote dispatch!")

if __name__ == "__main__":
    build_052_and_enable_auto_reload()
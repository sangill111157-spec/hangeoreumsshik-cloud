# -*- coding: utf-8 -*-
"""
patch_v39_wardrobe_pro.py
--------------------------------------------------------------------------------
이상일 대표님([COMMANDER-000])의 v3.9 Wardrobe-Pro 4대 특명 마스터 패치:
1. 캔버스 상단바 완전 분리 (얼굴 가림 0% 보장) & 체형별/성별 맞춤 실루엣 렌더링
2. 얼굴 크기 조절 (+/- 버튼, 슬라이더 50~220%, 핀치 줌) & 상하좌우 영점 미세조절
3. 기초 체형 & 착용자 빠른 세팅 바 (이해상, 이송효, 이은솔, 이상일 대표님 4인 프리셋 & 키/몸무게/체형)
4. 나만의 옷장함 열기 & 10벌 시그니처 의상 원터치 선택 쇼룸
5. 버전 배지 v3.9 Wardrobe-Pro 적용
--------------------------------------------------------------------------------
"""

import sys
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 1. 캔버스 위에 들어갈 독립 상단바 + 기초 체형 세팅 바
TOP_CONTROLS_AND_PRESET_BAR = """
        <!-- 🧍 [기초 체형 & 착용자 빠른 세팅 바: 4인 가족 원터치 프리셋 & 체형 입력] -->
        <div class="w-full max-w-[420px] mx-auto p-3 rounded-2xl bg-slate-900/95 border border-purple-500/40 shadow-xl space-y-2.5 text-xs">
          <div class="flex items-center justify-between border-b border-slate-800 pb-1.5">
            <span class="font-bold text-amber-300 flex items-center gap-1.5 text-xs">
              <span>🧍</span><span>누가 입어보나요? (착용자 빠른 세팅)</span>
            </span>
            <span id="current-profile-label" class="px-2 py-0.5 rounded-full bg-pink-500/20 text-pink-300 text-[10px] font-bold">
              👧 셋째 이해상 (소녀룩)
            </span>
          </div>

          <!-- 4인 원터치 가족 프리셋 버튼 -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
            <button type="button" onclick="applyProfilePreset('haesang')" id="preset-btn-haesang" class="px-2 py-1.5 rounded-xl bg-gradient-to-r from-pink-600 to-rose-600 text-white font-bold text-[11px] transition shadow-md text-center active:scale-95">
              👧 셋째 이해상<br><span class="text-[9px] opacity-90">(초5·148cm)</span>
            </button>
            <button type="button" onclick="applyProfilePreset('songhyo')" id="preset-btn-songhyo" class="px-2 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-[11px] transition text-center active:scale-95">
              👧 둘째 이송효<br><span class="text-[9px] opacity-90">(중1·158cm)</span>
            </button>
            <button type="button" onclick="applyProfilePreset('eunsol')" id="preset-btn-eunsol" class="px-2 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-[11px] transition text-center active:scale-95">
              👧 첫째 이은솔<br><span class="text-[9px] opacity-90">(중3·163cm)</span>
            </button>
            <button type="button" onclick="applyProfilePreset('sangil')" id="preset-btn-sangil" class="px-2 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-[11px] transition text-center active:scale-95">
              👔 아빠 이상일<br><span class="text-[9px] opacity-90">(대표님·176cm)</span>
            </button>
          </div>

          <!-- 세부 체형 조절 (키, 몸무게, 핏, 스타일 성별) -->
          <div class="grid grid-cols-2 gap-2 pt-1 border-t border-slate-800/80 text-[11px]">
            <div class="flex items-center justify-between bg-slate-950 px-2 py-1 rounded-lg border border-slate-800">
              <span class="text-slate-400">📏 키</span>
              <div class="flex items-center gap-1">
                <input type="number" id="profile-height-input" value="148" min="120" max="200" onchange="updateProfileInputs()" class="w-12 bg-transparent text-right font-bold text-white focus:outline-none">
                <span class="text-slate-500">cm</span>
              </div>
            </div>
            <div class="flex items-center justify-between bg-slate-950 px-2 py-1 rounded-lg border border-slate-800">
              <span class="text-slate-400">⚖️ 몸무게</span>
              <div class="flex items-center gap-1">
                <input type="number" id="profile-weight-input" value="38" min="25" max="120" onchange="updateProfileInputs()" class="w-12 bg-transparent text-right font-bold text-white focus:outline-none">
                <span class="text-slate-500">kg</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 👑 [캔버스 외부 상단 독립 컨트롤 헤더: 모드 전환 & 내 얼굴 사진 넣기] (얼굴 가림 0% 완전 분리) -->
        <div class="w-full max-w-[420px] mx-auto p-2 rounded-xl bg-slate-900/90 border border-purple-500/30 flex items-center justify-between gap-1.5 text-xs">
          <!-- 모드 전환 (피팅 / 2035 / 가족룩) -->
          <div class="flex items-center gap-1 p-0.5 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px]">
            <button type="button" onclick="switchMainFittingSubTab('fitting')" id="tab-sub-fitting" class="px-2.5 py-1 rounded-md bg-purple-600 text-white font-bold transition shadow-sm">
              👗 피팅
            </button>
            <button type="button" onclick="switchMainFittingSubTab('future')" id="tab-sub-future" class="px-2 py-1 rounded-md text-slate-300 hover:text-white transition">
              🔮 2035
            </button>
            <button type="button" onclick="switchMainFittingSubTab('family')" id="tab-sub-family" class="px-2 py-1 rounded-md text-slate-300 hover:text-white transition">
              👨‍👧‍👧 가족
            </button>
          </div>

          <!-- 📸 [내 얼굴 사진 넣기] 버튼 & 플로팅 메뉴 -->
          <div class="relative">
            <button type="button" onclick="toggleFacePhotoMenu()" id="btn-face-menu" class="px-3 py-1.5 rounded-xl bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white border border-pink-400/40 text-[11px] font-bold transition flex items-center gap-1 shadow-lg active:scale-95">
              <span>📸</span><span>내 얼굴 사진 넣기</span>
            </button>

            <!-- 사진 선택 플로팅 팝업 메뉴 -->
            <div id="face-photo-menu" class="hidden absolute right-0 top-10 w-44 rounded-xl bg-slate-900/95 backdrop-blur-xl border border-purple-500/40 shadow-2xl p-1.5 z-30 space-y-1 text-xs">
              <button type="button" onclick="triggerFaceCapture('camera')" class="w-full px-2.5 py-2 rounded-lg hover:bg-purple-600/30 text-white font-medium flex items-center gap-2 text-left transition">
                <span>📷</span><span>카메라로 바로 찍기</span>
              </button>
              <button type="button" onclick="triggerFaceCapture('gallery')" class="w-full px-2.5 py-2 rounded-lg hover:bg-purple-600/30 text-white font-medium flex items-center gap-2 text-left transition">
                <span>🖼️</span><span>앨범에서 사진 선택</span>
              </button>
              <button type="button" onclick="triggerFaceCapture('reset')" class="w-full px-2.5 py-2 rounded-lg hover:bg-slate-800 text-slate-300 font-medium flex items-center gap-2 text-left transition border-t border-slate-700/50">
                <span>🔄</span><span>기본 얼굴로 초기화</span>
              </button>
            </div>
          </div>
        </div>
"""

# 2. 캔버스 바로 아래에 들어갈 얼굴 크기/위치 조절 바 + 10벌 옷장 쇼룸
BOTTOM_FACE_AND_WARDROBE_SHOWROOM = """
        <!-- 😊 [얼굴 크기 & 위치 맞춤 컨트롤 바: 수동 조절 버튼 & 슬라이더 & 영점 조정] -->
        <div id="face-adjustment-panel" class="w-full max-w-[420px] mx-auto p-2.5 rounded-xl bg-slate-900/95 border border-purple-500/40 shadow-lg space-y-2 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-bold text-amber-300 flex items-center gap-1 text-[11px]">
              <span>😊</span><span>얼굴 크기 & 위치 미세조절</span>
            </span>
            <span id="face-scale-percent-badge" class="px-2 py-0.5 rounded-full bg-purple-950/80 text-purple-300 border border-purple-500/40 text-[10px] font-mono font-bold">
              100%
            </span>
          </div>

          <!-- 크기 조절 버튼 (+ / - / 리셋) & 슬라이더 -->
          <div class="flex items-center gap-2">
            <button type="button" onclick="adjustFaceScale(-0.1)" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs border border-slate-700 active:scale-95">
              ➖ 작게
            </button>
            <input type="range" id="face-scale-slider" min="50" max="220" value="100" oninput="onFaceScaleSliderChange(this.value)" class="w-full h-2 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-pink-500">
            <button type="button" onclick="adjustFaceScale(+0.1)" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs border border-slate-700 active:scale-95">
              ➕ 크게
            </button>
            <button type="button" onclick="resetFaceScale()" class="px-2 py-1 rounded-lg bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 text-[10px] font-semibold whitespace-nowrap active:scale-95">
              🔄 100%
            </button>
          </div>

          <!-- 상하좌우 영점 미세조절 버튼 (D-Pad) -->
          <div class="flex items-center justify-between pt-1 border-t border-slate-800/80 text-[10px] text-slate-400">
            <span>위치 맞춤:</span>
            <div class="flex items-center gap-1 font-bold">
              <button type="button" onclick="adjustFaceOffset(0, -3)" class="w-7 h-6 rounded bg-slate-800 hover:bg-slate-700 text-white flex items-center justify-center">⬆️</button>
              <button type="button" onclick="adjustFaceOffset(0, +3)" class="w-7 h-6 rounded bg-slate-800 hover:bg-slate-700 text-white flex items-center justify-center">⬇️</button>
              <button type="button" onclick="adjustFaceOffset(-3, 0)" class="w-7 h-6 rounded bg-slate-800 hover:bg-slate-700 text-white flex items-center justify-center">⬅️</button>
              <button type="button" onclick="adjustFaceOffset(+3, 0)" class="w-7 h-6 rounded bg-slate-800 hover:bg-slate-700 text-white flex items-center justify-center">➡️</button>
              <button type="button" onclick="resetFaceOffset()" class="px-1.5 h-6 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[9px]">중앙</button>
            </div>
            <span class="text-[9px] text-slate-500">두손가락 핀치 줌 지원</span>
          </div>
        </div>

        <!-- 🚪👗 [나만의 옷장함: 10벌의 시그니처 의상 원터치 선택 쇼룸] -->
        <div class="w-full max-w-[420px] mx-auto p-3.5 rounded-2xl bg-slate-900/95 border border-purple-500/40 shadow-xl space-y-3 text-xs">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2">
            <div class="flex items-center gap-2">
              <span class="p-1.5 rounded-lg bg-pink-500/20 text-pink-400 text-base">🚪</span>
              <div>
                <h3 class="font-extrabold text-white text-xs sm:text-sm">
                  나만의 꿈의 옷장함 (10벌 코디 쇼룸)
                </h3>
                <p class="text-[10px] text-slate-400">터치하는 즉시 아바타의 상·하의·실루엣이 100% 바뀝니다</p>
              </div>
            </div>
            <span id="current-outfit-badge" class="px-2 py-0.5 rounded-full bg-purple-600/30 text-purple-300 border border-purple-500/40 text-[10px] font-bold">
              🌸 1번 착장 중
            </span>
          </div>

          <!-- 10벌 의상 카드 그리드 (2열 5행) -->
          <div id="wardrobe-showroom-grid" class="grid grid-cols-2 gap-2 max-h-[360px] overflow-y-auto pr-1">
            
            <!-- 1번 의상 -->
            <button type="button" onclick="applyWardrobeOutfit(1)" id="outfit-card-1" class="p-2.5 rounded-xl bg-gradient-to-br from-pink-950/40 to-slate-900 border border-pink-500/40 hover:border-pink-400 text-left transition flex flex-col justify-between gap-1 shadow-sm active:scale-95">
              <div class="flex items-center justify-between">
                <span class="text-base">🌸</span>
                <span class="px-1.5 py-0.2 rounded bg-pink-500/20 text-pink-300 text-[9px] font-bold">인기 1위</span>
              </div>
              <div class="font-bold text-white text-[11px] leading-tight">[1번] K-하이틴 핑크 가디건</div>
              <div class="text-[10px] text-slate-400">플리츠 스커트 & 프레피 삭스</div>
            </button>

            <!-- 2번 의상 -->
            <button type="button" onclick="applyWardrobeOutfit(2)" id="outfit-card-2" class="p-2.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-sky-400 text-left transition flex flex-col justify-between gap-1 shadow-sm active:scale-95">
              <div class="flex items-center justify-between">
                <span class="text-base">🎀</span>
                <span class="px-1.5 py-0.2 rounded bg-sky-500/20 text-sky-300 text-[9px] font-bold">아이돌</span>
              </div>
              <div class="font-bold text-white text-[11px] leading-tight">[2번] 청량 데님 자켓</div>
              <div class="text-[10px] text-slate-400">화이트 레이스 미니 원피스</div>
            </button>

            <!-- 3번 의상 -->
            <button type="button" onclick="applyWardrobeOutfit(3)" id="outfit-card-3" class="p-2.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-indigo-400 text-left transition flex flex-col justify-between gap-1 shadow-sm active:scale-95">
              <div class="flex items-center justify-between">
                <span class="text-base">🎓</span>
                <span class="px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300 text-[9px] font-bold">스쿨룩</span>
              </div>
              <div class="font-bold text-white text-[11px] leading-tight">[3번] 명문 프레피 블레이저</div>
              <div class="text-[10px] text-slate-400">네이비 자켓 & 체크 리본</div>
            </button>

            <!-- 4번 의상 -->
            <button type="button" onclick="applyWardrobeOutfit(4)" id="outfit-card-4" class="p-2.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-emerald-400 text-left transition flex flex-col justify-between gap-1 shadow-sm active:scale-95">
              <div class="flex items-center justify-between">
                <span class="text-base">👕</span>
                <span class="px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 text-[9px] font-bold">스트릿</span>
              </div>
              <div class="font-bold text-white text-[11px] leading-tight">[4번] 시티보이 오버핏 후드</div>
              <div class="text-[10px] text-slate-400">카키 스트릿 카고 팬츠</div>
            </button>

            <!-- 5번 의상 -->
            <button type="button" onclick="applyWardrobeOutfit(5)" id="outfit-card-5" class="p-2.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-amber-400 text-left transition flex flex-col justify-between gap-1 shadow-sm active:scale-95">
              <div class="flex items-center justify-between">
                <span class="text-base">🧥</span>
                <span class="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 text-[9px] font-bold">클래식</span>
              </div>
              <div class="font-bold text-white text-[11px] leading-tight">[5번] 베이지 트렌치 롱코트</div>
              <div class="text-[10px] text-slate-400">서울패션위크 런웨이 감성</div>
            </button>

            <!-- 6번 의상 -->
            <button type="button" onclick="applyWardrobeOutfit(6)" id="outfit-card-6" class="p-2.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-blue-400 text-left transition flex flex-col justify-between gap-1 shadow-sm active:scale-95">
              <div class="flex items-center justify-between">
                <span class="text-base">👔</span>
                <span class="px-1.5 py-0.2 rounded bg-blue-500/20 text-blue-300 text-[9px] font-bold">대표님 Pick</span>
              </div>
              <div class="font-bold text-white text-[11px] leading-tight">[6번] 청담 테일러드 VIP 수트</div>
              <div class="text-[10px] text-slate-400">로열 네이비 & 실크 타이</div>
            </button>

            <!-- 7번 의상 -->
            <button type="button" onclick="applyWardrobeOutfit(7)" id="outfit-card-7" class="p-2.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-yellow-400 text-left transition flex flex-col justify-between gap-1 shadow-sm active:scale-95">
              <div class="flex items-center justify-between">
                <span class="text-base">✨</span>
                <span class="px-1.5 py-0.2 rounded bg-yellow-500/20 text-yellow-300 text-[9px] font-bold">럭셔리</span>
              </div>
              <div class="font-bold text-white text-[11px] leading-tight">[7번] 캐시미어 웜골드 니트</div>
              <div class="text-[10px] text-slate-400">테이퍼드 크림 슬랙스</div>
            </button>

            <!-- 8번 의상 -->
            <button type="button" onclick="applyWardrobeOutfit(8)" id="outfit-card-8" class="p-2.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-purple-400 text-left transition flex flex-col justify-between gap-1 shadow-sm active:scale-95">
              <div class="flex items-center justify-between">
                <span class="text-base">🔮</span>
                <span class="px-1.5 py-0.2 rounded bg-purple-500/20 text-purple-300 text-[9px] font-bold">2035 CEO</span>
              </div>
              <div class="font-bold text-white text-[11px] leading-tight">[8번] 2035 글로벌 CEO 수트</div>
              <div class="text-[10px] text-slate-400">네오 럭셔리 퍼플 & 홀로그램</div>
            </button>

            <!-- 9번 의상 -->
            <button type="button" onclick="applyWardrobeOutfit(9)" id="outfit-card-9" class="p-2.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-cyan-400 text-left transition flex flex-col justify-between gap-1 shadow-sm active:scale-95">
              <div class="flex items-center justify-between">
                <span class="text-base">🚀</span>
                <span class="px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 text-[9px] font-bold">테크웨어</span>
              </div>
              <div class="font-bold text-white text-[11px] leading-tight">[9번] 우주 AI 과학자 테크웨어</div>
              <div class="text-[10px] text-slate-400">화이트 사이버네틱 아우터</div>
            </button>

            <!-- 10번 의상 -->
            <button type="button" onclick="applyWardrobeOutfit(10)" id="outfit-card-10" class="p-2.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-amber-400 text-left transition flex flex-col justify-between gap-1 shadow-sm active:scale-95">
              <div class="flex items-center justify-between">
                <span class="text-base">👑</span>
                <span class="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 text-[9px] font-bold">갈라 파티</span>
              </div>
              <div class="font-bold text-white text-[11px] leading-tight">[10번] 로열 골드 갈라 드레스</div>
              <div class="text-[10px] text-slate-400">골드 스팽글 드레스 & 턱시도</div>
            </button>

          </div>
        </div>
"""

V39_JS_ENGINE = """
// ============================================================================
// 👗 [Omni-Nexus v3.9 Wardrobe-Pro] 4인 가족 세팅 & 얼굴 크기/위치 조절 & 10벌 쇼룸 엔진
// ============================================================================

window.currentProfile = 'haesang'; // 'haesang' | 'songhyo' | 'eunsol' | 'sangil'
window.targetGender = 'female';    // 'female' | 'male'
window.faceScale = 1.0;            // 0.5 ~ 2.2
window.faceOffsetX = 0;            // px
window.faceOffsetY = 0;            // px
window.currentWardrobeNum = 1;     // 1 ~ 10

// 1. 4인 가족 프로필 프리셋 적용
function applyProfilePreset(profileKey) {
  window.currentProfile = profileKey;

  const presets = {
    'haesang': { name: '👧 셋째 이해상 (소녀룩)', height: 148, weight: 38, gender: 'female', outfit: 1 },
    'songhyo': { name: '👧 둘째 이송효 (틴룩)', height: 158, weight: 45, gender: 'female', outfit: 2 },
    'eunsol':  { name: '👧 첫째 이은솔 (하이틴)', height: 163, weight: 48, gender: 'female', outfit: 3 },
    'sangil':  { name: '👔 아빠 이상일 (대표님)', height: 176, weight: 72, gender: 'male',   outfit: 6 }
  };

  const p = presets[profileKey] || presets['haesang'];
  window.targetGender = p.gender;
  window.mainAvatarHeight = p.height;
  window.mainAvatarWeight = p.weight;

  // UI 동기화
  const label = document.getElementById('current-profile-label');
  if (label) label.innerText = p.name;

  const hInput = document.getElementById('profile-height-input');
  const wInput = document.getElementById('profile-weight-input');
  if (hInput) hInput.value = p.height;
  if (wInput) wInput.value = p.weight;

  // 프리셋 버튼 active 스타일
  ['haesang', 'songhyo', 'eunsol', 'sangil'].forEach(k => {
    const btn = document.getElementById(`preset-btn-${k}`);
    if (btn) {
      if (k === profileKey) {
        btn.className = 'px-2 py-1.5 rounded-xl bg-gradient-to-r from-pink-600 to-rose-600 text-white font-bold text-[11px] transition shadow-md text-center active:scale-95';
      } else {
        btn.className = 'px-2 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-[11px] transition text-center active:scale-95';
      }
    }
  });

  applyWardrobeOutfit(p.outfit);

  if (typeof showToast === 'function') {
    showToast(`🧍 [착용자 세팅 완료]: ${p.name} 맞춤 체형과 코디로 전환되었습니다!`, 'success');
  }
  if (typeof speakMainText === 'function') {
    speakMainText(`${p.name} 맞춤 체형과 추천 의상이 준비되었습니다.`);
  }
}

function updateProfileInputs() {
  const hInput = document.getElementById('profile-height-input');
  const wInput = document.getElementById('profile-weight-input');
  if (hInput) window.mainAvatarHeight = parseInt(hInput.value, 10) || 155;
  if (wInput) window.mainAvatarWeight = parseInt(wInput.value, 10) || 45;
  drawMainFittingAvatar();
}

// 2. 얼굴 크기 조절 (+/- 및 슬라이더)
function adjustFaceScale(delta) {
  window.faceScale = Math.max(0.5, Math.min(2.2, window.faceScale + delta));
  syncFaceScaleUI();
  drawMainFittingAvatar();
}

function onFaceScaleSliderChange(val) {
  window.faceScale = parseInt(val, 10) / 100.0;
  syncFaceScaleUI();
  drawMainFittingAvatar();
}

function resetFaceScale() {
  window.faceScale = 1.0;
  syncFaceScaleUI();
  drawMainFittingAvatar();
  if (typeof showToast === 'function') showToast('🔄 얼굴 크기가 100% 기본값으로 리셋되었습니다.', 'info');
}

function syncFaceScaleUI() {
  const badge = document.getElementById('face-scale-percent-badge');
  const slider = document.getElementById('face-scale-slider');
  const pct = Math.round(window.faceScale * 100);
  if (badge) badge.innerText = `${pct}%`;
  if (slider) slider.value = pct;
}

// 3. 얼굴 위치 영점 미세조절 (dx, dy)
function adjustFaceOffset(dx, dy) {
  window.faceOffsetX = Math.max(-60, Math.min(60, window.faceOffsetX + dx));
  window.faceOffsetY = Math.max(-60, Math.min(60, window.faceOffsetY + dy));
  drawMainFittingAvatar();
}

function resetFaceOffset() {
  window.faceOffsetX = 0;
  window.faceOffsetY = 0;
  drawMainFittingAvatar();
}

// 4. 10벌 시그니처 의상 착장 변경
function applyWardrobeOutfit(outfitNum) {
  window.currentWardrobeNum = outfitNum;

  const outfitsMeta = {
    1: { name: '🌸 [1번] K-하이틴 핑크 가디건 & 플리츠 스커트', top: '#f43f5e', bottom: '#3b82f6', style: 'pleats_skirt' },
    2: { name: '🎀 [2번] 청량 아이돌 데님 자켓 & 화이트 원피스', top: '#0284c7', bottom: '#ffffff', style: 'onepiece' },
    3: { name: '🎓 [3번] 명문 프레피 블레이저 & 체크 리본', top: '#1e1b4b', bottom: '#1e293b', style: 'preppy' },
    4: { name: '👕 [4번] 시티보이 오버핏 후드 & 스트릿 카고', top: '#059669', bottom: '#334155', style: 'hoodie' },
    5: { name: '🧥 [5번] 베이지 트렌치 롱코트', top: '#d97706', bottom: '#1e293b', style: 'trench' },
    6: { name: '👔 [6번] 청담 테일러드 VIP 로열 네이비 수트', top: '#0f172a', bottom: '#0f172a', style: 'vip_suit' },
    7: { name: '✨ [7번] 캐시미어 웜골드 니트 & 슬랙스', top: '#ca8a04', bottom: '#f8fafc', style: 'knit_slacks' },
    8: { name: '🔮 [8번] 2035 글로벌 CEO 네오-퍼플 수트', top: '#581c87', bottom: '#020617', style: 'ceo_suit' },
    9: { name: '🚀 [9번] 우주 AI 과학자 사이버 테크웨어', top: '#0891b2', bottom: '#0f172a', style: 'techwear' },
    10: { name: '👑 [10번] 로열 골드 갈라 파티 드레스 & 턱시도', top: '#eab308', bottom: '#1c1917', style: 'gala' }
  };

  const meta = outfitsMeta[outfitNum] || outfitsMeta[1];

  // 카드 active 스타일링
  for (let i = 1; i <= 10; i++) {
    const card = document.getElementById(`outfit-card-${i}`);
    if (card) {
      if (i === outfitNum) {
        card.className = 'p-2.5 rounded-xl bg-gradient-to-br from-pink-950/60 to-purple-950/60 border-2 border-pink-400 text-left transition flex flex-col justify-between gap-1 shadow-lg scale-[1.02] active:scale-95';
      } else {
        card.className = 'p-2.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-slate-700 text-left transition flex flex-col justify-between gap-1 shadow-sm active:scale-95';
      }
    }
  }

  const badge = document.getElementById('current-outfit-badge');
  if (badge) badge.innerText = `${meta.name.split(']')[0]}] 착장 중`;

  drawMainFittingAvatar();

  if (typeof showToast === 'function') {
    showToast(`👗 [의상 체인지]: ${meta.name} 착장 완료!`, 'success');
  }
}

// 5. 모바일 두 손가락 핀치 줌 (Pinch Zoom) 이벤트
function initPinchZoomInteraction(canvasId) {
  const canvas = document.getElementById(canvasId || 'main-fitting-canvas');
  if (!canvas || canvas.dataset.pinchZoomInitialized) return;
  canvas.dataset.pinchZoomInitialized = 'true';

  let initialPinchDist = 0;
  let initialFaceScale = 1.0;

  canvas.addEventListener('touchstart', (e) => {
    if (e.touches.length === 2) {
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      initialPinchDist = Math.hypot(dx, dy);
      initialFaceScale = window.faceScale;
    }
  }, { passive: true });

  canvas.addEventListener('touchmove', (e) => {
    if (e.touches.length === 2 && initialPinchDist > 0) {
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      const currentDist = Math.hypot(dx, dy);
      const ratio = currentDist / initialPinchDist;

      window.faceScale = Math.max(0.5, Math.min(2.2, initialFaceScale * ratio));
      syncFaceScaleUI();
      drawMainFittingAvatar();
    }
  }, { passive: true });

  canvas.addEventListener('touchend', (e) => {
    if (e.touches.length < 2) {
      initialPinchDist = 0;
    }
  });
}

// 6. 3D 아바타 & 런웨이 투영 렌더러 전면 고도화
function drawMainFittingAvatar() {
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  const cx = w / 2;

  ctx.clearRect(0, 0, w, h);

  // 1. 배경
  const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
  bgGrad.addColorStop(0, '#060913');
  bgGrad.addColorStop(0.5, '#0b1329');
  bgGrad.addColorStop(1, '#020617');
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, w, h);

  // 2. 바닥 스포트라이트
  const tiltYOffset = (window.pitchTilt || 0) * 1.5;
  const floorY = h - 45 + tiltYOffset;
  const spotRadiusX = 145;
  const spotRadiusY = Math.max(16, 26 - (window.pitchTilt || 0) * 0.35);

  ctx.save();
  const floorGrad = ctx.createRadialGradient(cx, floorY, 15, cx, floorY, spotRadiusX);
  floorGrad.addColorStop(0, window.targetGender === 'female' ? 'rgba(244, 63, 94, 0.45)' : 'rgba(59, 130, 246, 0.45)');
  floorGrad.addColorStop(0.6, 'rgba(168, 85, 247, 0.2)');
  floorGrad.addColorStop(1, 'transparent');
  ctx.fillStyle = floorGrad;
  ctx.beginPath();
  ctx.ellipse(cx, floorY, spotRadiusX, spotRadiusY, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // 3. 각도 삼각함수
  const rad = ((window.yawAngle || 0) * Math.PI) / 180;
  const cosYaw = Math.cos(rad);
  const sinYaw = Math.sin(rad);
  const isBackView = cosYaw < -0.15;

  // 4. 인체 비율 및 머리 위치 (얼굴 상단 잘림 방지: headY = 145px로 충분히 내림!)
  const scale = (window.mainAvatarHeight / 165);
  const widthFactor = (window.mainAvatarWeight / 55);
  const headY = 145 + (window.pitchTilt || 0) * 0.4;
  const headRadius = 38 * scale;

  // 어깨 너비: 여성/소녀 모드일 땐 슬림하고 둥근 숄더, 남성 모드일 땐 당당한 테일러드 숄더
  const baseShoulderW = (window.targetGender === 'female' ? 44 : 56) * scale * widthFactor;
  const projShoulderW = baseShoulderW * (0.35 + 0.65 * Math.abs(cosYaw));
  const torsoH = (window.targetGender === 'female' ? 135 : 150) * scale;
  const legH = (window.targetGender === 'female' ? 190 : 205) * scale;

  // 10벌 의상 메타 색상
  const outfitsColors = {
    1: { top: '#f43f5e', bottom: '#3b82f6', accent: '#fbbf24', style: 'skirt' },
    2: { top: '#0284c7', bottom: '#ffffff', accent: '#f43f5e', style: 'onepiece' },
    3: { top: '#1e1b4b', bottom: '#1e293b', accent: '#ef4444', style: 'preppy' },
    4: { top: '#059669', bottom: '#334155', accent: '#10b981', style: 'hoodie' },
    5: { top: '#b45309', bottom: '#1e293b', accent: '#d97706', style: 'trench' },
    6: { top: '#0f172a', bottom: '#0f172a', accent: '#38bdf8', style: 'suit' },
    7: { top: '#ca8a04', bottom: '#f8fafc', accent: '#fbbf24', style: 'knit' },
    8: { top: '#581c87', bottom: '#020617', accent: '#c084fc', style: 'suit' },
    9: { top: '#0891b2', bottom: '#0f172a', accent: '#22d3ee', style: 'tech' },
    10: { top: '#eab308', bottom: '#1c1917', accent: '#fde047', style: 'gala' }
  };

  const outfit = outfitsColors[window.currentWardrobeNum || 1];

  // 5. 뒷머리 헤어 배경 (소녀/여성 모드일 때 긴 머리 실루엣)
  if (window.targetGender === 'female' && !isBackView) {
    ctx.save();
    ctx.fillStyle = '#1e1b18';
    ctx.beginPath();
    ctx.roundRect(cx - headRadius * 1.1, headY - 10, headRadius * 2.2, torsoH * 0.9, [20, 20, 10, 10]);
    ctx.fill();
    ctx.restore();
  }

  // 6. 하체 (스커트 vs 팬츠 vs 롱드레스)
  ctx.save();
  const legShift = sinYaw * 10;
  const legWidth = (18 * widthFactor) * (0.55 + 0.45 * Math.abs(cosYaw));

  if (outfit.style === 'skirt' || (window.targetGender === 'female' && (outfit.style === 'preppy' || outfit.style === 'onepiece'))) {
    // 🌸 플리츠 A라인 스커트 실루엣!
    ctx.fillStyle = outfit.bottom;
    const skirtTopW = projShoulderW * 0.75;
    const skirtBottomW = projShoulderW * 1.35;
    const skirtH = 75 * scale;
    const skirtY = headY + headRadius + torsoH - 15;

    ctx.beginPath();
    ctx.moveTo(cx - skirtTopW, skirtY);
    ctx.lineTo(cx + skirtTopW, skirtY);
    ctx.lineTo(cx + skirtBottomW, skirtY + skirtH);
    ctx.lineTo(cx - skirtBottomW, skirtY + skirtH);
    ctx.closePath();
    ctx.fill();

    // 플리츠 주름선
    ctx.strokeStyle = 'rgba(0,0,0,0.2)';
    ctx.lineWidth = 1.2;
    for (let f = -skirtBottomW * 0.8; f <= skirtBottomW * 0.8; f += 12) {
      ctx.beginPath();
      ctx.moveTo(cx + f * 0.5, skirtY);
      ctx.lineTo(cx + f, skirtY + skirtH);
      ctx.stroke();
    }

    // 스커트 아래 스타킹/다리
    ctx.fillStyle = '#fce7d8';
    ctx.fillRect(cx - legWidth * 1.8 + legShift * 0.3, skirtY + skirtH, legWidth, legH - skirtH);
    ctx.fillRect(cx + legWidth * 0.8 - legShift * 0.3, skirtY + skirtH, legWidth, legH - skirtH);

  } else if (outfit.style === 'gala' && window.targetGender === 'female') {
    // 👑 로열 골드 갈라 롱 드레스 실루엣!
    ctx.fillStyle = outfit.top;
    const dressTopW = projShoulderW * 0.7;
    const dressBottomW = projShoulderW * 1.6;
    const dressH = legH + 10;
    const dressY = headY + headRadius + torsoH - 20;

    ctx.beginPath();
    ctx.moveTo(cx - dressTopW, dressY);
    ctx.lineTo(cx + dressTopW, dressY);
    ctx.lineTo(cx + dressBottomW, dressY + dressH);
    ctx.lineTo(cx - dressBottomW, dressY + dressH);
    ctx.closePath();
    ctx.fill();

  } else {
    // 👖 테일러드 팬츠 / 스트릿 카고 팬츠
    ctx.fillStyle = outfit.bottom;
    ctx.beginPath();
    ctx.roundRect(cx - (projShoulderW * 0.42) + legShift * 0.5, headY + headRadius + torsoH - 10, legWidth, legH, [4, 4, 8, 8]);
    ctx.roundRect(cx + (projShoulderW * 0.42) - legWidth - legShift * 0.5, headY + headRadius + torsoH - 10, legWidth, legH, [4, 4, 8, 8]);
    ctx.fill();
  }

  // 슈즈
  ctx.fillStyle = '#0f172a';
  ctx.beginPath();
  ctx.roundRect(cx - projShoulderW * 0.45 + legShift * 0.5, headY + headRadius + torsoH + legH - 10, legWidth + 6, 12, [4, 8, 4, 4]);
  ctx.roundRect(cx + projShoulderW * 0.45 - legWidth - 6 - legShift * 0.5, headY + headRadius + torsoH + legH - 10, legWidth + 6, 12, [4, 8, 4, 4]);
  ctx.fill();
  ctx.restore();

  // 7. 상체 (가디건 / 블레이저 / 자켓 / 코트)
  ctx.save();
  ctx.fillStyle = outfit.top;

  // 허리 잘록 쉐이핑 (여성 모드) vs 탄탄한 수트 (남성 모드)
  if (window.targetGender === 'female') {
    ctx.beginPath();
    ctx.moveTo(cx - projShoulderW, headY + headRadius - 4);
    ctx.lineTo(cx + projShoulderW, headY + headRadius - 4);
    ctx.lineTo(cx + projShoulderW * 0.8, headY + headRadius + torsoH * 0.6);
    ctx.lineTo(cx + projShoulderW * 0.9, headY + headRadius + torsoH);
    ctx.lineTo(cx - projShoulderW * 0.9, headY + headRadius + torsoH);
    ctx.lineTo(cx - projShoulderW * 0.8, headY + headRadius + torsoH * 0.6);
    ctx.closePath();
    ctx.fill();
  } else {
    ctx.beginPath();
    ctx.roundRect(cx - projShoulderW, headY + headRadius - 4, projShoulderW * 2, torsoH, [8, 8, 4, 4]);
    ctx.fill();
  }

  // 이너 & V존 & 리본/타이
  if (!isBackView) {
    const vOffset = sinYaw * (projShoulderW * 0.4);
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.moveTo(cx + vOffset - 10 * Math.abs(cosYaw), headY + headRadius - 2);
    ctx.lineTo(cx + vOffset + 10 * Math.abs(cosYaw), headY + headRadius - 2);
    ctx.lineTo(cx + vOffset, headY + headRadius + 38);
    ctx.closePath();
    ctx.fill();

    // 포인트 리본 / 타이
    ctx.fillStyle = outfit.accent;
    ctx.beginPath();
    ctx.arc(cx + vOffset, headY + headRadius + 10, 5, 0, Math.PI * 2);
    ctx.fill();
  } else {
    // 뒷모습 등판 절개선
    ctx.strokeStyle = 'rgba(255,255,255,0.2)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(cx, headY + headRadius + 2);
    ctx.lineTo(cx, headY + headRadius + torsoH - 4);
    ctx.stroke();
  }

  // 양팔
  const armW = 14 * widthFactor;
  ctx.fillStyle = outfit.top;
  ctx.beginPath();
  ctx.roundRect(cx - projShoulderW - armW * 0.6, headY + headRadius, armW, torsoH * 0.85, [6, 6, 6, 6]);
  ctx.roundRect(cx + projShoulderW - armW * 0.4, headY + headRadius, armW, torsoH * 0.85, [6, 6, 6, 6]);
  ctx.fill();
  ctx.restore();

  // 8. 목 & 머리 & 얼굴 (확대/축소 및 영점 오프셋 100% 적용!)
  const faceCenterX = cx + sinYaw * (headRadius * 0.28) + (window.faceOffsetX || 0);
  const faceCenterY = headY + (window.faceOffsetY || 0);
  const curHeadRadius = headRadius * (window.faceScale || 1.0);

  // 목
  ctx.fillStyle = window.mainSkinTone || '#fce7d8';
  ctx.fillRect(cx - 7, headY + headRadius - 8, 14, 16);

  if (!isBackView) {
    if (window.userFaceImage && window.userFaceImage.complete) {
      // 🌟 본인 실제 얼굴 사진 원형 클리핑 합성! (확대비율 & 영점 완벽 반영)
      ctx.save();
      ctx.beginPath();
      ctx.arc(faceCenterX, faceCenterY, curHeadRadius * 0.94, 0, Math.PI * 2);
      ctx.clip();
      ctx.drawImage(
        window.userFaceImage,
        faceCenterX - curHeadRadius * 0.94,
        faceCenterY - curHeadRadius * 0.94,
        curHeadRadius * 1.88,
        curHeadRadius * 1.88
      );
      ctx.restore();

      // 골드 VIP 네온 테두리 링
      ctx.save();
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2.5;
      ctx.shadowColor = '#fbbf24';
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.arc(faceCenterX, faceCenterY, curHeadRadius * 0.94, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    } else {
      // 또렷한 패션 일러스트 이목구비
      if (typeof drawDetailedIllustrationFace === 'function') {
        drawDetailedIllustrationFace(ctx, faceCenterX, faceCenterY, curHeadRadius, sinYaw);
      }
    }
  } else {
    // 뒷모습 뒤통수 헤어
    ctx.save();
    const hairGrad = ctx.createRadialGradient(faceCenterX, faceCenterY - 10, 10, faceCenterX, faceCenterY, curHeadRadius * 1.05);
    hairGrad.addColorStop(0, '#2d241e');
    hairGrad.addColorStop(0.8, '#18120e');
    hairGrad.addColorStop(1, '#0c0907');
    ctx.fillStyle = hairGrad;
    ctx.beginPath();
    ctx.arc(faceCenterX, faceCenterY, curHeadRadius * 1.02, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  // 9. 하단 각도 배지 갱신
  updateAngleDisplayBadge();
}

// 각도 배지 업데이트
function updateAngleDisplayBadge() {
  const badge = document.getElementById('main-angle-display-badge');
  if (!badge) return;
  const yaw = Math.round(window.yawAngle || 0);
  const pitch = Math.round(window.pitchTilt || 0);
  badge.innerHTML = `🔄 3D 360° 터치 회전 (좌우: ${yaw}° · 상하: ${pitch >= 0 ? '+' : ''}${pitch}°)`;
}

// 페이지 로드 시 핀치 줌 & 프리셋 초기화
document.addEventListener('DOMContentLoaded', () => {
  initPinchZoomInteraction('main-fitting-canvas');
  initPinchZoomInteraction('app-fitting-canvas');
});
setTimeout(() => {
  initPinchZoomInteraction('main-fitting-canvas');
  initPinchZoomInteraction('app-fitting-canvas');
}, 300);
"""

def patch_index_html():
    print("[🛠️ index.html v3.9 Wardrobe-Pro 패치 시작]")
    with open("dashboard/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. 버전 배지 업그레이드: v3.9 Wardrobe-Pro
    html = re.sub(r'id="ota-version-text"[^>]*>.*?</span>', 'id="ota-version-text" class="font-bold text-amber-300">v3.9 Wardrobe-Pro</span>', html)

    # 2. 캔버스 뷰포트 내부에서 이전 겹쳐있던 플로팅 HUD(<div class="absolute top-2.5 ...) 완전 제거!
    # 캔버스 태그의 </canvas></canvas> 오타 정상화
    html = html.replace('</canvas></canvas>', '</canvas>')

    # 캔버스 컨테이너 시작점 찾기
    canvas_wrap_pattern = r'<!-- 👑 3D 터치 회전 & 글래스모피즘 HUD 풀뷰 캔버스 뷰포트 -->\s*<div[^>]*class="[^"]*aspect-\[3/4\][^"]*".*?<canvas[^>]*id="main-fitting-canvas"[^>]*></canvas>'
    m = re.search(canvas_wrap_pattern, html, re.DOTALL)
    if m:
        # 캔버스 내부의 absolute top 플로팅 HUD 제거
        idx_after_canvas = m.end()
        # find the next HUD overlay
        hud_in_canvas = re.search(r'\s*<!-- 🔮 \[Glassmorphism HUD: 상단 플로팅 오버레이\].*?</div>\s*</div>\s*</div>', html[idx_after_canvas:], re.DOTALL)
        if hud_in_canvas:
            html = html[:idx_after_canvas] + html[idx_after_canvas + hud_in_canvas.end():]
            print("  ✅ 캔버스 내부 얼굴 가림 오버레이 HUD 100% 제거 완료!")

    # 3. 캔버스 컨테이너 바로 위에 TOP_CONTROLS_AND_PRESET_BAR 주입 (중복 방지)
    if "누가 입어보나요?" not in html:
        idx_canvas_sec = html.find('<!-- 👑 3D 터치 회전 & 글래스모피즘 HUD 풀뷰 캔버스 뷰포트 -->')
        if idx_canvas_sec != -1:
            html = html[:idx_canvas_sec] + TOP_CONTROLS_AND_PRESET_BAR + "\n\n" + html[idx_canvas_sec:]
            print("  ✅ 캔버스 상단에 독립 컨트롤 헤더 및 4인 체형 세팅 바 주입 완료!")

    # 4. 캔버스 아래에 BOTTOM_FACE_AND_WARDROBE_SHOWROOM 주입
    if "나만의 꿈의 옷장함 (10벌 코디 쇼룸)" not in html:
        idx_next_box = html.find('id="post-photo-next-step-box"')
        if idx_next_box != -1:
            # post-photo-next-step-box 바로 뒤에 주입
            idx_box_close = html.find('</div>', idx_next_box)
            idx_box_final = html.find('</div>', idx_box_close + 6)
            if idx_box_final != -1:
                html = html[:idx_box_final+6] + "\n\n" + BOTTOM_FACE_AND_WARDROBE_SHOWROOM + "\n\n" + html[idx_box_final+6:]
                print("  ✅ 얼굴 조절 바 및 10벌 옷장 쇼룸 주입 완료!")

    # 5. V39_JS_ENGINE 주입
    if "👗 [Omni-Nexus v3.9 Wardrobe-Pro]" not in html:
        idx_script_end = html.rfind("</script>")
        if idx_script_end != -1:
            html = html[:idx_script_end] + "\n\n" + V39_JS_ENGINE + "\n" + html[idx_script_end:]
            print("  ✅ V39_JS_ENGINE 주입 완료!")

    with open("dashboard/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  ✅ dashboard/index.html v3.9 저장 완료!")

def patch_dream_closet_app():
    print("[🛠️ dream_closet_future_master_app.html v3.9 Wardrobe-Pro 패치 시작]")
    with open("dashboard/dream_closet_future_master_app.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = re.sub(r'id="ota-version-text"[^>]*>.*?</span>', 'id="ota-version-text" class="font-bold text-amber-300">v3.9 Wardrobe-Pro</span>', html)
    html = html.replace('</canvas></canvas>', '</canvas>')

    if "누가 입어보나요?" not in html:
        idx_canvas = html.find('id="app-fitting-canvas"')
        if idx_canvas != -1:
            idx_prev_div = html.rfind('<div', 0, idx_canvas)
            html = html[:idx_prev_div] + TOP_CONTROLS_AND_PRESET_BAR + "\n\n" + html[idx_prev_div:]
            print("  ✅ dream_closet 상단에 독립 컨트롤 헤더 및 4인 체형 세팅 바 주입 완료!")

    if "나만의 꿈의 옷장함 (10벌 코디 쇼룸)" not in html:
        idx_next_box = html.find('id="post-photo-next-step-box"')
        if idx_next_box != -1:
            idx_box_close = html.find('</div>', idx_next_box)
            idx_box_final = html.find('</div>', idx_box_close + 6)
            if idx_box_final != -1:
                html = html[:idx_box_final+6] + "\n\n" + BOTTOM_FACE_AND_WARDROBE_SHOWROOM + "\n\n" + html[idx_box_final+6:]
                print("  ✅ dream_closet에 얼굴 조절 바 및 10벌 옷장 쇼룸 주입 완료!")

    if "👗 [Omni-Nexus v3.9 Wardrobe-Pro]" not in html:
        idx_script_end = html.rfind("</script>")
        if idx_script_end != -1:
            html = html[:idx_script_end] + "\n\n" + V39_JS_ENGINE + "\n" + html[idx_script_end:]
            print("  ✅ dream_closet에 V39_JS_ENGINE 주입 완료!")

    with open("dashboard/dream_closet_future_master_app.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  ✅ dream_closet_future_master_app.html v3.9 저장 완료!")

def main():
    patch_index_html()
    patch_dream_closet_app()
    print("🎉 v3.9 Wardrobe-Pro 패치 100% 완료!")

if __name__ == "__main__":
    main()

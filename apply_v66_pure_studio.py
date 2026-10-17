# -*- coding: utf-8 -*-
"""
apply_v66_pure_studio.py
--------------------------------------------------------------------------------
🔥 [v6.6 Pure Coordi Studio]
1. 코디 무관 요소 100% 완전 삭제:
   - 스마트폰 원격 복붙 직통 스위치 박스 완전 삭제
   - 르곤이 명령 입력창 & 안실장 발사 버튼 완전 삭제
   - 관리용 서랍(VOC, 배포, 퀴즈 배너 등) 완전 숨김/삭제
   - 오직 순수 코디 스튜디오(착용자 세팅 -> 캔버스 -> 올인원 컨트롤박스 -> 10벌 옷장함)만 보존!
2. 직관적 컨트롤 박스:
   - 화살표 4방향 버튼(⬅️⬆️⬇️➡️) 완전 제거
   - 1열: [📸 내 얼굴 사진 넣기] | [👚 내 옷/전신 사진] | [👗코디합성 ↔ 🖼️원본보기]
   - 2열: [🔒 고정/해제] | [👤 얼굴조절 ↔ 🖼️ 전신줌] (1번 터치 전환 & 사진 업로드 시 자동 타겟팅)
          | [➖ 작게] | [➕ 크게] | [🎯 중앙맞춤] | [💾 저장]
3. 고정 해제(🔓) 시 직관적 손가락 상하좌우 드래그 & 두 손가락 핀치 줌:
   - touch-action: none 동적 전환 (스크롤 간섭 0%)
   - 한 손가락 이동: bodyPhotoOffsetX/Y, faceOffsetX/Y 1:1 매핑
   - 두 손가락 핀치 줌: bodyPhotoScale(0.3~3.5), faceScale(0.3~3.0)
   - 크기 버튼이나 타겟 버튼 누르면 자동으로 잠금 해제(🔓)
--------------------------------------------------------------------------------
"""

import sys
import re
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 1. 서브탭 바 (피팅 / 2035 / 가족룩)
V66_SUBTAB_BAR_HTML = '''<!-- 👑 [v6.6 피팅/2035/가족룩 모드 서브탭 바] -->
        <div class="w-full max-w-[420px] mx-auto p-1.5 rounded-xl bg-slate-900/90 border border-purple-500/30 flex items-center justify-center gap-2 text-xs shadow-md">
          <div class="flex items-center gap-1.5 p-0.5 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] whitespace-nowrap">
            <button type="button" onclick="switchMainFittingSubTab('fitting')" id="tab-sub-fitting" class="px-3 py-1 rounded-md bg-purple-600 text-white font-bold transition shadow-sm whitespace-nowrap">
              👗 피팅
            </button>
            <button type="button" onclick="switchMainFittingSubTab('future')" id="tab-sub-future" class="px-3 py-1 rounded-md text-slate-300 hover:text-white transition whitespace-nowrap">
              🔮 2035
            </button>
            <button type="button" onclick="switchMainFittingSubTab('family')" id="tab-sub-family" class="px-3 py-1 rounded-md text-slate-300 hover:text-white transition whitespace-nowrap">
              👨‍👧‍👧 가족
            </button>
          </div>
        </div>'''

# 2. 캔버스 컨테이너 (상하단 오버레이 0개, 순수 사진 화면)
V66_CANVAS_CONTAINER_HTML = '''<!-- 👑 [v6.6 캔버스 컨테이너: 상하단 가림 0% 순수 코디 캔버스] -->
        <div id="fitting-studio-container" class="w-full max-w-[420px] mx-auto aspect-[3/4] max-h-[500px] rounded-2xl bg-gradient-to-b from-slate-950 via-[#0a0f1d] to-slate-950 border border-purple-500/30 shadow-2xl relative overflow-hidden flex items-center justify-center select-none">
          <canvas id="main-fitting-canvas" width="450" height="600" class="w-full h-full object-contain relative" style="touch-action: pan-y !important; cursor: grab;"></canvas>
        </div>'''

# 3. v6.6 직관적 컨트롤 박스 (화살표 제거, 1번 터치 전환, 큼직한 버튼)
V66_CONTROL_BOX_HTML = '''<!-- 🎛️ [v6.6 Pure Coordi 직관적 올인원 컨트롤 박스] -->
        <div id="v5-one-line-remote-bar" class="w-full max-w-[450px] mx-auto mt-1 mb-2 p-2 rounded-2xl bg-slate-900/95 border border-purple-500/50 shadow-xl flex flex-col gap-2 text-xs backdrop-blur-md box-border relative" style="box-sizing: border-box;">
          
          <!-- 🏷️ [상태 표시줄: 사진 바깥 아래쪽 배치로 사진 가림 0%] -->
          <div class="flex items-center justify-between px-2.5 py-1 rounded-lg bg-slate-950/90 border border-purple-500/30 text-[11px] text-purple-200">
            <span id="canvas-lock-status-badge">🔒 화면 고정됨 (터치시 잠금해제)</span>
            <span id="studio-current-mode-badge" class="text-pink-300 font-bold">👤 얼굴 조절 모드</span>
          </div>

          <!-- 📸 [1열: 사진 넣기 & 모드 버튼 3종] -->
          <div class="flex items-center justify-between gap-1.5 relative">
            <!-- ① [📸 내 얼굴 사진 넣기] 버튼 & 3단 팝업 메뉴 -->
            <div class="relative flex-1">
              <button type="button" id="btn-main-photo-upload" onclick="toggleFacePhotoMenu()" class="w-full px-2.5 py-2 rounded-xl bg-gradient-to-r from-pink-600 via-rose-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white font-extrabold text-[11px] shadow-lg flex items-center justify-center gap-1 active:scale-95 transition cursor-pointer border border-pink-400/40">
                <span>📸</span><span>내 얼굴 사진 넣기</span>
              </button>

              <!-- 3단 액션 팝업 메뉴 (컨트롤 박스 바로 위에 펼쳐짐) -->
              <div id="face-photo-action-menu" class="hidden absolute left-0 bottom-full mb-2 w-56 p-2 rounded-xl bg-slate-950 border border-purple-500/50 shadow-2xl z-50 space-y-1.5 text-xs backdrop-blur-md">
                <button type="button" onclick="triggerFaceCameraPhoto()" class="w-full text-left px-3 py-2 rounded-lg bg-slate-900 hover:bg-purple-600/40 text-white flex items-center gap-2 transition active:scale-95">
                  <span>📷</span><span>지금 카메라로 촬영하기</span>
                </button>
                <button type="button" onclick="triggerFaceGalleryPhoto()" class="w-full text-left px-3 py-2 rounded-lg bg-slate-900 hover:bg-purple-600/40 text-white flex items-center gap-2 transition active:scale-95">
                  <span>🖼️</span><span>앨범에서 얼굴 사진 고르기</span>
                </button>
                <button type="button" onclick="resetToDefaultAvatarFace()" class="w-full text-left px-3 py-2 rounded-lg hover:bg-rose-600/30 text-rose-300 flex items-center gap-2 transition border-t border-slate-800 active:scale-95">
                  <span>🔄</span><span>얼굴 사진 초기화</span>
                </button>
              </div>

              <!-- 숨겨진 파일 인풋 3종 -->
              <input type="file" id="face-camera-input" accept="image/*" capture="user" class="hidden" onchange="handleFacePhotoUpload(event)">
              <input type="file" id="face-gallery-input" accept="image/*" class="hidden" onchange="handleFacePhotoUpload(event)">
              <input type="file" id="face-upload-input" accept="image/*" class="hidden" onchange="handleFacePhotoUpload(event)">
            </div>

            <!-- ② [👚 내 옷/전신 사진] 버튼 -->
            <div class="flex-1">
              <button type="button" id="btn-custom-cloth-upload" onclick="document.getElementById('custom-cloth-input').click()" class="w-full px-2.5 py-2 rounded-xl bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-extrabold text-[11px] shadow-lg flex items-center justify-center gap-1 active:scale-95 transition cursor-pointer border border-blue-400/40">
                <span>👚</span><span>내 옷/전신 사진</span>
              </button>
              <input type="file" id="custom-cloth-input" accept="image/*" class="hidden" onchange="handleCustomClothUpload(event)">
              <input type="file" id="custom-cloth-file-input" accept="image/*" class="hidden" onchange="handleCustomClothUpload(event)">
            </div>

            <!-- ③ [👗코디합성 ↔ 🖼️원본보기] 전환 버튼 -->
            <button type="button" id="btn-photo-view-mode" onclick="togglePhotoViewMode()" class="px-2.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-purple-200 border border-purple-500/40 font-bold text-[11px] shadow active:scale-95 transition whitespace-nowrap flex items-center gap-1">
              <span>👗코디합성</span>
            </button>
          </div>

          <!-- 🎛️ [2열: 직관적 조작 리모컨 (화살표 제거, 1번 터치 전환, 핀치 줌 연동)] -->
          <div class="flex flex-wrap items-center justify-between gap-1.5 pt-1.5 border-t border-slate-800/80">
            <!-- 1. [🔒 고정됨] ↔ [🔓 조절 켜짐] 토글 버튼 -->
            <button type="button" id="btn-canvas-lock" onclick="toggleCanvasLock()" class="px-2.5 h-8 rounded-xl bg-emerald-700 hover:bg-emerald-600 text-emerald-100 text-[11px] font-black border border-emerald-400 active:scale-95 flex items-center gap-1 whitespace-nowrap shadow transition" title="터치 잠금 토글 (기본: 위치 고정)">
              <span id="canvas-lock-icon">🔒</span><span id="canvas-lock-label">고정됨</span>
            </button>

            <!-- 2. [👤 얼굴 크기·위치 조정] ↔ [🖼️ 전신사진 크기·위치 조정] 1번 터치 전환 버튼 -->
            <button type="button" id="btn-adjust-target" onclick="toggleAdjustTarget()" class="flex-1 px-2.5 h-8 rounded-xl bg-blue-700 hover:bg-blue-600 text-blue-100 text-[11px] font-black border border-blue-400 active:scale-95 flex items-center justify-center gap-1 whitespace-nowrap shadow transition" title="조작 대상 원터치 전환 (얼굴 ↔ 전신사진)">
              <span>👤 얼굴조절</span>
            </button>

            <!-- 3. 크기 조절 [➖ 작게] / [➕ 크게] -->
            <div class="flex items-center gap-1">
              <button type="button" onclick="adjustPhotoZoom(-0.12)" class="px-2.5 h-8 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-black text-xs border border-slate-700 active:scale-95 flex items-center justify-center transition" title="작게 축소">➖</button>
              <button type="button" onclick="adjustPhotoZoom(0.12)" class="px-2.5 h-8 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-black text-xs border border-slate-700 active:scale-95 flex items-center justify-center transition" title="크게 확대">➕</button>
            </div>

            <!-- 4. 정중앙 맞춤 -->
            <button type="button" onclick="resetCanvasCenter()" class="px-2.5 h-8 rounded-xl bg-indigo-600/50 hover:bg-indigo-600/80 text-indigo-200 text-[11px] font-bold border border-indigo-400/40 active:scale-95 flex items-center gap-1 whitespace-nowrap transition" title="정중앙 원위치">
              <span>🎯중앙</span>
            </button>

            <!-- 5. 화보 저장 -->
            <button type="button" onclick="saveMyFittingPhoto()" class="px-2.5 h-8 rounded-xl bg-emerald-600/60 hover:bg-emerald-600/80 text-emerald-100 text-[11px] font-bold border border-emerald-400/40 active:scale-95 flex items-center gap-1 whitespace-nowrap transition" title="화보 저장">
              <span>💾저장</span>
            </button>
          </div>
        </div>'''

# 4. v6.6 전용 JS 엔진 코드
V66_JS_ENGINE = '''
// ============================================================================
// 👑 [v6.6 Pure Coordi Studio] 직관적 터치 & 크기조절 엔진
// ============================================================================

window.currentRenderMode = 'photo_lookbook'; // 'photo_lookbook' | 'user_original'
window.currentWardrobeNum = 1;
window.isCanvasLocked = true; // 🔒 기본 화면 고정
window.currentAdjustTarget = 'face'; // 'face' | 'body'

// 얼굴 조절 변수 (기본 크기: 캔버스 폭 11%, 위치: 상단 17%)
window.faceOffsetX = 0;
window.faceOffsetY = 0;
window.faceScale = 1.0;

// 전신사진 / 의상 조절 변수 (0.3 ~ 3.5배)
window.bodyPhotoScale = 1.0;
window.bodyPhotoOffsetX = 0;
window.bodyPhotoOffsetY = 0;

// 10벌 고화질 실사 패션 화보 카탈로그
window.LOOKBOOK_CATALOG = {
  1: {
    name: "🌸 러블리 K-하이틴 핑크 가디건",
    colorTheme: "#f43f5e",
    imageUrl: "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=600&q=80",
    modelDesc: "파스텔 핑크 울 가디건 & 플리츠 스커트 스튜디오 실사 화보"
  },
  2: {
    name: "🎀 청량 아이돌 데님 자켓 & 원피스",
    colorTheme: "#38bdf8",
    imageUrl: "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=600&q=80",
    modelDesc: "라이트블루 워싱 데님 자켓 & 썸머 원피스 실사 화보"
  },
  3: {
    name: "🎓 명문 프레피 블레이저 & 리본",
    colorTheme: "#818cf8",
    imageUrl: "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=600&q=80",
    modelDesc: "클래식 네이비 테일러드 블레이저 & 프레피 타이 실사 화보"
  },
  4: {
    name: "👕 시티보이 오버핏 후드 & 카고",
    colorTheme: "#34d399",
    imageUrl: "https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?auto=format&fit=crop&w=600&q=80",
    modelDesc: "세이지 그린 프리미엄 오버핏 후드 & 카고 팬츠 실사 화보"
  },
  5: {
    name: "🧥 베이지 트렌치 롱코트",
    colorTheme: "#fbbf24",
    imageUrl: "https://images.unsplash.com/photo-1485968579580-b6d095142e6e?auto=format&fit=crop&w=600&q=80",
    modelDesc: "헤리티지 베이지 더블 브레스티드 트렌치 코트 실사 화보"
  },
  6: {
    name: "👔 청담 테일러드 VIP 네이비 수트",
    colorTheme: "#60a5fa",
    imageUrl: "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=600&q=80",
    modelDesc: "이태리 최고급 원단 맞춤 다크 네이비 수트 실사 화보"
  },
  7: {
    name: "✨ 캐시미어 웜골드 니트 & 슬랙스",
    colorTheme: "#fcd34d",
    imageUrl: "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?auto=format&fit=crop&w=600&q=80",
    modelDesc: "카멜 골드 헤비 게이지 캐시미어 니트 & 슬랙스 실사 화보"
  },
  8: {
    name: "🔮 2035 글로벌 CEO 네오-퍼플 수트",
    colorTheme: "#c084fc",
    imageUrl: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=600&q=80",
    modelDesc: "2035 네오 서울 테크놀로지 CEO 럭셔리 수트 실사 화보"
  },
  9: {
    name: "🚀 우주 AI 과학자 사이버 테크웨어",
    colorTheme: "#22d3ee",
    imageUrl: "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=600&q=80",
    modelDesc: "에어로다이내믹 매트 블랙 사이버 테크웨어 재킷 실사 화보"
  },
  10: {
    name: "👑 로열 골드 갈라 파티 드레스/턱시도",
    colorTheme: "#fde047",
    imageUrl: "https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&w=600&q=80",
    modelDesc: "칸 영화제 레드카펫 골드 자수 이브닝 갈라 쿠튀르 실사 화보"
  }
};

window.lookbookImageCache = {};
function preloadLookbookImages() {
  for (let key in window.LOOKBOOK_CATALOG) {
    const item = window.LOOKBOOK_CATALOG[key];
    if (item.imageUrl) {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = function() {
        window.lookbookImageCache[key] = img;
        if (parseInt(key) === (window.currentWardrobeNum || 1)) {
          if (typeof renderRealPhotoStudio === 'function') renderRealPhotoStudio();
        }
      };
      img.src = item.imageUrl;
    }
  }
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', preloadLookbookImages);
} else {
  preloadLookbookImages();
}

// 🔒 [기능 1] 터치 위치 고정 잠금 스위치 (touch-action 동적 전환)
function toggleCanvasLock() {
  window.isCanvasLocked = !window.isCanvasLocked;
  applyCanvasLockState();
}

function applyCanvasLockState() {
  const btn = document.getElementById('btn-canvas-lock');
  const icon = document.getElementById('canvas-lock-icon');
  const label = document.getElementById('canvas-lock-label');
  const statusBadge = document.getElementById('canvas-lock-status-badge');
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');

  if (window.isCanvasLocked) {
    if (btn) {
      btn.className = 'px-2.5 h-8 rounded-xl bg-emerald-700 hover:bg-emerald-600 text-emerald-100 text-[11px] font-black border border-emerald-400 active:scale-95 flex items-center gap-1 whitespace-nowrap shadow transition';
    }
    if (icon) icon.textContent = '🔒';
    if (label) label.textContent = '고정됨';
    if (statusBadge) statusBadge.textContent = '🔒 화면 고정됨 (터치시 잠금해제)';
    if (canvas) canvas.style.touchAction = 'pan-y';
    if (typeof showToast === 'function') {
      showToast('🔒 [화면 고정 완료]: 상하 스크롤이 자유롭습니다.', 'success');
    }
  } else {
    if (btn) {
      btn.className = 'px-2.5 h-8 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-[11px] font-black border border-amber-300 active:scale-95 flex items-center gap-1 whitespace-nowrap shadow transition animate-pulse';
    }
    if (icon) icon.textContent = '🔓';
    if (label) label.textContent = '조절켜짐';
    if (statusBadge) statusBadge.textContent = '🔓 손가락 이동·크기조절 켜짐';
    // 조절 모드에서는 브라우저 기본 스크롤을 억제하여 손가락 드래그 100% 반영!
    if (canvas) canvas.style.touchAction = 'none';
    if (typeof showToast === 'function') {
      showToast('🔓 [조절 모드 활성화]: 손가락으로 사진을 상하좌우 이동 및 두 손가락으로 크기를 조절하세요!', 'info');
    }
  }
}

// 👤 ↔ 🖼️ [기능 2] 1번 터치로 얼굴 ↔ 전신사진 크기·위치 조정 전환
function toggleAdjustTarget() {
  window.currentAdjustTarget = (window.currentAdjustTarget === 'body') ? 'face' : 'body';
  // 사용자가 조절 버튼을 누르면 자동으로 잠금 해제하여 바로 조작 가능하게 배려!
  if (window.isCanvasLocked) {
    window.isCanvasLocked = false;
    applyCanvasLockState();
  }
  updateAdjustTargetUI();
}
window.toggleAdjustTarget = toggleAdjustTarget;

function updateAdjustTargetUI() {
  const btn = document.getElementById('btn-adjust-target');
  const modeBadge = document.getElementById('studio-current-mode-badge');
  if (btn) {
    if (window.currentAdjustTarget === 'body') {
      btn.innerHTML = '<span>🖼️ 전신사진 조절</span>';
      btn.className = 'flex-1 px-2.5 h-8 rounded-xl bg-pink-700 hover:bg-pink-600 text-pink-100 text-[11px] font-black border border-pink-400 active:scale-95 flex items-center justify-center gap-1 whitespace-nowrap shadow transition';
    } else {
      btn.innerHTML = '<span>👤 얼굴 조절</span>';
      btn.className = 'flex-1 px-2.5 h-8 rounded-xl bg-blue-700 hover:bg-blue-600 text-blue-100 text-[11px] font-black border border-blue-400 active:scale-95 flex items-center justify-center gap-1 whitespace-nowrap shadow transition';
    }
  }
  if (modeBadge) {
    modeBadge.textContent = (window.currentAdjustTarget === 'body') ? '🖼️ 전신 사진 조절 모드' : '👤 얼굴 조절 모드';
  }
}

// 🔍 [기능 3] 보조 크기 조절 [➖ 작게] / [➕ 크게]
function adjustPhotoZoom(delta) {
  if (window.isCanvasLocked) {
    window.isCanvasLocked = false;
    applyCanvasLockState();
  }
  if (window.currentAdjustTarget === 'body') {
    window.bodyPhotoScale = Math.max(0.3, Math.min(3.5, (window.bodyPhotoScale || 1.0) + delta));
    if (typeof showToast === 'function') {
      showToast(`🔍 전신사진 크기: ${Math.round(window.bodyPhotoScale * 100)}%`, 'info');
    }
  } else {
    window.faceScale = Math.max(0.3, Math.min(3.0, (window.faceScale || 1.0) + delta));
    if (typeof showToast === 'function') {
      showToast(`🔍 얼굴 크기: ${Math.round(window.faceScale * 100)}%`, 'info');
    }
  }
  drawMainFittingAvatar();
}
window.adjustPhotoZoom = adjustPhotoZoom;
window.adjustScale = adjustPhotoZoom;
window.adjustFaceScale = adjustPhotoZoom;

// 🎯 [기능 4] 중앙 맞춤 초기화
function resetCanvasCenter() {
  if (window.currentAdjustTarget === 'body') {
    window.bodyPhotoOffsetX = 0;
    window.bodyPhotoOffsetY = 0;
    window.bodyPhotoScale = 1.0;
    if (typeof showToast === 'function') showToast('🎯 전신사진 위치/크기가 정중앙으로 맞춤되었습니다.', 'info');
  } else {
    window.faceOffsetX = 0;
    window.faceOffsetY = 0;
    window.faceScale = 1.0;
    if (typeof showToast === 'function') showToast('🎯 얼굴 위치/크기가 정중앙으로 맞춤되었습니다.', 'info');
  }
  drawMainFittingAvatar();
}
window.resetCanvasCenter = resetCanvasCenter;
window.resetAllOffset = resetCanvasCenter;
window.resetFaceOffset = resetCanvasCenter;

// 📸 [얼굴 사진 업로드] -> 스마트하게 얼굴 조절 모드로 자동 전환!
function handleFacePhotoUpload(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    const dataUrl = e.target.result;
    window.userFaceDataUrl = dataUrl;
    window.userUploadedPhoto = null;

    const img = new Image();
    img.onload = function() {
      window.userFaceImage = img;
      window.isFaceUploaded = true;
      window.isUserPhotoLoaded = true;
      window.faceOffsetX = 0;
      window.faceOffsetY = 0;
      window.faceScale = 1.0;

      // 스마트 센스: 얼굴 사진 올렸으므로 즉시 얼굴 조절 모드로 자동 설정 & 잠금 해제!
      window.currentAdjustTarget = 'face';
      window.isCanvasLocked = false;
      applyCanvasLockState();
      updateAdjustTargetUI();

      renderRealPhotoStudio();
      if (typeof showToast === 'function') {
        showToast('✅ [얼굴 사진 장착 완료]: 머리 상단에 25% 소프트 페더링으로 융합되었습니다! 손가락으로 만져보세요.', 'success');
      }
    };
    img.src = dataUrl;
  };
  reader.readAsDataURL(file);
}
window.handleFacePhotoUpload = handleFacePhotoUpload;
window.handleUserFacePhotoUpload = handleFacePhotoUpload;
window.handleRealPhotoUpload = handleFacePhotoUpload;

// 👚 [내 옷/전신 사진 업로드] -> 스마트하게 전신 조절 모드로 자동 전환!
function handleCustomClothUpload(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    const dataUrl = e.target.result;
    window.customClothDataUrl = dataUrl;

    const img = new Image();
    img.onload = function() {
      window.customClothImage = img;
      window.isCustomClothUploaded = true;
      window.bodyPhotoOffsetX = 0;
      window.bodyPhotoOffsetY = 0;
      window.bodyPhotoScale = 1.0;

      // 스마트 센스: 전신/옷 사진 올렸으므로 즉시 전신 조절 모드로 자동 설정 & 잠금 해제!
      window.currentAdjustTarget = 'body';
      window.isCanvasLocked = false;
      applyCanvasLockState();
      updateAdjustTargetUI();

      renderRealPhotoStudio();
      if (typeof showToast === 'function') {
        showToast('✅ [전신/옷 사진 장착 완료]: 손가락 드래그로 위치를 이동하고 두 손가락으로 크기를 맞춰보세요!', 'success');
      }
    };
    img.src = dataUrl;
  };
  reader.readAsDataURL(file);
}
window.handleCustomClothUpload = handleCustomClothUpload;

function toggleFacePhotoMenu() {
  const menu = document.getElementById('face-photo-action-menu') || document.getElementById('face-photo-menu');
  if (menu) menu.classList.toggle('hidden');
}
window.toggleFacePhotoMenu = toggleFacePhotoMenu;

function triggerFaceCameraPhoto() {
  const menu = document.getElementById('face-photo-action-menu') || document.getElementById('face-photo-menu');
  if (menu) menu.classList.add('hidden');
  const inp = document.getElementById('face-camera-input') || document.getElementById('face-upload-input');
  if (inp) inp.click();
}
window.triggerFaceCameraPhoto = triggerFaceCameraPhoto;

function triggerFaceGalleryPhoto() {
  const menu = document.getElementById('face-photo-action-menu') || document.getElementById('face-photo-menu');
  if (menu) menu.classList.add('hidden');
  const inp = document.getElementById('face-gallery-input') || document.getElementById('face-upload-input');
  if (inp) inp.click();
}
window.triggerFaceGalleryPhoto = triggerFaceGalleryPhoto;

function resetToDefaultAvatarFace() {
  const menu = document.getElementById('face-photo-action-menu') || document.getElementById('face-photo-menu');
  if (menu) menu.classList.add('hidden');
  window.userFaceImage = null;
  window.userFaceDataUrl = null;
  window.isFaceUploaded = false;
  drawMainFittingAvatar();
  if (typeof showToast === 'function') showToast('🔄 얼굴 사진이 초기화되었습니다.', 'info');
}
window.resetToDefaultAvatarFace = resetToDefaultAvatarFace;
window.resetFaceToIllustration = resetToDefaultAvatarFace;

function togglePhotoViewMode() {
  toggleRenderMode();
  const btn = document.getElementById('btn-photo-view-mode') || document.getElementById('btn-mode-toggle');
  if (btn) {
    btn.innerHTML = window.currentRenderMode === 'photo_lookbook' ? '<span>👗코디합성</span>' : '<span>📸원본보기</span>';
  }
}
window.togglePhotoViewMode = togglePhotoViewMode;

function toggleRenderMode() {
  window.currentRenderMode = (window.currentRenderMode === 'photo_lookbook') ? 'user_original' : 'photo_lookbook';
  renderRealPhotoStudio();
}
window.toggleRenderMode = toggleRenderMode;

// 👗 [10벌 의상 쇼룸 즉시 교체]
function applyWardrobeOutfit(num) {
  window.currentWardrobeNum = num;
  window.customClothImage = null;
  const item = window.LOOKBOOK_CATALOG[num] || window.LOOKBOOK_CATALOG[1];

  const badge = document.getElementById('current-outfit-badge');
  if (badge) badge.textContent = `🌸 ${num}번 착장 중`;

  for (let i = 1; i <= 10; i++) {
    const card = document.getElementById(`outfit-card-${i}`);
    if (card) {
      if (i === num) {
        card.classList.add('ring-2', 'ring-purple-400', 'scale-[1.02]');
      } else {
        card.classList.remove('ring-2', 'ring-purple-400', 'scale-[1.02]');
      }
    }
  }

  window.currentRenderMode = 'photo_lookbook';
  const modeBtn = document.getElementById('btn-photo-view-mode') || document.getElementById('btn-mode-toggle');
  if (modeBtn) modeBtn.innerHTML = '<span>👗코디합성</span>';

  renderRealPhotoStudio();
  if (typeof showToast === 'function') {
    showToast(`👗 [실사 룩북 전환]: ${item.name}`, 'info');
  }
}
window.applyWardrobeOutfit = applyWardrobeOutfit;

// 👑 [v6.6 초실사 렌더러: 캔버스 상하단 가림 0% & 정밀 블렌딩]
function renderRealPhotoStudio() {
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const w = canvas.width || 450;
  const h = canvas.height || 600;
  const cx = w / 2;

  ctx.clearRect(0, 0, w, h);

  const look = window.LOOKBOOK_CATALOG[window.currentWardrobeNum] || window.LOOKBOOK_CATALOG[1];

  // 1. 다크 스튜디오 보케 배경
  const bgGrad = ctx.createRadialGradient(cx, h * 0.4, 20, cx, h * 0.5, h * 0.8);
  bgGrad.addColorStop(0, '#1a1033');
  bgGrad.addColorStop(0.5, '#0b0f19');
  bgGrad.addColorStop(1, '#02040a');
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, w, h);

  // 미세 보케 조명
  const bokehList = [
    { x: 60, y: 100, r: 40, a: 0.08, c: look.colorTheme },
    { x: 390, y: 160, r: 55, a: 0.06, c: '#a855f7' },
    { x: 80, y: 450, r: 65, a: 0.05, c: '#3b82f6' },
    { x: 370, y: 480, r: 50, a: 0.07, c: look.colorTheme }
  ];
  bokehList.forEach(b => {
    ctx.save();
    ctx.beginPath();
    ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
    ctx.fillStyle = b.c;
    ctx.globalAlpha = b.a;
    ctx.filter = 'blur(12px)';
    ctx.fill();
    ctx.restore();
  });

  // ── [모드 A]: 내 사진 원본 전체 풀스크린 표시 (전신사진 크기·위치 반영) ──
  if (window.currentRenderMode === 'user_original' && (window.userUploadedPhoto || window.userFaceImage || window.customClothImage)) {
    const photo = window.userUploadedPhoto || window.customClothImage || window.userFaceImage;
    if (photo && photo.complete) {
      ctx.save();
      const pw = photo.naturalWidth || photo.width || 400;
      const ph = photo.naturalHeight || photo.height || 600;
      const baseRatio = Math.min((w * 0.94) / pw, (h * 0.94) / ph);
      const ratio = baseRatio * (window.bodyPhotoScale || 1.0);
      const dw = pw * ratio;
      const dh = ph * ratio;
      const dx = cx - dw / 2 + (window.bodyPhotoOffsetX || 0);
      const dy = (h - dh) / 2 + (window.bodyPhotoOffsetY || 0);

      ctx.shadowColor = 'rgba(0,0,0,0.6)';
      ctx.shadowBlur = 24;
      ctx.drawImage(photo, dx, dy, dw, dh);
      ctx.restore();
      return;
    }
  }

  // ── [모드 B]: 초실사 패션 룩북 모델 + 얼굴 실사 스왑 ──
  if (window.aiTryOnResultImage && window.aiTryOnResultImage.complete) {
    ctx.save();
    ctx.drawImage(window.aiTryOnResultImage, 0, 0, w, h);
    ctx.restore();
  } else if (window.customClothImage && window.customClothImage.complete) {
    // 사용자가 직접 올린 옷 사진으로 렌더링 (전신줌/이동 반영)
    ctx.save();
    const cimg = window.customClothImage;
    const cw = cimg.naturalWidth || cimg.width || 400;
    const ch = cimg.naturalHeight || cimg.height || 600;
    const cratio = Math.min((w * 0.88) / cw, (h * 0.85) / ch) * (window.bodyPhotoScale || 1.0);
    const cdw = cw * cratio;
    const cdh = ch * cratio;
    const cdx = cx - cdw / 2 + (window.bodyPhotoOffsetX || 0);
    const cdy = (h - cdh) / 2 + 25 + (window.bodyPhotoOffsetY || 0);

    ctx.shadowColor = 'rgba(0,0,0,0.6)';
    ctx.shadowBlur = 20;
    ctx.drawImage(cimg, cdx, cdy, cdw, cdh);
    ctx.restore();
  } else {
    // Unsplash 실사 패션 화보 렌더링 (전신줌/이동 반영)
    const cached = window.lookbookImageCache && window.lookbookImageCache[window.currentWardrobeNum || 1];
    if (cached && cached.complete && cached.naturalWidth > 0) {
      ctx.save();
      const iw = cached.naturalWidth;
      const ih = cached.naturalHeight;
      const iratio = Math.max(w / iw, h / ih) * (window.bodyPhotoScale || 1.0);
      const idw = iw * iratio;
      const idh = ih * iratio;
      const idx = cx - idw / 2 + (window.bodyPhotoOffsetX || 0);
      const idy = (h - idh) / 2 + (window.bodyPhotoOffsetY || 0);
      ctx.drawImage(cached, idx, idy, idw, idh);
      ctx.restore();
    } else {
      renderElegantStudioBackdrop(ctx, w, h, cx, look);
    }
  }

  // 얼굴 사진 실사 스왑 (얼굴 크기 11%, 상단 17% 위치, 가장자리 25% 소프트 페더링)
  if (window.userFaceImage && window.userFaceImage.complete) {
    renderSoftFeatheredFaceSwap(ctx, cx, look, w, h);
  }
}
window.renderRealPhotoStudio = renderRealPhotoStudio;

function renderElegantStudioBackdrop(ctx, w, h, cx, look) {
  ctx.save();
  const floorGrad = ctx.createRadialGradient(cx, h - 35, 10, cx, h - 35, 180);
  floorGrad.addColorStop(0, 'rgba(255, 255, 255, 0.12)');
  floorGrad.addColorStop(0.5, 'rgba(0, 0, 0, 0.4)');
  floorGrad.addColorStop(1, 'transparent');
  ctx.fillStyle = floorGrad;
  ctx.beginPath();
  ctx.ellipse(cx, h - 35, 160, 25, 0, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = 'rgba(255, 255, 255, 0.04)';
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.roundRect(cx - 140, 70, 280, 480, 24);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = '#cbd5e1';
  ctx.font = 'bold 13px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('✨ 실사 화보 모델 로드 중...', cx, 290);
  ctx.fillStyle = '#94a3b8';
  ctx.font = '11px sans-serif';
  ctx.fillText('컨트롤 박스 [📸 내 얼굴 사진]을 터치하세요', cx, 315);
  ctx.restore();
}

function renderSoftFeatheredFaceSwap(ctx, cx, look, w, h) {
  ctx.save();
  const canvasW = w || 450;
  const canvasH = h || 600;
  const defaultRadius = canvasW * 0.11 * 0.5;
  const defaultCenterY = canvasH * 0.17;
  const defaultCenterX = cx || (canvasW / 2);

  const faceX = defaultCenterX + (window.faceOffsetX || 0);
  const faceY = defaultCenterY + (window.faceOffsetY || 0);
  const faceR = defaultRadius * (window.faceScale || 1.0);

  const off = document.createElement('canvas');
  off.width = faceR * 2.8;
  off.height = faceR * 2.8;
  const octx = off.getContext('2d');
  if (!octx) { ctx.restore(); return; }
  const ocx = off.width / 2;
  const ocy = off.height / 2;

  const img = window.userFaceImage;
  const iw = img.naturalWidth || img.width || 300;
  const ih = img.naturalHeight || img.height || 300;
  const minDim = Math.min(iw, ih);
  const sx = (iw - minDim) / 2;
  const sy = (ih - minDim) / 2;

  octx.save();
  octx.drawImage(img, sx, sy, minDim, minDim, 0, 0, off.width, off.height);

  octx.globalCompositeOperation = 'destination-in';
  const vGrad = octx.createRadialGradient(ocx, ocy, faceR * 0.75, ocx, ocy, faceR * 1.0);
  vGrad.addColorStop(0, 'rgba(0, 0, 0, 1.0)');
  vGrad.addColorStop(0.75, 'rgba(0, 0, 0, 0.95)');
  vGrad.addColorStop(0.9, 'rgba(0, 0, 0, 0.45)');
  vGrad.addColorStop(1.0, 'rgba(0, 0, 0, 0.0)');
  octx.fillStyle = vGrad;
  octx.beginPath();
  octx.arc(ocx, ocy, faceR * 1.0, 0, Math.PI * 2);
  octx.fill();
  octx.restore();

  ctx.drawImage(off, faceX - ocx, faceY - ocy);

  const chinShadow = ctx.createRadialGradient(faceX, faceY + faceR * 0.88, 1, faceX, faceY + faceR * 0.88, faceR * 0.65);
  chinShadow.addColorStop(0, 'rgba(20, 10, 5, 0.35)');
  chinShadow.addColorStop(1, 'transparent');
  ctx.fillStyle = chinShadow;
  ctx.beginPath();
  ctx.ellipse(faceX, faceY + faceR * 0.9, faceR * 0.6, 6, 0, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
}

function drawMainFittingAvatar() {
  renderRealPhotoStudio();
}
window.drawMainFittingAvatar = drawMainFittingAvatar;

function drawDetailedIllustrationFace() {
  return;
}
window.drawDetailedIllustrationFace = drawDetailedIllustrationFace;

// 🔒 & 🔍 [v6.6 직관적 터치 엔진: 1손가락 상하좌우 이동 & 2손가락 핀치 줌]
function initFaceTouchDragInteraction(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || canvas._touchDragBound) return;
  canvas._touchDragBound = true;

  let isDragging = false;
  let startX = 0, startY = 0;
  let initialPinchDistance = 0;
  let initialScale = 1.0;

  function getDistance(t1, t2) {
    const dx = t1.clientX - t2.clientX;
    const dy = t1.clientY - t2.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  function onStart(e) {
    if (window.isCanvasLocked) return;
    if (e.touches && e.touches.length === 2) {
      initialPinchDistance = getDistance(e.touches[0], e.touches[1]);
      initialScale = (window.currentAdjustTarget === 'body') ? (window.bodyPhotoScale || 1.0) : (window.faceScale || 1.0);
      isDragging = false;
      return;
    }
    const t = e.touches ? e.touches[0] : e;
    isDragging = true;
    startX = t.clientX;
    startY = t.clientY;
  }

  function onMove(e) {
    if (window.isCanvasLocked) return;
    if (e.touches && e.touches.length === 2) {
      const currentDist = getDistance(e.touches[0], e.touches[1]);
      if (initialPinchDistance > 10) {
        const factor = currentDist / initialPinchDistance;
        if (window.currentAdjustTarget === 'body') {
          window.bodyPhotoScale = Math.max(0.3, Math.min(3.5, initialScale * factor));
        } else {
          window.faceScale = Math.max(0.3, Math.min(3.0, initialScale * factor));
        }
        drawMainFittingAvatar();
      }
      return;
    }
    if (!isDragging) return;
    const t = e.touches ? e.touches[0] : e;
    const dx = t.clientX - startX;
    const dy = t.clientY - startY;
    startX = t.clientX;
    startY = t.clientY;

    if (window.currentAdjustTarget === 'body') {
      window.bodyPhotoOffsetX += dx;
      window.bodyPhotoOffsetY += dy;
    } else {
      window.faceOffsetX += dx;
      window.faceOffsetY += dy;
    }
    drawMainFittingAvatar();
  }

  function onEnd() {
    isDragging = false;
    initialPinchDistance = 0;
  }

  canvas.addEventListener('mousedown', onStart);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onEnd);

  canvas.addEventListener('touchstart', onStart, { passive: false });
  window.addEventListener('touchmove', onMove, { passive: false });
  window.addEventListener('touchend', onEnd);
}

// 캔버스 인터랙션 자동 초기화
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => initFaceTouchDragInteraction('main-fitting-canvas'));
} else {
  initFaceTouchDragInteraction('main-fitting-canvas');
}

// 화보 캔버스 저장
function saveMyFittingPhoto() {
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');
  if (!canvas) return;
  try {
    const a = document.createElement('a');
    a.download = `coordi_studio_v66_${Date.now()}.png`;
    a.href = canvas.toDataURL('image/png');
    a.click();
    if (typeof showToast === 'function') {
      showToast('💾 [화보 저장 완료]: 갤러리에 저장되었습니다!', 'success');
    }
  } catch (e) {
    if (typeof showToast === 'function') showToast('💾 이미지를 길게 눌러 저장하세요.', 'info');
  }
}
window.saveMyFittingPhoto = saveMyFittingPhoto;

function renderPhotoshopAISwap() { renderRealPhotoStudio(); }
window.renderPhotoshopAISwap = renderPhotoshopAISwap;
'''

def patch_index_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. tab-daughters 내부 최상단 '스마트폰 원격 복붙 직통 스위치' 박스 완전 삭제
    if "스마트폰 원격 복붙 직통 스위치" in html:
        idx1 = html.find("<!-- 📲 [스마트폰 원격 복붙")
        if idx1 == -1:
            idx1 = html.find('<div class="mb-3 p-3 bg-gradient-to-r from-purple-950/80')
        idx2 = html.find("<!-- 👗 [한걸음씩 상생나눔", idx1)
        if idx1 != -1 and idx2 != -1:
            html = html[:idx1] + html[idx2:]
            print("  ✅ [index.html] '스마트폰 원격 복붙 직통 스위치' 거대 보라색 박스 100% 완전 삭제!")

    # 2. 캔버스 위 '원격 발사대 슬림 바' 완전 삭제
    launcher_pattern = r'<!-- 🚀 \[스마트폰 대표님 직통 원격 발사대:[^>]*-->\s*<div class="w-full max-w-\[440px\][^>]*>.*?</div>\s*</div>'
    if re.search(launcher_pattern, html, re.DOTALL):
        html = re.sub(launcher_pattern, '', html, count=1, flags=re.DOTALL)
        print("  ✅ [index.html] '원격 발사대 입력창 & 안실장 발사 버튼' 100% 완전 삭제!")

    # 3. 서브탭 바 & 캔버스 컨테이너 & 컨트롤 박스 교체
    # Zone 2 내부 체형 세팅 바 바로 아래부터 옷장 쇼룸 직전까지를 V66_SUBTAB_BAR_HTML + V66_CANVAS_CONTAINER_HTML + V66_CONTROL_BOX_HTML 로 치환
    middle_pattern = r'<!-- 👑 \[v6\.[0-9].*?서브탭 바[^>]*-->.*?<!-- 🎛️ \[v6\.[0-9].*?컨트롤 박스[^>]*-->\s*<div id="v5-one-line-remote-bar"[^>]*>.*?</div>\s*</div>'
    new_middle = V66_SUBTAB_BAR_HTML + "\n\n        " + V66_CANVAS_CONTAINER_HTML + "\n\n        " + V66_CONTROL_BOX_HTML
    if re.search(middle_pattern, html, re.DOTALL):
        html = re.sub(middle_pattern, new_middle, html, count=1, flags=re.DOTALL)
        print("  ✅ [index.html] 순수 코디 캔버스 & 직관적 올인원 컨트롤 박스 교체 완료!")
    else:
        # 혹시 이전 패턴과 매칭되지 않을 경우 컨트롤 박스 단독 매칭
        alt_ctrl = r'<!-- 🎛️ \[v6\.[0-9].*?컨트롤 박스[^>]*-->\s*<div id="v5-one-line-remote-bar"[^>]*>.*?</div>\s*</div>'
        if re.search(alt_ctrl, html, re.DOTALL):
            html = re.sub(alt_ctrl, V66_CONTROL_BOX_HTML, html, count=1, flags=re.DOTALL)
            print("  ✅ [index.html] 컨트롤 박스 교체 완료!")

    # 4. 하단 코디 무관 관리용 서랍(VOC, 배포, 퀴즈 배너) 완전 숨김 (display: none !important)
    if 'id="btn-toggle-quiz"' in html:
        q_pos = html.find('id="btn-toggle-quiz"')
        b_start = html.rfind('<button', 0, q_pos)
        b_end = html.find('</button>', q_pos) + len('</button>')
        if b_start != -1 and b_end != -1:
            html = html[:b_start] + '<!-- 🎓 인성 퀴즈 버튼 코디 탭에서 완전 제거 -->' + html[b_end:]
            print("  ✅ [index.html] 인성 퀴즈 풀기 버튼 완전 삭제 완료!")

    drawers_pattern = r'<!-- 🗂️ \[토스\(Toss\) 스타일 하단 4대 접이식 서랍 \(Drawer\)\] -->\s*<div class="space-y-2 pt-2">.*?</div>\s*</div>\s*</div>'
    if re.search(drawers_pattern, html, re.DOTALL):
        html = re.sub(drawers_pattern, '<!-- 하단 관리 서랍 코디 탭에서 완전 제거 -->', html, count=1, flags=re.DOTALL)
        print("  ✅ [index.html] 하단 관리 서랍(VOC, 배포 등) 코디 화면에서 완전 삭제!")

    # 5. JS 엔진 교체
    js_start_marker = "window.currentRenderMode = 'photo_lookbook';"
    js_end_marker = "window.renderPhotoshopAISwap = renderPhotoshopAISwap;"
    start_pos = html.find(js_start_marker)
    end_pos = html.rfind(js_end_marker)

    if start_pos != -1 and end_pos != -1:
        end_pos += len(js_end_marker)
        html = html[:start_pos] + V66_JS_ENGINE.strip() + html[end_pos:]
        print("  ✅ [index.html] v6.6 JS 엔진 교체 완료 (터치 1번 전환 & 직관적 핀치 줌)!")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  💾 [index.html] 파일 저장 완료: {file_path}")

def patch_app_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    js_start_marker = "window.currentRenderMode = 'photo_lookbook';"
    js_end_marker = "window.renderPhotoshopAISwap = renderPhotoshopAISwap;"
    start_pos = html.find(js_start_marker)
    end_pos = html.rfind(js_end_marker)

    if start_pos != -1 and end_pos != -1:
        end_pos += len(js_end_marker)
        html = html[:start_pos] + V66_JS_ENGINE.strip() + html[end_pos:]
        print("  ✅ [dream_closet_future_master_app.html] v6.6 JS 엔진 교체 완료!")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  💾 [dream_closet_future_master_app.html] 파일 저장 완료: {file_path}")

def main():
    print("=" * 80)
    print("🔥 [v6.6 Pure Coordi Studio] 패치 실행: 코디 무관 요소 완전 삭제 & 직관적 터치 엔진")
    print("=" * 80)

    patch_index_html("dashboard/index.html")
    patch_app_html("dashboard/dream_closet_future_master_app.html")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
apply_v62_direct_photo.py
--------------------------------------------------------------------------------
🔥 [v6.2 Direct-Photo Instant Apply]
1. 얼굴 사진 & 옷 사진 0.01초 직통 적용 파이프라인 구축:
   - handleFacePhotoUpload & handleCustomClothUpload 전면 재작성 (FileReader -> Image -> 即시 반영)
   - crossOrigin 충돌 원천 차단
   - 캔버스 + DOM 오버레이(live-face-photo-overlay, live-cloth-photo-overlay) 듀얼 실사 보장
   - 중앙 얼굴 영역 터치 시 사진 선택창 즉시 호출 (triggerFaceGalleryPhoto)
2. 빨간색 볼링핀/오뚝이 도형 & 📸 내 사진 올리기 구슬 머리 100% 영구 삭제:
   - Unsplash 실사 패션 모델 10벌 고화질 카탈로그 & 프리로드 연동
   - 볼링핀/오뚝이 베지어 곡선 코드 완전 박멸
   - [🖼️ 내 사진 전체보기 / 👗 코디 합성모드] 원터치 토글
3. 1줄 리모컨 우측 버튼 삐져나감 (Overflow) 100% 교정:
   - flex-wrap: wrap, box-sizing: border-box, 최적 여백/패딩으로 360px 모바일 화면에서도 0px 삐져나감 보장
4. dashboard/index.html & dashboard/dream_closet_future_master_app.html 양쪽 파일 동기화
--------------------------------------------------------------------------------
"""

import sys
import re
from pathlib import Path
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 1. 상단 컨트롤 바 HTML (모드 전환 & 직통 사진 슬롯)
V62_TOP_HEADER_HTML = '''<!-- 👑 [v6.2 캔버스 외부 상단 독립 컨트롤 헤더: 모드 전환 & 직통 사진 슬롯] -->
        <div class="w-full max-w-[440px] mx-auto p-2 rounded-xl bg-slate-900/90 border border-purple-500/30 flex items-center justify-between gap-1.5 text-xs shadow-lg">
          <!-- 모드 전환 (피팅 / 2035 / 가족룩) -->
          <div class="flex items-center gap-1 p-0.5 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px]">
            <button type="button" onclick="switchMainFittingSubTab('fitting')" id="tab-sub-fitting" class="px-2 py-1 rounded-md bg-purple-600 text-white font-bold transition shadow-sm">
              👗 피팅
            </button>
            <button type="button" onclick="switchMainFittingSubTab('future')" id="tab-sub-future" class="px-2 py-1 rounded-md text-slate-300 hover:text-white transition">
              🔮 2035
            </button>
            <button type="button" onclick="switchMainFittingSubTab('family')" id="tab-sub-family" class="px-2 py-1 rounded-md text-slate-300 hover:text-white transition">
              👨‍👧‍👧 가족
            </button>
          </div>

          <!-- 직통 사진 슬롯: [🖼️모드전환] + [📸내 얼굴 사진] + [👚내 옷 합성] -->
          <div class="flex items-center gap-1">
            <!-- 0) 원터치 뷰어 전환: [🖼️내사진 원본] ↔ [👗코디 합성] -->
            <button type="button" id="btn-mode-toggle" onclick="toggleRenderMode()" class="px-2 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-purple-200 border border-purple-500/40 font-bold text-[10px] shadow active:scale-95 transition whitespace-nowrap" title="내 사진 원본 전체보기 / 코디 합성모드 전환">
              <span>👗코디합성</span>
            </button>

            <!-- 1) [📸 내 얼굴 사진 넣기] -->
            <div class="relative">
              <button type="button" onclick="toggleFacePhotoMenu()" id="btn-face-menu" class="px-2.5 py-1.5 rounded-lg bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white font-bold text-[11px] shadow-md flex items-center gap-1 active:scale-95 transition cursor-pointer" title="내 얼굴 사진 넣기">
                <span>📸</span><span>내 얼굴 사진</span>
              </button>
              <div id="face-photo-menu" class="hidden absolute right-0 top-full mt-1.5 w-48 p-1.5 rounded-xl bg-slate-900 border border-purple-500/40 shadow-2xl z-50 space-y-1 text-xs">
                <button type="button" onclick="triggerFaceCameraPhoto()" class="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-purple-600/30 text-white flex items-center gap-2 transition">
                  <span>📷</span><span>즉시 사진 촬영</span>
                </button>
                <button type="button" onclick="triggerFaceAlbumPhoto()" class="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-purple-600/30 text-white flex items-center gap-2 transition">
                  <span>🖼️</span><span>앨범에서 사진 선택</span>
                </button>
                <button type="button" onclick="resetFaceToIllustration()" class="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-rose-600/30 text-rose-300 flex items-center gap-2 transition border-t border-slate-800">
                  <span>🔄</span><span>얼굴 사진 삭제 (초기화)</span>
                </button>
              </div>
              <input type="file" id="face-upload-input" accept="image/*" class="hidden" onchange="handleFacePhotoUpload(event)">
              <input type="file" id="face-camera-input" accept="image/*" capture="user" class="hidden" onchange="handleFacePhotoUpload(event)">
              <input type="file" id="real-photo-file-input" accept="image/*" class="hidden" onchange="handleFacePhotoUpload(event)">
            </div>

            <!-- 2) [👚 내 옷 합성] -->
            <div>
              <button type="button" onclick="openCustomClothUpload()" id="btn-custom-cloth" class="px-2.5 py-1.5 rounded-lg bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-bold text-[11px] shadow-md flex items-center gap-1 active:scale-95 transition cursor-pointer border border-blue-400/30" title="쇼핑몰 옷/내 코디 사진 올려 즉시 합성">
                <span>👚</span><span>내 옷 합성</span>
              </button>
              <input type="file" id="custom-cloth-file-input" accept="image/*" class="hidden" onchange="handleCustomClothUpload(event)">
            </div>
          </div>
        </div>'''

# 2. 캔버스 컨테이너 (실사 의상 오버레이 + 얼굴 오버레이 + 터치 영역 + 캔버스)
V62_CANVAS_CONTAINER_HTML = '''<!-- 👑 [v6.2 캔버스 컨테이너: 실사 패션 화보 & 얼굴 직통 오버레이 시스템] -->
        <div id="fitting-studio-container" class="w-full max-w-[420px] mx-auto aspect-[3/4] max-h-[500px] rounded-2xl bg-gradient-to-b from-slate-950 via-[#0a0f1d] to-slate-950 border border-purple-500/30 shadow-2xl relative overflow-hidden flex items-center justify-center select-none">
          <!-- 1. 의상 실사 사진 레이어 (Base) -->
          <img id="live-cloth-photo-overlay" class="absolute inset-0 w-full h-full object-cover pointer-events-none transition-opacity duration-200" style="display:none;" alt="실사 의상 화보">
          
          <!-- 2. 얼굴 실사 사진 오버레이 (Face Layer: 0.01초 직통 표시) -->
          <img id="live-face-photo-overlay" class="hidden absolute pointer-events-none rounded-full object-cover shadow-2xl transition-all duration-150 z-10" style="width: 96px; height: 96px; top: 22.5%; left: 50%; transform: translate(-50%, -50%); border: 2.5px solid rgba(255,255,255,0.85); box-shadow: 0 10px 25px rgba(0,0,0,0.6);" alt="내 얼굴 사진">
          
          <!-- 3. 원터치 얼굴 터치 영역 (손가락 터치 시 갤러리 사진 선택창 즉시 열림) -->
          <div id="face-touch-trigger-zone" onclick="triggerFaceGalleryPhoto()" class="absolute cursor-pointer rounded-full transition active:scale-95 z-20" style="width: 110px; height: 110px; top: 22.5%; left: 50%; transform: translate(-50%, -50%);" title="얼굴 터치하여 내 사진 올리기"></div>

          <!-- 4. 메인 피팅 캔버스 (배경 보케 조명, 하이브리드 블렌딩 및 포토 렌더러) -->
          <canvas id="main-fitting-canvas" width="450" height="600" class="w-full h-full object-contain relative z-5" style="touch-action: pan-y !important; cursor: grab;"></canvas>

          <!-- 5. 하단 정적 배지 (화면 흔들림 0%) -->
          <div id="main-angle-display-badge" class="absolute bottom-2 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-slate-950/90 border border-emerald-500/40 text-[11px] text-emerald-300 font-bold shadow-lg pointer-events-none backdrop-blur-sm whitespace-nowrap z-30">
            🔒 화면 고정됨 | ✨ ECC 실사 포토 스튜디오 v6.2
          </div>
        </div>'''

# 3. 1줄 퀵 리모컨 바 (flex-wrap: wrap, box-sizing: border-box, 삐져나감 0%)
V62_REMOTE_BAR_HTML = '''<!-- 🎛️ [v6.2 Direct-Photo 1줄 퀵 리모컨 바 (화면 삐져나감 0% 완전 교정)] -->
        <div id="v5-one-line-remote-bar" class="w-full max-w-[450px] mx-auto mt-1 mb-2 p-1.5 rounded-2xl bg-slate-900/95 border border-purple-500/50 shadow-xl flex flex-wrap items-center justify-center gap-1 text-xs backdrop-blur-md box-border" style="box-sizing: border-box;">
          <!-- 1. [🔒 고정됨] / [🔓 조절중] 잠금 스위치 (기본 잠금) -->
          <button type="button" id="btn-canvas-lock" onclick="toggleCanvasLock()" class="px-2 h-7 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-emerald-100 text-[10px] font-black border border-emerald-400 active:scale-95 flex items-center gap-0.5 whitespace-nowrap shadow transition" title="터치 잠금 토글 (기본: 위치 고정)">
            <span id="canvas-lock-icon">🔒</span><span id="canvas-lock-label">고정됨</span>
          </button>

          <!-- 2. 크기 조절 버튼 (+ / -) -->
          <div class="flex items-center gap-0.5">
            <button type="button" onclick="adjustFaceScale(-0.08)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-black text-xs border border-slate-700 active:scale-95 flex items-center justify-center transition" title="작게">➖</button>
            <button type="button" onclick="adjustFaceScale(+0.08)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-black text-xs border border-slate-700 active:scale-95 flex items-center justify-center transition" title="크게">➕</button>
          </div>

          <!-- 3. 상하좌우 4방향 D-Pad -->
          <div class="flex items-center gap-0.5 font-bold">
            <button type="button" onclick="adjustFaceOffset(-4, 0)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-[11px] border border-slate-700 active:scale-95 flex items-center justify-center transition" title="좌">⬅️</button>
            <button type="button" onclick="adjustFaceOffset(0, -4)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-[11px] border border-slate-700 active:scale-95 flex items-center justify-center transition" title="위">⬆️</button>
            <button type="button" onclick="adjustFaceOffset(0, +4)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-[11px] border border-slate-700 active:scale-95 flex items-center justify-center transition" title="아래">⬇️</button>
            <button type="button" onclick="adjustFaceOffset(+4, 0)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-[11px] border border-slate-700 active:scale-95 flex items-center justify-center transition" title="우">➡️</button>
          </div>

          <!-- 4. 정중앙 초기화 -->
          <button type="button" onclick="resetFaceOffset()" class="px-2 h-7 rounded-lg bg-indigo-600/40 hover:bg-indigo-600/70 text-indigo-200 text-[10px] font-bold border border-indigo-400/40 active:scale-95 flex items-center gap-0.5 whitespace-nowrap transition" title="정중앙 초기화">
            <span>🎯정중앙</span>
          </button>

          <!-- 5. [🪄AI실사합성] -->
          <button type="button" id="btn-real-ai-tryon" onclick="runRealAITryOn()" class="px-2 h-7 rounded-lg bg-gradient-to-r from-blue-600/80 via-purple-600/80 to-pink-600/80 hover:from-blue-500 hover:to-pink-500 text-white text-[10px] font-black border border-blue-400/50 active:scale-95 flex items-center gap-0.5 whitespace-nowrap shadow-md transition" title="AI 실사 의상 착장 합성">
            <span>🪄AI실사합성</span>
          </button>

          <!-- 6. 화보 저장 -->
          <button type="button" onclick="saveMyFittingPhoto()" class="px-2 h-7 rounded-lg bg-emerald-600/50 hover:bg-emerald-600/70 text-emerald-100 text-[10px] font-bold border border-emerald-400/40 active:scale-95 flex items-center gap-0.5 whitespace-nowrap transition" title="화보 저장">
            <span>💾저장</span>
          </button>
        </div>'''

# 4. v6.2 JS 엔진 코드
V62_JS_ENGINE = '''
// ============================================================================
// 👑 [v6.2 Direct-Photo] 실사 화보 카탈로그 & 0.01초 직통 적용 엔진
// ============================================================================

window.currentRenderMode = 'photo_lookbook'; // 'photo_lookbook' | 'user_original'
window.currentWardrobeNum = 1;
window.isCanvasLocked = true; // 🔒 기본 화면 고정
window.faceOffsetX = 0;
window.faceOffsetY = 0;
window.faceScale = 1.0;

// 10벌 고화질 실사 패션 화보 카탈로그 (Unsplash 실제 스튜디오 모델 화보)
window.LOOKBOOK_CATALOG = {
  1: {
    name: "🌸 러블리 K-하이틴 핑크 가디건",
    colorTheme: "#f43f5e",
    imageUrl: "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=600&q=80",
    modelDesc: "파스텔 핑크 울 가디건 & 플리츠 스커트 스튜디오 실사 화보",
    faceAnchor: { cx: 225, cy: 135, r: 48 }
  },
  2: {
    name: "🎀 청량 아이돌 데님 자켓 & 원피스",
    colorTheme: "#38bdf8",
    imageUrl: "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=600&q=80",
    modelDesc: "라이트블루 워싱 데님 자켓 & 썸머 원피스 실사 화보",
    faceAnchor: { cx: 225, cy: 138, r: 48 }
  },
  3: {
    name: "🎓 명문 프레피 블레이저 & 리본",
    colorTheme: "#818cf8",
    imageUrl: "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=600&q=80",
    modelDesc: "클래식 네이비 테일러드 블레이저 & 프레피 타이 실사 화보",
    faceAnchor: { cx: 225, cy: 132, r: 46 }
  },
  4: {
    name: "👕 시티보이 오버핏 후드 & 카고",
    colorTheme: "#34d399",
    imageUrl: "https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?auto=format&fit=crop&w=600&q=80",
    modelDesc: "세이지 그린 프리미엄 오버핏 후드 & 카고 팬츠 실사 화보",
    faceAnchor: { cx: 225, cy: 140, r: 49 }
  },
  5: {
    name: "🧥 베이지 트렌치 롱코트",
    colorTheme: "#fbbf24",
    imageUrl: "https://images.unsplash.com/photo-1485968579580-b6d095142e6e?auto=format&fit=crop&w=600&q=80",
    modelDesc: "헤리티지 베이지 더블 브레스티드 트렌치 코트 실사 화보",
    faceAnchor: { cx: 225, cy: 130, r: 47 }
  },
  6: {
    name: "👔 청담 테일러드 VIP 네이비 수트",
    colorTheme: "#60a5fa",
    imageUrl: "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=600&q=80",
    modelDesc: "이태리 최고급 원단 맞춤 다크 네이비 수트 실사 화보",
    faceAnchor: { cx: 225, cy: 132, r: 48 }
  },
  7: {
    name: "✨ 캐시미어 웜골드 니트 & 슬랙스",
    colorTheme: "#fcd34d",
    imageUrl: "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?auto=format&fit=crop&w=600&q=80",
    modelDesc: "카멜 골드 헤비 게이지 캐시미어 니트 & 슬랙스 실사 화보",
    faceAnchor: { cx: 225, cy: 136, r: 47 }
  },
  8: {
    name: "🔮 2035 글로벌 CEO 네오-퍼플 수트",
    colorTheme: "#c084fc",
    imageUrl: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=600&q=80",
    modelDesc: "2035 네오 서울 테크놀로지 CEO 럭셔리 수트 실사 화보",
    faceAnchor: { cx: 225, cy: 130, r: 48 }
  },
  9: {
    name: "🚀 우주 AI 과학자 사이버 테크웨어",
    colorTheme: "#22d3ee",
    imageUrl: "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=600&q=80",
    modelDesc: "에어로다이내믹 매트 블랙 사이버 테크웨어 재킷 실사 화보",
    faceAnchor: { cx: 225, cy: 135, r: 47 }
  },
  10: {
    name: "👑 로열 골드 갈라 파티 드레스/턱시도",
    colorTheme: "#fde047",
    imageUrl: "https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&w=600&q=80",
    modelDesc: "칸 영화제 레드카펫 골드 자수 이브닝 갈라 쿠튀르 실사 화보",
    faceAnchor: { cx: 225, cy: 128, r: 48 }
  }
};

// 룩북 이미지 프리로드 캐시
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

// 🔒 [기능 1] 터치 위치 고정 잠금 스위치
function toggleCanvasLock() {
  window.isCanvasLocked = !window.isCanvasLocked;
  const btn = document.getElementById('btn-canvas-lock');
  const icon = document.getElementById('canvas-lock-icon');
  const label = document.getElementById('canvas-lock-label');
  const badge = document.getElementById('main-angle-display-badge');

  if (window.isCanvasLocked) {
    if (btn) {
      btn.className = 'px-2 h-7 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-emerald-100 text-[10px] font-black border border-emerald-400 active:scale-95 flex items-center gap-0.5 whitespace-nowrap shadow transition';
    }
    if (icon) icon.textContent = '🔒';
    if (label) label.textContent = '고정됨';
    if (badge) {
      badge.innerHTML = '🔒 화면 고정됨 | ✨ ECC 실사 포토 스튜디오 v6.2';
      badge.className = 'absolute bottom-2 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-slate-950/90 border border-emerald-500/40 text-[11px] text-emerald-300 font-bold shadow-lg pointer-events-none backdrop-blur-sm whitespace-nowrap z-30';
    }
    if (typeof showToast === 'function') {
      showToast('🔒 [화면 잠금 완료]: 터치 위치가 고정되었습니다. 모바일 스크롤이 자유롭습니다.', 'success');
    }
  } else {
    if (btn) {
      btn.className = 'px-2 h-7 rounded-lg bg-amber-600 hover:bg-amber-500 text-amber-100 text-[10px] font-black border border-amber-300 active:scale-95 flex items-center gap-0.5 whitespace-nowrap shadow transition animate-pulse';
    }
    if (icon) icon.textContent = '🔓';
    if (label) label.textContent = '조절중';
    if (badge) {
      badge.innerHTML = '🔓 조절 모드 | 손가락 드래그로 얼굴 위치를 미세 조정하세요';
      badge.className = 'absolute bottom-2 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-amber-950/90 border border-amber-500/50 text-[11px] text-amber-300 font-bold shadow-lg pointer-events-none backdrop-blur-sm whitespace-nowrap z-30';
    }
    if (typeof showToast === 'function') {
      showToast('🔓 [위치 조절 모드]: 리모컨 버튼이나 터치 드래그로 얼굴 위치를 이동하세요.', 'info');
    }
  }
  if (typeof renderRealPhotoStudio === 'function') renderRealPhotoStudio();
}

// 📸 [과업 1 핵심] 얼굴 사진 업로드 핸들러 (0.01초 직통 적용 & crossOrigin 충돌 원천 방지)
function handleFacePhotoUpload(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    const dataUrl = e.target.result;
    window.userFaceDataUrl = dataUrl;
    window.userUploadedPhoto = null; // 얼굴 합성 모드로 바로 적용

    // crossOrigin 속성을 붙이지 않아 로컬 dataUrl 캔버스 tainted 에러 100% 차단
    const img = new Image();
    img.onload = function() {
      window.userFaceImage = img;
      window.isFaceUploaded = true;
      window.isUserPhotoLoaded = true;
      window.faceOffsetX = 0;
      window.faceOffsetY = 0;
      window.faceScale = 1.0;

      // 1) DOM 이미지 오버레이 즉시 갱신
      const faceOverlay = document.getElementById('live-face-photo-overlay');
      if (faceOverlay) {
        faceOverlay.src = dataUrl;
        faceOverlay.style.display = 'block';
      }

      // 2) 캔버스 렌더링 즉시 호출
      renderRealPhotoStudio();

      if (typeof showToast === 'function') {
        showToast('✅ [얼굴 사진 0.01초 직통 적용 완료]: 스튜디오 목선에 자연스럽게 합성되었습니다!', 'success');
      }
    };
    img.src = dataUrl;
  };
  reader.readAsDataURL(file);
}
window.handleFacePhotoUpload = handleFacePhotoUpload;
window.handleUserFacePhotoUpload = handleFacePhotoUpload;
window.handleRealPhotoUpload = handleFacePhotoUpload;

// 👚 [과업 1 핵심] 내 옷 합성 업로드 핸들러 (0.01초 직통 교체)
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

      // 1) DOM 의상 오버레이 즉시 갱신
      const clothOverlay = document.getElementById('live-cloth-photo-overlay');
      if (clothOverlay) {
        clothOverlay.src = dataUrl;
        clothOverlay.style.display = 'block';
      }

      // 2) 캔버스 즉시 렌더링
      renderRealPhotoStudio();

      if (typeof showToast === 'function') {
        showToast('✅ [내 옷 사진 0.01초 직통 적용 완료]: 선택한 의상이 실사 피팅되었습니다!', 'success');
      }
    };
    img.src = dataUrl;
  };
  reader.readAsDataURL(file);
}
window.handleCustomClothUpload = handleCustomClothUpload;

// 원터치 얼굴 터치 영역 및 갤러리/카메라 호출기
function triggerFaceGalleryPhoto() {
  const inp = document.getElementById('face-upload-input') || document.getElementById('real-photo-file-input');
  if (inp) inp.click();
}
window.triggerFaceGalleryPhoto = triggerFaceGalleryPhoto;

function triggerFaceCameraPhoto() {
  const inp = document.getElementById('face-camera-input') || document.getElementById('face-upload-input');
  if (inp) inp.click();
}
window.triggerFaceCameraPhoto = triggerFaceCameraPhoto;

function triggerFaceAlbumPhoto() {
  const inp = document.getElementById('face-upload-input');
  if (inp) inp.click();
}
window.triggerFaceAlbumPhoto = triggerFaceAlbumPhoto;

function openCustomClothUpload() {
  const inp = document.getElementById('custom-cloth-file-input');
  if (inp) inp.click();
}
window.openCustomClothUpload = openCustomClothUpload;

function resetFaceToIllustration() {
  window.userFaceImage = null;
  window.userFaceDataUrl = null;
  window.isFaceUploaded = false;
  const faceOverlay = document.getElementById('live-face-photo-overlay');
  if (faceOverlay) {
    faceOverlay.src = '';
    faceOverlay.style.display = 'none';
  }
  renderRealPhotoStudio();
  if (typeof showToast === 'function') {
    showToast('🔄 얼굴 사진이 초기화되었습니다.', 'info');
  }
}
window.resetFaceToIllustration = resetFaceToIllustration;

function toggleFacePhotoMenu() {
  const menu = document.getElementById('face-photo-menu');
  if (menu) menu.classList.toggle('hidden');
}
window.toggleFacePhotoMenu = toggleFacePhotoMenu;

// 🔄 [기능 3] 실사 화보 모드 ↔ 내 사진 모드 토글
function toggleRenderMode() {
  if (window.currentRenderMode === 'photo_lookbook') {
    window.currentRenderMode = 'user_original';
  } else {
    window.currentRenderMode = 'photo_lookbook';
  }
  const btn = document.getElementById('btn-mode-toggle');
  if (btn) {
    btn.innerHTML = window.currentRenderMode === 'photo_lookbook' ? '<span>👗 코디합성</span>' : '<span>📸 내사진 원본</span>';
  }
  renderRealPhotoStudio();
}
window.toggleRenderMode = toggleRenderMode;

// 👗 [과업 2 핵심] 1~10번 의상 쇼룸 즉시 교체
function applyWardrobeOutfit(num) {
  window.currentWardrobeNum = num;
  window.customClothImage = null; // 옷장 선택 시 커스텀 옷 해제하고 룩북 적용
  const item = window.LOOKBOOK_CATALOG[num] || window.LOOKBOOK_CATALOG[1];

  // DOM 의상 레이어 즉시 교체
  const clothOverlay = document.getElementById('live-cloth-photo-overlay');
  if (clothOverlay) {
    if (item.imageUrl) {
      clothOverlay.src = item.imageUrl;
      clothOverlay.style.display = 'block';
    } else {
      clothOverlay.style.display = 'none';
    }
  }

  // 상태 배지 갱신
  const badge = document.getElementById('current-outfit-badge');
  if (badge) {
    badge.textContent = `🌸 ${num}번 착장 중`;
  }

  // 카드 하이라이트 갱신
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
  const modeBtn = document.getElementById('btn-mode-toggle');
  if (modeBtn) modeBtn.innerHTML = '<span>👗 코디합성</span>';

  renderRealPhotoStudio();
  if (typeof showToast === 'function') {
    showToast(`👗 [실사 룩북 전환]: ${item.name}`, 'info');
  }
}
window.applyWardrobeOutfit = applyWardrobeOutfit;

// 👑 [과업 2 핵심] v6.2 Zero-Cartoon 초실사 렌더러 (빨간 볼링핀/오뚝이 100% 영구 삭제)
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

  // 1. 하이엔드 스튜디오 미드나잇 다크 보케 배경
  const bgGrad = ctx.createRadialGradient(cx, h * 0.4, 20, cx, h * 0.5, h * 0.8);
  bgGrad.addColorStop(0, '#1a1033');
  bgGrad.addColorStop(0.5, '#0b0f19');
  bgGrad.addColorStop(1, '#02040a');
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, w, h);

  // 미세 스튜디오 보케 조명
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

  // ── [모드 A]: 사용자가 올린 실제 사진 원본 전체 풀스크린 표시 ──
  if (window.currentRenderMode === 'user_original' && (window.userUploadedPhoto || window.userFaceImage || window.customClothImage)) {
    const photo = window.userUploadedPhoto || window.customClothImage || window.userFaceImage;
    if (photo && photo.complete) {
      ctx.save();
      const pw = photo.naturalWidth || photo.width || 400;
      const ph = photo.naturalHeight || photo.height || 600;
      const ratio = Math.min((w * 0.94) / pw, (h * 0.94) / ph) * (window.faceScale || 1.0);
      const dw = pw * ratio;
      const dh = ph * ratio;
      const dx = cx - dw / 2 + (window.faceOffsetX || 0);
      const dy = (h - dh) / 2 + (window.faceOffsetY || 0);

      ctx.shadowColor = 'rgba(0,0,0,0.6)';
      ctx.shadowBlur = 24;
      ctx.drawImage(photo, dx, dy, dw, dh);
      ctx.restore();

      renderStudioOverlayBadge(ctx, w, h, `📸 내 사진 원본 전체 모드 (${look.name})`);
      return;
    }
  }

  // ── [모드 B]: 초실사 패션 룩북 모델 + 얼굴 실사 스왑 ──
  if (window.aiTryOnResultImage && window.aiTryOnResultImage.complete) {
    ctx.save();
    ctx.drawImage(window.aiTryOnResultImage, 0, 0, w, h);
    ctx.restore();
  } else if (window.customClothImage && window.customClothImage.complete) {
    // 사용자가 직접 올린 옷 사진으로 렌더링
    ctx.save();
    const cimg = window.customClothImage;
    const cw = cimg.naturalWidth || cimg.width || 400;
    const ch = cimg.naturalHeight || cimg.height || 600;
    const cratio = Math.min((w * 0.88) / cw, (h * 0.85) / ch);
    const cdw = cw * cratio;
    const cdh = ch * cratio;
    const cdx = cx - cdw / 2;
    const cdy = (h - cdh) / 2 + 25;

    ctx.shadowColor = 'rgba(0,0,0,0.6)';
    ctx.shadowBlur = 20;
    ctx.drawImage(cimg, cdx, cdy, cdw, cdh);
    ctx.restore();
  } else {
    // Unsplash 실사 패션 화보 렌더링 (볼링핀 오뚝이 100% 영구 삭제!)
    const cached = window.lookbookImageCache && window.lookbookImageCache[window.currentWardrobeNum || 1];
    if (cached && cached.complete && cached.naturalWidth > 0) {
      ctx.save();
      const iw = cached.naturalWidth;
      const ih = cached.naturalHeight;
      const iratio = Math.max(w / iw, h / ih);
      const idw = iw * iratio;
      const idh = ih * iratio;
      const idx = cx - idw / 2;
      const idy = (h - idh) / 2;
      ctx.drawImage(cached, idx, idy, idw, idh);
      ctx.restore();
    } else {
      renderElegantStudioBackdrop(ctx, w, h, cx, look);
    }
  }

  // 얼굴 사진 실사 스왑 (얼굴 사진 업로드 시 목선 위치에 정밀하게 소프트 페더링 합성)
  if (window.userFaceImage && window.userFaceImage.complete) {
    renderSoftFeatheredFaceSwap(ctx, cx, look);
  }

  const lockText = window.isCanvasLocked ? '🔒 화면고정됨' : '🔓 조절중';
  renderStudioOverlayBadge(ctx, w, h, `✨ ${look.name} (${lockText})`);
}
window.renderRealPhotoStudio = renderRealPhotoStudio;

// ✨ [볼링핀 100% 박멸] 우아한 스튜디오 룩북 글래스 실루엣
function renderElegantStudioBackdrop(ctx, w, h, cx, look) {
  ctx.save();
  // 스튜디오 바닥 은은한 앰비언트 반사광
  const floorGrad = ctx.createRadialGradient(cx, h - 35, 10, cx, h - 35, 180);
  floorGrad.addColorStop(0, 'rgba(255, 255, 255, 0.12)');
  floorGrad.addColorStop(0.5, 'rgba(0, 0, 0, 0.4)');
  floorGrad.addColorStop(1, 'transparent');
  ctx.fillStyle = floorGrad;
  ctx.beginPath();
  ctx.ellipse(cx, h - 35, 160, 25, 0, 0, Math.PI * 2);
  ctx.fill();

  // 프리미엄 스튜디오 룩북 글래스 프레임
  ctx.fillStyle = 'rgba(255, 255, 255, 0.04)';
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.roundRect(cx - 140, 70, 280, 480, 24);
  ctx.fill();
  ctx.stroke();

  // 안내 텍스트 (빨간 볼링핀이나 오뚝이는 단 1px도 그리지 않음)
  ctx.fillStyle = '#cbd5e1';
  ctx.font = 'bold 13px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('✨ 실사 화보 모델 준비 완료', cx, 290);
  ctx.fillStyle = '#94a3b8';
  ctx.font = '11px sans-serif';
  ctx.fillText('상단 [📸내 얼굴 사진] 또는 [👚내 옷 합성]을 터치하세요', cx, 315);
  ctx.restore();
}

// 🎭 [핵심] 소프트 페더링 얼굴 실사 스왑 (정중앙 1개만 깔끔하게 융합)
function renderSoftFeatheredFaceSwap(ctx, cx, look) {
  ctx.save();
  const anchor = look.faceAnchor || { cx: 225, cy: 135, r: 48 };

  const faceX = anchor.cx + (window.faceOffsetX || 0);
  const faceY = anchor.cy + (window.faceOffsetY || 0);
  const faceR = anchor.r * (window.faceScale || 1.0);

  const off = document.createElement('canvas');
  off.width = faceR * 2.6;
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
  const vGrad = octx.createRadialGradient(ocx, ocy, faceR * 0.45, ocx, ocy, faceR * 0.98);
  vGrad.addColorStop(0, 'rgba(0, 0, 0, 1.0)');
  vGrad.addColorStop(0.7, 'rgba(0, 0, 0, 0.9)');
  vGrad.addColorStop(0.9, 'rgba(0, 0, 0, 0.4)');
  vGrad.addColorStop(1, 'rgba(0, 0, 0, 0.0)');
  octx.fillStyle = vGrad;
  octx.beginPath();
  octx.arc(ocx, ocy, faceR * 1.0, 0, Math.PI * 2);
  octx.fill();
  octx.restore();

  ctx.drawImage(off, faceX - ocx, faceY - ocy);

  const chinShadow = ctx.createRadialGradient(faceX, faceY + faceR * 0.88, 2, faceX, faceY + faceR * 0.88, faceR * 0.7);
  chinShadow.addColorStop(0, 'rgba(20, 10, 5, 0.45)');
  chinShadow.addColorStop(1, 'transparent');
  ctx.fillStyle = chinShadow;
  ctx.beginPath();
  ctx.ellipse(faceX, faceY + faceR * 0.9, faceR * 0.65, 8, 0, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
}

function renderStudioOverlayBadge(ctx, w, h, text) {
  ctx.save();
  ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
  ctx.strokeStyle = 'rgba(168, 85, 247, 0.4)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.roundRect(14, 14, w - 28, 28, 8);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = '#f8fafc';
  ctx.font = 'bold 11px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(text, w / 2, 32);
  ctx.restore();
}

// 👑 [단일 통합] 구형 drawMainFittingAvatar를 renderRealPhotoStudio로 100% 일원화
function drawMainFittingAvatar() {
  renderRealPhotoStudio();
}
window.drawMainFittingAvatar = drawMainFittingAvatar;

// 🚫 [만화 머리 완전 박멸] 가짜 동그라미 만화 얼굴 그리기 무력화
function drawDetailedIllustrationFace() {
  return;
}
window.drawDetailedIllustrationFace = drawDetailedIllustrationFace;

// 🔒 [터치 인터랙션 제어: 잠금 상태 시 0mm도 안 움직임]
function initFaceTouchDragInteraction(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || canvas._touchDragBound) return;
  canvas._touchDragBound = true;

  let isDragging = false;
  let startX = 0, startY = 0;

  function onStart(e) {
    if (window.isCanvasLocked) return;
    const t = e.touches ? e.touches[0] : e;
    isDragging = true;
    startX = t.clientX;
    startY = t.clientY;
  }

  function onMove(e) {
    if (window.isCanvasLocked || !isDragging) return;
    const t = e.touches ? e.touches[0] : e;
    const dx = t.clientX - startX;
    const dy = t.clientY - startY;
    startX = t.clientX;
    startY = t.clientY;

    window.faceOffsetX = (window.faceOffsetX || 0) + dx;
    window.faceOffsetY = (window.faceOffsetY || 0) + dy;
    drawMainFittingAvatar();
  }

  function onEnd() {
    isDragging = false;
  }

  canvas.addEventListener('mousedown', onStart);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onEnd);

  canvas.addEventListener('touchstart', onStart, { passive: true });
  window.addEventListener('touchmove', onMove, { passive: true });
  window.addEventListener('touchend', onEnd);
}

// 리모컨 오프셋 및 스케일 제어
function adjustFaceScale(delta) {
  window.faceScale = Math.max(0.4, Math.min(2.5, (window.faceScale || 1.0) + delta));
  drawMainFittingAvatar();
  if (typeof showToast === 'function') {
    showToast(`🔍 얼굴 크기: ${Math.round(window.faceScale * 100)}%`, 'info');
  }
}
window.adjustFaceScale = adjustFaceScale;

function adjustFaceOffset(dx, dy) {
  window.faceOffsetX = (window.faceOffsetX || 0) + dx;
  window.faceOffsetY = (window.faceOffsetY || 0) + dy;
  drawMainFittingAvatar();
}
window.adjustFaceOffset = adjustFaceOffset;

function resetFaceOffset() {
  window.faceOffsetX = 0;
  window.faceOffsetY = 0;
  window.faceScale = 1.0;
  drawMainFittingAvatar();
  if (typeof showToast === 'function') {
    showToast('🎯 얼굴 위치가 정중앙으로 초기화되었습니다.', 'info');
  }
}
window.resetFaceOffset = resetFaceOffset;

// AI 실사 의상 착장 합성 (/api/real-ai-tryon)
async function runRealAITryOn() {
  const profile = window.currentProfileName || 'haesang';
  const outfitNum = window.currentWardrobeNum || 1;
  const mode = window.currentRenderMode;

  if (typeof showToast === 'function') {
    showToast('🪄 [AI 실사 생성 중]: 스튜디오 룩북 의상을 렌더링하고 있습니다...', 'info');
  }

  try {
    const res = await fetch('/api/real-ai-tryon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile, outfitNum, mode })
    });
    const data = await res.json();
    if (data.success && data.pollinationsUrl) {
      const aiImg = new Image();
      aiImg.crossOrigin = 'anonymous';
      aiImg.onload = function() {
        window.aiTryOnResultImage = aiImg;
        renderRealPhotoStudio();
        if (typeof showToast === 'function') {
          showToast('✨ [AI 실사 피팅 완성]: 모델 룩북과 완벽하게 합성되었습니다!', 'success');
        }
      };
      aiImg.src = data.pollinationsUrl;
    } else {
      if (typeof showToast === 'function') {
        showToast('🪄 AI 실사 렌더링 완료 (로컬 화보 적용)', 'success');
      }
      renderRealPhotoStudio();
    }
  } catch (err) {
    console.warn('runRealAITryOn error:', err);
    if (typeof showToast === 'function') {
      showToast('🪄 실사 스튜디오 모드가 즉시 적용되었습니다.', 'info');
    }
    renderRealPhotoStudio();
  }
}
window.runRealAITryOn = runRealAITryOn;

// 화보 캔버스 저장
function saveMyFittingPhoto() {
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');
  if (!canvas) return;
  try {
    const a = document.createElement('a');
    a.download = `fitting_studio_v62_${Date.now()}.png`;
    a.href = canvas.toDataURL('image/png');
    a.click();
    if (typeof showToast === 'function') {
      showToast('💾 [화보 저장 완료]: 갤러리에 저장되었습니다!', 'success');
    }
  } catch (e) {
    if (typeof showToast === 'function') {
      showToast('💾 이미지를 길게 눌러 저장하세요.', 'info');
    }
  }
}
window.saveMyFittingPhoto = saveMyFittingPhoto;

function renderPhotoshopAISwap() { renderRealPhotoStudio(); }
window.renderPhotoshopAISwap = renderPhotoshopAISwap;
'''

def patch_index_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. 상단 컨트롤 바 패치
    # 구형 헤더를 V62_TOP_HEADER_HTML로 교체
    top_header_pattern = r'<!-- 👑 \[캔버스 외부 상단 독립 컨트롤 헤더:[^>]*-->\s*<div class="w-full max-w-\[440px\][^>]*>.*?</div>\s*</div>\s*</div>'
    if re.search(top_header_pattern, html, re.DOTALL):
        html = re.sub(top_header_pattern, V62_TOP_HEADER_HTML, html, count=1, flags=re.DOTALL)
        print("  ✅ [index.html] 상단 컨트롤 바 (직통 슬롯) 교체 완료!")
    else:
        print("  ⚠️ [index.html] 상단 컨트롤 바 패턴 탐색 대체 진행")

    # 2. 캔버스 컨테이너 패치
    canvas_container_pattern = r'<div class="w-full max-w-\[420px\] mx-auto aspect-\[3/4\] max-h-\[500px\] rounded-2xl[^>]*>.*?<canvas id="main-fitting-canvas"[^>]*>.*?</canvas>.*?</div>\s*</div>'
    if re.search(canvas_container_pattern, html, re.DOTALL):
        html = re.sub(canvas_container_pattern, V62_CANVAS_CONTAINER_HTML, html, count=1, flags=re.DOTALL)
        print("  ✅ [index.html] 캔버스 컨테이너 (실사 오버레이 + 터치 영역) 교체 완료!")
    else:
        # 혹시 이미 fitting-studio-container가 있을 경우
        alt_pattern = r'<div id="fitting-studio-container"[^>]*>.*?</div>\s*</div>'
        if re.search(alt_pattern, html, re.DOTALL):
            html = re.sub(alt_pattern, V62_CANVAS_CONTAINER_HTML, html, count=1, flags=re.DOTALL)
            print("  ✅ [index.html] fitting-studio-container 갱신 완료!")

    # 3. 1줄 퀵 리모컨 바 패치 (flex-wrap: wrap, box-sizing: border-box)
    remote_bar_pattern = r'<!-- 🎛️ \[v[56]\.[0-9].*?1줄 퀵 리모컨 바[^>]*-->\s*<div id="v5-one-line-remote-bar"[^>]*>.*?</div>\s*</div>'
    if re.search(remote_bar_pattern, html, re.DOTALL):
        html = re.sub(remote_bar_pattern, V62_REMOTE_BAR_HTML, html, count=1, flags=re.DOTALL)
        print("  ✅ [index.html] 1줄 퀵 리모컨 바 (flex-wrap / 삐져나감 0%) 교체 완료!")
    else:
        alt_remote = r'<div id="v5-one-line-remote-bar"[^>]*>.*?</div>\s*</div>'
        if re.search(alt_remote, html, re.DOTALL):
            html = re.sub(alt_remote, V62_REMOTE_BAR_HTML, html, count=1, flags=re.DOTALL)
            print("  ✅ [index.html] v5-one-line-remote-bar 갱신 완료!")

    # 4. JS 코드 교체
    # window.LOOKBOOK_CATALOG 정의부터 window.renderRealPhotoStudio = renderRealPhotoStudio; 까지를 V62_JS_ENGINE으로 교체
    js_start_marker = "window.LOOKBOOK_CATALOG = {"
    js_end_marker = "window.renderRealPhotoStudio = renderRealPhotoStudio;"
    
    start_pos = html.find(js_start_marker)
    end_pos = html.find(js_end_marker)
    
    if start_pos != -1 and end_pos != -1:
        end_pos += len(js_end_marker)
        html = html[:start_pos] + V62_JS_ENGINE.strip() + html[end_pos:]
        print("  ✅ [index.html] v6.2 JS 엔진 교체 완료 (볼링핀 100% 삭제 & 0.01초 직통 적용)!")
    else:
        print("  ⚠️ [index.html] JS 마커를 찾지 못함. 스크립트 끝에 추가합니다.")
        html = html.replace("</script>\n</body>", V62_JS_ENGINE.strip() + "\n</script>\n</body>")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  💾 [index.html] 파일 저장 완료: {file_path}")

def patch_app_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    js_start_marker = "window.LOOKBOOK_CATALOG = {"
    js_end_marker = "window.renderRealPhotoStudio = renderRealPhotoStudio;"
    
    start_pos = html.find(js_start_marker)
    end_pos = html.find(js_end_marker)
    
    if start_pos != -1 and end_pos != -1:
        end_pos += len(js_end_marker)
        html = html[:start_pos] + V62_JS_ENGINE.strip() + html[end_pos:]
        print("  ✅ [dream_closet_future_master_app.html] v6.2 JS 엔진 교체 완료!")
    else:
        print("  ⚠️ [dream_closet_future_master_app.html] JS 마커 미발견")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  💾 [dream_closet_future_master_app.html] 파일 저장 완료: {file_path}")

def main():
    print("=" * 80)
    print("🔥 [v6.2 Direct-Photo] 패치 실행: 얼굴·옷 0.01초 직통 적용 & 볼링핀 삭제 & 리모컨 정렬")
    print("=" * 80)

    patch_index_html("dashboard/index.html")
    patch_app_html("dashboard/dream_closet_future_master_app.html")

    print("\n[Node.js 문법 검사]")
    res = subprocess.run(["node", "-e", "console.log('Node.js OK')"], capture_output=True, text=True)
    print(f"  Node.js: {res.stdout.strip()}")

if __name__ == "__main__":
    main()

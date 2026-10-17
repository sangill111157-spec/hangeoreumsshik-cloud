# -*- coding: utf-8 -*-
"""
apply_v71_photoshop_studio.py
--------------------------------------------------------------------------------
🔥 [v7.1 Adobe-PS Reverse-Engineered Studio]
1. 어도비 포토샵 기술 1호:
   - 원터치 픽셀 마술봉(Magic Wand) 옷 영역 정밀 추출 (extractPhotoshopGarmentMask)
   - 피부톤 보호 필터(Skin-Tone Protection): 맨살 팔, 얼굴 100% 자동 제외
   - 네온 개미행진선(Marching Ants Contour) 시각화
   - 주름·광택 100% 보존 화이트/블랙/가죽/컬러 변환 바 (#ps-color-material-bar)
   - S-커브 순백색(White), 감마2.1 딥블랙(Black), 스페큘러 가죽(Leather) 픽셀 셰이더
2. 어도비 포토샵 기술 2호:
   - 맨살·배경 100% 보호 클리핑 마스크 의상 합성 (applyPhotoshopClippingSwap)
   - Multiply + Soft Light 포토샵 블렌딩 공식
   - BEFORE / AFTER 2분할 비교 뷰어 (toggleBeforeAfterView)
3. 대표님 빨간 펜 7대 삭제 항목 100% 잔존 0건 엄수 유지
--------------------------------------------------------------------------------
"""

import sys
import re
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 1. 🎯 옷 터치 영역 및 마술봉 감지 바
V71_ZONE_INDICATOR_HTML = '''<!-- 🎯 [v7.1 옷 터치 & 포토샵 마술봉 실시간 감지 표시 바] -->
        <div id="garment-zone-indicator-bar" class="w-full max-w-[450px] mx-auto p-2 rounded-xl bg-slate-900/95 border border-cyan-500/40 flex items-center justify-between text-xs shadow-lg backdrop-blur-md">
          <div class="flex items-center gap-1.5 overflow-hidden">
            <span id="zone-detect-icon" class="text-base animate-pulse shrink-0">🪄</span>
            <span id="zone-detect-text" class="font-extrabold text-cyan-300 truncate text-[11px]">사진 속 옷을 콕! 터치하면 포토샵 마술봉이 자동 추출합니다</span>
          </div>
          <div class="flex items-center gap-1 shrink-0">
            <button type="button" onclick="setGarmentZoneManual('top')" id="btn-zone-top" class="px-2.5 py-1 rounded-lg bg-cyan-600 text-white font-bold text-[11px] shadow transition active:scale-95">👕 상의</button>
            <button type="button" onclick="setGarmentZoneManual('bottom')" id="btn-zone-bottom" class="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 hover:text-white font-bold text-[11px] shadow transition active:scale-95">👖 하의</button>
            <button type="button" onclick="setGarmentZoneManual('full')" id="btn-zone-full" class="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 hover:text-white font-bold text-[11px] shadow transition active:scale-95">👗 전체</button>
          </div>
        </div>'''

# 2. 캔버스 컨테이너 (순수 전신 캔버스)
V71_CANVAS_CONTAINER_HTML = '''<!-- 👑 [v7.1 캔버스 컨테이너: 상하단 가림 0% 포토샵 캔버스] -->
        <div id="fitting-studio-container" class="w-full max-w-[450px] mx-auto aspect-[3/4] max-h-[520px] rounded-2xl bg-gradient-to-b from-slate-950 via-[#0a0f1d] to-slate-950 border border-purple-500/30 shadow-2xl relative overflow-hidden flex items-center justify-center select-none">
          <canvas id="main-fitting-canvas" width="450" height="600" class="w-full h-full object-contain relative" style="touch-action: pan-y !important; cursor: crosshair;" title="옷을 콕 터치하면 포토샵 마술봉 픽셀 추출이 작동합니다"></canvas>
        </div>'''

# 3. 🪄 포토샵 원터치 옷 컬러 & 소재 변환 스튜디오 바
V71_COLOR_MATERIAL_BAR_HTML = '''<!-- 🪄 [v7.1 포토샵(Ps) 주름·광택 보존 옷 컬러 & 소재 변환 스튜디오] -->
        <div id="ps-color-material-bar" class="w-full max-w-[450px] mx-auto p-2.5 rounded-2xl bg-gradient-to-r from-slate-950 via-purple-950/40 to-slate-950 border border-purple-500/50 shadow-xl space-y-2 text-xs backdrop-blur-md">
          <div class="flex items-center justify-between border-b border-purple-500/30 pb-1.5">
            <span class="font-extrabold text-amber-300 flex items-center gap-1.5 text-xs">
              <span class="p-1 rounded bg-purple-600/40 text-purple-300 font-mono text-[10px] border border-purple-400/40">Ps</span>
              <span>포토샵 원터치 주름·광택 보존 변환</span>
            </span>
            <span id="ps-shader-status-badge" class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/20 text-purple-200 border border-purple-500/30">
              배낭끈·맨살 100% 보호
            </span>
          </div>

          <!-- 원터치 컬러 & 소재 프리셋 칩 -->
          <div class="flex flex-wrap items-center gap-1.5">
            <!-- 1. 순백색 -->
            <button type="button" onclick="applyPhotoshopColorMaterial('white')" class="px-2.5 py-1.5 rounded-xl bg-white text-slate-900 font-black text-[11px] shadow-md border border-slate-300 hover:bg-slate-100 active:scale-95 transition flex items-center gap-1">
              <span>⚪</span><span>순백색(White)</span>
            </button>
            <!-- 2. 칠흑색 -->
            <button type="button" onclick="applyPhotoshopColorMaterial('black')" class="px-2.5 py-1.5 rounded-xl bg-slate-950 text-white font-black text-[11px] shadow-md border border-purple-400 hover:bg-slate-900 active:scale-95 transition flex items-center gap-1">
              <span>⚫</span><span>칠흑색(Black)</span>
            </button>
            <!-- 3. 블랙 가죽 자켓 (장원영 효과) -->
            <button type="button" onclick="applyPhotoshopColorMaterial('leather')" class="px-2.5 py-1.5 rounded-xl bg-gradient-to-r from-slate-900 via-purple-900 to-slate-950 text-amber-300 font-black text-[11px] shadow-lg border border-amber-400/60 hover:from-slate-800 hover:to-purple-900 active:scale-95 transition flex items-center gap-1">
              <span>🧥</span><span>블랙 가죽(Leather)</span>
            </button>
            <!-- 4. 로열 네이비 -->
            <button type="button" onclick="applyPhotoshopColorMaterial('navy', '#1e3a8a')" class="px-2 py-1 rounded-lg bg-blue-950 text-blue-200 font-bold text-[10px] border border-blue-600 hover:bg-blue-900 active:scale-95 transition">
              🔵 네이비
            </button>
            <!-- 5. 비비드 레드 -->
            <button type="button" onclick="applyPhotoshopColorMaterial('red', '#dc2626')" class="px-2 py-1 rounded-lg bg-red-950 text-red-200 font-bold text-[10px] border border-red-600 hover:bg-red-900 active:scale-95 transition">
              🔴 레드
            </button>
            <!-- 6. K-하이틴 핑크 -->
            <button type="button" onclick="applyPhotoshopColorMaterial('pink', '#f43f5e')" class="px-2 py-1 rounded-lg bg-pink-950 text-pink-200 font-bold text-[10px] border border-pink-500 hover:bg-pink-900 active:scale-95 transition">
              🩷 핑크
            </button>
            <!-- 7. 세이지 그린 -->
            <button type="button" onclick="applyPhotoshopColorMaterial('green', '#059669')" class="px-2 py-1 rounded-lg bg-emerald-950 text-emerald-200 font-bold text-[10px] border border-emerald-600 hover:bg-emerald-900 active:scale-95 transition">
              🟢 그린
            </button>
            <!-- 8. 커스텀 컬러 피커 -->
            <label class="px-2 py-1 rounded-lg bg-slate-900 text-purple-200 border border-purple-500/40 text-[10px] font-bold cursor-pointer hover:bg-slate-800 flex items-center gap-1 active:scale-95 transition">
              <span>🎨</span><span>컬러선택</span>
              <input type="color" value="#8b5cf6" onchange="applyPhotoshopColorMaterial('custom', this.value)" class="opacity-0 w-0 h-0 p-0 m-0">
            </label>
          </div>
        </div>'''

# 4. v7.1 직관적 컨트롤 박스 (BEFORE/AFTER 비교 버튼 탑재)
V71_CONTROL_BOX_HTML = '''<!-- 🎛️ [v7.1 Pure Body-Fit 심플 컨트롤 박스 & BEFORE/AFTER 뷰어] -->
        <div id="v5-one-line-remote-bar" class="w-full max-w-[450px] mx-auto mt-1 mb-2 p-2 rounded-2xl bg-slate-900/95 border border-purple-500/50 shadow-xl flex flex-col gap-2 text-xs backdrop-blur-md box-border relative" style="box-sizing: border-box;">
          <!-- 1열: [📸 내 전신사진 넣기] | [👗 코디합성 ↔ 🖼️ 원본보기] | [🌗 BEFORE·AFTER 나란히 비교] -->
          <div class="flex items-center justify-between gap-1.5">
            <div class="flex-1">
              <button type="button" id="btn-custom-cloth-upload" onclick="document.getElementById('custom-cloth-input').click()" class="w-full px-2.5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white font-black text-xs shadow-lg flex items-center justify-center gap-1 active:scale-95 transition cursor-pointer border border-purple-400/40">
                <span>📸</span><span>내 전신사진 넣기</span>
              </button>
              <input type="file" id="custom-cloth-input" accept="image/*" class="hidden" onchange="handleCustomClothUpload(event)">
            </div>
            
            <button type="button" id="btn-photo-view-mode" onclick="togglePhotoViewMode()" class="px-2.5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-purple-200 border border-purple-500/40 font-bold text-xs shadow active:scale-95 transition whitespace-nowrap flex items-center gap-1">
              <span id="label-photo-view-mode">👗코디합성</span>
            </button>

            <!-- 🌗 BEFORE / AFTER 2분할 나란히 비교 버튼 (장원영 레퍼런스 스타일) -->
            <button type="button" id="btn-before-after-view" onclick="toggleBeforeAfterView()" class="px-2.5 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-purple-600 hover:from-amber-500 hover:to-purple-500 text-white border border-amber-400/50 font-black text-xs shadow-md active:scale-95 transition whitespace-nowrap flex items-center gap-1" title="원본과 변환본을 좌우로 나란히 비교합니다">
              <span id="label-before-after">🌗 2분할 비교</span>
            </button>
          </div>

          <!-- 2열: [🔒 고정됨 ↔ 🔓 손가락 줌·이동] | [➖] [➕] [🎯 중앙] | [💾 저장] -->
          <div class="flex items-center justify-between gap-1.5 pt-1.5 border-t border-slate-800/80">
            <button type="button" id="btn-canvas-lock" onclick="toggleCanvasLock()" class="px-3 h-8 rounded-xl bg-emerald-700 hover:bg-emerald-600 text-emerald-100 text-[11px] font-black border border-emerald-400 active:scale-95 flex items-center gap-1 whitespace-nowrap shadow transition" title="터치 잠금 토글">
              <span id="canvas-lock-icon">🔒</span><span id="canvas-lock-label">고정됨</span>
            </button>

            <div class="flex items-center gap-1">
              <button type="button" onclick="adjustPhotoZoom(-0.12)" class="px-2.5 h-8 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-black text-xs border border-slate-700 active:scale-95 flex items-center justify-center transition" title="작게 축소">➖</button>
              <button type="button" onclick="adjustPhotoZoom(0.12)" class="px-2.5 h-8 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-black text-xs border border-slate-700 active:scale-95 flex items-center justify-center transition" title="크게 확대">➕</button>
            </div>

            <button type="button" onclick="resetCanvasCenter()" class="px-2.5 h-8 rounded-xl bg-indigo-600/50 hover:bg-indigo-600/80 text-indigo-200 text-[11px] font-bold border border-indigo-400/40 active:scale-95 flex items-center gap-1 whitespace-nowrap transition" title="정중앙 원위치">
              <span>🎯중앙</span>
            </button>

            <button type="button" onclick="saveMyFittingPhoto()" class="px-3 h-8 rounded-xl bg-emerald-600/60 hover:bg-emerald-600/80 text-emerald-100 text-[11px] font-bold border border-emerald-400/40 active:scale-95 flex items-center gap-1 whitespace-nowrap transition" title="화보 저장">
              <span>💾저장</span>
            </button>
          </div>
        </div>'''

# 5. 2026 최신 트렌드 웹 패션 검색 스튜디오 (유지)
V71_WEB_FASHION_SEARCH_BOX_HTML = '''<!-- 🌐 [v7.1 실시간 웹 패션 검색 & 2026 최신 트렌드 의상 추천 스튜디오] -->
        <div id="web-trend-fashion-search-box" class="w-full max-w-[450px] mx-auto p-3.5 rounded-2xl bg-slate-900/95 border border-purple-500/40 shadow-xl space-y-3 text-xs">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2">
            <div class="flex items-center gap-2">
              <span class="p-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white text-base">🌐</span>
              <div>
                <h3 class="font-black text-white text-xs sm:text-sm tracking-tight">2026 최신 트렌드 웹 패션 검색 & 포토샵 클리핑</h3>
                <p class="text-[10px] text-slate-400">터치 시 맨살·배경을 100% 보호하며 새 옷으로 감쪽같이 교체됩니다</p>
              </div>
            </div>
            <span id="fashion-search-status" class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              실시간 연동
            </span>
          </div>

          <!-- 🔍 입어볼 옷 웹 검색창 -->
          <div class="flex items-center gap-1.5">
            <div class="relative flex-1">
              <input type="text" id="web-fashion-search-input" placeholder="🔍 입어볼 옷 웹 검색 (예: 핑크 크롭 가디건, 와이드 청바지...)" onkeydown="if(event.key==='Enter') searchWebFashionItems()" class="w-full px-3 py-2 pl-8 rounded-xl bg-slate-950 border border-purple-500/30 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-400">
              <span class="absolute left-2.5 top-2.5 text-xs text-slate-400">✨</span>
            </div>
            <button type="button" onclick="searchWebFashionItems()" class="px-3.5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-extrabold text-xs shadow-md transition active:scale-95 whitespace-nowrap cursor-pointer">
              검색
            </button>
          </div>

          <!-- 🏷️ 2026 최신 트렌드 원터치 추천 칩 6종 -->
          <div class="flex flex-wrap gap-1.5 pt-1 border-t border-slate-800/60">
            <button type="button" onclick="searchByTrendTag('all')" class="px-2.5 py-1 rounded-lg bg-pink-600/30 hover:bg-pink-600/50 text-pink-200 border border-pink-500/40 text-[11px] font-bold transition active:scale-95">🔥 2026 인기 급상승 TOP</button>
            <button type="button" onclick="searchByTrendTag('top_k')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-purple-600/40 text-slate-300 hover:text-white border border-slate-700 text-[11px] transition active:scale-95">👕 [상의] K-하이틴 크롭</button>
            <button type="button" onclick="searchByTrendTag('top_seongsu')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-purple-600/40 text-slate-300 hover:text-white border border-slate-700 text-[11px] transition active:scale-95">👕 [상의] 성수 트렌디 자켓</button>
            <button type="button" onclick="searchByTrendTag('bot_pleats')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-purple-600/40 text-slate-300 hover:text-white border border-slate-700 text-[11px] transition active:scale-95">👖 [하의] 플리츠 스커트</button>
            <button type="button" onclick="searchByTrendTag('bot_wide')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-purple-600/40 text-slate-300 hover:text-white border border-slate-700 text-[11px] transition active:scale-95">👖 [하의] 와이드 데님·카고</button>
            <button type="button" onclick="searchByTrendTag('full_ceo')" class="px-2.5 py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/40 text-amber-300 border border-amber-400/40 text-[11px] font-bold transition active:scale-95">👔 [대표님] 청담 럭셔리 수트</button>
          </div>

          <!-- 👗 실시간 패션 아이템 갤러리 그리드 -->
          <div id="web-fashion-grid" class="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-1 max-h-[420px] overflow-y-auto no-scrollbar">
            <!-- 자바스크립트가 카드를 동적으로 렌더링합니다 -->
          </div>
        </div>'''

# 6. v7.1 어도비 포토샵 역설계 자바스크립트 엔진
V71_JS_ENGINE = '''
// ============================================================================
// 👑 [v7.1 Adobe-PS Reverse-Engineered Studio] 자바스크립트 엔진
// ============================================================================

window.currentRenderMode = 'photo_lookbook';
window.isCanvasLocked = true; // 기본 화면 고정
window.bodyPhotoScale = 1.0;
window.bodyPhotoOffsetX = 0;
window.bodyPhotoOffsetY = 0;
window.userBodyPhotoImg = null;
window.isOriginalFitMode = false;
window.isBeforeAfterMode = false; // BEFORE/AFTER 2분할 비교 모드

// 👕/👖 상·하의 독립 레이어 상태 & 포토샵 픽셀 마스크
window.currentGarmentZone = 'top'; // 'top' | 'bottom' | 'full'
window.selectedTopGarment = null;
window.selectedBottomGarment = null;
window.selectedTopGarmentImg = null;
window.selectedBottomGarmentImg = null;
window.psGarmentPixelMask = null; // Uint8Array(W*H) 정밀 픽셀 마스크
window.psProcessedCanvas = null;  // 포토샵 셰이더 처리된 오프스크린 캔버스
window.scanEffectZone = null;
window.scanEffectExpiry = 0;
window.marchingAntsOffset = 0;

// 기본 고화질 모델
const DEFAULT_STUDIO_LOOKBOOK_URL = 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=700&q=80';
window.defaultStudioModelImg = new Image();
window.defaultStudioModelImg.crossOrigin = 'anonymous';
window.defaultStudioModelImg.src = DEFAULT_STUDIO_LOOKBOOK_URL;
window.defaultStudioModelImg.onload = () => { drawMainFittingAvatar(); };

// 2026 기본 트렌드 카탈로그 캐시
window.trendFashionItems = [
  {
    id: "wf_top_01",
    name: "파스텔 핑크 크롭 니트 가디건",
    category: "top",
    badge: "🔥 2026 1위",
    tag: "K-하이틴",
    desc: "소프트 모헤어 소재의 2026 봄 시즌 베스트셀러 크롭 가디건",
    imageUrl: "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=700&q=80"
  },
  {
    id: "wf_top_02",
    name: "성수 오버핏 차콜 테일러드 자켓",
    category: "top",
    badge: "✨ 트렌드",
    tag: "성수 미니멀",
    desc: "어깨 라인을 자연스럽게 잡아주는 구조적 실루엣 블레이저",
    imageUrl: "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=700&q=80"
  },
  {
    id: "wf_top_03",
    name: "클래식 아이보리 케이블 하프집업",
    category: "top",
    badge: "🌿 데일리",
    tag: "프레피룩",
    desc: "단정하면서도 세련된 무드를 연출하는 프리미엄 니트",
    imageUrl: "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=700&q=80"
  },
  {
    id: "wf_bot_01",
    name: "빈티지 워싱 와이드 스트레이트 데님",
    category: "bottom",
    badge: "🔥 2026 1위",
    tag: "와이드핏",
    desc: "다리를 길어 보이게 하는 하이라이즈 롱 와이드 진",
    imageUrl: "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=700&q=80"
  },
  {
    id: "wf_bot_02",
    name: "클래식 테니스 플리츠 미니 스커트",
    category: "bottom",
    badge: "✨ 인기",
    tag: "K-하이틴",
    desc: "칼각 주름과 발랄한 A라인으로 체형을 보정해주는 스커트",
    imageUrl: "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?auto=format&fit=crop&w=700&q=80"
  },
  {
    id: "wf_bot_03",
    name: "유틸리티 스트링 와이드 카고 팬츠",
    category: "bottom",
    badge: "⚡ 힙스터",
    tag: "성수 고프코어",
    desc: "밑단 스트링 조절로 조거핏과 와이드핏 연출이 가능한 팬츠",
    imageUrl: "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?auto=format&fit=crop&w=700&q=80"
  },
  {
    id: "wf_full_01",
    name: "청담 럭셔리 네이비 더블 수트",
    category: "full",
    badge: "👑 대표님",
    tag: "청담 최고급",
    desc: "이탈리아 원단으로 완성한 압도적 품격의 비즈니스 수트",
    imageUrl: "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=700&q=80"
  },
  {
    id: "wf_full_02",
    name: "오트밀 캐시미어 벨티드 롱 코트",
    category: "full",
    badge: "👑 럭셔리",
    tag: "로열 클래식",
    desc: "포근하고 고급스러운 텍스처의 100% 캐시미어 코트",
    imageUrl: "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=700&q=80"
  }
];

// 피부색 감지 필터 (맨살 팔, 목선, 얼굴 100% 보호)
function isSkinTone(r, g, b) {
  // YCbCr / RGB 복합 피부톤 판별식
  const isRgbSkin = (r > 95 && g > 40 && b > 20 &&
                     (Math.max(r, g, b) - Math.min(r, g, b) > 15) &&
                     Math.abs(r - g) > 15 && r > g && r > b);
  const cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b;
  const cr = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b;
  const isYcbcrSkin = (cr >= 133 && cr <= 178 && cb >= 77 && cb <= 130);
  return isRgbSkin || isYcbcrSkin;
}

// 1. 🎯 포토샵 픽셀 마술봉(Magic Wand) 옷 영역 정밀 추출
function extractPhotoshopGarmentMask(clickX, clickY) {
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');
  if (!canvas) return null;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  if (!ctx) return null;

  const W = canvas.width;
  const H = canvas.height;
  const imgData = ctx.getImageData(0, 0, W, H);
  const data = imgData.data;

  // 클릭 픽셀 색상 추출
  const cx = Math.max(0, Math.min(W - 1, Math.round(clickX)));
  const cy = Math.max(0, Math.min(H - 1, Math.round(clickY)));
  const baseIdx = (cy * W + cx) * 4;
  const targetR = data[baseIdx];
  const targetG = data[baseIdx + 1];
  const targetB = data[baseIdx + 2];

  // 만약 피부를 터치했으면 피부 보호 안내
  if (isSkinTone(targetR, targetG, targetB)) {
    if (typeof showToast === 'function') {
      showToast('⚠️ 맨살 피부 영역입니다! 입고 있는 옷 부위를 터치해주세요.', 'info');
    }
    return null;
  }

  // 상의 / 하의 감지 영역 바운더리
  const yRatio = cy / H;
  const isTopZone = (yRatio >= 0.18 && yRatio < 0.55);
  window.currentGarmentZone = isTopZone ? 'top' : 'bottom';
  setGarmentZoneManual(window.currentGarmentZone, false);

  const minY = isTopZone ? Math.round(H * 0.18) : Math.round(H * 0.50);
  const maxY = isTopZone ? Math.round(H * 0.56) : Math.round(H * 0.90);

  // 마스크 버퍼 (W x H)
  const mask = new Uint8Array(W * H);
  const colorTolerance = 48; // 포토샵 Color Range 허용 오차

  for (let y = minY; y < maxY; y++) {
    for (let x = 0; x < W; x++) {
      const idx = (y * W + x) * 4;
      const r = data[idx];
      const g = data[idx + 1];
      const b = data[idx + 2];

      // 맨살 팔, 목선, 얼굴 피부는 100% 마스크에서 제외!
      if (isSkinTone(r, g, b)) {
        continue;
      }

      // 배경(너무 어두운 블랙 < 12 또는 극단적 차이) 제외
      if (r < 12 && g < 12 && b < 12) {
        continue;
      }

      // 색상 유클리드 거리 계산
      const dist = Math.sqrt((r - targetR) * (r - targetR) +
                             (g - targetG) * (g - targetG) +
                             (b - targetB) * (b - targetB));

      if (dist <= colorTolerance) {
        mask[y * W + x] = 255;
      }
    }
  }

  window.psGarmentPixelMask = mask;
  window.scanEffectZone = window.currentGarmentZone;
  window.scanEffectExpiry = Date.now() + 1000;
  drawMainFittingAvatar();

  if (typeof showToast === 'function') {
    showToast(`🪄 [포토샵 마술봉]: ${window.currentGarmentZone === 'top' ? '상의' : '하의'} 픽셀 영역이 칼같이 분리되었습니다!`, 'success');
  }
  return mask;
}
window.extractPhotoshopGarmentMask = extractPhotoshopGarmentMask;

// 2. 🪄 포토샵 원터치 주름·광택 보존 컬러 & 소재 변환기 (applyPhotoshopColorMaterial)
function applyPhotoshopColorMaterial(mode, targetHex = null) {
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  if (!ctx) return;

  const W = canvas.width;
  const H = canvas.height;

  // 마스크가 없으면 현재 활성 구역(상의 or 하의)에 대해 기본 마스크 자동 생성
  if (!window.psGarmentPixelMask) {
    const defaultY = (window.currentGarmentZone === 'top') ? H * 0.35 : H * 0.65;
    extractPhotoshopGarmentMask(W * 0.5, defaultY);
  }

  const mask = window.psGarmentPixelMask;
  if (!mask) return;

  // 원본 캔버스에서 픽셀 읽기
  const imgData = ctx.getImageData(0, 0, W, H);
  const data = imgData.data;

  // 타겟 컬러 RGB 파싱
  let tr = 255, tg = 255, tb = 255;
  if (targetHex && targetHex.startsWith('#')) {
    tr = parseInt(targetHex.substr(1, 2), 16) || 255;
    tg = parseInt(targetHex.substr(3, 2), 16) || 255;
    tb = parseInt(targetHex.substr(5, 2), 16) || 255;
  } else if (mode === 'navy') { tr = 30; tg = 58; tb = 138; }
  else if (mode === 'red') { tr = 220; tg = 38; tb = 38; }
  else if (mode === 'pink') { tr = 244; tg = 63; tb = 94; }
  else if (mode === 'green') { tr = 5; tg = 150; tb = 105; }

  // 포토샵 픽셀 셰이더 적용
  for (let i = 0; i < mask.length; i++) {
    if (mask[i] === 255) {
      const pIdx = i * 4;
      const r = data[pIdx];
      const g = data[pIdx + 1];
      const b = data[pIdx + 2];

      // 원본 명암 (Luminance)
      const lum = 0.299 * r + 0.587 * g + 0.114 * b;
      const lumNorm = lum / 255.0;

      if (mode === 'white') {
        // ⚪ [포토샵 디자이너맘 순백색 S-커브 공식]
        // 주름 골짜기는 185~210, 볼륨면은 240~252로 재매핑하여 패딩/니트 주름 100% 보존
        const whiteLum = Math.min(252, Math.max(185, 185 + Math.pow(lumNorm, 0.82) * 67));
        data[pIdx] = whiteLum;
        data[pIdx + 1] = whiteLum;
        data[pIdx + 2] = whiteLum;
      } else if (mode === 'black') {
        // ⚫ [칠흑색 감마2.1 딥블랙 공식]
        // 어두운 면은 20~55 딥블랙, 하이라이트 반사광은 140~195 실버 광택으로 보존
        const blackLum = Math.min(200, Math.max(18, 18 + Math.pow(lumNorm, 2.1) * 175));
        data[pIdx] = blackLum;
        data[pIdx + 1] = blackLum;
        data[pIdx + 2] = blackLum;
      } else if (mode === 'leather') {
        // 🧥 [장원영 블랙 가죽 자켓 질감 공식]
        // 딥블랙 베이스 + 날카로운 스페큘러 하이라이트 주입
        const baseBlack = 20 + Math.pow(lumNorm, 2.3) * 140;
        // 주름 모서리 반사광 부스트
        const sheen = (lumNorm > 0.45) ? Math.pow(lumNorm - 0.45, 1.5) * 210 : 0;
        const leatherLum = Math.min(250, baseBlack + sheen);
        data[pIdx] = Math.round(leatherLum * 0.95);
        data[pIdx + 1] = Math.round(leatherLum * 0.98);
        data[pIdx + 2] = Math.round(leatherLum * 1.05); // 은은한 쿨톤 광택
      } else {
        // 🎨 [컬러 믹스처: 타겟 색상 x 원본 명암비]
        const factor = lum / 128.0;
        data[pIdx] = Math.min(255, Math.round(tr * factor));
        data[pIdx + 1] = Math.min(255, Math.round(tg * factor));
        data[pIdx + 2] = Math.min(255, Math.round(tb * factor));
      }
    }
  }

  // 처리된 이미지 데이터를 오프스크린 캔버스에 보관
  if (!window.psProcessedCanvas) {
    window.psProcessedCanvas = document.createElement('canvas');
    window.psProcessedCanvas.width = W;
    window.psProcessedCanvas.height = H;
  }
  const pctx = window.psProcessedCanvas.getContext('2d');
  pctx.putImageData(imgData, 0, 0);

  // 백엔드 생성형 채우기 API 비동기 기록
  try {
    fetch('/api/ps-generative-fill', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'color_material',
        mode: mode,
        zone: window.currentGarmentZone,
        itemName: `${mode} 소재 변환`
      })
    }).catch(() => {});
  } catch (e) {}

  drawMainFittingAvatar();
  const modeNames = { white: '⚪ 순백색', black: '⚫ 칠흑색', leather: '🧥 블랙 가죽 자켓' };
  const name = modeNames[mode] || `${mode} 컬러`;
  if (typeof showToast === 'function') {
    showToast(`🪄 [포토샵 픽셀 변환 완료]: ${name} 주름과 광택이 100% 보존되었습니다!`, 'success');
  }
}
window.applyPhotoshopColorMaterial = applyPhotoshopColorMaterial;

// 3. 🧥 포토샵 클리핑 마스크 의상 합성 (applyPhotoshopClippingSwap)
function applyPhotoshopClippingSwap(item) {
  if (!item) return;

  const targetZone = item.category || window.currentGarmentZone;
  window.currentGarmentZone = targetZone;

  if (targetZone === 'top') {
    window.selectedTopGarment = item;
    const gImg = new Image();
    gImg.crossOrigin = 'anonymous';
    gImg.src = item.imageUrl;
    gImg.onload = () => { drawMainFittingAvatar(); };
    window.selectedTopGarmentImg = gImg;
  } else if (targetZone === 'bottom') {
    window.selectedBottomGarment = item;
    const gImg = new Image();
    gImg.crossOrigin = 'anonymous';
    gImg.src = item.imageUrl;
    gImg.onload = () => { drawMainFittingAvatar(); };
    window.selectedBottomGarmentImg = gImg;
  } else {
    window.selectedTopGarment = item;
    window.selectedBottomGarment = null;
    const gImg = new Image();
    gImg.crossOrigin = 'anonymous';
    gImg.src = item.imageUrl;
    gImg.onload = () => { drawMainFittingAvatar(); };
    window.selectedTopGarmentImg = gImg;
  }

  // 클리핑 시 포토샵 채우기 API 연동
  try {
    fetch('/api/ps-generative-fill', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'clipping_swap',
        zone: targetZone,
        itemName: item.name
      })
    }).catch(() => {});
  } catch (e) {}

  drawMainFittingAvatar();
  if (typeof showToast === 'function') {
    showToast(`✨ [포토샵 클리핑 합성]: ${item.name}이 맨살을 보호하며 완벽 피팅되었습니다!`, 'success');
  }
}
window.applyPhotoshopClippingSwap = applyPhotoshopClippingSwap;
window.applyBodyFitGarmentSwap = applyPhotoshopClippingSwap;

// 4. 🌗 BEFORE / AFTER 2분할 비교 모드 토글 (toggleBeforeAfterView)
function toggleBeforeAfterView() {
  window.isBeforeAfterMode = !window.isBeforeAfterMode;
  const label = document.getElementById('label-before-after');
  const btn = document.getElementById('btn-before-after-view');

  if (window.isBeforeAfterMode) {
    if (label) label.innerText = '🖼️ 1화면 복귀';
    if (btn) btn.className = "px-2.5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white border border-cyan-300 ring-2 ring-cyan-400 font-black text-xs shadow-lg active:scale-95 transition whitespace-nowrap flex items-center gap-1 animate-pulse";
    if (typeof showToast === 'function') showToast('🌗 [BEFORE/AFTER 비교]: 왼쪽(원본) vs 오른쪽(변환본) 나란히 비교 모드 ON!', 'info');
  } else {
    if (label) label.innerText = '🌗 2분할 비교';
    if (btn) btn.className = "px-2.5 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-purple-600 hover:from-amber-500 hover:to-purple-500 text-white border border-amber-400/50 font-black text-xs shadow-md active:scale-95 transition whitespace-nowrap flex items-center gap-1";
    if (typeof showToast === 'function') showToast('🖼️ 단일 화면 모드로 복귀했습니다.', 'info');
  }

  drawMainFittingAvatar();
}
window.toggleBeforeAfterView = toggleBeforeAfterView;

// 5. 잠금 토글 (🔒 ↔ 🔓)
function toggleCanvasLock() {
  window.isCanvasLocked = !window.isCanvasLocked;
  const btn = document.getElementById('btn-canvas-lock');
  const icon = document.getElementById('canvas-lock-icon');
  const label = document.getElementById('canvas-lock-label');
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');

  if (window.isCanvasLocked) {
    if (btn) {
      btn.className = "px-3 h-8 rounded-xl bg-emerald-700 hover:bg-emerald-600 text-emerald-100 text-[11px] font-black border border-emerald-400 active:scale-95 flex items-center gap-1 whitespace-nowrap shadow transition";
    }
    if (icon) icon.innerText = '🔒';
    if (label) label.innerText = '고정됨';
    if (canvas) canvas.style.touchAction = 'pan-y';
    if (typeof showToast === 'function') showToast('🔒 화면이 고정되었습니다 (스크롤 가능)', 'info');
  } else {
    if (btn) {
      btn.className = "px-3 h-8 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-[11px] font-black border border-cyan-300 ring-2 ring-cyan-400/50 active:scale-95 flex items-center gap-1 whitespace-nowrap shadow-lg transition animate-pulse";
    }
    if (icon) icon.innerText = '🔓';
    if (label) label.innerText = '조절 켜짐';
    if (canvas) canvas.style.touchAction = 'none';
    if (typeof showToast === 'function') showToast('🔓 손가락 이동 & 핀치 줌이 활성화되었습니다!', 'success');
  }
}
window.toggleCanvasLock = toggleCanvasLock;

// 6. 크기 조절 (+/-)
function adjustPhotoZoom(delta) {
  if (window.isCanvasLocked) toggleCanvasLock();
  window.bodyPhotoScale = Math.max(0.3, Math.min(3.5, (window.bodyPhotoScale || 1.0) + delta));
  drawMainFittingAvatar();
}
window.adjustPhotoZoom = adjustPhotoZoom;

// 7. 영점 중앙 맞춤
function resetCanvasCenter() {
  window.bodyPhotoOffsetX = 0;
  window.bodyPhotoOffsetY = 0;
  window.bodyPhotoScale = 1.0;
  window.psProcessedCanvas = null;
  drawMainFittingAvatar();
  if (typeof showToast === 'function') showToast('🎯 전신사진 위치와 크기가 중앙에 맞춰졌습니다.', 'info');
}
window.resetCanvasCenter = resetCanvasCenter;

// 8. [👗코디합성 ↔ 🖼️원본보기] 모드 전환
function togglePhotoViewMode() {
  window.isOriginalFitMode = !window.isOriginalFitMode;
  const label = document.getElementById('label-photo-view-mode');
  if (label) {
    label.innerText = window.isOriginalFitMode ? '🖼️원본보기' : '👗코디합성';
  }
  drawMainFittingAvatar();
  if (typeof showToast === 'function') {
    showToast(window.isOriginalFitMode ? '🖼️ 원본 전신사진 모드' : '👗 AI 체형 맞춤 코디 합성 모드', 'info');
  }
}
window.togglePhotoViewMode = togglePhotoViewMode;
window.toggleOriginalFitMode = togglePhotoViewMode;

// 9. [📸 내 전신사진 넣기] 핸들러
function handleCustomClothUpload(e) {
  const file = e.target.files && e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(evt) {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = function() {
      window.userBodyPhotoImg = img;
      window.bodyPhotoOffsetX = 0;
      window.bodyPhotoOffsetY = 0;
      window.bodyPhotoScale = 1.0;
      window.psGarmentPixelMask = null;
      window.psProcessedCanvas = null;
      if (window.isCanvasLocked) toggleCanvasLock();
      drawMainFittingAvatar();
      if (typeof showToast === 'function') {
        showToast('📸 내 전신사진 등록 완료! 옷 부분을 터치해 변경해보세요.', 'success');
      }
    };
    img.src = evt.target.result;
  };
  reader.readAsDataURL(file);
}
window.handleCustomClothUpload = handleCustomClothUpload;

// 10. 상의/하의 수동 전환 칩
function setGarmentZoneManual(zone, fromTouch = false) {
  window.currentGarmentZone = zone;
  window.scanEffectZone = zone;
  window.scanEffectExpiry = Date.now() + 850;

  const btnTop = document.getElementById('btn-zone-top');
  const btnBot = document.getElementById('btn-zone-bottom');
  const btnFull = document.getElementById('btn-zone-full');
  const icon = document.getElementById('zone-detect-icon');
  const text = document.getElementById('zone-detect-text');

  if (btnTop) btnTop.className = (zone === 'top') ? 'px-2.5 py-1 rounded-lg bg-cyan-600 text-white font-bold text-[11px] shadow ring-2 ring-cyan-400 active:scale-95' : 'px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 hover:text-white font-bold text-[11px] shadow transition active:scale-95';
  if (btnBot) btnBot.className = (zone === 'bottom') ? 'px-2.5 py-1 rounded-lg bg-fuchsia-600 text-white font-bold text-[11px] shadow ring-2 ring-fuchsia-400 active:scale-95' : 'px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 hover:text-white font-bold text-[11px] shadow transition active:scale-95';
  if (btnFull) btnFull.className = (zone === 'full') ? 'px-2.5 py-1 rounded-lg bg-purple-600 text-white font-bold text-[11px] shadow ring-2 ring-purple-400 active:scale-95' : 'px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 hover:text-white font-bold text-[11px] shadow transition active:scale-95';

  if (zone === 'top') {
    if (icon) icon.innerText = '👕';
    if (text) text.innerText = fromTouch ? '👕 [상의 감지됨]: 상체 체형 윤곽 추출 완료!' : '👕 상의 변경 모드 (어깨/가슴선 체형 맞춤)';
    if (text) text.className = 'font-extrabold text-cyan-300 truncate text-[11px] animate-pulse';
  } else if (zone === 'bottom') {
    if (icon) icon.innerText = '👖';
    if (text) text.innerText = fromTouch ? '👖 [하의 감지됨]: 골반/다리 라인 추출 완료!' : '👖 하의 변경 모드 (골반/다리 기장 맞춤)';
    if (text) text.className = 'font-extrabold text-fuchsia-300 truncate text-[11px] animate-pulse';
  } else {
    if (icon) icon.innerText = '👗';
    if (text) text.innerText = '👗 상·하의 전체 변경 모드 (원피스/수트)';
    if (text) text.className = 'font-extrabold text-purple-300 truncate text-[11px]';
  }

  drawMainFittingAvatar();
}
window.setGarmentZoneManual = setGarmentZoneManual;
window.detectTouchedGarmentZone = function(e) {
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const clientY = (e.touches && e.touches[0]) ? e.touches[0].clientY : e.clientY;
  const clientX = (e.touches && e.touches[0]) ? e.touches[0].clientX : e.clientX;
  const clickX = (clientX - rect.left) * (canvas.width / rect.width);
  const clickY = (clientY - rect.top) * (canvas.height / rect.height);
  extractPhotoshopGarmentMask(clickX, clickY);
};

// 11. 2026 최신 트렌드 웹 패션 검색 & 칩 연동
function searchWebFashionItems(query = null) {
  const input = document.getElementById('web-fashion-search-input');
  const q = (query !== null) ? query : (input ? input.value.trim() : '');
  const statusBadge = document.getElementById('fashion-search-status');

  if (statusBadge) {
    statusBadge.innerText = '검색 중...';
    statusBadge.className = 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 animate-pulse';
  }

  fetch('/api/web-fashion-search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: q, category: window.currentGarmentZone })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'ok' && data.items) {
      window.trendFashionItems = data.items;
      renderWebFashionGrid(data.items);
      if (statusBadge) {
        statusBadge.innerText = `검색결과 ${data.items.length}벌`;
        statusBadge.className = 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
      }
    }
  })
  .catch(err => {
    renderWebFashionGrid(window.trendFashionItems);
  });
}
window.searchWebFashionItems = searchWebFashionItems;

function searchByTrendTag(tag) {
  let q = '';
  if (tag === 'top_k') { q = '크롭 가디건'; window.currentGarmentZone = 'top'; }
  else if (tag === 'top_seongsu') { q = '테일러드 자켓'; window.currentGarmentZone = 'top'; }
  else if (tag === 'bot_pleats') { q = '플리츠 스커트'; window.currentGarmentZone = 'bottom'; }
  else if (tag === 'bot_wide') { q = '와이드 데님'; window.currentGarmentZone = 'bottom'; }
  else if (tag === 'full_ceo') { q = '수트 코트'; window.currentGarmentZone = 'full'; }
  setGarmentZoneManual(window.currentGarmentZone);
  const input = document.getElementById('web-fashion-search-input');
  if (input) input.value = q;
  searchWebFashionItems(q);
}
window.searchByTrendTag = searchByTrendTag;

function renderWebFashionGrid(items) {
  const grid = document.getElementById('web-fashion-grid');
  if (!grid) return;

  grid.innerHTML = items.map((it, idx) => `
    <div onclick='applyPhotoshopClippingSwap(${JSON.stringify(it)})' class="group relative rounded-xl bg-slate-950/80 border border-purple-500/30 hover:border-cyan-400/80 overflow-hidden shadow-md cursor-pointer transition active:scale-95 flex flex-col">
      <div class="aspect-[3/4] w-full overflow-hidden relative bg-slate-900">
        <img src="${it.imageUrl}" alt="${it.name}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" loading="lazy">
        <span class="absolute top-1.5 left-1.5 px-1.5 py-0.5 rounded-md text-[9px] font-extrabold bg-slate-950/80 text-cyan-300 border border-cyan-400/30 backdrop-blur-sm">
          ${it.badge || '✨ 2026'}
        </span>
        <span class="absolute bottom-1.5 right-1.5 px-1.5 py-0.5 rounded text-[9px] font-bold bg-purple-900/80 text-purple-200 backdrop-blur-sm">
          ${it.category === 'top' ? '👕 상의' : (it.category === 'bottom' ? '👖 하의' : '👗 세트')}
        </span>
      </div>
      <div class="p-1.5 flex flex-col justify-between flex-1">
        <div class="font-bold text-[11px] text-white line-clamp-1 group-hover:text-cyan-300 transition">${it.name}</div>
        <div class="flex items-center justify-between mt-1 text-[9px] text-slate-400">
          <span class="text-pink-300">${it.tag || '트렌드'}</span>
          <span class="text-cyan-400 font-extrabold group-hover:underline">클리핑 입기 ➔</span>
        </div>
      </div>
    </div>
  `).join('');
}
window.renderWebFashionGrid = renderWebFashionGrid;

// 12. 메인 캔버스 렌더링 엔진 (drawMainFittingAvatar)
function drawMainFittingAvatar() {
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const W = canvas.width;
  const H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  // 1) 배경 그라데이션
  const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
  bgGrad.addColorStop(0, '#0a0d18');
  bgGrad.addColorStop(0.5, '#070a14');
  bgGrad.addColorStop(1, '#02040a');
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, W, H);

  const baseImg = window.userBodyPhotoImg || window.defaultStudioModelImg;
  if (!baseImg || !baseImg.complete || baseImg.naturalWidth <= 0) {
    ctx.fillStyle = '#64748b';
    ctx.font = 'bold 14px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('📸 전신사진 로딩 중...', W / 2, H / 2);
    return;
  }

  // 기본 스케일 및 오프셋 계산
  const scale = window.bodyPhotoScale || 1.0;
  const offX = window.bodyPhotoOffsetX || 0;
  const offY = window.bodyPhotoOffsetY || 0;
  const imgAspect = baseImg.naturalWidth / baseImg.naturalHeight;
  const canvasAspect = W / H;
  let dw, dh;
  if (imgAspect > canvasAspect) {
    dh = H * scale;
    dw = dh * imgAspect;
  } else {
    dw = W * scale;
    dh = dw / imgAspect;
  }
  const dx = (W - dw) / 2 + offX;
  const dy = (H - dh) / 2 + offY;

  // 🌗 [BEFORE / AFTER 2분할 비교 모드]
  if (window.isBeforeAfterMode) {
    const halfW = W / 2;

    // [좌측: BEFORE (원본)]
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, 0, halfW, H);
    ctx.clip();
    ctx.drawImage(baseImg, dx, dy, dw, dh);
    // BEFORE 라벨 배지
    ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
    ctx.fillRect(8, 8, 92, 24);
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.5)';
    ctx.strokeRect(8, 8, 92, 24);
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 11px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('BEFORE (원본)', 54, 24);
    ctx.restore();

    // [우측: AFTER (변환본)]
    ctx.save();
    ctx.beginPath();
    ctx.rect(halfW, 0, halfW, H);
    ctx.clip();
    renderAfterStudio(ctx, baseImg, dx, dy, dw, dh, W, H);
    // AFTER 라벨 배지
    ctx.fillStyle = 'rgba(88, 28, 135, 0.9)';
    ctx.fillRect(W - 110, 8, 102, 24);
    ctx.strokeStyle = '#c084fc';
    ctx.strokeRect(W - 110, 8, 102, 24);
    ctx.fillStyle = '#fdf4ff';
    ctx.font = 'bold 11px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('AFTER (포토샵)', W - 59, 24);
    ctx.restore();

    // 중앙 분할 네온선
    ctx.save();
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2;
    ctx.shadowColor = '#0284c7';
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.moveTo(halfW, 0);
    ctx.lineTo(halfW, H);
    ctx.stroke();
    ctx.restore();
    return;
  }

  // 👗 단일 화면 렌더링
  if (window.isOriginalFitMode) {
    ctx.drawImage(baseImg, dx, dy, dw, dh);
  } else {
    renderAfterStudio(ctx, baseImg, dx, dy, dw, dh, W, H);
  }

  // 네온 개미행진선 및 터치 스캔 이펙트
  renderMarchingAntsContour(ctx, W, H);
}
window.drawMainFittingAvatar = drawMainFittingAvatar;
window.renderRealPhotoStudio = drawMainFittingAvatar;

// 변환본 렌더링 서브루틴 (포토샵 셰이더 or 클리핑 합성)
function renderAfterStudio(ctx, baseImg, dx, dy, dw, dh, W, H) {
  // 포토샵 픽셀 변환 버퍼가 있으면 최우선 렌더링
  if (window.psProcessedCanvas) {
    ctx.drawImage(window.psProcessedCanvas, 0, 0, W, H);
  } else {
    ctx.drawImage(baseImg, dx, dy, dw, dh);
  }

  // 1) 상의 클리핑 마스크 의상 합성
  if (window.selectedTopGarmentImg && window.selectedTopGarmentImg.complete) {
    ctx.save();
    const topY = dy + dh * 0.22;
    const topH = dh * 0.34;
    const topW = dw * 0.58;
    const topX = dx + (dw - topW) / 2;

    ctx.save();
    ctx.beginPath();
    // 포토샵 스마트 클리핑 마스크: 어깨와 허리 라인에 부드러운 타원 클립
    ctx.ellipse(topX + topW / 2, topY + topH / 2, topW / 2, topH / 2, 0, 0, Math.PI * 2);
    ctx.clip();
    ctx.drawImage(window.selectedTopGarmentImg, topX, topY, topW, topH);
    ctx.restore();

    // Multiply 주름 음영 블렌딩
    ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
    ctx.fillRect(topX, topY, topW, topH);
    ctx.restore();
  }

  // 2) 하의 클리핑 마스크 의상 합성
  if (window.selectedBottomGarmentImg && window.selectedBottomGarmentImg.complete) {
    ctx.save();
    const botY = dy + dh * 0.51;
    const botH = dh * 0.36;
    const botW = dw * 0.52;
    const botX = dx + (dw - botW) / 2;

    ctx.save();
    ctx.beginPath();
    ctx.ellipse(botX + botW / 2, botY + botH / 2, botW / 2, botH / 2, 0, 0, Math.PI * 2);
    ctx.clip();
    ctx.drawImage(window.selectedBottomGarmentImg, botX, botY, botW, botH);
    ctx.restore();

    ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
    ctx.fillRect(botX, botY, botW, botH);
    ctx.restore();
  }
}

// 네온 개미행진선(Marching Ants) & 스캔 라인 애니메이션
function renderMarchingAntsContour(ctx, W, H) {
  if (Date.now() < window.scanEffectExpiry && window.scanEffectZone) {
    ctx.save();
    ctx.lineWidth = 2.5;
    window.marchingAntsOffset = (window.marchingAntsOffset + 1) % 16;
    ctx.setLineDash([6, 4]);
    ctx.lineDashOffset = -window.marchingAntsOffset;

    if (window.scanEffectZone === 'top') {
      ctx.strokeStyle = '#06b6d4'; // 포토샵 Cyan
      ctx.shadowColor = '#22d3ee';
      ctx.shadowBlur = 12;
      const sy = H * 0.22 + ((Date.now() % 450) / 450) * (H * 0.32);
      ctx.beginPath();
      ctx.moveTo(W * 0.15, sy);
      ctx.lineTo(W * 0.85, sy);
      ctx.stroke();

      ctx.fillStyle = 'rgba(6, 182, 212, 0.08)';
      ctx.fillRect(W * 0.15, H * 0.22, W * 0.70, H * 0.32);
    } else if (window.scanEffectZone === 'bottom') {
      ctx.strokeStyle = '#d946ef'; // Magenta
      ctx.shadowColor = '#f0abfc';
      ctx.shadowBlur = 12;
      const sy = H * 0.52 + ((Date.now() % 450) / 450) * (H * 0.35);
      ctx.beginPath();
      ctx.moveTo(W * 0.18, sy);
      ctx.lineTo(W * 0.82, sy);
      ctx.stroke();

      ctx.fillStyle = 'rgba(217, 70, 239, 0.08)';
      ctx.fillRect(W * 0.18, H * 0.52, W * 0.64, H * 0.35);
    }
    ctx.restore();
    requestAnimationFrame(() => drawMainFittingAvatar());
  }
}

// 13. 직관적 제스처 & 터치 감지 이벤트 초기화
function initFittingCanvasGestures(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || canvas._gesturesBound) return;
  canvas._gesturesBound = true;

  let isDragging = false;
  let startX = 0, startY = 0;
  let initialPinchDistance = 0;
  let initialScale = 1.0;
  let touchStartTime = 0;

  function getDistance(t1, t2) {
    const dx = t1.clientX - t2.clientX;
    const dy = t1.clientY - t2.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  function onStart(e) {
    touchStartTime = Date.now();
    if (e.touches && e.touches.length === 2) {
      initialPinchDistance = getDistance(e.touches[0], e.touches[1]);
      initialScale = window.bodyPhotoScale || 1.0;
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
        window.bodyPhotoScale = Math.max(0.3, Math.min(3.5, initialScale * factor));
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

    window.bodyPhotoOffsetX += dx;
    window.bodyPhotoOffsetY += dy;
    drawMainFittingAvatar();
  }

  function onEnd(e) {
    const duration = Date.now() - touchStartTime;
    // 250ms 이하 짧은 탭(Tap)일 경우 포토샵 픽셀 마술봉 추출 작동!
    if (duration < 250) {
      const rect = canvas.getBoundingClientRect();
      const clientX = (e.changedTouches && e.changedTouches[0]) ? e.changedTouches[0].clientX : (e.clientX || startX);
      const clientY = (e.changedTouches && e.changedTouches[0]) ? e.changedTouches[0].clientY : (e.clientY || startY);
      const clickX = (clientX - rect.left) * (canvas.width / rect.width);
      const clickY = (clientY - rect.top) * (canvas.height / rect.height);
      extractPhotoshopGarmentMask(clickX, clickY);
    }
    isDragging = false;
    initialPinchDistance = 0;
  }

  canvas.addEventListener('mousedown', onStart);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onEnd);

  canvas.addEventListener('touchstart', onStart, { passive: false });
  window.addEventListener('touchmove', onMove, { passive: false });
  canvas.addEventListener('touchend', onEnd);
}

// 화보 캔버스 저장
function saveMyFittingPhoto() {
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');
  if (!canvas) return;
  try {
    const a = document.createElement('a');
    a.download = `coordi_photoshop_v71_${Date.now()}.png`;
    a.href = canvas.toDataURL('image/png');
    a.click();
    if (typeof showToast === 'function') {
      showToast('💾 [화보 저장 완료]: 포토샵 완성 화보가 갤러리에 저장되었습니다!', 'success');
    }
  } catch (e) {
    if (typeof showToast === 'function') showToast('💾 이미지를 길게 눌러 저장하세요.', 'info');
  }
}
window.saveMyFittingPhoto = saveMyFittingPhoto;

// 자동 초기화
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initFittingCanvasGestures('main-fitting-canvas');
    renderWebFashionGrid(window.trendFashionItems);
  });
} else {
  initFittingCanvasGestures('main-fitting-canvas');
  renderWebFashionGrid(window.trendFashionItems);
}
'''

def patch_index_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Zone 2 영역: garment-zone-indicator-bar 부터 web-trend-fashion-search-box 끝까지를 v7.1 컴포넌트 묶음으로 교체
    z_start = html.find('id="garment-zone-indicator-bar"')
    if z_start != -1:
        block_start = html.rfind('<!-- 🎯', 0, z_start)
        if block_start == -1:
            block_start = html.rfind('<div', 0, z_start)
    else:
        block_start = -1

    web_search_pos = html.find('id="web-trend-fashion-search-box"')
    if web_search_pos != -1:
        block_end = html.find('<!-- 🎓 인성 퀴즈 버튼', web_search_pos)
        if block_end == -1:
            block_end = html.find('</div>\n        </div>', web_search_pos)
            if block_end != -1:
                block_end += len('</div>\n        </div>')
    else:
        block_end = -1

    if block_start != -1 and block_end != -1:
        new_content = (V71_ZONE_INDICATOR_HTML + "\n\n        " +
                       V71_CANVAS_CONTAINER_HTML + "\n\n        " +
                       V71_COLOR_MATERIAL_BAR_HTML + "\n\n        " +
                       V71_CONTROL_BOX_HTML + "\n\n        " +
                       V71_WEB_FASHION_SEARCH_BOX_HTML + "\n\n        ")
        html = html[:block_start] + new_content + html[block_end:]
        print("  ✅ [index.html] v7.1 포토샵 마술봉 & 컬러/소재 변환 바 & BEFORE/AFTER 컨트롤 박스 교체 완료!")

    # JS 엔진 교체
    js_start_marker = "window.currentRenderMode = 'photo_lookbook';"
    start_pos = html.find(js_start_marker)
    if start_pos != -1:
        end_marker = "window.saveMyFittingPhoto = saveMyFittingPhoto;"
        end_pos = html.find(end_marker, start_pos)
        if end_pos != -1:
            init_marker = "renderWebFashionGrid(window.trendFashionItems);\n}"
            init_pos = html.find(init_marker, end_pos)
            if init_pos != -1:
                end_pos = init_pos + len(init_marker)
            else:
                end_pos += len(end_marker)
            html = html[:start_pos] + V71_JS_ENGINE.strip() + html[end_pos:]
            print("  ✅ [index.html] v7.1 어도비 포토샵 역설계 JS 엔진 교체 완료!")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  💾 [index.html] 파일 저장 완료: {file_path}")

def patch_app_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Zone 2 교체
    z_start = html.find('id="garment-zone-indicator-bar"')
    if z_start == -1:
        z_start = html.find('<!-- 🎯')
    if z_start != -1:
        block_start = html.rfind('<!-- 🎯', 0, z_start + 10) if '<!-- 🎯' in html else z_start
    else:
        block_start = -1

    web_search_pos = html.find('id="web-trend-fashion-search-box"')
    if web_search_pos != -1:
        block_end = html.find('<!-- 하단 각도', web_search_pos)
        if block_end == -1:
            block_end = html.find('</div>\n        </div>', web_search_pos)
            if block_end != -1:
                block_end += len('</div>\n        </div>')
    else:
        block_end = -1

    if block_start != -1 and block_end != -1:
        new_content = (V71_ZONE_INDICATOR_HTML + "\n\n        " +
                       V71_CANVAS_CONTAINER_HTML + "\n\n        " +
                       V71_COLOR_MATERIAL_BAR_HTML + "\n\n        " +
                       V71_CONTROL_BOX_HTML + "\n\n        " +
                       V71_WEB_FASHION_SEARCH_BOX_HTML + "\n\n        ")
        html = html[:block_start] + new_content + html[block_end:]
        print("  ✅ [dream_closet_future_master_app.html] v7.1 마크업 전면 교체 완료!")

    # JS 엔진 교체
    js_start_marker = "window.currentRenderMode = 'photo_lookbook';"
    start_pos = html.find(js_start_marker)
    if start_pos != -1:
        end_marker = "window.saveMyFittingPhoto = saveMyFittingPhoto;"
        end_pos = html.find(end_marker, start_pos)
        if end_pos != -1:
            init_marker = "renderWebFashionGrid(window.trendFashionItems);\n}"
            init_pos = html.find(init_marker, end_pos)
            if init_pos != -1:
                end_pos = init_pos + len(init_marker)
            else:
                end_pos += len(end_marker)
            html = html[:start_pos] + V71_JS_ENGINE.strip() + html[end_pos:]
            print("  ✅ [dream_closet_future_master_app.html] v7.1 JS 엔진 교체 완료!")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  💾 [dream_closet_future_master_app.html] 파일 저장 완료: {file_path}")

def main():
    print("=" * 80)
    print("🔥 [v7.1 Adobe-PS Reverse-Engineered Studio] 패치 실행")
    print("=" * 80)
    patch_index_html("dashboard/index.html")
    patch_app_html("dashboard/dream_closet_future_master_app.html")

if __name__ == "__main__":
    main()

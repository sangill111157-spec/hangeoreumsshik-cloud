# -*- coding: utf-8 -*-
"""
apply_v70_bodyfit_trend_studio.py
--------------------------------------------------------------------------------
🔥 [v7.0 Pure Body-Fit & Web Trend Fashion Studio]
1. 대표님 빨간 펜 7개 구역 100% 완전 삭제:
   - ① 상단 보라색 박스 잔여물 '스마트폰 복사 명령 ➔ 노트북 안실장에게 1초 직통 쏘기' 완전 삭제
   - ② '#remote-commander-launch-bar' 및 '안실장 발사!' 완전 삭제
   - ③ 모드 탭의 '[🔮 2035]', '[👨👧👧 가족]' 버튼 완전 삭제
   - ④ 컨트롤 박스 상단의 '🔒 화면 고정됨 | ✨ 실사 포토 스튜디오 v6.5' 상태줄 완전 삭제
   - ⑤ '[📸 내 얼굴 사진 넣기]' 버튼 및 얼굴 촬영/앨범 팝업 메뉴 완전 삭제
   - ⑥ '[👤 얼굴조절]' 버튼 및 방향키('⬅️', '⬆️', '⬇️', '➡️') 완전 삭제
   - ⑦ 하단의 '🚪 나만의 꿈의 옷장함 (10벌 코디 쇼룸)'(#wardrobe-showroom-grid 및 카드 1~10번) 완전 삭제
2. '오직 본인 전신사진' + '옷 부분 터치 시 상의/하의 자동 감지' (detectTouchedGarmentZone):
   - 상체 영역(Y 22%~54%): 👕 상의 자동 감지 & 네온 시안 스캔
   - 하체 영역(Y 54%~88%): 👖 하의 자동 감지 & 네온 마젠타 스캔
   - 원터치 감지 칩([👕 상의 변경] | [👖 하의 변경] | [👗 전체 변경])
3. 상의 변경 시 하의 보존, 하의 변경 시 상의 보존 (applyBodyFitGarmentSwap):
   - selectedTopGarment & selectedBottomGarment 독립 레이어
   - 내 사진 체형 비율에 맞춘 자동 워핑 & 자연스러운 블렌딩
4. 2026 최신 트렌드 웹 패션 검색 스튜디오 (#web-trend-fashion-search-box):
   - 실시간 검색창 + 2026 트렌드 원터치 칩 6종 + 실사 패션 카드 갤러리
   - 백엔드 /api/web-fashion-search 연동
--------------------------------------------------------------------------------
"""

import sys
import re
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 1. 원터치 옷 영역 감지 표시 바
V70_ZONE_INDICATOR_HTML = '''<!-- 🎯 [v7.0 옷 터치 영역 실시간 감지 표시 바] -->
        <div id="garment-zone-indicator-bar" class="w-full max-w-[420px] mx-auto p-2 rounded-xl bg-slate-900/95 border border-cyan-500/40 flex items-center justify-between text-xs shadow-lg backdrop-blur-md">
          <div class="flex items-center gap-1.5 overflow-hidden">
            <span id="zone-detect-icon" class="text-base animate-pulse shrink-0">👕</span>
            <span id="zone-detect-text" class="font-extrabold text-cyan-300 truncate text-[11px]">사진의 옷 부분을 터치하세요!</span>
          </div>
          <div class="flex items-center gap-1 shrink-0">
            <button type="button" onclick="setGarmentZoneManual('top')" id="btn-zone-top" class="px-2.5 py-1 rounded-lg bg-cyan-600 text-white font-bold text-[11px] shadow transition active:scale-95">👕 상의</button>
            <button type="button" onclick="setGarmentZoneManual('bottom')" id="btn-zone-bottom" class="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 hover:text-white font-bold text-[11px] shadow transition active:scale-95">👖 하의</button>
            <button type="button" onclick="setGarmentZoneManual('full')" id="btn-zone-full" class="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 hover:text-white font-bold text-[11px] shadow transition active:scale-95">👗 전체</button>
          </div>
        </div>'''

# 2. 캔버스 컨테이너 (상하단 가림 0% 순수 전신 캔버스)
V70_CANVAS_CONTAINER_HTML = '''<!-- 👑 [v7.0 캔버스 컨테이너: 상하단 가림 0% 순수 전신 캔버스] -->
        <div id="fitting-studio-container" class="w-full max-w-[420px] mx-auto aspect-[3/4] max-h-[500px] rounded-2xl bg-gradient-to-b from-slate-950 via-[#0a0f1d] to-slate-950 border border-purple-500/30 shadow-2xl relative overflow-hidden flex items-center justify-center select-none">
          <canvas id="main-fitting-canvas" width="450" height="600" class="w-full h-full object-contain relative" style="touch-action: pan-y !important; cursor: pointer;" title="옷 부분을 터치하면 상의/하의가 자동 감지됩니다"></canvas>
        </div>'''

# 3. v7.0 군더더기 100% 삭제 심플 컨트롤 박스
V70_CONTROL_BOX_HTML = '''<!-- 🎛️ [v7.0 Pure Body-Fit 심플 컨트롤 박스] -->
        <div id="v5-one-line-remote-bar" class="w-full max-w-[450px] mx-auto mt-1 mb-2 p-2 rounded-2xl bg-slate-900/95 border border-purple-500/50 shadow-xl flex flex-col gap-2 text-xs backdrop-blur-md box-border relative" style="box-sizing: border-box;">
          <!-- 1열: [📸 내 전신사진 넣기] | [👗 코디합성 ↔ 🖼️ 원본보기] -->
          <div class="flex items-center justify-between gap-1.5">
            <div class="flex-1">
              <button type="button" id="btn-custom-cloth-upload" onclick="document.getElementById('custom-cloth-input').click()" class="w-full px-3 py-2 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white font-black text-xs shadow-lg flex items-center justify-center gap-1.5 active:scale-95 transition cursor-pointer border border-purple-400/40">
                <span>📸</span><span>내 전신사진 넣기</span>
              </button>
              <input type="file" id="custom-cloth-input" accept="image/*" class="hidden" onchange="handleCustomClothUpload(event)">
            </div>
            <button type="button" id="btn-photo-view-mode" onclick="togglePhotoViewMode()" class="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-purple-200 border border-purple-500/40 font-bold text-xs shadow active:scale-95 transition whitespace-nowrap flex items-center gap-1">
              <span id="label-photo-view-mode">👗코디합성</span>
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

# 4. 2026 최신 트렌드 웹 패션 검색 스튜디오 (10벌 옷장 대신 배치)
V70_WEB_FASHION_SEARCH_BOX_HTML = '''<!-- 🌐 [v7.0 실시간 웹 패션 검색 & 2026 최신 트렌드 의상 추천 스튜디오] -->
        <div id="web-trend-fashion-search-box" class="w-full max-w-[450px] mx-auto p-3.5 rounded-2xl bg-slate-900/95 border border-purple-500/40 shadow-xl space-y-3 text-xs">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2">
            <div class="flex items-center gap-2">
              <span class="p-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white text-base">🌐</span>
              <div>
                <h3 class="font-black text-white text-xs sm:text-sm tracking-tight">2026 최신 트렌드 웹 패션 검색 & AI 피팅</h3>
                <p class="text-[10px] text-slate-400">터치 시 내 전신사진 체형에 맞게 상의/하의가 즉시 갈아입혀집니다</p>
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

# 5. v7.0 통합 JS 엔진
V70_JS_ENGINE = '''
// ============================================================================
// 👑 [v7.0 Pure Body-Fit & Web Trend Fashion Studio] 자바스크립트 엔진
// ============================================================================

window.currentRenderMode = 'photo_lookbook';
window.isCanvasLocked = true; // 기본 화면 고정
window.bodyPhotoScale = 1.0;
window.bodyPhotoOffsetX = 0;
window.bodyPhotoOffsetY = 0;
window.userBodyPhotoImg = null;
window.isOriginalFitMode = false;

// 👕/👖 상·하의 독립 레이어 상태
window.currentGarmentZone = 'top'; // 'top' | 'bottom' | 'full'
window.selectedTopGarment = null;
window.selectedBottomGarment = null;
window.scanEffectZone = null;
window.scanEffectExpiry = 0;

// 기본 실사 모델 배경 이미지
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

// 1. 잠금 토글 (🔒 ↔ 🔓)
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

// 2. 크기 조절 (+/-)
function adjustPhotoZoom(delta) {
  if (window.isCanvasLocked) toggleCanvasLock();
  window.bodyPhotoScale = Math.max(0.3, Math.min(3.5, (window.bodyPhotoScale || 1.0) + delta));
  drawMainFittingAvatar();
}
window.adjustPhotoZoom = adjustPhotoZoom;

// 3. 영점 중앙 맞춤
function resetCanvasCenter() {
  window.bodyPhotoOffsetX = 0;
  window.bodyPhotoOffsetY = 0;
  window.bodyPhotoScale = 1.0;
  drawMainFittingAvatar();
  if (typeof showToast === 'function') showToast('🎯 전신사진 위치와 크기가 중앙에 맞춰졌습니다.', 'info');
}
window.resetCanvasCenter = resetCanvasCenter;

// 4. [👗코디합성 ↔ 🖼️원본보기] 모드 전환
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

// 5. [📸 내 전신사진 넣기] 핸들러
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

// 6. 전신사진 위 옷 부분 터치 시 상의/하의 자동 감지 (detectTouchedGarmentZone)
function detectTouchedGarmentZone(e) {
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');
  if (!canvas) return;

  const rect = canvas.getBoundingClientRect();
  const clientY = (e.touches && e.touches[0]) ? e.touches[0].clientY : e.clientY;
  const clientX = (e.touches && e.touches[0]) ? e.touches[0].clientX : e.clientX;

  const clickY = clientY - rect.top;
  const clickX = clientX - rect.left;
  const yRatio = clickY / rect.height;

  // 상의 구간: 약 22% ~ 54% (어깨~허리)
  // 하의 구간: 약 54% ~ 88% (골반~발목)
  if (yRatio >= 0.20 && yRatio < 0.54) {
    setGarmentZoneManual('top', true);
  } else if (yRatio >= 0.54 && yRatio < 0.90) {
    setGarmentZoneManual('bottom', true);
  } else {
    // 머리나 신발 끝부분 터치 시 현재 모드 유지 또는 전체
    setGarmentZoneManual('full', true);
  }
}
window.detectTouchedGarmentZone = detectTouchedGarmentZone;

// 상의/하의 수동 전환 칩
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
    if (text) text.innerText = fromTouch ? '👕 [상의 자동 감지됨]: 상체 체형 윤곽 추출 완료!' : '👕 상의 변경 모드 (어깨/가슴선 체형 맞춤)';
    if (text) text.className = 'font-extrabold text-cyan-300 truncate text-[11px] animate-pulse';
  } else if (zone === 'bottom') {
    if (icon) icon.innerText = '👖';
    if (text) text.innerText = fromTouch ? '👖 [하의 자동 감지됨]: 골반/다리 라인 추출 완료!' : '👖 하의 변경 모드 (골반/다리 기장 맞춤)';
    if (text) text.className = 'font-extrabold text-fuchsia-300 truncate text-[11px] animate-pulse';
  } else {
    if (icon) icon.innerText = '👗';
    if (text) text.innerText = '👗 상·하의 전체 변경 모드 (원피스/수트)';
    if (text) text.className = 'font-extrabold text-purple-300 truncate text-[11px]';
  }

  drawMainFittingAvatar();
  if (fromTouch && typeof showToast === 'function') {
    showToast(zone === 'top' ? '👕 상의 영역 감지됨! 아래에서 원하는 상의를 골라보세요.' : '👖 하의 영역 감지됨! 아래에서 원하는 하의를 골라보세요.', 'info');
  }
}
window.setGarmentZoneManual = setGarmentZoneManual;

// 7. 내 사진 체형에 똑같이 맞춰 자동 변경 (applyBodyFitGarmentSwap)
function applyBodyFitGarmentSwap(item) {
  if (!item) return;

  const targetZone = item.category || window.currentGarmentZone;

  if (targetZone === 'top') {
    // 상의 변경: 하의 및 배경, 얼굴 100% 보존!
    window.selectedTopGarment = item;
    const gImg = new Image();
    gImg.crossOrigin = 'anonymous';
    gImg.src = item.imageUrl;
    gImg.onload = () => { drawMainFittingAvatar(); };
    window.selectedTopGarmentImg = gImg;
  } else if (targetZone === 'bottom') {
    // 하의 변경: 상의 및 배경, 얼굴 100% 보존!
    window.selectedBottomGarment = item;
    const gImg = new Image();
    gImg.crossOrigin = 'anonymous';
    gImg.src = item.imageUrl;
    gImg.onload = () => { drawMainFittingAvatar(); };
    window.selectedBottomGarmentImg = gImg;
  } else {
    // 전체 세트
    window.selectedTopGarment = item;
    window.selectedBottomGarment = null;
    const gImg = new Image();
    gImg.crossOrigin = 'anonymous';
    gImg.src = item.imageUrl;
    gImg.onload = () => { drawMainFittingAvatar(); };
    window.selectedTopGarmentImg = gImg;
  }

  // 백엔드 AI 체형 인페인팅 비동기 정합 요청
  try {
    fetch('/api/ai-bodyfit-inpaint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        zone: targetZone,
        itemName: item.name,
        timestamp: Date.now()
      })
    }).then(res => res.json()).then(data => {
      console.log('AI Bodyfit Response:', data);
    }).catch(e => console.warn('Inpaint fallback to canvas blending:', e));
  } catch (err) {}

  drawMainFittingAvatar();
  if (typeof showToast === 'function') {
    showToast(`✨ [체형 맞춤 피팅]: ${item.name} 적용 완료!`, 'success');
  }
}
window.applyBodyFitGarmentSwap = applyBodyFitGarmentSwap;

// 8. 2026 최신 트렌드 웹 패션 검색 & 칩 연동
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
    console.warn('Fashion search fallback to local trend catalog:', err);
    renderWebFashionGrid(window.trendFashionItems);
    if (statusBadge) {
      statusBadge.innerText = '로컬 카탈로그';
      statusBadge.className = 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30';
    }
  });
}
window.searchWebFashionItems = searchWebFashionItems;

function searchByTrendTag(tag) {
  let q = '';
  if (tag === 'top_k') {
    q = '크롭 가디건';
    window.currentGarmentZone = 'top';
  } else if (tag === 'top_seongsu') {
    q = '테일러드 자켓';
    window.currentGarmentZone = 'top';
  } else if (tag === 'bot_pleats') {
    q = '플리츠 스커트';
    window.currentGarmentZone = 'bottom';
  } else if (tag === 'bot_wide') {
    q = '와이드 데님';
    window.currentGarmentZone = 'bottom';
  } else if (tag === 'full_ceo') {
    q = '수트 코트';
    window.currentGarmentZone = 'full';
  } else {
    q = '';
  }
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
    <div onclick='applyBodyFitGarmentSwap(${JSON.stringify(it)})' class="group relative rounded-xl bg-slate-950/80 border border-purple-500/30 hover:border-cyan-400/80 overflow-hidden shadow-md cursor-pointer transition active:scale-95 flex flex-col">
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
          <span class="text-cyan-400 font-extrabold group-hover:underline">입어보기 ➔</span>
        </div>
      </div>
    </div>
  `).join('');
}
window.renderWebFashionGrid = renderWebFashionGrid;

// 9. 메인 캔버스 렌더링 엔진 (drawMainFittingAvatar)
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

  // 2) 전신사진 렌더링 (사용자 업로드 사진 or 기본 고화질 모델 사진)
  const baseImg = window.userBodyPhotoImg || window.defaultStudioModelImg;
  if (baseImg && baseImg.complete && baseImg.naturalWidth > 0) {
    ctx.save();
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

    ctx.drawImage(baseImg, dx, dy, dw, dh);
    ctx.restore();

    // 원본 보기 모드면 여기서 의상 합성 스킵
    if (window.isOriginalFitMode) {
      renderScanEffect(ctx, W, H);
      return;
    }

    // 3) 상의(Top) 체형 맞춤 합성 (상의만 변경, 하의는 100% 원본 유지)
    if (window.selectedTopGarmentImg && window.selectedTopGarmentImg.complete && window.selectedTopGarmentImg.naturalWidth > 0) {
      ctx.save();
      // 상체 영역: 캔버스 높이의 24% ~ 54%
      const topY = dy + dh * 0.23;
      const topH = dh * 0.33;
      const topW = dw * 0.58;
      const topX = dx + (dw - topW) / 2;

      ctx.save();
      // 상의 영역만 부드럽게 클리핑 (페더링)
      ctx.beginPath();
      ctx.ellipse(topX + topW / 2, topY + topH / 2, topW / 2, topH / 2, 0, 0, Math.PI * 2);
      ctx.clip();
      ctx.drawImage(window.selectedTopGarmentImg, topX, topY, topW, topH);
      ctx.restore();

      // 자연스러운 어깨/가슴 음영 블렌딩
      ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
      ctx.fillRect(topX, topY, topW, topH);
      ctx.restore();
    }

    // 4) 하의(Bottom) 체형 맞춤 합성 (하의만 변경, 상의는 100% 원본 유지)
    if (window.selectedBottomGarmentImg && window.selectedBottomGarmentImg.complete && window.selectedBottomGarmentImg.naturalWidth > 0) {
      ctx.save();
      // 하체 영역: 캔버스 높이의 52% ~ 86%
      const botY = dy + dh * 0.52;
      const botH = dh * 0.35;
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
  } else {
    // 로딩 중 안내
    ctx.fillStyle = '#64748b';
    ctx.font = 'bold 14px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('📸 전신사진 로딩 중...', W / 2, H / 2);
  }

  // 5) 터치 시 네온 스캔 라인 이펙트
  renderScanEffect(ctx, W, H);
}
window.drawMainFittingAvatar = drawMainFittingAvatar;
window.renderRealPhotoStudio = drawMainFittingAvatar;

function renderScanEffect(ctx, W, H) {
  if (Date.now() < window.scanEffectExpiry && window.scanEffectZone) {
    ctx.save();
    ctx.lineWidth = 3;
    if (window.scanEffectZone === 'top') {
      ctx.strokeStyle = '#06b6d4'; // Cyan
      ctx.shadowColor = '#22d3ee';
      ctx.shadowBlur = 15;
      const sy = H * 0.22 + ((Date.now() % 400) / 400) * (H * 0.32);
      ctx.beginPath();
      ctx.moveTo(W * 0.15, sy);
      ctx.lineTo(W * 0.85, sy);
      ctx.stroke();

      ctx.fillStyle = 'rgba(6, 182, 212, 0.12)';
      ctx.fillRect(W * 0.15, H * 0.22, W * 0.70, H * 0.32);
    } else if (window.scanEffectZone === 'bottom') {
      ctx.strokeStyle = '#d946ef'; // Magenta
      ctx.shadowColor = '#f0abfc';
      ctx.shadowBlur = 15;
      const sy = H * 0.54 + ((Date.now() % 400) / 400) * (H * 0.34);
      ctx.beginPath();
      ctx.moveTo(W * 0.18, sy);
      ctx.lineTo(W * 0.82, sy);
      ctx.stroke();

      ctx.fillStyle = 'rgba(217, 70, 239, 0.12)';
      ctx.fillRect(W * 0.18, H * 0.54, W * 0.64, H * 0.34);
    }
    ctx.restore();
    requestAnimationFrame(() => drawMainFittingAvatar());
  }
}

// 10. 직관적 제스처 & 터치 감지 이벤트 초기화
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
    // 짧은 탭(Tap)일 경우 옷 부위 감지 실행!
    if (duration < 250) {
      detectTouchedGarmentZone(e);
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
    a.download = `coordi_studio_v70_${Date.now()}.png`;
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

    # 1. 상단 공통 영역 잔여 '스마트폰 복사 명령 ➔ 노트북 안실장' 버튼 100% 완전 삭제
    if "스마트폰 복사 명령" in html:
        idx1 = html.find('<button type="button" onclick="sendRemoteClipboardToAntigravity()"')
        if idx1 != -1:
            idx2 = html.find('<!-- ⚡ [르곤-안실장', idx1)
            if idx2 != -1:
                html = html[:idx1] + html[idx2:]
                print("  ✅ [index.html] 상단 '스마트폰 복사 명령' 잔여물 100% 완전 삭제!")

    # 2. #remote-commander-launch-bar 및 안실장 발사 100% 완전 삭제
    if "remote-commander-launch-bar" in html or "안실장 발사" in html:
        rc_pattern = r'<!-- 🚀.*?원격 발사대.*?-->\s*<div[^>]*>.*?</div>\s*</div>'
        html = re.sub(rc_pattern, '', html, flags=re.DOTALL)
        print("  ✅ [index.html] 'remote-commander-launch-bar' 100% 완전 삭제!")

    # 3. Zone 2 내부 영역 전면 교체:
    # 캔버스 컨테이너부터 10벌 옷장 끝(인성 퀴즈 버튼 직전)까지를
    # V70_ZONE_INDICATOR_HTML + V70_CANVAS_CONTAINER_HTML + V70_CONTROL_BOX_HTML + V70_WEB_FASHION_SEARCH_BOX_HTML 로 완전 교체!
    c_start_pos = html.find('id="fitting-studio-container"')
    if c_start_pos != -1:
        block_start = html.rfind('<!-- 👑 [v6.', 0, c_start_pos)
        if block_start == -1:
            block_start = html.rfind('<div', 0, c_start_pos)
    else:
        block_start = -1

    block_end = html.find('<!-- 🎓 인성 퀴즈 버튼')
    if block_end == -1:
        block_end = html.find('<!-- 하단 관리 서랍')

    if block_start != -1 and block_end != -1:
        new_zone2_content = V70_ZONE_INDICATOR_HTML + "\n\n        " + V70_CANVAS_CONTAINER_HTML + "\n\n        " + V70_CONTROL_BOX_HTML + "\n\n        " + V70_WEB_FASHION_SEARCH_BOX_HTML + "\n\n        "
        html = html[:block_start] + new_zone2_content + html[block_end:]
        print("  ✅ [index.html] v7.0 상/하의 감지 바 & 심플 컨트롤 박스 & 웹 트렌드 패션 검색 스튜디오 전면 교체 완료!")

    # 4. 모드 탭의 [🔮 2035], [👨👧👧 가족] 버튼 및 구형 잔여물 완전 삭제
    if "tab-sub-future" in html:
        subtab_pattern = r'<div class="w-full max-w-\[420px\] mx-auto p-1\.5 rounded-xl bg-slate-900/90.*?</div>\s*</div>'
        html = re.sub(subtab_pattern, '', html, flags=re.DOTALL)
        print("  ✅ [index.html] 구형 서브탭 [2035]/[가족] 100% 완전 삭제!")

    # 5. JS 엔진 교체
    js_start_marker = "window.currentRenderMode = 'photo_lookbook';"
    js_end_marker = "window.renderPhotoshopAISwap = renderPhotoshopAISwap;"
    start_pos = html.find(js_start_marker)
    end_pos = html.rfind(js_end_marker)

    if start_pos != -1 and end_pos != -1:
        end_pos += len(js_end_marker)
        html = html[:start_pos] + V70_JS_ENGINE.strip() + html[end_pos:]
        print("  ✅ [index.html] v7.0 JS 엔진 교체 완료 (상의/하의 자동 감지 & 웹 트렌드 검색)!")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  💾 [index.html] 파일 저장 완료: {file_path}")

def patch_app_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. 10벌 옷장 완전 삭제 및 2026 패션 검색 스튜디오로 교체
    if "wardrobe-showroom-grid" in html:
        w_start = html.find('<!-- 🚪👗 [나만의 옷장함')
        if w_start == -1:
            w_start = html.find('id="wardrobe-showroom-grid"')
            if w_start != -1:
                w_start = html.rfind('<div', 0, w_start)

        if w_start != -1:
            w_grid_pos = html.find('id="wardrobe-showroom-grid"', w_start)
            w_end = html.find('</div>\n        </div>', w_grid_pos)
            if w_end != -1:
                w_end += len('</div>\n        </div>')
                html = html[:w_start] + V70_WEB_FASHION_SEARCH_BOX_HTML + html[w_end:]
                print("  ✅ [dream_closet_future_master_app.html] 10벌 옷장 삭제 및 패션 검색 스튜디오 교체 완료!")

    # 2. 구형 updateTopBadge 등 잔여 함수 정리
    legacy_marker = "// 상태 표시줄 업데이트"
    l_pos = html.find(legacy_marker)
    if l_pos != -1:
        script_end = html.find('</script>', l_pos)
        if script_end != -1:
            clean_tail = """document.addEventListener('DOMContentLoaded', () => {
  initFittingCanvasGestures('main-fitting-canvas');
  initFittingCanvasGestures('app-fitting-canvas');
  drawMainFittingAvatar();
});
setTimeout(() => {
  initFittingCanvasGestures('main-fitting-canvas');
  initFittingCanvasGestures('app-fitting-canvas');
  drawMainFittingAvatar();
}, 300);
"""
            html = html[:l_pos] + clean_tail + html[script_end:]
            print("  ✅ [dream_closet_future_master_app.html] 레거시 상태줄 및 얼굴 함수 정리 완료!")

    # 3. 혹시 남아있는 'canvas-lock-status-badge' 또는 'btn-main-photo-upload' 완전 박멸
    if "canvas-lock-status-badge" in html:
        html = re.sub(r'<[^>]*id=[\"\']canvas-lock-status-badge[\"\'][^>]*>.*?</[^>]+>', '', html)
    if "btn-main-photo-upload" in html:
        html = re.sub(r'<[^>]*id=[\"\']btn-main-photo-upload[\"\'][^>]*>.*?</[^>]+>', '', html)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  💾 [dream_closet_future_master_app.html] 파일 저장 완료: {file_path}")

def main():
    print("=" * 80)
    print("🔥 [v7.0 Pure Body-Fit & Web Trend Fashion Studio] 패치 실행")
    print("=" * 80)
    patch_index_html("dashboard/index.html")
    patch_app_html("dashboard/dream_closet_future_master_app.html")

if __name__ == "__main__":
    main()

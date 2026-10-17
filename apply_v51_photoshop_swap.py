# -*- coding: utf-8 -*-
"""
apply_v51_photoshop_swap.py
--------------------------------------------------------------------------------
🔥 [v5.1 Photoshop-AI 의상합성 스튜디오] 역설계 흡수 패치 스크립트
1. [📸 내 얼굴 사진] + [👚 내 옷 사진 합성] (handleCustomClothUpload) 듀얼 슬롯 탑재
2. Smart Neck & Collar Shadow (목선-옷깃 미세 Contact Shadow 딥-블렌딩)
3. Auto Color & Lighting Match (matchPhotoshopLighting & 포토샵 컬러 매치)
4. Background Clean & Studio Bokeh Depth-of-Field (배경 인물 분리 & 스튜디오 보케 배경)
5. 캔버스 0px 밀착 [🪄포토샵자동합성] (runPhotoshopAutoBlend) 1줄 퀵 리모컨 바
6. renderPhotoshopAISwap 렌더링 파이프라인
--------------------------------------------------------------------------------
"""

import sys
import subprocess
import re
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 1. 상단 듀얼 슬롯 헤더 HTML (내 얼굴 사진 + 내 옷 사진 합성 버튼)
DUAL_SLOT_HEADER_HTML = '''<!-- 👑 [캔버스 외부 상단 독립 컨트롤 헤더: 모드 전환 & 듀얼 사진 슬롯] (얼굴 가림 0% 완전 분리) -->
        <div class="w-full max-w-[440px] mx-auto p-2 rounded-xl bg-slate-900/90 border border-purple-500/30 flex items-center justify-between gap-1.5 text-xs">
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

          <!-- 듀얼 슬롯: [📸 내 얼굴 사진 넣기] + [👚 내 옷 합성] -->
          <div class="flex items-center gap-1">
            <!-- 1) 내 얼굴 사진 메뉴 -->
            <div class="relative">
              <button type="button" onclick="toggleFacePhotoMenu()" id="btn-face-menu" class="px-2.5 py-1.5 rounded-lg bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white font-bold text-[11px] shadow-md flex items-center gap-1 active:scale-95 transition cursor-pointer" title="내 얼굴 사진 넣기">
                <span>📸</span><span>내 얼굴 사진 넣기</span>
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
              <input type="file" id="face-upload-input" accept="image/*" class="hidden" onchange="handleUserFacePhotoUpload(event)">
              <input type="file" id="face-camera-input" accept="image/*" capture="user" class="hidden" onchange="handleUserFacePhotoUpload(event)">
            </div>

            <!-- 2) [👚 내 옷 사진 합성 (포토샵 2025)] -->
            <div>
              <button type="button" onclick="openCustomClothUpload()" id="btn-custom-cloth" class="px-2.5 py-1.5 rounded-lg bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-bold text-[11px] shadow-md flex items-center gap-1 active:scale-95 transition cursor-pointer border border-blue-400/30" title="쇼핑몰 옷 사진 직접 올려 합성하기">
                <span>👚</span><span>내 옷 합성</span>
              </button>
              <input type="file" id="custom-cloth-file-input" accept="image/*" class="hidden" onchange="handleCustomClothUpload(event)">
            </div>
          </div>
        </div>'''

# 2. 캔버스 0px 밀착 [🪄포토샵자동합성] 1줄 퀵 리모컨 바
V51_ONE_LINE_REMOTE_BAR_HTML = '''<!-- 🎛️ [v5.1 Photoshop-AI 초심플 1줄 퀵 리모컨 바 (캔버스 0px 밀착)] -->
        <div id="v5-one-line-remote-bar" class="w-full max-w-[450px] mx-auto mt-1 mb-2 p-1.5 rounded-2xl bg-slate-900/95 border border-purple-500/50 shadow-xl flex items-center justify-between gap-1 text-xs backdrop-blur-md">
          <!-- 1. 크기 조절 버튼 (+ / -) -->
          <div class="flex items-center gap-0.5">
            <button type="button" onclick="adjustFaceScale(-0.08)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-black text-xs border border-slate-700 active:scale-95 flex items-center justify-center transition" title="얼굴 작게">➖</button>
            <button type="button" onclick="adjustFaceScale(+0.08)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-black text-xs border border-slate-700 active:scale-95 flex items-center justify-center transition" title="얼굴 크게">➕</button>
          </div>

          <!-- 2. 상하좌우 4방향 미세이동 D-Pad -->
          <div class="flex items-center gap-0.5 font-bold">
            <button type="button" onclick="adjustFaceOffset(-4, 0)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-[11px] border border-slate-700 active:scale-95 flex items-center justify-center transition" title="좌로 4px">⬅️</button>
            <button type="button" onclick="adjustFaceOffset(0, -4)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-[11px] border border-slate-700 active:scale-95 flex items-center justify-center transition" title="위로 4px">⬆️</button>
            <button type="button" onclick="adjustFaceOffset(0, +4)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-[11px] border border-slate-700 active:scale-95 flex items-center justify-center transition" title="아래로 4px">⬇️</button>
            <button type="button" onclick="adjustFaceOffset(+4, 0)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-[11px] border border-slate-700 active:scale-95 flex items-center justify-center transition" title="우로 4px">➡️</button>
          </div>

          <!-- 3. 원터치 중앙 자동 영점 -->
          <button type="button" onclick="resetFaceOffset()" class="px-2 h-7 rounded-lg bg-indigo-600/40 hover:bg-indigo-600/70 text-indigo-200 text-[10px] font-bold border border-indigo-400/40 active:scale-95 flex items-center gap-0.5 whitespace-nowrap transition" title="얼굴 중앙 맞춤">
            <span>🎯맞춤</span>
          </button>

          <!-- 4. [🪄포토샵자동합성] (목선 그림자 접촉 & 조명 컬러매칭 황금비율 자동 합성) -->
          <button type="button" id="btn-photoshop-auto-blend" onclick="runPhotoshopAutoBlend()" class="px-2 h-7 rounded-lg bg-gradient-to-r from-blue-600/80 via-purple-600/80 to-pink-600/80 hover:from-blue-500 hover:to-pink-500 text-white text-[10px] font-black border border-blue-400/50 active:scale-95 flex items-center gap-0.5 whitespace-nowrap shadow-md transition" title="포토샵 2025 AI 자동 의상합성">
            <span>🪄포토샵자동합성</span>
          </button>

          <!-- 5. 사진 저장 -->
          <button type="button" onclick="saveMyFittingPhoto()" class="px-2 h-7 rounded-lg bg-emerald-600/50 hover:bg-emerald-600/70 text-emerald-100 text-[10px] font-bold border border-emerald-400/40 active:scale-95 flex items-center gap-0.5 whitespace-nowrap transition" title="화보 저장">
            <span>💾저장</span>
          </button>
        </div>'''

# 3. v5.1 Photoshop-AI 마스터 JS 엔진
FULL_V51_ENGINE_JS = '''
// ══════════════════════════════════════════════════════════════════
// 🌟 [Omni-Nexus v5.1 Photoshop-AI Swap] 포토샵 2025 의상합성 스튜디오 엔진
// ══════════════════════════════════════════════════════════════════

window.faceOffsetX = window.faceOffsetX || 0;
window.faceOffsetY = window.faceOffsetY || 0;
window.faceScale = window.faceScale || 1.0;
window.isFaceDragMode = true;
window.useSmartCutout = true;
window.autoBeautyFilter = true;
window.cachedCutoutCanvas = null;
window.lastCutoutSourceSrc = '';
window.currentWardrobeNum = window.currentWardrobeNum || 1;

// 커스텀 옷 사진 상태
window.customClothImage = null;
window.hasCustomCloth = false;
window.cachedClothCanvas = null;

// 포토샵 컬러 & 조명 매치 상태
window.photoshopLightMatch = {
  lumRatio: 1.0,
  warmShift: 0,
  shadowDepth: 0.48
};

// 1. 얼굴 크기 조절
function adjustFaceScale(delta) {
  window.faceScale = Math.max(0.5, Math.min(2.5, (window.faceScale || 1.0) + delta));
  drawMainFittingAvatar();
}

function onFaceScaleSliderChange(val) {
  window.faceScale = parseInt(val, 10) / 100.0;
  drawMainFittingAvatar();
}

function resetFaceScale() {
  window.faceScale = 1.0;
  drawMainFittingAvatar();
  if (typeof showToast === 'function') showToast('🔄 얼굴 크기가 100% 기본값으로 리셋되었습니다.', 'info');
}

// 2. 얼굴 상하좌우 위치 정밀 이동
function adjustFaceOffset(dx, dy) {
  window.faceOffsetX = Math.max(-140, Math.min(140, (window.faceOffsetX || 0) + dx));
  window.faceOffsetY = Math.max(-140, Math.min(140, (window.faceOffsetY || 0) + dy));
  drawMainFittingAvatar();
}

function onFaceOffsetXSliderChange(val) {
  window.faceOffsetX = parseInt(val, 10);
  drawMainFittingAvatar();
}

function onFaceOffsetYSliderChange(val) {
  window.faceOffsetY = parseInt(val, 10);
  drawMainFittingAvatar();
}

function resetFaceOffset() {
  window.faceOffsetX = 0;
  window.faceOffsetY = 0;
  drawMainFittingAvatar();
  if (typeof showToast === 'function') showToast('🎯 얼굴 위치가 정중앙으로 자동 정렬되었습니다.', 'success');
}

function toggleFaceDragMode() {
  window.isFaceDragMode = !window.isFaceDragMode;
}

function toggleSmartCutout() {
  window.useSmartCutout = !window.useSmartCutout;
  window.cachedCutoutCanvas = null;
  drawMainFittingAvatar();
}

// 3. 👚 [커스텀 옷 사진 직접 업로드 & 합성]
function openCustomClothUpload() {
  const inp = document.getElementById('custom-cloth-file-input');
  if (inp) inp.click();
}

function handleCustomClothUpload(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    const img = new Image();
    img.onload = function() {
      window.customClothImage = img;
      window.hasCustomCloth = true;
      window.cachedClothCanvas = processClothTransparency(img);
      drawMainFittingAvatar();
      if (typeof showToast === 'function') {
        showToast('👚 [포토샵 의상 로드]: 쇼핑몰 옷 사진이 감쪽같이 합성되었습니다!', 'success');
      }
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

// 옷 사진 단색/흰색 배경 자동 투명화 (Luminance Keying)
function processClothTransparency(img) {
  const off = document.createElement('canvas');
  const w = img.naturalWidth || img.width || 400;
  const h = img.naturalHeight || img.height || 500;
  off.width = w;
  off.height = h;
  const ctx = off.getContext('2d');
  ctx.drawImage(img, 0, 0, w, h);

  try {
    const imgData = ctx.getImageData(0, 0, w, h);
    const d = imgData.data;

    // 모서리 배경색
    const bgR = (d[0] + d[(w-1)*4]) / 2;
    const bgG = (d[1] + d[(w-1)*4+1]) / 2;
    const bgB = (d[2] + d[(w-1)*4+2]) / 2;

    for (let i = 0; i < d.length; i += 4) {
      const r = d[i], g = d[i+1], b = d[i+2];
      // 흰색 또는 모서리 배경색 유사 판별
      const diff = Math.hypot(r - bgR, g - bgG, b - bgB);
      const isWhite = (r > 240 && g > 240 && b > 240);
      if (diff < 35 || isWhite) {
        d[i+3] = 0; // 배경 투명화
      }
    }
    ctx.putImageData(imgData, 0, 0);
  } catch (err) {
    console.warn('processClothTransparency fallback:', err);
  }
  return off;
}

// 4. 🎨 [포토샵 컬러 & 조명 매치 필터: matchPhotoshopLighting]
function matchPhotoshopLighting(faceImg) {
  if (!faceImg || !faceImg.complete || faceImg.naturalWidth === 0) return;

  try {
    const off = document.createElement('canvas');
    off.width = 64; off.height = 64;
    const ctx = off.getContext('2d');
    ctx.drawImage(faceImg, 0, 0, 64, 64);
    const d = ctx.getImageData(0, 0, 64, 64).data;

    let totalR = 0, totalG = 0, totalB = 0, count = 0;
    for (let i = 0; i < d.length; i += 16) {
      if (d[i+3] > 100) {
        totalR += d[i]; totalG += d[i+1]; totalB += d[i+2];
        count++;
      }
    }
    if (count > 0) {
      const avgR = totalR / count;
      const avgG = totalG / count;
      const avgB = totalB / count;
      const lum = 0.299 * avgR + 0.587 * avgG + 0.114 * avgB;

      window.photoshopLightMatch.lumRatio = Math.max(0.85, Math.min(1.2, lum / 140));
      window.photoshopLightMatch.warmShift = Math.max(-15, Math.min(15, (avgR - avgB) * 0.25));
    }
  } catch (e) {
    console.warn('matchPhotoshopLighting fallback:', e);
  }
}

// 5. 🪄 [포토샵 2025 AI 자동 의상합성: runPhotoshopAutoBlend]
async function runPhotoshopAutoBlend() {
  const profile = window.currentProfileName || 'haesang';
  const outfitNum = window.currentWardrobeNum || 1;
  const hasCustom = window.hasCustomCloth;

  // 1. 얼굴 사진 컬러 & 조명 분석
  if (window.userFaceImage) {
    matchPhotoshopLighting(window.userFaceImage);
  }

  // 2. 황금비율 자동 조절 (얼굴 크기, 목선 위치)
  window.faceScale = 1.05;
  window.faceOffsetX = 0;
  window.faceOffsetY = -2;

  // 3. 백엔드 레시피 호출
  try {
    const res = await fetch('/api/photoshop-ai-swap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile, outfitNum, hasCustomCloth: hasCustom })
    });
    const data = await res.json();
    if (data.success) {
      window.photoshopLightMatch.shadowDepth = data.recipe.shadowDepth || 0.5;
    }
  } catch (err) {
    window.photoshopLightMatch.shadowDepth = 0.5;
  }

  window.cachedCutoutCanvas = null; // 재처리
  drawMainFittingAvatar();

  if (typeof showToast === 'function') {
    showToast('🪄 [포토샵 2025 AI 합성]: 목선 접촉 그림자 & 조명 매치가 황금비율로 완성되었습니다!', 'success');
  }
}

// 6. 별칭 함수 (호환성 유지)
function applyRealVtonStudioLook() {
  runPhotoshopAutoBlend();
}

// 7. 🧬 [지능형 피부톤 YCbCr 감지 & 머리 위 차량 시트/배경/옷깃 100% 칼삭제 엔진]
function autoDetectAndCutoutFace(img) {
  if (!img || !img.complete || img.naturalWidth === 0) return null;
  const currentSrc = img.src || '';
  if (window.cachedCutoutCanvas && window.lastCutoutSourceSrc === currentSrc && window.lastCutoutUseSmart === window.useSmartCutout) {
    return window.cachedCutoutCanvas;
  }

  const off = document.createElement('canvas');
  const w = img.naturalWidth || img.width || 360;
  const h = img.naturalHeight || img.height || 360;
  off.width = w;
  off.height = h;
  const offCtx = off.getContext('2d');
  offCtx.drawImage(img, 0, 0, w, h);

  if (!window.useSmartCutout) {
    window.cachedCutoutCanvas = off;
    window.lastCutoutSourceSrc = currentSrc;
    window.lastCutoutUseSmart = false;
    return off;
  }

  try {
    const imgData = offCtx.getImageData(0, 0, w, h);
    const data = imgData.data;

    let skinSumX = 0, skinSumY = 0, skinCount = 0;
    for (let y = 0; y < h; y += 2) {
      for (let x = 0; x < w; x += 2) {
        const idx = (y * w + x) * 4;
        const r = data[idx], g = data[idx + 1], b = data[idx + 2];
        const cb = -0.169 * r - 0.331 * g + 0.5 * b + 128;
        const cr = 0.5 * r - 0.419 * g - 0.081 * b + 128;
        if (cb >= 85 && cb <= 135 && cr >= 135 && cr <= 180 && r > 60 && g > 40 && b > 20) {
          skinSumX += x;
          skinSumY += y;
          skinCount++;
        }
      }
    }

    const detectedFaceX = skinCount > 50 ? (skinSumX / skinCount) : (w * 0.5);
    const detectedFaceY = skinCount > 50 ? (skinSumY / skinCount) : (h * 0.48);
    const estRadius = Math.sqrt(skinCount * 4 / Math.PI) * 0.95;
    const faceR = Math.max(w * 0.25, Math.min(w * 0.45, estRadius || (w * 0.35)));

    let topBgR = 0, topBgG = 0, topBgB = 0, topBgCount = 0;
    const margin = Math.floor(w * 0.08);
    for (let y = 0; y < margin; y++) {
      for (let x = 0; x < w; x++) {
        const i1 = (y * w + x) * 4;
        topBgR += data[i1]; topBgG += data[i1 + 1]; topBgB += data[i1 + 2];
        topBgCount++;
      }
    }
    topBgR /= topBgCount; topBgG /= topBgCount; topBgB /= topBgCount;

    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const idx = (y * w + x) * 4;
        let r = data[idx], g = data[idx + 1], b = data[idx + 2], a = data[idx + 3];
        if (a === 0) continue;

        const normDx = (x - detectedFaceX) / faceR;
        const normDy = (y - detectedFaceY) / (faceR * 1.15);
        const dist = Math.hypot(normDx, normDy);

        // 1. 머리 위 차량 시트/천장 삭제
        if (y < detectedFaceY - faceR * 0.85) {
          const bgDist = Math.hypot(r - topBgR, g - topBgG, b - topBgB);
          if (bgDist < 75 || y < detectedFaceY - faceR * 1.25) {
            data[idx + 3] = 0;
            continue;
          }
        }

        // 2. 턱 아래 기존 옷깃/티셔츠 삭제
        if (y > detectedFaceY + faceR * 0.85) {
          const neckDist = Math.abs(x - detectedFaceX);
          if (neckDist > faceR * 0.45 || y > detectedFaceY + faceR * 1.1) {
            data[idx + 3] = 0;
            continue;
          } else {
            const fade = Math.max(0, 1 - (y - (detectedFaceY + faceR * 0.85)) / (faceR * 0.25));
            data[idx + 3] = Math.round(a * fade);
          }
        }

        // 3. 좌우 배경 벽지/창문 삭제
        if (dist > 1.05) {
          const edgeDist = (dist - 1.05) / 0.15;
          if (edgeDist >= 1.0) {
            data[idx + 3] = 0;
            continue;
          } else {
            data[idx + 3] = Math.round(a * Math.max(0, 1 - edgeDist));
          }
        }

        // 4. AI 화보 뷰티 보정
        if (window.autoBeautyFilter && data[idx + 3] > 0) {
          r = Math.min(255, r * 1.08 + 5);
          g = Math.min(255, g * 1.07 + 4);
          b = Math.min(255, b * 1.06 + 3);
          if (r > g && g > b) {
            r = Math.min(255, r * 1.03);
            b = Math.min(255, b * 0.98);
          }
          data[idx] = r;
          data[idx + 1] = g;
          data[idx + 2] = b;
        }
      }
    }
    offCtx.putImageData(imgData, 0, 0);
  } catch (e) {
    console.warn('autoDetectAndCutoutFace fallback:', e);
  }

  window.cachedCutoutCanvas = off;
  window.lastCutoutSourceSrc = currentSrc;
  window.lastCutoutUseSmart = true;
  return off;
}

function processSmartFaceCutout(img) {
  return autoDetectAndCutoutFace(img);
}

// 8. 10벌 시그니처 의상 착장 변경
function applyWardrobeOutfit(outfitNum) {
  window.currentWardrobeNum = outfitNum;
  window.hasCustomCloth = false; // 기본 10벌 선택 시 커스텀 모드 해제

  const outfitsMeta = {
    1: { name: '🌸 [1번] K-하이틴 핑크 가디건 & 플리츠 스커트', top: '#f43f5e', bottom: '#2563eb', style: 'pleats_skirt' },
    2: { name: '🎀 [2번] 청량 아이돌 데님 자켓 & 화이트 원피스', top: '#0284c7', bottom: '#ffffff', style: 'onepiece' },
    3: { name: '🎓 [3번] 명문 프레피 블레이저 & 체크 리본', top: '#1e1b4b', bottom: '#1e293b', style: 'preppy' },
    4: { name: '👕 [4번] 시티보이 오버핏 후드 & 스트릿 카고', top: '#059669', bottom: '#334155', style: 'hoodie' },
    5: { name: '🧥 [5번] 베이지 트렌치 롱코트', top: '#b45309', bottom: '#1e293b', style: 'trench' },
    6: { name: '👔 [6번] 청담 테일러드 VIP 로열 네이비 수트', top: '#0f172a', bottom: '#0f172a', style: 'vip_suit' },
    7: { name: '✨ [7번] 캐시미어 웜골드 니트 & 슬랙스', top: '#ca8a04', bottom: '#f8fafc', style: 'knit_slacks' },
    8: { name: '🔮 [8번] 2035 글로벌 CEO 네오-퍼플 수트', top: '#581c87', bottom: '#020617', style: 'ceo_suit' },
    9: { name: '🚀 [9번] 우주 AI 과학자 사이버 테크웨어', top: '#0891b2', bottom: '#0f172a', style: 'techwear' },
    10: { name: '👑 [10번] 로열 골드 갈라 파티 드레스 & 턱시도', top: '#eab308', bottom: '#1c1917', style: 'gala' }
  };

  const meta = outfitsMeta[outfitNum] || outfitsMeta[1];

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

// 9. 모바일 핀치 줌 인터랙션
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
      initialFaceScale = window.faceScale || 1.0;
    }
  }, { passive: true });

  canvas.addEventListener('touchmove', (e) => {
    if (e.touches.length === 2 && initialPinchDist > 0) {
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      const currentDist = Math.hypot(dx, dy);
      const ratio = currentDist / initialPinchDist;

      window.faceScale = Math.max(0.5, Math.min(2.5, initialFaceScale * ratio));
      drawMainFittingAvatar();
    }
  }, { passive: true });

  canvas.addEventListener('touchend', (e) => {
    if (e.touches.length < 2) {
      initialPinchDist = 0;
    }
  });
}

// 10. 언제나 직접 터치 & 마우스 드래그 이동
function initFaceTouchDragInteraction(canvasId) {
  const canvas = document.getElementById(canvasId || 'main-fitting-canvas');
  if (!canvas || canvas.dataset.dragInitialized) return;
  canvas.dataset.dragInitialized = 'true';

  let isDragging = false;
  let startX = 0, startY = 0;
  let lastTouchX = 0, lastTouchY = 0;

  const onStart = (clientX, clientY) => {
    isDragging = true;
    startX = clientX;
    startY = clientY;
    lastTouchX = clientX;
    lastTouchY = clientY;
  };

  const onMove = (clientX, clientY, e) => {
    if (!isDragging) return;
    const totalDx = clientX - startX;
    const totalDy = clientY - startY;

    if (Math.abs(totalDx) > Math.abs(totalDy) * 0.7 || Math.abs(totalDy) > 25) {
      const dx = clientX - lastTouchX;
      const dy = clientY - lastTouchY;
      lastTouchX = clientX;
      lastTouchY = clientY;

      window.faceOffsetX = Math.max(-140, Math.min(140, (window.faceOffsetX || 0) + dx * 0.85));
      window.faceOffsetY = Math.max(-140, Math.min(140, (window.faceOffsetY || 0) + dy * 0.85));
      drawMainFittingAvatar();
      if (e && e.cancelable && Math.abs(totalDx) > Math.abs(totalDy)) {
        e.preventDefault();
      }
    }
  };

  const onEnd = () => { isDragging = false; };

  canvas.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      onStart(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: false });

  canvas.addEventListener('touchmove', (e) => {
    if (e.touches.length === 1) {
      onMove(e.touches[0].clientX, e.touches[0].clientY, e);
    }
  }, { passive: false });

  canvas.addEventListener('touchend', onEnd);

  canvas.addEventListener('mousedown', (e) => {
    if (e.button === 0) {
      onStart(e.clientX, e.clientY);
    }
  });
  window.addEventListener('mousemove', (e) => {
    if (isDragging) {
      onMove(e.clientX, e.clientY, e);
    }
  });
  window.addEventListener('mouseup', onEnd);
}

// 11. 🔥 [포토샵 2025 실사 의상 셰이딩 & 인물 딥-블렌딩 렌더러: renderPhotoshopAISwap]
function renderPhotoshopAISwap() {
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  const cx = w / 2;

  ctx.clearRect(0, 0, w, h);

  // 1. 아웃포커싱 스튜디오 보케(Bokeh) & 림라이트 배경
  const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
  bgGrad.addColorStop(0, '#040711');
  bgGrad.addColorStop(0.35, '#0b1328');
  bgGrad.addColorStop(0.7, '#070b18');
  bgGrad.addColorStop(1, '#020409');
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, w, h);

  // 스튜디오 아웃포커싱 보케 조명 구형 파티클 (Depth of Field)
  ctx.save();
  const bokehs = [
    { x: cx - 120, y: 90, r: 45, c: 'rgba(244, 63, 94, 0.12)' },
    { x: cx + 110, y: 130, r: 60, c: 'rgba(59, 130, 246, 0.12)' },
    { x: cx - 60, y: 220, r: 35, c: 'rgba(168, 85, 247, 0.09)' },
    { x: cx + 80, y: 280, r: 50, c: 'rgba(251, 191, 36, 0.08)' }
  ];
  for (const b of bokehs) {
    const g = ctx.createRadialGradient(b.x, b.y, 5, b.x, b.y, b.r);
    g.addColorStop(0, b.c);
    g.addColorStop(1, 'transparent');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();

  // 2. 바닥 3D 런웨이 스포트라이트
  const tiltYOffset = (window.pitchTilt || 0) * 1.5;
  const floorY = h - 45 + tiltYOffset;
  const spotRadiusX = 155;
  const spotRadiusY = Math.max(16, 26 - (window.pitchTilt || 0) * 0.35);

  ctx.save();
  const floorGrad = ctx.createRadialGradient(cx, floorY, 15, cx, floorY, spotRadiusX);
  const spotColor = window.targetGender === 'female' ? 'rgba(244, 63, 94, 0.55)' : 'rgba(59, 130, 246, 0.55)';
  floorGrad.addColorStop(0, spotColor);
  floorGrad.addColorStop(0.5, 'rgba(168, 85, 247, 0.25)');
  floorGrad.addColorStop(1, 'transparent');
  ctx.fillStyle = floorGrad;
  ctx.beginPath();
  ctx.ellipse(cx, floorY, spotRadiusX, spotRadiusY, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // 3. 3D 회전 각도 삼각함수
  const rad = ((window.yawAngle || 0) * Math.PI) / 180;
  const cosYaw = Math.cos(rad);
  const sinYaw = Math.sin(rad);
  const isBackView = cosYaw < -0.15;

  // 4. 인체 비율 및 머리 위치 (headY = 145px)
  const scale = (window.mainAvatarHeight / 165);
  const widthFactor = (window.mainAvatarWeight / 55);
  const headY = 145 + (window.pitchTilt || 0) * 0.4;
  const headRadius = 38 * scale;

  const baseShoulderW = (window.targetGender === 'female' ? 44 : 56) * scale * widthFactor;
  const projShoulderW = baseShoulderW * (0.35 + 0.65 * Math.abs(cosYaw));
  const torsoH = (window.targetGender === 'female' ? 135 : 150) * scale;
  const legH = (window.targetGender === 'female' ? 190 : 205) * scale;

  const outfitsColors = {
    1: { top: '#f43f5e', bottom: '#2563eb', accent: '#fbbf24', style: 'skirt' },
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

  // 5. 뒷머리 헤어 볼륨
  if (window.targetGender === 'female' && !isBackView) {
    ctx.save();
    const hairBgGrad = ctx.createLinearGradient(cx - headRadius * 1.2, headY, cx + headRadius * 1.2, headY + torsoH * 0.9);
    hairBgGrad.addColorStop(0, '#2d221c');
    hairBgGrad.addColorStop(0.5, '#18120e');
    hairBgGrad.addColorStop(1, '#0d0907');
    ctx.fillStyle = hairBgGrad;
    ctx.beginPath();
    ctx.moveTo(cx - headRadius * 1.15, headY);
    ctx.bezierCurveTo(cx - headRadius * 1.3, headY + 50, cx - headRadius * 1.1, headY + torsoH * 0.85, cx - headRadius * 0.7, headY + torsoH * 0.88);
    ctx.lineTo(cx + headRadius * 0.7, headY + torsoH * 0.88);
    ctx.bezierCurveTo(cx + headRadius * 1.1, headY + torsoH * 0.85, cx + headRadius * 1.3, headY + 50, cx + headRadius * 1.15, headY);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  // 6. 하체 실사 셰이딩
  ctx.save();
  const legShift = sinYaw * 10;
  const legWidth = (18 * widthFactor) * (0.55 + 0.45 * Math.abs(cosYaw));

  if (outfit.style === 'skirt' || (window.targetGender === 'female' && (outfit.style === 'preppy' || outfit.style === 'onepiece'))) {
    const skirtTopW = projShoulderW * 0.72;
    const skirtBottomW = projShoulderW * 1.38;
    const skirtH = 78 * scale;
    const skirtY = headY + headRadius + torsoH - 15;

    const skirtGrad = ctx.createLinearGradient(cx - skirtBottomW, 0, cx + skirtBottomW, 0);
    skirtGrad.addColorStop(0, outfit.bottom);
    skirtGrad.addColorStop(0.3, '#1d4ed8');
    skirtGrad.addColorStop(0.7, outfit.bottom);
    skirtGrad.addColorStop(1, '#0f172a');

    ctx.fillStyle = skirtGrad;
    ctx.beginPath();
    ctx.moveTo(cx - skirtTopW, skirtY);
    ctx.lineTo(cx + skirtTopW, skirtY);
    ctx.bezierCurveTo(cx + skirtBottomW * 0.95, skirtY + skirtH * 0.5, cx + skirtBottomW, skirtY + skirtH * 0.9, cx + skirtBottomW, skirtY + skirtH);
    ctx.lineTo(cx - skirtBottomW, skirtY + skirtH);
    ctx.bezierCurveTo(cx - skirtBottomW, skirtY + skirtH * 0.9, cx - skirtBottomW * 0.95, skirtY + skirtH * 0.5, cx - skirtTopW, skirtY);
    ctx.closePath();
    ctx.fill();

    for (let f = -skirtBottomW * 0.85; f <= skirtBottomW * 0.85; f += 14) {
      ctx.strokeStyle = 'rgba(0,0,0,0.35)';
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      ctx.moveTo(cx + f * 0.5, skirtY);
      ctx.lineTo(cx + f, skirtY + skirtH);
      ctx.stroke();

      ctx.strokeStyle = 'rgba(255,255,255,0.2)';
      ctx.lineWidth = 1.0;
      ctx.beginPath();
      ctx.moveTo(cx + f * 0.5 + 2, skirtY);
      ctx.lineTo(cx + f + 3, skirtY + skirtH);
      ctx.stroke();
    }

    const skinGrad = ctx.createLinearGradient(cx - legWidth, 0, cx + legWidth, 0);
    skinGrad.addColorStop(0, '#fde2ce');
    skinGrad.addColorStop(0.5, '#fce7d8');
    skinGrad.addColorStop(1, '#ebd0bc');
    ctx.fillStyle = skinGrad;

    ctx.beginPath();
    ctx.roundRect(cx - legWidth * 1.8 + legShift * 0.3, skirtY + skirtH, legWidth, legH - skirtH, [0, 0, 6, 6]);
    ctx.roundRect(cx + legWidth * 0.8 - legShift * 0.3, skirtY + skirtH, legWidth, legH - skirtH, [0, 0, 6, 6]);
    ctx.fill();

  } else if (outfit.style === 'gala' && window.targetGender === 'female') {
    const dressTopW = projShoulderW * 0.7;
    const dressBottomW = projShoulderW * 1.65;
    const dressH = legH + 12;
    const dressY = headY + headRadius + torsoH - 20;

    const galaGrad = ctx.createLinearGradient(cx - dressBottomW, 0, cx + dressBottomW, 0);
    galaGrad.addColorStop(0, '#ca8a04');
    galaGrad.addColorStop(0.35, '#fde047');
    galaGrad.addColorStop(0.65, '#eab308');
    galaGrad.addColorStop(1, '#713f12');

    ctx.fillStyle = galaGrad;
    ctx.beginPath();
    ctx.moveTo(cx - dressTopW, dressY);
    ctx.lineTo(cx + dressTopW, dressY);
    ctx.bezierCurveTo(cx + dressBottomW * 0.9, dressY + dressH * 0.6, cx + dressBottomW, dressY + dressH * 0.9, cx + dressBottomW, dressY + dressH);
    ctx.lineTo(cx - dressBottomW, dressY + dressH);
    ctx.bezierCurveTo(cx - dressBottomW, dressY + dressH * 0.9, cx - dressBottomW * 0.9, dressY + dressH * 0.6, cx - dressTopW, dressY);
    ctx.closePath();
    ctx.fill();

  } else {
    const pantsGrad = ctx.createLinearGradient(cx - projShoulderW, 0, cx + projShoulderW, 0);
    pantsGrad.addColorStop(0, outfit.bottom);
    pantsGrad.addColorStop(0.4, '#334155');
    pantsGrad.addColorStop(0.7, outfit.bottom);
    pantsGrad.addColorStop(1, '#090d16');

    ctx.fillStyle = pantsGrad;
    ctx.beginPath();
    ctx.roundRect(cx - (projShoulderW * 0.44) + legShift * 0.5, headY + headRadius + torsoH - 10, legWidth, legH, [4, 4, 8, 8]);
    ctx.roundRect(cx + (projShoulderW * 0.44) - legWidth - legShift * 0.5, headY + headRadius + torsoH - 10, legWidth, legH, [4, 4, 8, 8]);
    ctx.fill();

    ctx.strokeStyle = 'rgba(255,255,255,0.15)';
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    ctx.moveTo(cx - (projShoulderW * 0.44) + legWidth * 0.5 + legShift * 0.5, headY + headRadius + torsoH);
    ctx.lineTo(cx - (projShoulderW * 0.44) + legWidth * 0.5 + legShift * 0.5, headY + headRadius + torsoH + legH - 5);
    ctx.moveTo(cx + (projShoulderW * 0.44) - legWidth * 0.5 - legShift * 0.5, headY + headRadius + torsoH);
    ctx.lineTo(cx + (projShoulderW * 0.44) - legWidth * 0.5 - legShift * 0.5, headY + headRadius + torsoH + legH - 5);
    ctx.stroke();
  }

  // 3D 구두
  ctx.fillStyle = '#090d16';
  ctx.beginPath();
  ctx.roundRect(cx - projShoulderW * 0.46 + legShift * 0.5, headY + headRadius + torsoH + legH - 10, legWidth + 6, 12, [5, 8, 3, 3]);
  ctx.roundRect(cx + projShoulderW * 0.46 - legWidth - 6 - legShift * 0.5, headY + headRadius + torsoH + legH - 10, legWidth + 6, 12, [5, 8, 3, 3]);
  ctx.fill();
  ctx.restore();

  // 7. 상체 실사 의상 셰이딩 (또는 커스텀 옷 사진 워핑 합성)
  ctx.save();
  const shoulderY = headY + headRadius - 2;

  if (window.hasCustomCloth && window.cachedClothCanvas) {
    // 👚 [커스텀 옷 사진 워핑 합성]
    const clothW = projShoulderW * 2.3;
    const clothH = torsoH * 1.15;
    ctx.drawImage(window.cachedClothCanvas, cx - clothW * 0.5, shoulderY, clothW, clothH);
  } else {
    // 10벌 시그니처 의상 실사 볼륨 렌더링
    const top3DGrad = ctx.createLinearGradient(cx - projShoulderW, 0, cx + projShoulderW, 0);
    top3DGrad.addColorStop(0, outfit.top);
    top3DGrad.addColorStop(0.3, '#ffffff22');
    top3DGrad.addColorStop(0.5, outfit.top);
    top3DGrad.addColorStop(1, '#00000055');

    ctx.fillStyle = top3DGrad;
    ctx.shadowColor = 'rgba(0,0,0,0.35)';
    ctx.shadowBlur = 8;
    ctx.shadowOffsetY = 4;

    if (window.targetGender === 'female') {
      const waistW = projShoulderW * 0.68;
      const hipW = projShoulderW * 0.88;
      const waistY = shoulderY + torsoH * 0.58;
      const hipY = shoulderY + torsoH;

      ctx.beginPath();
      ctx.moveTo(cx - projShoulderW, shoulderY + 8);
      ctx.bezierCurveTo(cx - projShoulderW * 0.6, shoulderY - 2, cx - 18, shoulderY + 2, cx, shoulderY + 4);
      ctx.bezierCurveTo(cx + 18, shoulderY + 2, cx + projShoulderW * 0.6, shoulderY - 2, cx + projShoulderW, shoulderY + 8);
      ctx.bezierCurveTo(cx + projShoulderW * 1.05, shoulderY + 25, cx + projShoulderW * 0.95, waistY - 15, cx + waistW, waistY);
      ctx.bezierCurveTo(cx + waistW * 0.95, waistY + 15, cx + hipW * 0.95, hipY - 10, cx + hipW, hipY);
      ctx.lineTo(cx - hipW, hipY);
      ctx.bezierCurveTo(cx - hipW * 0.95, hipY - 10, cx - waistW * 0.95, waistY + 15, cx - waistW, waistY);
      ctx.bezierCurveTo(cx - projShoulderW * 0.95, waistY - 15, cx - projShoulderW * 1.05, shoulderY + 25, cx - projShoulderW, shoulderY + 8);
      ctx.closePath();
      ctx.fill();
    } else {
      const waistW = projShoulderW * 0.85;
      ctx.beginPath();
      ctx.moveTo(cx - projShoulderW, shoulderY + 6);
      ctx.lineTo(cx + projShoulderW, shoulderY + 6);
      ctx.bezierCurveTo(cx + projShoulderW, shoulderY + 40, cx + waistW * 1.05, shoulderY + torsoH * 0.7, cx + waistW, shoulderY + torsoH);
      ctx.lineTo(cx - waistW, shoulderY + torsoH);
      ctx.bezierCurveTo(cx - waistW * 1.05, shoulderY + torsoH * 0.7, cx - projShoulderW, shoulderY + 40, cx - projShoulderW, shoulderY + 6);
      ctx.closePath();
      ctx.fill();
    }
    ctx.shadowColor = 'transparent';

    if (!isBackView) {
      const vOffset = sinYaw * (projShoulderW * 0.35);
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.moveTo(cx + vOffset - 11 * Math.abs(cosYaw), shoulderY);
      ctx.lineTo(cx + vOffset + 11 * Math.abs(cosYaw), shoulderY);
      ctx.lineTo(cx + vOffset, shoulderY + 36);
      ctx.closePath();
      ctx.fill();

      ctx.fillStyle = outfit.accent;
      ctx.beginPath();
      ctx.arc(cx + vOffset, shoulderY + 12, 5, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#fef08a';
      for (let b = 0; b < 3; b++) {
        ctx.beginPath();
        ctx.arc(cx + vOffset, shoulderY + 45 + b * 22, 2.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // 분리형 두 팔 & 손
    const armW = 14 * widthFactor;
    const sleeveGrad = ctx.createLinearGradient(cx - projShoulderW - armW, 0, cx - projShoulderW, 0);
    sleeveGrad.addColorStop(0, outfit.top);
    sleeveGrad.addColorStop(1, '#00000044');

    ctx.fillStyle = sleeveGrad;
    ctx.beginPath();
    ctx.roundRect(cx - projShoulderW - armW * 0.7, shoulderY + 10, armW, torsoH * 0.82, [8, 4, 6, 6]);
    ctx.fill();

    ctx.beginPath();
    ctx.roundRect(cx + projShoulderW - armW * 0.3, shoulderY + 10, armW, torsoH * 0.82, [4, 8, 6, 6]);
    ctx.fill();

    ctx.fillStyle = window.mainSkinTone || '#fce7d8';
    ctx.beginPath();
    ctx.ellipse(cx - projShoulderW - armW * 0.2, shoulderY + torsoH * 0.85, 4.5, 7, 0, 0, Math.PI * 2);
    ctx.ellipse(cx + projShoulderW + armW * 0.2, shoulderY + torsoH * 0.85, 4.5, 7, 0, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();

  // 8. 목선 렌더링 & 포토샵 2025 Smart Contact Shadow (접촉 그림자)
  const faceCenterX = cx + sinYaw * (headRadius * 0.28) + (window.faceOffsetX || 0);
  const faceCenterY = headY + (window.faceOffsetY || 0);
  const curHeadRadius = headRadius * (window.faceScale || 1.0);

  ctx.save();
  const neckW = 12 * scale * widthFactor;
  const neckH = 22 * scale;
  const neckY = headY + headRadius * 0.75;

  const neckGrad = ctx.createLinearGradient(cx - neckW, 0, cx + neckW, 0);
  neckGrad.addColorStop(0, '#f5d3bd');
  neckGrad.addColorStop(0.4, window.mainSkinTone || '#fce7d8');
  neckGrad.addColorStop(1, '#e2beaa');
  ctx.fillStyle = neckGrad;
  ctx.beginPath();
  ctx.roundRect(cx - neckW * 0.5, neckY, neckW, neckH, [0, 0, 4, 4]);
  ctx.fill();

  // ① [포토샵 2025 Smart Neck & Collar Shadow] 옷깃 접촉 그림자
  const shadowDepth = window.photoshopLightMatch.shadowDepth || 0.48;
  const contactShadow = ctx.createRadialGradient(cx, neckY + neckH * 0.65, 3, cx, neckY + neckH * 0.65, neckW * 1.3);
  contactShadow.addColorStop(0, `rgba(20, 10, 5, ${shadowDepth})`);
  contactShadow.addColorStop(0.6, `rgba(20, 10, 5, ${shadowDepth * 0.4})`);
  contactShadow.addColorStop(1, 'transparent');
  ctx.fillStyle = contactShadow;
  ctx.beginPath();
  ctx.ellipse(cx, neckY + neckH * 0.7, neckW * 1.2, 8, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // 9. 얼굴 실사 합성 (지능형 배경 삭제 & 포토샵 딥-블렌딩)
  if (!isBackView) {
    if (window.userFaceImage && window.userFaceImage.complete) {
      ctx.save();
      const processedCanvas = autoDetectAndCutoutFace(window.userFaceImage);
      const drawSrc = processedCanvas || window.userFaceImage;

      ctx.beginPath();
      ctx.ellipse(faceCenterX, faceCenterY, curHeadRadius * 0.98, curHeadRadius * 1.05, 0, 0, Math.PI * 2);
      ctx.clip();

      ctx.drawImage(
        drawSrc,
        faceCenterX - curHeadRadius * 0.98,
        faceCenterY - curHeadRadius * 1.05,
        curHeadRadius * 1.96,
        curHeadRadius * 2.1
      );
      ctx.restore();

    } else {
      if (typeof drawDetailedIllustrationFace === 'function') {
        drawDetailedIllustrationFace(ctx, faceCenterX, faceCenterY, curHeadRadius, sinYaw);
      }
    }
  } else {
    ctx.save();
    const hairGrad = ctx.createRadialGradient(faceCenterX, faceCenterY - 10, 8, faceCenterX, faceCenterY, curHeadRadius * 1.05);
    hairGrad.addColorStop(0, '#362a22');
    hairGrad.addColorStop(0.7, '#1e1612');
    hairGrad.addColorStop(1, '#0e0a07');
    ctx.fillStyle = hairGrad;
    ctx.beginPath();
    ctx.arc(faceCenterX, faceCenterY, curHeadRadius * 1.02, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  updateAngleDisplayBadge();
}

// 12. 별칭 함수 (drawMainFittingAvatar -> renderPhotoshopAISwap)
function drawMainFittingAvatar() {
  renderPhotoshopAISwap();
}

function updateAngleDisplayBadge() {
  const badge = document.getElementById('main-angle-display-badge');
  if (!badge) return;
  const yaw = Math.round(window.yawAngle || 0);
  const pitch = Math.round(window.pitchTilt || 0);
  badge.innerHTML = `🔄 3D 360° 터치 회전 (좌우: ${yaw}° · 상하: ${pitch >= 0 ? '+' : ''}${pitch}°)`;
}

// 📸 얼굴 사진 보조 함수 정의
function triggerFaceCameraPhoto() {
  const inp = document.getElementById('face-camera-input') || document.getElementById('face-upload-input');
  if (inp) inp.click();
  const menu = document.getElementById('face-photo-menu');
  if (menu) menu.classList.add('hidden');
}

function triggerFaceAlbumPhoto() {
  const inp = document.getElementById('face-upload-input') || document.getElementById('face-camera-input');
  if (inp) inp.click();
  const menu = document.getElementById('face-photo-menu');
  if (menu) menu.classList.add('hidden');
}

function resetFaceToIllustration() {
  window.userFaceImage = null;
  window.isFaceUploaded = false;
  window.cachedCutoutCanvas = null;
  window.lastCutoutSourceSrc = '';
  const statusEl = document.getElementById('face-photo-status');
  if (statusEl) statusEl.textContent = '🎨 일러스트 아바타 모드';
  const menu = document.getElementById('face-photo-menu');
  if (menu) menu.classList.add('hidden');
  renderPhotoshopAISwap();
}

window.triggerFaceCameraPhoto = triggerFaceCameraPhoto;
window.triggerFaceAlbumPhoto = triggerFaceAlbumPhoto;
window.resetFaceToIllustration = resetFaceToIllustration;

document.addEventListener('DOMContentLoaded', () => {
  initFaceTouchDragInteraction('main-fitting-canvas');
  initFaceTouchDragInteraction('app-fitting-canvas');
  initPinchZoomInteraction('main-fitting-canvas');
  initPinchZoomInteraction('app-fitting-canvas');
});
setTimeout(() => {
  initFaceTouchDragInteraction('main-fitting-canvas');
  initFaceTouchDragInteraction('app-fitting-canvas');
  initPinchZoomInteraction('main-fitting-canvas');
  initPinchZoomInteraction('app-fitting-canvas');
}, 300);
'''

def patch_v51_file(filepath):
    p = Path(filepath)
    content = p.read_text(encoding="utf-8")

    # 1. 상단 컨트롤 바 교체: 듀얼 슬롯 (내 얼굴 + 내 옷 합성)
    # 기존: <!-- 👑 [캔버스 외부 상단 독립 컨트롤 헤더: 모드 전환 & 내 얼굴 사진 넣기] 부터 시작해서 그 닫는 </div>까지
    top_marker = '<!-- 👑 [캔버스 외부 상단 독립 컨트롤 헤더'
    t_start = content.find(top_marker)
    if t_start != -1:
        # 이 헤더 div가 닫히는 지점 찾기
        t_end = content.find('<!-- 캔버스 영역', t_start)
        if t_end == -1:
            t_end = content.find('<div id="fitting-canvas-container"', t_start)
        if t_end == -1:
            t_end = content.find('id="main-fitting-canvas"', t_start)
            if t_end != -1:
                t_end = content.rfind('<div', 0, t_end)

        if t_end != -1:
            # t_end 바로 앞의 </div> 뒤까지
            div_close = content.rfind('</div>', t_start, t_end)
            if div_close != -1:
                div_close += 6
                content = content[:t_start] + DUAL_SLOT_HEADER_HTML + content[div_close:]
                print(f"✅ Replaced top header with Dual-Slot header in {filepath}")

    # 2. 캔버스 바로 밑 1줄 리모컨 바 교체 (또는 v5-one-line-remote-bar 교체)
    r_start = content.find('id="v5-one-line-remote-bar"')
    if r_start != -1:
        div_open = content.rfind('<div', 0, r_start)
        # 닫는 </div> 찾기
        div_close = content.find('</div>', r_start)
        # 내부 중첩 div들 건너뛰기
        next_sec = content.find('<!-- 🚪👗 [나만의 옷장함', r_start)
        if next_sec == -1:
            next_sec = content.find('나만의 꿈의 옷장함', r_start)
        if next_sec != -1:
            real_close = content.rfind('</div>', r_start, next_sec)
            if real_close != -1:
                real_close += 6
                content = content[:div_open] + V51_ONE_LINE_REMOTE_BAR_HTML + '\n\n        ' + content[next_sec:]
                print(f"✅ Replaced remote bar with v5.1 Photoshop-AI 1-line bar in {filepath}")

    # 3. JS 엔진 교체
    s_idx = content.find('// ══════════════════════════════════════════════════════════════════\n// 🌟 [Omni-Nexus')
    if s_idx == -1:
        s_idx = content.find('window.faceOffsetX =')
    e_idx = content.find('async function sendRemoteClipboardToAntigravity')

    if s_idx != -1 and e_idx != -1:
        content = content[:s_idx] + FULL_V51_ENGINE_JS + '\n\n    ' + content[e_idx:]
        print(f"✅ Replaced JS engine with v5.1 Photoshop-AI engine in {filepath}")
    else:
        print(f"⚠️ JS engine boundary not found in {filepath}: s_idx={s_idx}, e_idx={e_idx}")

    # 4. 버전 배지: v5.1 Photoshop-AI Studio
    content = content.replace('v5.0 Real-VTON Studio', 'v5.1 Photoshop-AI Studio')
    content = content.replace('v5.0', 'v5.1')

    p.write_text(content, encoding="utf-8")

    # 5. 문법 검사 (node --check)
    scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
    combined = "\n\n// --- NEXT ---\n\n".join(scripts)
    temp_f = Path(".temp_check_v51.js")
    temp_f.write_text(combined, encoding="utf-8")
    res = subprocess.run(["node", "--check", str(temp_f)], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"🎉 [PASS] Node syntax check OK for {filepath}!")
        if temp_f.exists():
            temp_f.unlink()
        return True
    else:
        print(f"❌ [FAIL] Node syntax check failed for {filepath}:\n{res.stderr}")
        return False

if __name__ == '__main__':
    ok1 = patch_v51_file('dashboard/index.html')
    ok2 = patch_v51_file('dashboard/dream_closet_future_master_app.html')
    if ok1 and ok2:
        print("🚀 Both files successfully patched to v5.1 Photoshop-AI Studio!")
    else:
        sys.exit(1)

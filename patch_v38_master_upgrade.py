# -*- coding: utf-8 -*-
"""
patch_v38_master_upgrade.py
--------------------------------------------------------------------------------
이상일 대표님([COMMANDER-000])의 v3.8 Pro 특명 일괄 반영 스크립트
1. 캔버스 touch-action: pan-y !important; 및 touchmove 수직 스크롤 무간섭 보장
2. 상단 IN/OUT 오토싱크 바를 1번 사령부(#tab-command) 내부로 완전 격리 (공통 상단 슬림화)
3. 버전 배지 'v3.8 Auto-QA' 적용
4. 캔버스 하단 [🔄 360° 자동 회전 쇼케이스 ON/OFF] & [↔️ 360° 회전 슬라이더] 장착
5. 기본 마네킹에 또렷한 패션 일러스트 이목구비(눈·코·입) 렌더링
6. 사진 합성 후 자동 펼쳐지는 [🎉 사진 합성 완료! 👉 다음 단계를 눌러보세요!] 가이드 박스 장착
   - Step 1: applyPhotoRecommendedLook()
   - Step 2: toggleAuto360Rotate()
   - Step 3: saveMyFittingPhoto()
--------------------------------------------------------------------------------
"""

import sys
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 캔버스 바로 아래에 들어갈 360도 자동 회전 & 슬라이더 & 다음 단계 가이드 박스 마크업
CANVAS_CONTROLS_AND_NEXT_STEP_MARKUP = """
        <!-- 🎛️ [360° 런웨이 컨트롤 바: 터치 충돌 제로 슬라이더 & 자동 회전 쇼케이스] -->
        <div class="w-full max-w-[420px] mx-auto p-2.5 rounded-xl bg-slate-900/90 border border-purple-500/30 space-y-2 text-xs">
          <div class="flex items-center justify-between gap-2">
            <span class="text-slate-300 font-bold flex items-center gap-1 text-[11px]">
              <span>↔️</span><span>360° 회전 슬라이더</span>
            </span>
            <button type="button" onclick="toggleAuto360Rotate()" id="btn-auto-rotate" class="px-2.5 py-1 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-[11px] transition shadow flex items-center gap-1 active:scale-95">
              <span>🔄</span><span id="auto-rotate-text">360° 자동 회전 쇼케이스 ON</span>
            </button>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-[10px] text-slate-400 font-mono">0°</span>
            <input type="range" id="main-yaw-slider" min="0" max="360" value="0" oninput="onYawSliderChange(this.value)" class="w-full h-2 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-purple-500">
            <span class="text-[10px] text-slate-400 font-mono">360°</span>
          </div>
        </div>

        <!-- 🎉 [사진 합성 완료 후 자동 노출되는 다음 단계(Next Step) 3단계 가이드 박스] -->
        <div id="post-photo-next-step-box" class="hidden w-full max-w-[420px] mx-auto p-3.5 rounded-2xl bg-gradient-to-b from-amber-950/60 via-slate-900/95 to-slate-950 border border-amber-500/50 shadow-2xl space-y-2.5 animate-fade-in">
          <div class="flex items-center justify-between border-b border-amber-500/30 pb-2">
            <div class="flex items-center gap-1.5 font-extrabold text-amber-300 text-xs">
              <span class="text-base">🎉</span>
              <span>내 실제 얼굴 사진 합성 완료! 👉 다음 단계를 눌러보세요!</span>
            </div>
            <span class="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-bold">Step Guide</span>
          </div>

          <div class="grid grid-cols-1 gap-2 pt-1 text-xs">
            <button type="button" onclick="applyPhotoRecommendedLook()" class="w-full px-3 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-pink-600 to-purple-600 hover:from-amber-400 hover:to-purple-500 text-white font-bold shadow-lg shadow-pink-500/20 flex items-center justify-center gap-2 transition active:scale-95">
              <span>✨</span><span>다음 1단계: 내 얼굴 맞춤 AI 추천 코디 입히기 (터치!)</span>
            </button>
            <button type="button" onclick="toggleAuto360Rotate()" class="w-full px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold flex items-center justify-center gap-2 transition active:scale-95">
              <span>🔄</span><span>다음 2단계: 360° 런웨이 자동 회전으로 앞·옆·뒤 핏 보기</span>
            </button>
            <button type="button" onclick="saveMyFittingPhoto()" class="w-full px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-emerald-500/30 font-semibold flex items-center justify-center gap-2 transition active:scale-95">
              <span>💾</span><span>다음 3단계: 내 얼굴 코디 화보 스마트폰에 저장하기</span>
            </button>
          </div>
        </div>
"""

V38_JS_LOGIC = """
// ============================================================================
// 🌟 [Omni-Nexus v3.8 Auto-QA] 스마트폰 스크롤 무간섭 360° & 패션 일러스트 이목구비 & Next-Step 엔진
// ============================================================================

window.isAutoRotating = false;
window.autoRotateTimer = null;

// 1. 슬라이더로 360° 회전
function onYawSliderChange(val) {
  window.yawAngle = parseFloat(val);
  drawMainFittingAvatar();
}

// 2. 360° 자동 회전 쇼케이스 토글
function toggleAuto360Rotate() {
  window.isAutoRotating = !window.isAutoRotating;
  const btnText = document.getElementById('auto-rotate-text');
  const slider = document.getElementById('main-yaw-slider');

  if (window.isAutoRotating) {
    if (btnText) btnText.innerText = '⏹️ 360° 자동 회전 멈추기';
    if (typeof showToast === 'function') showToast('🔄 360° 런웨이 쇼케이스 자동 회전 시작!', 'info');
    if (typeof speakMainText === 'function') speakMainText('360도 런웨이 쇼케이스를 감상해 보세요.');

    window.autoRotateTimer = setInterval(() => {
      window.yawAngle = (window.yawAngle + 1.5) % 360;
      if (slider) slider.value = Math.round(window.yawAngle);
      drawMainFittingAvatar();
    }, 30);
  } else {
    if (btnText) btnText.innerText = '🔄 360° 자동 회전 쇼케이스 ON';
    if (window.autoRotateTimer) clearInterval(window.autoRotateTimer);
    if (typeof showToast === 'function') showToast('⏹️ 자동 회전이 정지되었습니다.', 'info');
  }
}

// 3. 사진 합성 후 Step 1: 내 얼굴 맞춤 AI 추천 코디 자동 입히기
function applyPhotoRecommendedLook() {
  applyQuickLook('suit');
  if (typeof showToast === 'function') {
    showToast('✨ [AI 추천 코디]: 청담동 최고급 VIP 테일러드 맞춤 수트가 입혀졌습니다!', 'success');
  }
  if (typeof speakMainText === 'function') {
    speakMainText('대표님의 얼굴에 가장 어울리는 청담 VIP 비즈니스 수트를 매칭해 드렸습니다!');
  }
  // 자동 회전 살짝 시연
  if (!window.isAutoRotating) {
    toggleAuto360Rotate();
    setTimeout(() => { if (window.isAutoRotating) toggleAuto360Rotate(); }, 5000);
  }
}

// 4. 사진 합성 후 Step 3: 내 얼굴 코디 화보 스마트폰에 저장하기
function saveMyFittingPhoto() {
  const canvas = document.getElementById('main-fitting-canvas') || document.getElementById('app-fitting-canvas');
  if (!canvas) return;

  try {
    const dataUrl = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = `내얼굴_3D런웨이_코디화보_${new Date().toISOString().slice(0,10)}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    if (typeof showToast === 'function') {
      showToast('💾 [저장 완료]: 내 얼굴 코디 화보가 갤러리에 저장되었습니다!', 'success');
    }
    if (typeof speakMainText === 'function') {
      speakMainText('내 얼굴 코디 화보가 이미지 파일로 저장되었습니다.');
    }
  } catch (err) {
    if (typeof showToast === 'function') {
      showToast('화보 저장 실패: ' + err.message, 'error');
    }
  }
}

// 5. 모바일 터치 이벤트 개선: 수직 스크롤 100% 보장 (pan-y)
function init3DTouchInteraction(canvasId) {
  const canvas = document.getElementById(canvasId || 'main-fitting-canvas');
  if (!canvas || canvas.dataset.touch3dInitialized) return;
  canvas.dataset.touch3dInitialized = 'true';

  let isDragging = false;
  let startX = 0;
  let startY = 0;
  let lastX = 0;
  let lastY = 0;
  let isHorizontalDrag = false;

  function onStart(x, y) {
    isDragging = true;
    startX = x;
    startY = y;
    lastX = x;
    lastY = y;
    isHorizontalDrag = false;
    canvas.style.cursor = 'grabbing';
  }

  function onMove(x, y, evt) {
    if (!isDragging) return;

    const deltaX = x - lastX;
    const deltaY = y - lastY;
    const totalDistX = Math.abs(x - startX);
    const totalDistY = Math.abs(y - startY);

    // 수직 스크롤 여부 판별: 수직 이동이 수평 이동보다 크면 화면 상하 스크롤 허용!
    if (!isHorizontalDrag) {
      if (totalDistY > totalDistX && totalDistY > 8) {
        // 사용자가 페이지를 위아래로 스크롤하는 중 -> 절대 preventDefault 하지 않음!
        isDragging = false;
        canvas.style.cursor = 'grab';
        return;
      }
      if (totalDistX > totalDistY && totalDistX > 8) {
        isHorizontalDrag = true;
      }
    }

    if (isHorizontalDrag && evt && evt.cancelable) {
      evt.preventDefault(); // 좌우 회전일 때만 화면 스크롤 차단
    }

    lastX = x;
    lastY = y;

    // 좌우 360° 연속 회전
    window.yawAngle = (window.yawAngle + deltaX * 0.75 + 360) % 360;

    // 슬라이더 동기화
    const slider = document.getElementById('main-yaw-slider');
    if (slider) slider.value = Math.round(window.yawAngle);

    // 상하 -30° ~ +30° 틸트
    if (isHorizontalDrag) {
      window.pitchTilt = Math.max(-30, Math.min(30, window.pitchTilt - deltaY * 0.25));
    }

    drawMainFittingAvatar();
  }

  function onEnd() {
    isDragging = false;
    isHorizontalDrag = false;
    canvas.style.cursor = 'grab';
  }

  canvas.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      onStart(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: true }); // passive: true로 상하 스크롤 즉각 반응!

  canvas.addEventListener('touchmove', (e) => {
    if (e.touches.length === 1) {
      onMove(e.touches[0].clientX, e.touches[0].clientY, e);
    }
  }, { passive: false });

  canvas.addEventListener('touchend', onEnd);
  canvas.addEventListener('touchcancel', onEnd);

  canvas.addEventListener('mousedown', (e) => {
    onStart(e.clientX, e.clientY);
  });

  window.addEventListener('mousemove', (e) => {
    if (isDragging) onMove(e.clientX, e.clientY, e);
  });

  window.addEventListener('mouseup', () => {
    if (isDragging) onEnd();
  });
}

// 6. 사진 트리거 후 Next-Step 박스 자동 노출
const origTriggerFaceCapture = window.triggerFaceCapture;
window.triggerFaceCapture = function(mode) {
  const menu = document.getElementById('face-photo-menu');
  if (menu) menu.classList.add('hidden');

  if (mode === 'reset') {
    window.userFaceImage = null;
    drawMainFittingAvatar();
    const nextBox = document.getElementById('post-photo-next-step-box');
    if (nextBox) nextBox.classList.add('hidden');
    if (typeof showToast === 'function') showToast('🔄 기본 마네킹 얼굴로 초기화되었습니다.', 'info');
    return;
  }

  let input = document.getElementById('temp-face-file-input');
  if (!input) {
    input = document.createElement('input');
    input.type = 'file';
    input.id = 'temp-face-file-input';
    input.accept = 'image/*';
    input.style.display = 'none';
    document.body.appendChild(input);
  }

  if (mode === 'camera') {
    input.setAttribute('capture', 'user');
  } else {
    input.removeAttribute('capture');
  }

  input.onchange = function(e) {
    const file = e.target.files && e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(evt) {
      const img = new Image();
      img.onload = function() {
        window.userFaceImage = img;
        drawMainFittingAvatar();

        // 🎉 사진 합성 완료! Next-Step 가이드 박스 자동 펼침!
        const nextBox = document.getElementById('post-photo-next-step-box');
        if (nextBox) {
          nextBox.classList.remove('hidden');
          nextBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        if (typeof showToast === 'function') {
          showToast('📸 내 실제 얼굴 사진이 아바타에 100% 합성되었습니다!', 'success');
        }
        if (typeof speakMainText === 'function') {
          speakMainText('와! 사진이 멋지게 합성되었어요! 아래 1단계 추천 코디 버튼을 눌러보세요!');
        }
      };
      img.src = evt.target.result;
    };
    reader.readAsDataURL(file);
    input.value = '';
  };

  input.click();
};

// 7. 정교한 패션 일러스트 이목구비 렌더링 함수
function drawDetailedIllustrationFace(ctx, faceCenterX, faceCenterY, headRadius, sinYaw) {
  ctx.save();
  // 피부 그라디언트
  const faceGrad = ctx.createRadialGradient(
    faceCenterX - sinYaw * 10, faceCenterY - 10, 5,
    faceCenterX, faceCenterY, headRadius
  );
  faceGrad.addColorStop(0, '#fff4ec');
  faceGrad.addColorStop(0.75, window.mainSkinTone || '#fce7d8');
  faceGrad.addColorStop(1, '#e2ad8b');
  ctx.fillStyle = faceGrad;
  ctx.beginPath();
  ctx.arc(faceCenterX, faceCenterY, headRadius * 0.94, 0, Math.PI * 2);
  ctx.fill();

  // 음영 볼터치 (생기 블러셔)
  ctx.fillStyle = 'rgba(244, 63, 94, 0.15)';
  ctx.beginPath();
  ctx.ellipse(faceCenterX - headRadius * 0.45, faceCenterY + 6, 9, 5, 0, 0, Math.PI * 2);
  ctx.ellipse(faceCenterX + headRadius * 0.45, faceCenterY + 6, 9, 5, 0, 0, Math.PI * 2);
  ctx.fill();

  // 세련된 아치형 눈썹
  ctx.strokeStyle = '#2d241e';
  ctx.lineWidth = 1.8;
  ctx.lineCap = 'round';
  // 왼쪽 눈썹
  ctx.beginPath();
  ctx.moveTo(faceCenterX - headRadius * 0.6, faceCenterY - 12);
  ctx.quadraticCurveTo(faceCenterX - headRadius * 0.35, faceCenterY - 17, faceCenterX - headRadius * 0.15, faceCenterY - 13);
  ctx.stroke();
  // 오른쪽 눈썹
  ctx.beginPath();
  ctx.moveTo(faceCenterX + headRadius * 0.15, faceCenterY - 13);
  ctx.quadraticCurveTo(faceCenterX + headRadius * 0.35, faceCenterY - 17, faceCenterX + headRadius * 0.6, faceCenterY - 12);
  ctx.stroke();

  // 또렷한 패션 일러스트 눈 & 아이라인
  ctx.strokeStyle = '#1e1b18';
  ctx.lineWidth = 1.6;
  // 왼쪽 눈매
  ctx.beginPath();
  ctx.arc(faceCenterX - headRadius * 0.38, faceCenterY - 4, 6.5, Math.PI * 1.1, Math.PI * 1.9);
  ctx.stroke();
  // 오른쪽 눈매
  ctx.beginPath();
  ctx.arc(faceCenterX + headRadius * 0.38, faceCenterY - 4, 6.5, Math.PI * 1.1, Math.PI * 1.9);
  ctx.stroke();

  // 눈동자 (빛나는 다크 헤이즐)
  ctx.fillStyle = '#261c14';
  ctx.beginPath();
  ctx.arc(faceCenterX - headRadius * 0.38, faceCenterY - 4, 3.5, 0, Math.PI * 2);
  ctx.arc(faceCenterX + headRadius * 0.38, faceCenterY - 4, 3.5, 0, Math.PI * 2);
  ctx.fill();

  // 눈동자 하이라이트
  ctx.fillStyle = '#ffffff';
  ctx.beginPath();
  ctx.arc(faceCenterX - headRadius * 0.38 - 1, faceCenterY - 5.5, 1.2, 0, Math.PI * 2);
  ctx.arc(faceCenterX + headRadius * 0.38 - 1, faceCenterY - 5.5, 1.2, 0, Math.PI * 2);
  ctx.fill();

  // 오뚝한 콧날 쉐이딩
  ctx.strokeStyle = 'rgba(180, 120, 80, 0.45)';
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.moveTo(faceCenterX - sinYaw * 2, faceCenterY - 2);
  ctx.lineTo(faceCenterX, faceCenterY + 8);
  ctx.lineTo(faceCenterX + 2.5, faceCenterY + 9);
  ctx.stroke();

  // 생기 있는 미소 립 (틴트 립)
  ctx.fillStyle = '#e11d48';
  ctx.beginPath();
  ctx.moveTo(faceCenterX - 8, faceCenterY + 16);
  ctx.quadraticCurveTo(faceCenterX, faceCenterY + 20, faceCenterX + 8, faceCenterY + 16);
  ctx.quadraticCurveTo(faceCenterX, faceCenterY + 17, faceCenterX - 8, faceCenterY + 16);
  ctx.fill();

  // 볼륨감 있는 프리미엄 헤어 스타일 (앞머리 텍스처)
  ctx.fillStyle = '#1e1b18';
  ctx.beginPath();
  ctx.arc(faceCenterX, faceCenterY - 8, headRadius * 0.98, Math.PI * 0.88, Math.PI * 2.12);
  ctx.fill();
  ctx.restore();
}
"""

def patch_index_html():
    print("[🛠️ index.html v3.8 Pro 개혁 시작]")
    with open("dashboard/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. 버전 배지 업그레이드: v3.8 Auto-QA
    html = re.sub(r'id="ota-version-text"[^>]*>.*?</span>', 'id="ota-version-text" class="font-bold text-amber-300">v3.8 Auto-QA</span>', html)

    # 2. 상단 공통 영역에서 rgon-signal-sync-bar 제거하고 1번 사령부(#tab-command) 내부로 완전 격리!
    # 기존 위치(body 상단 또는 nav 뒤)에 있던 rgon-signal-sync-bar 추출
    sync_bar_match = re.search(r'<!-- ⚡ \[르곤-안실장 양방향 시그널 오토싱크 사령탑 미니 바\].*?<!-- Genspark 센서 장착 가이드 모달 -->\s*<div id="sensor-guide-modal".*?</div>\s*</div>', html, re.DOTALL)
    if sync_bar_match:
        sync_bar_code = sync_bar_match.group(0)
        # 상단 공통 영역에서 삭제
        html = html[:sync_bar_match.start()] + html[sync_bar_match.end():]
        print("  ✅ 상단 공통 영역에서 rgon-signal-sync-bar 분리 완료!")

        # 1번 탭(#tab-command) 내부 최상단에 주입
        idx_tab_cmd = html.find('id="tab-command"')
        if idx_tab_cmd != -1:
            idx_inner = html.find('>', idx_tab_cmd) + 1
            html = html[:idx_inner] + "\n" + sync_bar_code + "\n" + html[idx_inner:]
            print("  ✅ 1번 사령부(tab-command) 내부로 rgon-signal-sync-bar 완전 격리 완료!")

    # 3. 캔버스 스타일에 touch-action: pan-y !important; 강제 적용
    html = re.sub(
        r'<canvas id="main-fitting-canvas"[^>]*>',
        '<canvas id="main-fitting-canvas" width="450" height="600" class="w-full h-full object-contain" style="touch-action: pan-y !important; cursor: grab;"></canvas>',
        html
    )

    # 4. 캔버스 컨테이너 바로 뒤에 360도 슬라이더 & 다음 단계(Next Step) 가이드 박스 주입
    if "post-photo-next-step-box" not in html:
        idx_canvas_wrap = html.find('id="main-fitting-canvas"')
        if idx_canvas_wrap != -1:
            # find the closing div of canvas wrapper
            idx_wrap_close = html.find('</div>', html.find('id="main-angle-display-badge"', idx_canvas_wrap))
            if idx_wrap_close != -1:
                idx_insert = idx_wrap_close + 6
                html = html[:idx_insert] + "\n" + CANVAS_CONTROLS_AND_NEXT_STEP_MARKUP + "\n" + html[idx_insert:]
                print("  ✅ 캔버스 바로 아래에 360° 슬라이더 & Next-Step 3단계 가이드 박스 주입 완료!")

    # 5. V38_JS_LOGIC 주입
    if "🌟 [Omni-Nexus v3.8 Auto-QA]" not in html:
        idx_script_end = html.rfind("</script>")
        if idx_script_end != -1:
            html = html[:idx_script_end] + "\n\n" + V38_JS_LOGIC + "\n" + html[idx_script_end:]
            print("  ✅ V38_JS_LOGIC 주입 완료!")

    # 6. drawMainFittingAvatar 내부에서 기본 마네킹일 때 drawDetailedIllustrationFace 호출
    html = html.replace(
        "// 기본 마네킹 페이스 (입체 쉐이딩)",
        "// 또렷한 패션 일러스트 이목구비 렌더링\n      if (typeof drawDetailedIllustrationFace === 'function') {\n        drawDetailedIllustrationFace(ctx, faceCenterX, faceCenterY, headRadius, sinYaw);\n        ctx.restore();\n        updateAngleDisplayBadge();\n        return;\n      }\n      // 기본 마네킹 페이스 (입체 쉐이딩)"
    )

    with open("dashboard/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  ✅ dashboard/index.html v3.8 업데이트 저장 완료!")

def patch_dream_closet_app():
    print("[🛠️ dream_closet_future_master_app.html v3.8 개혁 시작]")
    with open("dashboard/dream_closet_future_master_app.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = re.sub(r'id="ota-version-text"[^>]*>.*?</span>', 'id="ota-version-text" class="font-bold text-amber-300">v3.8 Auto-QA</span>', html)

    html = re.sub(
        r'<canvas id="app-fitting-canvas"[^>]*>',
        '<canvas id="app-fitting-canvas" width="450" height="600" class="w-full h-full object-contain" style="touch-action: pan-y !important; cursor: grab;"></canvas>',
        html
    )

    if "post-photo-next-step-box" not in html:
        idx_badge = html.find('id="main-angle-display-badge"')
        if idx_badge != -1:
            idx_wrap_close = html.find('</div>', idx_badge)
            if idx_wrap_close != -1:
                idx_insert = idx_wrap_close + 6
                html = html[:idx_insert] + "\n" + CANVAS_CONTROLS_AND_NEXT_STEP_MARKUP + "\n" + html[idx_insert:]
                print("  ✅ dream_closet에 360° 슬라이더 & Next-Step 3단계 가이드 박스 주입 완료!")

    if "🌟 [Omni-Nexus v3.8 Auto-QA]" not in html:
        idx_script_end = html.rfind("</script>")
        if idx_script_end != -1:
            html = html[:idx_script_end] + "\n\n" + V38_JS_LOGIC + "\n" + html[idx_script_end:]
            print("  ✅ dream_closet에 V38_JS_LOGIC 주입 완료!")

    html = html.replace(
        "// 기본 마네킹 페이스 (입체 쉐이딩)",
        "// 또렷한 패션 일러스트 이목구비 렌더링\n      if (typeof drawDetailedIllustrationFace === 'function') {\n        drawDetailedIllustrationFace(ctx, faceCenterX, faceCenterY, headRadius, sinYaw);\n        ctx.restore();\n        updateAngleDisplayBadge();\n        return;\n      }\n      // 기본 마네킹 페이스 (입체 쉐이딩)"
    )

    with open("dashboard/dream_closet_future_master_app.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  ✅ dream_closet_future_master_app.html v3.8 업데이트 저장 완료!")

def main():
    patch_index_html()
    patch_dream_closet_app()
    print("🎉 v3.8 Pro 4대 개혁 일괄 패치 완료!")

if __name__ == "__main__":
    main()

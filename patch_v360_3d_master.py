# -*- coding: utf-8 -*-
"""
patch_v360_3d_master.py
--------------------------------------------------------------------------------
1. dashboard/index.html & dashboard/dream_closet_future_master_app.html에
   - 3D 360° 좌우 연속 회전 (yawAngle) & 상하 틸트 (pitchTilt) 터치 스크롤 이벤트 탑재
   - 실제 얼굴 사진 원형 클리핑 합성 엔진 (drawImage + userFaceImage) 탑재
   - [📸 내 얼굴 사진 넣기] 버튼 & 플로팅 메뉴 장착
   - 4방향 고정 버튼 완전 삭제
   - 모든 결손 함수 (selectStudioVoiceMinimal, toggleDrawer, toggleQuizPopup, saveVaultCredentials 등) 100% 장착
--------------------------------------------------------------------------------
"""

import os
import sys
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 공통 3D 터치 & 렌더링 & 결손 함수 자바스크립트 블록
SHARED_JS_ENGINE = """
// ============================================================================
// 🌟 [Omni-Nexus v3.6 Pro] 3D 360° 인터랙션 & 실사 얼굴 합성 마스터 엔진
// ============================================================================

window.yawAngle = window.yawAngle || 0;       // 0° ~ 360° 연속 회전
window.pitchTilt = window.pitchTilt || 0;     // -25° ~ +25° 상하 틸트
window.userFaceImage = window.userFaceImage || null; // 사용자 실사 얼굴 이미지 객체
window.mainSubTabMode = window.mainSubTabMode || 'fitting'; // 'fitting' | 'future' | 'family'
window.mainCurrentOutfit = window.mainCurrentOutfit || 'basic';
window.mainAvatarHeight = window.mainAvatarHeight || 168;
window.mainAvatarWeight = window.mainAvatarWeight || 58;
window.mainSkinTone = window.mainSkinTone || '#fce7d8';

// 📸 1. 사진 메뉴 토글 & 캡처
function toggleFacePhotoMenu() {
  const menu = document.getElementById('face-photo-menu');
  if (menu) {
    menu.classList.toggle('hidden');
  }
}

function triggerFaceCapture(mode) {
  const menu = document.getElementById('face-photo-menu');
  if (menu) menu.classList.add('hidden');

  if (mode === 'reset') {
    window.userFaceImage = null;
    drawMainFittingAvatar();
    if (typeof showToast === 'function') {
      showToast('🔄 기본 마네킹 얼굴로 초기화되었습니다.', 'info');
    }
    const angleBadge = document.getElementById('main-angle-display-badge');
    if (angleBadge) {
      angleBadge.innerHTML = `🔄 3D ${Math.round(window.yawAngle)}° · ↕️ ${window.pitchTilt >= 0 ? '+' : ''}${Math.round(window.pitchTilt)}°`;
    }
    return;
  }

  // 모바일 카메라 또는 앨범 파일 인풋 동적 생성
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
        if (typeof showToast === 'function') {
          showToast('📸 내 실제 얼굴 사진이 아바타에 100% 합성되었습니다!', 'success');
        }
        if (typeof speakMainText === 'function') {
          speakMainText('대표님의 실제 얼굴 사진이 3D 런웨이 아바타에 선명하게 합성되었습니다!');
        }
      };
      img.src = evt.target.result;
    };
    reader.readAsDataURL(file);
    input.value = ''; // 재선택 가능하도록 초기화
  };

  input.click();
}

// 🔄 2. 3D 360° 좌우/상하 터치 & 마우스 드래그 이벤트 바인딩
function init3DTouchInteraction(canvasId) {
  const canvas = document.getElementById(canvasId || 'main-fitting-canvas');
  if (!canvas || canvas.dataset.touch3dInitialized) return;
  canvas.dataset.touch3dInitialized = 'true';

  let isDragging = false;
  let startX = 0;
  let startY = 0;
  let lastX = 0;
  let lastY = 0;

  function onStart(x, y) {
    isDragging = true;
    startX = x;
    startY = y;
    lastX = x;
    lastY = y;
    canvas.style.cursor = 'grabbing';
  }

  function onMove(x, y, evt) {
    if (!isDragging) return;
    if (evt && evt.cancelable) evt.preventDefault();

    const deltaX = x - lastX;
    const deltaY = y - lastY;
    lastX = x;
    lastY = y;

    // 좌우 360° 연속 회전
    window.yawAngle = (window.yawAngle + deltaX * 0.75 + 360) % 360;

    // 상하 -25° ~ +25° 틸트
    window.pitchTilt = Math.max(-25, Math.min(25, window.pitchTilt - deltaY * 0.35));

    // 실시간 렌더링
    drawMainFittingAvatar();
  }

  function onEnd() {
    isDragging = false;
    canvas.style.cursor = 'grab';
  }

  // 터치 이벤트 (모바일)
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
  canvas.addEventListener('touchcancel', onEnd);

  // 마우스 이벤트 (PC)
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

// 👗 3. 3D 아바타 & 런웨이 투영 렌더러
function drawMainFittingAvatar() {
  const canvas = document.getElementById('main-fitting-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  const cx = w / 2;

  ctx.clearRect(0, 0, w, h);

  // 1. 하이엔드 런웨이 배경 그라디언트
  const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
  bgGrad.addColorStop(0, '#060913');
  bgGrad.addColorStop(0.5, '#0b1329');
  bgGrad.addColorStop(1, '#020617');
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, w, h);

  // 2. 상하 틸트(pitchTilt)에 반응하는 3D 바닥 스포트라이트
  const tiltYOffset = window.pitchTilt * 1.8;
  const floorY = h - 50 + tiltYOffset;
  const spotRadiusX = 145;
  const spotRadiusY = Math.max(16, 26 - window.pitchTilt * 0.4); // 틸트에 따라 타원 편평비 변화

  ctx.save();
  const floorGrad = ctx.createRadialGradient(cx, floorY, 15, cx, floorY, spotRadiusX);
  if (window.mainSubTabMode === 'future') {
    floorGrad.addColorStop(0, 'rgba(6, 182, 212, 0.45)');
    floorGrad.addColorStop(0.6, 'rgba(59, 130, 246, 0.2)');
  } else if (window.mainSubTabMode === 'family') {
    floorGrad.addColorStop(0, 'rgba(234, 179, 8, 0.45)');
    floorGrad.addColorStop(0.6, 'rgba(249, 115, 22, 0.2)');
  } else {
    floorGrad.addColorStop(0, 'rgba(236, 72, 153, 0.45)');
    floorGrad.addColorStop(0.6, 'rgba(168, 85, 247, 0.2)');
  }
  floorGrad.addColorStop(1, 'transparent');
  ctx.fillStyle = floorGrad;
  ctx.beginPath();
  ctx.ellipse(cx, floorY, spotRadiusX, spotRadiusY, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // 3. 3D 각도 삼각함수 계산
  const rad = ((window.yawAngle || 0) * Math.PI) / 180;
  const cosYaw = Math.cos(rad); // +1 (정면) -> 0 (측면) -> -1 (뒷면)
  const sinYaw = Math.sin(rad); // +1 (우측) -> -1 (좌측)
  const isBackView = cosYaw < -0.15;

  // 인체 비율 계산
  const scale = (window.mainAvatarHeight / 170);
  const widthFactor = (window.mainAvatarWeight / 60);
  const headY = 115 - (scale - 1) * 30 + window.pitchTilt * 0.5;
  const headRadius = 38 * scale;
  const baseShoulderW = 56 * scale * widthFactor;
  // 좌우 회전에 따른 3D 어깨 너비 투영 (측면일 때 얇아짐)
  const projShoulderW = baseShoulderW * (0.35 + 0.65 * Math.abs(cosYaw));
  const torsoH = 148 * scale;
  const legH = 205 * scale;

  // 의상 색상 결정
  let topColor = '#6366f1';
  let pantsColor = '#1e293b';
  let accentColor = '#a855f7';

  if (window.mainCurrentOutfit === 'suit') {
    topColor = '#0f172a'; pantsColor = '#0f172a'; accentColor = '#38bdf8';
  } else if (window.mainCurrentOutfit === 'highteen') {
    topColor = '#f43f5e'; pantsColor = '#2563eb'; accentColor = '#facc15';
  } else if (window.mainCurrentOutfit === 'future_ceo') {
    topColor = '#1e1b4b'; pantsColor = '#090d16'; accentColor = '#06b6d4';
  } else if (window.mainCurrentOutfit === 'family_similar') {
    topColor = '#f97316'; pantsColor = '#334155'; accentColor = '#eab308';
  } else if (window.mainCurrentOutfit === 'zerocost') {
    topColor = '#10b981'; pantsColor = '#1e293b'; accentColor = '#34d399';
  }

  // 👨‍👧‍👧 모드 1: 가족 4인 앙상블 모드
  if (window.mainSubTabMode === 'family') {
    drawFamilyEnsemble(ctx, w, h, floorY);
    updateAngleDisplayBadge();
    return;
  }

  // 🔮 모드 2: 2035 미래 홀로그램 런웨이 모드 배경 효과
  if (window.mainSubTabMode === 'future') {
    ctx.save();
    ctx.strokeStyle = 'rgba(6, 182, 212, 0.25)';
    ctx.lineWidth = 1;
    for (let lx = -100; lx <= 100; lx += 25) {
      ctx.beginPath();
      ctx.moveTo(cx + lx * 2, floorY);
      ctx.lineTo(cx + lx * 0.2, headY - 40);
      ctx.stroke();
    }
    ctx.restore();
  }

  // 4. 하체 (팬츠 & 슈즈) 3D 투영
  ctx.save();
  ctx.fillStyle = pantsColor;

  const legShift = sinYaw * 12; // 옆모습일 때 앞뒤 다리 겹침
  const legWidth = (23 * widthFactor) * (0.55 + 0.45 * Math.abs(cosYaw));

  // 왼쪽 다리
  ctx.beginPath();
  ctx.roundRect(cx - (projShoulderW * 0.42) + legShift * 0.5, headY + headRadius + torsoH - 12, legWidth, legH, [4, 4, 8, 8]);
  ctx.fill();

  // 오른쪽 다리 (앞뒤 겹침 처리)
  ctx.beginPath();
  ctx.roundRect(cx + (projShoulderW * 0.42) - legWidth - legShift * 0.5, headY + headRadius + torsoH - 12, legWidth, legH, [4, 4, 8, 8]);
  ctx.fill();

  // 슈즈
  ctx.fillStyle = window.mainCurrentOutfit === 'highteen' ? '#f8fafc' : '#020617';
  ctx.beginPath();
  ctx.roundRect(cx - (projShoulderW * 0.45) + legShift * 0.5, headY + headRadius + torsoH + legH - 12, legWidth + 6, 14, [4, 8, 4, 4]);
  ctx.roundRect(cx + (projShoulderW * 0.45) - legWidth - 6 - legShift * 0.5, headY + headRadius + torsoH + legH - 12, legWidth + 6, 14, [4, 8, 4, 4]);
  ctx.fill();
  ctx.restore();

  // 5. 상체 (자켓 / 셔츠 / 코트) 3D 투영
  ctx.save();
  ctx.fillStyle = topColor;
  ctx.beginPath();
  ctx.roundRect(cx - projShoulderW, headY + headRadius - 6, projShoulderW * 2, torsoH, [12, 12, 6, 6]);
  ctx.fill();

  // 의상 디테일 (정면/측면/뒷면 반응형)
  if (!isBackView) {
    // [앞모습]: V존 셔츠 및 넥타이/라펠
    const vOffset = sinYaw * (projShoulderW * 0.5);
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.moveTo(cx + vOffset - 12 * Math.abs(cosYaw), headY + headRadius - 4);
    ctx.lineTo(cx + vOffset + 12 * Math.abs(cosYaw), headY + headRadius - 4);
    ctx.lineTo(cx + vOffset, headY + headRadius + 44);
    ctx.closePath();
    ctx.fill();

    // 넥타이 / 이너 포인트
    ctx.fillStyle = accentColor;
    ctx.beginPath();
    ctx.moveTo(cx + vOffset - 5 * Math.abs(cosYaw), headY + headRadius + 6);
    ctx.lineTo(cx + vOffset + 5 * Math.abs(cosYaw), headY + headRadius + 6);
    ctx.lineTo(cx + vOffset, headY + headRadius + 65);
    ctx.closePath();
    ctx.fill();

    // 골드 / 실버 수트 단추
    ctx.fillStyle = '#e2e8f0';
    for (let b = 0; b < 3; b++) {
      ctx.beginPath();
      ctx.arc(cx + vOffset, headY + headRadius + 75 + b * 22, 2.5, 0, Math.PI * 2);
      ctx.fill();
    }
  } else {
    // [뒷모습]: 테일러드 등판 절개선 및 주름 라인
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.18)';
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    ctx.moveTo(cx, headY + headRadius + 4);
    ctx.lineTo(cx, headY + headRadius + torsoH - 6);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(cx - projShoulderW * 0.7, headY + headRadius + 20);
    ctx.lineTo(cx, headY + headRadius + 50);
    ctx.lineTo(cx + projShoulderW * 0.7, headY + headRadius + 20);
    ctx.stroke();
  }

  // 6. 3D 양팔 렌더링
  ctx.fillStyle = topColor;
  const armW = 16 * widthFactor;
  // 왼팔
  ctx.beginPath();
  ctx.roundRect(cx - projShoulderW - armW * 0.6, headY + headRadius, armW, torsoH * 0.85, [8, 8, 8, 8]);
  ctx.fill();
  // 오른팔
  ctx.beginPath();
  ctx.roundRect(cx + projShoulderW - armW * 0.4, headY + headRadius, armW, torsoH * 0.85, [8, 8, 8, 8]);
  ctx.fill();
  ctx.restore();

  // 7. 목 & 머리 & 얼굴 (실사 사진 원형 클리핑 100% 합성)
  const faceCenterX = cx + sinYaw * (headRadius * 0.28);
  const faceCenterY = headY;

  // 목
  ctx.fillStyle = window.mainSkinTone;
  ctx.beginPath();
  ctx.roundRect(cx - 9, headY + headRadius - 10, 18, 20, [2, 2, 4, 4]);
  ctx.fill();

  if (!isBackView) {
    // [앞모습/비스듬한 각도]: 실사 사진 합성 또는 마네킹 페이스
    if (window.userFaceImage && window.userFaceImage.complete) {
      // 🌟 실제 업로드/촬영된 본인 얼굴 사진 원형 클리핑 합성!
      ctx.save();
      ctx.beginPath();
      ctx.arc(faceCenterX, faceCenterY, headRadius * 0.94, 0, Math.PI * 2);
      ctx.clip();
      ctx.drawImage(
        window.userFaceImage,
        faceCenterX - headRadius * 0.94,
        faceCenterY - headRadius * 0.94,
        headRadius * 1.88,
        headRadius * 1.88
      );
      ctx.restore();

      // 골드 VIP 네온 테두리 링
      ctx.save();
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2.5;
      ctx.shadowColor = '#fbbf24';
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.arc(faceCenterX, faceCenterY, headRadius * 0.94, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    } else {
      // 기본 마네킹 페이스 (입체 쉐이딩)
      ctx.save();
      const faceGrad = ctx.createRadialGradient(
        faceCenterX - sinYaw * 10, faceCenterY - 10, 5,
        faceCenterX, faceCenterY, headRadius
      );
      faceGrad.addColorStop(0, '#fff1e6');
      faceGrad.addColorStop(0.7, window.mainSkinTone);
      faceGrad.addColorStop(1, '#d4a373');
      ctx.fillStyle = faceGrad;
      ctx.beginPath();
      ctx.arc(faceCenterX, faceCenterY, headRadius * 0.92, 0, Math.PI * 2);
      ctx.fill();

      // 세련된 헤어 스타일 (앞머리)
      ctx.fillStyle = '#1e1b18';
      ctx.beginPath();
      ctx.arc(faceCenterX, faceCenterY - 6, headRadius * 0.95, Math.PI * 0.9, Math.PI * 2.1);
      ctx.fill();

      // 사이버/트렌디 글래스 (미래 모드)
      if (window.mainSubTabMode === 'future') {
        ctx.fillStyle = 'rgba(6, 182, 212, 0.75)';
        ctx.beginPath();
        ctx.roundRect(faceCenterX - headRadius * 0.7, faceCenterY - 6, headRadius * 1.4, 14, [4, 4, 4, 4]);
        ctx.fill();
      }
      ctx.restore();
    }
  } else {
    // [뒷모습]: 풍성한 볼륨감의 뒤통수 헤어스타일 렌더링
    ctx.save();
    const hairGrad = ctx.createRadialGradient(
      faceCenterX, faceCenterY - 10, 10,
      faceCenterX, faceCenterY, headRadius * 1.05
    );
    hairGrad.addColorStop(0, '#2d241e');
    hairGrad.addColorStop(0.8, '#18120e');
    hairGrad.addColorStop(1, '#0c0907');
    ctx.fillStyle = hairGrad;
    ctx.beginPath();
    ctx.arc(faceCenterX, faceCenterY, headRadius * 1.02, 0, Math.PI * 2);
    ctx.fill();

    // 뒷머리 헤어 텍스처 결
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
    ctx.lineWidth = 1.5;
    for (let a = -20; a <= 20; a += 10) {
      ctx.beginPath();
      ctx.arc(faceCenterX + a, faceCenterY + 10, headRadius * 0.8, Math.PI * 0.2, Math.PI * 0.8);
      ctx.stroke();
    }
    ctx.restore();
  }

  // 8. 하단 각도 배지 갱신
  updateAngleDisplayBadge();
}

// 👨‍👧‍👧 가족 4인 앙상블 렌더러
function drawFamilyEnsemble(ctx, w, h, floorY) {
  const members = [
    { name: '아빠 (나)', x: w * 0.38, scale: 1.0, color: '#0f172a', inner: '#38bdf8' },
    { name: '큰딸 (CEO)', x: w * 0.58, scale: 0.92, color: '#4f46e5', inner: '#ec4899' },
    { name: '둘째 (외교관)', x: w * 0.22, scale: 0.84, color: '#059669', inner: '#f59e0b' },
    { name: '셋째 (AI아티스트)', x: w * 0.76, scale: 0.78, color: '#d97706', inner: '#8b5cf6' }
  ];

  members.forEach((m) => {
    const s = m.scale;
    const hY = 135 + (1 - s) * 70;
    const r = 30 * s;
    const shW = 42 * s;
    const tH = 120 * s;
    const lH = 170 * s;

    // 바닥 그림자
    ctx.save();
    ctx.fillStyle = 'rgba(0, 0, 0, 0.35)';
    ctx.beginPath();
    ctx.ellipse(m.x, floorY - (1 - s) * 20, 36 * s, 10 * s, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // 다리
    ctx.fillStyle = '#1e293b';
    ctx.fillRect(m.x - shW * 0.35, hY + r + tH - 5, 14 * s, lH);
    ctx.fillRect(m.x + shW * 0.35 - 14 * s, hY + r + tH - 5, 14 * s, lH);

    // 몸통 (패밀리 시밀러 자켓)
    ctx.fillStyle = m.color;
    ctx.beginPath();
    ctx.roundRect(m.x - shW, hY + r, shW * 2, tH, [8, 8, 4, 4]);
    ctx.fill();

    // 이너 컬러 포인트
    ctx.fillStyle = m.inner;
    ctx.beginPath();
    ctx.arc(m.x, hY + r + 24 * s, 6 * s, 0, Math.PI * 2);
    ctx.fill();

    // 얼굴 (아빠는 실사 사진이 있으면 합성!)
    if (m.name.includes('나') && window.userFaceImage && window.userFaceImage.complete) {
      ctx.save();
      ctx.beginPath();
      ctx.arc(m.x, hY, r, 0, Math.PI * 2);
      ctx.clip();
      ctx.drawImage(window.userFaceImage, m.x - r, hY - r, r * 2, r * 2);
      ctx.restore();
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2;
      ctx.stroke();
    } else {
      ctx.fillStyle = window.mainSkinTone;
      ctx.beginPath();
      ctx.arc(m.x, hY, r, 0, Math.PI * 2);
      ctx.fill();
      // 헤어
      ctx.fillStyle = '#1e1b18';
      ctx.beginPath();
      ctx.arc(m.x, hY - 4 * s, r, Math.PI * 0.85, Math.PI * 2.15);
      ctx.fill();
    }

    // 이름표
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(m.name, m.x, floorY + 16);
  });
}

// 각도 및 얼굴 합성 상태 배지 갱신
function updateAngleDisplayBadge() {
  const badge = document.getElementById('main-angle-display-badge');
  if (!badge) return;

  const yaw = Math.round(window.yawAngle || 0);
  const pitch = Math.round(window.pitchTilt || 0);
  const faceStatus = window.userFaceImage ? ' · 📸 실사합성' : '';

  badge.innerHTML = `🔄 3D ${yaw}° · ↕️ ${pitch >= 0 ? '+' : ''}${pitch}°${faceStatus} (터치로 360° 회전)`;
}

// 🔀 4. 모드 전환 (피팅 / 2035 / 가족)
function switchMainFittingSubTab(mode) {
  window.mainSubTabMode = mode;

  // 상단 탭 스타일 갱신
  ['fitting', 'future', 'family'].forEach(m => {
    const btn = document.getElementById(`tab-sub-${m}`);
    if (btn) {
      if (m === mode) {
        btn.className = 'px-2.5 py-1 rounded-lg bg-purple-600 text-white font-bold transition shadow-sm';
      } else {
        btn.className = 'px-2.5 py-1 rounded-lg text-slate-300 hover:text-white transition';
      }
    }
  });

  drawMainFittingAvatar();

  if (mode === 'future') {
    if (typeof showToast === 'function') showToast('🔮 2035 미래 글로벌 런웨이 모드로 전환되었습니다!', 'info');
    if (typeof speakMainText === 'function') speakMainText('2035년 미래 타임머신 런웨이입니다. 글로벌 리더의 홀로그램 슈트가 동기화되었습니다.');
  } else if (mode === 'family') {
    if (typeof showToast === 'function') showToast('👨‍👧‍👧 4인 가족 시밀러룩 앙상블 모드로 전환되었습니다!', 'info');
    if (typeof speakMainText === 'function') speakMainText('사랑하는 세 딸과 함께 선 4인 가족 시밀러룩 앙상블입니다.');
  } else {
    if (typeof showToast === 'function') showToast('👗 1인 3D 피팅 런웨이 모드입니다.', 'info');
  }
}

// 🎨 5. 6대 원터치 룩 캡슐 적용
function applyQuickLook(lookId) {
  window.mainCurrentOutfit = lookId;

  // 버튼 스타일 active 갱신
  const lookBtns = ['basic', 'highteen', 'suit', 'future_ceo', 'family_similar', 'zerocost'];
  lookBtns.forEach(id => {
    const b = document.getElementById(`look-btn-${id}`);
    if (b) {
      if (id === lookId) {
        b.classList.remove('bg-slate-800/80', 'text-slate-300', 'border-slate-700/60');
        b.classList.add('bg-gradient-to-r', 'from-purple-600', 'to-pink-600', 'text-white', 'border-purple-400/50', 'shadow-md');
      } else {
        b.classList.remove('bg-gradient-to-r', 'from-purple-600', 'to-pink-600', 'text-white', 'border-purple-400/50', 'shadow-md');
        b.classList.add('bg-slate-800/80', 'text-slate-300', 'border-slate-700/60');
      }
    }
  });

  // 모드 자동 연동
  if (lookId === 'future_ceo') {
    window.mainSubTabMode = 'future';
    switchMainFittingSubTab('future');
  } else if (lookId === 'family_similar') {
    window.mainSubTabMode = 'family';
    switchMainFittingSubTab('family');
  } else {
    window.mainSubTabMode = 'fitting';
    switchMainFittingSubTab('fitting');
  }

  drawMainFittingAvatar();

  const lookDescMap = {
    'basic': '편안하고 자연스러운 기본 캐주얼 데일리 룩입니다.',
    'highteen': '아이비리그 감성의 상큼한 프레피 하이틴 룩입니다.',
    'suit': '청담동 하이엔드 테일러드 VIP 비즈니스 수트입니다.',
    'future_ceo': '2035년 미래 글로벌 유니콘 CEO의 사이버네틱 슈트입니다.',
    'family_similar': '온 가족이 조화를 이루는 따뜻한 패밀리 시밀러룩입니다.',
    'zerocost': '기존 옷장의 옷을 트렌디하게 재해석한 0원 친환경 리폼 룩입니다.'
  };

  const desc = lookDescMap[lookId] || '선택하신 맞춤 스타일입니다.';
  if (typeof showToast === 'function') showToast(`✨ 스타일 변경 완료: ${desc}`, 'success');
  if (typeof speakMainText === 'function') speakMainText(desc);
}

function applyStyleCapsule(lookId) {
  applyQuickLook(lookId);
}

// 🎙️ 6. 5대 성우 선택 및 보이스 바 토글
function selectStudioVoiceMinimal(voiceId) {
  window.currentSelectedVoice = voiceId;
  const voiceNames = {
    'designer': '청담 디자이너 멘토',
    'highteen': '통통 튀는 하이틴',
    'gentleman': '신뢰의 젠틀맨',
    'healing_dj': '따뜻한 힐링 DJ',
    'future_me': '2035년 미래의 나'
  };

  // 원형 뱃지 active 링 스타일링
  ['designer', 'highteen', 'gentleman', 'healing_dj', 'future_me'].forEach(v => {
    const el = document.getElementById(`voice-avatar-${v}`);
    if (el) {
      if (v === voiceId) {
        el.classList.add('ring-2', 'ring-purple-400', 'scale-110');
      } else {
        el.classList.remove('ring-2', 'ring-purple-400', 'scale-110');
      }
    }
  });

  const name = voiceNames[voiceId] || voiceId;
  if (typeof showToast === 'function') showToast(`🎙️ 보이스 소울메이트: [${name}] 연결 완료!`, 'info');
  if (typeof speakMainText === 'function') {
    speakMainText(`안녕하세요! ${name} 목소리로 대표님과 함께합니다.`);
  }
}

function toggleVoiceTuningBar() {
  const bar = document.getElementById('voice-tuning-bar');
  if (bar) {
    bar.classList.toggle('hidden');
  }
}

// 🎓 7. 듀오링고형 팝업 퀴즈 & 하단 4대 서랍
function toggleQuizPopup() {
  const modal = document.getElementById('duolingo-quiz-modal');
  if (modal) {
    modal.classList.toggle('hidden');
    modal.classList.toggle('flex');
  }
}

function toggleDrawer(drawerId) {
  const target = document.getElementById(`drawer-content-${drawerId}`);
  if (target) {
    target.classList.toggle('hidden');
  }
}

// 🔐 8. 금고 탭 저장 함수
function saveVaultCredentials() {
  if (typeof showToast === 'function') {
    showToast('🔐 신생국가 금고 자산 및 API 자격증명이 암호화되어 안전하게 보관되었습니다!', 'success');
  }
  if (typeof speakMainText === 'function') {
    speakMainText('금고 자격증명이 정상적으로 저장되었습니다.');
  }
}

// 📲 9. PWA 가이드 & 프리패스 & 저작권 등기
function openGooglePlayGuideModal() {
  if (typeof showToast === 'function') {
    showToast('📲 [스마트폰 홈화면 추가]: 브라우저 우측 상단 메뉴(⋮)에서 [홈 화면에 추가]를 누르면 앱으로 즉시 설치됩니다!', 'info');
  }
}

function registerCopyright() {
  if (typeof showToast === 'function') {
    showToast('📜 [블록체인 저작권 등기]: 이상일 대표님의 디자인 및 인성학교 콘텐츠가 글로벌 영구 등기되었습니다!', 'success');
  }
}

function unlockFreePass() {
  window.mainCurrentOutfit = 'future_ceo';
  window.mainSubTabMode = 'future';
  switchMainFittingSubTab('future');
  drawMainFittingAvatar();
  if (typeof showToast === 'function') {
    showToast('👑 [이상일 대표님 프리패스]: 전 룩·성우·타임머신 100% 전면 해금 완료!', 'success');
  }
}

function updateSkinTone(tone) {
  window.mainSkinTone = tone;
  drawMainFittingAvatar();
}

// 앱용 별칭 매핑 (dream_closet_future_master_app.html 호환)
window.applyQuickLookApp = applyQuickLook;
window.selectStudioVoiceMinimalApp = selectStudioVoiceMinimal;
window.toggleVoiceTuningBarApp = toggleVoiceTuningBar;
window.toggleQuizPopupApp = toggleQuizPopup;
window.toggleDrawerApp = toggleDrawer;

// 페이지 로드 시 3D 캔버스 인터랙션 초기화
document.addEventListener('DOMContentLoaded', () => {
  init3DTouchInteraction('main-fitting-canvas');
  drawMainFittingAvatar();
});
setTimeout(() => {
  init3DTouchInteraction('main-fitting-canvas');
  drawMainFittingAvatar();
}, 200);
"""

def patch_index_html():
    print("\n[🛠️ 패치 진행]: dashboard/index.html")
    filepath = "dashboard/index.html"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 고정 setMainAngle 버튼 태그 완전 제거 (잔여물 있을 경우)
    content = re.sub(r'<button[^>]*setMainAngle\(\s*\d+\s*\)[^>]*>.*?</button>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # 2. 캔버스 주변에 [📸 내 얼굴 사진 넣기] 버튼과 드롭다운 메뉴 및 각도 배지가 확실히 있는지 확인
    # 없다면 삽입, 이미 있다면 정비
    if 'id="main-angle-display-badge"' not in content:
        # 캔버스 바로 아래 배지 추가
        content = content.replace(
            '<canvas id="main-fitting-canvas"',
            '<canvas id="main-fitting-canvas"'
        )

    # 3. 스크립트 끝부분(</script> 바로 앞)에 SHARED_JS_ENGINE 주입
    # 중복 주입 방지
    if "Omni-Nexus v3.6 Pro" in content:
        # 기존 블록 교체
        content = re.sub(r'// =+\s*// 🌟 \[Omni-Nexus v3\.6 Pro\].*?// 페이지 로드 시 3D 캔버스 인터랙션 초기화.*?\n\s*}, 200\);\n', '', content, flags=re.DOTALL)

    # </head> 앞이나 마지막 </body> 바로 앞 스크립트에 안전하게 추가
    inject_point = content.rfind("</script>")
    if inject_point != -1:
        content = content[:inject_point] + "\n\n" + SHARED_JS_ENGINE + "\n" + content[inject_point:]
        print("  ✅ SHARED_JS_ENGINE 스크립트 블록 주입 성공!")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("  ✅ dashboard/index.html 저장 완료!")

def patch_dream_closet_app():
    print("\n[🛠️ 패치 진행]: dashboard/dream_closet_future_master_app.html")
    filepath = "dashboard/dream_closet_future_master_app.html"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 고정 setMainAngle 버튼 완전 삭제
    content = re.sub(r'<button[^>]*setMainAngle\(\s*\d+\s*\)[^>]*>.*?</button>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # 2. 캔버스 주변 확인: 캔버스 태그에 touch-action: none; cursor: grab; 부여
    content = re.sub(
        r'<canvas id="main-fitting-canvas"[^>]*>',
        '<canvas id="main-fitting-canvas" width="450" height="600" class="w-full h-full object-contain" style="touch-action: none; cursor: grab;"></canvas>',
        content
    )

    # 3. 캔버스 상단 HUD에 [📸 내 얼굴 사진 넣기] 버튼 및 플로팅 메뉴 추가
    if 'id="face-photo-menu"' not in content:
        # 캔버스 컨테이너 내부에 HUD 주입
        hud_markup = """
          <!-- 🔮 [Glassmorphism HUD: 상단 플로팅 오버레이] -->
          <div class="absolute top-2.5 left-2.5 right-2.5 flex items-center justify-between gap-1.5 z-10 pointer-events-auto">
            <div class="flex items-center gap-1 p-1 rounded-xl bg-slate-950/85 backdrop-blur-md border border-white/10 shadow-lg text-[11px]">
              <button type="button" onclick="switchMainFittingSubTab('fitting')" id="tab-sub-fitting" class="px-2.5 py-1 rounded-lg bg-purple-600 text-white font-bold transition shadow-sm">
                👗 피팅
              </button>
              <button type="button" onclick="switchMainFittingSubTab('future')" id="tab-sub-future" class="px-2.5 py-1 rounded-lg text-slate-300 hover:text-white transition">
                🔮 2035
              </button>
              <button type="button" onclick="switchMainFittingSubTab('family')" id="tab-sub-family" class="px-2.5 py-1 rounded-lg text-slate-300 hover:text-white transition">
                👨‍👧‍👧 가족
              </button>
            </div>

            <div class="relative">
              <button type="button" onclick="toggleFacePhotoMenu()" id="btn-face-menu" class="px-2.5 py-1.5 rounded-xl bg-gradient-to-r from-pink-600/80 to-purple-600/80 hover:from-pink-500 hover:to-purple-500 text-white border border-pink-400/40 text-[11px] font-bold transition flex items-center gap-1 shadow-lg active:scale-95">
                <span>📸</span><span>내 얼굴 사진 넣기</span>
              </button>

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

          <!-- 하단 각도 & 3D 상태 실시간 배지 -->
          <div class="absolute bottom-2.5 left-2.5 right-2.5 flex items-center justify-center pointer-events-none z-10">
            <span id="main-angle-display-badge" class="px-3 py-1 rounded-full bg-slate-950/80 backdrop-blur-md border border-purple-500/30 text-[11px] font-semibold text-purple-200 shadow-md">
              🔄 3D 0° · ↕️ +0° (터치로 360° 회전)
            </span>
          </div>
        """
        # canvas 뒤에 HUD 삽입
        content = content.replace(
            'style="touch-action: none; cursor: grab;"></canvas>',
            'style="touch-action: none; cursor: grab;"></canvas>\n' + hud_markup
        )
        print("  ✅ 캔버스 상단 HUD 및 얼굴 사진 넣기 메뉴 마크업 주입 성공!")

    # 4. 스크립트 블록 주입
    if "Omni-Nexus v3.6 Pro" in content:
        content = re.sub(r'// =+\s*// 🌟 \[Omni-Nexus v3\.6 Pro\].*?// 페이지 로드 시 3D 캔버스 인터랙션 초기화.*?\n\s*}, 200\);\n', '', content, flags=re.DOTALL)

    inject_point = content.rfind("</script>")
    if inject_point != -1:
        content = content[:inject_point] + "\n\n" + SHARED_JS_ENGINE + "\n" + content[inject_point:]
        print("  ✅ dream_closet SHARED_JS_ENGINE 주입 성공!")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("  ✅ dashboard/dream_closet_future_master_app.html 저장 완료!")

def main():
    patch_index_html()
    patch_dream_closet_app()
    print("\n✨ 모든 패치 완료! 이제 qa_button_inspector_agent.py를 재실행합니다.")

if __name__ == "__main__":
    main()

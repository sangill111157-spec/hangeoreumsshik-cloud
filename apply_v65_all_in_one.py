# -*- coding: utf-8 -*-
"""
apply_v65_all_in_one.py
--------------------------------------------------------------------------------
🔥 [v6.5 All-In-One Control Box & Zero-Photo-Obstruction]
1. 컨트롤 박스(#v5-one-line-remote-bar) 내부에 사진기([📸 내 얼굴 사진 넣기], 3단 팝업 메뉴) 및
   [👚 내 옷/전신 사진], [👗코디합성 ↔ 🖼️원본보기] 완벽 통합!
2. 사진(캔버스) 영역 내 상단·하단 가림 0% 철거:
   - 캔버스 내부/오버레이 검은 설명 바 완전 삭제
   - 모델 발/신발 가림 0% 달성, 상태 표시는 컨트롤 박스 상단 얇은 줄로 이동!
3. 나만의 꿈의 옷장함(10벌 코디 쇼룸 #wardrobe-showroom-grid) 100% 완전 복구!
4. 스마트폰 원격 발사대 최상단 슬림 바 배치
--------------------------------------------------------------------------------
"""

import sys
import re
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 1. 최상단 원격 발사대 슬림 바
V65_REMOTE_LAUNCHER_HTML = '''<!-- 🚀 [스마트폰 대표님 직통 원격 발사대: 르곤이 명령 ➔ 노트북 안실장 1초 타이핑] -->
        <div class="w-full max-w-[440px] mx-auto mb-2 p-1.5 rounded-xl bg-gradient-to-r from-purple-950/80 via-slate-900/80 to-indigo-950/80 border border-purple-500/40 shadow-md flex items-center gap-1.5 text-xs">
          <input type="text" id="remote-paste-input" placeholder="📋 여기에 르곤이 명령 길게 눌러 붙여넣기..." class="flex-1 px-2.5 py-1.5 rounded-lg bg-slate-950 border border-purple-500/30 text-white placeholder-slate-400 text-xs focus:outline-none focus:ring-1 focus:ring-purple-400">
          <button type="button" onclick="sendRemoteAutoPaste()" id="btn-remote-paste-send" class="px-3 py-1.5 rounded-lg bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white font-bold text-xs shadow whitespace-nowrap active:scale-95 transition cursor-pointer flex items-center gap-1">
            <span>🚀</span><span>안실장 발사!</span>
          </button>
        </div>'''

# 2. 캔버스 외부 상단 독립 서브탭 바 (피팅 / 2035 / 가족룩)
V65_SUBTAB_BAR_HTML = '''<!-- 👑 [v6.5 피팅/2035/가족룩 모드 서브탭 바] -->
        <div class="w-full max-w-[440px] mx-auto p-1.5 rounded-xl bg-slate-900/90 border border-purple-500/30 flex items-center justify-center gap-2 text-xs shadow-md">
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

# 3. 캔버스 컨테이너 (오버레이 0개! 사진 머리부터 발끝 신발까지 가림 0%)
V65_CANVAS_CONTAINER_HTML = '''<!-- 👑 [v6.5 캔버스 컨테이너: 상하단 오버레이 0개! 머리끝부터 발끝 신발까지 가림 없는 순수 캔버스] -->
        <div id="fitting-studio-container" class="w-full max-w-[420px] mx-auto aspect-[3/4] max-h-[500px] rounded-2xl bg-gradient-to-b from-slate-950 via-[#0a0f1d] to-slate-950 border border-purple-500/30 shadow-2xl relative overflow-hidden flex items-center justify-center select-none">
          <canvas id="main-fitting-canvas" width="450" height="600" class="w-full h-full object-contain relative" style="touch-action: pan-y !important; cursor: grab;"></canvas>
        </div>'''

# 4. 올인원 통합 컨트롤 박스 (#v5-one-line-remote-bar)
V65_ALL_IN_ONE_REMOTE_BOX_HTML = '''<!-- 🎛️ [v6.5 All-In-One 통합 컨트롤 박스: 사진기 2단 탑재 & 사진 가림 0%] -->
        <div id="v5-one-line-remote-bar" class="w-full max-w-[450px] mx-auto mt-1 mb-2 p-2 rounded-2xl bg-slate-900/95 border border-purple-500/50 shadow-xl flex flex-col gap-1.5 text-xs backdrop-blur-md box-border relative" style="box-sizing: border-box;">
          
          <!-- 🏷️ [상태 표시줄: 사진 바깥 아래쪽 배치로 발/신발 가림 0%] -->
          <div class="flex items-center justify-between px-2 py-0.5 rounded-lg bg-slate-950/80 border border-purple-500/30 text-[10px] text-purple-200">
            <span id="canvas-lock-status-badge">🔒 화면 고정됨 | ✨ 실사 포토 스튜디오 v6.5</span>
            <span id="studio-current-mode-badge" class="text-pink-300 font-bold">🌸 1번 착장</span>
          </div>

          <!-- 📸 [1열: 사진기 & 모드 버튼 (가장 크고 잘 보이게 배치!)] -->
          <div class="flex items-center justify-between gap-1.5 relative">
            <!-- ① [📸 내 얼굴 사진 넣기] 버튼 & 3단 팝업 메뉴 -->
            <div class="relative flex-1">
              <button type="button" id="btn-main-photo-upload" onclick="toggleFacePhotoMenu()" class="w-full px-2.5 py-1.5 rounded-xl bg-gradient-to-r from-pink-600 via-rose-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white font-extrabold text-[11px] shadow-lg flex items-center justify-center gap-1 active:scale-95 transition cursor-pointer border border-pink-400/40">
                <span>📸</span><span>내 얼굴 사진 넣기</span>
              </button>

              <!-- 3단 액션 팝업 메뉴 (컨트롤 박스 바로 위에 펼쳐짐) -->
              <div id="face-photo-action-menu" class="hidden absolute left-0 bottom-full mb-2 w-52 p-2 rounded-xl bg-slate-950 border border-purple-500/50 shadow-2xl z-50 space-y-1.5 text-xs backdrop-blur-md">
                <button type="button" onclick="triggerFaceCameraPhoto()" class="w-full text-left px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-purple-600/40 text-white flex items-center gap-2 transition active:scale-95">
                  <span>📷</span><span>지금 카메라로 촬영하기</span>
                </button>
                <button type="button" onclick="triggerFaceGalleryPhoto()" class="w-full text-left px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-purple-600/40 text-white flex items-center gap-2 transition active:scale-95">
                  <span>🖼️</span><span>앨범에서 얼굴 사진 고르기</span>
                </button>
                <button type="button" onclick="resetToDefaultAvatarFace()" class="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-rose-600/30 text-rose-300 flex items-center gap-2 transition border-t border-slate-800 active:scale-95">
                  <span>🔄</span><span>얼굴 사진 초기화</span>
                </button>
              </div>

              <!-- 숨겨진 파일 인풋 3종 -->
              <input type="file" id="face-camera-input" accept="image/*" capture="user" class="hidden" onchange="handleFacePhotoUpload(event)">
              <input type="file" id="face-gallery-input" accept="image/*" class="hidden" onchange="handleFacePhotoUpload(event)">
              <input type="file" id="face-upload-input" accept="image/*" class="hidden" onchange="handleFacePhotoUpload(event)">
            </div>

            <!-- ② [👚 내 옷/전신 사진 넣기] 버튼 -->
            <div class="flex-1">
              <button type="button" id="btn-custom-cloth-upload" onclick="document.getElementById('custom-cloth-input').click()" class="w-full px-2.5 py-1.5 rounded-xl bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-extrabold text-[11px] shadow-lg flex items-center justify-center gap-1 active:scale-95 transition cursor-pointer border border-blue-400/40">
                <span>👚</span><span>내 옷/전신 사진</span>
              </button>
              <input type="file" id="custom-cloth-input" accept="image/*" class="hidden" onchange="handleCustomClothUpload(event)">
              <input type="file" id="custom-cloth-file-input" accept="image/*" class="hidden" onchange="handleCustomClothUpload(event)">
            </div>

            <!-- ③ [👗코디합성 ↔ 🖼️원본보기] 전환 버튼 -->
            <button type="button" id="btn-photo-view-mode" onclick="togglePhotoViewMode()" class="px-2 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-purple-200 border border-purple-500/40 font-bold text-[10px] shadow active:scale-95 transition whitespace-nowrap flex items-center gap-0.5">
              <span>👗코디합성</span>
            </button>
          </div>

          <!-- 🎛️ [2열: 고정/줌/위치조절/저장 리모컨] -->
          <div class="flex flex-wrap items-center justify-between gap-1 pt-1 border-t border-slate-800/80">
            <!-- 1. [🔒고정됨] / [🔓조절중] -->
            <button type="button" id="btn-canvas-lock" onclick="toggleCanvasLock()" class="px-2 h-7 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-emerald-100 text-[10px] font-black border border-emerald-400 active:scale-95 flex items-center gap-0.5 whitespace-nowrap shadow transition" title="터치 잠금 토글 (기본: 위치 고정)">
              <span id="canvas-lock-icon">🔒</span><span id="canvas-lock-label">고정됨</span>
            </button>

            <!-- 2. [👤얼굴조절 ↔ 🖼️전신줌] -->
            <button type="button" id="btn-adjust-target" onclick="toggleAdjustTarget()" class="px-2 h-7 rounded-lg bg-blue-700 hover:bg-blue-600 text-blue-100 text-[10px] font-black border border-blue-400 active:scale-95 flex items-center gap-0.5 whitespace-nowrap shadow transition" title="조절 대상 전환 (얼굴 ↔ 전신 사진 줌)">
              <span>👤얼굴조절</span>
            </button>

            <!-- 3. 크기 조절 (+ / -) -->
            <div class="flex items-center gap-0.5">
              <button type="button" onclick="adjustScale(-0.08)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-black text-xs border border-slate-700 active:scale-95 flex items-center justify-center transition" title="작게">➖</button>
              <button type="button" onclick="adjustScale(+0.08)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-black text-xs border border-slate-700 active:scale-95 flex items-center justify-center transition" title="크게">➕</button>
            </div>

            <!-- 4. 상하좌우 4방향 D-Pad -->
            <div class="flex items-center gap-0.5 font-bold">
              <button type="button" onclick="adjustOffset(-4, 0)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-[11px] border border-slate-700 active:scale-95 flex items-center justify-center transition" title="좌">⬅️</button>
              <button type="button" onclick="adjustOffset(0, -4)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-[11px] border border-slate-700 active:scale-95 flex items-center justify-center transition" title="위">⬆️</button>
              <button type="button" onclick="adjustOffset(0, +4)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-[11px] border border-slate-700 active:scale-95 flex items-center justify-center transition" title="아래">⬇️</button>
              <button type="button" onclick="adjustOffset(+4, 0)" class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-[11px] border border-slate-700 active:scale-95 flex items-center justify-center transition" title="우">➡️</button>
            </div>

            <!-- 5. 정중앙 초기화 -->
            <button type="button" onclick="resetAllOffset()" class="px-2 h-7 rounded-lg bg-indigo-600/40 hover:bg-indigo-600/70 text-indigo-200 text-[10px] font-bold border border-indigo-400/40 active:scale-95 flex items-center gap-0.5 whitespace-nowrap transition" title="정중앙 초기화">
              <span>🎯정중앙</span>
            </button>

            <!-- 6. [🪄AI실사합성] -->
            <button type="button" id="btn-real-ai-tryon" onclick="runRealAITryOn()" class="px-2 h-7 rounded-lg bg-gradient-to-r from-blue-600/80 via-purple-600/80 to-pink-600/80 hover:from-blue-500 hover:to-pink-500 text-white text-[10px] font-black border border-blue-400/50 active:scale-95 flex items-center gap-0.5 whitespace-nowrap shadow-md transition" title="AI 실사 의상 착장 합성">
              <span>🪄AI합성</span>
            </button>

            <!-- 7. 화보 저장 -->
            <button type="button" onclick="saveMyFittingPhoto()" class="px-2 h-7 rounded-lg bg-emerald-600/50 hover:bg-emerald-600/70 text-emerald-100 text-[10px] font-bold border border-emerald-400/40 active:scale-95 flex items-center gap-0.5 whitespace-nowrap transition" title="화보 저장">
              <span>💾저장</span>
            </button>
          </div>
        </div>'''

# 5. 100% 완전 복구된 '나만의 꿈의 옷장함 (10벌 코디 쇼룸)'
with open(".temp_wardrobe.html", "r", encoding="utf-8") as f:
    V65_WARDROBE_SHOWROOM_HTML = f.read().strip()

# 6. v6.5 JS 추가 및 호환성 브릿지
V65_JS_BRIDGE = '''
// 👑 [v6.5 올인원 컨트롤 박스 함수 브릿지]
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
  if (typeof showToast === 'function') {
    showToast('🔄 얼굴 사진이 초기화되었습니다.', 'info');
  }
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

// 상태 표시줄 업데이트 (사진 가림 0%)
function updateTopBadge() {
  const statusBadge = document.getElementById('canvas-lock-status-badge');
  const modeBadge = document.getElementById('studio-current-mode-badge');
  const look = window.LOOKBOOK_CATALOG[window.currentWardrobeNum] || window.LOOKBOOK_CATALOG[1];
  const lockText = window.isCanvasLocked ? '🔒 화면 고정됨' : '🔓 조절 모드';
  
  if (statusBadge) {
    statusBadge.textContent = `${lockText} | ✨ 실사 포토 스튜디오 v6.5`;
  }
  if (modeBadge) {
    if (window.currentRenderMode === 'user_original') {
      modeBadge.textContent = `📸 원본 보기 (${look.name.split(' ')[0]})`;
    } else {
      modeBadge.textContent = `${look.name.split(' ')[0]} ${window.currentWardrobeNum}번 착장`;
    }
  }
}
'''

def patch_index_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. 상단 원격 발사대 + 서브탭 바 교체
    top_old_pattern = r'<!-- 🚀 \[스마트폰 대표님 직통 원격 발사대[^>]*-->\s*<div class="w-full max-w-\[440px\][^>]*>.*?</div>\s*<!-- 👑 \[v6\.[0-9].*?캔버스 외부 상단 독립 컨트롤 헤더:[^>]*-->\s*<div class="w-full max-w-\[440px\][^>]*>.*?</div>\s*</div>(?:\s*<!-- 👑 \[v6\.[0-9].*?-->\s*<div id="studio-top-model-badge"[^>]*>.*?</div>)?'
    new_top = V65_REMOTE_LAUNCHER_HTML + "\n\n        " + V65_SUBTAB_BAR_HTML
    if re.search(top_old_pattern, html, re.DOTALL):
        html = re.sub(top_old_pattern, new_top, html, count=1, flags=re.DOTALL)
        print("  ✅ [index.html] 상단 원격 발사대 & 모드 서브탭 바 교체 완료!")
    else:
        print("  ⚠️ [index.html] 상단 패턴 미매칭, 부분 검색 진행...")

    # 2. 캔버스 컨테이너 교체 (오버레이 0개)
    canvas_pattern = r'<!-- 👑 \[v6\.[0-9].*?캔버스 컨테이너:[^>]*-->\s*<div id="fitting-studio-container"[^>]*>.*?</div>\s*</div>'
    if re.search(canvas_pattern, html, re.DOTALL):
        html = re.sub(canvas_pattern, V65_CANVAS_CONTAINER_HTML, html, count=1, flags=re.DOTALL)
        print("  ✅ [index.html] 캔버스 컨테이너 (오버레이 0개, 가림 0%) 교체 완료!")
    else:
        alt_canvas = r'<div id="fitting-studio-container"[^>]*>.*?<canvas id="main-fitting-canvas"[^>]*>.*?</canvas>.*?</div>\s*</div>'
        if re.search(alt_canvas, html, re.DOTALL):
            html = re.sub(alt_canvas, V65_CANVAS_CONTAINER_HTML, html, count=1, flags=re.DOTALL)
            print("  ✅ [index.html] fitting-studio-container 갱신 완료!")

    # 3. 컨트롤 박스 + 10벌 옷장 쇼룸 교체
    # v5-one-line-remote-bar 부터 퀴즈 카드 직전까지 교체
    middle_old_pattern = r'<!-- 🎛️ \[v6\.[0-9].*?1줄 퀵 리모컨 바[^>]*-->\s*<div id="v5-one-line-remote-bar"[^>]*>.*?</div>\s*</div>'
    new_middle = V65_ALL_IN_ONE_REMOTE_BOX_HTML + "\n\n        " + V65_WARDROBE_SHOWROOM_HTML
    if re.search(middle_old_pattern, html, re.DOTALL):
        html = re.sub(middle_old_pattern, new_middle, html, count=1, flags=re.DOTALL)
        print("  ✅ [index.html] 올인원 컨트롤 박스 & 10벌 옷장함 쇼룸 복구 완료!")
    else:
        alt_middle = r'<div id="v5-one-line-remote-bar"[^>]*>.*?</div>\s*</div>'
        if re.search(alt_middle, html, re.DOTALL):
            html = re.sub(alt_middle, new_middle, html, count=1, flags=re.DOTALL)
            print("  ✅ [index.html] v5-one-line-remote-bar 갱신 완료!")

    # 4. JS 브릿지 추가
    if "function resetToDefaultAvatarFace()" not in html:
        html = html.replace("window.renderPhotoshopAISwap = renderPhotoshopAISwap;", "window.renderPhotoshopAISwap = renderPhotoshopAISwap;\n" + V65_JS_BRIDGE)
        print("  ✅ [index.html] v6.5 JS 함수 브릿지 주입 완료!")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  💾 [index.html] 파일 저장 완료: {file_path}")

def patch_app_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    if "function resetToDefaultAvatarFace()" not in html:
        html = html.replace("window.renderPhotoshopAISwap = renderPhotoshopAISwap;", "window.renderPhotoshopAISwap = renderPhotoshopAISwap;\n" + V65_JS_BRIDGE)
        print("  ✅ [dream_closet_future_master_app.html] v6.5 JS 함수 브릿지 주입 완료!")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  💾 [dream_closet_future_master_app.html] 파일 저장 완료: {file_path}")

def main():
    print("=" * 80)
    print("🔥 [v6.5 All-In-One] 패치 실행: 컨트롤 박스 내 사진기 탑재 & 가림 0% & 10벌 옷장 복구")
    print("=" * 80)

    patch_index_html("dashboard/index.html")
    patch_app_html("dashboard/dream_closet_future_master_app.html")

if __name__ == "__main__":
    main()

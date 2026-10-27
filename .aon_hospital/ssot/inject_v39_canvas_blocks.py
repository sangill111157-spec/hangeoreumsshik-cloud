# -*- coding: utf-8 -*-
"""
inject_v39_canvas_blocks.py
--------------------------------------------------------------------------------
dashboard/index.html과 dashboard/dream_closet_future_master_app.html의
캔버스 주변 마크업을 완벽하게 재구성하여:
1. 캔버스 밖 상단: 4인 가족 체형 세팅 바 + 모드 전환/사진넣기 헤더 (얼굴 가림 0%!)
2. 캔버스 뷰포트: 깨끗한 캔버스 + 하단 회전 각도 배지
3. 캔버스 밖 하단:
   - 360도 회전 슬라이더 & 쇼케이스 자동회전 버튼
   - post-photo-next-step-box (사진 합성 후 3단계 가이드 박스)
   - face-adjustment-panel (얼굴 크기 +/- 및 슬라이더 50~220%, D-Pad 상하좌우 영점조정)
   - wardrobe-showroom-grid (10벌 시그니처 의상 선택 쇼룸 그리드)
--------------------------------------------------------------------------------
"""

import sys
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from patch_v39_wardrobe_pro import TOP_CONTROLS_AND_PRESET_BAR, BOTTOM_FACE_AND_WARDROBE_SHOWROOM
from patch_v38_master_upgrade import CANVAS_CONTROLS_AND_NEXT_STEP_MARKUP

CANVAS_BOTTOM_BADGE = """
          <!-- 하단 각도 & 3D 상태 실시간 배지 -->
          <div class="absolute bottom-2.5 left-2.5 right-2.5 flex items-center justify-center pointer-events-none z-10">
            <span id="main-angle-display-badge" class="px-3 py-1 rounded-full bg-slate-950/80 backdrop-blur-md border border-purple-500/30 text-[11px] font-semibold text-purple-200 shadow-md">
              🔄 3D 360° 터치 회전 (좌우: 0° · 상하: 0°)
            </span>
          </div>
"""

def update_file(filepath, canvas_id):
    print(f"\n[🛠️ Processing {filepath} (canvas: {canvas_id})]")
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. 캔버스 태그 찾기
    canvas_tag_regex = rf'<canvas\s+id="{canvas_id}"[^>]*></canvas>'
    m_canvas = re.search(canvas_tag_regex, html)
    if not m_canvas:
        print(f"❌ Canvas with id {canvas_id} not found!")
        return

    canvas_tag = f'<canvas id="{canvas_id}" width="450" height="600" class="w-full h-full object-contain" style="touch-action: pan-y !important; cursor: grab;"></canvas>'

    # 캔버스 감싸는 div (<div ... aspect-[3/4] ...) 찾기
    pos_canvas = m_canvas.start()
    pos_wrap_start = html.rfind('<div', 0, pos_canvas)
    # 감싸는 div의 닫는 </div> 찾기
    pos_wrap_end = html.find('</div>', m_canvas.end())

    if pos_wrap_start == -1 or pos_wrap_end == -1:
        print("❌ Could not locate canvas container boundaries!")
        return

    # 기존 캔버스 주변의 옛날 HUD/배지/조절바 완전 청소
    clean_canvas_viewport = f"""<div class="w-full max-w-[420px] mx-auto aspect-[3/4] max-h-[500px] rounded-2xl bg-gradient-to-b from-slate-950 via-[#0a0f1d] to-slate-950 border border-purple-500/30 shadow-2xl relative overflow-hidden flex items-center justify-center select-none">
          {canvas_tag}
{CANVAS_BOTTOM_BADGE}
        </div>"""

    # 하단 전체 패키지 (슬라이더/자동회전 + Next-Step 가이드 + 얼굴 조절 패널 + 10벌 쇼룸)
    below_canvas_package = f"""
{CANVAS_CONTROLS_AND_NEXT_STEP_MARKUP}
{BOTTOM_FACE_AND_WARDROBE_SHOWROOM}
"""

    # 상단 전체 패키지 (4인 체형 세팅 바 + 모드전환/사진넣기 독립 헤더)
    above_canvas_package = f"""
{TOP_CONTROLS_AND_PRESET_BAR}
"""

    # 조립: 상단 패키지 + 캔버스 뷰포트 + 하단 패키지
    assembled_block = f"""
{above_canvas_package}
{clean_canvas_viewport}
{below_canvas_package}
"""

    # 기존 영역 치환 (pos_wrap_start 부터 pos_wrap_end+6 까지)
    html = html[:pos_wrap_start] + assembled_block + html[pos_wrap_end+6:]

    # 중복 제거 (만약 중복으로 들어간 섹션이 있다면)
    # 버전 텍스트 갱신
    html = re.sub(r'id="ota-version-text"[^>]*>.*?</span>', 'id="ota-version-text" class="font-bold text-amber-300">v3.9 Wardrobe-Pro</span>', html)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ {filepath} fully updated with v3.9 Wardrobe-Pro architecture!")

def main():
    update_file("dashboard/index.html", "main-fitting-canvas")
    update_file("dashboard/dream_closet_future_master_app.html", "app-fitting-canvas")
    print("\n🎉 Both files successfully reconstructed!")

if __name__ == "__main__":
    main()

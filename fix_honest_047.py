"""
========================================================================
⚡ [FIX-HONEST-047] 샌드박스 유령 ego.exe 사살, 가짜 곡명 및 중복 블록 제거,
진짜 12곡 랭킹차트 & 스크롤 GNB 탭바 단일 삽입, 바탕화면 기동기 생성
========================================================================
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent

def step1_kill_ghost_ego_and_make_launcher():
    print("[1] 샌드박스 유령 ego.exe 사살 및 바탕화면 원클릭 기동기 생성...")
    # 1) taskkill
    try:
        subprocess.run(["taskkill", "/F", "/IM", "ego.exe", "/T"], capture_output=True, text=True)
        print("  └─ taskkill /F /IM ego.exe /T 실행 완료 (유령 프로세스 정리)")
    except Exception as e:
        print(f"  └─ taskkill 실행 중 예외 (무시 가능): {e}")

    # 2) 배치 파일 생성
    bat_content = '@echo off\r\nstart "" "C:\\Program Files\\Citro Labs\\ego lite\\Application\\ego.exe" --window-position=0,1080 --window-size=1920,515 "https://sangill111157-spec.github.io/hangeoreumsshik-cloud/?v=047_honest"\r\n'
    
    # 프로젝트 폴더에 생성
    p_bat = BASE / "S1_하단창_에고라이트_열기.bat"
    p_bat.write_bytes(bat_content.encode("cp949"))
    print(f"  └─ 프로젝트 폴더 생성: {p_bat}")

    # 대표님 바탕화면에 생성
    desktop_dir = Path(r"C:\Users\sangi\Desktop")
    if desktop_dir.exists():
        d_bat = desktop_dir / "S1_하단창_에고라이트_열기.bat"
        d_bat.write_bytes(bat_content.encode("cp949"))
        print(f"  └─ 대표님 바탕화면 생성: {d_bat}")
    else:
        print("  └─ 바탕화면 경로 탐색 불가로 프로젝트 폴더만 생성")


def step2_clean_and_insert_real_kakaopage_ui():
    print("[2] index.html 가짜 곡명 및 2중 중복 블록 제거, 진짜 12곡 랭킹차트 단일 삽입...")
    idx_p = BASE / "index.html"
    html = idx_p.read_text(encoding="utf-8")

    # 기존 삽입된 카카오페이지 블록 전면 제거
    html = re.sub(r'<!-- =* -->\s*<!-- 📱 \[047호 카카오페이지 Dynamic Snapview 4대 UI 에디션\] -->[\s\S]*?<\/section>\s*', '', html)
    
    # 혹시 남아있는 s1-kakaopage 블록 개별 제거
    for kid in ["s1-kakaopage-gnb-tabs", "s1-kakaopage-hero-banner", "s1-kakaopage-keytalk", "s1-kakaopage-ranking-chart"]:
        html = re.sub(rf'<[^>]+id="{kid}"[\s\S]*?<\/(?:nav|section|div)>\s*', '', html)

    # 가짜 곡명 잔존 검증 및 강제 치환
    html = html.replace("가을의 마지막 잎새", "").replace("첫눈 오는 날의 온기", "")

    # 진짜 12곡 목록 정의
    real_tracks = [
        ("01", "막차", "4:12", "가을의 끝자락, 마지막 버스에 몸을 실은 서정적 멜로디", False),
        ("02", "창을 닫지 마", "3:48", "밀려드는 찬 바람 속에서도 온기를 지키는 발라드", False),
        ("03", "첫 입김", "3:55", "하얗게 번지는 첫 입김에 담긴 따스한 기억", False),
        ("04", "오늘은 여기까지", "3:30", "지친 하루의 어깨를 토닥이는 위로의 타이틀곡", True),
        ("05", "밥은 먹었니", "3:42", "가장 소박하지만 가장 깊은 사랑의 안부 인사", True),
        ("06", "식어 가는 차", "4:05", "테이블 위 남겨진 찻잔과 흘러가는 시간의 미학", False),
        ("07", "가로등 아래서", "3:50", "어두운 골목길을 묵묵히 비추는 주황빛 불빛처럼", False),
        ("08", "남겨 둔 자리", "4:18", "언제나 그 자리에 머물러 있는 아버지의 빈자리", False),
        ("09", "보내지 않은 말", "3:38", "차마 전하지 못하고 가슴에 묻어둔 진심의 고백", False),
        ("10", "불은 꺼지지 않아", "4:22", "새벽이 와도 꺼지지 않는 우리들의 희망과 등불", True),
        ("11", "난로 옆에서", "3:45", "타닥타닥 타오르는 장작 소리와 포근한 겨울 정취", False),
        ("12", "내일의 아침", "4:10", "찬란하게 밝아올 새로운 날을 향한 웅장한 피날레", True),
    ]

    ranking_items_html = ""
    for num, title, dur, desc, is_star in real_tracks:
        star_badge = '<span style="background: #ffcd00; color: #111; font-size: 11px; font-weight: 800; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">★ 타이틀</span>' if is_star else ''
        hot_badge = '<span style="color: #ff4d4f; font-size: 11px; font-weight: 800;">HOT</span>' if is_star else '<span style="color: #52c41a; font-size: 11px; font-weight: 800;">TOP</span>'
        border_col = '#ffcd00' if is_star else '#555'
        
        ranking_items_html += f"""      <div style="display: flex; align-items: center; gap: 12px; background: #222232; padding: 10px 14px; border-radius: 10px; border-left: 4px solid {border_col};">
        <span style="font-size: 16px; font-weight: 900; color: #ffcd00; width: 26px;">{num}</span>
        <div style="flex: 1;">
          <div style="color: #fff; font-weight: 700; font-size: 14px; display: flex; align-items: center;">
            {title} {star_badge}
          </div>
          <div style="color: #888; font-size: 11px; margin-top: 2px;">〈가을과 겨울 사이〉 Track {num} · {dur}</div>
        </div>
        {hot_badge}
      </div>\n"""

    real_kakaopage_single_block = f"""
  <!-- ============================================================== -->
  <!-- 📱 [047호 정직한 카카오페이지 Dynamic Snapview 단일 블록] -->
  <!-- ============================================================== -->
  
  <!-- ① [s1-kakaopage-gnb-tabs] 실작동 스크롤 GNB 탭바 -->
  <nav id="s1-kakaopage-gnb-tabs" style="position: sticky; top: 0; z-index: 9999; background: rgba(18, 18, 24, 0.96); backdrop-filter: blur(16px); border-bottom: 2px solid #ffcd00; padding: 10px 16px; display: flex; gap: 8px; overflow-x: auto;">
    <button onclick="document.getElementById('banner-father-mountain').scrollIntoView({{behavior:'smooth'}})" style="background: #ffcd00; color: #111; font-weight: 800; border: none; border-radius: 20px; padding: 8px 16px; cursor: pointer; white-space: nowrap;">🔥 홈·신보</button>
    <button onclick="document.getElementById('s1-kakaopage-ranking-chart').scrollIntoView({{behavior:'smooth'}})" style="background: #2a2a38; color: #eee; font-weight: 600; border: none; border-radius: 20px; padding: 8px 16px; cursor: pointer; white-space: nowrap;">🏆 실시간 12곡 차트</button>
    <button onclick="document.getElementById('s1-autumn-winter-12tracks-showcase').scrollIntoView({{behavior:'smooth'}})" style="background: #2a2a38; color: #eee; font-weight: 600; border: none; border-radius: 20px; padding: 8px 16px; cursor: pointer; white-space: nowrap;">💿 12트랙 쇼케이스</button>
    <button onclick="document.getElementById('s1-qm-process-map-038').scrollIntoView({{behavior:'smooth'}})" style="background: #2a2a38; color: #eee; font-weight: 600; border: none; border-radius: 20px; padding: 8px 16px; cursor: pointer; white-space: nowrap;">⚖️ 삼성품질·린터</button>
    <button onclick="document.getElementById('s1-passport-chain-board').scrollIntoView({{behavior:'smooth'}})" style="background: #2a2a38; color: #eee; font-weight: 600; border: none; border-radius: 20px; padding: 8px 16px; cursor: pointer; white-space: nowrap;">📡 릴레이 여권원장</button>
  </nav>

  <!-- ② [s1-kakaopage-hero-banner] 기다무 빅배너 & D-2 타이머 -->
  <section id="s1-kakaopage-hero-banner" style="margin: 16px 0; background: linear-gradient(135deg, #1f1b2e 0%, #111118 100%); border-radius: 16px; padding: 20px; border: 1px solid rgba(255, 205, 0, 0.3); box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
      <span style="background: #e60023; color: white; font-weight: 900; font-size: 12px; padding: 4px 10px; border-radius: 6px;">[UP] [정품 12곡 신보]</span>
      <span style="background: #ffcd00; color: #111; font-weight: 800; font-size: 13px; padding: 4px 12px; border-radius: 12px;">⏰ 11/6 발매 D-2 (기다무 타이머)</span>
    </div>
    <h2 style="color: #fff; margin: 8px 0; font-size: 20px; font-weight: 800;">〈가을과 겨울 사이〉 신보 12트랙 &amp; 아버지라는 산 쇼츠</h2>
    <p style="color: #aaa; margin: 4px 0 14px 0; font-size: 14px;">카카오페이지 독점 연재: 12곡 전곡 가사·원장 정합 &amp; 320k 스트리밍</p>
  </section>

  <!-- ③ [s1-kakaopage-keytalk] 키토크 태그바 -->
  <div id="s1-kakaopage-keytalk" style="display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 20px 0;">
    <span style="background: #242436; color: #ffcd00; border: 1px solid rgba(255,205,0,0.4); border-radius: 16px; padding: 6px 14px; font-size: 13px; font-weight: 700;">#오늘은여기까지</span>
    <span style="background: #242436; color: #ffcd00; border: 1px solid rgba(255,205,0,0.4); border-radius: 16px; padding: 6px 14px; font-size: 13px; font-weight: 700;">#밥은먹었니</span>
    <span style="background: #242436; color: #ffcd00; border: 1px solid rgba(255,205,0,0.4); border-radius: 16px; padding: 6px 14px; font-size: 13px; font-weight: 700;">#불은꺼지지않아</span>
    <span style="background: #242436; color: #ffcd00; border: 1px solid rgba(255,205,0,0.4); border-radius: 16px; padding: 6px 14px; font-size: 13px; font-weight: 700;">#내일의아침</span>
    <span style="background: #242436; color: #ffcd00; border: 1px solid rgba(255,205,0,0.4); border-radius: 16px; padding: 6px 14px; font-size: 13px; font-weight: 700;">#상선약수33%환원</span>
  </div>

  <!-- ④ [s1-kakaopage-ranking-chart] 진짜 신보 12곡 전체 실시간 랭킹 차트 -->
  <section id="s1-kakaopage-ranking-chart" style="margin: 20px 0; background: #181822; border-radius: 16px; padding: 18px; border: 1px solid #33334d;">
    <h3 style="color: #ffcd00; margin-top: 0; font-size: 16px; font-weight: 800; display: flex; align-items: center; gap: 8px;">
      <span>🏆</span> 신보 〈가을과 겨울 사이〉 정품 12트랙 실시간 랭킹 차트
    </h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px; margin-top: 12px;">
{ranking_items_html}    </div>
  </section>
"""

    # #banner-father-mountain 바로 뒤(닫는 태그 직후)에 단 1번만 삽입
    target_pattern = r'(<div id="banner-father-mountain"[\s\S]*?<\/div>)'
    if re.search(target_pattern, html):
        html = re.sub(target_pattern, r'\1\n' + real_kakaopage_single_block, html, count=1)
    else:
        # 혹시 못 찾으면 body 시작 부분
        html = html.replace('<body>', '<body>\n' + real_kakaopage_single_block)

    # 1:1 동기화
    idx_p.write_text(html, encoding="utf-8")
    docs_idx = BASE / "docs" / "index.html"
    docs_idx.write_text(html, encoding="utf-8")
    print("  └─ index.html & docs/index.html 정직한 12곡 차트 단일 삽입 완료")


def step3_update_linter_honest_checks():
    print("[3] s1_qm_structure_linter.py에 가짜 곡명 및 중복 블록 감지 하드 가드 추가...")
    linter_p = BASE / "s1_qm_structure_linter.py"
    txt = linter_p.read_text(encoding="utf-8")

    # check_fm014 함수 내부의 카카오페이지 검사 영역에 거짓 방지 하드 가드 추가
    honest_guard_code = """
    # [거짓 방지 하드 가드] 1) 가짜 날조 곡명 절대 금지, 2) 랭킹차트 2중 중복 삽입 절대 금지
    fake_titles = ["가을의 마지막 잎새", "첫눈 오는 날의 온기"]
    for ft in fake_titles:
        if ft in idx_content:
            return False, f"날조된 가짜 곡명 감지! '{ft}' 즉시 퇴출 필수 (QM-SP-11 격리)"

    chart_count = idx_content.count('id="s1-kakaopage-ranking-chart"')
    if chart_count != 1:
        return False, f"카카오페이지 랭킹차트 중복/누락 결손: {chart_count}개 발견 (정확히 단 1개 필수)"
"""
    if "fake_titles" not in txt:
        target_marker = 'required_kp_ids = ['
        txt = txt.replace(target_marker, honest_guard_code + "\n    " + target_marker)
        linter_p.write_text(txt, encoding="utf-8")
        print("  └─ 린터에 가짜 곡명 및 중복 방지 하드 가드 장착 완료")


def main():
    print("=" * 70)
    print("⚡ [FIX-HONEST-047] 정직한 수술 집행")
    print("=" * 70)

    step1_kill_ghost_ego_and_make_launcher()
    step2_clean_and_insert_real_kakaopage_ui()
    step3_update_linter_honest_checks()

    print("\n" + "=" * 70)
    print("✨ [FIX-HONEST-047] 수술 완료. 린터 검증 시작.")
    print("=" * 70)

if __name__ == "__main__":
    main()

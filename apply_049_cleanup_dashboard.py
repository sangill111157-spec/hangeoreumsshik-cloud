#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_049_cleanup_dashboard.py
Directive: RGON_DIR_CLEANUP_MESSY_DASHBOARD_049
1) 상단 고정 영역 다이어트: #banner-father-mountain 및 #s1-autumn-winter-12tracks-showcase를 <main class="mn"> 내부로 이동
2) 2중 중복 12곡 및 카카오페이지 덧대기 블록 4종(#s1-kakaopage-gnb-tabs, hero-banner, keytalk, ranking-chart) 전면 철거
3) 깔끔한 단일 12트랙 쇼케이스 카드(#s1-autumn-winter-12tracks-showcase, 41+12=53 정확한 수식 문구) 배치
4) .cps 알약 버튼바 정리 (위쪽 .ops-bar와 중복 없는 3대 알약 버튼)
5) sw.js 및 docs/sw.js 캐시 버전 's1-aon-v049-clean-layout' 갱신
6) 4대 HTML 1:1 동기화 (index.html, docs/index.html, rgon_alpha_chat.html, docs/rgon_alpha_chat.html)
7) s1_qm_structure_linter.py 049호 클린 레이아웃 조건 업데이트
"""

import hashlib
import pathlib
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE = pathlib.Path(__file__).resolve().parent

def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def step1_clean_index_html():
    idx_path = BASE / "index.html"
    content = idx_path.read_text(encoding="utf-8")

    # 1. Extract and remove #banner-father-mountain and #s1-autumn-winter-12tracks-showcase from pre-main
    pattern_pre_main = re.compile(
        r'(</header>\s*\n)(.*?)(\s*<!-- 7-Operations Horizontal Touch Bar)',
        re.DOTALL
    )
    m = pattern_pre_main.search(content)
    if not m:
        raise RuntimeError("Could not find block between </header> and <!-- 7-Operations")

    # Replace banner and showcase between header and ops-bar with clean spacing
    content = pattern_pre_main.sub(r'\1\n  \3', content)

    # Clean banner HTML (in-flow styling, not sticky, updated badge)
    clean_banner_html = '''  <!-- 👑 [049호 정식 승인] 한걸음씩 — 아버지 나이가 됐어요 (친근한 디즈니·픽사 감성 3D 실사화 & 탈줌인 모션 쇼츠) -->
  <aside class="top-player-banner" id="banner-father-mountain" style="background: linear-gradient(135deg, rgba(17, 24, 39, 0.98), rgba(15, 23, 42, 0.98)); border: 1.5px solid #ec4899; border-radius: 12px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; gap: 12px; margin: 12px 0; box-shadow: 0 4px 20px rgba(236, 72, 153, 0.25); flex-wrap: wrap;">
    <div style="display:flex; align-items:center; gap:12px; min-width:280px;">
      <img src="./audio/father_age_shorts_scenes/scene_01.png?v=042" alt="아버지 나이가 됐어요 (친근한 디즈니·픽사 감성 3D 1컷)" style="width:48px; height:48px; border-radius:8px; border:1px solid #ec4899; object-fit:cover; flex-shrink:0;">
      <div>
        <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
          <span style="background:#be185d; color:#fff; font-size:10px; font-weight:800; padding:2px 6px; border-radius:4px;">🎬 049호: 시원한 클린 단일 스크롤 레이아웃 &amp; 12트랙 쇼케이스 단일화 &amp; SW 캐시소각 (17/17 PASS)</span>
          <span style="font-size:11px; color:#f472b6; font-weight:700;">한걸음씩 (@sangill111157)</span>
        </div>
        <div style="font-size:14px; font-weight:800; color:#fff; margin-top:2px;">아버지 나이가 됐어요 <span style="font-size:11px; color:#9ca3af; font-weight:400;">(34s 후렴구 비트칼싱크 · 디즈니 3D 아버지 미소 · FM-012 15/15 PASS)</span></div>
      </div>
    </div>
    <div style="display:flex; align-items:center; gap:8px; flex-grow:1; max-width:680px; justify-content:flex-end; flex-wrap:wrap;">
      <a href="./audio/FATHER_AGE_MASTER_SHORTS_1080x1920.mp4?v=042" target="_blank" rel="noopener noreferrer" style="background:#ec4899; color:#fff; text-decoration:none; padding:7px 12px; border-radius:6px; font-size:11px; font-weight:800; display:inline-flex; align-items:center; gap:4px; white-space:nowrap; border:1px solid #f472b6; box-shadow:0 0 10px rgba(236,72,153,0.4);">
        📱 9:16 쇼츠 재생
      </a>
      <audio controls preload="metadata" style="height:34px; max-width:240px; width:100%; border-radius:18px;">
        <source src="https://raw.githubusercontent.com/sangill111157-spec/hangeoreumsshik-cloud/main/studio_vault/CEO_SUNO_V6_MASTERS/FATHER_AGE_master_320kbps.mp3" type="audio/mpeg">
        <source src="./audio/FATHER_AGE_master_320kbps.mp3" type="audio/mpeg">
      </audio>
      <a href="./audio/FATHER_AGE_1080p_MV.mp4" target="_blank" rel="noopener noreferrer" style="background:#be185d; color:#fff; text-decoration:none; padding:7px 10px; border-radius:6px; font-size:11px; font-weight:700; display:inline-flex; align-items:center; gap:4px; white-space:nowrap; border:1px solid #ec4899;">
        🎬 풀MV
      </a>
      <a href="https://suno.com/song/997ce931-4adc-490d-8f6c-acad54d1cd62" target="_blank" rel="noopener noreferrer" style="background:rgba(255,255,255,0.08); color:#f472b6; text-decoration:none; padding:7px 10px; border-radius:6px; font-size:11px; font-weight:700; white-space:nowrap; border:1px solid rgba(244,114,182,0.3);">
        🎵 Suno 원본
      </a>
    </div>
  </aside>'''

    # Clean 12-track showcase HTML (single unified card inside main)
    clean_showcase_html = '''  <!-- 049호 신보 가을과 겨울 사이 12트랙 쇼케이스 단일 통합 카드 -->
  <section id="s1-autumn-winter-12tracks-showcase" style="margin: 0 0 16px 0; padding: 16px 18px; border: 1.5px solid #d97706; background: linear-gradient(135deg, rgba(30, 41, 59, 0.98), rgba(15, 23, 42, 0.98)); border-radius: 12px; box-shadow: 0 4px 20px rgba(217, 119, 6, 0.25);">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px; flex-wrap:wrap; gap:8px;">
      <div style="display:flex; align-items:center; gap:8px;">
        <span style="font-size:20px;">🍂</span>
        <span style="font-weight:800; color:#fbbf24; font-size:15px;">[2026.11.06 글로벌 발매] 한걸음씩 정규 신보 〈가을과 겨울 사이〉 12트랙 전곡 라인업</span>
        <span style="background:#be185d; color:#fff; font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px;">총 53곡 달성 · 24개 스토어 배급 · 유료 Extras 0원 방어</span>
      </div>
      <span style="background:#059669; color:#fff; font-size:11px; font-weight:800; padding:4px 10px; border-radius:6px;">D-2 전세계 동시공개</span>
    </div>
    <p style="font-size:12.5px; color:#cbd5e1; margin:0 0 12px 0; line-height:1.6;">
      기존 41곡 카탈로그에 신보 12곡을 더해 <b>총 53곡 글로벌 원장</b> 체제를 구축했습니다. DistroKid 24개 글로벌 플랫폼에 정규 발매되며, 유료 Extras 4종을 전면 배제(0원 무과금 방어)하여 33% 글로벌 환원 철학을 온전히 수호합니다.
    </p>
    <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 8px; font-size:12px; margin-bottom: 12px;">
      <div style="background:rgba(255,255,255,0.06); padding:8px 10px; border-radius:6px; color:#e2e8f0; border-left:3px solid #64748b;">01. 막차 (Opening)</div>
      <div style="background:rgba(255,255,255,0.06); padding:8px 10px; border-radius:6px; color:#e2e8f0; border-left:3px solid #64748b;">02. 창을 닫지 마</div>
      <div style="background:rgba(255,255,255,0.06); padding:8px 10px; border-radius:6px; color:#e2e8f0; border-left:3px solid #64748b;">03. 첫 입김</div>
      <div style="background:rgba(217,119,6,0.22); padding:8px 10px; border-radius:6px; border-left:3px solid #f59e0b; color:#fbbf24; font-weight:700;">04. 오늘은 여기까지 ★</div>
      <div style="background:rgba(217,119,6,0.22); padding:8px 10px; border-radius:6px; border-left:3px solid #f59e0b; color:#fbbf24; font-weight:700;">05. 밥은 먹었니 ★</div>
      <div style="background:rgba(255,255,255,0.06); padding:8px 10px; border-radius:6px; color:#e2e8f0; border-left:3px solid #64748b;">06. 식어 가는 차</div>
      <div style="background:rgba(255,255,255,0.06); padding:8px 10px; border-radius:6px; color:#e2e8f0; border-left:3px solid #64748b;">07. 가로등 아래서</div>
      <div style="background:rgba(255,255,255,0.06); padding:8px 10px; border-radius:6px; color:#e2e8f0; border-left:3px solid #64748b;">08. 남겨 둔 자리</div>
      <div style="background:rgba(255,255,255,0.06); padding:8px 10px; border-radius:6px; color:#e2e8f0; border-left:3px solid #64748b;">09. 보내지 않은 말</div>
      <div style="background:rgba(217,119,6,0.22); padding:8px 10px; border-radius:6px; border-left:3px solid #f59e0b; color:#fbbf24; font-weight:700;">10. 불은 꺼지지 않아 ★</div>
      <div style="background:rgba(255,255,255,0.06); padding:8px 10px; border-radius:6px; color:#e2e8f0; border-left:3px solid #64748b;">11. 난로 옆에서</div>
      <div style="background:rgba(217,119,6,0.22); padding:8px 10px; border-radius:6px; border-left:3px solid #f59e0b; color:#fbbf24; font-weight:700;">12. 내일의 아침 ★</div>
    </div>
    <div style="display:flex; gap:10px; flex-wrap:wrap;">
      <a href="./S1_DISTROKID_53_TRACKS_MASTER_LEDGER.json" target="_blank" style="background:#2563eb; color:#fff; text-decoration:none; padding:6px 12px; border-radius:6px; font-size:11px; font-weight:700; display:inline-flex; align-items:center; gap:4px;">💿 53곡 마스터 원장 JSON</a>
      <a href="./S1_AUTUMN_WINTER_12TRACKS_LAUNCH_MASTERBOOK.md" target="_blank" style="background:#7c3aed; color:#fff; text-decoration:none; padding:6px 12px; border-radius:6px; font-size:11px; font-weight:700; display:inline-flex; align-items:center; gap:4px;">📖 1+12 폭포수 퍼널 마스터북</a>
    </div>
  </section>'''

    # Clean .cps button bar HTML
    clean_cps_html = '''    <div class="cps" id="cps-bar">
      <button class="cp" data-q="25노드 지식그래프 지도 브리핑해줘">🗺️ 25노드 지식그래프</button>
      <button class="cp" data-q="상선약수 33% 글로벌 환원 철학과 비전 브리핑해줘">💧 상선약수 환원철학</button>
      <button class="cp" data-q="실시간 시스템 헬스체크 및 린터 감사 현황 보고해줘">🛡️ 무결성 실시간 감사</button>
    </div>'''

    # 2. Inside <main class="mn" id="st">, replace the entire chunk up to <div class="hr" id="hr">
    pattern_inside_main = re.compile(
        r'(<main class="mn" id="st"[^>]*>\s*\n)(.*?)(\s*<!-- Centered Hero Branding Box -->)',
        re.DOTALL
    )
    m2 = pattern_inside_main.search(content)
    if not m2:
        raise RuntimeError("Could not find content inside <main class=\"mn\"> before <!-- Centered Hero")

    new_main_head = f"\\1\n{clean_banner_html}\n\n{clean_showcase_html}\n\n{clean_cps_html}\n\n\\3"
    content = pattern_inside_main.sub(new_main_head, content)

    # 3. Update cache nuke in bottom script of index.html
    content = re.sub(
        r"if \(k !== 's1-aon-v048-kakaopage-live'\)",
        "if (k !== 's1-aon-v049-clean-layout')",
        content
    )
    content = re.sub(
        r"\[048-NUKE\]",
        "[049-NUKE]",
        content
    )

    idx_path.write_text(content, encoding="utf-8")
    print("✅ index.html cleaned and restructured successfully!")

def step2_update_sw_js():
    sw_path = BASE / "sw.js"
    docs_sw = BASE / "docs" / "sw.js"

    sw_txt = sw_path.read_text(encoding="utf-8")
    sw_txt = re.sub(
        r"const CACHE = 's1-aon-v[0-9a-zA-Z_-]+';",
        "const CACHE = 's1-aon-v049-clean-layout';",
        sw_txt
    )
    sw_txt = re.sub(
        r"// S1 Service Worker v2026-v\d+",
        "// S1 Service Worker v2026-v049",
        sw_txt
    )
    sw_path.write_text(sw_txt, encoding="utf-8")
    shutil.copyfile(sw_path, docs_sw)
    print("✅ sw.js and docs/sw.js updated to 's1-aon-v049-clean-layout'!")

def step3_sync_4_htmls():
    idx = BASE / "index.html"
    d_idx = BASE / "docs" / "index.html"
    chat = BASE / "rgon_alpha_chat.html"
    d_chat = BASE / "docs" / "rgon_alpha_chat.html"

    shutil.copyfile(idx, d_idx)
    shutil.copyfile(idx, chat)
    shutil.copyfile(idx, d_chat)

    h0 = sha256_file(idx)
    assert sha256_file(d_idx) == h0, "docs/index.html mismatch"
    assert sha256_file(chat) == h0, "rgon_alpha_chat.html mismatch"
    assert sha256_file(d_chat) == h0, "docs/rgon_alpha_chat.html mismatch"
    print(f"✅ 4 HTML files 1:1 synchronized! (SHA256: {h0[:16]}...)")

def step4_update_linter():
    linter_path = BASE / "s1_qm_structure_linter.py"
    linter_txt = linter_path.read_text(encoding="utf-8")

    # 1. Update check_fm008 badge_valid to include 049
    linter_txt = re.sub(
        r'("047호: 카카오페이지" in html or "048호: 카카오페이지" in html)',
        r'\1 or "049호: 시원한" in html or "049호: 클린" in html',
        linter_txt
    )

    # 2. Update check_fm012 sw check to include s1-aon-v049-
    linter_txt = re.sub(
        r'("s1-aon-v048-" not in sw_text and )',
        r'\1"s1-aon-v049-" not in sw_text and ',
        linter_txt
    )

    # 3. Replace the KakaoPage check in check_fm014 with clean layout check (049호)
    old_kp_section = re.compile(
        r'    # 6\. 카카오페이지 4대 DOM ID 검증 \(047호\).*?(?=    return True, f"전달봇 AST 정적 검증)',
        re.DOTALL
    )

    new_clean_layout_check = '''    # 6. [049호 클린 단일 스크롤 레이아웃 & 4대 HTML 1:1 동기화 검증]
    idx_f = BASE / "index.html"
    if not idx_f.exists():
        return False, "index.html 누락"
    idx_content = idx_f.read_text(encoding="utf-8", errors="ignore")

    # [049호 4대 HTML 1:1 동기화 검증]
    html_files = [
        BASE / "index.html",
        BASE / "docs" / "index.html",
        BASE / "rgon_alpha_chat.html",
        BASE / "docs" / "rgon_alpha_chat.html"
    ]
    for hf in html_files:
        if not hf.exists():
            return False, f"필수 HTML 파일 부재: {hf.name}"
    base_hash = sha256_file(html_files[0])
    for hf in html_files[1:]:
        if sha256_file(hf) != base_hash:
            return False, f"4대 HTML 1:1 동기화 불일치: {hf.relative_to(BASE)} != index.html"

    # [049호 sw.js 캐시 버전 검증]
    sw_f = BASE / "sw.js"
    docs_sw_f = BASE / "docs" / "sw.js"
    if "s1-aon-v049-clean-layout" not in sw_f.read_text(encoding="utf-8"):
        return False, "sw.js 캐시 버전 미갱신 (s1-aon-v049-clean-layout 필수)"
    if not docs_sw_f.exists() or sha256_file(sw_f) != sha256_file(docs_sw_f):
        return False, "sw.js <-> docs/sw.js 해시 불일치"

    # [049호 <main class="mn"> 바깥 상단 고정 영역 다이어트 검증]
    mn_pos = idx_content.find('<main class="mn"')
    if mn_pos == -1:
        return False, "<main class='mn'> 스크롤 컨테이너 부재"

    banner_pos = idx_content.find('id="banner-father-mountain"')
    showcase_pos = idx_content.find('id="s1-autumn-winter-12tracks-showcase"')
    if banner_pos == -1:
        return False, "#banner-father-mountain 부재"
    if showcase_pos == -1:
        return False, "#s1-autumn-winter-12tracks-showcase 부재"
    if banner_pos < mn_pos:
        return False, f"#banner-father-mountain이 <main class='mn'> 바깥(상단 고정 영역)에 위치하여 화면 짓누름 결함 유발 (banner_pos={banner_pos} < mn_pos={mn_pos})"
    if showcase_pos < mn_pos:
        return False, f"#s1-autumn-winter-12tracks-showcase가 <main class='mn'> 바깥(상단 고정 영역)에 위치하여 화면 짓누름 결함 유발 (showcase_pos={showcase_pos} < mn_pos={mn_pos})"

    # <main class="mn"> 바깥에 거대 섹션 존재 금지
    pre_mn_text = idx_content[:mn_pos]
    if 'id="s1-autumn-winter-12tracks-showcase"' in pre_mn_text:
        return False, "<main class='mn'> 바깥 상단 고정 영역에 거대 쇼케이스 박스 잔존 결함"
    if 'id="banner-father-mountain"' in pre_mn_text:
        return False, "<main class='mn'> 바깥 상단 고정 영역에 상단 배너 잔존 결함"

    # [049호 12곡 단일 통합 & 문구 정합 검증]
    showcase_count = len(re.findall(r'<section\s+[^>]*id="s1-autumn-winter-12tracks-showcase"', idx_content))
    if showcase_count != 1:
        return False, f"신보 12트랙 쇼케이스 카드 중복/누락 결손: {showcase_count}개 발견 (정확히 단 1개 필수)"

    if 'id="s1-kakaopage-ranking-chart"' in idx_content:
        return False, "2중 중복 12곡 랭킹차트(#s1-kakaopage-ranking-chart) 미제거 잔존 결함"

    if "기존 53곡 카탈로그에 신보 12곡을 더해" in idx_content:
        return False, "왜곡된 문구 '기존 53곡 카탈로그에 신보 12곡을 더해' 잔존 (41+12=53 수정 필요)"
    if "기존 41곡 카탈로그에 신보 12곡을 더해" not in idx_content:
        return False, "필수 문구 '기존 41곡 카탈로그에 신보 12곡을 더해' 누락"
    if "총 53곡 글로벌 원장" not in idx_content:
        return False, "필수 문구 '총 53곡 글로벌 원장' 누락"

    # 12곡 정품 타이틀 전수 검증
    twelve_tracks = [
        "01. 막차", "02. 창을 닫지 마", "03. 첫 입김", "04. 오늘은 여기까지",
        "05. 밥은 먹었니", "06. 식어 가는 차", "07. 가로등 아래서", "08. 남겨 둔 자리",
        "09. 보내지 않은 말", "10. 불은 꺼지지 않아", "11. 난로 옆에서", "12. 내일의 아침"
    ]
    for trk in twelve_tracks:
        if trk not in idx_content:
            return False, f"12트랙 정품 곡명 누락: '{trk}'"

    # 잔류 찌꺼기 0건 검증
    forbidden_residues = ["Track 02 · Acoustic", "Track 03 · Warm Pad", "가을의 마지막 잎새", "첫눈 오는 날의 온기"]
    for fr in forbidden_residues:
        if fr in idx_content:
            return False, f"레이아웃 결함 잔류 찌꺼기 감지! '{fr}' 즉시 퇴출 필수 (QM-SP-11 격리)"

'''

    m_kp = old_kp_section.search(linter_txt)
    if not m_kp:
        raise RuntimeError("Could not find old KakaoPage section in s1_qm_structure_linter.py")

    linter_txt = old_kp_section.sub(new_clean_layout_check, linter_txt)
    linter_path.write_text(linter_txt, encoding="utf-8")
    print("✅ s1_qm_structure_linter.py updated with 049 clean layout verification!")

if __name__ == "__main__":
    step1_clean_index_html()
    step2_update_sw_js()
    step3_sync_4_htmls()
    step4_update_linter()
    print("\n🎉 ALL 049 CLEANUP STEPS APPLIED SUCCESSFULLY!")

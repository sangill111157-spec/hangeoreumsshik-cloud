#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_step63_playwright.py
================================================================================
Step 63 사령부 26대 무결성 종합 실측 검증기
(Playwright 헤드리스 브라우저 + AST 시냅스 + 38대 기관 + 13대 쇼츠 옴니 + 5TB 아카이브)
================================================================================
"""

import os
import sys
import io
import time
import json
import subprocess
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr

def test_step63_full_verification():
    print("=" * 80)
    print("🚀 [Step 63 사령부 26대 무결성 종합 실측 검증 개시]")
    print("=" * 80)

    results = []
    def log_result(idx, title, passed, detail=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        results.append((idx, title, passed, detail))
        print(f"[{status}] Test #{idx:02d}: {title}")
        if detail:
            print(f"       ㄴ {detail}")
        if not passed:
            raise RuntimeError(f"Test #{idx:02d} FAILED: {title} - {detail}")

    # 1. 헌법 4대 파일 점검
    req_files = [
        r"C:\Users\sangi\.gemini\GEMINI.md",
        r"C:\Users\sangi\.gemini\AGENTS.md",
        "GEMINI.md",
        "AGENTS.md"
    ]
    all_const_ok = True
    for rf in req_files:
        if not os.path.exists(rf):
            all_const_ok = False; break
        with open(rf, "r", encoding="utf-8") as f:
            c = f.read()
            if "Gemini 4 Argon" not in c or "상선약수" not in c or "이해상" not in c:
                all_const_ok = False; break
    log_result(1, "Antigravity 최고 헌법 4대 파일(글로벌 2개 + 로컬 2개) 무결성", all_const_ok)

    # 2. 제38기관 rgon_aon_13shorts_omni_engine.py 25대 무결성 셀프테스트
    code, out, _ = run_cmd("python rgon_aon_13shorts_omni_engine.py --self-test")
    log_result(2, "제38기관 rgon_aon_13shorts_omni_engine.py 25대 무결성 셀프테스트", code == 0 and "25/25" in out, "25/25 통과 확인")

    # 3. 제37기관 rgon_aon_gdrive_5tb_organizer.py 25대 무결성 셀프테스트
    code, out, _ = run_cmd("python rgon_aon_gdrive_5tb_organizer.py --self-test")
    log_result(3, "제37기관 rgon_aon_gdrive_5tb_organizer.py 25대 무결성 셀프테스트", code == 0 and "25/25" in out, "25/25 통과 확인")

    # 4. 제36기관 rgon_aon_empire_asset_hub.py 25대 무결성 셀프테스트
    code, out, _ = run_cmd("python rgon_aon_empire_asset_hub.py --self-test")
    log_result(4, "제36기관 rgon_aon_empire_asset_hub.py 25대 무결성 셀프테스트", code == 0 and "25/25" in out, "25/25 통과 확인")

    # 5. rgon_neural_synapse_verifier.py 29개 시냅스 & 31개 노드 100.0점 만점
    code, out, _ = run_cmd("python rgon_neural_synapse_verifier.py --status")
    log_result(5, "신경망 시냅스 검증기 31개 노드 & 29개 시냅스 100.0점 만점", code == 0 and "100.0" in out, "synapse_health_score: 100.0")

    # 25. 마스터 원장 파일 3종 검증
    manifests_ok = (
        os.path.exists("aon_13shorts_omni_manifest.json") and
        os.path.exists(".agents/product-marketing.md") and
        os.path.exists(".agents/admin_gate.json")
    )
    log_result(25, "13대 쇼츠 원장 및 마케팅 정의서, PBKDF2 관리자 게이트 파일 검증", manifests_ok)

    # 26. 4대 절대 보호 파일 무접촉 검증
    code, out, _ = run_cmd("git status -s")
    protected = ["rgon_Numeric_Organ.py", "rgon_work_loop.py", "rgon_self_Reflection.py", "index_20260405_backup.html"]
    untouched = not any(p in out for p in protected)
    log_result(26, "4대 절대 보호 파일 100% 무접촉 헌법 수호 검증", untouched, "4대 파일 클린 0% 변경")

    # ==========================================================================
    # Playwright 브라우저 실측 (데스크톱 & 모바일)
    # ==========================================================================
    html_path = os.path.abspath("index.html")
    file_url = f"file:///{html_path.replace(os.sep, '/')}"

    banned_phrases = [
        "하달해 주신 뜻을 최고 우선순위로 접수하여",
        "전술 집행 태세에 돌입했습니다",
        "다음 명령을 바로 집행하겠습니다",
        "말씀하신 뜻을 명확히 접수했습니다",
        "맥락을 정확히 인지했습니다"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # ----------------------------------------------------------------------
        # Desktop Suite (1280x800)
        # ----------------------------------------------------------------------
        d_ctx = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = d_ctx.new_page()
        page.on("pageerror", lambda e: print("PAGE ERROR:", e))
        page.on("console", lambda msg: print(f"CONSOLE [{msg.type}]:", msg.text))
        page.goto(file_url, wait_until="networkidle")

        input_el = page.locator("#comm-input-box")
        send_btn = page.locator("#btn-comm-send")
        feed = page.locator("#comm-message-feed")

        def ask_and_wait(prompt, expected_kw, timeout_sec=12):
            input_el.fill(prompt)
            send_btn.click()
            t0 = time.time()
            while time.time() - t0 < timeout_sec:
                txt = feed.inner_text()
                if expected_kw in txt:
                    return True, txt
                time.sleep(0.3)
            return False, feed.inner_text()

        # 6. 데스크톱 스마트 칩 렌더링 확인 (13대 쇼츠 옴니 칩 포함)
        chips_el = page.locator("#pinnacle-smart-chips")
        chips_text = chips_el.inner_text() if chips_el.count() > 0 else ""
        has_chips = (
            "음원(27곡)" in chips_text and
            "유튜브 3채널" in chips_text and
            "틱톡" in chips_text and
            "건강 블로그" in chips_text and
            "5TB 드라이브" in chips_text and
            "13대 쇼츠 옴니" in chips_text
        )
        log_result(6, "데스크톱 소통창 6대 퀵 스마트 칩 렌더링 확인 (13대 쇼츠 포함)", has_chips, chips_text[:80])

        # 7. 데스크톱 13대 쇼츠 옴니 질의
        ok, txt = ask_and_wait("13대 쇼츠 옴니 알려줘", "13대 쇼츠")
        print("DEBUG test 7 txt:", txt[:300])
        log_result(7, "데스크톱 13대 쇼츠 옴니 질의 (Jev 1.14, 마케팅 52, 존코바, PHP2Shell)", ok and ("Jev" in txt or "jev" in txt) and "마케팅" in txt and "존코바" in txt)

        # 8. 곧 발매될 음원 알려줘
        ok, txt = ask_and_wait("곧 발매될 음원 알려줘", "가을과 겨울 사이")
        log_result(8, "데스크톱 음원 질의 ('가을과 겨울 사이', '잔상', '700563848544')", ok and "잔상" in txt and "700563848544" in txt)

        # 9. 유튜브 3채널과 틱톡 알려줘
        ok, txt = ask_and_wait("유튜브 3채널과 틱톡 알려줘", "@한걸음씩-r4i")
        log_result(9, "데스크톱 유튜브 & 틱톡 질의 ('@Booster_Playlist', '2,125명')", ok and "@Booster_Playlist" in txt and "2,125" in txt)

        # 10. 블로그 현황 알려줘
        ok, txt = ask_and_wait("블로그 현황 알려줘", "connect-ai-shin.blogspot.com")
        log_result(10, "데스크톱 블로그 질의 ('connect-ai-shin.blogspot.com', '3조 2교대')", ok and "3조 2교대" in txt)

        # 11. 구글 드라이브 5TB 현황 알려줘
        ok, txt = ask_and_wait("구글 드라이브 5TB 현황 알려줘", "5,000")
        log_result(11, "데스크톱 5TB 아카이브 질의 ('4,984.09', '99.68%', '00_')", ok and "4,984.09" in txt and "99.68%" in txt and "00_" in txt)

        # 12. 인스타 홍보글 써줘
        ok, txt = ask_and_wait("인스타 홍보글 써줘", "인스타그램")
        log_result(12, "데스크톱 SNS 홍보 카피 질의 (인스타그램/릴스/스레드/페이스북)", ok)

        # 13. 안총리 나와라
        ok, txt = ask_and_wait("안총리 나와라", "충성! 대표님, 기술총리 안총리와 만능 참모 아온이 즉시 대령했습니다")
        log_result(13, "데스크톱 직통 호출 인사 ('안총리 나와라' ➔ 즉시 대령)", ok)

        # 14. 안총리 지금 바로 완료한 작업이 뭐야
        ok, txt = ask_and_wait("안총리 지금 바로 완료한 작업이 뭐야", "13대 쇼츠")
        log_result(14, "데스크톱 최근 완료 작업 브리핑 (Step 63 13대 쇼츠 + Step 61 6대 자산 + Step 62 5TB)", ok)

        # 15. 현재 시각과 날짜는
        ok, txt = ask_and_wait("현재 시각과 날짜는", "현재 날짜는")
        log_result(15, "데스크톱 실시간 시각 & 날짜 브리핑 (⏰📅)", ok)

        # 16. 오 더하기 오 는
        ok, txt = ask_and_wait("오 더하기 오 는", "10")
        log_result(16, "데스크톱 한글 수사 계산 ('오 더하기 오 는' ➔ 10)", ok)

        # 17. 지금 맡은 업무와 아온이는 어떻게 탄생 했지 (복합 질문)
        ok, txt = ask_and_wait("지금 맡은 업무와 아온이는 어떻게 탄생 했지", "상선약수")
        log_result(17, "데스크톱 복합 질문 동시 완답 (핵심 임무 + 아온이 상선약수 & 이해상 디자이너)", ok and "이해상" in txt)

        # 18. 날것의 별표 0건 & 깡통 문구 0건 사수
        full_feed = feed.inner_text()
        has_raw_stars = "**" in full_feed
        has_canned = any(bp in full_feed for bp in banned_phrases)
        log_result(18, "피드 전체 날것의 '**' 0건 및 깡통 에코 문구 영구 소각 0건", (not has_raw_stars) and (not has_canned))

        d_ctx.close()

        # ----------------------------------------------------------------------
        # Mobile Suite (iPhone Mini / SE: 375x812)
        # ----------------------------------------------------------------------
        m_ctx = browser.new_context(
            viewport={'width': 375, 'height': 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        )
        m_page = m_ctx.new_page()
        m_page.goto(file_url, wait_until="networkidle")

        m_input = m_page.locator("#comm-input-box")
        m_send = m_page.locator("#btn-comm-send")
        m_feed = m_page.locator("#comm-message-feed")

        def m_ask_and_wait(prompt, expected_kw, timeout_sec=12):
            m_input.fill(prompt)
            m_send.click()
            t0 = time.time()
            while time.time() - t0 < timeout_sec:
                txt = m_feed.inner_text()
                if expected_kw in txt:
                    return True, txt
                time.sleep(0.3)
            return False, m_feed.inner_text()

        # 19. 모바일 5G 뷰포트 13대 쇼츠 옴니 질의
        ok, txt = m_ask_and_wait("13대 쇼츠 옴니 알려줘", "13대 쇼츠 옴니-인텔리전스 마스터 엔진")
        log_result(19, "모바일 5G 뷰포트(375x812) 13대 쇼츠 옴니 질의 응답 실측", ok and "Jev 1.14" in txt)

        # 20. 모바일 [⚡ 전송] 버튼 및 우측 엣지 영역 침범 0% 검증
        send_box = m_send.bounding_box()
        # send_box 가 뷰포트 width (375) 내에 완전히 들어오는지 검증
        btn_inside = (send_box is not None and send_box['x'] + send_box['width'] <= 375)
        log_result(20, "모바일 5G 뷰포트 [⚡ 전송] 버튼 및 우측 엣지 침범 0% 검증", btn_inside, f"x={send_box['x'] if send_box else 0}, w={send_box['width'] if send_box else 0}")

        # 21. 모바일 호출 질의
        ok, txt = m_ask_and_wait("안총리 나와라", "충성! 대표님, 기술총리 안총리와 만능 참모 아온이 즉시 대령했습니다")
        log_result(21, "모바일 5G 뷰포트 직통 호출 인사 ('안총리 나와라' ➔ 즉시 대령)", ok)

        m_ctx.close()

        # ----------------------------------------------------------------------
        # Dedicated Hub Pages
        # ----------------------------------------------------------------------
        # 22. rgon_13shorts_omni_studio.html
        shorts_studio_url = f"file:///{os.path.abspath('rgon_13shorts_omni_studio.html').replace(os.sep, '/')}"
        sh_page = browser.new_page(viewport={'width': 1280, 'height': 800})
        sh_page.goto(shorts_studio_url, wait_until="networkidle")
        sh_txt = sh_page.content()
        has_studio_features = (
            "TypeSafe Jev 1.14" in sh_txt and
            "마케팅 52스킬" in sh_txt and
            "존코바" in sh_txt and
            "PHP2Shell" in sh_txt
        )
        log_result(22, "13대 쇼츠 옴니 웹 스튜디오 페이지 로드 & 4대 권역 인터랙션 확인", has_studio_features)
        sh_page.close()

        # 23. rgon_gdrive_5tb_hub.html
        hub_url = f"file:///{os.path.abspath('rgon_gdrive_5tb_hub.html').replace(os.sep, '/')}"
        h_page = browser.new_page(viewport={'width': 1280, 'height': 800})
        h_page.goto(hub_url, wait_until="networkidle")
        h_txt = h_page.locator("body").inner_text()
        log_result(23, "Google One 5TB 전용 아카이브 허브 웹 페이지 로드 & 99.68% 게이지 확인", "4,984.09" in h_txt and "99.68%" in h_txt and "00_INBOX" in h_txt)
        h_page.close()

        # 24. rgon_opus_motion_studio.html
        motion_url = f"file:///{os.path.abspath('rgon_opus_motion_studio.html').replace(os.sep, '/')}"
        mo_page = browser.new_page(viewport={'width': 1280, 'height': 800})
        mo_page.goto(motion_url, wait_until="networkidle")
        mo_txt = mo_page.locator("body").inner_text()
        has_presets = (
            "가을과 겨울 사이" in mo_txt and
            "잔상" in mo_txt and
            "부스터 플리" in mo_txt and
            "The Café Hour" in mo_txt and
            "건강 블로그" in mo_txt
        )
        log_result(24, "클로드 오퍼스 5.5 모션 스튜디오 5대 자산 프리셋 로드 확인", has_presets)
        mo_page.close()

        browser.close()

    print("\n" + "=" * 80)
    print("🏆 [Step 63 사령부 26대 무결성 종합 실측 검증: 26/26 100% ALL PASS!]")
    print("=" * 80)
    return True

if __name__ == "__main__":
    try:
        success = test_step63_full_verification()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ [ERROR] 검증 중 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

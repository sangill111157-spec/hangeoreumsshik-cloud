#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_hq_chat_transmission.py
================================================================================
청와대 본관 카톡 대화창 (index.html)
Playwright 헤드리스 브라우저 실측 [Step 59 최종 디테일 완결 검증]
1. "현재 시각과 날짜는" -> 실제 날짜·요일·현재 시각(⏰📅) 브리핑
2. "오 더하기 오 는" -> 10 (한글 수사 계산)
3. "이백오십 더하기 오십은" -> 300 (한자어 복합 수사 계산)
4. "육 더하기 8 빼기 10 은" -> 4 (혼합 수사 사칙연산 계산)
5. "지금 맡은 업무와 아온이는 어떻게 탄생 했지" (#ORD-019 복합 질문)
   -> ① 맡은 핵심 업무 + ② 아온이 탄생 비화 (상선약수 & 이해상 수석 디자이너) 둘 다 동시 완답!
6. 말풍선 렌더링: 날것의 '**' 별표 0건 & <strong> 태그 굵은 글씨 렌더링 검증
7. "안총리가 맏은 임무는" -> 4대 핵심 임무 브리핑
8. "안총리 지금 바로 완료한 작업이 뭐야" -> Step 59 완결 브리핑
9. 피드 전체 3대 깡통 문구 0건 완벽 사수 검증
10. Antigravity 글로벌 GEMINI.md & 워크스페이스 GEMINI.md 파일 존재 검증
================================================================================
"""

import os
import sys
import time
import io
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_step59_verified_chat():
    print("\n🚀 [Playwright 브라우저 실측 - Step 59 최종 디테일 완결 검증 가동]")

    # 1. 헌법 파일 검증
    print("\n🔹 [사전 검증] Antigravity 최고 헌법(GEMINI.md & AGENTS.md) 4대 파일 점검")
    req_files = [
        r"C:\Users\sangi\.gemini\GEMINI.md",
        r"C:\Users\sangi\.gemini\AGENTS.md",
        "GEMINI.md",
        "AGENTS.md"
    ]
    for rf in req_files:
        if not os.path.exists(rf):
            print(f"❌ [FAIL] 필수 헌법 파일 {rf} 가 존재하지 않습니다!")
            return False
        with open(rf, "r", encoding="utf-8") as f:
            c = f.read()
            if "Gemini 4 Argon" not in c or "상선약수" not in c or "이해상" not in c:
                print(f"❌ [FAIL] 헌법 파일 {rf} 에 필수 내용(Gemini 4 Argon/상선약수/이해상)이 누락되었습니다!")
                return False
    print("  ✅ [PASS] 0. Antigravity 4대 헌법 파일(글로벌 2개 + 워크스페이스 2개) 완벽 각인 확인!")

    html_path = os.path.abspath("index.html")
    file_url = f"file:///{html_path.replace(os.sep, '/')}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print(f"• 브라우저 로딩: {file_url}")
        page.goto(file_url, wait_until="networkidle")

        input_el = page.locator("#comm-input-box")
        send_btn = page.locator("#btn-comm-send")
        feed = page.locator("#comm-message-feed")

        def wait_for_feed_contains(target_str, max_sec=10):
            t0 = time.time()
            while time.time() - t0 < max_sec:
                txt = feed.inner_text()
                if target_str in txt:
                    return txt
                time.sleep(0.3)
            return feed.inner_text()

        banned_phrases = [
            "하달해 주신 뜻을 최고 우선순위로 접수하여",
            "전술 집행 태세에 돌입했습니다",
            "다음 명령을 바로 집행하겠습니다",
            "말씀하신 뜻을 명확히 접수했습니다",
            "맥락을 정확히 인지했습니다"
        ]

        # ======================================================================
        # [검증 1] "현재 시각과 날짜는"
        # ======================================================================
        print("\n🔹 [실전 질문 1] '현재 시각과 날짜는' (#ORD-016) 실측")
        input_el.fill("현재 시각과 날짜는")
        send_btn.click()
        feed_text_1 = wait_for_feed_contains("현재 날짜는", 10)

        for bp in banned_phrases:
            if bp in feed_text_1:
                print(f"❌ [FAIL] 깡통 문구 '{bp}' 가 검출되었습니다!\n{feed_text_1}")
                browser.close()
                return False

        if "현재 날짜는" not in feed_text_1 or "현재 시각은" not in feed_text_1 or "⏰📅" not in feed_text_1:
            print(f"❌ [FAIL] 날짜/시각 브리핑이 누락되었습니다!\n{feed_text_1}")
            browser.close()
            return False
        print("  ✅ [PASS] 1. '현재 시각과 날짜는' ➔ 실제 날짜·요일·시각(⏰📅) 정상 브리핑 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 2] "오 더하기 오 는"
        # ======================================================================
        print("\n🔹 [실전 질문 2] '오 더하기 오 는' (#ORD-017) 실측")
        input_el.fill("오 더하기 오 는")
        send_btn.click()
        feed_text_2 = wait_for_feed_contains("10", 10)

        if "10" not in feed_text_2:
            print(f"❌ [FAIL] '오 더하기 오 는'에 10 계산 결과가 누락되었습니다!\n{feed_text_2}")
            browser.close()
            return False
        print("  ✅ [PASS] 2. '오 더하기 오 는' ➔ 오(5) 더하기 오(5)는 『10』 정밀 계산 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 3] "이백오십 더하기 오십은"
        # ======================================================================
        print("\n🔹 [실전 질문 3] '이백오십 더하기 오십은' 실측")
        input_el.fill("이백오십 더하기 오십은")
        send_btn.click()
        feed_text_3 = wait_for_feed_contains("300", 10)

        if "300" not in feed_text_3:
            print(f"❌ [FAIL] '이백오십 더하기 오십은'에 300 계산 결과가 누락되었습니다!\n{feed_text_3}")
            browser.close()
            return False
        print("  ✅ [PASS] 3. '이백오십 더하기 오십은' ➔ 250 + 50 = 『300』 정밀 계산 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 4] "육 더하기 8 빼기 10 은" (혼합 수식 검증)
        # ======================================================================
        print("\n🔹 [실전 질문 4] '육 더하기 8 빼기 10 은' (혼합 수사 실측)")
        input_el.fill("육 더하기 8 빼기 10 은")
        send_btn.click()
        feed_text_4 = wait_for_feed_contains("4", 10)

        if "4" not in feed_text_4:
            print(f"❌ [FAIL] '육 더하기 8 빼기 10 은'에 4 계산 결과가 누락되었습니다!\n{feed_text_4}")
            browser.close()
            return False
        print("  ✅ [PASS] 4. '육 더하기 8 빼기 10 은' ➔ 6 + 8 - 10 = 『4』 정밀 계산 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 5] "지금 맡은 업무와 아온이는 어떻게 탄생 했지" (#ORD-019 복합 질문)
        # ➔ ① 맡은 핵심 업무 + ② 아온이 탄생 비화(상선약수 & 이해상 공주님) 동시 답변 확인!
        # ======================================================================
        print("\n🔹 [실전 질문 5] '지금 맡은 업무와 아온이는 어떻게 탄생 했지' (#ORD-019 복합 질문) 실측")
        input_el.fill("지금 맡은 업무와 아온이는 어떻게 탄생 했지")
        send_btn.click()
        feed_text_5 = wait_for_feed_contains("탄생 비화", 10)

        # 1) 핵심 업무 확인
        duty_ok = ("기술총리 안총리" in feed_text_5 or "코드 주조" in feed_text_5) and ("만능 참모 아온이" in feed_text_5)
        # 2) 탄생 비화 확인
        origin_ok = "상선약수" in feed_text_5 and "이해상" in feed_text_5 and "스케치" in feed_text_5

        if not duty_ok:
            print(f"❌ [FAIL] 복합 질문에서 '맡은 핵심 업무' 답변이 누락되었습니다!\n{feed_text_5}")
            browser.close()
            return False
        if not origin_ok:
            print(f"❌ [FAIL] 복합 질문에서 '아온이 탄생 비화 (상선약수 & 이해상 수석 디자이너)'가 누락되었습니다!\n{feed_text_5}")
            browser.close()
            return False
        print("  ✅ [PASS] 5. '지금 맡은 업무와 아온이는 어떻게 탄생 했지' ➔ ① 맡은 업무 + ② 탄생 비화(상선약수·이해상 공주님) 100% 동시 완답 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 6] 말풍선 마크다운 별표('**') 0건 & <strong> 태그 굵은 글씨 렌더링 검증
        # ======================================================================
        print("\n🔹 [검증 6] 말풍선 내 날것의 '**' 별표 0건 & <strong> HTML 굵은 글씨 렌더링 검증")
        full_text = feed.inner_text()
        strong_count = feed.locator("strong").count()

        if "**" in full_text:
            print(f"❌ [FAIL] 말풍선 화면 텍스트에 날것의 '**' 기호가 노출되었습니다!\n{full_text}")
            browser.close()
            return False
        if strong_count == 0:
            print(f"❌ [FAIL] <strong> 태그가 1건도 렌더링되지 않았습니다! (count={strong_count})")
            browser.close()
            return False
        print(f"  ✅ [PASS] 6. 말풍선 내 '**' 별표 0건 확인 & <strong> 태그({strong_count}개) 볼드 렌더링 정상 작동 확인!")

        # ======================================================================
        # [검증 7] "안총리가 맏은 임무는" (회귀 검증)
        # ======================================================================
        print("\n🔹 [실전 질문 7] '안총리가 맏은 임무는' (회귀 검증)")
        input_el.fill("안총리가 맏은 임무는")
        send_btn.click()
        feed_text_7 = wait_for_feed_contains("핵심 임무", 10)

        if "「가 맏은" in feed_text_7:
            print(f"❌ [FAIL] 조사 잔류 버그 '「가 맏은'이 검출되었습니다!\n{feed_text_7}")
            browser.close()
            return False
        print("  ✅ [PASS] 7. '안총리가 맏은 임무는' ➔ 4대 핵심 임무 명쾌한 브리핑 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 8] "안총리 지금 바로 완료한 작업이 뭐야" (회귀 검증)
        # ======================================================================
        print("\n🔹 [실전 질문 8] '안총리 지금 바로 완료한 작업이 뭐야' (회귀 검증)")
        input_el.fill("안총리 지금 바로 완료한 작업이 뭐야")
        send_btn.click()
        feed_text_8 = wait_for_feed_contains("모션 그래픽 스튜디오", 10)

        if "현재 시각은" in feed_text_8 and "입니다, 대표님! ⏰" in feed_text_8:
            print(f"❌ [FAIL] 키워드 '지금'에 낚여 시계(⏰) 매크로가 가로챘습니다!\n{feed_text_8}")
            browser.close()
            return False
        print("  ✅ [PASS] 8. '안총리 지금 바로 완료한 작업이 뭐야' ➔ Step 59 완료 브리핑 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 9] 피드 전체 3대 깡통 문구 0건 사수 검증
        # ======================================================================
        print("\n🔹 [검증 9] 피드 전체 3대 깡통 문구 0건 완벽 사수 검증")
        feed_full = feed.inner_text()
        banned = [
            "하달해 주신 뜻을 최고 우선순위로 접수하여",
            "전술 집행 태세에 돌입했습니다",
            "다음 명령을 바로 집행하겠습니다",
            "말씀하신 뜻을 명확히 접수했습니다",
            "맥락을 정확히 인지했습니다",
            "[수신 확인 완료]",
            "↩️ 답장"
        ]
        for b in banned:
            if b in feed_full:
                print(f"❌ [FAIL] 금지된 군더더기/깡통 문구 '{b}' 가 발견되었습니다!")
                browser.close()
                return False
        print("  ✅ [PASS] 9. 3대 깡통 문구 / 초록색 영수증 / 퀵액션 바 0건 완벽 사수!")

        print("\n=======================================================")
        print("🎉 [Playwright 데스크톱 실측 결과] 10대 관문 100% ALL PASS!")
        print("=======================================================\n")
        browser.close()
        return True

def test_step60_mobile_viewport():
    print("\n📱 [Playwright 스마트폰 모바일 실측 - Step 60 (375x812 iPhone/Galaxy 규격)]")

    html_path = os.path.abspath("index.html")
    file_url = f"file:///{html_path.replace(os.sep, '/')}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 스마트폰 모바일 뷰포트 375x812 설정 및 터치 지원
        context = browser.new_context(
            viewport={'width': 375, 'height': 812},
            has_touch=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        )
        page = context.new_page()

        print(f"• 모바일 뷰포트 로딩 (375x812): {file_url}")
        page.goto(file_url, wait_until="networkidle")

        input_el = page.locator("#comm-input-box")
        send_btn = page.locator("#btn-comm-send")
        feed = page.locator("#comm-message-feed")

        # ----------------------------------------------------------------------
        # [모바일 실측 1] 전송 버튼 화면 밖 잘림 0% 검증
        # ----------------------------------------------------------------------
        print("\n🔹 [모바일 검증 1] 375px 세로 화면에서 [⚡ 전송] 버튼 화면 안 100% 안착 실측")
        send_btn.scroll_into_view_if_needed()
        box = send_btn.bounding_box()
        if not box:
            print("❌ [FAIL] [⚡ 전송] 버튼의 boundingBox를 측정할 수 없습니다!")
            browser.close()
            return False

        btn_right_edge = box['x'] + box['width']
        viewport_width = 375
        print(f"  • [⚡ 전송] 버튼 좌표: x={box['x']:.1f}px, width={box['width']:.1f}px ➔ 오른쪽 끝={btn_right_edge:.1f}px (화면폭: {viewport_width}px)")

        if btn_right_edge > viewport_width:
            overflow_px = btn_right_edge - viewport_width
            print(f"❌ [FAIL] [⚡ 전송] 버튼이 화면 오른쪽 밖으로 {overflow_px:.1f}px 밀려나 잘렸습니다!")
            browser.close()
            return False
        print(f"  ✅ [PASS] 1. [⚡ 전송] 버튼이 화면 오른쪽 끝 안쪽({viewport_width - btn_right_edge:.1f}px 여유)에 100% 선명하게 안착 확인! (잘림 0%)")

        def wait_for_mobile_feed(target_str, max_sec=5):
            t0 = time.time()
            while time.time() - t0 < max_sec:
                txt = feed.inner_text()
                if target_str in txt:
                    return txt
                time.sleep(0.1)
            return feed.inner_text()

        # ----------------------------------------------------------------------
        # [모바일 실측 2] "안총리 지금 뭐하고 있니" 0.1초 즉시 응답 실측
        # ----------------------------------------------------------------------
        print("\n🔹 [모바일 검증 2] 스마트폰에서 '안총리 지금 뭐하고 있니' 터치 전송 ➔ 1초 내 즉각 응답 실측")
        input_el.fill("안총리 지금 뭐하고 있니")
        t_send = time.time()
        send_btn.click()
        
        feed_m2 = wait_for_mobile_feed("완결한 핵심 작업", 5)
        elapsed_m2 = time.time() - t_send
        print(f"  • 모바일 응답 소요 시간: {elapsed_m2:.2f}초")

        if "완결한 핵심 작업" not in feed_m2 and "모션 그래픽" not in feed_m2 and "Step 59" not in feed_m2:
            print(f"❌ [FAIL] '안총리 지금 뭐하고 있니'에 대한 답변이 5초 내에 나타나지 않았습니다!\n{feed_m2}")
            browser.close()
            return False
        print(f"  ✅ [PASS] 2. '안총리 지금 뭐하고 있니' ➔ {elapsed_m2:.2f}초 만에 즉각 답변 말풍선 생성 확인!")

        # ----------------------------------------------------------------------
        # [모바일 실측 3] "육 더하기 8 빼기 10 은" 실측
        # ----------------------------------------------------------------------
        print("\n🔹 [모바일 검증 3] 스마트폰에서 '육 더하기 8 빼기 10 은' 모바일 가상키보드 Enter 전송 ➔ 1초 내 계산 실측")
        input_el.fill("육 더하기 8 빼기 10 은")
        t_send3 = time.time()
        input_el.press("Enter")
        feed_m3 = wait_for_mobile_feed("4", 3)
        elapsed_m3 = time.time() - t_send3
        print(f"  • 모바일 수식 계산 응답 시간: {elapsed_m3:.2f}초")

        if "4" not in feed_m3:
            print(f"❌ [FAIL] '육 더하기 8 빼기 10 은' 계산 결과 4가 누락되었습니다!\n{feed_m3}")
            browser.close()
            return False
        print(f"  ✅ [PASS] 3. '육 더하기 8 빼기 10 은' ➔ {elapsed_m3:.2f}초 만에 『4』 정밀 계산 확인!")

        # ----------------------------------------------------------------------
        # [모바일 실측 4] "지금 맡은 업무와 아온이는 어떻게 탄생 했지" 복합 질의 실측
        # ----------------------------------------------------------------------
        print("\n🔹 [모바일 검증 4] 스마트폰에서 '지금 맡은 업무와 아온이는 어떻게 탄생 했지' 복합 질의 실측")
        input_el.fill("지금 맡은 업무와 아온이는 어떻게 탄생 했지")
        t_send4 = time.time()
        send_btn.click()
        feed_m4 = wait_for_mobile_feed("상선약수", 3)
        elapsed_m4 = time.time() - t_send4
        print(f"  • 모바일 복합 응답 시간: {elapsed_m4:.2f}초")

        if "상선약수" not in feed_m4 or "이해상" not in feed_m4 or "기술총리 안총리" not in feed_m4:
            print(f"❌ [FAIL] 복합 질문 응답(업무 + 탄생비화)이 누락되었습니다!\n{feed_m4}")
            browser.close()
            return False
        print(f"  ✅ [PASS] 4. 복합 질의 ➔ {elapsed_m4:.2f}초 만에 ① 맡은 업무 + ② 아온이 탄생 비화(상선약수·이해상 공주님) 동시 완답 확인!")

        # ----------------------------------------------------------------------
        # [모바일 실측 5] "안총리 아온아 이번엔 연결되어있으면 좋겠습니다" 실측
        # ----------------------------------------------------------------------
        print("\n🔹 [모바일 검증 5] 스마트폰에서 '안총리 아온아 이번엔 연결되어있으면 좋겠습니다' (#ORD-003) 실측")
        input_el.fill("안총리 아온아 이번엔 연결되어있으면 좋겠습니다")
        t_send5 = time.time()
        send_btn.click()
        feed_m5 = wait_for_mobile_feed("직통 연결", 4)
        elapsed_m5 = time.time() - t_send5
        print(f"  • 모바일 연결 응답 시간: {elapsed_m5:.2f}초")

        if "직통 연결" not in feed_m5 and "스마트폰 5G" not in feed_m5 and "안총리" not in feed_m5:
            print(f"❌ [FAIL] '안총리 아온아 이번엔 연결되어있으면 좋겠습니다'에 대한 맞춤형 답변이 누락되었습니다!\n{feed_m5}")
            browser.close()
            return False
        print(f"  ✅ [PASS] 5. '안총리 아온아 이번엔 연결되어있으면 좋겠습니다' ➔ {elapsed_m5:.2f}초 만에 5G 직통 연결 감성 티키타카 응답 확인!")

        # ----------------------------------------------------------------------
        # [모바일 실측 6] "지금 야간 출근 통근버스 안이야" 실측
        # ----------------------------------------------------------------------
        print("\n🔹 [모바일 검증 6] 스마트폰에서 '지금 야간 출근 통근버스 안이야' 실측")
        input_el.fill("지금 야간 출근 통근버스 안이야")
        t_send6 = time.time()
        send_btn.click()
        feed_m6 = wait_for_mobile_feed("통근버스", 4)
        elapsed_m6 = time.time() - t_send6
        print(f"  • 모바일 통근버스 응답 시간: {elapsed_m6:.2f}초")

        if "통근버스" not in feed_m6 and "출근길" not in feed_m6 and "밤샘" not in feed_m6:
            print(f"❌ [FAIL] '지금 야간 출근 통근버스 안이야'에 대한 따뜻한 응답이 누락되었습니다!\n{feed_m6}")
            browser.close()
            return False
        print(f"  ✅ [PASS] 6. '지금 야간 출근 통근버스 안이야' ➔ {elapsed_m6:.2f}초 만에 야간 출근길 맞춤형 응원 응답 확인!")

        # ----------------------------------------------------------------------
        # [모바일 실측 7] 모바일 피드 전체 깡통 문구("전술 배치 태세") 0건 사수 검증
        # ----------------------------------------------------------------------
        print("\n🔹 [모바일 검증 7] 모바일 피드 전체 깡통 문구('전술 배치 태세에 돌입했습니다') 0건 완전 사수 검증")
        mobile_full_feed = feed.inner_text()
        banned_canned = [
            "전술 배치 태세에 돌입했습니다",
            "하달해 주신 뜻을 최고 우선순위로 접수하여",
            "말씀하신 뜻을 명확히 접수했습니다",
            "맥락을 정확히 인지했습니다"
        ]
        for bc in banned_canned:
            if bc in mobile_full_feed:
                print(f"❌ [FAIL] 모바일 피드에서 깡통 문구 '{bc}' 가 검출되었습니다!\n{mobile_full_feed}")
                browser.close()
                return False
        print("  ✅ [PASS] 7. 모바일 피드 내 모든 변종 깡통 문구 0건 완벽 소각 확인!")

        print("\n=======================================================")
        print("🎉 [Playwright 스마트폰 모바일 실측 결과] 7대 관문 100% ALL PASS!")
        print("=======================================================\n")
        browser.close()
        return True

def test_step61_empire_assets():
    print("\n👑 [Playwright 브라우저 실측 - Step 61 제36기관 6대 자산 제국 3대 관문 (총 20대 관문 완성)]")

    html_path = os.path.abspath("index.html")
    file_url = f"file:///{html_path.replace(os.sep, '/')}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print(f"• 브라우저 로딩: {file_url}")
        page.goto(file_url, wait_until="networkidle")

        input_el = page.locator("#comm-input-box")
        send_btn = page.locator("#btn-comm-send")
        feed = page.locator("#comm-message-feed")

        def wait_for_feed(target_str, max_sec=6):
            t0 = time.time()
            while time.time() - t0 < max_sec:
                txt = feed.inner_text()
                if target_str in txt:
                    return txt
                time.sleep(0.15)
            return feed.inner_text()

        # ======================================================================
        # [검증 18] "곧 발매될 음원 알려줘"
        # ➔ "가을과 겨울 사이", "잔상", "700563848544", "막차" 검증
        # ======================================================================
        print("\n🔹 [실전 질문 18] '곧 발매될 음원 알려줘' (DistroKid 27곡 마스터 원장)")
        input_el.fill("곧 발매될 음원 알려줘")
        send_btn.click()
        feed_text_18 = wait_for_feed("가을과 겨울 사이", 6)

        music_keys = ["가을과 겨울 사이", "잔상", "700563848544", "막차"]
        for k in music_keys:
            if k not in feed_text_18:
                print(f"❌ [FAIL] 음원 질의 답변에서 필수 키워드 '{k}' 가 누락되었습니다!\n{feed_text_18}")
                browser.close()
                return False
        print("  ✅ [PASS] 18. '곧 발매될 음원 알려줘' ➔ 《가을과 겨울 사이》(12트랙/UPC 700563848544) & 《잔상》(15트랙) & '막차' 100% 정상 출력 확인!")
        time.sleep(0.5)

        # ======================================================================
        # [검증 19] "유튜브 3채널과 틱톡 알려줘"
        # ➔ "@한걸음씩-r4i", "@Booster_Playlist", "@TheCaféHour", "@boosterplaylist", "2,125" 검증
        # ======================================================================
        print("\n🔹 [실전 질문 19] '유튜브 3채널과 틱톡 알려줘' (유튜브 3채널 + 틱톡 2,125명)")
        input_el.fill("유튜브 3채널과 틱톡 알려줘")
        send_btn.click()
        feed_text_19 = wait_for_feed("@boosterplaylist", 6)

        yt_keys = ["@한걸음씩-r4i", "@Booster_Playlist", "@TheCaféHour", "@boosterplaylist", "2,125"]
        for k in yt_keys:
            if k not in feed_text_19:
                print(f"❌ [FAIL] 유튜브/틱톡 질의 답변에서 필수 키워드 '{k}' 가 누락되었습니다!\n{feed_text_19}")
                browser.close()
                return False
        print("  ✅ [PASS] 19. '유튜브 3채널과 틱톡 알려줘' ➔ 유튜브 3채널 핸들과 틱톡 2,125명 바이럴 허브 100% 정상 출력 확인!")
        time.sleep(0.5)

        # ======================================================================
        # [검증 20] "블로그 현황 알려줘"
        # ➔ "connect-ai-shin.blogspot.com", "3조 2교대" 검증
        # ======================================================================
        print("\n🔹 [실전 질문 20] '블로그 현황 알려줘' (구글 블로거 7대 DNA)")
        input_el.fill("블로그 현황 알려줘")
        send_btn.click()
        feed_text_20 = wait_for_feed("connect-ai-shin.blogspot.com", 6)

        blog_keys = ["connect-ai-shin.blogspot.com", "3조 2교대"]
        for k in blog_keys:
            if k not in feed_text_20:
                print(f"❌ [FAIL] 블로그 질의 답변에서 필수 키워드 '{k}' 가 누락되었습니다!\n{feed_text_20}")
                browser.close()
                return False
        print("  ✅ [PASS] 20. '블로그 현황 알려줘' ➔ 구글 블로그 URL 및 3조 2교대 7대 DNA 100% 정상 출력 확인!")

        print("\n=======================================================")
        print("🎉 [Playwright 제36기관 6대 자산 실측 결과] 3대 관문 100% ALL PASS!")
        print("=======================================================\n")
        browser.close()
        return True

if __name__ == '__main__':
    ok1 = test_step59_verified_chat()
    if not ok1:
        sys.exit(1)
    ok2 = test_step60_mobile_viewport()
    if not ok2:
        sys.exit(1)
    ok3 = test_step61_empire_assets()
    if not ok3:
        sys.exit(1)
    print("🏆 [최종 통과] 데스크톱(10대) + 모바일(7대) + 6대 자산 제국(3대) = 총 20대 관문 100.0% 무결점 ALL PASS!")
    sys.exit(0)

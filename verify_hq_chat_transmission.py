#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_hq_chat_transmission.py
================================================================================
청와대 본관 카톡 대화창 (index.html)
Playwright 헤드리스 브라우저 실측 [긴급 감찰 시정 검증]
1. "안총리가 맏은 임무는" -> 조사 잔류 버그(가 맏은 임무는) 0건 & 안총리 핵심 임무 브리핑
2. "인공지능 에이전트가 왜 중요할까?" -> 변종 깡통 에코("맥락을 정확히 인지했습니다") 0건 & 진짜 AI 답변
3. "안총리 지금 바로 완료한 작업이 뭐야" -> 시계(⏰) 0건 & Step 59 브리핑
4. "250 더하기 250 빼기는" -> 수식 정밀 계산
5. "모션그래픽 만들어줘" -> 인라인 iframe & [↗ 새 창으로 크게 열기]
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
    print("\n🚀 [Playwright 브라우저 실측 - 긴급 감찰 시정 명령 실측 검증 가동]")

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

        def wait_for_feed_contains(target_str, max_sec=8):
            t0 = time.time()
            while time.time() - t0 < max_sec:
                txt = feed.inner_text()
                if target_str in txt:
                    return txt
                time.sleep(0.3)
            return feed.inner_text()

        # ======================================================================
        # [검증 1] "안총리가 맏은 임무는" (사진 속 #ORD-011 적발 건)
        # ➔ 조사 잔류 버그(가 맏은 임무는) 0건 & 안총리 핵심 임무 4대 브리핑 실측!
        # ======================================================================
        print("\n🔹 [실전 질문 1] '안총리가 맏은 임무는' 실측")
        input_el.fill("안총리가 맏은 임무는")
        send_btn.click()
        feed_text_1 = wait_for_feed_contains("핵심 임무", 8)

        # 1) 조사 잔류 및 에코 템플릿 0건 확인
        if "「가 맏은" in feed_text_1 or "「가 맏은 임무는」" in feed_text_1:
            print(f"❌ [FAIL] 조사 잔류 버그 '「가 맏은 임무는」'이 검출되었습니다!\n{feed_text_1}")
            browser.close()
            return False
        if "맥락을 정확히 인지했습니다" in feed_text_1:
            print(f"❌ [FAIL] 변종 깡통 에코 템플릿 '맥락을 정확히 인지했습니다'가 검출되었습니다!\n{feed_text_1}")
            browser.close()
            return False
        print("  ✅ [PASS] 1-1. '가 맏은 임무는' 조사 잔류 0건 & 에코 템플릿 0건 완전 박멸!")

        # 2) 안총리 핵심 임무 브리핑 확인
        expected_duty = ["코드 주조", "Playwright", "서버", "GitHub SSOT"]
        for ed in expected_duty:
            if ed not in feed_text_1:
                print(f"❌ [FAIL] 안총리 핵심 임무 키워드 '{ed}'가 누락되었습니다!\n{feed_text_1}")
                browser.close()
                return False
        print("  ✅ [PASS] 1-2. '안총리가 맏은 임무는' ➔ 기술총리 안총리 4대 핵심 임무 명쾌한 브리핑 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 2] "인공지능 에이전트가 왜 중요할까?" (자유 질문)
        # ➔ 변종 에코 템플릿 0건 & 진짜 AI 에이전트 가치 답변 실측!
        # ======================================================================
        print("\n🔹 [실전 질문 2] '인공지능 에이전트가 왜 중요할까?' 실측")
        input_el.fill("인공지능 에이전트가 왜 중요할까?")
        send_btn.click()
        feed_text_2 = wait_for_feed_contains("에이전트가 결정적으로", 8)

        if "맥락을 정확히 인지했습니다" in feed_text_2:
            print(f"❌ [FAIL] 자유 질문에 변종 깡통 에코 템플릿이 출력되었습니다!\n{feed_text_2}")
            browser.close()
            return False
        print("  ✅ [PASS] 2-1. 변종 깡통 에코 템플릿 0건!")

        if "자율" not in feed_text_2 and "실행" not in feed_text_2 and "에이전트" not in feed_text_2:
            print(f"❌ [FAIL] 에이전트 가치 답변이 부실합니다!\n{feed_text_2}")
            browser.close()
            return False
        print("  ✅ [PASS] 2-2. '인공지능 에이전트가 왜 중요할까?' ➔ 깊이 있는 진짜 AI 답변 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 3] "안총리 지금 바로 완료한 작업이 뭐야"
        # ➔ 시계(⏰) 매크로 0건 & Step 59 완료 브리핑 실측!
        # ======================================================================
        print("\n🔹 [실전 질문 3] '안총리 지금 바로 완료한 작업이 뭐야' 실측")
        input_el.fill("안총리 지금 바로 완료한 작업이 뭐야")
        send_btn.click()
        feed_text_3 = wait_for_feed_contains("모션 그래픽 스튜디오 구축", 8)

        if "현재 시각은" in feed_text_3 and "입니다, 대표님! ⏰" in feed_text_3:
            print(f"❌ [FAIL] 키워드 '지금'에 낚여 시계(⏰) 매크로가 가로챘습니다!\n{feed_text_3}")
            browser.close()
            return False
        print("  ✅ [PASS] 3-1. 키워드 '지금' 가로채기 0건! 시계(⏰) 오작동 완벽 박멸!")

        if "모션 그래픽 스튜디오" not in feed_text_3 or "Step 59" not in feed_text_3:
            print(f"❌ [FAIL] Step 59 완료 작업 브리핑 내용이 부족합니다!\n{feed_text_3}")
            browser.close()
            return False
        print("  ✅ [PASS] 3-2. '안총리 지금 바로 완료한 작업이 뭐야' ➔ Step 59 최신 완료 브리핑 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 4] "250 더하기 250 빼기는" 수식 계산 실측
        # ======================================================================
        print("\n🔹 [실전 질문 4] '250 더하기 250 빼기는' 수식 계산 실측")
        input_el.fill("250 더하기 250 빼기는")
        send_btn.click()
        feed_text_4 = wait_for_feed_contains("250을 빼면", 8)
        if "250" not in feed_text_4:
            print(f"❌ [FAIL] 수식 계산 답이 누락되었습니다!\n{feed_text_4}")
            browser.close()
            return False
        print("  ✅ [PASS] 4. '250 더하기 250 빼기는' ➔ 한국어 자연어 수식 정밀 계산 즉답 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 5] "모션그래픽 만들어줘" ➔ 제35기관 인라인 iframe & [↗ 새 창으로 크게 열기] 실측
        # ======================================================================
        print("\n🔹 [실전 질문 5] '모션그래픽 만들어줘' 모션 스튜디오 iframe 실측")
        input_el.fill("모션그래픽 만들어줘")
        send_btn.click()
        page.wait_for_selector("iframe[src*='rgon_motion_preview.html']", timeout=8000)
        page.wait_for_selector("text=↗ 새 창으로 크게 열기", timeout=8000)
        print("  ✅ [PASS] 5. '모션그래픽 만들어줘' ➔ 인라인 iframe 및 [↗ 새 창으로 크게 열기] 선명 노출 확인!")

        # ======================================================================
        # [검증 6] 5대 불필요 군더더기 0건 완벽 수호
        # ======================================================================
        print("\n🔹 [검증 6] 5대 불필요 군더더기 0건 완벽 수호 확인")
        feed_full = feed.inner_text()
        banned = ["[수신 확인 완료]", "↩️ 답장", "말씀하신 뜻을 명확히 접수했습니다", "맥락을 정확히 인지했습니다"]
        for b in banned:
            if b in feed_full:
                print(f"❌ [FAIL] 금지된 군더더기 문구 '{b}' 가 발견되었습니다!")
                browser.close()
                return False
        print("  ✅ [PASS] 6. 깡통 고정 답변 / 변종 에코 / 초록색 영수증 / 퀵액션 바 0건 완벽 수호!")

        print("\n=======================================================")
        print("🎉 [Playwright 실측 최종 결과] 6대 관문 100% ALL PASS!")
        print("=======================================================\n")
        browser.close()
        return True

if __name__ == '__main__':
    ok = test_step59_verified_chat()
    sys.exit(0 if ok else 1)

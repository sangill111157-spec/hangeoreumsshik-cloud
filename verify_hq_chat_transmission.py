#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_hq_chat_transmission.py
================================================================================
청와대 본관 카톡 대화창 (index.html)
Playwright 헤드리스 브라우저 실측 [Step 59 무결점 완결 검증]
1. "현재 시각과 날짜는" -> 실제 날짜·요일·현재 시각(⏰📅) 브리핑
2. "오 더하기 오 는" -> 10 (한글 수사 계산)
3. "이백오십 더하기 오십은" -> 300 (한자어 복합 수사 계산)
4. "안총리가 맏은 임무는" -> 4대 핵심 임무 브리핑
5. "안총리 지금 바로 완료한 작업이 뭐야" -> Step 59 완결 브리핑
6. 3대 깡통 문구("하달해 주신 뜻을...", "말씀하신 뜻을...", "맥락을 정확히...") 0건 완벽 수호
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
    print("\n🚀 [Playwright 브라우저 실측 - Step 59 무결점 완결 실측 검증 가동]")

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

        # ======================================================================
        # [검증 1] "현재 시각과 날짜는" (#ORD-016 적발 건 해결 실측)
        # ➔ 깡통 문구 0건 & 실제 날짜·요일·현재 시각(⏰📅) 브리핑 확인!
        # ======================================================================
        print("\n🔹 [실전 질문 1] '현재 시각과 날짜는' (#ORD-016) 실측")
        input_el.fill("현재 시각과 날짜는")
        send_btn.click()
        feed_text_1 = wait_for_feed_contains("현재 날짜는", 10)

        # 3대 깡통 문구 검출 시 즉시 탈락
        banned_phrases = [
            "하달해 주신 뜻을 최고 우선순위로 접수하여",
            "전술 집행 태세에 돌입했습니다",
            "다음 명령을 바로 집행하겠습니다",
            "말씀하신 뜻을 명확히 접수했습니다",
            "맥락을 정확히 인지했습니다"
        ]
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
        # [검증 2] "오 더하기 오 는" (#ORD-017 적발 건 해결 실측)
        # ➔ 한글 수사 계산기 10 즉답 확인!
        # ======================================================================
        print("\n🔹 [실전 질문 2] '오 더하기 오 는' (#ORD-017) 실측")
        input_el.fill("오 더하기 오 는")
        send_btn.click()
        feed_text_2 = wait_for_feed_contains("10", 10)

        for bp in banned_phrases:
            if bp in feed_text_2:
                print(f"❌ [FAIL] 깡통 문구 '{bp}' 가 검출되었습니다!\n{feed_text_2}")
                browser.close()
                return False

        if "10" not in feed_text_2:
            print(f"❌ [FAIL] '오 더하기 오 는'에 10 계산 결과가 누락되었습니다!\n{feed_text_2}")
            browser.close()
            return False
        print("  ✅ [PASS] 2. '오 더하기 오 는' ➔ 오(5) 더하기 오(5)는 『10』 정밀 계산 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 3] "이백오십 더하기 오십은" (복합 한자어 수사 실측)
        # ➔ 300 즉답 확인!
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
        # [검증 4] "안총리가 맏은 임무는" (회귀 검증)
        # ➔ 조사 잔류('가 맏은') 0건 & 안총리 핵심 임무 브리핑 확인!
        # ======================================================================
        print("\n🔹 [실전 질문 4] '안총리가 맏은 임무는' (회귀 검증)")
        input_el.fill("안총리가 맏은 임무는")
        send_btn.click()
        feed_text_4 = wait_for_feed_contains("핵심 임무", 10)

        if "「가 맏은" in feed_text_4 or "「가 맏은 임무는」" in feed_text_4:
            print(f"❌ [FAIL] 조사 잔류 버그 '「가 맏은 임무는」'이 검출되었습니다!\n{feed_text_4}")
            browser.close()
            return False

        expected_duty = ["코드 주조", "Playwright", "서버", "GitHub SSOT"]
        for ed in expected_duty:
            if ed not in feed_text_4:
                print(f"❌ [FAIL] 안총리 핵심 임무 키워드 '{ed}'가 누락되었습니다!\n{feed_text_4}")
                browser.close()
                return False
        print("  ✅ [PASS] 4. '안총리가 맏은 임무는' ➔ 4대 핵심 임무 명쾌한 브리핑 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 5] "안총리 지금 바로 완료한 작업이 뭐야" (회귀 검증)
        # ➔ 시계 0건 & Step 59 완결 브리핑 확인!
        # ======================================================================
        print("\n🔹 [실전 질문 5] '안총리 지금 바로 완료한 작업이 뭐야' (회귀 검증)")
        input_el.fill("안총리 지금 바로 완료한 작업이 뭐야")
        send_btn.click()
        feed_text_5 = wait_for_feed_contains("모션 그래픽 스튜디오 구축", 10)

        if "현재 시각은" in feed_text_5 and "입니다, 대표님! ⏰" in feed_text_5:
            print(f"❌ [FAIL] 키워드 '지금'에 낚여 시계(⏰) 매크로가 가로챘습니다!\n{feed_text_5}")
            browser.close()
            return False
        if "모션 그래픽 스튜디오" not in feed_text_5 or "Step 59" not in feed_text_5:
            print(f"❌ [FAIL] Step 59 완료 작업 브리핑 내용이 부족합니다!\n{feed_text_5}")
            browser.close()
            return False
        print("  ✅ [PASS] 5. '안총리 지금 바로 완료한 작업이 뭐야' ➔ Step 59 완료 브리핑 확인!")
        time.sleep(1.0)

        # ======================================================================
        # [검증 6] 피드 전체 3대 깡통 문구 0건 완벽 사수 검증
        # ======================================================================
        print("\n🔹 [검증 6] 피드 전체 3대 깡통 문구 0건 완벽 사수 검증")
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
        print("  ✅ [PASS] 6. 3대 깡통 문구 / 초록색 영수증 / 퀵액션 바 0건 완벽 사수!")

        print("\n=======================================================")
        print("🎉 [Playwright 실측 최종 결과] 6대 관문 100% ALL PASS!")
        print("=======================================================\n")
        browser.close()
        return True

if __name__ == '__main__':
    ok = test_step59_verified_chat()
    sys.exit(0 if ok else 1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_hq_chat_transmission.py
================================================================================
청와대 실시간 양방향 소통 사령부 (index.html)
Playwright 실제 헤드리스 Chromium 브라우저 마우스 클릭 & DOM 실측 검증기
================================================================================
검증 항목:
1. 실제 Chromium 브라우저로 index.html 로드
2. 입력창(#comm-input-box)에 "1차 테스트 확인용 지시서 전달 확인 응답 보고" 실제 fill()
3. 전송 버튼(button:has-text("전송")) 실제 마우스 click()
4. 검증 1: input.input_value() == "" (입력창 즉시 비워짐)
5. 검증 2: 대화창 DOM 내부에 "1차 테스트 확인용 지시서 전달 확인 응답 보고" 대표님 말풍선 렌더링 확인
6. 검증 3: 대화창 DOM 내부에 "충성! 이상일 대표님!" 르곤·참모단 맞춤형 응답 확인
7. 검증 4: 대화창 DOM 내부에 "[수신 확인 완료]" 에메랄드 도장 배지 실제 렌더링 확인
8. 검증 5: localStorage('RGON_HQ_CHAT_HISTORY') 영구 기록 확인
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

TEST_PROMPT = "1차 테스트 확인용 지시서 전달 확인 응답 보고"

def test_live_browser_click():
    print("\n🚀 [Playwright 실제 브라우저 실측 검증 가동]")
    print(f"• 테스트 지시 문구: '{TEST_PROMPT}'")

    html_path = os.path.abspath("index.html")
    file_url = f"file:///{html_path.replace(os.sep, '/')}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print(f"• 브라우저 로딩: {file_url}")
        page.goto(file_url, wait_until="networkidle")

        # 1. 입력창 찾기
        input_el = page.locator("#comm-input-box")
        if not input_el.is_visible():
            print("❌ [FAIL] #comm-input-box 요소가 화면에 보이지 않습니다!")
            browser.close()
            return False

        print("• 1단계: 입력창 발견 및 포커스 ➔ 텍스트 fill()")
        input_el.fill(TEST_PROMPT)
        time.sleep(0.1)

        val_before = input_el.input_value()
        if val_before != TEST_PROMPT:
            print(f"❌ [FAIL] 입력창에 텍스트 주입 실패: {val_before}")
            browser.close()
            return False
        print(f"  ✅ 입력창 텍스트 주입 완료: '{val_before}'")

        # 2. 전송 버튼 찾기 및 실제 마우스 클릭
        send_btn = page.locator("#btn-comm-send")
        if not send_btn.is_visible():
            send_btn = page.locator("button:has-text('전송')").first

        print("• 2단계: ⚡ 전송 버튼 실제 마우스 클릭(click()) 집행!")
        send_btn.click()

        # 3. 비동기 DOM 업데이트 대기 (최대 1초)
        time.sleep(0.3)

        # 4. 검증 1: 입력창 비워졌는지 확인
        val_after = input_el.input_value()
        if val_after != "":
            print(f"❌ [FAIL] 전송 후 입력창이 비워지지 않았습니다! 남은 값: '{val_after}'")
            browser.close()
            return False
        print("  ✅ [PASS] 1. 입력창 즉시 초기화 성공: input.value === ''")

        # 5. 검증 2 & 3 & 4: 대화창 내부 텍스트 검증
        feed_el = page.locator("#comm-message-feed")
        feed_text = feed_el.inner_text()

        if TEST_PROMPT not in feed_text:
            print(f"❌ [FAIL] 대화창 내부에 대표님 입력 문구가 없습니다!\n{feed_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 2. 대표님 전용 지시 말풍선 DOM 렌더링 성공 (원문 일치)")

        if "충성! 이상일 대표님!" not in feed_text:
            print(f"❌ [FAIL] 대화창 내부에 르곤·참모단 맞춤형 응답이 없습니다!\n{feed_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 3. 르곤 & 31대 기관 맞춤형 응답 말풍선 렌더링 성공")

        if "[수신 확인 완료]" not in feed_text:
            print(f"❌ [FAIL] 대화창 내부에 [수신 확인 완료] 도장 배지가 없습니다!\n{feed_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 4. 🟢 실시간 에메랄드 수신 확인 도장 배지 렌더링 성공!")

        # 6. 검증 5: localStorage 기록 확인
        storage_history = page.evaluate("() => localStorage.getItem('RGON_HQ_CHAT_HISTORY')")
        if not storage_history or TEST_PROMPT not in storage_history:
            print(f"❌ [FAIL] localStorage에 지시 내용이 기록되지 않았습니다! {storage_history}")
            browser.close()
            return False
        print("  ✅ [PASS] 5. 사령부 원장(localStorage) 영구 보존 성공!")

        browser.close()

    print("\n🏆 [최종 실측 합격] Playwright 실제 브라우저 마우스 클릭 & DOM 실측 100% 무결점 통과!\n")
    return True

if __name__ == '__main__':
    ok = test_live_browser_click()
    sys.exit(0 if ok else 1)

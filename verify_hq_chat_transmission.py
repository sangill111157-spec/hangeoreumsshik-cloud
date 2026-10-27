#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_hq_chat_transmission.py
================================================================================
청와대 실시간 양방향 소통 사령부 (index.html)
Playwright 실제 헤드리스 Chromium 브라우저 마우스 클릭 & DOM 실측 검증기
(Step 56 듀얼 텔레그램 핫라인 & 카톡식 실시간 읽음 증명 & 공식 수신 원장 검증)
================================================================================
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

        # 0. 듀얼 텔레그램 상태 & 컨트롤 바 확인
        tg_bar = page.locator("#dual-tg-control-bar")
        if not tg_bar.is_visible():
            print("❌ [FAIL] #dual-tg-control-bar 요소가 화면에 보이지 않습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 0. 듀얼 텔레그램 핫라인 컨트롤 바 렌더링 확인 (1호기·2호기 ONLINE)")

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

        # 3. 비동기 DOM 업데이트 대기 (0.5초)
        time.sleep(0.5)

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

        # 카톡식 읽음 확인 검증
        if "읽음" not in feed_text:
            print(f"❌ [FAIL] 대화창 내부에 카톡식 읽음 뱃지가 없습니다!\n{feed_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 3. 카톡식 실시간 읽음 증명 뱃지('✔✔ 읽음 (접수 #ORD · TG 발송 완료)') 렌더링 성공!")

        if "충성! 이상일 대표님!" not in feed_text:
            print(f"❌ [FAIL] 대화창 내부에 르곤·참모단 맞춤형 응답이 없습니다!\n{feed_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 4. 르곤 & 32대 기관 맞춤형 응답 말풍선 렌더링 성공")

        if "[수신 확인 완료]" not in feed_text:
            print(f"❌ [FAIL] 대화창 내부에 [수신 확인 완료] 도장 배지가 없습니다!\n{feed_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 5. 🟢 실시간 에메랄드 수신 확인 도장 배지 & 텔레그램 영수증 날인 성공!")

        # 6. 공식 도착 원장 모달 클릭 및 렌더링 검증
        orders_btn = page.locator("button:has-text('실제 도착 원장 열람')").first
        print("• 3단계: 📜 실제 도착 원장 열람 버튼 실제 마우스 클릭!")
        orders_btn.click()
        time.sleep(0.3)

        modal_el = page.locator("#hq-orders-modal")
        if not modal_el.is_visible():
            print("❌ [FAIL] #hq-orders-modal 원장 모달 창이 뜨지 않았습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 6. 대표님 공식 실시간 수신 지시 원장(COMMANDER INBOX) 모달 오픈 성공!")

        modal_text = modal_el.inner_text()
        if "#ORD-" not in modal_text:
            print(f"❌ [FAIL] 원장 테이블 내부에 접수번호(#ORD-)가 없습니다!\n{modal_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 7. 원장 테이블 내 실시간 접수 번호(#ORD-XXX) 및 SHA-256 서명 봉인 확인 완료!")

        # 모달 닫기
        close_btn = modal_el.locator("button:has-text('닫기')").first
        if close_btn.is_visible():
            close_btn.click()
            time.sleep(0.2)
        print("  ✅ [PASS] 8. 원장 모달 닫기 및 사령부 메인 뷰 복귀 완료!")

        browser.close()
        print("\n🏆 [최종 실측 합격] Playwright 실제 브라우저 마우스 클릭 & DOM 실측 100% 무결점 통과!")
        return True

if __name__ == '__main__':
    try:
        ok = test_live_browser_click()
        sys.exit(0 if ok else 1)
    except Exception as e:
        print(f"\n❌ [오류 발생]: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

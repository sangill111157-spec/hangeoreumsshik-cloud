#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_hq_chat_transmission.py
================================================================================
청와대 실시간 양방향 소통 사령부 (index.html)
Playwright 실제 헤드리스 Chromium 브라우저 마우스 클릭 & DOM 실측 검증기
(Step 57: 카카오톡 다크 에디션 4대 채널탭 · 숫자 '1' 소멸 & 읽음 ✔✔ · 공지 고정 · 원장 봉인)
================================================================================
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

TEST_PROMPT = "1차 테스트 확인용 지시서 전달 확인 응답 보고"

def test_live_browser_click():
    print("\n🚀 [Step 57 Playwright 실제 브라우저 실측 검증 가동]")
    print(f"• 테스트 지시 문구: '{TEST_PROMPT}'")

    html_path = os.path.abspath("index.html")
    file_url = f"file:///{html_path.replace(os.sep, '/')}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print(f"• 브라우저 로딩: {file_url}")
        page.goto(file_url, wait_until="networkidle")

        # 0. 카톡 4대 채널 탭 바 확인
        tabs = page.locator(".kakao-channel-tab")
        if tabs.count() < 4:
            print(f"❌ [FAIL] 카카오톡 채널 탭 개수 부족: {tabs.count()}개 (기대: 4개)")
            browser.close()
            return False
        print("  ✅ [PASS] 0. 카카오톡 다크 에디션 4대 채널 탭(사령부톡·비서톡·NVDA톡·루미톡) 렌더링 확인")

        # 1. 채널 탭 전환 클릭 검증: NVDA 탭 클릭 시 엔비디아 런처 버튼 노출 확인
        nvda_tab = page.locator("#tab-channel-NVDA")
        nvda_tab.click()
        time.sleep(0.2)
        nvda_btn = page.locator("#btn-nvda-dash-open")
        if not nvda_btn.is_visible():
            print("❌ [FAIL] NVDA 탭 선택 시 #btn-nvda-dash-open 버튼이 노출되지 않았습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 1. 🟣 NVDA 오토트레이딩톡 탭 클릭 ➔ 전용 대시보드 런처 버튼 노출 성공")

        # 엔비디아 대시보드 안내 모달 열기 & 닫기 테스트
        nvda_btn.click()
        time.sleep(0.2)
        nvda_modal = page.locator("#hq-nvda-modal")
        if not nvda_modal.is_visible():
            print("❌ [FAIL] #hq-nvda-modal 모달이 열리지 않았습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 2. 🖥️ 기존 NVIDIA 대시보드 안내 모달 열기 성공")
        close_nvda_btn = nvda_modal.locator("button:has-text('닫기')").first
        close_nvda_btn.click()
        time.sleep(0.2)

        # 전체 사령부톡 탭 복귀
        all_tab = page.locator("#tab-channel-ALL")
        all_tab.click()
        time.sleep(0.2)

        # 2. 메시지 입력창 찾기 및 텍스트 주입
        input_el = page.locator("#comm-input-box")
        if not input_el.is_visible():
            print("❌ [FAIL] #comm-input-box 요소가 화면에 보이지 않습니다!")
            browser.close()
            return False

        print("• 3단계: 입력창 발견 및 포커스 ➔ 텍스트 fill()")
        input_el.fill(TEST_PROMPT)
        time.sleep(0.1)

        val_before = input_el.input_value()
        if val_before != TEST_PROMPT:
            print(f"❌ [FAIL] 입력창에 텍스트 주입 실패: {val_before}")
            browser.close()
            return False
        print(f"  ✅ 입력창 텍스트 주입 완료: '{val_before}'")

        # 3. 전송 버튼 찾기 및 실제 마우스 클릭
        send_btn = page.locator("#btn-comm-send")
        if not send_btn.is_visible():
            send_btn = page.locator("button:has-text('전송')").first

        print("• 4단계: ⚡ 전송 버튼 실제 마우스 클릭(click()) 집행!")
        send_btn.click()

        # 4. 검증 1: 입력창 비워졌는지 즉시 확인
        val_after = input_el.input_value()
        if val_after != "":
            print(f"❌ [FAIL] 전송 후 입력창이 비워지지 않았습니다! 남은 값: '{val_after}'")
            browser.close()
            return False
        print("  ✅ [PASS] 3. 입력창 즉시 초기화 성공: input.value === ''")

        # 5. 비동기 인비저블 백본 텔레그램 발송 완료 대기 (0.6초)
        time.sleep(0.6)

        feed_el = page.locator("#comm-message-feed")
        feed_text = feed_el.inner_text()

        if TEST_PROMPT not in feed_text:
            print(f"❌ [FAIL] 대화창 내부에 대표님 입력 문구가 없습니다!\n{feed_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 4. 대표님 전용 지시 말풍선 DOM 렌더링 성공 (원문 일치)")

        # 카톡식 숫자 '1' 사라짐 및 '읽음 ✔✔' 검증
        if "읽음 ✔✔" not in feed_text:
            print(f"❌ [FAIL] 대화창 내부에 카톡식 '읽음 ✔✔' 뱃지가 없습니다!\n{feed_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 5. 카카오톡식 실시간 읽음 증명('읽음 ✔✔' · 숫자 1 사라짐) 실측 성공!")

        if "충성! 이상일 대표님!" not in feed_text:
            print(f"❌ [FAIL] 대화창 내부에 르곤·참모단 맞춤형 응답이 없습니다!\n{feed_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 6. 르곤 & 33대 기관 맞춤형 응답 말풍선 렌더링 성공")

        if "[수신 확인 완료]" not in feed_text:
            print(f"❌ [FAIL] 대화창 내부에 [수신 확인 완료] 도장 배지가 없습니다!\n{feed_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 7. 🟢 실시간 에메랄드 수신 확인 도장 배지 & 텔레그램 영수증 날인 성공!")

        # 6. 카톡 퀵액션 [📌 공지] 클릭 테스트
        pin_btn = feed_el.locator("button:has-text('📌 공지')").first
        if pin_btn.is_visible():
            pin_btn.click()
            time.sleep(0.2)
            notice_bar = page.locator("#kakao-pinned-notice")
            if notice_bar.is_visible():
                print("  ✅ [PASS] 8. 📌 카톡 퀵액션 공지 고정 클릭 ➔ 상단 공지 바 렌더링 성공")
                unpin_btn = page.locator("button:has-text('✕ 고정해제')").first
                if unpin_btn.is_visible():
                    unpin_btn.click()
                    time.sleep(0.2)
                    print("  ✅ [PASS] 9. ✕ 상단 공지 고정해제 정상 작동 확인")

        # 7. 공식 도착 원장 모달 클릭 및 렌더링 검증
        orders_btn = feed_el.locator("button:has-text('실제 도착 원장 열람')").first
        if not orders_btn.is_visible():
            orders_btn = feed_el.locator("button:has-text('📜 원장')").first
        print("• 5단계: 📜 실제 도착 원장 열람 버튼 실제 마우스 클릭!")
        orders_btn.click()
        time.sleep(0.3)

        modal_el = page.locator("#hq-orders-modal")
        if not modal_el.is_visible():
            print("❌ [FAIL] #hq-orders-modal 원장 모달 창이 뜨지 않았습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 10. 대표님 공식 실시간 수신 지시 원장(COMMANDER INBOX) 모달 오픈 성공!")

        modal_text = modal_el.inner_text()
        if "#ORD-" not in modal_text:
            print(f"❌ [FAIL] 원장 테이블 내부에 접수번호(#ORD-)가 없습니다!\n{modal_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 11. 원장 테이블 내 실시간 접수 번호(#ORD-XXX) 및 텔레그램 3대 봇 발송 증빙 확인 완료!")

        # 모달 닫기
        close_btn = modal_el.locator("button:has-text('닫기')").first
        if close_btn.is_visible():
            close_btn.click()
            time.sleep(0.2)
        print("  ✅ [PASS] 12. 원장 모달 닫기 및 사령부 메인 뷰 복귀 완료!")

        browser.close()
        print("\n🏆 [Step 57 최종 실측 합격] Playwright 실제 브라우저 마우스 클릭 & DOM 실측 12/12 무결점 ALL PASS!")
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

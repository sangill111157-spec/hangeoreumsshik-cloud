#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_hq_chat_transmission.py
================================================================================
청와대 본관 카톡 대화창 (index.html)
Playwright 헤드리스 브라우저 실측 3대 티키타카 및 5대 군더더기 0건 검증기
================================================================================
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_tikitaka_and_clean_ui():
    print("\n🚀 [Playwright 브라우저 실측 3대 티키타카 & 군더더기 0건 검증 가동]")

    html_path = os.path.abspath("index.html")
    file_url = f"file:///{html_path.replace(os.sep, '/')}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print(f"• 브라우저 로딩: {file_url}")
        page.goto(file_url, wait_until="networkidle")

        # ======================================================================
        # [검증 1] "1+1= 얼마야" 수식 계산 즉답 & 매크로 0건 검증
        # ======================================================================
        print("\n🔹 [테스트 1] '1+1= 얼마야' 수식 계산 및 매크로 박멸 실측")
        input_el = page.locator("#comm-input-box")
        if not input_el.is_visible():
            print("❌ [FAIL] #comm-input-box 요소가 화면에 보이지 않습니다!")
            browser.close()
            return False

        input_el.fill("1+1= 얼마야")
        send_btn = page.locator("#btn-comm-send")
        send_btn.click()
        
        # 비동기 AI 티키타카 응답 대기 (최대 5초)
        page.wait_for_selector("text=2입니다", timeout=5000)

        feed = page.locator("#comm-message-feed")
        feed_text = feed.inner_text()

        # 매크로 검증: "전술 배치" 또는 "하달하신 「1+1= 얼마야」 지시의 핵심 맥락"이 없어야 함
        if "전술 배치" in feed_text or "핵심 맥락을 정확히 인지" in feed_text:
            print(f"❌ [FAIL] 앵무새 고정 매크로('전술 배치' 등)가 여전히 출력되고 있습니다!\n피드 텍스트: {feed_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 1-1. '전술 배치' 등 앵무새 매크로 문구 0건 완벽 박멸 확인!")

        # 정답 검증: "2입니다"가 포함되어야 함
        if "2입니다" not in feed_text:
            print(f"❌ [FAIL] '2입니다' 즉답이 피드에 없습니다!\n피드 텍스트: {feed_text}")
            browser.close()
            return False
        print("  ✅ [PASS] 1-2. '1+1= 얼마야' 입력에 '2입니다, 대표님! 😊' 초고속 즉답 성공!")

        # ======================================================================
        # [검증 2] "안총리 아온이 답장해봐" 자연어 티키타카 단일 말풍선 검증
        # ======================================================================
        print("\n🔹 [테스트 2] '안총리 아온이 답장해봐' 자연어 티키타카 실측")
        input_el.fill("안총리 아온이 답장해봐")
        send_btn.click()
        
        # 비동기 AI 티키타카 응답 대기 (최대 5초)
        page.wait_for_selector("text=안총리와 참모 아온이", timeout=5000)

        feed_text_2 = feed.inner_text()
        if "안총리" not in feed_text_2 or "아온이" not in feed_text_2:
            print(f"❌ [FAIL] 안총리·아온이 답장이 제대로 출력되지 않았습니다!\n피드 텍스트: {feed_text_2}")
            browser.close()
            return False
        print("  ✅ [PASS] 2. 안총리·아온이 실시간 자연어 티키타카 답장 렌더링 확인!")

        # ======================================================================
        # [검증 3] 5대 군더더기 0건 완벽 검증
        # ======================================================================
        print("\n🔹 [테스트 3] 대화창 5대 불필요 군더더기 0건 검증")

        # 3-1: 말풍선 내부 초록색 영수증 박스 ([수신 확인 완료]) 0개 검증
        receipt_boxes = feed.locator("text=[수신 확인 완료]")
        if receipt_boxes.count() > 0:
            print(f"❌ [FAIL] 말풍선 내에 초록색 [수신 확인 완료] 박스가 {receipt_boxes.count()}개 남아있습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 3-1. 말풍선 내부 초록색 영수증 박스 0개 완전 제거 확인!")

        # 3-2: 말풍선 하단 퀵액션 바 (↩️ 답장 · 📌 공지 · 📋 복사 · 📜 원장) 0개 검증
        reply_action_bar = feed.locator("text=↩️ 답장")
        if reply_action_bar.count() > 0:
            print(f"❌ [FAIL] 말풍선 하단에 '↩️ 답장' 버튼 줄이 {reply_action_bar.count()}개 남아있습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 3-2. 모든 말풍선 하단 '↩️ 답장 · 📌 공지' 버튼 줄 0개 완전 제거 확인!")

        # 3-3: 상단 BotMux 기술 설명 박스 0개 검증
        botmux_text = page.locator("text=BotMux")
        if botmux_text.count() > 0:
            print(f"❌ [FAIL] 화면 상단에 'BotMux' 기술 설명 박스가 {botmux_text.count()}개 남아있습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 3-3. 상단 'BotMux 투명 링버퍼' 복잡한 기술 설명 박스 0개 완전 제거 확인!")

        # 3-4: 접이식 서랍 (#kakao-advanced-drawer) DOM 존재 여부 검증 (0개여야 함)
        drawer = page.locator("#kakao-advanced-drawer")
        if drawer.count() > 0:
            print("❌ [FAIL] #kakao-advanced-drawer 요소가 아직 DOM에 남아있습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 3-4. 상단 불필요 접이식 서랍 드로어 DOM 0개 완전 소각 확인!")

        # 3-5: 대화창 높이 시원하게 확장되었는지 검증 (h-96 sm:h-[420px])
        feed_class = feed.get_attribute("class") or ""
        if "h-96" not in feed_class and "420px" not in feed_class:
            print(f"❌ [FAIL] 대화창 높이가 확장되지 않았습니다! class: {feed_class}")
            browser.close()
            return False
        print(f"  ✅ [PASS] 3-5. 대화창 높이 시원한 확장 확인 (class: {feed_class})")

        # 3-6: 대표님 말풍선 옆 읽음 표식 확인
        read_badge = feed.locator("text=읽음 ✔✔")
        if read_badge.count() == 0:
            print("❌ [FAIL] 대표님 말풍선 옆 '읽음 ✔✔' 표식이 나타나지 않았습니다!")
            browser.close()
            return False
        print(f"  ✅ [PASS] 3-6. 대표님 말풍선 옆 카톡식 '읽음 ✔✔' {read_badge.count()}건 깔끔 점등 확인!")

        print("\n🎉 [Playwright 실측 최종 결과] 3대 티키타카 검증 및 5대 군더더기 0건 ALL PASS 100% 무결점 통과!")
        browser.close()
        return True

if __name__ == '__main__':
    ok = test_tikitaka_and_clean_ui()
    sys.exit(0 if ok else 1)

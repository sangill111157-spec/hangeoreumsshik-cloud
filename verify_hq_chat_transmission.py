#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_hq_chat_transmission.py
================================================================================
청와대 본관 카톡 대화창 (index.html)
Playwright 헤드리스 브라우저 실측 [Step 58] 6대 멀티모달 & 실시간 작업 기억 티키타카 검증기
================================================================================
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_step58_multimodal_and_live_context():
    print("\n🚀 [Playwright 브라우저 실측 Step 58 멀티모달 & 작업기억 티키타카 검증 가동]")

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

        # ======================================================================
        # [검증 1] "2+2=" 수식 계산 즉답 실측
        # ======================================================================
        print("\n🔹 [테스트 1] '2+2=' 수식 계산 즉답 실측")
        input_el.fill("2+2=")
        send_btn.click()
        page.wait_for_selector("text=4입니다", timeout=5000)
        feed_text_1 = feed.inner_text()
        if "4입니다" not in feed_text_1:
            print(f"❌ [FAIL] '4입니다' 즉답이 없습니다!\n{feed_text_1}")
            browser.close()
            return False
        print("  ✅ [PASS] 1. '2+2=' 입력 ➔ '4입니다, 대표님! 😊' 즉답 확인!")

        # ======================================================================
        # [검증 2] "안실장 아온아 지금 우리가 뭘 하고 있지 답장줘" 호칭 가로채기 0% 면역 & 작업 기억 브리핑 검증
        # ======================================================================
        print("\n🔹 [테스트 2] '안실장 아온아 지금 우리가 뭘 하고 있지 답장줘' 실시간 작업 기억 브리핑 실측")
        input_el.fill("안실장 아온아 지금 우리가 뭘 하고 있지 답장줘")
        send_btn.click()
        page.wait_for_selector("text=멀티모달 만능 소통", timeout=6000)
        feed_text_2 = feed.inner_text()

        # 1) 단순 대기 인사가 아니어야 함
        if "바로 여기 대기 중입니다! 거추장스러운 의전 인사말 빼고" in feed_text_2:
            print(f"❌ [FAIL] 호칭 가로채기 버그 발생! 단순 대기 인사말이 출력되었습니다!\n{feed_text_2}")
            browser.close()
            return False
        print("  ✅ [PASS] 2-1. 호칭 가로채기(Short-Circuit) 버그 0% 완전 면역 확인!")

        # 2) 실제 작업 브리핑 내용 포함 확인
        expected_keywords = ["소통 사령부", "멀티모달", "v11.57", "34대 기관", "시냅스 100.0점"]
        for kw in expected_keywords:
            if kw not in feed_text_2:
                print(f"❌ [FAIL] 작업 브리핑에 필수 키워드 '{kw}'가 누락되었습니다!\n{feed_text_2}")
                browser.close()
                return False
        print("  ✅ [PASS] 2-2. 현재 사령부 작업 상태 실시간 실측 브리핑 성공!")

        # ======================================================================
        # [검증 3] 유튜브 URL 인라인 플레이어 카드 렌더링 검증
        # ======================================================================
        print("\n🔹 [테스트 3] 유튜브 URL 인라인 플레이어 카드 실측")
        input_el.fill("이 영상 봐봐 https://youtu.be/d-WRGKllOKU 멋져")
        send_btn.click()
        page.wait_for_selector("iframe[src*='d-WRGKllOKU']", timeout=5000)
        print("  ✅ [PASS] 3. 유튜브 URL 전송 ➔ 인라인 iframe 플레이어 카드 렌더링 확인!")

        # ======================================================================
        # [검증 4] 일반 웹 URL 스마트 프리뷰 카드 렌더링 검증
        # ======================================================================
        print("\n🔹 [테스트 4] 웹 URL 스마트 링크 프리뷰 카드 실측")
        input_el.fill("파이프캣 깃허브 https://github.com/pipecat-ai/pipecat 살펴봐")
        send_btn.click()
        page.wait_for_selector("text=github.com 스마트 링크 프리뷰", timeout=5000)
        print("  ✅ [PASS] 4. 일반 웹 URL 전송 ➔ 도메인 자동 파싱 스마트 프리뷰 카드 렌더링 확인!")

        # ======================================================================
        # [검증 5] 텔레파시 추천 질문 칩 3개 및 액션 버튼(📎, 🎙️) 실측
        # ======================================================================
        print("\n🔹 [테스트 5] 텔레파시 추천 칩 3개 및 멀티모달 액션 버튼 실측")
        chips = page.locator("#pinnacle-smart-chips button")
        if chips.count() < 3:
            print(f"❌ [FAIL] 텔레파시 추천 칩 개수 부족: {chips.count()}개 (기대: 3개)")
            browser.close()
            return False
        print(f"  ✅ [PASS] 5-1. 텔레파시 원터치 추천 질문 칩 {chips.count()}개 렌더링 확인!")

        # 첫 번째 칩(작업 현황 브리핑) 클릭 테스트
        chips.first.click()
        page.wait_for_selector("text=제34기관 멀티모달", timeout=5000)
        print("  ✅ [PASS] 5-2. 텔레파시 칩 원터치 클릭 ➔ 실시간 브리핑 즉답 확인!")

        attach_btn = page.locator("#btn-comm-attach")
        mic_btn = page.locator("#btn-comm-mic")
        if not attach_btn.is_visible() or not mic_btn.is_visible():
            print("❌ [FAIL] 📎 첨부 버튼 또는 🎙️ 음성 버튼이 보이지 않습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 5-3. 멀티모달 파일첨부(📎) 및 음성인식(🎙️) 액션 버튼 정상 노출 확인!")

        # ======================================================================
        # [검증 6] 5대 불필요 군더더기 0건 완벽 수호 검증
        # ======================================================================
        print("\n🔹 [테스트 6] 5대 불필요 군더더기 0건 완벽 수호 검증")
        feed_full = feed.inner_text()

        # 1) 초록색 영수증 박스 0개
        if "[수신 확인 완료]" in feed_full:
            print("❌ [FAIL] 말풍선 안에 초록색 영수증 박스가 남아있습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 6-1. 초록색 영수증 박스 0개 완전 제거 유지!")

        # 2) ↩️ 답장 줄 0개
        if "↩️ 답장" in feed_full:
            print("❌ [FAIL] 말풍선 하단에 '↩️ 답장' 버튼 줄이 남아있습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 6-2. 말풍선 하단 '↩️ 답장' 줄 0개 완전 제거 유지!")

        # 3) 상단 BotMux 기술 설명 박스 0개
        if page.locator("text=BotMux").count() > 0:
            print("❌ [FAIL] 상단 BotMux 기술 설명 박스가 아직 남아있습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 6-3. 상단 BotMux 복잡한 기술 설명 박스 0개 완전 제거 유지!")

        # 4) 접이식 서랍 0개
        if page.locator("#kakao-advanced-drawer").count() > 0:
            print("❌ [FAIL] #kakao-advanced-drawer 요소가 아직 DOM에 남아있습니다!")
            browser.close()
            return False
        print("  ✅ [PASS] 6-4. 상단 불필요 서랍 DOM 0개 완전 소각 유지!")

        print("\n🎉 [Playwright 실측 최종 결과] Step 58 멀티모달 & 실시간 작업기억 티키타카 ALL PASS 100% 무결점 통과!")
        browser.close()
        return True

if __name__ == '__main__':
    ok = test_step58_multimodal_and_live_context()
    sys.exit(0 if ok else 1)

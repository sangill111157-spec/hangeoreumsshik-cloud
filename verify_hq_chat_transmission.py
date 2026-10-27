#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_hq_chat_transmission.py
================================================================================
청와대 본관 카톡 대화창 (index.html)
Playwright 헤드리스 브라우저 실측 [Step 59] 
실제 AI 두뇌 & 한국어 자연어 수식 & 오타 추론 & 오퍼스 5.5 모션 스튜디오 검증기
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

def test_step59_live_brain_and_opus_motion():
    print("\n🚀 [Playwright 브라우저 실측 Step 59 실제 AI 두뇌 & 오퍼스 5.5 모션 스튜디오 검증 가동]")

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
        # [검증 1] "250 더하기 250 더하기 250 빼기는" 한국어 수식 정밀 계산 실측
        # ======================================================================
        print("\n🔹 [테스트 1] '250 더하기 250 더하기 250 빼기는' 한국어 수식 계산 즉답 실측")
        input_el.fill("250 더하기 250 더하기 250 빼기는")
        send_btn.click()
        page.wait_for_selector("text=750", timeout=5000)
        feed_text_1 = feed.inner_text()
        if "750" not in feed_text_1 or "250" not in feed_text_1:
            print(f"❌ [FAIL] '750' 및 '250' 계산 답이 누락되었습니다!\n{feed_text_1}")
            browser.close()
            return False
        print("  ✅ [PASS] 1. '250 더하기 250 더하기 250 빼기는' ➔ 750 및 250 정밀 계산 즉답 확인!")

        # ======================================================================
        # [검증 2] "안총리 우리가 현재 어떻거 만들고 있지" 오타 포함 현재 작업 브리핑 실측
        # ======================================================================
        print("\n🔹 [테스트 2] '안총리 우리가 현재 어떻거 만들고 있지' 오타 포함 작업 브리핑 실측")
        input_el.fill("안총리 우리가 현재 어떻거 만들고 있지")
        send_btn.click()
        page.wait_for_selector("text=모션 그래픽 스튜디오", timeout=6000)
        feed_text_2 = feed.inner_text()

        # 1) 깡통 고정 답변 0건 확인
        if "말씀하신 뜻을 명확히 접수했습니다" in feed_text_2:
            print(f"❌ [FAIL] 깡통 고정 문구가 출력되었습니다!\n{feed_text_2}")
            browser.close()
            return False
        print("  ✅ [PASS] 2-1. 깡통 고정 문구 0건 완전 박멸 확인!")

        # 2) 실제 작업 브리핑 내용 확인
        expected_keywords = ["소통 사령부", "모션 그래픽 스튜디오", "v11.58", "35대 기관", "55스킬"]
        for kw in expected_keywords:
            if kw not in feed_text_2:
                print(f"❌ [FAIL] 작업 브리핑에 필수 키워드 '{kw}'가 누락되었습니다!\n{feed_text_2}")
                browser.close()
                return False
        print("  ✅ [PASS] 2-2. 오타('어떻거')에도 불구하고 최신 Step 59 작업 상태 실시간 브리핑 성공!")

        # ======================================================================
        # [검증 3] "안총리 아온이 너희들은 누구니" 정체성 답변 실측
        # ======================================================================
        print("\n🔹 [테스트 3] '안총리 아온이 너희들은 누구니' 정체성 답변 실측")
        input_el.fill("안총리 아온이 너희들은 누구니")
        send_btn.click()
        page.wait_for_selector("text=기술총리 안총리와", timeout=5000)
        feed_text_3 = feed.inner_text()
        if "안총리" not in feed_text_3 or "아온이" not in feed_text_3:
            print(f"❌ [FAIL] 정체성 답변이 누락되었습니다!\n{feed_text_3}")
            browser.close()
            return False
        print("  ✅ [PASS] 3. '안총리 아온이 너희들은 누구니' ➔ 정체성 및 소명 답변 확인!")

        # ======================================================================
        # [검증 4] "모션그래픽 만들어줘" ➔ 제35기관 인라인 iframe 렌더링 실측
        # ======================================================================
        print("\n🔹 [테스트 4] '모션그래픽 만들어줘' 모션 스튜디오 iframe 실측")
        input_el.fill("모션그래픽 만들어줘")
        send_btn.click()
        page.wait_for_selector("iframe[src*='rgon_motion_preview.html']", timeout=6000)
        print("  ✅ [PASS] 4. '모션그래픽 만들어줘' ➔ 인라인 모션 그래픽 스튜디오(iframe) 렌더링 확인!")

        # ======================================================================
        # [검증 5] 텔레파시 칩 중 '🎬 오퍼스 모션그래픽' 클릭 실측
        # ======================================================================
        print("\n🔹 [테스트 5] 텔레파시 칩 '🎬 오퍼스 모션그래픽' 클릭 실측")
        opus_chip = page.locator("#pinnacle-smart-chips button:has-text('오퍼스 모션그래픽')")
        if not opus_chip.is_visible():
            print("❌ [FAIL] '🎬 오퍼스 모션그래픽' 스마트 칩이 보이지 않습니다!")
            browser.close()
            return False
        opus_chip.click()
        page.wait_for_selector("iframe[src*='rgon_motion_preview.html']", timeout=6000)
        print("  ✅ [PASS] 5. 텔레파시 칩 원터치 클릭 ➔ 모션 그래픽 스튜디오 직결 확인!")

        # ======================================================================
        # [검증 6] 5대 불필요 군더더기 0건 완벽 수호 검증
        # ======================================================================
        print("\n🔹 [테스트 6] 5대 불필요 군더더기 0건 완벽 수호 검증")
        feed_full = feed.inner_text()

        forbidden_patterns = [
            ("초록색 영수증 박스", "[수신 확인 완료]"),
            ("BotMux 설명 박스", "텔레그램 봇 자동 라우팅 시스템"),
            ("↩️ 답장 바", "↩️ 답장"),
            ("하단 독 도구함", "도구함"),
            ("깡통 고정 문구", "말씀하신 뜻을 명확히 접수했습니다")
        ]

        for label, pat in forbidden_patterns:
            if pat in feed_full:
                print(f"❌ [FAIL] 군더더기 '{label}' ({pat})가 발견되었습니다!\n{feed_full}")
                browser.close()
                return False
            print(f"  ✅ [PASS] 군더더기 0건 수호: '{label}' 미노출 확인!")

        # ======================================================================
        # [스크린샷 캡처 보존]
        # ======================================================================
        os.makedirs("artifacts", exist_ok=True)
        screenshot_path = "artifacts/step59_verified_chat.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n📸 [실측 영수증] 전체 화면 캡처 저장 완료: {screenshot_path}")

        browser.close()

    print("\n🎉 =======================================================")
    print("🌟 [Step 59 Playwright 브라우저 실측 6대 검증 관문 100% ALL PASS!]")
    print("• 한국어 자연어 수식 즉답: 100% PASS")
    print("• 오타('어떻거') 포함 작업기억 브리핑: 100% PASS")
    print("• 정체성 티키타카: 100% PASS")
    print("• 오퍼스 5.5 모션 스튜디오 iframe 직결: 100% PASS")
    print("• 텔레파시 스마트 칩 연동: 100% PASS")
    print("• 5대 군더더기 및 깡통 고정 답변: 0건 완전 박멸!")
    print("=======================================================\n")
    return True

if __name__ == "__main__":
    success = test_step59_live_brain_and_opus_motion()
    sys.exit(0 if success else 1)

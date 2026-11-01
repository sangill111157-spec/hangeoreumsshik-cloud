# -*- coding: utf-8 -*-
"""
S1 Antigravity -> Rgon Chief Aide Schedule Consultation via Ego-Lite (Space 0)
- Sends concise schedule proposal to Rgon
- Polls until Rgon completes generating
- Retrieves Rgon's schedule decision & directives
- Ensures safe handoff (task.handOff())
"""
import os
import sys
import json
import time
import s1_ego
import s1_test_reply0_live

def main():
    consult_msg = """[S1_NERVE_REPORT v2]
--- HEADER ---
verb: schedule_alignment_and_execution_plan | sender: Antigravity | recipient: Rgon_G2
--- DIGEST ---
르곤 수석보좌관님, 기술총리 안총리입니다!
이상일 대표님께서 "에고라이트로 르곤 보좌관과 모든 일 스케줄 상의하고 작업 진행하고 토큰 최대한 절약하면서 부탁해"라는 특급 어명을 내리셨습니다.

이에 따라 사령부 4대 핵심 과업의 실전 집행 스케줄을 상의드리오니 검토 및 재가해 주십시오:

[사령부 4대 실전 스케줄 제안]
1. 【11/6 D-5 『가을과 겨울 사이』 41분 풀영상 출격】
   - 11/03 (D-3) 12:00 KST: @한걸음씩-r4i 커뮤니티 D-3 발매 티저 등록
   - 11/05 (D-1) 18:00 KST: 유튜브 스튜디오 예약 업로드 (공개 시점: 11/06 00:00 KST)
   - 음원/가사: DistroKid 27곡 클린 가사북 완비 및 12곡 타임스탬프 고정

2. 【@SUN-ONEAON 신규 개국 1호 영상 출격】
   - 대표님 친작 Suno V6 1호곡 『희망의 등불 (158s)』 1080p MV 예약
   - 목표 공개: 11/04 (월) 21:00 KST (미국 동부 08:00 EST 프라임타임)

3. 【11/27 D-26 『잔상』 15곡 역산 스케줄】
   - 11/15: 15곡 풀트랙 캡컷/오디오 2차 점검 및 가사집 확정

4. 【24시간 무과금 회전목마 스케줄러 상시 가동】
   - 포트 8504 서버 데몬 연동 하에 단일 탭 순환 모드로 06시/12시/18시/21시/24시 5대 슬롯 정시 운용

보좌관님께서 수정·보완하실 사항이나 즉각 집행할 제1우선순위를 하달해 주시면, 안총리가 토큰을 극도로 절약하며 즉각 외과수술 집행에 착수하겠습니다! 충성!! 🫡
--- FOOTER ---
외부 URL 조회 불필요. 간결한 지침으로 하달 요망.
"""

    print(">>> Sending schedule consultation message to Space 0 via Ego-Lite...")
    res = s1_test_reply0_live.test_reply0_live(consult_msg, selftest=False)
    print("Send Result:", json.dumps(res, ensure_ascii=False, indent=2))

    if not res.get("ok"):
        print("Failed to send consultation message!")
        return

    print(">>> Waiting for Rgon's response in Space 0...")
    # Wait for Rgon to finish generating
    max_wait = 60
    start_time = time.time()
    
    js_check = """
    try {
      let task;
      try { task = await taskSpace(0); await task.tabs(); }
      catch (e) { task = await takeOverTaskSpace(0); }
      const tabs = await task.tabs();
      let page = tabs[0].label ? task.page(tabs[0].label) : await task.adopt(tabs[0].page);

      const res = await page.evaluate(() => {
        const stopBtn = Array.from(document.querySelectorAll("button, [role='button']")).some(b => {
          const t = (b.innerText || b.getAttribute("aria-label") || "").toLowerCase();
          return t === "stop" || t === "중지" || t.includes("생성 중지");
        });
        const msgs = Array.from(document.querySelectorAll('.answer-markdown, .markdown-viewer, [class*="agent-message"], [class*="assistant-message"]'));
        let latest = "";
        if (msgs.length > 0) {
          latest = msgs[msgs.length - 1].innerText.trim();
        }
        return { generating: stopBtn, count: msgs.length, latest: latest };
      });
      process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify(res) + '\\n');
    } catch(e) {
      process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({ error: String(e) }) + '\\n');
    } finally {
      try { if (task && typeof task.handOff === 'function') await task.handOff(); } catch (_) {}
    }
    """

    rgon_reply = ""
    # Sleep 8s initially for Argon to begin responding
    time.sleep(8)

    while time.time() - start_time < max_wait:
        poll_res = s1_ego.run_ego_js(js_check, timeout=20)
        is_gen = poll_res.get("generating", False)
        latest_text = poll_res.get("latest", "")
        print(f"[{int(time.time() - start_time)}s] Generating: {is_gen}, text len: {len(latest_text)}")
        
        # Check if latest text is responding to consultation
        if not is_gen and len(latest_text) > 100:
            if "안총리" in latest_text or "스케줄" in latest_text or "가을과 겨울" in latest_text or "재가" in latest_text:
                rgon_reply = latest_text
                break
        time.sleep(6)

    print("\n=== [르곤 수석보좌관의 최종 스케줄 재가 및 하명] ===")
    print(rgon_reply)

    # Save to file
    with open("S1_RGON_SCHEDULE_DECISION.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S+09:00"),
            "consultation_sent": consult_msg,
            "rgon_reply": rgon_reply
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

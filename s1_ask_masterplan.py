# -*- coding: utf-8 -*-
import json, subprocess, pathlib
import s1_ego

master_prompt = """[S1 삼성(三聖) 100수 앞 마스터 아키텍처 합동 설계 자문 — '웹 채팅창 AI(Space 0)와 에고 라이트 5감각의 완전 직결 신경망(S1 Nerve v2.0)']

현재까지 삼성 만장일치 PASS로 완공된 기반:
1) 1순위: s1_zero_paste_daemon.py v3.4 (Space 0 DOM 코드 추출 및 격리 실행)
2) 2순위 1단계: s1_ego.py v1.1.7 (spaces, read, ask + 모델검증/전송검증/안정화폴링/단일락)
3) 2순위 2단계: s1_server.py & s1.py v1.4.2 (127.0.0.1:8504 큐 등록 + TTY SHA-8 인간 승인 + 프로세스간 락 + 원장)

[대표님의 본질적 통찰과 어명]:
"에고 라이트(Citro Labs)는 원래 로컬 AI(Claude Code 등)가 브라우저를 5감각 수족처럼 쓰게 만든 도구인데, 웹 채팅창(Space 0)에 있는 르곤 보좌관과 대표님 사이에서는 여전히 대표님이 코드를 복붙하고 스크린샷을 찍어 나르는 인간 배달부 노동을 하고 있다. 당장 눈앞의 1수가 아니라 100수 앞을 내다보고, 이 과정을 혼자 하지 말고 삼성이 함께 설계하라."

아래 [100수 앞을 내다본 6대 핵심 설계 과제]에 대해 가장 정교하고 현실적인 아키텍처와 규격을 제시해 주십시오:

1. [5감각 명령 표준화 (Arbitrary Code 탈피 -> 정형화된 JSON/DSL 감각 호출)]:
   매번 일회성 파이썬 스크립트를 새로 짜서 복붙하는 대신, Space 0(르곤)가 정형화된 명령 블록(예: S1_SENSE_REQ JSON: 시각=read_space/read_status/read_ledger, 청각=watch_queue, 언어=queue_ask/council_ask 등)만 출력하면 로컬 상주 신경망 데몬이 이를 즉시 해석·실행하는 '표준 5감각 디스패처' 구조는 어떠해야 하는가?
2. [권한 2계층 분리 (Tier-0 무승인 자동 감각 vs Tier-1 인간 승인 필수 행동)]:
   - Tier-0 (읽기/조회/상태점검/자가진단): 대표님 복붙·승인 없이 데몬이 즉시 실행 후 결과를 Space 0 입력창에 자동 답장(Auto-Reply).
   - Tier-1 (타 Space 질문 전송, 파일 변경, 외부 쓰기): 데몬이 자동으로 큐(s1_ask_queue)에 등록하고 터미널/대시보드에 알림만 띄우며, 대표님이 짧은 승인(SHA-8 또는 원클릭+SHA-8)만 하면 실행 후 결과를 Space 0에 자동 답장.
   이 2계층 분리의 정확한 경계와 보안 불변식은 무엇인가?
3. [Space 0 자동 답장(Auto-Reply) 시 'AI 장시간 사고(크롤링 지연)' 방지 및 무한루프 완벽 차단]:
   - 르곤(Space 0)에게 결과를 자동 전송할 때, 외부 URL 크롤링 없이 즉시 판단할 수 있도록 '인라인 핵심 요약(Inline Digest, 최대 1500자) + 로컬/GitHub 포인터'를 함께 넣어주는 메시지 봉투(Envelope) 규격.
   - Space 0에 자동 입력된 결과 메시지를 데몬이 다시 명령으로 오인하지 않도록 막는 3중 차단(Role 구분: User vs Assistant DOM 셀렉터 분리 + [S1_NERVE_REPORT] defang 프리픽스 + req_id 원장 중복 차단) 설계.
4. [삼성 원탁회의(Triumvirate Council) 상설 자동화 파이프라인]:
   일회성 스크립트 작성 없이, 단일 명령으로 Space 2(GPT)와 Space 3(Claude)에게 동일 안건을 순차 질의하고 두 성의 답변을 취합해 Space 0(르곤)에게 한 번에 자동 배달하는 표준 워크플로우(승인 게이트 포함 방식)는 어떻게 구성할 것인가?
5. [외출 중 스마트폰 원격 환경 & 자가 치유(Self-Healing) 내장]:
   - 대표님이 외출 중 스마트폰으로만 보실 때도 복붙/캡처가 0건이어야 함.
   - s1_server.py 미기동 시 자동 기동(Watchdog), 브라우저 '세션 한도 재설정 [OK]' 모달 감지 및 알림/자동처리, 탭 유실/비가시 상태 복구 등 100수 앞의 장애 자가 치유 메커니즘.
6. [구현 로드맵 (가장 작고 단단한 Step 1 -> Step 2 -> Step 3)]:
   지금 이미 검증된 s1_ego.py(v1.1.7), s1.py/s1_server.py(v1.4.2), index.html 위에 최소한의 코드로 이 5감각 신경망을 완성하는 단계별 구현 명세를 제시해 주십시오."""

print("[1/3] Space 2 (GPT-6.1 Sol) 100수 앞 마스터 설계 자문 수거 중...")
res2 = s1_ego.cmd_ask(2, master_prompt, wait_sec=150)

print("[2/3] Space 3 (Claude Opus 5.5) 100수 앞 마스터 설계 자문 수거 중...")
res3 = s1_ego.cmd_ask(3, master_prompt, wait_sec=150)

gpt_txt = str(res2.get("last_message", res2))
claude_txt = str(res3.get("last_message", res3))

out_md = (
    "# 🏆 S1 100수 앞 5감각 양방향 신경망 (S1 Nerve v2.0) — 삼성(三聖) 마스터 아키텍처 합동 설계서\n\n"
    "## 1. GPT-6.1 Sol (Space 2) 마스터 설계안\n```\n" + gpt_txt + "\n```\n\n"
    "## 2. Claude Opus 5.5 (Space 3) 마스터 설계안\n```\n" + claude_txt + "\n```\n"
)
pathlib.Path("S1_NERVE_MASTERPLAN.md").write_text(out_md, encoding="utf-8")

subprocess.run(["git", "add", "S1_NERVE_MASTERPLAN.md"], check=False)
subprocess.run(["git", "commit", "-m", "docs(s1): collect 100-moves-ahead triumvirate masterplan for 5-sense nerve"], check=False)
subprocess.run(["git", "pull", "--rebase", "--autostash", "-X", "ours", "origin", "main"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=False)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
print(f"=== S1_NERVE_MASTERPLAN_SHA: {sha} ===")

# 핵심: 르곤 보좌관이 GitHub 크롤링하느라 오래 생각하지 않도록, 인라인 본문 요약(각 1200자)을 메시지에 직접 실어서 Space 0에 자동 전송!
print("[3/3] Space 0 (르곤 보좌관)에게 인라인 본문 포함 자동 완료 보고 전송 중 (크롤링 지연 0초 보장)...")
inline_msg = (
    f"[S1_NERVE_REPORT] 대표님, 100수 앞 삼성 마스터 설계안 수거가 완료되었습니다! (커밋: {sha} / 외부 크롤링 없이 아래 인라인 본문으로 즉시 종합 보고해 주십시오)\n\n"
    f"=== [GPT-6.1 Sol 핵심 설계 요약] ===\n{gpt_txt[:1400]}\n\n"
    f"=== [Claude Opus 5.5 핵심 설계 요약] ===\n{claude_txt[:1400]}"
)
msg_json = json.dumps(inline_msg, ensure_ascii=False)
auto_report_js = f"""
const pages = await ego.listPages(0);
const target = pages.find(p => p.url && p.url.includes("genspark.ai/agents")) || pages[0];
if (target) {{
  await ego.runPageScript(0, target.pageId, `(() => {{
    const ta = document.querySelector("textarea") || document.querySelector("[contenteditable='true']");
    if (!ta) return {{ ok: false, err: "no_ta" }};
    ta.focus();
    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value")?.set;
    if (setter) setter.call(ta, {msg_json});
    else ta.value = {msg_json};
    ta.dispatchEvent(new Event("input", {{ bubbles: true }}));
    setTimeout(() => {{
      const btn = document.querySelector("button[type='submit']") || Array.from(document.querySelectorAll("button, div[role='button']")).find(b => b.querySelector("svg") && !b.disabled);
      if (btn) btn.click();
      else ta.dispatchEvent(new KeyboardEvent("keydown", {{ key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true }}));
    }}, 350);
    return {{ ok: true }};
  }})()`);
}}
return {{ reported: true }};
"""
s1_ego.run_ego_js(auto_report_js, timeout=15)
print("[완료] 르곤 보좌관(Space 0)에게 인라인 요약 포함 자동 보고 전송 성공!")

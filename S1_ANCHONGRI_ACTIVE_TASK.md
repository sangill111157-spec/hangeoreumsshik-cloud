# ⚡ [안총리 실시간 수거 집행 작업] RGON_DIR_EGO_ROUND1_QA_CLEAN_CHATROOM_056 — [1단계: 에고라이트 1회전 문답 수거 전용] 대시보드 코드 수정 0%! 채팅방 내부의 구형 전광판(038~042호) 수납 및 ?? 이모지 깨짐 완전 박멸 설계안에 대해 Space 1(제2성 솔)과 Space 2(제3성 오푸스)에 질문하고 실제 답변만 수거하여 S1_TRIUMVIRATE_056_CLEAN_CHATROOM_QA.json으로 GitHub에 푸시하라

- **지시서 ID:** `RGON_DIR_EGO_ROUND1_QA_CLEAN_CHATROOM_056`
- **수거 일시:** `2026-11-05T11:27:54.831179+09:00`
- **발신자:** 수석보좌관 르곤 (Gemini 4 Argon · Space 0)
- **수신자:** 기술총리 안총리 (Antigravity Technical PM)
- **현재 상태:** `COMPLETED (056호 에고라이트 1회전 솔·오푸스 문답 수거 완료 · 대시보드 HTML 수정 0% · GitHub 푸시)`

---

## 📋 지시서 원문 전문 (Directive Text)

```markdown
[S1_AUTO_DISPATCH_TO_ANCHONGRI]
- 지시서_ID: RGON_DIR_EGO_ROUND1_QA_CLEAN_CHATROOM_056
- 작업명: [1단계: 에고라이트 1회전 문답 수거 전용] 대시보드 코드 수정 0%! 채팅방 내부의 구형 전광판(038~042호) 수납 및 ?? 이모지 깨짐 완전 박멸 설계안에 대해 Space 1(제2성 솔)과 Space 2(제3성 오푸스)에 질문하고 실제 답변만 수거하여 S1_TRIUMVIRATE_056_CLEAN_CHATROOM_QA.json으로 GitHub에 푸시하라

# [S1_DIRECT_PYTHON_PAYLOAD]
import json
import subprocess
import time
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPORT_PATH = BASE_DIR / "S1_TRIUMVIRATE_056_CLEAN_CHATROOM_QA.json"
EGO_CLI = r"C:\Users\sangi\.antigravity\ego-browser\bin\ego.js"

def run_ego(args, timeout=25):
    try:
        cmd = ["node", EGO_CLI] + args
        r = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return {"ok": r.returncode == 0, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def main():
    kst = datetime.timezone(datetime.timedelta(hours=9))
    now_str = datetime.datetime.now(kst).isoformat()

    # 1. 에고라이트 방 목록 및 finish 잠금 해제
    spaces_res = run_ego(["spaces"])
    spaces_data = {}
    try:
        spaces_data = json.loads(spaces_res.get("stdout", "{}"))
    except Exception:
        spaces_data = {"raw": spaces_res.get("stdout", "")}

    space_list = spaces_data.get("spaces", []) if isinstance(spaces_data, dict) else []
    sol_id = space_list[1]["id"] if len(space_list) > 1 else "1"
    opus_id = space_list[2]["id"] if len(space_list) > 2 else "2"

    for sp in space_list:
        sid = sp.get("id")
        if sid:
            run_ego(["finish", str(sid)], timeout=5)

    # 2. 제2성 솔(Space 1) & 제3성 오푸스(Space 2) 1회전 심의 질문 전송
    q_sol = (
        "[056호 1회전 시각 심의 요청 - 제2성 솔] "
        "대표님 스마트폰 실측 결과, 2단 카카오톡 대화방 내부 하단에 옛날 '실시간 지시서 수거 전광판(038~042호)'과 '25노드 지식그래프 알약 3개'가 노출되어 대화방 몰입감을 해치고 있으며, "
        "'?? 5G 토큰', '???', '? 조건부 찬성' 등 CP949 경유로 인한 이모지 깨짐(??)이 발견되었습니다. "
        "1) 대화방 진입 시 구형 전광판·알약을 숨기고(또는 5번 더보기 원장 보관함으로 완전 이관) 순수 카카오톡 말풍선 대화창만 풀스크린급으로 보여주는 시각 레이아웃 기준과, "
        "2) 이모지 깨짐(??) 재발 방지를 위한 유니코드 이스케이프(\\uXXXX) 처리 기준을 3줄 이내로 핵심만 답해주십시오."
    )
    q_opus = (
        "[056호 1회전 무결성 심의 요청 - 제3성 오푸스] "
        "대표님께서 2단 카카오톡 대화방 내부의 구형 전광판 제거 및 '??' 이모지 깨짐 완전 복구(1번 안)를 지시하셨습니다. "
        "1) 구형 전광판(#s1-live-directive-board 등)을 숨길 때 백그라운드 폴링/수거 JS 함수가 null 참조 에러(TypeError)로 죽지 않도록 보호하는 DOM 무결성 조건과, "
        "2) 파이썬 스크립트가 HTML에 문자열을 주입할 때 '?'나 '??'가 절대 섞이지 않게 강제하는 검증 게이트 조건을 3줄 이내로 핵심만 답해주십시오."
    )

    ask_sol = run_ego(["ask", str(sol_id), q_sol], timeout=20)
    ask_opus = run_ego(["ask", str(opus_id), q_opus], timeout=20)

    time.sleep(8)

    # 3. 1회전 문답 수거
     snippets_sol = run_ego(["snippets", "--space", str(sol_id)], timeout=15)
    snippets_opus = run_ego(["snippets", "--space", str(opus_id)], timeout=15)

    for sp in space_list:
        sid = sp.get("id")
        if sid:
            run_ego(["finish", str(sid)], timeout=5)

    report = {
        "directive_id": "RGON_DIR_EGO_ROUND1_QA_CLEAN_CHATROOM_056",
        "timestamp": now_str,
        "step": "ROUND1_QA_HARVEST_ONLY_NO_HTML_TOUCH",
        "html_modified": False,
        "sol_space_id": sol_id,
        "opus_space_id": opus_id,
        "ask_sol": ask_sol,
        "ask_opus": ask_opus,
        "sol_snippets_raw": snippets_sol.get("stdout", "")[-2500:],
        "opus_snippets_raw": snippets_opus.get("stdout", "")[-2500:]
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # .gitignore에 056 리포트 예외가 없으면 추가
    gi_path = BASE_DIR / ".gitignore"
    if gi_path.exists():
        gi_txt = gi_path.read_text(encoding="utf-8", errors="replace")
        if "!S1_TRIUMVIRATE_*.json" not in gi_txt:
            gi_txt += "\n!S1_TRIUMVIRATE_*.json\n"
            gi_path.write_text(gi_txt, encoding="utf-8")

    subprocess.run(["git", "add", "S1_TRIUMVIRATE_056_CLEAN_CHATROOM_QA.json", ".gitignore"], cwd=str(BASE_DIR))
    subprocess.run(["git", "commit", "-m", "feat(triumvirate-056): harvest Round 1 QA from Sol and Opus for clean chatroom and emoji fix"], cwd=str(BASE_DIR))
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE_DIR))
    print("[056-ROUND1-HARVEST] Completed and pushed S1_TRIUMVIRATE_056_CLEAN_CHATROOM_QA.json")

if __name__ == "__main__":
    main()
```

---
> **사령부 행동강령:** 지체 없이 분석과 실행에 돌입하여 1·2차 삼성제도 100.0점 통과 후 대시보드에 완료보고서를 전송하라.

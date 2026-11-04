import json
import datetime
from pathlib import Path
import s1_ego

BASE = Path(__file__).resolve().parent
KST = datetime.timezone(datetime.timedelta(hours=9))

def now_iso():
    return datetime.datetime.now(KST).isoformat()

# 제1성 르곤이 제2성(솔)과 제3성(오푸스)에게 보내는 1회전 공식 심의 질문
QUESTION_FOR_TRIUMVIRATE = """[삼성제도 1회전 공식 문답 심의 요청 ? 050호]
이상일 대표님께서 스마트폰 카카오톡 실제 캡처 5장(1.친구/홈, 2.채팅, 3.지금/숏폼, 4.쇼핑/오늘의PICK, 5.더보기 4x3 그리드)을 보내주시며 "카카오 기본 하단바 5페이지별로 구성"하라고 하명하셨습니다.
기존처럼 한 페이지에 모든 요소를 길게 나열하는 방식을 폐기하고, 하단 고정 5탭 바를 눌러 5개 독립 페이지(Page 1~5)를 전환(나머지 4개 페이지는 display:none 숨김)하는 구조로 개편하고자 합니다.
1) 시각/UX 관점(제2성 솔) 및 무결성/기존기능 보존 관점(제3성 오푸스)에서 반드시 지켜야 할 핵심 설계 조건 3가지와,
2) 절대 범해서는 안 될 실패 요인(반박/주의사항)을 답변해 주십시오."""

def main():
    print("[050-QA-HARVEST] Starting 1-Round Ego-Lite Copy-Paste & Answer Harvest (NO HTML EDITING)...")
    spaces_info = s1_ego.cmd_spaces()
    
    # Space 2 (제2성 솔) 1회전 질문 복붙 및 답변 수거
    res_space2 = s1_ego.cmd_ask(2, QUESTION_FOR_TRIUMVIRATE, wait_sec=75, tail_chars=4000)
    if not res_space2.get("ok"):
        # 만약 전송 조건 불일치 시 현재 Space 2 화면의 최신 메시지 읽기 폴백 병행
        read_space2 = s1_ego.cmd_read(2, tail_chars=3000)
    else:
        read_space2 = {}

    # Space 3 (제3성 오푸스) 1회전 질문 복붙 및 답변 수거
    res_space3 = s1_ego.cmd_ask(3, QUESTION_FOR_TRIUMVIRATE, wait_sec=75, tail_chars=4000)
    if not res_space3.get("ok"):
        read_space3 = s1_ego.cmd_read(3, tail_chars=3000)
    else:
        read_space3 = {}

    report = {
        "directive_id": "RGON_DIR_EGO_ROUND1_QA_HARVEST_ONLY_050",
        "timestamp": now_iso(),
        "rule": "STRICTLY_1_ROUND_QA_HARVEST_ONLY_NO_CODE_EDIT",
        "question_sent": QUESTION_FOR_TRIUMVIRATE,
        "spaces_overview": spaces_info,
        "space2_sol_ask_result": res_space2,
        "space2_sol_read_fallback": read_space2,
        "space3_opus_ask_result": res_space3,
        "space3_opus_read_fallback": read_space3
    }

    out_path = BASE / "S1_TRIUMVIRATE_ROUND1_QA_REPORT.json"
    docs_out_path = BASE / "docs" / "S1_TRIUMVIRATE_ROUND1_QA_REPORT.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    docs_out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[050-QA-HARVEST] Saved real 1-round QA report to S1_TRIUMVIRATE_ROUND1_QA_REPORT.json")

if __name__ == "__main__":
    main()
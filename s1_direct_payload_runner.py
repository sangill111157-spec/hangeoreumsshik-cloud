import json, subprocess, sys, time, datetime, pathlib

BASE = pathlib.Path(__file__).resolve().parent
OUT_JSON = BASE / "S1_064_SIDE_ROOMS_TRIUMVIRATE_ANSWERS.json"
DOCS_OUT_JSON = BASE / "docs" / "S1_064_SIDE_ROOMS_TRIUMVIRATE_ANSWERS.json"

def call_ego(args, timeout=25):
    try:
        r = subprocess.run(
            [sys.executable, str(BASE / "s1_ego.py")] + args,
            cwd=str(BASE),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout
        )
        return {"ok": r.returncode == 0, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def main():
    kst = datetime.timezone(datetime.timedelta(hours=9))
    now_str = datetime.datetime.now(kst).isoformat()

    # 1. 에고라이트 옆방 Space 1(솔) & Space 2(오푸스) 최신 답변 전문 수거
    snip_sol = call_ego(["snippets", "--space", "1"])
    snip_opus = call_ego(["snippets", "--space", "2"])

    # 만약 옆방에 추가 질문이 필요할 경우를 대비해, 남은 먹통 버튼(12트랙 곡 박스 12개 + 6대 신경망 카드 6개) 해결법도 함께 질의 후 수거
    q_next = (
        "[064호 삼성제도 합의 요청] 063B호 2차 청소로 상단 중복 알약 바(.s1-kakao-sub-pills)와 중복 원장 버튼이 모두 정리되었습니다. "
        "이제 남은 미작동 요소는 딱 2곳입니다: "
        "① 1번(홈) 페이지의 '6대 신경망 라이브 카드(1.모바일~6.4대채널)' 6개, "
        "② 3번(지금) 페이지의 '신보 12트랙 곡 박스(01.막차~12.내일의아침)' 12개. "
        "이 6개 카드와 12개 트랙 박스를 클릭했을 때 각각 어떤 화면/모달/오디오가 작동해야 가장 완벽한지 3줄 이내로 최종 설계안을 주십시오."
    )
    call_ego(["ask", "--space", "1", "--prompt", q_next])
    call_ego(["ask", "--space", "2", "--prompt", q_next])
    time.sleep(10)

    snip_sol_after = call_ego(["snippets", "--space", "1"])
    snip_opus_after = call_ego(["snippets", "--space", "2"])

    for s in ("0", "1", "2", "3"):
        call_ego(["finish", "--space", s], timeout=8)

    data = {
        "directive_id": "RGON_DIR_HARVEST_SOL_OPUS_SIDE_ROOMS_064",
        "timestamp": now_str,
        "html_modified": False,
        "sol_space1_before": snip_sol.get("stdout", "")[-3500:],
        "opus_space2_before": snip_opus.get("stdout", "")[-3500:],
        "sol_space1_latest": snip_sol_after.get("stdout", "")[-3500:],
        "opus_space2_latest": snip_opus_after.get("stdout", "")[-3500:],
    }

    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    DOCS_OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DOCS_OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    gi = (BASE / ".gitignore").read_text(encoding="utf-8", errors="replace")
    if "!S1_064_SIDE_ROOMS_TRIUMVIRATE_ANSWERS.json" not in gi:
        (BASE / ".gitignore").write_text(
            gi + "\n!S1_064_SIDE_ROOMS_TRIUMVIRATE_ANSWERS.json\n!docs/S1_064_SIDE_ROOMS_TRIUMVIRATE_ANSWERS.json\n",
            encoding="utf-8"
        )

    subprocess.run(["git", "add", "-f", "S1_064_SIDE_ROOMS_TRIUMVIRATE_ANSWERS.json", "docs/S1_064_SIDE_ROOMS_TRIUMVIRATE_ANSWERS.json", ".gitignore"], cwd=str(BASE))
    subprocess.run(["git", "commit", "-m", "feat(triumvirate-064): harvest Sol & Opus side-room answers for 6-nodes and 12-tracks"], cwd=str(BASE))
    subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE))

    h_sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), text=True).strip()
    msg0 = f"[064호 옆방 삼성제도 수거 완료] 솔(Space 1) & 오푸스(Space 2)의 심의 답변 수거 및 GitHub 푸시 완료! (커밋: {h_sha})"
    call_ego(["ask", "--space", "0", "--prompt", msg0], timeout=25)
    call_ego(["finish", "--space", "0"], timeout=8)

if __name__ == "__main__":
    main()
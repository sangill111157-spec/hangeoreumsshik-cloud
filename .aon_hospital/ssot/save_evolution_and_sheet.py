from __future__ import annotations
import csv
import json
import os
import subprocess
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

ROWS = [
    {
        "일시": NOW,
        "구분": "잘한 점 (Well Done)",
        "핵심항목": "최고 전문가 레버리지 분업 확립",
        "상세내용": "기획/지시(르곤) -> 정밀 코드 작성(GPT 6.1 SOL / Claude Opus) -> 현장 즉시 실행(안총리) 체제로 시행착오를 줄이고 해결 속도를 극대화함",
        "교훈_및_조치": "앞으로도 각자 가장 잘하는 영역에 집중하는 레버리지 원칙 유지",
        "상태": "완료"
    },
    {
        "일시": NOW,
        "구분": "잘한 점 (Well Done)",
        "핵심항목": "어사이드 지휘 패널 클린 완성본 구축",
        "상세내용": "clean_ui.py로 불필요한 [5대 웹창 한꺼번에 모두 열기] 버튼을 완전히 제거하고 필요한 창만 개별 오픈 + 원클릭 복사 구조 완성",
        "교훈_및_조치": "복잡한 과잉 버튼보다 직관적이고 깔끔한 실전 UI 유지",
        "상태": "완료"
    },
    {
        "일시": NOW,
        "구분": "잘한 점 (Well Done)",
        "핵심항목": "한 줄 지시 10초 광고 올인원 스튜디오(v4) 개통",
        "상세내용": "'간단한 10초 광고 만들기 주제는 종이컵' 한 줄 입력으로 [0~3초 훅/3~7초 디테일/7~10초 클로징 기획안 + 9:16 세로 애니메이션 + TTS 나레이션 + WebM 다운로드 + 지휘패널 복사버튼 종이컵 자동변환] 달성",
        "교훈_및_조치": "실제 테스트 한 줄을 던져보고 막히는 곳을 즉시 교정하는 실전 검증 방식 정착",
        "상태": "완료"
    },
    {
        "일시": NOW,
        "구분": "못한 점 (To Improve)",
        "핵심항목": "서비스워커(sw.js) 및 브라우저 캐시 잔류",
        "상세내용": "로컬 개발 중 구버전 sw.js 캐시(836kB)가 남아 새 패치가 화면에 즉시 반영되지 않아 시간 소모 발생",
        "교훈_및_조치": "로컬 자동 해제형 sw.js 적용 및 빌드 쿼리스트링(__rgon_ad_build)으로 재발 원천 차단",
        "상태": "교정완료"
    },
    {
        "일시": NOW,
        "구분": "못한 점 (To Improve)",
        "핵심항목": "백엔드 고정 매크로(앵무새) 응답 문제",
        "상세내용": "창작/광고 지시를 내려도 기존 NVDA/청사 고정 멘트만 반복 출력하던 한계 발견",
        "교훈_및_조치": "프론트엔드 광고 인터셉터로 매크로를 우회하고 주제 맞춤형 기획안 생성 엔진 장착",
        "상태": "교정완료"
    },
    {
        "일시": NOW,
        "구분": "못한 점 (To Improve)",
        "핵심항목": "채팅창 내부 DOM 덮어쓰기 및 미표시 현상",
        "상세내용": "기존 채팅 피드 컨테이너 내부에 카드를 넣었을 때 화면 밖으로 밀리거나 리렌더링으로 사라지는 문제 발생",
        "교훈_및_조치": "document.body 직속 최상위 고정 모달(v4, z-index:2147483640) 및 우측 하단 재열기 플로팅 배지로 100% 표시 보장",
        "상태": "교정완료"
    },
    {
        "일시": NOW,
        "구분": "내일 진화 과제 (Next Step)",
        "핵심항목": "야간 무인 자율 진화 & 영상 내 음성 통합 녹음",
        "상세내용": "1) 다운로드 영상 파일에 성우 목소리까지 통합 녹음 2) 자는 동안 스스로 발전하고 구글 시트에 일일 성적표를 자동 누적하는 스케줄러 가동",
        "교훈_및_조치": "무인 자동화 파이프라인 고도화",
        "상태": "예정"
    }
]

# 1. JSON 진화 기억 장부 누적 저장 (evolution_memory.json)
json_path = ROOT / "evolution_memory.json"
history = []
if json_path.exists():
    try:
        history = json.loads(json_path.read_text(encoding="utf-8"))
        if not isinstance(history, list):
            history = []
    except Exception:
        history = []
history.extend(ROWS)
json_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

# 2. Markdown 진화 일지 저장 (RGON_EVOLUTION_LOG.md)
md_path = ROOT / "RGON_EVOLUTION_LOG.md"
md_lines = [
    "# 🏛️ 르곤-알파 자가진화 기억 장부 (잘한 점 · 못한 점 · 교훈 일지)\n",
    f"- **최종 업데이트**: `{NOW}`\n",
    "| 일시 | 구분 | 핵심항목 | 상세내용 | 교훈 및 조치 | 상태 |",
    "| :--- | :--- | :--- | :--- | :--- | :--- |",
]
for r in ROWS:
    md_lines.append(
        f"| {r['일시']} | **{r['구분']}** | {r['핵심항목']} | {r['상세내용']} | {r['교훈_및_조치']} | {r['상태']} |"
    )
md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

# 3. 구글 시트 / 엑셀 호환 CSV 누적 저장 (RGON_GOOGLE_SHEET_LOG.csv, UTF-8-SIG)
csv_path = ROOT / "RGON_GOOGLE_SHEET_LOG.csv"
file_exists = csv_path.exists()
with csv_path.open("a", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["일시", "구분", "핵심항목", "상세내용", "교훈_및_조치", "상태"])
    if not file_exists:
        writer.writeheader()
    writer.writerows(ROWS)

# 4. 구글 시트에 바로 [Ctrl + V] 붙여넣기 할 수 있도록 TSV(탭 구분) 표를 윈도우 클립보드에 자동 복사
tsv_lines = ["일시\t구분\t핵심항목\t상세내용\t교훈 및 조치\t상태"]
for r in ROWS:
    tsv_lines.append(f"{r['일시']}\t{r['구분']}\t{r['핵심항목']}\t{r['상세내용']}\t{r['교훈_및_조치']}\t{r['상태']}")
tsv_text = "\r\n".join(tsv_lines)
try:
    subprocess.run(["clip"], input=tsv_text.encode("utf-16le"), check=False)
    print("[클립보드 복사 완료] 구글 시트에서 Ctrl+V 만 누르면 표 전체가 칸에 맞춰 바로 들어갑니다!")
except Exception as e:
    print(f"[클립보드 참고] {e}")

# 5. 환경변수에 구글 시트 웹훅(Apps Script URL)이 설정된 경우 자동 전송
webhook = os.environ.get("GOOGLE_SHEET_WEBHOOK_URL", "").strip()
if webhook:
    try:
        req = urllib.request.Request(
            webhook,
            data=json.dumps({"rows": ROWS}, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=8).read()
        print("[구글 시트 웹훅 자동 전송 완료]")
    except Exception as e:
        print(f"[구글 시트 웹훅 실패] {e}")

print("EVOLUTION LOG & GOOGLE SHEET SYNC COMPLETE!")

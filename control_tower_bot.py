"""
══════════════════════════════════════════════════════════════════
 한걸음씩 & NVDA 트레이딩 통합 스마트폰 관제탑 엔진
 control_tower_bot.py
 
 [핵심 설계 원칙 - Zero-Dependency / 초경량 REST API]
 1. 알림 전송 (send_briefing):
    - GitHub Actions 및 로컬/클라우드 파이프라인의 성공/실패/시그널 알림을
      대표님의 텔레그램 채팅방으로 마크다운 포맷으로 즉시 발송
    - 토큰 미설정 시에도 에러 없이 콘솔에 [Dry-Run 미리보기]로 정상 동작 (방어 코드)
 2. 원격 클라우드 트리거 (trigger_github_workflow):
    - 스마트폰 텔레그램 명령어나 CLI에서 GitHub REST API(workflow_dispatch)를 호출하여
      로컬 PC 부하 0%로 마이크로소프트 클라우드 Ubuntu 서버를 즉시 깨움!
══════════════════════════════════════════════════════════════════
"""
# [RGON-WBC-GUARD-V18-START]
try:
    import rgon_white_blood_cell as _rgon_wbc
    _rgon_wbc.install_excepthook('control_tower_bot.py')
except Exception:
    _rgon_wbc = None
# [RGON-WBC-GUARD-V18-END]

import os
import sys
import io
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path

# 콘솔 UTF-8 출력 보장
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── 설정 로드 ──
def get_env_or_connect_ai(key: str, default: str = "") -> str:
    """환경 변수 우선 조회, 없으면 Connect-AI 설정 파일에서 로드"""
    val = os.getenv(key, "").strip()
    if val:
        return val

    # Connect-AI 설정 폴더 탐색 (토큰 공유)
    cfg_paths = [
        Path(r"C:\Users\sangi\.connect-ai-brain\_company\_agents\secretary\tools\telegram_setup.json"),
        Path(r"C:\Users\sangi\OneDrive\Desktop\hangeoreumsshik\automation\config\.env")
    ]
    for p in cfg_paths:
        if p.exists():
            try:
                if p.suffix == ".json":
                    data = json.loads(p.read_text(encoding="utf-8"))
                    if key in data and data[key]:
                        return data[key]
                elif p.suffix == ".env":
                    for line in p.read_text(encoding="utf-8").splitlines():
                        if line.startswith(f"{key}="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
    return default

def mask_secret(secret: str) -> str:
    """민감 정보(토큰, 키)를 앞뒤 3자리 제외하고 마스킹(***) 처리"""
    if not secret:
        return "미설정"
    if len(secret) <= 6:
        return "***"
    return f"{secret[:3]}***{secret[-3:]}"

TELEGRAM_BOT_TOKEN = get_env_or_connect_ai("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = get_env_or_connect_ai("TELEGRAM_CHAT_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.getenv("GITHUB_REPO", "").strip()  # 예: "owner/repo"

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

# ══════════════════════════════════════════════════════════════
# 1. 텔레그램 브리핑 알림 전송 (기능 A)
# ══════════════════════════════════════════════════════════════
def send_briefing(
    task_name: str,
    status: str = "SUCCESS",
    message: str = "",
    details: str = "",
    token: str = None,
    chat_id: str = None
) -> bool:
    """
    대표님 텔레그램으로 정돈된 상태 브리핑 메시지 전송
    토큰 부재 시 에러 없이 [Dry-Run] 콘솔 출력으로 우아하게 폴백
    """
    bot_token = token or TELEGRAM_BOT_TOKEN
    target_chat = chat_id or TELEGRAM_CHAT_ID

    status_upper = status.upper()
    if "SUCCESS" in status_upper or "OK" in status_upper:
        icon = "✅"
        status_text = "성공 (SUCCESS)"
    elif "FAIL" in status_upper or "ERROR" in status_upper:
        icon = "🚨"
        status_text = "실패/오류 (FAILED)"
    else:
        icon = "ℹ️"
        status_text = status

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 텔레그램 HTML 포맷 메시지 작성
    lines = [
        f"<b>{icon} [한걸음씩 통합 관제탑]</b>",
        f"<b>작업</b>: <code>{task_name}</code>",
        f"<b>상태</b>: <b>{status_text}</b>",
        f"<b>시각</b>: <code>{now_str}</code>",
    ]
    if message:
        lines.append(f"\n<b>내용</b>:\n{message}")
    if details:
        lines.append(f"\n<pre>{details}</pre>")
    lines.append("\n<i>- 노트북 부하: 0% | 클라우드 무인 관제</i>")

    formatted_text = "\n".join(lines)

    # 토큰/Chat ID가 없는 경우 Graceful Dry-Run
    if not bot_token or not target_chat:
        print("\n" + "=" * 55)
        print("📢 [Dry-Run 미리보기] 텔레그램 설정 미감지 — 콘솔로 출력합니다:")
        print("-" * 55)
        # HTML 태그 가독성 있게 치환하여 콘솔 출력
        clean_text = (
            formatted_text.replace("<b>", "")
            .replace("</b>", "")
            .replace("<code>", "[")
            .replace("</code>", "]")
            .replace("<i>", "")
            .replace("</i>", "")
            .replace("<pre>", "\n--- 세부 정보 ---\n")
            .replace("</pre>", "")
        )
        print(clean_text)
        print("=" * 55 + "\n")
        return True

    # 텔레그램 Bot API 전송
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": formatted_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(api_url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                log(f"텔레그램 브리핑 전송 완료 (작업: {task_name}, 상태: {status})")
                return True
            else:
                log(f"텔레그램 응답 비정상 (코드: {resp.status})")
                return False
    except urllib.error.HTTPError as e:
        log(f"[WARN] 텔레그램 HTTP 에러: {e.code} - {e.reason}")
        return False
    except Exception as e:
        log(f"[WARN] 텔레그램 전송 실패: {e}")
        return False

# ══════════════════════════════════════════════════════════════
# 2. GitHub Actions 클라우드 원격 트리거 (기능 B)
# ══════════════════════════════════════════════════════════════
def trigger_github_workflow(
    command: str,
    repo: str = None,
    token: str = None,
    workflow_file: str = "hangeoreumsshik_cloud.yml",
    ref: str = "main"
) -> bool:
    """
    GitHub REST API (workflow_dispatch)를 호출하여
    원격 마이크로소프트 Ubuntu 클라우드 서버에서 작업을 즉시 실행
    """
    target_repo = repo or GITHUB_REPO
    github_token = token or GITHUB_TOKEN

    valid_commands = ["report", "analytics", "strategy", "produce_healing", "all"]
    if command not in valid_commands:
        log(f"[ERROR] 잘못된 명령입니다: '{command}'. 허용된 명령: {valid_commands}")
        return False

    if not target_repo or not github_token:
        print("\n" + "=" * 55)
        print("🚀 [Dry-Run 원격 발사 미리보기] GITHUB_REPO / GITHUB_TOKEN 미설정")
        print(f" - 대상 저장소: {target_repo or '(미설정)'}")
        print(f" - 실행 워크플로우: {workflow_file}")
        print(f" - 전달 파라미터(command): {command}")
        print("💡 GITHUB_TOKEN(PAT)과 GITHUB_REPO를 설정하면 클라우드가 즉시 깨어납니다.")
        print("=" * 55 + "\n")
        return True

    url = f"https://api.github.com/repos/{target_repo}/actions/workflows/{workflow_file}/dispatches"
    payload = {
        "ref": ref,
        "inputs": {
            "command": command
        }
    }

    try:
        json_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=json_data,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {github_token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "HanGeoreum-ControlTower"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            # 204 No Content가 정상 응답
            if resp.status in (200, 204):
                log(f"🎉 GitHub Actions 클라우드 원격 트리거 성공! (명령: {command})")
                send_briefing(
                    task_name=f"원격 명령 발사 [{command}]",
                    status="SUCCESS",
                    message=f"GitHub Actions 클라우드 서버가 성공적으로 가동되었습니다.\n(브랜치: {ref}, 워크플로우: {workflow_file})"
                )
                return True
            else:
                log(f"GitHub API 응답 코드: {resp.status}")
                return False
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        log(f"[ERROR] GitHub API 트리거 실패 ({e.code}): {err_msg}")
        return False
    except Exception as e:
        log(f"[ERROR] GitHub 원격 호출 중 예외: {e}")
        return False

# ══════════════════════════════════════════════════════════════
# 3. CLI 엔트리포인트
# ══════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description="한걸음씩 & NVDA 텔레그램 단일 관제탑")
    parser.add_argument("--notify", action="store_true", help="브리핑 알림 전송 모드")
    parser.add_argument("--task", type=str, default="System Check", help="작업 이름")
    parser.add_argument("--status", type=str, default="SUCCESS", help="작업 상태 (SUCCESS / FAILED / INFO)")
    parser.add_argument("--message", type=str, default="", help="알림 본문 메시지")
    parser.add_argument("--details", type=str, default="", help="상세 로그 또는 추가 텍스트")

    parser.add_argument("--trigger", type=str, choices=["report", "analytics", "strategy", "produce_healing", "all"],
                        help="GitHub Actions 원격 클라우드 작업 트리거")
    parser.add_argument("--repo", type=str, help="GitHub 대상 저장소 (owner/repo)")
    parser.add_argument("--ref", type=str, default="main", help="Git 브랜치/태그")

    args = parser.parse_args()

    if args.trigger:
        trigger_github_workflow(command=args.trigger, repo=args.repo, ref=args.ref)
    elif args.notify or args.message:
        send_briefing(
            task_name=args.task,
            status=args.status,
            message=args.message,
            details=args.details
        )
    else:
        # 인자 없이 실행 시 자가 점검 (Self-Check)
        print("🌟 [한걸음씩 단일 관제탑 (Control Tower)] 정상 로드 완료")
        print(f" - 텔레그램 봇 토큰: {mask_secret(TELEGRAM_BOT_TOKEN)} ({'정상 로드' if TELEGRAM_BOT_TOKEN else '미설정'})")
        print(f" - 텔레그램 Chat ID: {mask_secret(TELEGRAM_CHAT_ID)} ({'정상 로드' if TELEGRAM_CHAT_ID else '미설정'})")
        print(f" - GitHub Token: {mask_secret(GITHUB_TOKEN)} ({'정상 로드' if GITHUB_TOKEN else '미설정'})")
        print("\n사용 예시:")
        print("  1) 알림 테스트: python control_tower_bot.py --notify --task 'produce_healing' --status 'SUCCESS' --message '8시간 롱폼 렌더링 완료'")
        print("  2) 클라우드 트리거: python control_tower_bot.py --trigger produce_healing --repo owner/repo")

if __name__ == "__main__":
    main()

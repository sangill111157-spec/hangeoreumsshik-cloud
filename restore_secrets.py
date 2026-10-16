"""
══════════════════════════════════════════════════════════════════
 GitHub Secrets Base64 자동 복원 엔진
 restore_secrets.py
 
 [기능]
 1. GitHub Actions 실행 시 환경 변수로 주입된 Base64 인코딩 시크릿을
    자동으로 ./config/ 하위의 원본 파일(token.pickle 등)로 복원
 2. 로컬 PC에 이미 파일이 존재할 경우 안전하게 건너뜀 (Skip)
 3. 권한 및 경로 자동 생성
══════════════════════════════════════════════════════════════════
"""

import os
import sys
import io
import base64
from pathlib import Path

# 콘솔 UTF-8 출력 보장
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 복원 대상 시크릿 매핑 (환경변수명 -> config 내 파일명)
SECRET_MAPPING = {
    "G_TOKEN_PICKLE_B64": "token.pickle",
    "G_TOKEN_BOOSTER_B64": "token_booster.pickle",
    "G_YT_TOKEN_B64": "yt_token.pickle",
    "G_CLIENT_SECRET_B64": "client_secret.json",
    "G_DOTENV_B64": ".env"
}

def log(msg: str):
    print(f"[restore_secrets] {msg}", flush=True)

def restore_secrets():
    base_dir = Path(__file__).resolve().parent
    config_dir = base_dir / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    restored_count = 0
    skipped_count = 0

    log(f"시크릿 복원 시작... 대상 폴더: {config_dir}")

    for env_key, filename in SECRET_MAPPING.items():
        target_path = config_dir / filename
        env_val = os.getenv(env_key, "").strip()

        if target_path.exists() and target_path.stat().st_size > 0:
            # 로컬 파일이 이미 존재하면 안전하게 유지
            log(f" - [SKIP] {filename} (이미 로컬에 존재함, 크기: {target_path.stat().st_size} bytes)")
            skipped_count += 1
            continue

        if not env_val:
            # 환경변수도 없고 파일도 없는 경우
            log(f" - [INFO] {env_key} 환경변수 미제공 (필요 시 등록 요망)")
            continue

        try:
            # Base64 디코딩 후 복원
            decoded_bytes = base64.b64decode(env_val)
            target_path.write_bytes(decoded_bytes)
            log(f" - [OK] {filename} 복원 완료! ({len(decoded_bytes)} bytes)")
            restored_count += 1
        except Exception as e:
            log(f" - [ERROR] {filename} 복원 실패 ({env_key}): {e}")

    log(f"복원 완료 요약: 복원됨 {restored_count}개 | 건너뜀 {skipped_count}개")
    return True

if __name__ == "__main__":
    restore_secrets()

"""
══════════════════════════════════════════════════════════════════
 GitHub Actions Secrets 등록 도우미
 export_secrets_helper.py
 
 [기능]
 로컬 ./config/ 폴더의 필수 인증 파일들을 Base64 문자열로 인코딩하여
 GitHub Settings -> Secrets에 등록하기 편하게 정리해 줍니다.
 (보안을 위해 콘솔에 출력하지 않고 secrets_to_upload.txt에 저장)
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

FILES_TO_EXPORT = {
    "G_TOKEN_PICKLE_B64": "token.pickle",
    "G_TOKEN_BOOSTER_B64": "token_booster.pickle",
    "G_YT_TOKEN_B64": "yt_token.pickle",
    "G_CLIENT_SECRET_B64": "client_secret.json",
    "G_DOTENV_B64": ".env"
}

def export_secrets():
    base_dir = Path(__file__).resolve().parent
    config_dir = base_dir / "config"
    output_file = base_dir / "secrets_to_upload.txt"

    lines = [
        "# ==================================================================",
        "# GitHub Actions Secrets 등록용 키 & Base64 인코딩 값 목록",
        "# 저장소: Settings -> Secrets and variables -> Actions -> New repository secret",
        "# (주의: 이 파일은 .gitignore에 등록되어 Git에 포함되지 않습니다)",
        "# ==================================================================\n"
    ]

    exported_keys = []

    for secret_name, filename in FILES_TO_EXPORT.items():
        file_path = config_dir / filename
        if file_path.exists() and file_path.stat().st_size > 0:
            b64_str = base64.b64encode(file_path.read_bytes()).decode("utf-8")
            lines.append(f"[{secret_name}]")
            lines.append(b64_str)
            lines.append("-" * 65 + "\n")
            exported_keys.append((secret_name, filename, file_path.stat().st_size))

    output_file.write_text("\n".join(lines), encoding="utf-8")

    print("\n" + "=" * 60)
    print("✨ [GitHub Secrets 등록 도우미] 인코딩 완료!")
    print(f"📄 저장된 파일: {output_file.name} (보안 격리 완료)")
    print("-" * 60)
    print(f"{'Secret 키 이름':<25} | {'원본 파일':<20} | 크기")
    print("-" * 60)
    for k, fname, size in exported_keys:
        print(f"{k:<25} | {fname:<20} | {size} bytes")
    print("=" * 60)
    print("💡 대표님께서는 나중에 GitHub 웹사이트 저장소 설정(Settings -> Secrets)에서")
    print("   위 Secret 이름과 secrets_to_upload.txt 안의 값을 복사해 등록하시면 됩니다.\n")

if __name__ == "__main__":
    export_secrets()

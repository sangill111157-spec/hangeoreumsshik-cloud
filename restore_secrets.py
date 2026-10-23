#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [RGON-SELF-HEAL-V17] 窮則變 變則通 通則久 — 주역 궁변통구 자가치유 시크릿 복원기
"""
restore_secrets.py  (RGON v6.3.0-step17 자가치유판)
- GitHub Actions 등에서 환경변수(Secrets)가 있을 때만 해당 파일로 복원한다.
- 기존 로직이 있으면 restore_secrets_legacy.py 로 보존되어 먼저 실행된다.
- 환경변수가 비었거나, legacy 로직이 실패해도 경고만 남기고 항상 exit 0 (analytics/report 잡 보호).
"""
import os
import sys
import json
import base64
import binascii
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEGACY = ROOT / "restore_secrets_legacy.py"
BINARY_SUFFIX = (".pickle", ".pkl", ".bin", ".p12", ".pfx")
DEFAULT_MAP = {
    "CLIENT_SECRET_JSON": "client_secret.json",
    "CLIENT_SECRETS_JSON": "client_secrets.json",
    "CREDENTIALS_JSON": "credentials.json",
    "TOKEN_JSON": "token.json",
    "YOUTUBE_TOKEN_JSON": "youtube_token.json",
    "SERVICE_ACCOUNT_JSON": "service_account.json",
    "DOTENV": ".env",
    "ENV_FILE": ".env",
}


def _log(level, msg):
    try:
        print("[restore_secrets][%s] %s" % (level, msg), flush=True)
    except Exception:
        pass


def _is_protected(p):
    return p.suffix.lower() in (".html", ".js") or p.name.lower() == "manifest.json"


def _decode(value, suffix):
    s = value.strip()
    compact = "".join(s.split())
    if suffix in BINARY_SUFFIX:
        try:
            return base64.b64decode(compact, validate=True)
        except (binascii.Error, ValueError):
            return value.encode("utf-8")
    if s[:1] in ("{", "["):
        return s.encode("utf-8")
    if len(compact) >= 8 and len(compact) % 4 == 0:
        try:
            raw = base64.b64decode(compact, validate=True)
            raw.decode("utf-8")
            return raw
        except (binascii.Error, ValueError):
            pass
    return value.encode("utf-8")


def _load_map():
    m = dict(DEFAULT_MAP)
    extra = os.environ.get("RGON_SECRET_MAP", "").strip()
    if extra:
        try:
            d = json.loads(extra)
            if isinstance(d, dict):
                m.update({str(k): str(v) for k, v in d.items()})
        except Exception as e:
            _log("WARN", "RGON_SECRET_MAP 파싱 실패 — 기본 매핑만 사용 (%s)" % type(e).__name__)
    return m


def _run_legacy():
    if not LEGACY.exists():
        return None
    try:
        runpy.run_path(str(LEGACY), run_name="__main__")
        _log("INFO", "legacy 복원 로직 정상 완료")
        return True
    except SystemExit as e:
        if e.code in (None, 0):
            _log("INFO", "legacy 복원 로직 정상 종료")
            return True
        _log("WARN", "legacy 종료코드 %r — 궁변통구: 기본 복원 경로로 변통" % (e.code,))
        return False
    except Exception as e:
        _log("WARN", "legacy 예외 %s — 궁변통구: 기본 복원 경로로 변통" % type(e).__name__)
        return False


def _restore(only_missing=False):
    restored, skipped = 0, 0
    for env_name, rel in _load_map().items():
        val = os.environ.get(env_name)
        if not val or not val.strip():
            continue
        try:
            target = (ROOT / rel).resolve()
            target.relative_to(ROOT)
        except Exception:
            _log("WARN", "%s: 루트 밖 경로 거부" % env_name)
            continue
        if _is_protected(target):
            _log("WARN", "%s: 보호 파일 경로 거부" % env_name)
            continue
        if only_missing and target.exists():
            skipped += 1
            continue
        try:
            data = _decode(val, target.suffix.lower())
            if target.exists() and target.read_bytes() == data:
                skipped += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            restored += 1
            _log("INFO", "%s → %s 복원 완료" % (env_name, rel))
        except Exception as e:
            _log("WARN", "%s 복원 실패 %s — 건너뛰고 계속" % (env_name, type(e).__name__))
    return restored, skipped


def restore_all():
    _log("INFO", "궁변통구 자가치유 시크릿 복원 시작")
    legacy_ok = _run_legacy()
    restored, skipped = _restore(only_missing=bool(legacy_ok))
    if not legacy_ok and restored == 0 and skipped == 0:
        _log("WARN", "복원할 시크릿 환경변수가 없습니다 — 경고만 남기고 정상 진행(exit 0)")
    _log("INFO", "완료: restored=%d, skipped=%d, legacy=%s" % (restored, skipped, legacy_ok))
    return restored


if __name__ == "__main__":
    try:
        restore_all()
    except BaseException as e:
        _log("WARN", "예기치 않은 예외 %s — 궁변통구: 파이프라인 보호를 위해 정상 종료" % type(e).__name__)
    sys.exit(0)

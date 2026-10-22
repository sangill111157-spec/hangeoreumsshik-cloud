# -*- coding: utf-8 -*-
# RGON Step 11 과제 B-1: 6대 청사(D1~D6) 24시간 무인 박동(Heartbeat) 엔진 + GitHub Actions 무료 주방 설치기
# HTML 3곳과 rgon_constitution.json은 읽기만 하고 수정하지 않는다. 표준 라이브러리만 사용하며 네트워크 소켓은 쓰지 않는다.
import os, re, sys, json, hashlib, tempfile, datetime, subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"C:\Users\sangi\Downloads\shin-agent"
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
KST = datetime.timezone(datetime.timedelta(hours=9))
BOM = b"\xef\xbb\xbf"
BACKUP_DIR = os.path.join(ROOT, "backups")

HTML_RELS = ["rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html"]
SNAP_RELS = ["rgon_brain_snapshot.json", "dashboard/rgon_brain_snapshot.json", "docs/rgon_brain_snapshot.json"]
EVO_REL = "evolution_memory.json"
CONST_REL = "rgon_constitution.json"
TREASURY_REL = "treasury_ledger.json"
SCHEDULE_REL = "brain_basket/master_schedule.json"
PULSE_REL = "scripts/rgon_agency_pulse.py"
WF_REL = ".github/workflows/rgon_agency_pulse.yml"

PROTECTED_IDS = [
    "rgon-step5-solo-panel",
    "rgon-step7-chat-zone",
    "rgon-step8-constitution-bar",
    "rgon-step9-aggregator-board",
    "rgon-step10-agency-awaken",
    "dokdae-feed",
]
AGENCY_CODES = ["D1", "D2", "D3", "D4", "D5", "D6"]

# ======================================================================
# 1) 무인 박동 스크립트 본문 (scripts/rgon_agency_pulse.py)
# ======================================================================
PULSE_SRC = r'''# -*- coding: utf-8 -*-
"""RGON 6대 청사(D1~D6) 무인 박동(Heartbeat) 엔진
- 표준 라이브러리만 사용하고 네트워크와 유료 API는 쓰지 않는다.
- 독대실 HTML 3곳과 rgon_constitution.json은 읽기 전용이다(무접촉).
- rgon_brain_snapshot.json(루트/dashboard/docs)의 agency_pulse만 원자적으로 갱신한다(R13).
"""
import os, re, sys, json, hashlib, tempfile, datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.environ.get("RGON_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KST = datetime.timezone(datetime.timedelta(hours=9))
BOM = b"\xef\xbb\xbf"

HTML_RELS = ["rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html"]
SNAP_RELS = ["rgon_brain_snapshot.json", "dashboard/rgon_brain_snapshot.json", "docs/rgon_brain_snapshot.json"]
CONST_REL = "rgon_constitution.json"
TREASURY_REL = "treasury_ledger.json"
SCHEDULE_REL = "brain_basket/master_schedule.json"
AB_SCRIPT_ID = "rgon-step11-ab-realname"

PROTECTED_IDS = [
    "rgon-step5-solo-panel",
    "rgon-step7-chat-zone",
    "rgon-step8-constitution-bar",
    "rgon-step9-aggregator-board",
    "rgon-step10-agency-awaken",
    "dokdae-feed",
]

ANTIBODIES = {
    1: "PS 따옴표 함정 방지",
    2: "모바일 가로폭 보호",
    3: "체크박스 선택 보존",
    4: "정적 JSON 폴백",
    5: "서랍 빈여백 제거",
    6: "세로 글자 깨짐 방지",
    7: "배지 깜빡임 방지",
    8: "승인(Y) 전 코드 금지",
    9: "단일 코드블록 원칙",
    10: "자기참조 오판 방지",
    11: "최소 변경 Top1 선택",
    12: "중복 반복출력 금지",
    13: "0바이트 덮어쓰기 금지",
}

AGENCIES = [
    ("D1", "알파-D1 퀀트", "R&D · 4대 AI 교차검증 전광판 대기 상태 점검"),
    ("D2", "알파-D2 바이럴", "핵심 키워드 & BM 파이프라인 준비도 점검"),
    ("D3", "알파-D3 미디어", "브리핑 · TTS · 미디어 자산 상태 점검"),
    ("D4", "알파-D4 홍익", "제0조 홍익인간 원칙 & 헌법 v1.0 무결성 해시 점검"),
    ("D5", "알파-D5 가디언", "13대 항체(R1~R13) & 독대실 HTML 3곳 해시 일치 수호 점검"),
    ("D6", "알파-D6 트레저리", "treasury_ledger.json 금고 장부 무결성 & 무과금(Free Tier) 점검"),
]

RANK = {"OK": 0, "STANDBY": 1, "WARN": 2, "ALERT": 3}
MEDIA_DIRS = ["media", "assets", "audio", "tts", "briefings", "briefing",
              "dashboard/media", "docs/media", "dashboard/audio", "docs/audio"]
MEDIA_EXT = {".mp3", ".wav", ".ogg", ".m4a", ".mp4", ".webm", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


def p(rel):
    return os.path.join(ROOT, *rel.split("/"))


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def decode(data):
    if data.startswith(BOM):
        return data[len(BOM):].decode("utf-8"), True
    return data.decode("utf-8"), False


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    if not data:
        raise RuntimeError("R13 차단: 0바이트 기록 시도 -> %s" % path)
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".rgon_pulse_", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        if os.path.getsize(tmp) != len(data):
            raise RuntimeError("임시파일 크기 불일치 -> %s" % path)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass
    if os.path.getsize(path) != len(data):
        raise RuntimeError("기록 후 크기 검증 실패 -> %s" % path)


def id_pat(pid):
    return r"\bid\s*=\s*[\"']" + re.escape(pid) + r"[\"']"


def count_ids(text):
    return {pid: len(re.findall(id_pat(pid), text)) for pid in PROTECTED_IDS}


def load_json_rel(rel):
    path = p(rel)
    info = {"exists": False, "valid": False, "obj": None, "sha256": None, "bytes": 0, "bom": False, "error": None}
    if not os.path.isfile(path):
        return info
    raw = read_bytes(path)
    info.update({"exists": True, "bytes": len(raw), "sha256": sha256(raw)})
    try:
        txt, bom = decode(raw)
        info["bom"] = bom
        if not txt.strip():
            info["error"] = "empty"
            return info
        info["obj"] = json.loads(txt)
        info["valid"] = True
    except Exception as ex:
        info["error"] = str(ex)[:160]
    return info


def worst(statuses):
    return max(statuses, key=lambda s: RANK.get(s, 3)) if statuses else "OK"


def key_hits(obj, pattern, depth=0, limit=5):
    n = 0
    if depth > limit:
        return 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if re.search(pattern, str(k)):
                n += 1
            n += key_hits(v, pattern, depth + 1, limit)
    elif isinstance(obj, list):
        for v in obj[:500]:
            n += key_hits(v, pattern, depth + 1, limit)
    return n


def scan_html():
    files = {}
    for rel in HTML_RELS:
        path = p(rel)
        if not os.path.isfile(path):
            files[rel] = {"exists": False}
            continue
        raw = read_bytes(path)
        txt = decode(raw)[0]
        files[rel] = {
            "exists": True,
            "sha256": sha256(raw),
            "bytes": len(raw),
            "ids": count_ids(txt),
            "ab_script": bool(re.search(id_pat(AB_SCRIPT_ID), txt)),
        }
    ex = [f for f in files.values() if f.get("exists")]
    full = len(ex) == len(HTML_RELS)
    return {
        "files": files,
        "all_exist": full,
        "hash_unified": full and len(set(f["sha256"] for f in ex)) == 1,
        "ids_ok": full and all(all(v >= 1 for v in f["ids"].values()) for f in ex),
        "ab_script_all": full and all(f["ab_script"] for f in ex),
    }


def scan_media():
    found, count, seen = [], 0, 0
    for rel in MEDIA_DIRS:
        d = p(rel)
        if not os.path.isdir(d):
            continue
        found.append(rel)
        for base, dirs, names in os.walk(d):
            dirs[:] = [x for x in dirs if not x.startswith(".")]
            for nm in names:
                seen += 1
                if os.path.splitext(nm)[1].lower() in MEDIA_EXT:
                    count += 1
            if seen >= 5000:
                break
        if seen >= 5000:
            break
    return found, count


def check_antibodies(snap):
    recs = snap.get("antibody_realnames") if isinstance(snap, dict) else None
    ok, bad = [], []
    table = {}
    if isinstance(recs, list):
        for r in recs:
            if isinstance(r, dict) and isinstance(r.get("id"), str):
                table[r["id"]] = r
    for n, name in ANTIBODIES.items():
        r = table.get("R%d" % n)
        (ok if (r and r.get("name") == name) else bad).append("R%d" % n)
    return ok, bad


def build_pulse(snap, now):
    # R10: 직전 박동 기록(agency_pulse)을 뺀 상태로 점검한다(자기참조 오판 방지)
    base_snap = {k: v for k, v in snap.items() if k not in ("agency_pulse", "agency_pulse_updated")}
    prev = snap.get("agency_pulse") if isinstance(snap.get("agency_pulse"), dict) else {}
    prev_base = prev.get("baseline") if isinstance(prev.get("baseline"), dict) else {}

    html = scan_html()
    const = load_json_rel(CONST_REL)
    treasury = load_json_rel(TREASURY_REL)
    schedule = load_json_rel(SCHEDULE_REL)
    ab_ok, ab_bad = check_antibodies(base_snap)
    media_dirs, media_count = scan_media()

    agencies = {}

    # D1 퀀트
    f0 = [f for f in html["files"].values() if f.get("exists")]
    board = bool(f0) and all(f["ids"]["rgon-step9-aggregator-board"] >= 1 for f in f0)
    chat = bool(f0) and all(f["ids"]["rgon-step7-chat-zone"] >= 1 for f in f0)
    d1 = "OK" if (board and chat) else "WARN"
    agencies["D1"] = {"metrics": {"aggregator_board_present": board, "chat_zone_present": chat,
                                  "cross_validation_board": "대기(STANDBY-READY)" if board else "미탐지"}, "status": d1}

    # D2 바이럴
    kw = key_hits(base_snap, r"(?i)(keyword|키워드|(^|[_\-\s])bm($|[_\-\s])|pipeline|파이프라인)")
    if schedule["exists"] and not schedule["valid"]:
        d2 = "WARN"
    elif schedule["valid"] or kw > 0:
        d2 = "OK"
    else:
        d2 = "STANDBY"
    agencies["D2"] = {"metrics": {"master_schedule_exists": schedule["exists"], "master_schedule_valid": schedule["valid"],
                                  "keyword_bm_keys": kw}, "status": d2}

    # D3 미디어
    br = key_hits(base_snap, r"(?i)(brief|브리핑|tts|media|미디어)")
    d3 = "OK" if (media_count > 0 or br > 0) else "STANDBY"
    agencies["D3"] = {"metrics": {"media_dirs": media_dirs, "media_files": media_count, "briefing_keys": br}, "status": d3}

    # D4 홍익
    hongik = False
    if const["valid"]:
        hongik = "홍익" in json.dumps(const["obj"], ensure_ascii=False)
    baseline = prev_base.get("constitution_sha256")
    if os.environ.get("RGON_PULSE_RESET_BASELINE") == "1" or not baseline:
        baseline = const["sha256"]
    same = bool(const["sha256"]) and const["sha256"] == baseline
    if not const["exists"]:
        d4 = "ALERT"
    elif not const["valid"] or not same:
        d4 = "ALERT"
    elif not hongik:
        d4 = "WARN"
    else:
        d4 = "OK"
    agencies["D4"] = {"metrics": {"constitution_exists": const["exists"], "constitution_valid": const["valid"],
                                  "constitution_sha256": const["sha256"], "baseline_match": same,
                                  "article0_hongik_found": hongik}, "status": d4}

    # D5 가디언
    d5_flags = [html["hash_unified"], html["ids_ok"], len(ab_bad) == 0]
    d5 = "OK" if all(d5_flags) else ("ALERT" if not html["all_exist"] else "WARN")
    agencies["D5"] = {"metrics": {"html_all_exist": html["all_exist"], "html_hash_unified": html["hash_unified"],
                                  "protected_ids_ok": html["ids_ok"], "ab_realname_script_all": html["ab_script_all"],
                                  "antibodies_active": len(ab_ok), "antibodies_total": 13,
                                  "antibodies_need_check": ab_bad}, "status": d5}

    # D6 트레저리
    if not treasury["exists"]:
        d6 = "STANDBY"
    elif not treasury["valid"]:
        d6 = "WARN"
    else:
        d6 = "OK"
    agencies["D6"] = {"metrics": {"ledger_exists": treasury["exists"], "ledger_valid": treasury["valid"],
                                  "ledger_sha256": treasury["sha256"], "free_tier": True,
                                  "paid_api_calls": 0, "network_used": False}, "status": d6}

    for code, name, duty in AGENCIES:
        a = agencies[code]
        agencies[code] = {"code": code, "name": name, "duty": duty, "status": a["status"],
                          "checked_at": now, "metrics": a["metrics"]}

    beat = prev.get("beat_count") if isinstance(prev.get("beat_count"), int) else 0
    return {
        "version": "1.0",
        "engine": "scripts/rgon_agency_pulse.py",
        "runner": "github-actions" if os.environ.get("GITHUB_ACTIONS") == "true" else "local",
        "checked_at": now,
        "beat_count": beat + 1,
        "overall": worst([a["status"] for a in agencies.values()]),
        "network_used": False,
        "paid_api_calls": 0,
        "agencies": agencies,
        "html_integrity": {
            "hash_unified": html["hash_unified"],
            "protected_ids_ok": html["ids_ok"],
            "sha256": {rel: f.get("sha256") for rel, f in html["files"].items()},
        },
        "antibodies": {
            "active": len(ab_ok),
            "total": 13,
            "list": [{"id": "R%d" % n, "name": ANTIBODIES[n],
                      "status": "활성" if ("R%d" % n) in ab_ok else "점검필요"} for n in range(1, 14)],
        },
        "constitution": {"version": "v1.0", "sha256": const["sha256"]},
        "baseline": {"constitution_sha256": baseline},
    }


def dump(obj, bom):
    raw = (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    json.loads(raw.decode("utf-8"))
    return (BOM + raw) if bom else raw


def html_hashes():
    out = {}
    for rel in HTML_RELS:
        path = p(rel)
        out[rel] = sha256(read_bytes(path)) if os.path.isfile(path) else None
    return out


def run_pulse():
    if not os.path.isdir(ROOT):
        print("[PULSE-FAIL] ROOT 없음: %s" % ROOT)
        return 1
    before = html_hashes()
    now = datetime.datetime.now(KST).isoformat(timespec="seconds")

    root_info = load_json_rel(SNAP_RELS[0])
    if root_info["exists"] and (not root_info["valid"] or not isinstance(root_info["obj"], dict)):
        print("[PULSE-FAIL] 루트 스냅샷이 유효한 JSON 객체가 아닙니다. 덮어쓰지 않고 멈춥니다(R13).")
        return 2
    snap = root_info["obj"] if root_info["exists"] else {}

    pulse = build_pulse(snap, now)
    snap["agency_pulse"] = pulse
    snap["agency_pulse_updated"] = now
    atomic_write(p(SNAP_RELS[0]), dump(snap, root_info["bom"]))
    print("[PULSE] 기록: %s" % SNAP_RELS[0])

    for rel in SNAP_RELS[1:]:
        path = p(rel)
        if os.path.isfile(path):
            info = load_json_rel(rel)
            if info["valid"] and isinstance(info["obj"], dict):
                obj = info["obj"]
                obj["agency_pulse"] = pulse
                obj["agency_pulse_updated"] = now
                atomic_write(path, dump(obj, info["bom"]))
                print("[PULSE] 미러 기록: %s" % rel)
            else:
                print("[PULSE-WARN] 미러 JSON 무효, 원본 그대로 두고 건너뜀: %s" % rel)
        elif os.path.isdir(os.path.dirname(path)):
            atomic_write(path, dump(snap, root_info["bom"]))
            print("[PULSE] 미러 신규 생성: %s" % rel)

    after = html_hashes()
    if before != after:
        print("[PULSE-FAIL] 박동 중에 HTML 해시 변동이 감지되었습니다(이 엔진은 HTML을 쓰지 않습니다): %s" % after)
        return 3

    for code, name, duty in AGENCIES:
        print("[PULSE] %s %-12s %-7s | %s" % (code, name, pulse["agencies"][code]["status"], duty))
    print("[PULSE] 항체 %d/13 활성 · HTML 3곳 해시 일치=%s · 종합=%s"
          % (pulse["antibodies"]["active"], pulse["html_integrity"]["hash_unified"], pulse["overall"]))
    print("[PULSE-OK] 6대 청사 무인 박동 #%d 완료 (%s)" % (pulse["beat_count"], now))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run_pulse())
    except Exception as e:
        print("[PULSE-FAIL] 예기치 않은 오류: %s" % e)
        sys.exit(1)
'''

# ======================================================================
# 2) GitHub Actions 워크플로우 (.github/workflows/rgon_agency_pulse.yml)
# ======================================================================
WORKFLOW_SRC = r"""name: RGON Agency Pulse (6대 청사 무인 박동)

on:
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: rgon-agency-pulse
  cancel-in-progress: false

jobs:
  pulse:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run 6-agency pulse
        env:
          PYTHONIOENCODING: utf-8
        run: python scripts/rgon_agency_pulse.py

      - name: Commit and push snapshot
        run: |
          git config user.name "rgon-pulse-bot"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          for f in rgon_brain_snapshot.json dashboard/rgon_brain_snapshot.json docs/rgon_brain_snapshot.json; do
            if [ -f "$f" ]; then git add "$f"; fi
          done
          if git diff --cached --quiet; then
            echo "변경 없음 - 커밋 생략"
            exit 0
          fi
          git commit -m "chore(pulse): 6대 청사 무인 박동 갱신 [skip ci]"
          git pull --rebase origin "${GITHUB_REF_NAME}"
          git push origin "HEAD:${GITHUB_REF_NAME}"
"""

# ======================================================================
# 설치기 유틸
# ======================================================================
def log(msg):
    print(msg, flush=True)

def ap(rel):
    return os.path.join(ROOT, *rel.split("/"))

def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()

def decode(data):
    if data.startswith(BOM):
        return data[len(BOM):].decode("utf-8"), True
    return data.decode("utf-8"), False

def encode(text, bom):
    raw = text.encode("utf-8")
    return (BOM + raw) if bom else raw

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def atomic_write(path, data):
    if not data:
        raise RuntimeError("R13 차단: 0바이트 기록 시도 -> %s" % path)
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".rgon_tmp_", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        if os.path.getsize(tmp) != len(data):
            raise RuntimeError("임시파일 크기 불일치 -> %s" % path)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass
    if os.path.getsize(path) != len(data):
        raise RuntimeError("기록 후 크기 검증 실패 -> %s" % path)

def count_ids(text):
    out = {}
    for pid in PROTECTED_IDS:
        pat = r'\bid\s*=\s*["\']' + re.escape(pid) + r'["\']'
        out[pid] = len(re.findall(pat, text))
    return out

def capture_guard():
    """설치 과정에서 바뀌면 안 되는 파일(HTML 3곳, 헌법, 금고, 스케줄)의 해시와 보호 ID 개수를 저장"""
    g = {"html": {}, "readonly": {}}
    for rel in HTML_RELS:
        path = ap(rel)
        if not os.path.isfile(path):
            g["html"][rel] = None
            continue
        raw = read_bytes(path)
        g["html"][rel] = {"sha256": sha256(raw), "ids": count_ids(decode(raw)[0])}
    for rel in (CONST_REL, TREASURY_REL, SCHEDULE_REL):
        path = ap(rel)
        g["readonly"][rel] = sha256(read_bytes(path)) if os.path.isfile(path) else None
    return g

def backup_path(rel):
    parts = rel.split("/")
    base, ext = os.path.splitext(parts[-1])
    sub = parts[:-1]
    name = "%s_step11b1_bak_%s%s" % (base, TS, ext or ".bak")
    return os.path.join(BACKUP_DIR, *(sub + [name]))

def parse_iso(s):
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        return None

# ======================================================================
# 메인
# ======================================================================
def main():
    start_dt = datetime.datetime.now(KST) - datetime.timedelta(seconds=2)
    if not os.path.isdir(ROOT):
        log("[FAIL] ROOT 경로 없음: %s" % ROOT)
        return 1

    # 0) 설치 전 무결성 기준 저장
    pre = capture_guard()
    missing = [r for r, v in pre["html"].items() if v is None]
    if missing:
        log("[FAIL] 독대실 HTML이 없습니다: %s (중단)" % ", ".join(missing))
        return 1
    for rel, v in pre["html"].items():
        zero = [k for k, c in v["ids"].items() if c == 0]
        log("[GUARD] %-34s sha256 %s · 보호ID %d/6%s" % (
            rel, v["sha256"][:12], 6 - len(zero), (" (없음: %s)" % ", ".join(zero)) if zero else ""))
    if len(set(v["sha256"] for v in pre["html"].values())) != 1:
        log("[WARN] HTML 3곳 해시가 지금도 서로 다릅니다. 이번 과제에서는 HTML을 건드리지 않으므로 그대로 보존합니다.")
    if pre["readonly"][CONST_REL] is None:
        log("[WARN] %s 없음 → D4 홍익청사가 ALERT로 보고됩니다." % CONST_REL)

    # 1) G3 사전 백업과 원본 상태 저장(롤백용)
    touch_rels = SNAP_RELS + [EVO_REL, PULSE_REL, WF_REL]
    backup_only = [TREASURY_REL, SCHEDULE_REL]
    orig = {}
    for rel in touch_rels + backup_only:
        path = ap(rel)
        if os.path.isfile(path):
            data = read_bytes(path)
            if not data:
                log("[FAIL] R13: 원본이 0바이트입니다 → %s (중단)" % rel)
                return 1
            bp = backup_path(rel)
            atomic_write(bp, data)
            if read_bytes(bp) != data:
                log("[FAIL] 백업 검증 실패 → %s" % bp)
                return 1
            log("[BACKUP] %s → %s" % (rel, os.path.relpath(bp, ROOT)))
            if rel in touch_rels:
                orig[rel] = data
        elif rel in touch_rels:
            orig[rel] = None

    def rollback(reason):
        log("[ROLLBACK] %s" % reason)
        for rel in reversed(touch_rels):
            path = ap(rel)
            try:
                if orig.get(rel) is not None:
                    if not os.path.isfile(path) or read_bytes(path) != orig[rel]:
                        atomic_write(path, orig[rel])
                        log("  ↺ 복원: %s" % rel)
                elif os.path.isfile(path):
                    os.remove(path)
                    log("  ↺ 신규 파일 제거: %s" % rel)
            except Exception as ex:
                log("  !! 복원 실패: %s (%s) - backups/ 폴더에서 수동 복원 필요" % (rel, ex))
        log("[FAIL] Step 11 과제 B-1 중단: 백업본으로 복원했습니다")

    def guard_ok(stage):
        now = capture_guard()
        for rel in HTML_RELS:
            a, b = pre["html"][rel], now["html"][rel]
            if b is None or a["sha256"] != b["sha256"] or a["ids"] != b["ids"]:
                rollback("%s: HTML 무결성 변동 감지 → %s" % (stage, rel))
                return False
        for rel, h in pre["readonly"].items():
            if now["readonly"][rel] != h:
                rollback("%s: 읽기 전용 장부 변동 감지 → %s" % (stage, rel))
                return False
        return True

    try:
        # 2) 박동 스크립트와 워크플로우를 원자적으로 생성
        compile(PULSE_SRC, PULSE_REL, "exec")
        for rel, src in ((PULSE_REL, PULSE_SRC), (WF_REL, WORKFLOW_SRC)):
            data = src.replace("\r\n", "\n").encode("utf-8")
            if orig.get(rel) == data:
                log("[SKIP] %s 이미 최신" % rel)
                continue
            atomic_write(ap(rel), data)
            if read_bytes(ap(rel)) != data:
                raise RuntimeError("재판독 불일치 → %s" % rel)
            log("[CREATE] %s (%d bytes)" % (rel, len(data)))
        wf = read_bytes(ap(WF_REL)).decode("utf-8")
        for must in ("cron: '0 */6 * * *'", "workflow_dispatch", "contents: write", "python scripts/rgon_agency_pulse.py"):
            if must not in wf:
                raise RuntimeError("워크플로우 필수 항목 누락: %s" % must)
    except Exception as ex:
        rollback("파일 생성 실패: %s" % ex)
        return 1

    if not guard_ok("생성 단계"):
        return 1

    # 3) 첫 박동 1회 실행
    env = dict(os.environ)
    env["RGON_ROOT"] = ROOT
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        proc = subprocess.run([sys.executable, ap(PULSE_REL)], cwd=ROOT, env=env,
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    except Exception as ex:
        rollback("첫 박동 실행 실패: %s" % ex)
        return 1
    for line in (proc.stdout or "").splitlines():
        log("  " + line)
    if proc.stderr and proc.stderr.strip():
        for line in proc.stderr.strip().splitlines()[-10:]:
            log("  [stderr] " + line)
    if proc.returncode != 0:
        rollback("첫 박동 비정상 종료 (exit %d)" % proc.returncode)
        return 1

    if not guard_ok("박동 단계"):
        return 1

    # 4) 스냅샷 기록 검증
    try:
        snap = json.loads(decode(read_bytes(ap(SNAP_RELS[0])))[0])
        pulse = snap.get("agency_pulse")
        if not isinstance(pulse, dict) or not isinstance(pulse.get("agencies"), dict):
            raise RuntimeError("agency_pulse 구조 누락")
        for code in AGENCY_CODES:
            a = pulse["agencies"].get(code)
            if not isinstance(a, dict) or not a.get("status") or not a.get("checked_at"):
                raise RuntimeError("%s 점검 기록 누락" % code)
            t = parse_iso(a["checked_at"])
            if t is None or t < start_dt:
                raise RuntimeError("%s 점검 시각이 이번 실행보다 이전입니다: %s" % (code, a["checked_at"]))
        for rel in SNAP_RELS[1:]:
            path = ap(rel)
            if os.path.isfile(path):
                m = json.loads(decode(read_bytes(path))[0])
                if (m.get("agency_pulse") or {}).get("checked_at") != pulse["checked_at"]:
                    log("[WARN] 미러 박동 시각이 루트와 다릅니다(미러 JSON 무효로 건너뛰었을 수 있음): %s" % rel)
                else:
                    log("[VERIFY] 미러 동기화 확인: %s" % rel)
        log("[VERIFY] %s · D1~D6 점검 시각 %s · 종합 %s" % (SNAP_RELS[0], pulse["checked_at"], pulse.get("overall")))
    except Exception as ex:
        rollback("스냅샷 검증 실패: %s" % ex)
        return 1

    # 5) evolution_memory.json에 첫 박동 기록
    try:
        evo_path = ap(EVO_REL)
        if orig.get(EVO_REL) is not None:
            e_text, e_bom = decode(orig[EVO_REL])
            evo = json.loads(e_text) if e_text.strip() else {}
        else:
            evo, e_bom = {}, False
        entry = {
            "event": "step11_task_b1_agency_pulse_awaken",
            "timestamp": datetime.datetime.now(KST).isoformat(timespec="seconds"),
            "summary": "6대 청사(D1~D6) 24시간 무인 박동 엔진 + GitHub Actions 무료 주방(6시간 주기) 장착, 첫 박동 성공",
            "engine": PULSE_REL,
            "workflow": WF_REL,
            "schedule_cron": "0 */6 * * *",
            "first_pulse_at": pulse["checked_at"],
            "overall": pulse.get("overall"),
            "agencies": {c: {"name": pulse["agencies"][c].get("name"), "status": pulse["agencies"][c].get("status")}
                         for c in AGENCY_CODES},
            "antibodies_active": (pulse.get("antibodies") or {}).get("active"),
            "html_sha256_preserved": {rel: pre["html"][rel]["sha256"] for rel in HTML_RELS},
            "html_untouched": True,
            "backup_ts": TS,
        }
        if isinstance(evo, list):
            evo.append(entry)
        elif isinstance(evo, dict):
            target = None
            for k in ("history", "events", "log", "logs", "entries", "evolutions", "memory", "step_log"):
                if isinstance(evo.get(k), list):
                    target = evo[k]
                    break
            if target is None:
                if "step_log" in evo:
                    raise RuntimeError("step_log 키가 리스트가 아닙니다")
                target = evo.setdefault("step_log", [])
            target.append(entry)
        else:
            raise RuntimeError("지원하지 않는 장부 구조")
        out = json.dumps(evo, ensure_ascii=False, indent=2) + "\n"
        json.loads(out)
        data = encode(out, e_bom)
        atomic_write(evo_path, data)
        if read_bytes(evo_path) != data:
            raise RuntimeError("장부 재판독 불일치")
        log("[EVOLUTION] step11_task_b1_agency_pulse_awaken 기록 완료")
    except Exception as ex:
        rollback("evolution_memory 기록 실패: %s" % ex)
        return 1

    # 6) 최종 무결성 검증
    if not guard_ok("최종 단계"):
        return 1
    for rel in HTML_RELS:
        log("  - %-34s %s (무접촉 보존)" % (rel, pre["html"][rel]["sha256"]))
    log("[GUARD] HTML 3곳 SHA-256 및 보호 ID 설치 전후 100% 동일 · 헌법/금고/스케줄 장부 무변경")
    log("[OK] Step 11 과제 B-1 6대 청사 24시간 무인 박동 엔진 장착 및 첫 점검 완료 (HTML 3곳 무결성 100% 보존)")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("[FAIL] 예기치 않은 오류: %s" % e, flush=True)
        sys.exit(1)
Copy
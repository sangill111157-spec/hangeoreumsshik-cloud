# -*- coding: utf-8 -*-
# RGON Step 11 과제 A — 독대실 내장 스냅샷(R1~R13) 정화 + 6대 청사 미니카드 정화 + 3곳 동기화
import os, re, sys, json, tempfile, datetime, hashlib

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"C:\Users\sangi\Downloads\shin-agent"
HTML_TARGETS = [
    ("root", "rgon_alpha_chat.html"),
    ("dashboard", os.path.join("dashboard", "rgon_alpha_chat.html")),
    ("docs", os.path.join("docs", "rgon_alpha_chat.html")),
]
SNAPSHOT_REL = "rgon_brain_snapshot.json"
EVOLUTION_REL = "evolution_memory.json"
BACKUP_DIR = os.path.join(ROOT, "backups")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BOM = b"\xef\xbb\xbf"

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
    ("D1", "알파-D1 퀀트"),
    ("D2", "알파-D2 바이럴"),
    ("D3", "알파-D3 미디어"),
    ("D4", "알파-D4 홍익"),
    ("D5", "알파-D5 가디언"),
    ("D6", "알파-D6 트레저리"),
]

AGENCY_ANCHOR = "6대 청사 실시간 보좌 지표 보기"

# ---------------------------------------------------------------- 공통 유틸
def log(msg):
    print(msg, flush=True)

def abspath(rel):
    return os.path.join(ROOT, rel)

def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()

def decode(data):
    if data.startswith(BOM):
        return data[len(BOM):].decode("utf-8"), True
    return data.decode("utf-8"), False

def encode(text, has_bom):
    raw = text.encode("utf-8")
    return (BOM + raw) if has_bom else raw

def atomic_write_bytes(path, data):
    """R13: 0바이트 금지 + 동일 파일 동시 open 금지 → 임시파일 기록 후 os.replace"""
    if not data:
        raise RuntimeError("R13 위반 차단: 0바이트 기록 시도 → %s" % path)
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".rgon_tmp_", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        if os.path.getsize(tmp) != len(data):
            raise RuntimeError("임시파일 크기 불일치 → %s" % path)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass
    if os.path.getsize(path) != len(data):
        raise RuntimeError("기록 후 크기 검증 실패 → %s" % path)

def sha(data):
    return hashlib.sha256(data).hexdigest()[:12]

# ---------------------------------------------------------------- R10 보호 ID 카운트
def count_ids(text):
    out = {}
    for pid in PROTECTED_IDS:
        pat = r'\bid\s*=\s*["\']' + re.escape(pid) + r'["\']'
        out[pid] = len(re.findall(pat, text))
    return out

# ---------------------------------------------------------------- 항체 R1~R13 정화
EMOJI = r'(?:\U0001F6E1\uFE0F?|(?i:\\ud83d\\udee1(?:\\ufe0f)?))'
MARK_RE = re.compile(
    r'(?P<pre>' + EMOJI + r'?[ \t]*)R(?P<n>\d{1,2})[ \t]*·[ \t]*항체[ \t]*R(?P=n)[ \t]*·[ \t]*활성'
)
MAX_GAP = 200

def ab_item(pre, n):
    return "%sR%d · %s · 활성" % (pre, n, ANTIBODIES[n])

def purify_antibodies(text):
    matches = list(MARK_RE.finditer(text))
    if not matches:
        return text, 0
    runs, cur = [], [matches[0]]
    for m in matches[1:]:
        gap = text[cur[-1].end():m.start()]
        if len(gap) <= MAX_GAP and not re.search(r'\bid\s*=', gap):
            cur.append(m)
        else:
            runs.append(cur)
            cur = [m]
    runs.append(cur)

    replaced = 0
    for run in reversed(runs):
        nums = [int(m.group("n")) for m in run]
        if len(run) >= 2 and 1 in nums:
            pre = run[0].group("pre")
            sep = text[run[0].end():run[1].start()]
            block = sep.join(ab_item(pre, n) for n in range(1, 14))
            text = text[:run[0].start()] + block + text[run[-1].end():]
            replaced += len(run)
        else:
            for m in reversed(run):
                n = int(m.group("n"))
                if n in ANTIBODIES:
                    text = text[:m.start()] + ab_item(m.group("pre"), n) + text[m.end():]
                    replaced += 1
    return text, replaced

def purify_json_obj(obj):
    cnt = 0
    if isinstance(obj, dict):
        for k in list(obj.keys()):
            obj[k], c = purify_json_obj(obj[k])
            cnt += c
    elif isinstance(obj, list):
        for i in range(len(obj)):
            obj[i], c = purify_json_obj(obj[i])
            cnt += c
    elif isinstance(obj, str):
        new, c = purify_antibodies(obj)
        return new, c
    return obj, cnt

# ---------------------------------------------------------------- 6대 청사 상태 조회
def find_agency_status(snapshot, code, name):
    found = [None]
    keys = ("status", "state", "상태", "가동", "mode")

    def walk(o):
        if found[0] is not None:
            return
        if isinstance(o, dict):
            label = " ".join(str(v) for v in o.values() if isinstance(v, str))
            label += " " + " ".join(str(k) for k in o.keys())
            if (name in label) or re.search(r'(?<![A-Za-z0-9])' + code + r'(?![0-9])', label):
                for k in keys:
                    if k in o and isinstance(o[k], (str, int, float)) and str(o[k]).strip():
                        found[0] = str(o[k]).strip()
                        return
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    if snapshot is not None:
        walk(snapshot)
    st = found[0] or "실시간 가동중"
    st = re.sub(r'[<>"\'`$\\]', "", st)[:24] or "실시간 가동중"
    return st

def build_agency_phrases(snapshot):
    return ["%s · %s · 헌법 v1.0 / 항체 R1~R13 수호" % (name, find_agency_status(snapshot, code, name))
            for code, name in AGENCIES]

# ---------------------------------------------------------------- 6대 청사 미니카드 정화
DUMMY_RE = re.compile(
    r'(?:NVDA|BTC|ETH|TSLA|AAPL|MSFT|SPY|QQQ|SOL|XRP|KOSPI|KOSDAQ|NASDAQ|GOLD|USD/KRW)'
    r'\s*[:：]?\s*(?:₩|\$|USD\s*)?\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?'
    r'(?:\s*(?:원|USD))?(?:\s*\(?[+\-−]?\d+(?:\.\d+)?%\)?)?'
)
PROTECTED_ANY_RE = re.compile(
    r'\bid\s*=\s*["\'](?:' + "|".join(re.escape(p) for p in PROTECTED_IDS) + r')["\']'
)

def purify_agency_cards(text, phrases):
    regions, pos = [], 0
    while True:
        idx = text.find(AGENCY_ANCHOR, pos)
        if idx < 0:
            break
        end = min(len(text), idx + 8000)
        det = text.find("</details>", idx)
        if 0 <= det < idx + 20000:
            end = det
        pm = PROTECTED_ANY_RE.search(text, idx, end)
        if pm:
            end = pm.start()
        regions.append((idx, end))
        pos = idx + len(AGENCY_ANCHOR)
    if not regions:
        return text, 0, 0

    merged = []
    for s, e in sorted(regions):
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(e, merged[-1][1]))
        else:
            merged.append((s, e))

    total = 0
    for s, e in reversed(merged):
        seg = text[s:e]
        counter = [0]

        def repl(_m):
            i = counter[0]
            counter[0] += 1
            return phrases[i] if i < len(phrases) else "헌법 v1.0 · 항체 R1~R13 수호 지표 정상"

        new_seg = DUMMY_RE.sub(repl, seg)
        total += counter[0]
        text = text[:s] + new_seg + text[e:]
    return text, total, len(merged)

# ---------------------------------------------------------------- 백업 경로
def backup_path_for(tag, rel):
    if rel.endswith(".html"):
        name = "rgon_alpha_chat_step11_bak_%s.html" % TS
        return os.path.join(BACKUP_DIR, name) if tag == "root" else os.path.join(BACKUP_DIR, tag, name)
    base = os.path.splitext(os.path.basename(rel))[0]
    return os.path.join(BACKUP_DIR, "%s_step11_bak_%s.json" % (base, TS))

# ---------------------------------------------------------------- 메인
def main():
    if not os.path.isdir(ROOT):
        log("[FAIL] ROOT 경로 없음: %s" % ROOT)
        return 1

    files = []  # (tag, rel, abs)
    for tag, rel in HTML_TARGETS:
        p = abspath(rel)
        if os.path.isfile(p):
            files.append((tag, rel, p))
        else:
            log("[WARN] HTML 대상 없음(건너뜀): %s" % rel)
    if not any(r.endswith(".html") for _, r, _ in files):
        log("[FAIL] 동기화 대상 HTML이 하나도 없습니다.")
        return 1
    for rel in (SNAPSHOT_REL, EVOLUTION_REL):
        p = abspath(rel)
        if os.path.isfile(p):
            files.append(("json", rel, p))
        else:
            log("[WARN] 장부 없음(건너뜀): %s" % rel)

    # 1) G3 사전 백업
    originals, backups = {}, {}
    for tag, rel, p in files:
        data = read_bytes(p)
        if not data:
            log("[FAIL] R13: 원본이 0바이트입니다 → %s (중단)" % rel)
            return 1
        originals[p] = data
        bp = backup_path_for(tag, rel)
        atomic_write_bytes(bp, data)
        if read_bytes(bp) != data:
            log("[FAIL] 백업 검증 실패 → %s" % bp)
            return 1
        backups[p] = bp
        log("[BACKUP] %s → %s" % (rel, os.path.relpath(bp, ROOT)))

    written = []

    def rollback(reason):
        log("[ROLLBACK] %s" % reason)
        for wp in reversed(written):
            try:
                atomic_write_bytes(wp, read_bytes(backups[wp]))
                log("  ↺ 복원: %s" % os.path.relpath(wp, ROOT))
            except Exception as ex:
                log("  !! 복원 실패: %s (%s) — 백업본 수동 확인: %s" % (wp, ex, backups[wp]))

    # 2) 스냅샷 로드 + 정화
    snap_path = abspath(SNAPSHOT_REL)
    snapshot_obj = None
    new_contents = {}
    if snap_path in originals:
        s_text, s_bom = decode(originals[snap_path])
        try:
            snapshot_obj = json.loads(s_text)
        except Exception as ex:
            log("[WARN] 스냅샷 JSON 파싱 실패 → 스냅샷 정화 생략 (%s)" % ex)
            s_text = None
        if s_text is not None:
            new_s, c = purify_antibodies(s_text)
            if c:
                try:
                    snapshot_obj = json.loads(new_s)
                except Exception as ex:
                    log("[FAIL] 스냅샷 정화 결과 JSON 무효 → 중단 (%s)" % ex)
                    return 1
            else:
                obj_copy = json.loads(s_text)
                obj_copy, c = purify_json_obj(obj_copy)
                if c:
                    new_s = json.dumps(obj_copy, ensure_ascii=False, indent=2) + "\n"
                    snapshot_obj = obj_copy
            if c:
                new_contents[snap_path] = encode(new_s, s_bom)
            log("[SNAPSHOT] 항체 구형 표기 정화: %d건" % c)

    phrases = build_agency_phrases(snapshot_obj)

    # 3) HTML 3곳 정화 (메모리 내)
    html_before_ids = {}
    for tag, rel, p in files:
        if not rel.endswith(".html"):
            continue
        text, bom = decode(originals[p])
        before = count_ids(text)
        html_before_ids[p] = before
        zero = [k for k, v in before.items() if v == 0]
        if zero:
            log("[WARN] %s: 원본에 보호 ID 없음 → %s" % (rel, ", ".join(zero)))
        t1, c_ab = purify_antibodies(text)
        t2, c_ag, n_reg = purify_agency_cards(t1, phrases)
        after = count_ids(t2)
        if after != before:
            log("[FAIL] R10: %s 메모리 검증 단계 보호 ID 변동 감지 → 기록 전 중단" % rel)
            for pid in PROTECTED_IDS:
                if before[pid] != after[pid]:
                    log("  - %s: %d → %d" % (pid, before[pid], after[pid]))
            return 1
        if not t2.strip():
            log("[FAIL] R13: %s 결과가 비어 있음 → 중단" % rel)
            return 1
        log("[HTML] %-40s 항체정화 %d건 · 청사카드 영역 %d곳 / 더미값 %d건" % (rel, c_ab, n_reg, c_ag))
        if t2 != text:
            new_contents[p] = encode(t2, bom)

    # 4) 원자적 기록 + 사후 검증
    try:
        for p, data in new_contents.items():
            atomic_write_bytes(p, data)
            written.append(p)
            check = read_bytes(p)
            if check != data:
                raise RuntimeError("재판독 불일치 → %s" % p)
            if p in html_before_ids:
                ids_now = count_ids(decode(check)[0])
                if ids_now != html_before_ids[p]:
                    raise RuntimeError("R10 보호 ID 변동 → %s" % os.path.relpath(p, ROOT))
            if p.endswith(".json"):
                json.loads(decode(check)[0])
            log("[WRITE] %s (%s → %s)" % (os.path.relpath(p, ROOT), sha(originals[p]), sha(data)))
    except Exception as ex:
        rollback(str(ex))
        log("[FAIL] Step 11 과제 A 중단 — 백업본 복원 완료")
        return 1

    # 5) 최종 보호 ID 전수 재검증
    for p, before in html_before_ids.items():
        now = count_ids(decode(read_bytes(p))[0])
        if now != before:
            rollback("최종 검증 보호 ID 변동 → %s" % os.path.relpath(p, ROOT))
            log("[FAIL] Step 11 과제 A 중단 — 백업본 복원 완료")
            return 1

    # 6) 3곳 동기화 상태 리포트
    hashes = {os.path.relpath(p, ROOT): sha(read_bytes(p)) for p in html_before_ids}
    if len(set(hashes.values())) == 1:
        log("[SYNC] HTML %d곳 내용 완전 일치 (%s)" % (len(hashes), list(hashes.values())[0]))
    else:
        log("[SYNC] 동일 정화 규칙 적용 완료 (원본 차이로 해시 상이):")
        for k, v in hashes.items():
            log("  - %s : %s" % (k, v))

    # 7) evolution_memory.json 장부 기록
    evo_path = abspath(EVOLUTION_REL)
    if evo_path in originals:
        try:
            e_text, e_bom = decode(originals[evo_path])
            evo = json.loads(e_text) if e_text.strip() else {}
            entry = {
                "event": "step11_task_a_purify",
                "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                "summary": "독대실 내장 스냅샷 항체 R1~R13 한글 실명 정화 + 6대 청사 미니카드 구형 더미값 정화 + HTML 3곳 동기화",
                "antibodies": ["R%d %s" % (n, ANTIBODIES[n]) for n in range(1, 14)],
                "agencies": phrases,
                "files_changed": [os.path.relpath(p, ROOT) for p in written],
                "protected_ids_intact": True,
                "backup_ts": TS,
            }
            if isinstance(evo, list):
                evo.append(entry)
            elif isinstance(evo, dict):
                target = None
                for k in ("history", "events", "log", "logs", "entries", "evolutions", "memory"):
                    if isinstance(evo.get(k), list):
                        target = evo[k]
                        break
                if target is None:
                    target = evo.setdefault("step_log", [])
                    if not isinstance(target, list):
                        raise RuntimeError("step_log 키가 리스트가 아님")
                target.append(entry)
            else:
                raise RuntimeError("지원하지 않는 장부 구조")
            out = json.dumps(evo, ensure_ascii=False, indent=2) + "\n"
            json.loads(out)
            atomic_write_bytes(evo_path, encode(out, e_bom))
            log("[EVOLUTION] 장부 기록 완료: %s" % EVOLUTION_REL)
        except Exception as ex:
            try:
                atomic_write_bytes(evo_path, originals[evo_path])
            except Exception:
                pass
            log("[WARN] evolution_memory 기록 생략(원본 유지): %s" % ex)

    log("[OK] Step 11 과제 A 정화 및 3곳 동기화 완료 (보호 ID 100% 무결)")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("[FAIL] 예기치 않은 오류: %s" % e, flush=True)
        sys.exit(1)
Copy
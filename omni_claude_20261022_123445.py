# -*- coding: utf-8 -*-
# RGON Step 11 과제 B-2: 누락 보호 ID 2종 정적 복원 + 6대 청사 ALL OK 검증 + GitHub 클라우드 동기화
# 변경 방식은 삽입만 사용한다(기존 문자는 1글자도 지우지 않음). 헌법, 박동 엔진, 워크플로우는 읽기 전용으로 둔다.
import os, re, sys, json, bisect, shutil, hashlib, tempfile, datetime, subprocess

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
PULSE_REL = "scripts/rgon_agency_pulse.py"
WF_REL = ".github/workflows/rgon_agency_pulse.yml"
TOUCH_RELS = HTML_RELS + SNAP_RELS + [EVO_REL]
READONLY_RELS = [CONST_REL, PULSE_REL, WF_REL]
GIT_BRANCH = "main"

PROTECTED_IDS = [
    "rgon-step5-solo-panel",
    "rgon-step7-chat-zone",
    "rgon-step8-constitution-bar",
    "rgon-step9-aggregator-board",
    "rgon-step10-agency-awaken",
    "dokdae-feed",
]
RESTORE_IDS = ["rgon-step7-chat-zone", "dokdae-feed"]
CLASS_ALIASES = {
    "rgon-step7-chat-zone": {"rgon-step7-chat-zone", "step7-chat-zone", "chat-zone", "rgon-chat-zone"},
    "dokdae-feed": {"dokdae-feed", "dokdae_feed", "dokdaeFeed", "rgon-dokdae-feed"},
}
AGENCY_CODES = ["D1", "D2", "D3", "D4", "D5", "D6"]
ANTIBODIES = {
    1: "PS 따옴표 함정 방지", 2: "모바일 가로폭 보호", 3: "체크박스 선택 보존", 4: "정적 JSON 폴백",
    5: "서랍 빈여백 제거", 6: "세로 글자 깨짐 방지", 7: "배지 깜빡임 방지", 8: "승인(Y) 전 코드 금지",
    9: "단일 코드블록 원칙", 10: "자기참조 오판 방지", 11: "최소 변경 Top1 선택", 12: "중복 반복출력 금지",
    13: "0바이트 덮어쓰기 금지",
}
ANCHOR_ATTR = 'data-rgon-anchor="step11-b2"'
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

# ======================================================================
# 공통 유틸
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

def id_pat(pid):
    return r'\bid\s*=\s*["\']' + re.escape(pid) + r'["\']'

def raw_counts(text):
    return {pid: len(re.findall(id_pat(pid), text)) for pid in PROTECTED_IDS}

# ======================================================================
# R10: 실제 태그 속성만 센다(script, style, 주석 안의 문자열은 제외)
# ======================================================================
MASK_RE = re.compile(r'<script\b.*?</script\s*>|<style\b.*?</style\s*>|<!--.*?-->', re.S | re.I)

def mask_spans(text):
    spans = [(m.start(), m.end()) for m in MASK_RE.finditer(text)]
    return spans, [s for s, _ in spans]

def in_spans(pos, spans_pack):
    spans, starts = spans_pack
    i = bisect.bisect_right(starts, pos) - 1
    return i >= 0 and spans[i][0] < pos < spans[i][1]

def in_tag(text, pos):
    return text.rfind("<", 0, pos) > text.rfind(">", 0, pos)

def tag_id_positions(text, pid, sp):
    return [m.start() for m in re.finditer(id_pat(pid), text)
            if not in_spans(m.start(), sp) and in_tag(text, m.start())]

def tag_counts(text):
    sp = mask_spans(text)
    return {pid: len(tag_id_positions(text, pid, sp)) for pid in PROTECTED_IDS}

def snippet_of_opening(text, pos):
    lt = text.rfind("<", 0, pos)
    gt = text.find(">", pos)
    m = re.match(r"<([a-zA-Z][a-zA-Z0-9-]*)", text[lt:lt + 64])
    if lt < 0 or gt < 0 or not m:
        return None
    return {"start": lt, "end": gt + 1, "tag": m.group(1)}

def element_end(text, op, sp):
    tag = op["tag"]
    if tag.lower() in VOID_TAGS or text[op["end"] - 2] == "/":
        return op["end"]
    pat = re.compile(r"<(/?)" + re.escape(tag) + r"(?=[\s>/])", re.I)
    depth = 1
    for m in pat.finditer(text, op["end"]):
        if in_spans(m.start(), sp):
            continue
        gt = text.find(">", m.end())
        if gt < 0:
            return None
        if m.group(1):
            depth -= 1
            if depth == 0:
                return gt + 1
        elif text[gt - 1] != "/":
            depth += 1
    return None

# ======================================================================
# 누락 원인 진단
# ======================================================================
def diagnose(text, pid):
    q = r'["\'`]'
    e = re.escape(pid)
    sp = mask_spans(text)
    pats = [
        ("JS getElementById 참조", r"getElementById\(\s*" + q + e + q),
        ("JS querySelector #참조", r"querySelector(?:All)?\(\s*" + q + r"[^\"'`]*#" + e + r"(?![\w-])"),
        ("JS .id 동적 부여", r"\.id\s*=\s*" + q + e + q),
        ("JS setAttribute 동적 부여", r"setAttribute\(\s*[\"']id[\"']\s*,\s*" + q + e + q),
        ("JS 템플릿 id=`...`", r"\bid\s*=\s*\\?[\"']?\s*`\s*" + e),
        ("CSS #선택자", r"#" + e + r"(?![\w-])"),
    ]
    found = {}
    for label, pat in pats:
        n = len(re.findall(pat, text))
        if n:
            found[label] = n
    cls = 0
    for m in re.finditer(r'(?<![\w-])class\s*=\s*(["\'])(.*?)\1', text, re.S):
        if not in_spans(m.start(), sp) and set(m.group(2).split()) & CLASS_ALIASES.get(pid, {pid}):
            cls += 1
    return {
        "raw_attr": len(re.findall(id_pat(pid), text)),
        "tag_attr": len(tag_id_positions(text, pid, sp)),
        "plain_mentions": text.count(pid),
        "class_matches": cls,
        "js_css_refs": found,
    }

def explain(d):
    if d["tag_attr"] > 0:
        return "정상(태그 속성 존재)"
    if d["raw_attr"] > 0:
        return "script/주석 문자열 안에만 존재(JS 동적 생성 추정)"
    if d["js_css_refs"]:
        return "JS/CSS에서 참조만 하고 정적 태그 속성은 없음"
    if d["class_matches"]:
        return "클래스명으로만 존재(id 속성 누락)"
    if d["plain_mentions"]:
        return "문자열 언급만 있고 태그 속성 없음"
    return "HTML 전체에서 흔적 없음(과거 편집 중 소실 추정)"

# ======================================================================
# 정적 복원 계획 (삽입만 사용)
# ======================================================================
OPEN_TAG_RE = re.compile(r"<([a-zA-Z][a-zA-Z0-9-]*)(\s[^<>]*?)?(/?)>", re.S)

def class_candidates(text, pid, sp):
    out = []
    aliases = CLASS_ALIASES.get(pid, {pid})
    for m in OPEN_TAG_RE.finditer(text):
        if in_spans(m.start(), sp):
            continue
        attrs = m.group(2) or ""
        if re.search(r'(?<![\w-])id\s*=', attrs):
            continue
        cm = re.search(r'(?<![\w-])class\s*=\s*(["\'])(.*?)\1', attrs, re.S)
        if cm and set(cm.group(2).split()) & aliases:
            out.append(m)
    return out

def anchor_position(text, sp):
    for pid in ("rgon-step9-aggregator-board", "rgon-step8-constitution-bar"):
        pos = tag_id_positions(text, pid, sp)
        if pos:
            op = snippet_of_opening(text, pos[0])
            if op:
                end = element_end(text, op, sp)
                if end:
                    return end, "#%s 바로 아래" % pid
    m = re.search(r'<script\b[^>]*\bid\s*=\s*["\']rgon-step11-ab-realname["\']', text, re.I)
    if m:
        return m.start(), "동적 항체 패치 스크립트 직전"
    idx = text.lower().rfind("</body>")
    if idx >= 0:
        return idx, "</body> 직전"
    return None, None

def build_restore(text):
    sp = mask_spans(text)
    counts = tag_counts(text)
    missing = [pid for pid in RESTORE_IDS if counts[pid] == 0]
    edits, notes = [], []
    for pid in list(missing):
        c = class_candidates(text, pid, sp)
        if len(c) == 1:
            m = c[0]
            edits.append((m.start() + 1 + len(m.group(1)), ' id="%s"' % pid))
            notes.append("%s: 기존 <%s class=...> 컨테이너에 id 부여" % (pid, m.group(1)))
            missing.remove(pid)
        elif len(c) > 1:
            notes.append("%s: 클래스 후보 %d개라 오부여 위험이 있어 앵커 방식 사용" % (pid, len(c)))
    if missing:
        pos, where = anchor_position(text, sp)
        if pos is None:
            raise RuntimeError("비침투 앵커 장착 위치를 찾지 못했습니다")
        if missing == ["rgon-step7-chat-zone", "dokdae-feed"]:
            block = ('<div id="rgon-step7-chat-zone" style="display:contents;" %s>'
                     '<div id="dokdae-feed" style="display:contents;" %s></div></div>' % (ANCHOR_ATTR, ANCHOR_ATTR))
        else:
            block = "".join('<div id="%s" style="display:contents;" %s></div>' % (pid, ANCHOR_ATTR) for pid in missing)
        edits.append((pos, block))
        notes.append("%s: display:contents 비침투 앵커 장착(%s, 공백 텍스트 노드 0개)" % (", ".join(missing), where))
    for pos, _ in edits:
        if in_spans(pos, sp):
            raise RuntimeError("삽입 위치가 script/style 내부입니다 -> 중단")
    new = text
    for pos, s in sorted(edits, key=lambda x: x[0], reverse=True):
        new = new[:pos] + s + new[pos:]
    return new, edits, notes

def strip_old_anchors(text):
    """재실행할 때 이전 B-2 앵커가 겹치지 않도록 제거한다(R12)"""
    pat = re.compile(r'<div id="rgon-step7-chat-zone" style="display:contents;" ' + re.escape(ANCHOR_ATTR) +
                     r'><div id="dokdae-feed" style="display:contents;" ' + re.escape(ANCHOR_ATTR) + r'></div></div>'
                     r'|<div id="(?:rgon-step7-chat-zone|dokdae-feed)" style="display:contents;" ' +
                     re.escape(ANCHOR_ATTR) + r'></div>')
    return pat.subn("", text)

def realname_records():
    return [{"id": "R%d" % n, "name": ANTIBODIES[n], "label": "R%d: %s" % (n, ANTIBODIES[n]), "status": "활성"}
            for n in range(1, 14)]

def backup_path(rel):
    parts = rel.split("/")
    base, ext = os.path.splitext(parts[-1])
    return os.path.join(BACKUP_DIR, *(parts[:-1] + ["%s_step11b2_bak_%s%s" % (base, TS, ext or ".bak")]))

# ======================================================================
# Git
# ======================================================================
GIT_ENV = dict(os.environ)
GIT_ENV["GIT_TERMINAL_PROMPT"] = "0"
GIT_ENV["LC_ALL"] = "C.UTF-8"

def git(args, timeout=180):
    p = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=GIT_ENV, timeout=timeout)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()

def git_tail(out, err, n=6):
    lines = (out + "\n" + err).strip().splitlines()
    for ln in lines[-n:]:
        log("    | " + ln)

def verify_after_rebase(expect_html_sha):
    for rel in HTML_RELS:
        if sha256(read_bytes(ap(rel))) != expect_html_sha:
            return "리베이스 후 HTML 해시가 정본과 다릅니다: %s" % rel
    for rel in SNAP_RELS + [EVO_REL]:
        path = ap(rel)
        if os.path.isfile(path):
            try:
                json.loads(decode(read_bytes(path))[0])
            except Exception as ex:
                return "리베이스 후 JSON 무효: %s (%s)" % (rel, ex)
    return None

def git_sync(paths, expect_html_sha):
    if not shutil.which("git"):
        return False, "git 실행 파일을 찾지 못했습니다"
    rc, out, err = git(["rev-parse", "--is-inside-work-tree"])
    if rc != 0 or out != "true":
        return False, "ROOT가 git 저장소가 아닙니다"
    rc, br, _ = git(["rev-parse", "--abbrev-ref", "HEAD"])
    if br != GIT_BRANCH:
        return False, "현재 브랜치가 '%s'입니다. main에서만 push하도록 막혀 있습니다" % br
    rc, url, _ = git(["remote", "get-url", "origin"])
    if rc != 0:
        return False, "origin 원격 저장소가 없습니다"
    log("[GIT] origin = %s · branch = %s" % (url, br))

    ident = []
    if not git(["config", "user.email"])[1]:
        ident = ["-c", "user.name=rgon-local", "-c", "user.email=rgon-local@users.noreply.github.com"]

    rc, out, err = git(["add", "--"] + paths)
    if rc != 0:
        git_tail(out, err)
        return False, "git add 실패"
    rc, _, _ = git(["diff", "--cached", "--quiet", "--"] + paths)
    if rc == 1:
        msg = "feat(step11-b2): 보호 ID 6/6 정적 복원 · 6대 청사 ALL OK · HTML 3곳 해시 통일"
        rc, out, err = git(ident + ["commit", "-m", msg, "--"] + paths)
        if rc != 0:
            git_tail(out, err)
            return False, "git commit 실패"
        log("[GIT] commit %s" % git(["rev-parse", "--short", "HEAD"])[1])
    else:
        log("[GIT] 새로 커밋할 변경 없음 → push만 확인")

    rc, out, err = git(["push", "origin", GIT_BRANCH])
    if rc != 0:
        log("[GIT] push 거절됨 → 원격 최신(박동 봇 커밋 등) 반영 후 재시도")
        git_tail(out, err, 3)
        rc, out, err = git(ident + ["pull", "--rebase", "--autostash", "origin", GIT_BRANCH])
        if rc != 0:
            git(["rebase", "--abort"])
            log("[GIT] 일반 리베이스 충돌 → 로컬 최신 박동 우선(-X theirs)으로 재시도")
            rc, out, err = git(ident + ["pull", "--rebase", "--autostash", "-X", "theirs", "origin", GIT_BRANCH])
            if rc != 0:
                git(["rebase", "--abort"])
                git_tail(out, err)
                return False, "리베이스 실패(로컬 커밋은 그대로 보존)"
        bad = verify_after_rebase(expect_html_sha)
        if bad:
            return False, bad + " (push 보류)"
        rc, out, err = git(["push", "origin", GIT_BRANCH])
        if rc != 0:
            git_tail(out, err)
            return False, "git push 재시도 실패(인증 또는 권한 확인 필요)"
    git(["fetch", "origin", GIT_BRANCH], timeout=120)
    h1 = git(["rev-parse", "HEAD"])[1]
    h2 = git(["rev-parse", "origin/" + GIT_BRANCH])[1]
    if not h1 or h1 != h2:
        return False, "push 이후 HEAD와 origin/main이 다릅니다 (%s vs %s)" % (h1[:10], h2[:10])
    return True, h1[:10]

# ======================================================================
# 메인
# ======================================================================
def main():
    start_dt = datetime.datetime.now(KST) - datetime.timedelta(seconds=2)
    if not os.path.isdir(ROOT):
        log("[FAIL] ROOT 경로 없음: %s" % ROOT)
        return 1
    for rel in HTML_RELS + [PULSE_REL]:
        if not os.path.isfile(ap(rel)):
            log("[FAIL] 필수 파일 없음: %s" % rel)
            return 1
    if not os.path.isfile(ap(WF_REL)):
        log("[WARN] 워크플로우 없음: %s (push 대상에서 제외)" % WF_REL)

    readonly_hash = {rel: (sha256(read_bytes(ap(rel))) if os.path.isfile(ap(rel)) else None) for rel in READONLY_RELS}

    # 1) G3 사전 백업
    orig = {}
    for rel in TOUCH_RELS + READONLY_RELS:
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
            if rel in TOUCH_RELS:
                orig[rel] = data
        elif rel in TOUCH_RELS:
            orig[rel] = None

    def rollback(reason):
        log("[ROLLBACK] %s" % reason)
        for rel in reversed(TOUCH_RELS):
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
                log("  !! 복원 실패: %s (%s) → backups/ 폴더에서 수동 복원 필요" % (rel, ex))
        log("[FAIL] Step 11 과제 B-2 중단: 백업본으로 복원했습니다")

    def readonly_ok():
        for rel, h in readonly_hash.items():
            now = sha256(read_bytes(ap(rel))) if os.path.isfile(ap(rel)) else None
            if now != h:
                return rel
        return None

    # 2) 정본 선정과 누락 원인 진단
    cands = []
    for rel in HTML_RELS:
        text, bom = decode(orig[rel])
        tc = tag_counts(text)
        alive = sum(1 for v in tc.values() if v > 0)
        cands.append({"rel": rel, "text": text, "bom": bom, "tc": tc, "raw": raw_counts(text),
                      "score": (1 if tc["rgon-step10-agency-awaken"] else 0, alive, sum(tc.values()),
                                os.path.getmtime(ap(rel)))})
        log("[SCAN] %-34s sha256 %s · 태그 보호ID %d/6" % (rel, sha256(orig[rel])[:12], alive))
    cands.sort(key=lambda c: c["score"], reverse=True)
    canon = cands[0]
    if canon["tc"]["rgon-step10-agency-awaken"] == 0:
        log("[FAIL] Step 10(rgon-step10-agency-awaken) 포함 정본 없음 → 중단")
        return 1
    log("[CANON] 정본: %s" % canon["rel"])

    for pid in RESTORE_IDS:
        d = diagnose(canon["text"], pid)
        refs = ", ".join("%s %d" % kv for kv in d["js_css_refs"].items()) or "없음"
        log("[DIAG] %-22s 태그속성 %d · 전체매칭 %d · 언급 %d · 클래스 %d · 참조[%s] → %s" % (
            pid, d["tag_attr"], d["raw_attr"], d["plain_mentions"], d["class_matches"], refs, explain(d)))
        if d["tag_attr"] == 0 and d["js_css_refs"]:
            log("[WARN] %s 는 JS/CSS가 참조합니다. 복원 후 독대실 화면에서 대화창과 피드 위치를 꼭 확인하십시오." % pid)

    # 3) 메모리 안에서 복원(삽입만)
    try:
        base_text, removed = strip_old_anchors(canon["text"])
        if removed:
            log("[R12] 이전 B-2 앵커 %d개를 정리한 뒤 다시 장착" % removed)
        new_text, edits, notes = build_restore(base_text)
    except Exception as ex:
        log("[FAIL] 복원 계획 실패(아무 파일도 수정하지 않음): %s" % ex)
        return 1
    for n in notes:
        log("[RESTORE] " + n)
    if not edits:
        log("[RESTORE] 정본에 보호 ID가 이미 6/6 있어 HTML은 정본 그대로 동기화")

    if len(new_text) != len(base_text) + sum(len(s) for _, s in edits):
        log("[FAIL] Minimal Diff 검증 실패(삽입 외 변경 감지) → 기록 전 중단")
        return 1
    after_tc, after_raw = tag_counts(new_text), raw_counts(new_text)
    lacking = [pid for pid in PROTECTED_IDS if after_tc[pid] < 1]
    dropped = [pid for pid in PROTECTED_IDS
               if after_tc[pid] < canon["tc"][pid] or after_raw[pid] < canon["raw"][pid] - removed]
    if lacking or dropped:
        log("[FAIL] R10: 보호 ID 검증 실패 → 기록 전 중단 (미달: %s / 감소: %s)" %
            (", ".join(lacking) or "-", ", ".join(dropped) or "-"))
        return 1
    for pid in PROTECTED_IDS:
        if after_tc[pid] > 1:
            log("[WARN] %s 태그 속성이 %d개입니다(중복 id)" % (pid, after_tc[pid]))
    canon_bytes = encode(new_text, canon["bom"])
    canon_sha = sha256(canon_bytes)
    log("[HTML] 보호 ID 6/6 확보 · 삽입 %d곳 · +%d bytes · 정본 sha256 %s" %
        (len(edits), len(canon_bytes) - len(orig[canon["rel"]]), canon_sha[:12]))

    # 4) HTML 3곳 원자적 기록 + 스냅샷 항체 실명 보정
    try:
        for rel in HTML_RELS:
            if orig[rel] == canon_bytes:
                log("[SKIP] %s 이미 정본과 동일" % rel)
                continue
            atomic_write(ap(rel), canon_bytes)
            if sha256(read_bytes(ap(rel))) != canon_sha:
                raise RuntimeError("SHA-256 재판독 불일치 → %s" % rel)
            log("[WRITE] %s (sha256 %s)" % (rel, canon_sha[:12]))
        hs = {rel: sha256(read_bytes(ap(rel))) for rel in HTML_RELS}
        if len(set(hs.values())) != 1:
            raise RuntimeError("HTML 3곳 해시 불일치: %s" % hs)

        sp = ap(SNAP_RELS[0])
        if orig.get(SNAP_RELS[0]) is not None:
            s_text, s_bom = decode(orig[SNAP_RELS[0]])
            snap = json.loads(s_text)
            if isinstance(snap, dict):
                cur = snap.get("antibody_realnames")
                table = {r.get("id"): r.get("name") for r in cur if isinstance(r, dict)} if isinstance(cur, list) else {}
                if any(table.get("R%d" % n) != ANTIBODIES[n] for n in range(1, 14)):
                    snap["antibody_realnames"] = realname_records()
                    snap["antibody_summary"] = "항체 R1~R13 (13종)"
                    out = json.dumps(snap, ensure_ascii=False, indent=2) + "\n"
                    json.loads(out)
                    atomic_write(sp, encode(out, s_bom))
                    log("[SNAPSHOT] 항체 R1~R13 실명 목록 보정(D5 가디언 점검용)")
    except Exception as ex:
        rollback("HTML/스냅샷 기록 실패: %s" % ex)
        return 1

    bad = readonly_ok()
    if bad:
        rollback("읽기 전용 파일 변동 감지: %s" % bad)
        return 1

    # 5) 무인 박동 재실행 → D1~D6 ALL OK 검증
    env = dict(os.environ)
    env["RGON_ROOT"] = ROOT
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        proc = subprocess.run([sys.executable, ap(PULSE_REL)], cwd=ROOT, env=env, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=180)
    except Exception as ex:
        rollback("박동 실행 실패: %s" % ex)
        return 1
    for line in (proc.stdout or "").splitlines():
        log("  " + line)
    if proc.stderr and proc.stderr.strip():
        for line in proc.stderr.strip().splitlines()[-10:]:
            log("  [stderr] " + line)
    if proc.returncode != 0:
        rollback("박동 비정상 종료 (exit %d)" % proc.returncode)
        return 1

    try:
        snap = json.loads(decode(read_bytes(ap(SNAP_RELS[0])))[0])
        pulse = snap.get("agency_pulse") or {}
        ags = pulse.get("agencies") or {}
        not_ok = []
        for code in AGENCY_CODES:
            a = ags.get(code) or {}
            t = None
            try:
                t = datetime.datetime.fromisoformat(a.get("checked_at", ""))
            except Exception:
                pass
            if a.get("status") != "OK" or t is None or t < start_dt:
                not_ok.append(code)
                log("[PULSE-CHECK] %s %s = %s · metrics %s" % (code, a.get("name"), a.get("status"),
                    json.dumps(a.get("metrics"), ensure_ascii=False)[:400]))
        if not_ok or pulse.get("overall") != "OK":
            raise RuntimeError("ALL OK 미달성 (비정상: %s · overall=%s)" % (", ".join(not_ok) or "-", pulse.get("overall")))
        log("[VERIFY] D1~D6 전원 OK · overall OK · 박동 #%s (%s)" % (pulse.get("beat_count"), pulse.get("checked_at")))
    except Exception as ex:
        rollback(str(ex))
        return 1

    # 6) evolution_memory.json 이력 기록
    try:
        if orig.get(EVO_REL) is not None:
            e_text, e_bom = decode(orig[EVO_REL])
            evo = json.loads(e_text) if e_text.strip() else {}
        else:
            evo, e_bom = {}, False
        entry = {
            "event": "step11_task_b2_all_ok_and_cloud_sync",
            "timestamp": datetime.datetime.now(KST).isoformat(timespec="seconds"),
            "summary": "누락 보호 ID 2종(rgon-step7-chat-zone, dokdae-feed) 정적 복원 · 6대 청사 ALL OK · HTML 3곳 해시 통일 · GitHub 동기화",
            "canonical": canon["rel"],
            "restore_notes": notes,
            "protected_ids_tag_count": after_tc,
            "html_sha256": canon_sha,
            "agencies": {c: ags[c].get("status") for c in AGENCY_CODES},
            "overall": pulse.get("overall"),
            "beat_count": pulse.get("beat_count"),
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
        atomic_write(ap(EVO_REL), data)
        if read_bytes(ap(EVO_REL)) != data:
            raise RuntimeError("장부 재판독 불일치")
        log("[EVOLUTION] step11_task_b2_all_ok_and_cloud_sync 기록 완료")
    except Exception as ex:
        rollback("evolution_memory 기록 실패: %s" % ex)
        return 1

    # 7) 최종 로컬 무결성 검증
    final = {rel: read_bytes(ap(rel)) for rel in HTML_RELS}
    if len(set(sha256(b) for b in final.values())) != 1 or sha256(final[HTML_RELS[0]]) != canon_sha:
        rollback("최종 HTML 3곳 해시 불일치")
        return 1
    for rel, b in final.items():
        tc = tag_counts(decode(b)[0])
        if any(tc[pid] < 1 for pid in PROTECTED_IDS):
            rollback("최종 보호 ID 6/6 미달 → %s" % rel)
            return 1
    bad = readonly_ok()
    if bad:
        rollback("읽기 전용 파일 변동 감지: %s" % bad)
        return 1
    for rel in HTML_RELS:
        log("  - %-34s %s · 보호ID 6/6" % (rel, canon_sha))
    log("[SYNC] HTML 3곳 SHA-256 해시 100% 완전 일치")

    # 8) GitHub 클라우드 커밋 & 푸시 (로컬 검증은 이미 통과했으므로 git이 실패해도 로컬 결과는 보존)
    paths = [rel for rel in HTML_RELS + SNAP_RELS + [EVO_REL, PULSE_REL, WF_REL] if os.path.isfile(ap(rel))]
    try:
        ok, info = git_sync(paths, canon_sha)
    except Exception as ex:
        ok, info = False, "git 실행 오류: %s" % ex
    if not ok:
        log("[FAIL] GitHub 동기화 실패: %s" % info)
        log("[INFO] 로컬 복원과 ALL OK 결과는 정상 보존됨 → 원인 해결 후 'git push origin main' 재실행")
        return 1
    log("[GIT] push 완료 · origin/main = %s" % info)

    log("[OK] Step 11 과제 B-2 보호 ID 6/6 완전 복원 · 6대 청사 ALL OK 달성 · GitHub 클라우드 동기화 완료")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("[FAIL] 예기치 않은 오류: %s" % e, flush=True)
        sys.exit(1)
Copy
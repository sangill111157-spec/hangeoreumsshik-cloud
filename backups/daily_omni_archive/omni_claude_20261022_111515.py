# -*- coding: utf-8 -*-
# RGON Step 11 과제 A-2 — JS 동적 항체(R1~R13) 한글 실명 매핑 + HTML 3곳 SHA-256 해시 100% 통일
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
SCRIPT_ID = "rgon-step11-ab-realname"

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

# ---------------------------------------------------------------- 공통 유틸
def log(msg):
    print(msg, flush=True)

def ap(rel):
    return os.path.join(ROOT, rel)

def rel_of(p):
    return os.path.relpath(p, ROOT)

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

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def atomic_write_bytes(path, data):
    """R13: 0바이트 금지 · 동일 파일 동시 open 금지 → 임시파일 + fsync + os.replace"""
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

# ---------------------------------------------------------------- R10 보호 ID 카운트
def count_ids(text):
    out = {}
    for pid in PROTECTED_IDS:
        pat = r'\bid\s*=\s*["\']' + re.escape(pid) + r'["\']'
        out[pid] = len(re.findall(pat, text))
    return out

# ---------------------------------------------------------------- 항체 정적 정화 규칙
def js_escape(s):
    return "".join(("\\u%04x" % ord(c)) if ord(c) > 127 else c for c in s)

ESC_HC = r'\\u[dD]56[dD]\\u[cC][cC][bB]4'          # "항체" 유니코드 이스케이프
ESC_DOT = r'(?:·|\\u00[bB]7)'                       # "·" 원문 또는 이스케이프
NO_RANGE = r'(?![\d~\-–])'

RE_COUNT = re.compile(r'항체(\s*)R1(\s*)([~\-–])(\s*)R1[0-2](\s*)\((\s*)1[0-2](\s*)종(\s*)\)')
RE_RANGE = re.compile(r'항체(\s*)R1(\s*)([~\-–])(\s*)R1[0-2](?!\d)')
RE_DUP = re.compile(r'R(\d{1,2})[ \t]*·[ \t]*항체[ \t]*R\1' + NO_RANGE)
RE_ONE = re.compile(r'항체[ \t]*R(\d{1,2})' + NO_RANGE)
RE_ESC_COUNT = re.compile(ESC_HC + r'(\s*)R1(\s*)~(\s*)R1[0-2](\s*)\((\s*)1[0-2](\s*)\\uc885(\s*)\)', re.I)
RE_ESC_DUP = re.compile(r'R(\d{1,2})[ \t]*' + ESC_DOT + r'[ \t]*' + ESC_HC + r'[ \t]*R\1' + NO_RANGE)
RE_ESC_ONE = re.compile(ESC_HC + r'[ \t]*R(\d{1,2})' + NO_RANGE)

def purify_text(text):
    stats = {"badge": 0, "dup": 0, "one": 0, "esc": 0}

    def c_count(m):
        stats["badge"] += 1
        return "항체%sR1%s%s%sR13%s(%s13%s종%s)" % m.groups()

    def c_range(m):
        stats["badge"] += 1
        return "항체%sR1%s%s%sR13" % m.groups()

    def c_dup(m):
        n = int(m.group(1))
        if n not in ANTIBODIES:
            return m.group(0)
        stats["dup"] += 1
        return "R%d · %s" % (n, ANTIBODIES[n])

    def c_one(m):
        n = int(m.group(1))
        if n not in ANTIBODIES:
            return m.group(0)
        stats["one"] += 1
        return "R%d %s" % (n, ANTIBODIES[n])

    def c_esc_count(m):
        stats["esc"] += 1
        g = m.groups()
        return js_escape("항체") + "%sR1%s~%sR13%s(%s13%s" % g[:6] + js_escape("종") + "%s)" % g[6]

    def c_esc_dup(m):
        n = int(m.group(1))
        if n not in ANTIBODIES:
            return m.group(0)
        stats["esc"] += 1
        return js_escape("R%d · %s" % (n, ANTIBODIES[n]))

    def c_esc_one(m):
        n = int(m.group(1))
        if n not in ANTIBODIES:
            return m.group(0)
        stats["esc"] += 1
        return js_escape("R%d %s" % (n, ANTIBODIES[n]))

    text = RE_COUNT.sub(c_count, text)
    text = RE_RANGE.sub(c_range, text)
    text = RE_DUP.sub(c_dup, text)
    text = RE_ONE.sub(c_one, text)
    text = RE_ESC_COUNT.sub(c_esc_count, text)
    text = RE_ESC_DUP.sub(c_esc_dup, text)
    text = RE_ESC_ONE.sub(c_esc_one, text)
    return text, stats

def purify_json_obj(obj):
    total = 0
    if isinstance(obj, dict):
        for k in list(obj.keys()):
            obj[k], c = purify_json_obj(obj[k])
            total += c
    elif isinstance(obj, list):
        for i in range(len(obj)):
            obj[i], c = purify_json_obj(obj[i])
            total += c
    elif isinstance(obj, str):
        new, st = purify_text(obj)
        return new, sum(st.values())
    return obj, total

# ---------------------------------------------------------------- JS 동적 DOM 패치 (비침투 · 초경량)
def build_dom_script():
    names = ",".join('%d:"%s"' % (n, ANTIBODIES[n].replace('"', '\\"')) for n in range(1, 14))
    js = r"""<script id="%s">
(function(){
  "use strict";
  if (window.__rgonStep11AbRealname) return;
  window.__rgonStep11AbRealname = true;
  var N = {%s};
  var HC = "\ud56d\uccb4";
  var reCnt = new RegExp(HC + "(\\s*)R1(\\s*)([~\\-\u2013])(\\s*)R1[0-2](\\s*)\\((\\s*)1[0-2](\\s*)\uc885(\\s*)\\)", "g");
  var reRng = new RegExp(HC + "(\\s*)R1(\\s*)([~\\-\u2013])(\\s*)R1[0-2](?!\\d)", "g");
  var reDup = new RegExp("R(\\d{1,2})[ \\t]*\u00b7[ \\t]*" + HC + "[ \\t]*R\\1(?![\\d~\\-\u2013])", "g");
  var reOne = new RegExp(HC + "[ \\t]*R(\\d{1,2})(?![\\d~\\-\u2013])", "g");
  var SKIP = {SCRIPT:1, STYLE:1, TEXTAREA:1, NOSCRIPT:1, INPUT:1, CODE:1, PRE:1};
  function fix(s){
    if (!s || s.indexOf(HC) < 0) return s;
    s = s.replace(reCnt, function(m,a,b,c,d,e,f,g,h){ return HC+a+"R1"+b+c+d+"R13"+e+"("+f+"13"+g+"\uc885"+h+")"; });
    s = s.replace(reRng, function(m,a,b,c,d){ return HC+a+"R1"+b+c+d+"R13"; });
    s = s.replace(reDup, function(m,n){ return N[n] ? ("R"+n+" \u00b7 "+N[n]) : m; });
    s = s.replace(reOne, function(m,n){ return N[n] ? ("R"+n+" "+N[n]) : m; });
    return s;
  }
  function okNode(t){
    var p = t.parentNode;
    if (!p || p.nodeType !== 1) return false;
    if (SKIP[p.nodeName]) return false;
    if (p.isContentEditable) return false;
    return true;
  }
  function scan(root){
    if (!root) return;
    if (root.nodeType === 3) {
      if (okNode(root)) { var v = fix(root.nodeValue); if (v !== root.nodeValue) root.nodeValue = v; }
      return;
    }
    if (root.nodeType !== 1 && root.nodeType !== 9 && root.nodeType !== 11) return;
    if (root.nodeType === 1 && SKIP[root.nodeName]) return;
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false), t, list = [];
    while ((t = w.nextNode())) { if (t.nodeValue && t.nodeValue.indexOf(HC) >= 0 && okNode(t)) list.push(t); }
    for (var i = 0; i < list.length; i++) {
      var nv = fix(list[i].nodeValue);
      if (nv !== list[i].nodeValue) list[i].nodeValue = nv;
    }
  }
  var queue = [], pending = false;
  var raf = window.requestAnimationFrame || function(f){ return setTimeout(f, 16); };
  function flush(){
    pending = false;
    var q = queue; queue = [];
    for (var i = 0; i < q.length; i++) { try { scan(q[i]); } catch(e) {} }
  }
  function push(n){
    queue.push(n);
    if (!pending) { pending = true; raf(flush); }
  }
  function boot(){
    try { scan(document.body); } catch(e) {}
    try { document.title = fix(document.title); } catch(e) {}
    if (!window.MutationObserver || !document.body) return;
    new MutationObserver(function(muts){
      for (var i = 0; i < muts.length; i++) {
        var m = muts[i];
        if (m.type === "characterData") { push(m.target); continue; }
        for (var j = 0; j < m.addedNodes.length; j++) push(m.addedNodes[j]);
      }
    }).observe(document.body, {childList:true, subtree:true, characterData:true});
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
</script>""" % (SCRIPT_ID, names)
    return js

RE_OLD_SCRIPT = re.compile(
    r'[ \t]*<script\b[^>]*\bid\s*=\s*["\']' + re.escape(SCRIPT_ID) + r'["\'][^>]*>.*?</script>[ \t]*\r?\n?',
    re.S | re.I,
)

def install_dom_script(text):
    text, removed = RE_OLD_SCRIPT.subn("", text)
    nl = "\r\n" if "\r\n" in text else "\n"
    block = build_dom_script().replace("\n", nl)
    idx = text.lower().rfind("</body>")
    if idx >= 0:
        text = text[:idx] + block + nl + text[idx:]
    else:
        text = text + nl + block + nl
    return text, removed

# ---------------------------------------------------------------- 백업 경로
def backup_path_for(tag, rel):
    if rel.endswith(".html"):
        name = "rgon_alpha_chat_step11a2_bak_%s.html" % TS
        return os.path.join(BACKUP_DIR, name) if tag == "root" else os.path.join(BACKUP_DIR, tag, name)
    base = os.path.splitext(os.path.basename(rel))[0]
    return os.path.join(BACKUP_DIR, "%s_step11a2_bak_%s.json" % (base, TS))

def realname_records():
    return [{"id": "R%d" % n, "name": ANTIBODIES[n], "label": "R%d: %s" % (n, ANTIBODIES[n]), "status": "활성"}
            for n in range(1, 14)]

# ---------------------------------------------------------------- 메인
def main():
    if not os.path.isdir(ROOT):
        log("[FAIL] ROOT 경로 없음: %s" % ROOT)
        return 1

    html_files, json_files = [], []
    for tag, rel in HTML_TARGETS:
        html_files.append((tag, rel, ap(rel)))
    for rel in (SNAPSHOT_REL, EVOLUTION_REL):
        p = ap(rel)
        if os.path.isfile(p):
            json_files.append(("json", rel, p))
        else:
            log("[WARN] 장부 없음(건너뜀): %s" % rel)

    existing_html = [(t, r, p) for t, r, p in html_files if os.path.isfile(p)]
    if not existing_html:
        log("[FAIL] HTML 대상이 하나도 없습니다.")
        return 1

    # 1) G3 사전 백업
    originals, backups = {}, {}
    for tag, rel, p in existing_html + json_files:
        data = read_bytes(p)
        if not data:
            log("[FAIL] R13: 원본 0바이트 → %s (중단)" % rel)
            return 1
        originals[p] = data
        bp = backup_path_for(tag, rel)
        atomic_write_bytes(bp, data)
        if read_bytes(bp) != data:
            log("[FAIL] 백업 검증 실패 → %s" % bp)
            return 1
        backups[p] = bp
        log("[BACKUP] %s → %s" % (rel, rel_of(bp)))

    written = []

    def rollback(reason):
        log("[ROLLBACK] %s" % reason)
        for wp in reversed(written):
            try:
                if wp in backups:
                    atomic_write_bytes(wp, read_bytes(backups[wp]))
                    log("  ↺ 복원: %s" % rel_of(wp))
                else:
                    os.remove(wp)
                    log("  ↺ 신규 생성 파일 제거: %s" % rel_of(wp))
            except Exception as ex:
                log("  !! 복원 실패: %s (%s)" % (wp, ex))

    # 2) 정본(Canonical) 선정
    cands = []
    for tag, rel, p in existing_html:
        text, bom = decode(originals[p])
        ids = count_ids(text)
        alive = sum(1 for v in ids.values() if v > 0)
        has10 = ids["rgon-step10-agency-awaken"] > 0
        cands.append({"tag": tag, "rel": rel, "path": p, "text": text, "bom": bom, "ids": ids,
                      "score": (1 if has10 else 0, alive, sum(ids.values()), os.path.getmtime(p), len(originals[p]))})
        log("[SCAN] %-36s 보호ID %d/6 · Step10 %s · sha256 %s" %
            (rel, alive, "O" if has10 else "X", sha256(originals[p])[:12]))
    cands.sort(key=lambda c: c["score"], reverse=True)
    canon = cands[0]
    if canon["ids"]["rgon-step10-agency-awaken"] == 0:
        log("[FAIL] Step 10(rgon-step10-agency-awaken) 포함 정본 없음 → 중단")
        return 1
    log("[CANON] 정본 선정: %s" % canon["rel"])

    # 3) 정본 메모리 정화
    before_ids = canon["ids"]
    t0, removed = RE_OLD_SCRIPT.subn("", canon["text"])
    t1, st = purify_text(t0)
    t2, _ = install_dom_script(t1)
    after_ids = count_ids(t2)
    lost = [pid for pid in PROTECTED_IDS if after_ids[pid] < before_ids[pid]]
    if lost:
        log("[FAIL] R10: 메모리 검증 단계 보호 ID 감소 → 기록 전 중단: %s" % ", ".join(lost))
        return 1
    if t2.count('id="%s"' % SCRIPT_ID) + t2.count("id='%s'" % SCRIPT_ID) != 1:
        log("[FAIL] R12: 동적 패치 스크립트 중복/누락 감지 → 중단")
        return 1
    canon_bytes = encode(t2, canon["bom"])
    canon_hash = sha256(canon_bytes)
    log("[HTML] 정적 정화 — 배지 %d건 · 중복표기 %d건 · 단독표기 %d건 · 이스케이프 %d건 · 기존 패치 갱신 %d건"
        % (st["badge"], st["dup"], st["one"], st["esc"], removed))
    log("[HTML] <script id=\"%s\"> </body> 직전 장착 완료" % SCRIPT_ID)

    for c in cands:
        if c is canon:
            continue
        dec = [pid for pid in PROTECTED_IDS if after_ids[pid] < c["ids"][pid]]
        if dec:
            log("[WARN] %s 원본 대비 보호 ID 개수 차이(정본 기준 통일): %s" % (c["rel"], ", ".join(dec)))

    # 4) JSON 장부 메모리 정화
    json_new = {}
    snap_p = ap(SNAPSHOT_REL)
    if snap_p in originals:
        s_text, s_bom = decode(originals[snap_p])
        try:
            snap = json.loads(s_text)
            snap, c = purify_json_obj(snap)
            if isinstance(snap, dict):
                snap["antibody_realnames"] = realname_records()
                snap["antibody_summary"] = "항체 R1~R13 (13종)"
                snap["antibody_realname_updated"] = datetime.datetime.now().isoformat(timespec="seconds")
            elif isinstance(snap, list):
                snap.append({"antibody_realnames": realname_records(), "antibody_summary": "항체 R1~R13 (13종)"})
            out = json.dumps(snap, ensure_ascii=False, indent=2) + "\n"
            json.loads(out)
            json_new[snap_p] = encode(out, s_bom)
            log("[SNAPSHOT] 구형 표기 정화 %d건 + 항체 R1~R13 한글 실명 기록" % c)
        except Exception as ex:
            log("[WARN] 스냅샷 처리 생략(원본 유지): %s" % ex)

    evo_p = ap(EVOLUTION_REL)
    if evo_p in originals:
        e_text, e_bom = decode(originals[evo_p])
        try:
            evo = json.loads(e_text) if e_text.strip() else {}
            evo, c = purify_json_obj(evo)
            entry = {
                "event": "step11_task_a2_ab_realname_sync",
                "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                "summary": "JS 동적 항체 R1~R13 한글 실명 매핑 + HTML 3곳 SHA-256 해시 통일",
                "canonical": canon["rel"],
                "antibodies": ["R%d: %s" % (n, ANTIBODIES[n]) for n in range(1, 14)],
                "html_sha256": canon_hash,
                "protected_ids_intact": True,
                "backup_ts": TS,
            }
            if isinstance(evo, list):
                evo.append(entry)
            elif isinstance(evo, dict):
                evo["antibody_realnames"] = realname_records()
                target = None
                for k in ("history", "events", "log", "logs", "entries", "evolutions", "memory", "step_log"):
                    if isinstance(evo.get(k), list):
                        target = evo[k]
                        break
                if target is None:
                    if "step_log" in evo:
                        raise RuntimeError("step_log 키가 리스트가 아님")
                    target = evo.setdefault("step_log", [])
                target.append(entry)
            else:
                raise RuntimeError("지원하지 않는 장부 구조")
            out = json.dumps(evo, ensure_ascii=False, indent=2) + "\n"
            json.loads(out)
            json_new[evo_p] = encode(out, e_bom)
            log("[EVOLUTION] 구형 표기 정화 %d건 + 항체 실명 및 이력 기록 준비" % c)
        except Exception as ex:
            log("[WARN] evolution_memory 처리 생략(원본 유지): %s" % ex)

    # 5) 원자적 기록 (HTML 3곳 동일 바이트 + 장부)
    try:
        for tag, rel, p in html_files:
            if p in originals and originals[p] == canon_bytes:
                log("[SKIP] %s 이미 정본과 동일" % rel)
                continue
            if p not in originals:
                log("[INFO] %s 없음 → 정본으로 신규 생성" % rel)
            atomic_write_bytes(p, canon_bytes)
            written.append(p)
            chk = read_bytes(p)
            if sha256(chk) != canon_hash:
                raise RuntimeError("SHA-256 재판독 불일치 → %s" % rel)
            now = count_ids(decode(chk)[0])
            if any(now[pid] < before_ids[pid] for pid in PROTECTED_IDS):
                raise RuntimeError("R10 보호 ID 감소 → %s" % rel)
            log("[WRITE] %s (sha256 %s)" % (rel, canon_hash[:12]))
        for p, data in json_new.items():
            if originals.get(p) == data:
                continue
            atomic_write_bytes(p, data)
            written.append(p)
            chk = read_bytes(p)
            if chk != data:
                raise RuntimeError("장부 재판독 불일치 → %s" % rel_of(p))
            json.loads(decode(chk)[0])
            log("[WRITE] %s" % rel_of(p))
    except Exception as ex:
        rollback(str(ex))
        log("[FAIL] Step 11 과제 A-2 중단 — 백업본 복원 완료")
        return 1

    # 6) 최종 전수 검증
    hashes = {}
    for tag, rel, p in html_files:
        data = read_bytes(p)
        hashes[rel] = sha256(data)
        now = count_ids(decode(data)[0])
        if any(now[pid] < before_ids[pid] for pid in PROTECTED_IDS):
            rollback("최종 검증 보호 ID 감소 → %s" % rel)
            log("[FAIL] Step 11 과제 A-2 중단 — 백업본 복원 완료")
            return 1
    if len(set(hashes.values())) != 1 or len(hashes) != 3:
        rollback("최종 SHA-256 불일치: %s" % hashes)
        log("[FAIL] Step 11 과제 A-2 중단 — 백업본 복원 완료")
        return 1
    for rel, h in hashes.items():
        log("  - %-36s %s" % (rel, h))

    log("[SYNC] HTML 3곳 SHA-256 해시 100% 완전 일치")
    log("[OK] Step 11 과제 A-2 동적 항체 실명화 및 3곳 해시 통일 완료")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("[FAIL] 예기치 않은 오류: %s" % e, flush=True)
        sys.exit(1)
Copy
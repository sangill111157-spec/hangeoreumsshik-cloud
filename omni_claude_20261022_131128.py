# -*- coding: utf-8 -*-
# RGON Step 11 과제 B-3: 독대실 UI에 6대 청사 무인 박동(agency_pulse) 라이브 바인딩 장착 + 클라우드 배포
# 변경 범위: HTML 3곳의 </body> 직전에 <script id="rgon-step11-pulse-live"> 1개만 삽입(또는 갱신). 기존 태그와 보호 ID는 그대로 둔다.
# 헌법, 박동 엔진, 워크플로우, 금고, 스케줄 장부는 읽기 전용이다. 표준 라이브러리만 사용한다.
import os, re, sys, json, shutil, hashlib, tempfile, datetime, subprocess

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
GIT_BRANCH = "main"

HTML_RELS = ["rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html"]
SNAP_RELS = ["rgon_brain_snapshot.json", "dashboard/rgon_brain_snapshot.json", "docs/rgon_brain_snapshot.json"]
EVO_REL = "evolution_memory.json"
PULSE_REL = "scripts/rgon_agency_pulse.py"
WF_REL = ".github/workflows/rgon_agency_pulse.yml"
READONLY_RELS = ["rgon_constitution.json", PULSE_REL, WF_REL, "treasury_ledger.json", "brain_basket/master_schedule.json"]
TOUCH_RELS = HTML_RELS + SNAP_RELS + [EVO_REL]

LIVE_ID = "rgon-step11-pulse-live"
AB_SCRIPT_ID = "rgon-step11-ab-realname"
MIN_BEAT = 3

PROTECTED_IDS = [
    "rgon-step5-solo-panel",
    "rgon-step7-chat-zone",
    "rgon-step8-constitution-bar",
    "rgon-step9-aggregator-board",
    "rgon-step10-agency-awaken",
    "dokdae-feed",
]
AGENCIES = [
    ("D1", "알파-D1 퀀트", "R&D · 4대 AI 교차검증 전광판 대기 상태 점검"),
    ("D2", "알파-D2 바이럴", "핵심 키워드 & BM 파이프라인 준비도 점검"),
    ("D3", "알파-D3 미디어", "브리핑 · TTS · 미디어 자산 상태 점검"),
    ("D4", "알파-D4 홍익", "제0조 홍익인간 원칙 & 헌법 v1.0 무결성 해시 점검"),
    ("D5", "알파-D5 가디언", "13대 항체(R1~R13) & 독대실 HTML 3곳 해시 일치 수호 점검"),
    ("D6", "알파-D6 트레저리", "treasury_ledger.json 금고 장부 무결성 & 무과금(Free Tier) 점검"),
]
AGENCY_CODES = [a[0] for a in AGENCIES]

# ======================================================================
# 라이브 바인딩 스크립트 (보호 ID는 문자열을 쪼개서 getElementById로만 참조한다. R10)
# ======================================================================
LIVE_JS = r"""<script id="rgon-step11-pulse-live">
(function(){
  "use strict";
  if (window.__rgonPulseLive) return;
  window.__rgonPulseLive = true;
  var FALLBACK = __RGON_FALLBACK__;
  var SNAP_URL = "./rgon_brain_snapshot.json";
  var PERIOD = 60000;
  var AWAKEN = "rgon-step10-" + "agency-awaken";
  var ANCHOR_TEXT = "6대 청사 실시간 보좌 지표 보기";
  var BANNER_ID = "rgon-pulse-live-banner";
  var STYLE_ID = "rgon-pulse-live-style";
  var CODES = ["D1","D2","D3","D4","D5","D6"];
  var NAMES = {D1:"알파-D1 퀀트",D2:"알파-D2 바이럴",D3:"알파-D3 미디어",D4:"알파-D4 홍익",D5:"알파-D5 가디언",D6:"알파-D6 트레저리"};
  var ICON = {OK:"🟢",STANDBY:"🟡",WARN:"🟠",ALERT:"🔴"};
  var SKIP = {SCRIPT:1,STYLE:1,NOSCRIPT:1,TEXTAREA:1,INPUT:1,SELECT:1,OPTION:1,BUTTON:1,HTML:1,BODY:1,HEAD:1,TITLE:1};
  var INLINE = {SPAN:1,B:1,STRONG:1,EM:1,I:1,SMALL:1,A:1,LABEL:1,CODE:1,MARK:1,U:1,FONT:1};
  var lastGood = null, lastKey = "", busy = false, timer = null;

  function css(){
    if (document.getElementById(STYLE_ID)) return;
    var s = document.createElement("style");
    s.id = STYLE_ID;
    s.textContent =
      "#" + BANNER_ID + "{display:block;writing-mode:horizontal-tb;max-width:100%;box-sizing:border-box;margin:8px 0;padding:10px 12px;border:1px solid rgba(34,197,94,.45);border-radius:10px;background:rgba(34,197,94,.08);font-size:13px;line-height:1.5;color:inherit;word-break:keep-all;overflow-wrap:anywhere;}" +
      "#" + BANNER_ID + "[data-state=warn]{border-color:rgba(249,115,22,.55);background:rgba(249,115,22,.08);}" +
      "#" + BANNER_ID + " .rpl-head{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;justify-content:space-between;}" +
      "#" + BANNER_ID + " .rpl-sum{font-weight:700;min-width:0;flex:1 1 240px;}" +
      "#" + BANNER_ID + " .rpl-btn{flex:0 0 auto;cursor:pointer;border:1px solid currentColor;border-radius:8px;background:transparent;color:inherit;padding:3px 10px;font-size:12px;writing-mode:horizontal-tb;white-space:nowrap;}" +
      "#" + BANNER_ID + " .rpl-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:6px;margin-top:8px;}" +
      "#" + BANNER_ID + " .rpl-card{box-sizing:border-box;max-width:100%;min-width:0;padding:6px 8px;border-radius:8px;background:rgba(127,127,127,.08);writing-mode:horizontal-tb;}" +
      "#" + BANNER_ID + " .rpl-card b{display:block;}" +
      "#" + BANNER_ID + " .rpl-duty{display:block;opacity:.85;font-size:12px;}" +
      "#" + BANNER_ID + " .rpl-met{display:block;opacity:.7;font-size:11px;}" +
      "#" + BANNER_ID + " .rpl-src{opacity:.65;font-size:11px;margin-top:4px;}" +
      ".rgon-pulse-chip{display:block;writing-mode:horizontal-tb;max-width:100%;box-sizing:border-box;margin-top:4px;font-size:11px;line-height:1.4;opacity:.9;overflow-wrap:anywhere;word-break:keep-all;}";
    (document.head || document.documentElement).appendChild(s);
  }

  function fmt(s){ s = String(s || ""); return s ? s.replace("T", " ").slice(0, 19) : "-"; }
  function setText(el, t){ if (el && el.textContent !== t) el.textContent = t; }

  function metricText(code, m){
    m = m || {};
    switch (code) {
      case "D1": return "교차검증판 " + (m.cross_validation_board || (m.aggregator_board_present ? "대기" : "미탐지")) + " · 대화창 " + (m.chat_zone_present ? "확인" : "미확인");
      case "D2": return "마스터 스케줄 " + (m.master_schedule_valid ? "정상" : "미확인") + " · 키워드/BM 키 " + (m.keyword_bm_keys || 0);
      case "D3": return "미디어 " + (m.media_files || 0) + "개 · 브리핑 키 " + (m.briefing_keys || 0);
      case "D4": return "헌법 해시 " + (m.baseline_match ? "일치" : "불일치") + " · 제0조 홍익 " + (m.article0_hongik_found ? "확인" : "미확인");
      case "D5": return "항체 " + (m.antibodies_active || 0) + "/" + (m.antibodies_total || 13) + " · HTML 3곳 " + (m.html_hash_unified ? "해시 일치" : "해시 불일치");
      case "D6": return "금고 장부 " + (m.ledger_valid ? "정상" : "미확인") + " · Free Tier · 유료호출 " + (m.paid_api_calls || 0);
    }
    return "";
  }

  function agency(p, code){
    var a = (p && p.agencies && p.agencies[code]) || {};
    return {code: code, name: a.name || NAMES[code], duty: a.duty || "", status: String(a.status || "STANDBY"), metrics: a.metrics || {}};
  }

  function summary(p){
    var bad = [];
    for (var i = 0; i < CODES.length; i++) if (agency(p, CODES[i]).status !== "OK") bad.push(CODES[i]);
    var ab = (p && p.antibodies) || {};
    var allOk = bad.length === 0 && p && p.overall === "OK";
    var head = allOk ? "🟢 6대 청사 무인 박동 #" + (p.beat_count || 0) + " · D1~D6 ALL OK"
                     : "🟠 6대 청사 무인 박동 #" + ((p && p.beat_count) || 0) + " · 점검 필요: " + (bad.join(", ") || "종합 판정");
    return {ok: allOk, text: head + " · 항체 " + (ab.active || 0) + "/" + (ab.total || 13) + " 활성 · 최근 점검: " + fmt(p && p.checked_at)};
  }

  function findAnchor(){
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false), t;
    while ((t = w.nextNode())) {
      if (t.nodeValue && t.nodeValue.indexOf(ANCHOR_TEXT) >= 0 && t.parentElement && !t.parentElement.closest("#" + BANNER_ID)) return t.parentElement;
    }
    return null;
  }

  function ensureBanner(){
    var b = document.getElementById(BANNER_ID);
    if (b) return b;
    b = document.createElement("div");
    b.id = BANNER_ID;
    b.setAttribute("role", "status");
    b.setAttribute("aria-live", "polite");
    var head = document.createElement("div"); head.className = "rpl-head";
    var sum = document.createElement("div"); sum.className = "rpl-sum"; sum.textContent = "🟡 6대 청사 무인 박동 수신 대기";
    var btn = document.createElement("button"); btn.type = "button"; btn.className = "rpl-btn"; btn.textContent = "🔄 지금 동기화";
    btn.addEventListener("click", function(){ load(true); });
    head.appendChild(sum); head.appendChild(btn);
    var grid = document.createElement("div"); grid.className = "rpl-grid";
    for (var i = 0; i < CODES.length; i++) {
      var c = document.createElement("div"); c.className = "rpl-card"; c.setAttribute("data-rpl-code", CODES[i]);
      var nb = document.createElement("b"); var du = document.createElement("span"); du.className = "rpl-duty";
      var me = document.createElement("span"); me.className = "rpl-met";
      c.appendChild(nb); c.appendChild(du); c.appendChild(me); grid.appendChild(c);
    }
    var src = document.createElement("div"); src.className = "rpl-src";
    b.appendChild(head); b.appendChild(grid); b.appendChild(src);
    var host = document.getElementById(AWAKEN);
    if (host) { host.insertBefore(b, host.firstChild); return b; }
    var anc = findAnchor();
    if (anc) {
      var det = anc.closest("details");
      var ref = det || anc;
      if (ref.parentNode) { ref.parentNode.insertBefore(b, ref); return b; }
    }
    document.body.insertBefore(b, document.body.firstChild);
    return b;
  }

  function hostOf(el){
    var h = el, k = 0;
    while (h && INLINE[h.nodeName] && h.parentElement && k < 3) { h = h.parentElement; k++; }
    return h;
  }

  function bindCards(p){
    for (var i = 0; i < CODES.length; i++) {
      var code = CODES[i], name = NAMES[code], a = agency(p, code);
      var line = (ICON[a.status] || "⚪") + " " + a.status + " · " + a.duty + " · " + metricText(code, a.metrics);
      var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false), t, hosts = [];
      while ((t = w.nextNode()) && hosts.length < 3) {
        var pe = t.parentElement;
        if (!pe || !t.nodeValue || t.nodeValue.indexOf(name) < 0) continue;
        if (pe.closest("#" + BANNER_ID) || pe.closest(".rgon-pulse-chip") || pe.isContentEditable) continue;
        var h = hostOf(pe);
        if (!h || SKIP[h.nodeName] || hosts.indexOf(h) >= 0) continue;
        var tx = h.textContent || "", multi = 0;
        for (var j = 0; j < CODES.length; j++) if (tx.indexOf(NAMES[CODES[j]]) >= 0) multi++;
        if (multi > 1) continue;
        hosts.push(h);
      }
      for (var k = 0; k < hosts.length; k++) {
        var chip = null, ch = hosts[k].children;
        for (var x = 0; x < ch.length; x++) if (ch[x].getAttribute("data-rgon-pulse-chip") === code) { chip = ch[x]; break; }
        if (!chip) {
          chip = document.createElement("span");
          chip.className = "rgon-pulse-chip";
          chip.setAttribute("data-rgon-pulse-chip", code);
          hosts[k].appendChild(chip);
        }
        setText(chip, line);
      }
    }
  }

  function bindSyncButtons(){
    var list = document.querySelectorAll("button, a, [role=button]");
    for (var i = 0; i < list.length; i++) {
      var el = list[i];
      if (el.closest("#" + BANNER_ID) || el.getAttribute("data-rgon-pulse-sync") === "1") continue;
      if ((el.textContent || "").indexOf("지금 동기화") >= 0) {
        el.setAttribute("data-rgon-pulse-sync", "1");
        el.addEventListener("click", function(){ load(true); });
      }
    }
  }

  function render(p, src){
    if (!document.body || !p) return;
    css();
    var b = ensureBanner();
    var s = summary(p);
    var key = JSON.stringify([p.beat_count, p.checked_at, p.overall, p.agencies, p.antibodies, src]);
    if (key !== lastKey) {
      lastKey = key;
      var st = s.ok ? "ok" : "warn";
      if (b.getAttribute("data-state") !== st) b.setAttribute("data-state", st);
      setText(b.querySelector(".rpl-sum"), s.text);
      var cards = b.querySelectorAll(".rpl-card");
      for (var i = 0; i < cards.length; i++) {
        var a = agency(p, cards[i].getAttribute("data-rpl-code"));
        setText(cards[i].querySelector("b"), (ICON[a.status] || "⚪") + " " + a.status + " · " + a.code + " " + a.name);
        setText(cards[i].querySelector(".rpl-duty"), a.duty);
        setText(cards[i].querySelector(".rpl-met"), metricText(a.code, a.metrics));
      }
      setText(b.querySelector(".rpl-src"), "출처: " + src + " · 60초 주기 자동 갱신");
    }
    try { bindCards(p); } catch (e) {}
    try { bindSyncButtons(); } catch (e) {}
  }

  function load(){
    if (busy) return;
    busy = true;
    var finish = function(p, src){ busy = false; render(p, src); };
    if (!window.fetch) { finish(lastGood || FALLBACK, lastGood ? "직전 수신값 유지" : "내장 폴백(R4)"); return; }
    var ctrl = window.AbortController ? new AbortController() : null;
    var to = setTimeout(function(){ if (ctrl) ctrl.abort(); }, 8000);
    var opt = {cache: "no-store"};
    if (ctrl) opt.signal = ctrl.signal;
    fetch(SNAP_URL + "?t=" + Date.now(), opt)
      .then(function(r){ if (!r.ok) throw new Error("http " + r.status); return r.json(); })
      .then(function(j){
        var p = j && j.agency_pulse;
        if (!p || !p.agencies) throw new Error("no agency_pulse");
        lastGood = p;
        clearTimeout(to);
        finish(p, "실시간 스냅샷");
      })
      .catch(function(){
        clearTimeout(to);
        finish(lastGood || FALLBACK, lastGood ? "직전 수신값 유지" : "내장 폴백(R4)");
      });
  }

  function boot(){
    try { render(FALLBACK, "내장 폴백(R4)"); } catch (e) {}
    load();
    if (timer) clearInterval(timer);
    timer = setInterval(load, PERIOD);
    document.addEventListener("visibilitychange", function(){ if (!document.hidden) load(); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
</script>"""

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

def count_ids(text):
    return {pid: len(re.findall(id_pat(pid), text)) for pid in PROTECTED_IDS}

def backup_path(rel):
    parts = rel.split("/")
    base, ext = os.path.splitext(parts[-1])
    return os.path.join(BACKUP_DIR, *(parts[:-1] + ["%s_step11b3_bak_%s%s" % (base, TS, ext or ".bak")]))

def parse_iso(s):
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        return None

# ======================================================================
# 내장 폴백 데이터(R4): 현재 스냅샷의 agency_pulse를 가볍게 줄여서 넣는다
# ======================================================================
def slim_pulse(p):
    if not isinstance(p, dict) or not isinstance(p.get("agencies"), dict):
        return {
            "beat_count": 0, "checked_at": "", "overall": "STANDBY",
            "agencies": {c: {"code": c, "name": n, "duty": d, "status": "STANDBY", "metrics": {}} for c, n, d in AGENCIES},
            "antibodies": {"active": 0, "total": 13},
        }
    ags = p["agencies"]
    out = {}
    for code, name, duty in AGENCIES:
        a = ags.get(code) if isinstance(ags.get(code), dict) else {}
        m = a.get("metrics") if isinstance(a.get("metrics"), dict) else {}
        mm = {}
        for k, v in m.items():
            if isinstance(v, bool) or isinstance(v, (int, float)):
                mm[k] = v
            elif isinstance(v, str) and len(v) <= 80 and not k.endswith("sha256"):
                mm[k] = v
        out[code] = {"code": code, "name": a.get("name") or name, "duty": a.get("duty") or duty,
                     "status": str(a.get("status") or "STANDBY"), "checked_at": a.get("checked_at") or "", "metrics": mm}
    ab = p.get("antibodies") if isinstance(p.get("antibodies"), dict) else {}
    return {"beat_count": p.get("beat_count") if isinstance(p.get("beat_count"), int) else 0,
            "checked_at": p.get("checked_at") or "", "overall": p.get("overall") or "STANDBY",
            "agencies": out, "antibodies": {"active": ab.get("active") or 0, "total": ab.get("total") or 13}}

def js_literal(obj):
    s = json.dumps(obj, ensure_ascii=True, separators=(",", ":"))
    return s.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")

def build_live_block(fallback):
    return LIVE_JS.replace("__RGON_FALLBACK__", js_literal(fallback))

RE_OLD_LIVE = re.compile(
    r'[ \t]*<script\b[^>]*\bid\s*=\s*["\']' + re.escape(LIVE_ID) + r'["\'][^>]*>.*?</script\s*>[ \t]*\r?\n?',
    re.S | re.I,
)

# ======================================================================
# Git
# ======================================================================
GIT_ENV = dict(os.environ)
GIT_ENV["GIT_TERMINAL_PROMPT"] = "0"

def git(args, timeout=180):
    p = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=GIT_ENV, timeout=timeout)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()

def git_tail(out, err, n=6):
    for ln in (out + "\n" + err).strip().splitlines()[-n:]:
        log("    | " + ln)

def verify_after_rebase(expect_sha):
    for rel in HTML_RELS:
        if sha256(read_bytes(ap(rel))) != expect_sha:
            return "리베이스 후 HTML 해시가 정본과 다릅니다: %s" % rel
    for rel in SNAP_RELS + [EVO_REL]:
        if os.path.isfile(ap(rel)):
            try:
                json.loads(decode(read_bytes(ap(rel)))[0])
            except Exception as ex:
                return "리베이스 후 JSON 무효: %s (%s)" % (rel, ex)
    return None

def git_sync(paths, expect_sha):
    if not shutil.which("git"):
        return False, "git 실행 파일을 찾지 못했습니다"
    rc, out, _ = git(["rev-parse", "--is-inside-work-tree"])
    if rc != 0 or out != "true":
        return False, "ROOT가 git 저장소가 아닙니다"
    _, br, _ = git(["rev-parse", "--abbrev-ref", "HEAD"])
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
        msg = "feat(step11-b3): 6대 청사 무인 박동 라이브 전광판 바인딩 · HTML 3곳 해시 통일"
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
        bad = verify_after_rebase(expect_sha)
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
    for rel in HTML_RELS + [PULSE_REL, SNAP_RELS[0]]:
        if not os.path.isfile(ap(rel)):
            log("[FAIL] 필수 파일 없음: %s" % rel)
            return 1

    readonly_hash = {rel: (sha256(read_bytes(ap(rel))) if os.path.isfile(ap(rel)) else None) for rel in READONLY_RELS}

    # 1) G3 사전 백업
    orig = {}
    for rel in TOUCH_RELS:
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
            orig[rel] = data
            log("[BACKUP] %s → %s" % (rel, os.path.relpath(bp, ROOT)))
        else:
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
        log("[FAIL] Step 11 과제 B-3 중단: 백업본으로 복원했습니다")

    def readonly_changed():
        for rel, h in readonly_hash.items():
            now = sha256(read_bytes(ap(rel))) if os.path.isfile(ap(rel)) else None
            if now != h:
                return rel
        return None

    # 2) 정본 선정과 보호 ID 사전 점검
    cands = []
    for rel in HTML_RELS:
        text, bom = decode(orig[rel])
        ids = count_ids(text)
        alive = sum(1 for v in ids.values() if v > 0)
        cands.append({"rel": rel, "text": text, "bom": bom, "ids": ids,
                      "score": (1 if ids["rgon-step10-agency-awaken"] else 0, alive,
                                1 if all(v == 1 for v in ids.values()) else 0, os.path.getmtime(ap(rel)))})
        log("[SCAN] %-34s sha256 %s · 보호ID %d/6" % (rel, sha256(orig[rel])[:12], alive))
    if len(set(sha256(orig[r]) for r in HTML_RELS)) != 1:
        log("[WARN] HTML 3곳 해시가 지금 서로 다릅니다 → 정본 기준으로 다시 통일합니다")
    cands.sort(key=lambda c: c["score"], reverse=True)
    canon = cands[0]
    log("[CANON] 정본: %s" % canon["rel"])
    before = canon["ids"]
    not_one = {pid: n for pid, n in before.items() if n != 1}
    if not_one:
        log("[FAIL] R10: 정본 보호 ID가 각 1개가 아닙니다 → 아무 파일도 수정하지 않고 중단")
        for pid, n in not_one.items():
            log("  - %s: %d개" % (pid, n))
        return 1

    # 3) 내장 폴백과 라이브 스크립트 준비
    try:
        snap0 = json.loads(decode(orig[SNAP_RELS[0]])[0])
    except Exception as ex:
        log("[FAIL] 루트 스냅샷 JSON 무효(덮어쓰지 않고 중단): %s" % ex)
        return 1
    prev_pulse = snap0.get("agency_pulse") if isinstance(snap0, dict) else None
    prev_beat = prev_pulse.get("beat_count") if isinstance(prev_pulse, dict) and isinstance(prev_pulse.get("beat_count"), int) else 0
    fallback = slim_pulse(prev_pulse)
    block = build_live_block(fallback)
    if any(re.search(id_pat(pid), block) for pid in PROTECTED_IDS):
        log("[FAIL] R10: 라이브 스크립트 안에 보호 ID 속성 문자열이 들어 있습니다 → 중단")
        return 1
    if "</script" in block[:-len("</script>")].lower():
        log("[FAIL] 라이브 스크립트 본문에 </script 문자열이 들어 있습니다 → 중단")
        return 1
    log("[LIVE] 내장 폴백(R4) = 박동 #%d · overall %s · %s" % (fallback["beat_count"], fallback["overall"], fallback["checked_at"] or "-"))

    # 4) 메모리 안에서 장착(삽입만, 이전 B-3 스크립트가 있으면 교체. R12)
    base_text, removed = RE_OLD_LIVE.subn("", canon["text"])
    if removed:
        log("[R12] 이전 %s 스크립트 %d개를 교체합니다" % (LIVE_ID, removed))
    nl = "\r\n" if "\r\n" in base_text else "\n"
    ins = block.replace("\n", nl) + nl
    idx = base_text.lower().rfind("</body>")
    if idx < 0:
        new_text = base_text + nl + ins
    else:
        new_text = base_text[:idx] + ins + base_text[idx:]
    if new_text.replace(ins, "", 1) != base_text and new_text.replace(nl + ins, "", 1) != base_text:
        log("[FAIL] Minimal Diff 검증 실패(삽입 외 변경 감지) → 기록 전 중단")
        return 1
    after = count_ids(new_text)
    if after != before or any(v != 1 for v in after.values()):
        log("[FAIL] R10: 보호 ID 개수 변동 → 기록 전 중단 %s" % after)
        return 1
    if len(re.findall(id_pat(LIVE_ID), new_text)) != 1:
        log("[FAIL] R12: 라이브 스크립트 중복/누락 → 기록 전 중단")
        return 1
    if re.search(id_pat(AB_SCRIPT_ID), canon["text"]) and not re.search(id_pat(AB_SCRIPT_ID), new_text):
        log("[FAIL] 동적 항체 패치 스크립트가 사라졌습니다 → 기록 전 중단")
        return 1
    canon_bytes = encode(new_text, canon["bom"])
    canon_sha = sha256(canon_bytes)
    log("[HTML] <script id=\"%s\"> </body> 직전 장착 · +%d bytes · 정본 sha256 %s" %
        (LIVE_ID, len(canon_bytes) - len(orig[canon["rel"]]), canon_sha[:12]))

    # 5) HTML 3곳 원자적 기록
    try:
        for rel in HTML_RELS:
            if orig[rel] == canon_bytes:
                log("[SKIP] %s 이미 정본과 동일" % rel)
                continue
            atomic_write(ap(rel), canon_bytes)
            if sha256(read_bytes(ap(rel))) != canon_sha:
                raise RuntimeError("SHA-256 재판독 불일치 → %s" % rel)
            log("[WRITE] %s (sha256 %s)" % (rel, canon_sha[:12]))
    except Exception as ex:
        rollback("HTML 기록 실패: %s" % ex)
        return 1
    bad = readonly_changed()
    if bad:
        rollback("읽기 전용 파일 변동 감지: %s" % bad)
        return 1

    # 6) 무인 박동 1회 실행 → 박동 #3 이상 · D1~D6 ALL OK 검증
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
            t = parse_iso(a.get("checked_at", ""))
            if a.get("status") != "OK" or t is None or t < start_dt:
                not_ok.append(code)
                log("[PULSE-CHECK] %s %s = %s · metrics %s" % (code, a.get("name"), a.get("status"),
                    json.dumps(a.get("metrics"), ensure_ascii=False)[:400]))
        if not_ok or pulse.get("overall") != "OK":
            raise RuntimeError("ALL OK 미달성 (비정상: %s · overall=%s)" % (", ".join(not_ok) or "-", pulse.get("overall")))
        beat = pulse.get("beat_count") if isinstance(pulse.get("beat_count"), int) else 0
        if beat < MIN_BEAT or beat <= prev_beat:
            raise RuntimeError("박동 번호 검증 실패 (이전 #%d → 현재 #%d, 최소 #%d 필요)" % (prev_beat, beat, MIN_BEAT))
        hi = pulse.get("html_integrity") or {}
        if not hi.get("hash_unified") or not hi.get("protected_ids_ok"):
            raise RuntimeError("박동 엔진이 HTML 무결성 이상을 보고했습니다: %s" % hi)
        for rel in SNAP_RELS[1:]:
            if os.path.isfile(ap(rel)):
                m = json.loads(decode(read_bytes(ap(rel)))[0])
                if (m.get("agency_pulse") or {}).get("checked_at") != pulse.get("checked_at"):
                    log("[WARN] 미러 박동 시각이 루트와 다릅니다: %s" % rel)
                else:
                    log("[VERIFY] 미러 동기화 확인: %s" % rel)
        log("[VERIFY] D1~D6 전원 OK · overall OK · 박동 #%d (%s)" % (beat, pulse.get("checked_at")))
    except Exception as ex:
        rollback(str(ex))
        return 1

    # 7) evolution_memory.json 이력 기록
    try:
        if orig.get(EVO_REL) is not None:
            e_text, e_bom = decode(orig[EVO_REL])
            evo = json.loads(e_text) if e_text.strip() else {}
        else:
            evo, e_bom = {}, False
        entry = {
            "event": "step11_task_b3_pulse_live_ui_binding",
            "timestamp": datetime.datetime.now(KST).isoformat(timespec="seconds"),
            "summary": "독대실 UI에 6대 청사 무인 박동(agency_pulse) 라이브 전광판 바인딩 장착(60초 주기 · 지금 동기화 · 내장 폴백) · HTML 3곳 해시 통일 · 클라우드 배포",
            "script_id": LIVE_ID,
            "canonical": canon["rel"],
            "html_sha256": canon_sha,
            "protected_ids": after,
            "beat_count": beat,
            "checked_at": pulse.get("checked_at"),
            "overall": pulse.get("overall"),
            "agencies": {c: ags[c].get("status") for c in AGENCY_CODES},
            "antibodies_active": (pulse.get("antibodies") or {}).get("active"),
            "fallback_beat": fallback["beat_count"],
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
        log("[EVOLUTION] step11_task_b3_pulse_live_ui_binding 기록 완료")
    except Exception as ex:
        rollback("evolution_memory 기록 실패: %s" % ex)
        return 1

    # 8) 최종 로컬 무결성 검증
    final = {rel: read_bytes(ap(rel)) for rel in HTML_RELS}
    if len(set(sha256(b) for b in final.values())) != 1 or sha256(final[HTML_RELS[0]]) != canon_sha:
        rollback("최종 HTML 3곳 해시 불일치")
        return 1
    for rel, b in final.items():
        ids = count_ids(decode(b)[0])
        if any(ids[pid] != 1 for pid in PROTECTED_IDS):
            rollback("최종 보호 ID가 각 1개가 아닙니다 → %s %s" % (rel, ids))
            return 1
    bad = readonly_changed()
    if bad:
        rollback("읽기 전용 파일 변동 감지: %s" % bad)
        return 1
    for rel in HTML_RELS:
        log("  - %-34s %s · 보호ID 6/6 (각 1개)" % (rel, canon_sha))
    log("[SYNC] HTML 3곳 SHA-256 해시 100% 완전 일치")

    # 9) GitHub 클라우드 커밋 & 푸시 (git이 실패해도 로컬 검증 결과는 보존)
    paths = [rel for rel in HTML_RELS + SNAP_RELS + [EVO_REL] if os.path.isfile(ap(rel))]
    try:
        ok, info = git_sync(paths, canon_sha)
    except Exception as ex:
        ok, info = False, "git 실행 오류: %s" % ex
    if not ok:
        log("[FAIL] GitHub 동기화 실패: %s" % info)
        log("[INFO] 로컬 라이브 바인딩과 ALL OK 결과는 정상 보존됨 → 원인 해결 후 'git push origin main' 재실행")
        return 1
    log("[GIT] push 완료 · origin/main = %s" % info)

    log("[OK] Step 11 과제 B-3 6대 청사 무인 박동 라이브 전광판 직결 및 클라우드 배포 완료")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("[FAIL] 예기치 않은 오류: %s" % e, flush=True)
        sys.exit(1)
Copy
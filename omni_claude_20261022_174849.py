#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RGON G1 Step 11 / 과제 E-1
모바일 PWA 대시보드 + 로건봇(Telegram) 무토큰 우체부 + 실시간 장부 응답기 올인원 합체 · 박동 #8 클라우드 배포
실행: RGON_Run.bat -> rgon_runner.py -> 본 스크립트 (단독 실행 가능, 파이썬 표준 라이브러리만 사용)

설계 메모
- 텔레그램 자격증명은 환경변수 / .env* / 설정 JSON·PY 의 정확한 키 이름(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)으로만 조회하며,
  값은 로그·장부·HTML·커밋 어디에도 평문으로 남기지 않는다(출력 마스킹 + 커밋 직전 유출 검사).
- 원격 동기화는 -X theirs 를 쓰지 않는다. 충돌 시 원격 변경이 조용히 덮어써지지 않도록 rebase 를 중단하고 파일 변경 없이 종료한다.
"""
import sys, os, re, ast, json, shutil, hashlib, subprocess, time, tempfile
from pathlib import Path
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ───────────────────────── 설정 ─────────────────────────
ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
CONSTITUTION = ROOT / "rgon_constitution.json"
CONST_PREFIX = "bd5060dea1e2"
BRIDGE = ROOT / "scripts" / "rgon_telegram_bridge.py"
PULSE = ROOT / "scripts" / "rgon_agency_pulse.py"
HTMLS = [ROOT / "rgon_alpha_chat.html",
         ROOT / "dashboard" / "rgon_alpha_chat.html",
         ROOT / "docs" / "rgon_alpha_chat.html"]
SNAPS = [ROOT / "rgon_brain_snapshot.json",
         ROOT / "dashboard" / "rgon_brain_snapshot.json",
         ROOT / "docs" / "rgon_brain_snapshot.json"]
EVOLUTION = ROOT / "evolution_memory.json"
BACKUP_DIR = ROOT / "backups"

EVENT = "step11_task_e1_all_in_one_mobile_telegram_hub"
PROTECTED_IDS = ["rgon-step5-solo-panel", "rgon-step7-chat-zone", "rgon-step8-constitution-bar",
                 "rgon-step9-aggregator-board", "rgon-step10-agency-awaken", "dokdae-feed"]
STALE_PHRASE = "[실시간 박동 연동 · 14대 항체 수호 · 무과금 Free Tier 100%]"
KEYWORDS = ["AI 에이전트 군단 자동화", "4대 AI 교차검증 레버리지", "원클릭 무인 사령부",
            "홍익인간 안전 가드레일", "24시간 클라우드 자가진화"]
BTN_LABELS = ["[📋 실시간 브리핑 대화창에 호출]", "[🔊 음성 아나운서 듣기/정지]",
              "[🧠 자율진화 Top1 지시서 장전]", "[✈️ 로건봇(텔레그램) 브리핑 공유]"]
FINAL_OK = "[OK] Step 11 과제 E-1 모바일 올인원 소통창 & 무토큰 로건봇 브리지 합체 · 박동 #8 클라우드 배포 완료"

NOW = datetime.now()
TS = NOW.strftime("%Y%m%d_%H%M%S")
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S")
TAG = "_step11e1_bak_" + TS

TARGETS = [BRIDGE] + HTMLS + SNAPS + [EVOLUTION]
BACKUPS = {}
CREATED = []


def log(msg):
    print(msg, flush=True)


def rel(p):
    try:
        return str(Path(p).relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(p)


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ═════════════════════ 무토큰 로건봇 우체부 모듈 소스 ═════════════════════
BRIDGE_SRC = r'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RGON 로건봇(Telegram) 무토큰 우체부 — 파이썬 표준 라이브러리(urllib)만 사용
  python scripts/rgon_telegram_bridge.py --send "메시지"
  python scripts/rgon_telegram_bridge.py --send-stdin
  python scripts/rgon_telegram_bridge.py --poll-once     (박동/브리핑/상태/키워드 질의에 자동 답장)
  python scripts/rgon_telegram_bridge.py --selftest

보안 원칙
- TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 는 환경변수, .env*, 설정 JSON/PY 의 '정확한 키 이름'으로만 조회한다.
- 토큰 값은 화면/로그/장부 어디에도 평문으로 출력하지 않는다(전 출력 마스킹).
- 토큰 또는 채팅 ID 가 없으면 에러 없이 [TELEGRAM-STANDBY] 로 안전 통과한다.
"""
import sys, os, re, json, argparse
import urllib.request, urllib.error, urllib.parse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
API = "https://api.telegram.org/bot%s/%s"
KEY_TOKEN = "TELEGRAM_BOT_TOKEN"
KEY_CHAT = "TELEGRAM_CHAT_ID"
STATE = HERE / ".rgon_tg_state.json"
MASK = "***MASKED***"
_SECRETS = set()
_TOKEN_SHAPE = re.compile(r"\d{6,}:[A-Za-z0-9_-]{20,}")


def _register(v):
    v = str(v or "").strip()
    if len(v) >= 6:
        _SECRETS.add(v)


def mask(text):
    s = str(text)
    for sec in sorted(_SECRETS, key=len, reverse=True):
        s = s.replace(sec, MASK)
    return _TOKEN_SHAPE.sub(MASK, s)


def log(msg):
    print(mask(msg), flush=True)


# ───────────── 자격증명 조회 (정확한 키 이름만) ─────────────
_ENV_LINE = re.compile(r"^\s*(?:export\s+)?(TELEGRAM_BOT_TOKEN|TELEGRAM_CHAT_ID)\s*[=:]\s*(.+?)\s*$")
_PY_LINE = re.compile(r"^\s*(TELEGRAM_BOT_TOKEN|TELEGRAM_CHAT_ID)\s*=\s*[\"']([^\"']+)[\"']")
_SKIP_JSON = {"rgon_brain_snapshot.json", "evolution_memory.json", "package-lock.json", "manifest.json",
              "rgon_constitution.json", "master_schedule.json"}


def _unq(v):
    v = str(v).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v.strip()


def _scan_lines(path, regex, out):
    try:
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            m = regex.match(line)
            if m and m.group(1) not in out and _unq(m.group(2)):
                out[m.group(1)] = _unq(m.group(2))
    except Exception:
        pass


def _scan_json(path, out):
    try:
        if path.stat().st_size > 2 * 1024 * 1024:
            return
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return

    def walk(o, d=0):
        if d > 8:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                ku = str(k).upper()
                if ku in (KEY_TOKEN, KEY_CHAT) and ku not in out and isinstance(v, (str, int)) and _unq(v):
                    out[ku] = _unq(v)
                elif isinstance(v, (dict, list)):
                    walk(v, d + 1)
        elif isinstance(o, list):
            for x in o:
                walk(x, d + 1)
    walk(data)


def find_credentials():
    """(token, chat_id, 출처 요약) 반환. 값은 절대 출력하지 않는다."""
    found, srcs = {}, []
    for k in (KEY_TOKEN, KEY_CHAT):
        v = os.environ.get(k)
        if v and v.strip():
            found[k] = v.strip()
            srcs.append("환경변수")
    dirs = [ROOT, ROOT / "scripts", ROOT / "config"]
    for d in dirs:
        if len(found) == 2 or not d.is_dir():
            continue
        for p in sorted(d.glob(".env*")):
            if p.is_file():
                before = len(found)
                _scan_lines(p, _ENV_LINE, found)
                if len(found) > before:
                    srcs.append(p.name)
    for d in dirs:
        if len(found) == 2 or not d.is_dir():
            continue
        for p in sorted(d.glob("*.json")):
            if p.name in _SKIP_JSON or not p.is_file():
                continue
            before = len(found)
            _scan_json(p, found)
            if len(found) > before:
                srcs.append(p.name)
    for d in dirs:
        if len(found) == 2 or not d.is_dir():
            continue
        for p in sorted(d.glob("*.py")):
            if p.name == Path(__file__).name or not p.is_file():
                continue
            before = len(found)
            _scan_lines(p, _PY_LINE, found)
            if len(found) > before:
                srcs.append(p.name)
    token, chat = found.get(KEY_TOKEN), found.get(KEY_CHAT)
    _register(token)
    return token, chat, sorted(set(srcs))


# ───────────── Telegram HTTP (urllib 전용) ─────────────
def _api(token, method, payload=None, timeout=20):
    url = API % (token, method)
    data = urllib.parse.urlencode(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")[:200]
        except Exception:
            body = ""
        raise RuntimeError(mask("HTTP %s %s" % (e.code, body)))
    except Exception as e:
        raise RuntimeError(mask("%s: %s" % (type(e).__name__, e)))


def _split(text, n=3900):
    text = str(text)
    out = []
    while len(text) > n:
        cut = text.rfind("\n", 0, n)
        if cut < n // 2:
            cut = n
        out.append(text[:cut])
        text = text[cut:].lstrip("\n")
    if text:
        out.append(text)
    return out or [""]


def send_telegram_report(text, creds=None):
    token, chat, _src = creds if creds else find_credentials()
    if not token or not chat:
        log("[TELEGRAM-STANDBY] 토큰/채팅 ID 미설정 - 안전 통과 (발송 생략)")
        return False
    try:
        for part in _split(text):
            res = _api(token, "sendMessage", {"chat_id": chat, "text": part, "disable_web_page_preview": "true"})
            if not res.get("ok"):
                log("[TELEGRAM-WARN] 발송 거부: " + str(res.get("description", ""))[:120])
                return False
        log("[TELEGRAM-OK] 대표님 텔레그램 발송 완료 (토큰 %s)" % MASK)
        return True
    except Exception as e:
        log("[TELEGRAM-WARN] 발송 실패: %s" % e)
        return False


# ───────────── 실시간 장부 요약 ─────────────
def _load_snapshot():
    try:
        return json.loads((ROOT / "rgon_brain_snapshot.json").read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _find(o, key, d=0):
    if d > 8 or not isinstance(o, (dict, list)):
        return None
    if isinstance(o, dict):
        if key in o:
            return o[key]
        vals = list(o.values())
    else:
        vals = o
    for v in vals:
        r = _find(v, key, d + 1)
        if r is not None:
            return r
    return None


_BEAT_KEYS = {"beat", "beat_no", "beat_number", "pulse_no", "pulse_number", "pulse_count",
              "heartbeat", "pulse_beat", "seq", "박동"}


def _beats(o, out, d=0):
    if d > 8:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            if str(k).lower() in _BEAT_KEYS and isinstance(v, int) and not isinstance(v, bool):
                out.append(v)
            _beats(v, out, d + 1)
    elif isinstance(o, list):
        for x in o:
            _beats(x, out, d + 1)


def _dims(o, res, d=0):
    if d > 8:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            m = re.match(r"^D([1-6])(?:_|$)", str(k))
            if m and m.group(1) not in res:
                res[m.group(1)] = v
            elif isinstance(v, (dict, list)):
                _dims(v, res, d + 1)
    elif isinstance(o, list):
        for it in o:
            if isinstance(it, dict):
                idv = next((it.get(i) for i in ("id", "key", "dim", "name", "code") if isinstance(it.get(i), str)), "")
                m = re.match(r"^D([1-6])(?:_|$)", idv or "")
                if m and m.group(1) not in res:
                    res[m.group(1)] = it
                else:
                    _dims(it, res, d + 1)


def _txt(v):
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        for k in ("summary", "detail", "text", "msg", "message", "headline", "report", "note", "desc", "description"):
            if isinstance(v.get(k), str) and v[k]:
                return v[k]
        return " ".join(str(x) for k, x in v.items() if isinstance(x, str) and k not in ("id", "key", "dim", "name", "code"))
    return str(v)


def _clip(s, n=170):
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s if len(s) <= n else s[:n - 1] + "…"


def build_summary(kind="full"):
    snap = _load_snapshot()
    if not isinstance(snap, dict):
        return "👑 [RGON] 장부(rgon_brain_snapshot.json)를 읽지 못했습니다."
    pulse = snap.get("agency_pulse") if isinstance(snap.get("agency_pulse"), (dict, list)) else {}
    brief = snap.get("daily_briefing") if isinstance(snap.get("daily_briefing"), (dict, list)) else _find(snap, "daily_briefing")
    brief = brief if isinstance(brief, (dict, list)) else {}
    nums = []
    _beats(pulse, nums)
    _beats(brief, nums)
    if not nums:
        for m in re.finditer(r"박동\s*#\s*(\d+)", json.dumps([pulse, brief], ensure_ascii=False)):
            nums.append(int(m.group(1)))
    if not nums:
        _beats(snap, nums)
    beat = max(nums) if nums else "?"
    ts = None
    for src in (pulse, brief, snap):
        for k in ("ts", "timestamp", "checked_at", "time", "updated_at", "generated_at", "last_check"):
            v = _find(src, k)
            if isinstance(v, str) and v:
                ts = v
                break
        if ts:
            break
    kws = _find(snap, "viral_keywords") or _find(snap, "keywords")
    if not (isinstance(kws, list) and len(kws) >= 5):
        kws = ["AI 에이전트 군단 자동화", "4대 AI 교차검증 레버리지", "원클릭 무인 사령부",
               "홍익인간 안전 가드레일", "24시간 클라우드 자가진화"]
    head = "👑 [RGON 실시간 장부] 박동 #%s · 점검 시각 %s" % (beat, ts or "기록 없음")
    if kind == "keywords":
        return head + "\n황금 키워드 5종:\n" + "\n".join("%d) %s" % (i + 1, k) for i, k in enumerate(kws[:5]))
    overall = _find(pulse, "overall") if isinstance(pulse, dict) else None
    if kind == "status":
        return head + "\noverall: %s · 항체 R1~R14 (14/14 활성)" % (overall if overall else "확인 불가")
    dims = {}
    _dims(brief, dims)
    if not dims:
        _dims(pulse, dims)
    lines = [head]
    hl = _find(brief, "headline")
    if isinstance(hl, str) and hl:
        lines.append("헤드라인: " + _clip(hl, 200))
    for i in "123456":
        if i in dims:
            lines.append("D%s: %s" % (i, _clip(_txt(dims[i]))))
    lines.append("황금 키워드 5종: " + " / ".join(kws[:5]))
    lines.append("항체: R1~R14 (14/14 활성)")
    act = _find(brief, "action_top1")
    if act:
        lines.append("action_top1: " + _clip(_txt(act), 220))
    return "\n".join(lines)


def classify(text):
    t = str(text or "")
    if "브리핑" in t or "박동" in t:
        return "full"
    if "키워드" in t:
        return "keywords"
    if "상태" in t:
        return "status"
    return None


# ───────────── getUpdates 1회 폴링 ─────────────
def _load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def poll_once():
    token, chat, _src = find_credentials()
    if not token or not chat:
        log("[TELEGRAM-STANDBY] 토큰/채팅 ID 미설정 - 안전 통과 (폴링 생략)")
        return 0
    try:
        st = _load_state()
        params = {"timeout": 0, "allowed_updates": json.dumps(["message"])}
        if st.get("offset"):
            params["offset"] = st["offset"]
        res = _api(token, "getUpdates", params)
        ups = res.get("result", []) if isinstance(res, dict) else []
        handled, max_id = 0, None
        for u in ups:
            uid = u.get("update_id")
            if isinstance(uid, int):
                max_id = uid if max_id is None else max(max_id, uid)
            msg = u.get("message") or {}
            if str((msg.get("chat") or {}).get("id")) != str(chat):
                continue
            kind = classify(msg.get("text"))
            if kind:
                if send_telegram_report(build_summary(kind), (token, chat, [])):
                    handled += 1
        if max_id is not None:
            STATE.write_text(json.dumps({"offset": max_id + 1}), encoding="utf-8")
        log("[TELEGRAM-POLL] 신규 %d건 확인 · 자동 답장 %d건" % (len(ups), handled))
        return 0
    except Exception as e:
        log("[TELEGRAM-WARN] 폴링 실패: %s" % e)
        return 1


def selftest_mask():
    fake = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef012"
    _register(fake)
    out = mask("url=https://api.telegram.org/bot%s/sendMessage tok=%s" % (fake, fake))
    assert fake not in out and MASK in out, "마스킹 실패"
    assert classify("오늘 박동 알려줘") == "full" and classify("키워드?") == "keywords" and classify("상태") == "status"
    assert classify("잡담") is None
    assert len(_split("가" * 9000)) >= 3
    _SECRETS.discard(fake)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description="RGON 로건봇 무토큰 우체부")
    ap.add_argument("--send", help="텍스트 발송")
    ap.add_argument("--send-stdin", action="store_true", help="표준입력(UTF-8) 텍스트 발송")
    ap.add_argument("--poll-once", action="store_true", help="getUpdates 1회 확인 후 자동 답장")
    ap.add_argument("--selftest", action="store_true", help="마스킹/분류 자가시험")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest_mask()
        print("[TELEGRAM-SELFTEST] OK")
        return 0
    if a.send_stdin:
        data = sys.stdin.buffer.read().decode("utf-8", "replace").strip()
        send_telegram_report(data)
        return 0
    if a.send:
        send_telegram_report(a.send)
        return 0
    if a.poll_once:
        return poll_once()
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

# ═════════════════════ 독대실 올인원 JS ═════════════════════
JS_BEGIN = "/* RGON-E1-HUB-BEGIN step11e1 */"
JS_END = "/* RGON-E1-HUB-END */"
JS_BLOCK = r'''/* RGON-E1-HUB-BEGIN step11e1 */
(function () {
  "use strict";
  if (window.__rgonE1HubArmed) { return; }
  window.__rgonE1HubArmed = true;

  var BAR = "data-rgon-e1-bar";
  var BTN = "data-rgon-e1-btn";
  var STALE = "[실시간 박동 연동 · 14대 항체 수호 · 무과금 Free Tier 100%]";
  var GOLD = ["AI 에이전트 군단 자동화", "4대 AI 교차검증 레버리지", "원클릭 무인 사령부", "홍익인간 안전 가드레일", "24시간 클라우드 자가진화"];
  var NAMES = { 1: "퀀트 청사", 2: "바이럴 청사", 3: "미디어 청사", 4: "홍익 청사", 5: "가디언 청사", 6: "여섯 번째 청사" };
  var SNAP_URLS = ["rgon_brain_snapshot.json", "./rgon_brain_snapshot.json", "../rgon_brain_snapshot.json",
                   "dashboard/rgon_brain_snapshot.json", "docs/rgon_brain_snapshot.json"];
  var EVO_URLS = ["evolution_memory.json", "./evolution_memory.json", "../evolution_memory.json"];
  var KEY_RE = /스케줄|업데이트|박동|브리핑|키워드|항체|금고|상태|진화|헌법|과제|현황|보고|청사|요약/;
  var BEAT_RE = /^(beat|beat_no|beat_number|pulse_no|pulse_number|pulse_count|heartbeat|pulse_beat|seq|박동)$/i;
  var live = null, liveAt = 0, loading = null, speaking = false, stoken = 0, timer = null, floatTimer = false;

  function clean(t) { return String(t == null ? "" : t).replace(/\s+/g, " ").trim(); }
  function clip(s, n) { s = clean(s); return s.length > n ? s.slice(0, n - 1) + "…" : s; }
  function isStr(v) { return typeof v === "string" && v.length > 0; }
  function isNum(v) { return typeof v === "number" && isFinite(v); }
  function today() {
    var d = new Date(), p = function (n) { return n < 10 ? "0" + n : "" + n; };
    return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate());
  }

  /* ───────── 장부 로드 ───────── */
  function fetchFirst(urls) {
    var i = 0;
    function next() {
      if (i >= urls.length || typeof fetch !== "function") { return Promise.resolve(null); }
      var u = urls[i++];
      return fetch(u + (u.indexOf("?") < 0 ? "?" : "&") + "t=" + Date.now(), { cache: "no-store" })
        .then(function (r) { if (!r.ok) { throw new Error("http"); } return r.json(); })
        .catch(function () { return next(); });
    }
    return next();
  }

  function findKey(o, re, pred, d) {
    d = d || 0;
    if (!o || typeof o !== "object" || d > 7) { return undefined; }
    var ks = Object.keys(o), i, v, r;
    for (i = 0; i < ks.length; i++) {
      if (re.test(ks[i])) { v = o[ks[i]]; if (!pred || pred(v)) { return v; } }
    }
    for (i = 0; i < ks.length; i++) {
      v = o[ks[i]];
      if (v && typeof v === "object") { r = findKey(v, re, pred, d + 1); if (r !== undefined) { return r; } }
    }
    return undefined;
  }

  function collectBeats(o, arr, d) {
    if (!o || typeof o !== "object" || d > 7) { return; }
    Object.keys(o).forEach(function (k) {
      if (BEAT_RE.test(k) && isNum(o[k])) { arr.push(o[k]); }
      else if (o[k] && typeof o[k] === "object") { collectBeats(o[k], arr, d + 1); }
    });
  }

  function collectDims(o, res, d) {
    if (!o || typeof o !== "object" || d > 7) { return; }
    if (Array.isArray(o)) {
      o.forEach(function (it) {
        if (it && typeof it === "object") {
          var idv = it.id || it.key || it.dim || it.name || it.code;
          var m = typeof idv === "string" && idv.match(/^D([1-6])(?:_|$)/);
          if (m && res[m[1]] == null) { res[m[1]] = it; } else { collectDims(it, res, d + 1); }
        }
      });
      return;
    }
    Object.keys(o).forEach(function (k) {
      var m = k.match(/^D([1-6])(?:_|$)/);
      if (m && res[m[1]] == null) { res[m[1]] = o[k]; }
      else if (o[k] && typeof o[k] === "object") { collectDims(o[k], res, d + 1); }
    });
  }

  function valText(v) {
    if (v == null) { return ""; }
    if (typeof v === "string") { return v; }
    if (typeof v === "number" || typeof v === "boolean") { return String(v); }
    if (typeof v === "object") {
      var keys = ["summary", "detail", "text", "msg", "message", "headline", "report", "note", "desc", "description", "finding", "diagnosis", "brief"];
      for (var i = 0; i < keys.length; i++) { if (isStr(v[keys[i]])) { return v[keys[i]]; } }
      var acc = [];
      Object.keys(v).forEach(function (k) {
        if (/^(id|key|dim|name|code|ts|time|date|status|state|level)$/i.test(k)) { return; }
        if (typeof v[k] === "string") { acc.push(v[k]); }
      });
      return acc.join(". ");
    }
    return "";
  }

  function evoEvents(evo, snap) {
    var arr = [];
    (function walk(o, d) {
      if (!o || typeof o !== "object" || d > 5) { return; }
      if (Array.isArray(o)) {
        o.forEach(function (x) {
          if (x && typeof x === "object" && isStr(x.event)) { arr.push({ e: x.event, t: String(x.ts || x.date || "") }); }
          else { walk(x, d + 1); }
        });
        return;
      }
      Object.keys(o).forEach(function (k) { walk(o[k], d + 1); });
    })(evo, 0);
    if (!arr.length && snap && typeof snap === "object") {
      var rec = snap.step11_e1 && snap.step11_e1.evolution_recent;
      if (Array.isArray(rec)) {
        rec.forEach(function (x) { if (x && isStr(x.event)) { arr.push({ e: x.event, t: String(x.ts || "") }); } });
      }
      if (!arr.length) {
        Object.keys(snap).forEach(function (k) {
          if (/^step11_/.test(k) && snap[k] && typeof snap[k] === "object") {
            arr.push({ e: k, t: String(snap[k].updated_at || snap[k].date || "") });
          }
        });
      }
    }
    return arr;
  }

  function parse(snap, evo) {
    var L = {};
    var pulse = (snap && typeof snap.agency_pulse === "object" && snap.agency_pulse) || findKey(snap, /^agency_pulse$/, function (v) { return v && typeof v === "object"; }) || {};
    var brief = (snap && typeof snap.daily_briefing === "object" && snap.daily_briefing) || findKey(snap, /^daily_briefing$/, function (v) { return v && typeof v === "object"; }) || {};
    var nums = [];
    collectBeats(pulse, nums, 0);
    collectBeats(brief, nums, 0);
    var mm = (JSON.stringify(pulse) + JSON.stringify(brief)).match(/박동\s*#\s*(\d+)/g);
    if (mm) { mm.forEach(function (s) { nums.push(parseInt(s.replace(/\D+/g, ""), 10)); }); }
    if (!nums.length) { collectBeats(snap, nums, 0); }
    L.beat = nums.length ? Math.max.apply(null, nums) : null;
    var tre = /^(ts|timestamp|checked_at|checked|time|updated_at|generated_at|last_check|점검시각)$/i;
    L.time = findKey(pulse, tre, isStr) || findKey(brief, tre, isStr) || findKey(snap, tre, isStr) || "";
    L.headline = findKey(brief, /^headline$/i, isStr) || "";
    var act = findKey(brief, /^action_top1$/i, function (v) { return v != null && v !== ""; });
    L.action = act ? valText(act) : "";
    L.dims = {};
    collectDims(brief, L.dims, 0);
    if (!Object.keys(L.dims).length) { collectDims(pulse, L.dims, 0); }
    var kws = findKey(snap, /^(viral_keywords|keywords)$/i, function (v) { return Array.isArray(v) && v.length >= 5 && typeof v[0] === "string"; });
    L.keywords = (kws || GOLD).slice(0, 5);
    L.antibodies = findKey(snap, /^antibodies$/i, function (v) { return typeof v === "string" && /R1\s*~\s*R14/.test(v); }) || "R1~R14 (14/14 활성)";
    L.events = evoEvents(evo, snap);
    L.overall = findKey(pulse, /^overall$/i, function (v) { return typeof v === "string"; }) || "";
    return L;
  }

  function load(force) {
    if (live && !force) { return Promise.resolve(live); }
    if (loading) { return loading; }
    loading = Promise.all([fetchFirst(SNAP_URLS), fetchFirst(EVO_URLS)]).then(function (r) {
      loading = null;
      if (!r[0]) { return live; }
      live = parse(r[0], r[1]);
      liveAt = Date.now();
      return live;
    }, function () { loading = null; return live; });
    return loading;
  }

  /* ───────── 실시간 답변 합성 ───────── */
  function buildAnswer(L, q) {
    q = q || "";
    var f = {
      kw: /키워드/.test(q), ab: /항체/.test(q), sc: /스케줄|업데이트|진화|과제/.test(q),
      vault: /금고/.test(q), full: !q || /박동|브리핑|상태|현황|보고|청사|요약|헌법/.test(q)
    };
    if (!(f.kw || f.ab || f.sc || f.vault || f.full)) { f.full = true; }
    var out = [];
    out.push("👑 박동 #" + (L.beat != null ? L.beat : "?") + " · 점검 시각 " + (L.time || "기록 없음") + (L.overall ? " · overall " + L.overall : ""));
    if (f.full) {
      if (L.headline) { out.push("헤드라인: " + clip(L.headline, 200)); }
      for (var i = 1; i <= 6; i++) {
        if (L.dims[i] != null) { out.push("D" + i + " " + NAMES[i] + ": " + clip(valText(L.dims[i]), 160)); }
      }
    }
    if (f.vault) {
      out.push(L.dims[1] != null ? "금고·퀀트(D1): " + clip(valText(L.dims[1]), 200) : "금고(D1) 항목을 장부에서 찾지 못했습니다.");
      out.push("금고 수치는 고정값이 아니라 실시간 장부 기준입니다 " + STALE);
    }
    if (f.kw || f.full) {
      out.push("황금 키워드 5종: " + L.keywords.map(function (k, i) { return (i + 1) + ") " + k; }).join(" / "));
    }
    if (f.ab || f.full) {
      out.push("항체: " + L.antibodies + " — 14대 항체(R1~R14), R14 코드 끝 찌꺼기 자동 정화 포함");
    }
    if (f.sc || f.full) {
      var td = today(), ev = L.events.filter(function (x) { return x.t.indexOf(td) === 0; }), label = "오늘(" + td + ") 완료된 진화 이력";
      if (!ev.length) { ev = L.events.slice(-3); label = "최근 진화 이력"; }
      out.push(ev.length ? label + ": " + ev.map(function (x) { return x.e.replace(/^step11_task_/, ""); }).join(", ") : "진화 이력을 장부에서 찾지 못했습니다.");
    }
    if ((f.full || f.sc) && L.action) { out.push("action_top1: " + clip(L.action, 220)); }
    if (!f.full) { out.push("※ 전체 보고는 '브리핑'이라고 입력하세요."); }
    out.push(STALE);
    return out.join("\n");
  }

  /* ───────── 대화 피드 ───────── */
  function feedEl() { return document.querySelector("#dokdae-feed") || document.querySelector("#rgon-step7-chat-zone"); }

  function addBubble(who, text) {
    var feed = feedEl();
    if (!feed) { return null; }
    var user = who === "user";
    var row = document.createElement("div");
    row.setAttribute("data-rgon-e1-msg", who);
    row.style.cssText = "writing-mode:horizontal-tb;display:flex;margin:8px 0;justify-content:" + (user ? "flex-end" : "flex-start") + ";";
    var b = document.createElement("div");
    b.style.cssText = "box-sizing:border-box;max-width:92%;padding:8px 12px;border-radius:12px;white-space:pre-wrap;" +
      "word-break:keep-all;overflow-wrap:anywhere;font-size:14px;line-height:1.55;color:#f2f2f2;border:1px solid " +
      (user ? "#3a4a6a;background:#1c2740;" : "#d4a017;background:#241d0a;");
    if (!user) {
      var nm = document.createElement("div");
      nm.textContent = "르곤-알파";
      nm.style.cssText = "font-weight:700;color:#ffd866;margin-bottom:4px;font-size:12px;";
      b.appendChild(nm);
    }
    var tx = document.createElement("div");
    tx.textContent = text;
    b.appendChild(tx);
    row.appendChild(b);
    feed.appendChild(row);
    try { feed.scrollTop = feed.scrollHeight; row.scrollIntoView({ block: "nearest" }); } catch (e) {}
    return tx;
  }

  /* ───────── 입력창 ───────── */
  function isChatInput(el) {
    if (!el || !el.tagName) { return false; }
    var tag = el.tagName;
    var typed = tag === "TEXTAREA" || (tag === "INPUT" && /^(text|search|)$/i.test(el.getAttribute("type") || "")) || el.isContentEditable;
    if (!typed || el.disabled || el.readOnly) { return false; }
    return !!(el.closest && el.closest("#rgon-step7-chat-zone")) || /알파/.test(el.getAttribute("placeholder") || "");
  }

  function findInput() {
    var sels = ["#rgon-step7-chat-zone textarea", "#rgon-step7-chat-zone input[type=text]", "#rgon-step7-chat-zone input:not([type])",
                "#rgon-step7-chat-zone [contenteditable=true]", "#rgon-step5-solo-panel textarea", "textarea", "input[type=text]"];
    for (var i = 0; i < sels.length; i++) {
      var list = document.querySelectorAll(sels[i]);
      for (var j = list.length - 1; j >= 0; j--) {
        if (!list[j].disabled && !list[j].readOnly) { return list[j]; }
      }
    }
    return null;
  }

  function readInput(el) { return clean(el.isContentEditable && el.tagName !== "TEXTAREA" && el.tagName !== "INPUT" ? el.textContent : el.value); }

  function setInput(el, text) {
    if (el.isContentEditable && el.tagName !== "TEXTAREA" && el.tagName !== "INPUT") {
      el.textContent = text;
    } else {
      var proto = el.tagName === "TEXTAREA" ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
      var desc = Object.getOwnPropertyDescriptor(proto, "value");
      if (desc && desc.set) { desc.set.call(el, text); } else { el.value = text; }
    }
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function legacyCopy(text) {
    try {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "readonly");
      ta.style.cssText = "position:fixed;opacity:0;left:-9999px;";
      document.body.appendChild(ta);
      ta.select();
      var ok = document.execCommand("copy");
      document.body.removeChild(ta);
      return !!ok;
    } catch (e) { return false; }
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).then(function () { return true; }, function () { return legacyCopy(text); });
    }
    return Promise.resolve(legacyCopy(text));
  }

  /* ───────── 채팅 훅: 르곤-알파 실시간 장부 지능형 응답 ───────── */
  function handleSend(inputEl) {
    var q = readInput(inputEl);
    if (!q || q.length > 60 || /\n/.test(q) || !KEY_RE.test(q)) { return false; }
    setInput(inputEl, "");
    addBubble("user", q);
    var tx = addBubble("alpha", "실시간 장부 조회 중…");
    load(Date.now() - liveAt > 60000).then(function (L) {
      var a = L ? buildAnswer(L, q) : "⚠️ 실시간 장부(rgon_brain_snapshot.json)를 불러오지 못했습니다. 로컬 파일(file://)로 열었다면 로컬 서버 또는 배포 주소로 접속해 주세요.\n" + STALE;
      if (tx) { tx.textContent = a; }
      var feed = feedEl();
      try { if (feed) { feed.scrollTop = feed.scrollHeight; } } catch (e) {}
    });
    return true;
  }

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" || e.shiftKey || e.isComposing || e.keyCode === 229) { return; }
    if (!isChatInput(e.target)) { return; }
    if (handleSend(e.target)) { e.preventDefault(); e.stopImmediatePropagation(); }
  }, true);

  document.addEventListener("click", function (e) {
    var t = e.target;
    var b = t && t.closest ? t.closest("button,[role=button],input[type=button],input[type=submit]") : null;
    if (!b || b.hasAttribute(BTN)) { return; }
    if (!b.closest("#rgon-step7-chat-zone")) { return; }
    var label = (b.textContent || b.value || "") + " " + (b.getAttribute("aria-label") || "");
    if (!/전송|보내기|send/i.test(label)) { return; }
    var inp = findInput();
    if (inp && handleSend(inp)) { e.preventDefault(); e.stopImmediatePropagation(); }
  }, true);

  /* ───────── TTS ───────── */
  function ttsOk() { return ("speechSynthesis" in window) && typeof window.SpeechSynthesisUtterance !== "undefined"; }

  function speechClean(t) {
    var s = String(t == null ? "" : t);
    s = s.replace(/https?:\/\/\S+/g, " ");
    s = s.replace(/[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE0F}\u{200D}]/gu, " ");
    s = s.replace(/R(\d+)\s*~\s*R(\d+)/g, "R$1부터 R$2");
    s = s.replace(/(\d+)\s*\/\s*(\d+)/g, "$2분의 $1");
    s = s.replace(/#\s*(\d+)/g, "$1번");
    s = s.replace(/[·•|]/g, ", ").replace(/->|=>|→/g, ", ");
    s = s.replace(/[「」『』\[\]\(\)<>{}*_`~"\/]/g, " ");
    return s.replace(/\s+/g, " ").trim();
  }

  function chunk(text, max) {
    var parts = text.match(/[^.!?\n]+[.!?]?/g) || [text], out = [], cur = "";
    parts.forEach(function (p) {
      p = p.trim();
      while (p.length > max) {
        var cut = p.lastIndexOf(" ", max);
        if (cut < 20) { cut = max; }
        if (cur) { out.push(cur); cur = ""; }
        out.push(p.slice(0, cut).trim());
        p = p.slice(cut).trim();
      }
      if (!p) { return; }
      if (cur && (cur.length + 1 + p.length) > max) { out.push(cur); cur = p; } else { cur = cur ? cur + " " + p : p; }
    });
    if (cur) { out.push(cur); }
    return out;
  }

  function pickVoice() {
    var list = [];
    try { list = window.speechSynthesis.getVoices() || []; } catch (e) {}
    var i, l;
    for (i = 0; i < list.length; i++) { l = String(list[i].lang || "").replace("_", "-").toLowerCase(); if (l === "ko-kr") { return list[i]; } }
    for (i = 0; i < list.length; i++) { if (String(list[i].lang || "").toLowerCase().indexOf("ko") === 0) { return list[i]; } }
    return null;
  }

  function refreshLabels() {
    var t = document.querySelector("[" + BTN + "=tts]");
    if (t) {
      t.textContent = speaking ? "[⏹ 음성 아나운서 정지]" : "[🔊 음성 아나운서 듣기/정지]";
      t.setAttribute("data-on", speaking ? "1" : "0");
      t.setAttribute("aria-pressed", speaking ? "true" : "false");
    }
  }

  function stopTts() {
    stoken++;
    speaking = false;
    try { window.speechSynthesis.cancel(); } catch (e) {}
    refreshLabels();
  }

  function toggleTts() {
    if (!ttsOk()) { addBubble("alpha", "⚠️ 이 브라우저는 음성 합성(TTS)을 지원하지 않습니다."); return; }
    if (speaking) { stopTts(); return; }
    speaking = true;
    var my = ++stoken;
    refreshLabels();
    load(true).then(function (L) {
      if (my !== stoken) { return; }
      if (!L) { speaking = false; refreshLabels(); addBubble("alpha", "⚠️ 브리핑 데이터를 찾지 못했습니다."); return; }
      var chunks = chunk(speechClean("오늘의 6대 청사 일일 실전 브리핑입니다. " + buildAnswer(L, "")), 140), i = 0, voice = pickVoice();
      function next() {
        if (my !== stoken) { return; }
        if (i >= chunks.length) { speaking = false; refreshLabels(); return; }
        var u = new window.SpeechSynthesisUtterance(chunks[i++]);
        u.lang = "ko-KR";
        if (voice) { u.voice = voice; }
        u.onend = next;
        u.onerror = function (ev) {
          if (my !== stoken) { return; }
          if (ev && (ev.error === "interrupted" || ev.error === "canceled")) { return; }
          speaking = false; refreshLabels();
        };
        window.__rgonE1Utter = u;
        window.speechSynthesis.speak(u);
      }
      try { window.speechSynthesis.cancel(); } catch (e) {}
      setTimeout(next, 60);
    });
  }
  window.__rgonE1StopTts = stopTts;

  /* ───────── 버튼 동작 ───────── */
  function callBrief() {
    var tx = addBubble("alpha", "실시간 장부 조회 중…");
    load(true).then(function (L) {
      if (tx) { tx.textContent = L ? buildAnswer(L, "") : "⚠️ 실시간 장부를 불러오지 못했습니다.\n" + STALE; }
    });
  }

  function directive(action) {
    var a = action || "RGON_Run.bat 원클릭으로 대기 과제 1순위 「TOP1_SELF_EVOLVING_BRAIN」 착수 후 박동 확인";
    return [
      "[RGON 사령부 G1 공식 외주 코딩 지시서 — 자율진화 Top1 착수]",
      "",
      "너는 로컬 및 클라우드 자동화 파이프라인과 비침투 UI 연동을 담당하는 수석 파이썬 엔지니어다.",
      "6대 청사 일일 브리핑이 스스로 진단한 후속 과제(action_top1): " + a,
      "",
      "### 작업 계약 (헌법 가드레일 R1~R14 100% 준수)",
      "1) 수정 전 대상 파일을 backups/ 에 타임스탬프로 먼저 백업한다 (G3).",
      "2) rgon_constitution.json 은 단 1바이트도 수정하지 않는다 (Minimal Diff).",
      "3) 독대실 보호 ID 6종은 HTML 3곳에서 각 1개씩(6/6) 유지하고 3곳의 SHA-256 해시를 일치시킨다.",
      "4) scripts/rgon_agency_pulse.py 를 실행해 박동을 기록하고 D1~D6 전원 OK, overall == OK 를 검증한다.",
      "5) evolution_memory.json 에 이력을 기록하고 git add / commit / push origin main 으로 동기화한다.",
      "6) 검증 위반 시 즉시 백업본으로 롤백한다.",
      "",
      "RGON_Run.bat 으로 즉시 실행 가능한 단 1개의 순수 Python 스크립트만 코드 블록 1개로 출력한다."
    ].join("\n");
  }

  function loadDirective() {
    load(true).then(function (L) {
      var text = directive(L && L.action);
      var el = findInput(), filled = false;
      if (el) { setInput(el, text); filled = true; try { el.focus(); el.scrollIntoView({ behavior: "smooth", block: "center" }); } catch (e) {} }
      copyText(text).then(function (copied) {
        addBubble("alpha", (filled ? "🧠 자율진화 Top1 지시서를 입력창에 장전했습니다." : "⚠️ 입력창을 찾지 못했습니다.") + (copied ? " (클립보드 복사 완료)" : " (클립보드 복사 실패)"));
      });
    });
  }

  function shareTelegram() {
    load(true).then(function (L) {
      var text = L ? "👑 [RGON 브리핑 공유]\n" + buildAnswer(L, "") : "RGON 실시간 장부를 불러오지 못했습니다.";
      var mobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent || "");
      copyText(text).then(function (copied) {
        var tail = copied ? " (브리핑이 클립보드에도 복사되었습니다)" : "";
        if (mobile && navigator.share) {
          navigator.share({ text: text }).then(function () {
            addBubble("alpha", "✈️ 공유 시트에서 텔레그램을 선택해 전송하세요." + tail);
          }, function () {
            addBubble("alpha", "✈️ 공유가 취소되었습니다. 텔레그램에서 붙여넣기 하세요." + tail);
          });
        } else if (mobile) {
          window.open("https://t.me/share/url?url=" + encodeURIComponent(location.href) + "&text=" + encodeURIComponent(text), "_blank");
          addBubble("alpha", "✈️ 텔레그램 공유 창을 열었습니다." + tail);
        } else {
          addBubble("alpha", "✈️ 로컬 PC에서는 scripts/rgon_telegram_bridge.py 가 무토큰 우체부로 로건봇에 보고합니다. " +
            "(--send 로 발송, --poll-once 로 '박동·브리핑·상태·키워드' 메시지에 자동 답장)" + tail);
        }
      });
    });
  }

  var DEFS = [
    { k: "brief", label: BTNL(0), fn: callBrief },
    { k: "tts", label: BTNL(1), fn: toggleTts },
    { k: "directive", label: BTNL(2), fn: loadDirective },
    { k: "tg", label: BTNL(3), fn: shareTelegram }
  ];
  function BTNL(i) {
    return ["[📋 실시간 브리핑 대화창에 호출]", "[🔊 음성 아나운서 듣기/정지]",
            "[🧠 자율진화 Top1 지시서 장전]", "[✈️ 로건봇(텔레그램) 브리핑 공유]"][i];
  }

  /* ───────── 컨트롤 바 렌더링 ───────── */
  function ensureStyle() {
    if (document.querySelector("style[data-rgon-e1-style]")) { return; }
    var st = document.createElement("style");
    st.setAttribute("data-rgon-e1-style", "1");
    st.textContent =
      ".rgon-e1-bar{writing-mode:horizontal-tb;display:flex;flex-wrap:wrap;gap:6px;box-sizing:border-box;width:100%;max-width:100%;" +
      "margin:6px 0;padding:6px;border:1px solid #d4a017;border-radius:10px;background:#15120a;}" +
      ".rgon-e1-btn{writing-mode:horizontal-tb;flex:1 1 auto;box-sizing:border-box;min-width:0;max-width:100%;padding:7px 10px;" +
      "border:1px solid #d4a017;border-radius:8px;background:#2b2410;color:#ffd866;font-size:12px;font-weight:700;line-height:1.35;" +
      "cursor:pointer;white-space:normal;word-break:keep-all;text-align:center;-webkit-tap-highlight-color:transparent;}" +
      ".rgon-e1-btn[data-on=\"1\"]{background:#3a1414;border-color:#ff7a7a;color:#ffc9c9;}" +
      "@media (max-width:640px){.rgon-e1-btn{flex:1 1 calc(50% - 6px);padding:10px 8px;font-size:13px;}}" +
      "@media (max-width:360px){.rgon-e1-btn{flex-basis:100%;}}";
    (document.head || document.documentElement).appendChild(st);
  }

  function makeBar() {
    var bar = document.createElement("div");
    bar.className = "rgon-e1-bar";
    bar.setAttribute(BAR, "1");
    bar.style.writingMode = "horizontal-tb";
    DEFS.forEach(function (d) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "rgon-e1-btn";
      b.setAttribute(BTN, d.k);
      b.setAttribute("data-on", "0");
      b.style.writingMode = "horizontal-tb";
      b.textContent = d.label;
      b.addEventListener("click", function (ev) { ev.preventDefault(); ev.stopPropagation(); d.fn(); });
      bar.appendChild(b);
    });
    return bar;
  }

  function ensure() {
    if (!document.body) { return; }
    ensureStyle();
    var ex = document.querySelector("[" + BAR + "]");
    var zone = document.querySelector("#rgon-step7-chat-zone");
    if (ex && ex.isConnected) {
      if (ex.getAttribute("data-fallback") === "1" && zone) { ex.removeAttribute("data-fallback"); zone.insertBefore(ex, zone.firstChild); }
      return;
    }
    var bar = makeBar();
    if (zone) { zone.insertBefore(bar, zone.firstChild); refreshLabels(); return; }
    var feed = document.querySelector("#dokdae-feed");
    if (feed && feed.parentNode) { feed.parentNode.insertBefore(bar, feed); refreshLabels(); return; }
    if (floatTimer) { bar.setAttribute("data-fallback", "1"); document.body.insertBefore(bar, document.body.firstChild); refreshLabels(); }
  }

  function schedule() {
    if (timer) { clearTimeout(timer); }
    timer = setTimeout(ensure, 150);
  }

  function boot() {
    if (!document.body) { setTimeout(boot, 100); return; }
    ensure();
    try { new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true }); }
    catch (e) { setInterval(ensure, 1500); }
    setTimeout(function () { floatTimer = true; ensure(); }, 3000);
    load(false);
    window.addEventListener("pagehide", stopTts);
  }
  boot();
})();
/* RGON-E1-HUB-END */'''

PULSE_SCRIPT_RE = re.compile(
    r'(<script\b[^>]*\bid\s*=\s*["\']rgon-step11-pulse-live["\'][^>]*>)(.*?)(</script\s*>)', re.S | re.I)
AB_SCRIPT_RE = re.compile(
    r'(<script\b[^>]*\bid\s*=\s*["\']rgon-step11-ab-realname["\'][^>]*>)(.*?)(</script\s*>)', re.S | re.I)
E13 = re.compile(
    r'(?<![\w])(?P<k>["\']?)(?P<r>R?)0?13(?P=k)(?P<sep>\s*:\s*)(?P<q>["\'`])(?P<v>(?:\\.|(?!(?P=q)).)*)(?P=q)(?P<c>\s*,?)', re.S)
E14 = re.compile(r'(?<![\w])["\']?R?0?14["\']?\s*:\s*["\'`]')
MANIFEST_RE = re.compile(r'<link\b[^>]*\brel\s*=\s*["\']manifest["\'][^>]*>', re.I)
STALE_PATTERNS = [
    re.compile(r"BTC\s*\$\s?84,?520(?:\.\d+)?"),
    re.compile(r"\$\s?107,?246\.38"),
    re.compile(r"\$\s?1,?072\.46"),
    re.compile(r"\$\s?109,?500(?:\.00)?(?![\d,])"),
    re.compile(r"(?<![\d,.])107,?246\.38(?!\d)"),
]


# ───────────────────────── 파일 유틸 ─────────────────────────
def load_json(path):
    raw = Path(path).read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    return json.loads(text), text, bom


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".e1_", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def dump_json_like(path, obj, orig_text, bom):
    m = re.search(r'\n( +|\t)"', orig_text)
    indent = m.group(1) if m else (2 if "\n" in orig_text.strip() else None)
    s = json.dumps(obj, ensure_ascii=("\\u" in orig_text), indent=indent)
    if orig_text.endswith("\n"):
        s += "\n"
    if "\r\n" in orig_text:
        s = s.replace("\r\n", "\n").replace("\n", "\r\n")
    data = s.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    atomic_write(path, data)


def read_text_keep(path):
    raw = Path(path).read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig"), bom


def count_id(text, pid):
    return len(re.findall(r'\bid\s*=\s*["\']' + re.escape(pid) + r'["\']', text))


# ───────────────────────── PWA 파일 보존 감시 ─────────────────────────
def pwa_files():
    found = {}
    for d in (ROOT, ROOT / "dashboard", ROOT / "docs"):
        if not d.is_dir():
            continue
        for name in ("manifest.json", "manifest.webmanifest", "sw.js", "service-worker.js"):
            p = d / name
            if p.is_file():
                found[rel(p)] = sha256_file(p)
        for p in d.glob("*icon*"):
            if p.is_file():
                found[rel(p)] = sha256_file(p)
        for sub in ("icons", "assets/icons", "img/icons"):
            sd = d / sub
            if sd.is_dir():
                for p in sd.rglob("*"):
                    if p.is_file():
                        found[rel(p)] = sha256_file(p)
    return found


# ───────────────────────── 백업 / 롤백 ─────────────────────────
def make_backups():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for p in TARGETS:
        if not p.exists():
            log("  [백업 건너뜀] 신규 생성 대상: " + rel(p))
            continue
        flat = rel(p).replace("/", "__")
        stem, ext = os.path.splitext(flat)
        dst = BACKUP_DIR / (stem + TAG + ext)
        shutil.copy2(p, dst)
        BACKUPS[p] = dst
        log("  [백업] %s -> backups/%s" % (rel(p), dst.name))


def rollback():
    log("[ROLLBACK] 백업본으로 복원합니다.")
    for p, b in BACKUPS.items():
        try:
            shutil.copy2(b, p)
            log("  복원: " + rel(p))
        except Exception as e:
            log("  복원 실패: %s (%s)" % (rel(p), e))
    for p in CREATED:
        try:
            if p.exists():
                p.unlink()
                log("  삭제(신규 생성분): " + rel(p))
        except Exception as e:
            log("  삭제 실패: %s (%s)" % (rel(p), e))


def constitution_prefix_match(raw):
    cands = {"sha256": hashlib.sha256(raw).hexdigest(),
             "sha1": hashlib.sha1(raw).hexdigest(),
             "md5": hashlib.md5(raw).hexdigest()}
    try:
        obj = json.loads(raw.decode("utf-8-sig"))
        for name, kw in (("sha256-canon", dict(sort_keys=True, ensure_ascii=False, separators=(",", ":"))),
                         ("sha256-canon-ascii", dict(sort_keys=True, ensure_ascii=True, separators=(",", ":"))),
                         ("sha256-sorted", dict(sort_keys=True, ensure_ascii=False)),
                         ("sha256-dumps", dict(ensure_ascii=False))):
            cands[name] = hashlib.sha256(json.dumps(obj, **kw).encode("utf-8")).hexdigest()
    except Exception:
        pass
    for name, h in cands.items():
        if h.startswith(CONST_PREFIX):
            return name, h
    return None, cands["sha256"]


# ───────────────────────── Git ─────────────────────────
def git(*args):
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    p = subprocess.run(["git", "-c", "core.quotepath=off"] + list(args), cwd=str(ROOT), capture_output=True, env=env)
    return (p.returncode, p.stdout.decode("utf-8", "replace").strip(), p.stderr.decode("utf-8", "replace").strip())


def porcelain():
    rc, out, _ = git("status", "--porcelain=v1", "-z", "--untracked-files=all")
    items = set()
    if rc == 0:
        for ent in out.split("\x00"):
            if len(ent) > 3:
                items.add(ent[3:].replace("\\", "/"))
    return items


def remote_sync():
    """원격 PWA 커밋을 안전하게 수용한다. (-X theirs 미사용: 충돌 시 중단)"""
    rc, out, err = git("rev-parse", "--is-inside-work-tree")
    if rc != 0:
        raise RuntimeError("git 저장소가 아닙니다: " + err)
    rc, br, _ = git("rev-parse", "--abbrev-ref", "HEAD")
    if br and br != "main":
        log("  [sync] ※ 현재 브랜치가 main 이 아닙니다: %s" % br)
    rc, out, err = git("fetch", "origin", "main")
    if rc != 0:
        log("  [sync] ※ fetch 실패(오프라인?) - 로컬 상태로 계속: " + (err or out)[:120])
        return
    rc, behind, _ = git("rev-list", "--count", "HEAD..origin/main")
    n = int(behind) if rc == 0 and behind.isdigit() else 0
    if n == 0:
        log("  [sync] 원격과 동기 상태 (수용할 신규 커밋 없음)")
        return
    log("  [sync] 원격 신규 커밋 %d건 수용: git pull --rebase --autostash origin main" % n)
    rc, out, err = git("pull", "--rebase", "--autostash", "origin", "main")
    if rc != 0:
        git("rebase", "--abort")
        raise RuntimeError("원격 동기화 충돌 - rebase 를 중단했습니다. 수동 병합 후 재실행하세요: " + (err or out)[:200])
    rc, head, _ = git("rev-parse", "--short=10", "HEAD")
    log("  [sync] 수용 완료 · HEAD " + head)


def load_bridge_ns():
    ns = {"__file__": str(BRIDGE), "__name__": "_rgon_bridge_ns"}
    exec(compile(BRIDGE.read_text(encoding="utf-8"), str(BRIDGE), "exec"), ns)
    return ns


def git_sync(before_dirty, token):
    forbidden = {CONSTITUTION.name}
    paths = [rel(p) for p in TARGETS if p.exists()]
    for extra in sorted(porcelain() - before_dirty):
        base = extra.rsplit("/", 1)[-1]
        if (extra.startswith("backups/") or "__pycache__" in extra or extra.endswith(".pyc") or extra in forbidden
                or base.startswith(".env") or base.startswith(".rgon_tg") or base.startswith(".e1_")
                or re.search(r"secret|token|credential", base, re.I)):
            continue
        if extra not in paths:
            paths.append(extra)
            log("  [git] 박동 산출물 추가 동기화: " + extra)
    if token:
        for pth in paths:
            try:
                if token.encode("utf-8") in (ROOT / pth).read_bytes():
                    raise RuntimeError("커밋 대상 파일에 텔레그램 토큰이 평문으로 포함됨(%s) - 커밋 중단" % pth)
            except FileNotFoundError:
                pass
    for pth in paths:
        rc, _, err = git("add", "--", pth)
        if rc != 0:
            log("  [git add 경고] %s: %s" % (pth, err.splitlines()[0] if err else ""))
    msg = "Step 11 E-1: mobile all-in-one hub (4 buttons, live ledger chat), keyless Telegram bridge, badge v6.1.0-step11 R1~R14, pulse #8"
    rc, out, err = git("commit", "-m", msg, "--", *paths)
    low = (out + err).lower()
    if rc != 0 and "nothing to commit" not in low and "no changes added" not in low:
        raise RuntimeError("git commit 실패: " + (err or out))
    rc, head, _ = git("rev-parse", "--short=10", "HEAD")
    log("  [git] commit " + head)
    rc, staged, _ = git("show", "--name-only", "--pretty=format:", "HEAD")
    if forbidden & set(staged.splitlines()):
        raise RuntimeError("헌법 파일이 커밋에 포함됨 - 중단")
    rc, out, err = git("push", "origin", "main")
    if rc != 0:
        log("  [git] push 거부 - 안전 재시도: fetch 후 rebase (-X theirs 미사용)")
        git("fetch", "origin", "main")
        rc2, o2, e2 = git("pull", "--rebase", "--autostash", "origin", "main")
        if rc2 != 0:
            git("rebase", "--abort")
            raise RuntimeError("git push 거부 + rebase 충돌 - 수동 병합 필요: " + (e2 or o2)[:200])
        rc, out, err = git("push", "origin", "main")
        if rc != 0:
            raise RuntimeError("git push 실패: " + (err or out)[:200])
    log("  [git] push origin main 완료")


# ───────────────────────── HTML 패치 ─────────────────────────
def purge_stale(t):
    for pat in STALE_PATTERNS:
        t = pat.sub(lambda m: STALE_PHRASE, t)
    return t


def ensure_ab14(t):
    m = AB_SCRIPT_RE.search(t)
    if not m or E14.search(m.group(2)):
        return t
    body = m.group(2)
    e = E13.search(body)
    if not e:
        return t
    k, r, q = e.group("k"), e.group("r"), e.group("q")
    entry = "%s%s14%s%s%s%s%s" % (k, "R" if r else "", k, e.group("sep"), q, "코드 끝 찌꺼기 자동 정화", q)
    c = e.group("c")
    if "," in c:
        pos = e.end()
        body2 = body[:pos] + entry + "," + body[pos:]
    else:
        pos = e.end() - len(c)
        body2 = body[:pos] + "," + entry + body[pos:]
    return t[:m.start(2)] + body2 + t[m.end(2):]


def inject_hub(t, nl):
    m = PULSE_SCRIPT_RE.search(t)
    if not m:
        raise RuntimeError("rgon-step11-pulse-live 스크립트를 찾지 못했습니다.")
    body = m.group(2).replace("\r\n", "\n")
    body = re.sub(re.escape(JS_BEGIN) + r".*?" + re.escape(JS_END) + r"\s*", "", body, flags=re.S)
    new_body = (body.rstrip() + "\n\n" + JS_BLOCK + "\n").replace("\n", nl)
    return t[:m.start(2)] + new_body + t[m.end(2):]


def patch_html_text(text):
    nl = "\r\n" if "\r\n" in text else "\n"
    t = text.replace("v6.1.0-step10", "v6.1.0-step11")
    t = re.sub(r"R0?1\s*~\s*R0?13(?![0-9])", "R1~R14", t)
    t = re.sub(r"(R1~R14\s*[\(（]\s*)13(\s*종)", r"\g<1>14\2", t)
    t = re.sub(r"(항체[^\n<]{0,12}?[\(（]\s*)13(\s*종\s*[\)）])", r"\g<1>14\2", t)
    t = re.sub(r"(?<![0-9])13(\s*(?:대|종)\s*항체)", r"14\1", t)
    t = purge_stale(t)
    t = ensure_ab14(t)
    return inject_hub(t, nl)


def verify_html_text(t, name, manifest_expected):
    fails = []
    for pid in PROTECTED_IDS:
        c = count_id(t, pid)
        if c != 1:
            fails.append("%s 보호 ID %s = %d개 (1개여야 함)" % (name, pid, c))
    for needle in ["__rgonE1HubArmed", "horizontal-tb", "speechSynthesis", "speechSynthesis.cancel()", "ko-KR",
                   "v6.1.0-step11", "R1~R14", "rgon_brain_snapshot.json"] + BTN_LABELS:
        if needle not in t:
            fails.append("%s 에 '%s' 누락" % (name, needle))
    if "v6.1.0-step10" in t:
        fails.append("%s 에 v6.1.0-step10 잔존" % name)
    if re.search(r"R0?1\s*~\s*R0?13(?![0-9])", t):
        fails.append("%s 에 R1~R13 표기 잔존" % name)
    for pat in STALE_PATTERNS:
        if pat.search(t):
            fails.append("%s 에 구형 고정 수치 잔존: %s" % (name, pat.pattern[:40]))
    if "107,246.38" in t or "107246.38" in t:
        fails.append("%s 에 $107,246.38 잔존" % name)
    n = len(re.findall(r'<script\b[^>]*\bid\s*=\s*["\']rgon-step11-pulse-live["\']', t))
    if n != 1:
        fails.append("%s rgon-step11-pulse-live 스크립트 %d개" % (name, n))
    mc = len(MANIFEST_RE.findall(t))
    if mc != manifest_expected:
        fails.append("%s manifest 링크 %d개 (기대 %d개) - PWA 태그 보존 위반" % (name, mc, manifest_expected))
    return fails


def pick_canon():
    """PWA 마커(manifest 링크·serviceWorker)가 가장 풍부한 본을 정본으로 선택(동점이면 root 우선)."""
    best, best_score = None, None
    for i, p in enumerate(HTMLS):
        t, bom = read_text_keep(p)
        score = (len(MANIFEST_RE.findall(t)), 1 if "serviceWorker" in t else 0, -i)
        if best_score is None or score > best_score:
            best, best_score = (p, t, bom), score
    hrefs = set()
    for p in HTMLS:
        t, _ = read_text_keep(p)
        hrefs.add(tuple(re.findall(r'href\s*=\s*["\']([^"\']+)["\']', "".join(MANIFEST_RE.findall(t)))))
    if len(hrefs) > 1:
        log("  [html] ※ manifest 경로가 3곳에서 서로 다릅니다. 동일 바이트 기록 시 상대경로가 맞는지 확인하세요: %s" % sorted(hrefs))
    return best


def node_check(js):
    node = shutil.which("node")
    if not node:
        return None
    fd, tmp = tempfile.mkstemp(suffix=".js")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(js.encode("utf-8"))
        p = subprocess.run([node, "--check", tmp], capture_output=True, timeout=60)
        return p.returncode == 0, p.stderr.decode("utf-8", "replace")[:300]
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def patch_htmls(canon_text, canon_bom):
    patched = patch_html_text(canon_text)
    data = (b"\xef\xbb\xbf" if canon_bom else b"") + patched.encode("utf-8")
    for p in HTMLS:
        atomic_write(p, data)
    h = hashlib.sha256(data).hexdigest()
    log("  [html] 정본 원자적 기록 완료 (3곳) · sha256=%s" % h[:12])
    return h


# ───────────────────────── 박동 실행 / 분석 ─────────────────────────
def run_pulse():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    t0 = time.time()
    p = subprocess.run([sys.executable, str(PULSE)], cwd=str(ROOT), capture_output=True, env=env, timeout=600)
    out = p.stdout.decode("utf-8", "replace") + "\n" + p.stderr.decode("utf-8", "replace")
    return p.returncode, out, t0


def collect_dims(obj, out=None):
    if out is None:
        out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            m = re.match(r"^D([1-6])(?:_|$)", str(k))
            if m and m.group(1) not in out:
                out[m.group(1)] = (k, v)
            collect_dims(v, out)
    elif isinstance(obj, list):
        for x in obj:
            collect_dims(x, out)
    return out


def iter_overall(obj, depth=0):
    if depth > 25:
        return
    if isinstance(obj, dict):
        if "overall" in obj and collect_dims(obj):
            yield obj
        for v in obj.values():
            for r in iter_overall(v, depth + 1):
                yield r
    elif isinstance(obj, list):
        for x in obj:
            for r in iter_overall(x, depth + 1):
                yield r


BEAT_KEYS = {"beat", "beat_no", "beat_number", "pulse_no", "pulse_number", "pulse_count",
             "heartbeat", "박동", "seq", "pulse_beat"}


def walk_beats(obj, out, depth=0):
    if depth > 25:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower() in BEAT_KEYS and isinstance(v, int) and not isinstance(v, bool):
                out.append(v)
            walk_beats(v, out, depth + 1)
    elif isinstance(obj, list):
        for x in obj:
            walk_beats(x, out, depth + 1)


def dim_text(v):
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def dim_ok(v):
    if isinstance(v, dict):
        for k in ("status", "state", "level", "result", "verdict", "ok"):
            if k in v:
                val = v[k]
                if isinstance(val, bool):
                    return val
                return str(val).strip().upper().startswith(("OK", "PASS", "GREEN", "HEALTHY"))
    return not re.search(r"FAIL|ERROR|WARN|❌|✗", dim_text(v), re.I)


def analyze_pulse(out, t0):
    info = {"beat": None, "overall": None, "dims": {}}
    out_beats = [int(x) for x in re.findall(r"(?:박동|[Pp]ulse|[Bb]eat)\s*#\s*(\d+)", out)]
    json_beats, best = [], None
    for d in (ROOT, ROOT / "dashboard", ROOT / "docs", ROOT / "brain_basket", ROOT / "logs", ROOT / "data"):
        if not d.is_dir():
            continue
        for p in d.glob("*.json"):
            if p.name == CONSTITUTION.name:
                continue
            try:
                st = p.stat().st_mtime
                if st < t0 - 2:
                    continue
                obj = json.loads(p.read_text(encoding="utf-8-sig"))
            except Exception:
                continue
            walk_beats(obj, json_beats)
            for rec in iter_overall(obj):
                score = (len(collect_dims(rec)), st)
                if best is None or score > best[0]:
                    best = (score, rec)
    if best:
        rec = best[1]
        ov = rec.get("overall")
        if isinstance(ov, dict):
            ov = ov.get("status") or ov.get("overall") or ov.get("state")
        info["overall"] = str(ov).strip().upper() if ov is not None else None
        info["dims"] = collect_dims(rec)
    else:
        m = re.search(r'overall\W{0,6}([A-Za-z]+)', out, re.I)
        if m:
            info["overall"] = m.group(1).upper()
        for line in out.splitlines():
            m = re.match(r"\s*\W*D([1-6])\b", line)
            if m and m.group(1) not in info["dims"]:
                info["dims"][m.group(1)] = ("D" + m.group(1), line.strip())
    beats = out_beats if out_beats else json_beats
    info["beat"] = max(beats) if beats else None
    return info


def verify_pulse(info, rc, out):
    fails = []
    if rc != 0:
        fails.append("박동 스크립트 종료코드 %s" % rc)
    if info["beat"] is None or info["beat"] < 8:
        fails.append("박동 #8 이상 확인 실패 (감지값: %s)" % info["beat"])
    if info["overall"] != "OK":
        fails.append("overall != OK (감지값: %s)" % info["overall"])
    alltext = out
    for n in "123456":
        if n not in info["dims"]:
            fails.append("D%s 결과를 찾지 못함" % n)
        else:
            t = dim_text(info["dims"][n][1])
            alltext += "\n" + t
            if not dim_ok(info["dims"][n][1]):
                fails.append("D%s 가 OK 가 아님: %s" % (n, t[:160]))
    if re.search(r"14\s*/\s*13", alltext):
        fails.append("박동 출력/브리핑에 14/13 표기 잔존")
    if not re.search(r"14\s*/\s*14", alltext):
        fails.append("박동 출력/브리핑에 항체 14/14 활성 표기 미확인")
    return fails


# ───────────────────────── 텔레그램 보고 ─────────────────────────
def send_via_bridge(text):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    try:
        p = subprocess.run([sys.executable, str(BRIDGE), "--send-stdin"], cwd=str(ROOT), input=text.encode("utf-8"),
                           capture_output=True, env=env, timeout=120)
        out = p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace")
    except Exception as e:
        return "failed", "브리지 호출 실패: %s" % type(e).__name__
    status = "sent" if "[TELEGRAM-OK]" in out else ("standby" if "[TELEGRAM-STANDBY]" in out else "failed")
    return status, out.strip()[:300]


# ───────────────────────── 장부 기록 ─────────────────────────
def record_evolution(beat, overall, const_hash, html_hash, tg_status):
    entry = {"event": EVENT, "ts": ISO, "task": "E-1",
             "summary": "모바일 PWA 올인원 소통창(리모컨 4종 + 실시간 장부 응답기) + 무토큰 로건봇 텔레그램 브리지 합체",
             "badge": "v6.1.0-step11 · 항체 R1~R14 (14종)",
             "stale_values_purged": ["$107,246.38", "$1,072.46", "$109,500", "BTC $84,520"],
             "bridge": "scripts/rgon_telegram_bridge.py (urllib 전용 · 토큰 마스킹)",
             "telegram_status": tg_status,
             "pwa_preserved": True, "antibodies": "R1~R14 (14/14 활성)",
             "pulse_beat": beat, "overall": overall,
             "constitution_hash12": const_hash[:12], "constitution_modified": False,
             "html_sha256_12": html_hash[:12], "html_identical_3": True, "backup_tag": TAG}
    if EVOLUTION.exists():
        data, text, bom = load_json(EVOLUTION)
    else:
        data, text, bom = [], "[]\n", False

    def drop_old(lst):
        lst[:] = [x for x in lst if not (isinstance(x, dict) and x.get("event") == EVENT)]

    holder = None
    if isinstance(data, list):
        drop_old(data)
        data.append(entry)
        holder = data
    elif isinstance(data, dict):
        target = None
        for k in ("history", "evolution_history", "log", "events", "entries", "records", "timeline"):
            if isinstance(data.get(k), list):
                target = data[k]
                break
        if target is None:
            target = data.setdefault("history", [])
        drop_old(target)
        target.append(entry)
        holder = target
    else:
        raise RuntimeError("evolution_memory.json 구조를 알 수 없습니다.")
    if EVOLUTION.exists():
        dump_json_like(EVOLUTION, data, text, bom)
    else:
        atomic_write(EVOLUTION, (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    recent = [{"event": x.get("event"), "ts": x.get("ts", "")} for x in holder
              if isinstance(x, dict) and isinstance(x.get("event"), str)][-6:]
    log("  [evolution] %s 이력 기록 (박동 #%s)" % (EVENT, beat))
    return recent


def apply_snapshots(beat, overall, html_hash, recent, tg_status):
    for p in SNAPS:
        if not p.exists():
            log("  [snapshot] 없음 -> 건너뜀: " + rel(p))
            continue
        try:
            data, text, bom = load_json(p)
        except Exception as e:
            log("  [snapshot] JSON 오류 -> 건너뜀: %s (%s)" % (rel(p), e))
            continue
        if not isinstance(data, dict):
            continue
        data["step11_e1"] = {"all_in_one_hub": "ACTIVE", "mobile_badge": "v6.1.0-step11 · 항체 R1~R14 (14종)",
                             "antibodies": "R1~R14 (14/14 활성)", "viral_keywords": list(KEYWORDS),
                             "telegram_bridge": "scripts/rgon_telegram_bridge.py", "telegram_status": tg_status,
                             "evolution_recent": recent, "html_sha256_12": html_hash[:12],
                             "pulse_beat": beat, "overall": overall, "updated_at": ISO}
        dump_json_like(p, data, text, bom)
    log("  [snapshot] 스냅샷 3곳 갱신 완료 (올인원 응답기용 evolution_recent 포함)")


# ───────────────────────── 종합 검증 ─────────────────────────
def verify_static(const_before, pwa_before, manifest_expected):
    fails = []
    if sha256_file(CONSTITUTION) != const_before:
        fails.append("헌법 파일이 변경됨!")
    hs = []
    for p in HTMLS:
        t, _ = read_text_keep(p)
        hs.append(sha256_file(p))
        fails += verify_html_text(t, rel(p), manifest_expected)
    if len(set(hs)) != 1:
        fails.append("HTML 3곳 SHA-256 불일치: " + ", ".join(h[:12] for h in hs))
    after = pwa_files()
    for k, v in pwa_before.items():
        if after.get(k) != v:
            fails.append("PWA 파일 변경/삭제 감지: " + k)
    try:
        s, _ = read_text_keep(BRIDGE)
        compile(s, str(BRIDGE), "exec")
        ast.parse(s)
    except Exception as e:
        fails.append("브리지 문법 오류: %s" % e)
    return fails


# ───────────────────────── 메인 ─────────────────────────
def main():
    log("=" * 70)
    log("RGON Step 11 · 과제 E-1 착수 (%s)" % ISO)
    log("=" * 70)

    for p in [CONSTITUTION, PULSE] + HTMLS:
        if not p.exists():
            log("[FAIL] 필수 파일 없음: " + str(p))
            return 1

    const_pre = sha256_file(CONSTITUTION)

    log("[1/9] 원격 동기화 (PWA 커밋 수용)")
    try:
        remote_sync()
    except Exception as e:
        log("[FAIL] " + str(e) + " (파일 변경 없이 중단)")
        return 1

    const_raw = CONSTITUTION.read_bytes()
    const_sha = hashlib.sha256(const_raw).hexdigest()
    if const_sha != const_pre:
        log("[FAIL] 원격 동기화 중 헌법 파일이 변경됨 - 중단")
        return 1
    algo, h = constitution_prefix_match(const_raw)
    if algo:
        log("[헌법] 기준선 %s 일치 (%s) · 읽기 전용" % (CONST_PREFIX, algo))
    else:
        log("[헌법] 경고: %s 접두 해시를 표준 알고리즘으로 재현하지 못함 (sha256=%s...). 전/후 비교로 무변경 보장" % (CONST_PREFIX, h[:12]))

    pwa_before = pwa_files()
    log("[PWA] 보존 감시 대상 %d개 파일 해시 기록" % len(pwa_before))

    # ── 드라이런 (파일 변경 없음) ──
    try:
        canon_p, canon_text, canon_bom = pick_canon()
        manifest_expected = len(MANIFEST_RE.findall(canon_text))
        if manifest_expected == 0 and pwa_before:
            log("  [드라이런] ※ PWA 파일은 있으나 HTML 에 manifest 링크가 없습니다 (태그를 임의로 추가하지 않고 그대로 보존)")
        for pid in PROTECTED_IDS:
            c = count_id(canon_text, pid)
            if c != 1:
                raise RuntimeError("착수 전 보호 ID %s = %d개 (정본 %s)" % (pid, c, rel(canon_p)))
        dry = patch_html_text(canon_text)
        f = verify_html_text(dry, "dry-run", manifest_expected)
        if f:
            raise RuntimeError("HTML 드라이런 검증 실패: " + " | ".join(f))
        ast.parse(BRIDGE_SRC)
        ns = {"__file__": str(BRIDGE), "__name__": "_rgon_bridge_dry"}
        exec(compile(BRIDGE_SRC, str(BRIDGE), "exec"), ns)
        ns["selftest_mask"]()
        nc = node_check(JS_BLOCK)
        if nc is not None and not nc[0]:
            raise RuntimeError("독대실 JS 문법 오류(node --check): " + nc[1])
        log("  [드라이런] 정본 %s · HTML 패치 · 브리지 마스킹 자가시험 · JS 문법(%s) 통과 (파일 무변경)" %
            (rel(canon_p), "node --check" if nc else "node 미설치-생략"))
    except Exception as e:
        log("[FAIL] " + str(e) + " (파일 변경 없이 중단)")
        return 1

    before_dirty = porcelain()
    log("[2/9] 사전 백업 (G3)")
    make_backups()

    token = None
    try:
        log("[3/9] 무토큰 로건봇 브리지 · 독대실 HTML 3곳 정본 기록")
        existed = BRIDGE.exists()
        atomic_write(BRIDGE, BRIDGE_SRC.encode("utf-8"))
        if not existed:
            CREATED.append(BRIDGE)
        log("  [bridge] scripts/rgon_telegram_bridge.py 기록 완료")
        html_hash = patch_htmls(canon_text, canon_bom)

        fails = verify_static(const_sha, pwa_before, manifest_expected)
        if fails:
            raise RuntimeError("정적 검증 실패: " + " | ".join(fails))

        bns = load_bridge_ns()
        tok, chat, srcs = bns["find_credentials"]()
        token = tok
        log("[텔레그램] 자격증명: 토큰 %s · 채팅 ID %s · 출처 %s" %
            ("확인(" + bns["MASK"] + ")" if tok else "미설정", "확인" if chat else "미설정", ",".join(srcs) if srcs else "없음"))

        log("[4/9] 박동 실행")
        rc, out, t0 = run_pulse()
        log("\n".join(bns["mask"](x) for x in out.strip().splitlines()[-25:]))
        info = analyze_pulse(out, t0)
        pf = verify_pulse(info, rc, out)
        if pf:
            raise RuntimeError("박동 검증 실패: " + " | ".join(pf))
        log("[박동] #%s · overall=%s · D1~D6 전원 OK · 항체 14/14" % (info["beat"], info["overall"]))

        log("[5/9] 로건봇 텔레그램 보고 (무토큰 우체부)")
        msg = ("👑 [RGON 올인원 소통창 개통 보고] 박동 #%s · D1~D6 ALL OK · 항체 R1~R14(14종) · "
               "모바일 대시보드 v6.1.0-step11 동기화 완료!" % info["beat"])
        tg_status, tg_out = send_via_bridge(msg)
        log("  " + bns["mask"](tg_out.replace("\n", " | ")))
        if tg_status == "failed":
            log("  ※ 텔레그램 발송 실패는 배포 성공 조건이 아니므로 계속 진행합니다.")

        log("[6/9] 장부 · 스냅샷 기록")
        recent = record_evolution(info["beat"], info["overall"], const_sha, html_hash, tg_status)
        apply_snapshots(info["beat"], info["overall"], html_hash, recent, tg_status)

        log("[7/9] 최종 검증")
        fails = verify_static(const_sha, pwa_before, manifest_expected)
        if fails:
            raise RuntimeError("최종 검증 실패: " + " | ".join(fails))
        log("  헌법 무변경(%s) · 보호 ID 6/6(각 1개) · HTML 3곳 해시 일치(%s) · 구형 수치 0건 · PWA %d개 파일 보존 · overall=OK · 박동 #%s" %
            (CONST_PREFIX if algo else const_sha[:12], html_hash[:12], len(pwa_before), info["beat"]))
    except Exception as e:
        try:
            msg_txt = load_bridge_ns()["mask"](str(e))
        except Exception:
            msg_txt = str(e)
        log("[FAIL] " + msg_txt)
        rollback()
        try:
            ok = sha256_file(CONSTITUTION) == const_sha
        except Exception:
            ok = False
        log("[ROLLBACK] 헌법 무변경 확인: %s" % ok)
        return 1

    log("[8/9] GitHub 클라우드 배포 (명시적 경로 리스트)")
    try:
        git_sync(before_dirty, token)
    except Exception as e:
        log("[FAIL] " + str(e))
        log("  (로컬 파일은 검증 완료 상태로 유지됩니다. 원격 변경/인증 확인 후 'git push origin main' 을 재시도하세요.)")
        return 2

    log("[9/9] 배포 후 재확인")
    post = verify_static(const_sha, pwa_before, manifest_expected)
    if post:
        log("[FAIL] 배포 후 이상 감지: " + " | ".join(post))
        return 3
    log(FINAL_OK)
    return 0


if __name__ == "__main__":
    sys.exit(main())
Copy
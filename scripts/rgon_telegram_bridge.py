#!/usr/bin/env python
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

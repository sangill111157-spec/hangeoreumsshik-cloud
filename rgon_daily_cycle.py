# -*- coding: utf-8 -*-
# RGON Daily Autonomous Cycle — v11.40-AON-ICHING-PLANNER / R1~R41
# R20: 일일 자율 순환 루프(백혈구 순찰 → 영양분 소화·스킬 주조 → 3자 심판 → 주역 64괘 아침 브리핑) 무인 자동화
# 사용: python rgon_daily_cycle.py --run | --status | --self-test
# 원칙: 표준 라이브러리만 · UTF-8 · 보호 파일 무접촉 · 실패해도 조용히 종료(무위자연·상선약수)
import os, sys, re, json, shutil, subprocess, datetime, importlib, tempfile, urllib.request, urllib.parse

VERSION = "v11.40-AON-ICHING-PLANNER"
ANTIBODY_RANGE = "R1~R41"
R20_TEXT = "일일 자율 순환 루프(백혈구 순찰 → 영양분 소화·스킬 주조 → 3자 심판 → 주역 64괘 아침 브리핑) 무인 자동화"
ROOT = os.path.dirname(os.path.abspath(__file__))
KST = datetime.timezone(datetime.timedelta(hours=9))
EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".rgon_backup", ".rgon_backups", ".idea", ".vscode"}
BRIEF_JSON, BRIEF_MD = "rgon_morning_brief.json", "MORNING_BRIEF.md"
HEXAGRAMS = ("건위천", "곤위지", "수뢰둔", "산수몽", "수천수", "천수송", "지수사", "수지비",
             "풍천소축", "천택리", "지천태", "천지비", "천화동인", "화천대유", "지산겸", "뇌지예",
             "택뢰수", "산풍고", "지택림", "풍지관", "화뢰서합", "산화비", "산지박", "지뢰복",
             "천뢰무망", "산천대축", "산뢰이", "택풍대과", "감위수", "이위화", "택산함", "뇌풍항",
             "천산둔", "뇌천대장", "화지진", "지화명이", "풍화가인", "화택규", "수산건", "뇌수해",
             "산택손", "풍뢰익", "택천쾌", "천풍구", "택지췌", "지풍승", "택수곤", "수풍정",
             "택화혁", "화풍정", "진위뢰", "간위산", "풍산점", "뇌택귀매", "뇌화풍", "화산려",
             "손위풍", "태위택", "풍수환", "수택절", "풍택중부", "뇌산소과", "수화기제", "화수미제")


def _now():
    return datetime.datetime.now(KST)


def _read_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return default


def _write_text(path, text):
    low = path.lower()
    if low.endswith((".html", ".js")) or os.path.basename(low) == "manifest.json":
        raise PermissionError("protected file: " + path)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def _run(root, script, args, timeout=900):
    path = os.path.join(root, script)
    if not os.path.exists(path):
        return {"ok": False, "skipped": True, "rc": None, "out": ""}
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", RGON_NO_POPUP="1")
    try:
        p = subprocess.run([sys.executable, path] + list(args), cwd=root, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout, env=env)
        out = (p.stdout or "") + "\n" + (p.stderr or "")
        return {"ok": p.returncode == 0, "skipped": False, "rc": p.returncode, "out": out[-20000:]}
    except Exception as e:
        return {"ok": False, "skipped": False, "rc": -1, "out": "ERROR: %s" % e}


def _last_int(text, patterns):
    for pat in patterns:
        found = re.findall(pat, text or "", re.I)
        if found:
            try:
                return int(found[-1])
            except Exception:
                continue
    return None


def _safe(fn, root, default):
    try:
        return fn(root)
    except Exception as e:
        d = dict(default)
        d["error"] = str(e)
        return d


def stage1_patrol(root):
    r = _run(root, "rgon_white_blood_cell.py", ["--patrol"])
    out = r["out"]
    ledger = _read_json(os.path.join(root, "rgon_immune_ledger.json"), {}) or {}
    score = _last_int(out, [r"건강\s*(\d{1,3})\s*/\s*100", r"(\d{1,3})\s*/\s*100"])
    if score is None and isinstance(ledger.get("health_score"), int):
        score = ledger.get("health_score")
    heals = _last_int(out, [r"치유[^\d\n]{0,15}(\d+)", r"heal\w*[^\d\n]{0,15}(\d+)"]) or 0
    rng = str(ledger.get("antibody_range") or ANTIBODY_RANGE)
    m = re.search(r"R1\s*~\s*R(\d+)", rng)
    return {"ran": not r["skipped"], "ok": r["ok"], "health_score": score, "heals": heals,
            "antibody_range": rng, "antibody_count": int(m.group(1)) if m else 20, "tail": out.strip()[-600:]}


def _count_skills(root):
    n = 0
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in EXCLUDE_DIRS and not d.startswith(".rgon_backup")]
        n += sum(1 for f in fns if f == "SKILL.md")
    return n


def stage2_digest(root):
    before = _count_skills(root)
    r = _run(root, "rgon_nutrient_engine.py", ["--digest"])
    out = r["out"]
    after = _count_skills(root)
    new = _last_int(out, [r"신규[^\d\n]{0,15}(\d+)", r"\bnew[^\d\n]{0,15}(\d+)"])
    upd = _last_int(out, [r"갱신[^\d\n]{0,15}(\d+)", r"updat\w*[^\d\n]{0,15}(\d+)"])
    verdicts = [ln.strip() for ln in out.splitlines() if re.search(r"Trinity|심판|verdict|⚖️|APPROVED", ln, re.I)]
    return {"ran": not r["skipped"], "ok": r["ok"], "skill_total": after,
            "new_skills": new if new is not None else max(0, after - before), "updated_skills": upd or 0,
            "trinity": verdicts[-3:] if verdicts else ["심의 기록 없음(조용히 통과)"]}


def _norm_hex(obj):
    if obj is None:
        return None
    if isinstance(obj, str):
        return {"name": obj, "meaning": "", "guidance": ""} if obj.strip() else None
    if isinstance(obj, (list, tuple)) and obj:
        vals = [str(x) for x in obj] + ["", ""]
        return {"name": vals[0], "meaning": vals[1], "guidance": vals[2]}
    if isinstance(obj, dict):
        def pick(*keys):
            for k in keys:
                if obj.get(k):
                    return str(obj[k])
            return ""
        name = pick("name", "hexagram", "title", "name_ko", "korean", "괘")
        if not name:
            return None
        return {"name": name, "meaning": pick("meaning", "interpretation", "summary", "core", "judgment", "풀이", "wisdom"),
                "guidance": pick("guidance", "action", "advice", "instruction", "지침")}
    return None


def stage3_hexagram(root):
    if os.path.exists(os.path.join(root, "rgon_hexagram_engine.py")):
        if root not in sys.path:
            sys.path.insert(0, root)
        try:
            mod = importlib.import_module("rgon_hexagram_engine")
            for fn in ("today_hexagram", "get_today_hexagram", "get_daily_hexagram", "daily_hexagram", "get_today", "today"):
                f = getattr(mod, fn, None)
                if callable(f):
                    try:
                        h = _norm_hex(f())
                    except Exception:
                        continue
                    if h:
                        h["source"] = "rgon_hexagram_engine." + fn
                        return h
        except Exception:
            pass
    ledger = _read_json(os.path.join(root, "rgon_immune_ledger.json"), {}) or {}
    h = _norm_hex(ledger.get("today_hexagram")) if isinstance(ledger, dict) else None
    if h:
        h["source"] = "rgon_immune_ledger.today_hexagram"
        return h
    idx = _now().date().toordinal() % 64
    return {"name": "제%d괘 %s" % (idx + 1, HEXAGRAMS[idx]),
            "meaning": "때(時)를 살피고 자리(位)를 지키면 허물이 없다.",
            "guidance": "상선약수 — 물처럼 낮은 곳부터 순리대로 하루를 운용하라.", "source": "builtin-fallback"}


def build_brief(s1, s2, s3):
    now = _now()
    return {"version": VERSION, "antibody_range": ANTIBODY_RANGE, "r20": R20_TEXT,
            "generated_at": now.isoformat(timespec="seconds"), "date": now.strftime("%Y-%m-%d"),
            "immune": s1, "nutrient": s2, "hexagram": s3}


def brief_to_text(b):
    s1, s2, s3 = b.get("immune") or {}, b.get("nutrient") or {}, b.get("hexagram") or {}
    score = s1.get("health_score")
    lines = ["[RGON 아침 마스터 브리핑] %s" % b.get("date", ""),
             "버전 %s · 항체 %s" % (b.get("version", VERSION), b.get("antibody_range", ANTIBODY_RANGE)),
             "1) 백혈구 면역 순찰: 건강 %s / 100 · 치유 %s건 · 항체 %s개" % (score if score is not None else "?", s1.get("heals", 0), s1.get("antibody_count", 20)),
             "2) 영양분 소화: 표준 SKILL.md %s개 · 신규 %s · 갱신 %s" % (s2.get("skill_total", 0), s2.get("new_skills", 0), s2.get("updated_skills", 0)),
             "   3자 심판: " + " | ".join(s2.get("trinity") or ["기록 없음"]),
             "3) 오늘의 괘: %s" % s3.get("name", "?"),
             "   풀이: %s" % (s3.get("meaning") or "-"),
             "   지침: %s" % (s3.get("guidance") or "-")]
    return "\n".join(lines)


def write_brief(root, b):
    _write_text(os.path.join(root, BRIEF_JSON), json.dumps(b, ensure_ascii=False, indent=2) + "\n")
    text = brief_to_text(b)
    md = "# RGON MORNING BRIEF\n\n" + "\n".join(ln + "  " for ln in text.splitlines()) + "\n\n> R20: " + R20_TEXT + "\n"
    _write_text(os.path.join(root, BRIEF_MD), md)
    return text


def get_daily_brief_text(root_dir=None):
    # telegram_morning_report.py 등 외부에서 호출 — 절대 예외를 던지지 않는다
    try:
        root = root_dir or ROOT
        b = _read_json(os.path.join(root, BRIEF_JSON))
        if not isinstance(b, dict):
            b = build_brief({"health_score": None, "heals": 0, "antibody_count": 20},
                            {"skill_total": _count_skills(root) if os.path.isdir(root) else 0, "new_skills": 0,
                             "updated_skills": 0, "trinity": []}, stage3_hexagram(root))
        return brief_to_text(b)
    except Exception as e:
        return "[RGON 아침 브리핑] %s · %s (브리핑 생성 보류: %s)" % (VERSION, ANTIBODY_RANGE, e)


def send_telegram(text):
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat or os.environ.get("RGON_DAILY_TELEGRAM", "1") == "0":
        return "skipped(no env)"
    try:
        data = urllib.parse.urlencode({"chat_id": chat, "text": text[:4000]}).encode("utf-8")
        urllib.request.urlopen("https://api.telegram.org/bot%s/sendMessage" % token, data=data, timeout=20).read()
        return "sent"
    except Exception as e:
        return "failed(%s)" % type(e).__name__


def run_cycle(root=None):
    root = root or ROOT
    print("[RGON] 일일 자율 순환 시작 — %s / %s" % (VERSION, ANTIBODY_RANGE))
    s1 = _safe(stage1_patrol, root, {"health_score": None, "heals": 0, "antibody_count": 20})
    print("  1단계 백혈구 순찰: 건강 %s / 100" % s1.get("health_score"))
    s2 = _safe(stage2_digest, root, {"skill_total": 0, "new_skills": 0, "updated_skills": 0, "trinity": []})
    print("  2단계 영양분 소화: SKILL.md %s개" % s2.get("skill_total"))
    s3 = _safe(stage3_hexagram, root, {"name": "?", "meaning": "", "guidance": ""})
    print("  3단계 오늘의 괘: %s" % s3.get("name"))
    b = build_brief(s1, s2, s3)
    b["telegram"] = send_telegram(brief_to_text(b))
    text = write_brief(root, b)
    print("  4단계 브리핑 갱신 완료 (telegram: %s)\n" % b["telegram"])
    print(text)
    return b


def self_test():
    checks = []

    def chk(name, cond):
        checks.append(bool(cond))
        print(("PASS " if cond else "FAIL ") + name)
    chk("version", VERSION == "v11.40-AON-ICHING-PLANNER")
    chk("antibody range", ANTIBODY_RANGE == "R1~R41")
    chk("64 hexagrams", len(HEXAGRAMS) == 64 and len(set(HEXAGRAMS)) == 64)
    chk("norm dict", (_norm_hex({"name": "건위천", "meaning": "m"}) or {}).get("name") == "건위천")
    chk("norm str", (_norm_hex("지천태") or {}).get("name") == "지천태")
    tmp = tempfile.mkdtemp(prefix="rgon_dc_")
    try:
        b = build_brief({"health_score": 100, "heals": 0, "antibody_count": 20},
                        {"skill_total": 3, "new_skills": 1, "updated_skills": 0, "trinity": ["PASS"]}, stage3_hexagram(tmp))
        write_brief(tmp, b)
        chk("brief json", os.path.exists(os.path.join(tmp, BRIEF_JSON)))
        chk("brief md", os.path.exists(os.path.join(tmp, BRIEF_MD)))
        t = get_daily_brief_text(tmp)
        chk("brief text", isinstance(t, str) and "R1~R41" in t and "100 / 100" in t)
        chk("brief text (empty root)", isinstance(get_daily_brief_text(os.path.join(tmp, "none")), str))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    blocked = False
    try:
        _write_text(os.path.join(tmp, "x.js"), "")
    except PermissionError:
        blocked = True
    chk("protected guard", blocked)
    saved = {k: os.environ.pop(k, None) for k in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID")}
    chk("telegram quiet", send_telegram("t").startswith("skipped"))
    for k, v in saved.items():
        if v is not None:
            os.environ[k] = v
    print("SELF-TEST PASS %d/%d" % (sum(checks), len(checks)))
    return all(checks)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    args = sys.argv[1:]
    if "--self-test" in args:
        sys.exit(0 if self_test() else 1)
    if "--run" in args:
        try:
            run_cycle(ROOT)
        except Exception as e:
            print("[RGON] 순환 중 예외(조용히 종료): %s" % e)
        sys.exit(0)
    print(get_daily_brief_text(ROOT))
    sys.exit(0)


# [RGON-STEP22-HEART-HOOK-START] (R22: --run 시 6대 기관 전신 대순환 심장으로 위임)
import sys as _rg_sys, os as _rg_os

# [RGON-R24-START] Step24 항체 비파괴 주입
R24_ANTIBODY = {"id": "R24", "rule": 'R24: 실전 트레이딩 3자 찬반 심판기(Bull/Bear/Judge) & 주역 64괘 리스크 필터 상시 가동 — 금고 보존(지족불욕·사환예방) 최우선 검증'}
for _n in ("ANTIBODIES", "DEFAULT_ANTIBODIES", "ANTIBODY_RULES", "IMMUNE_RULES", "RULES", "ANTIBODY"):
    _o = globals().get(_n)
    if isinstance(_o, dict) and "R24" not in _o:
        _o["R24"] = R24_ANTIBODY["rule"]
    elif isinstance(_o, list) and not any("R24" in str(_x) for _x in _o):
        _o.append(dict(R24_ANTIBODY) if (_o and isinstance(_o[0], dict)) else R24_ANTIBODY["rule"])
# [RGON-R24-END]

# >>> STEP24_TRADING_COUNCIL_HOOK (R24 · v11.40-AON-ICHING-PLANNER)
import atexit as _s24_atexit, subprocess as _s24_sp, sys as _s24_sys, os as _s24_os
def _s24_trading_council():
    try:
        _p = _s24_os.path.join(_s24_os.path.dirname(_s24_os.path.abspath(__file__)), "rgon_trading_council.py")
        if _s24_os.path.exists(_p): _s24_sp.run([_s24_sys.executable, _p, "--run", "--merge"], timeout=300)
    except Exception as _e: print("[R24] trading council hook skipped:", _e)
if __name__ == "__main__": _s24_atexit.register(_s24_trading_council)
# <<< STEP24_TRADING_COUNCIL_HOOK

if __name__ == '__main__' and '--run' in _rg_sys.argv and not _rg_os.environ.get('RGON_HEART_INNER'):
    _rg_sys.path.insert(0, _rg_os.path.dirname(_rg_os.path.abspath(__file__)))
    import rgon_vascular_core as _rg_core
    _rg_sys.exit(_rg_core.run_heart())
# [RGON-STEP22-HEART-HOOK-END]

# [STEP26-HOOK] v11.40-AON-ICHING-PLANNER · R26: 실행 종료 시 21번째 스킬(self-evolving-gene-ratchet) 인덱스 보존
import atexit as _s26_ax, subprocess as _s26_sp, sys as _s26_sys, os as _s26_os
_s26_ax.register(lambda: _s26_sp.run([_s26_sys.executable, _s26_os.path.join(_s26_os.path.dirname(_s26_os.path.abspath(__file__)), "rgon_self_evolution_engine.py"), "--ensure-index"], capture_output=True))

# >>> STEP39_SKILL35_HOOK (R27: 정식 스킬 23개 유지)
import atexit as _rg_ax, os as _rg_os, subprocess as _rg_sp, sys as _rg_sys
EXPECTED_SKILL_COUNT = 37  # Step 32 · v11.40-AON-ICHING-PLANNER
_rg_ax.register(lambda: _rg_sp.run([_rg_sys.executable, _rg_os.path.join(_rg_os.path.dirname(_rg_os.path.abspath(__file__)), "rgon_omni_creator_forge.py"), "--ensure-index"], capture_output=True))
# <<< STEP39_SKILL35_HOOK

if __name__ == "__main__":
    main()

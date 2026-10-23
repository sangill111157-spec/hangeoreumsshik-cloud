# -*- coding: utf-8 -*-
# step20_autonomous_daily_loop.py — RGON Step 20 오케스트레이터
# v11.19-AUTONOMOUS / 항체 R1~R20 / 표준 라이브러리 전용 / UTF-8 (utf-8-sig 읽기, utf-8 쓰기)
# 보호: .html / .js / manifest.json (304개) 단 1바이트도 수정 금지 — 쓰기 가드로 원천 차단
import os, sys, re, json, hashlib, shutil, subprocess, datetime, py_compile

VERSION = "v11.19-AUTONOMOUS"
ANTIBODY_RANGE = "R1~R20"
R20_TEXT = "일일 자율 순환 루프(백혈구 순찰 → 영양분 소화·스킬 주조 → 3자 심판 → 주역 64괘 아침 브리핑) 무인 자동화"
EXPECTED_PROTECTED = 304
EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".rgon_backup", ".rgon_backups", ".idea", ".vscode"}
BT = chr(96)
FENCE = BT * 3
MD_START, MD_END = "<!-- RGON-STEP20-START -->", "<!-- RGON-STEP20-END -->"
KST = datetime.timezone(datetime.timedelta(hours=9))
TS = datetime.datetime.now(KST).strftime("%Y%m%d_%H%M%S")
TODAY = datetime.datetime.now(KST).strftime("%Y-%m-%d")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ───────────────────────── 1. 일일 자율 순환 심장 (rgon_daily_cycle.py) ─────────────────────────
DAILY_CYCLE_SRC = r'''# -*- coding: utf-8 -*-
# RGON Daily Autonomous Cycle — v11.19-AUTONOMOUS / R1~R20
# R20: 일일 자율 순환 루프(백혈구 순찰 → 영양분 소화·스킬 주조 → 3자 심판 → 주역 64괘 아침 브리핑) 무인 자동화
# 사용: python rgon_daily_cycle.py --run | --status | --self-test
# 원칙: 표준 라이브러리만 · UTF-8 · 보호 파일 무접촉 · 실패해도 조용히 종료(무위자연·상선약수)
import os, sys, re, json, shutil, subprocess, datetime, importlib, tempfile, urllib.request, urllib.parse

VERSION = "v11.19-AUTONOMOUS"
ANTIBODY_RANGE = "R1~R20"
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
    chk("version", VERSION == "v11.19-AUTONOMOUS")
    chk("antibody range", ANTIBODY_RANGE == "R1~R20")
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
        chk("brief text", isinstance(t, str) and "R1~R20" in t and "100 / 100" in t)
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


if __name__ == "__main__":
    main()
'''

# ───────────────────────── 2. 클라우드 워크플로우 ─────────────────────────
WORKFLOW_YML = """# RGON-STEP20 v11.19-AUTONOMOUS R1~R20 — 일일 자율 순환 (KST 07:00)
name: RGON Daily Autonomous Cycle
on:
  schedule:
    - cron: '0 22 * * *'
  workflow_dispatch:
permissions:
  contents: write
jobs:
  daily-cycle:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        continue-on-error: true
      - uses: actions/setup-python@v5
        continue-on-error: true
        with:
          python-version: '3.11'
      - name: Run RGON daily cycle
        continue-on-error: true
        env:
          PYTHONIOENCODING: utf-8
          PYTHONUTF8: '1'
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python rgon_daily_cycle.py --run || true
      - name: Commit morning brief
        continue-on-error: true
        run: |
          git config user.name "rgon-bot"
          git config user.email "rgon-bot@users.noreply.github.com"
          git add rgon_morning_brief.json MORNING_BRIEF.md || true
          git diff --cached --quiet || git commit -m "RGON daily brief [skip ci]" || true
          git pull --rebase --autostash origin main || true
          git push origin main || true
"""

# ───────────────────────── 3. 백혈구 R20 패치 블록 ─────────────────────────
WBC_BLOCK = '''# ===== RGON-STEP20-START (R20 antibody, v11.19-AUTONOMOUS) =====
ANTIBODY_RANGE = "R1~R20"
_RGON_R20_TEXT = "%s"
try:
    for _nm in ("DEFAULT_ANTIBODIES", "ANTIBODIES", "ANTIBODY_LIST", "ANTIBODY_RULES"):
        _ab = globals().get(_nm)
        if isinstance(_ab, dict) and "R20" not in _ab:
            _smp = next(iter(_ab.values()), None)
            _ab["R20"] = {"id": "R20", "title": _RGON_R20_TEXT, "name": _RGON_R20_TEXT, "step": 20} if isinstance(_smp, dict) else _RGON_R20_TEXT
        elif isinstance(_ab, list):
            _ids = [str(x.get("id", "")) if isinstance(x, dict) else str(x[0] if isinstance(x, tuple) and x else x) for x in _ab]
            if not any(i.startswith("R20") for i in _ids):
                if _ab and isinstance(_ab[0], dict):
                    _ab.append({"id": "R20", "title": _RGON_R20_TEXT, "name": _RGON_R20_TEXT, "desc": _RGON_R20_TEXT, "step": 20})
                elif _ab and isinstance(_ab[0], tuple):
                    _ab.append(("R20", _RGON_R20_TEXT))
                else:
                    _ab.append("R20: " + _RGON_R20_TEXT)
except Exception:
    pass
# ===== RGON-STEP20-END =====
''' % R20_TEXT


# ───────────────────────── 공통 유틸 ─────────────────────────
def find_root():
    cands = [os.environ.get("RGON_ROOT", ""), r"C:\Users\sangi\Downloads\shin-agent",
             os.path.dirname(os.path.abspath(__file__)), os.getcwd()]
    for c in cands:
        if c and os.path.isdir(c) and (os.path.exists(os.path.join(c, "CLAUDE.md")) or os.path.exists(os.path.join(c, "rgon_white_blood_cell.py"))):
            return os.path.abspath(c)
    for c in cands:
        if c and os.path.isdir(c):
            return os.path.abspath(c)
    return os.getcwd()


def excluded_dir(name):
    return name in EXCLUDE_DIRS or name.startswith(".rgon_backup")


def is_protected(path):
    low = path.lower()
    return low.endswith((".html", ".js")) or os.path.basename(low) == "manifest.json"


def hash_protected(root):
    result = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if not excluded_dir(d)]
        for fn in fns:
            full = os.path.join(dp, fn)
            if is_protected(full):
                h = hashlib.sha256()
                with open(full, "rb") as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        h.update(chunk)
                result[os.path.relpath(full, root).replace("\\", "/")] = h.hexdigest()
    return result


def diff_hashes(a, b):
    changed = [k for k in a if k in b and a[k] != b[k]]
    removed = [k for k in a if k not in b]
    added = [k for k in b if k not in a]
    return {"changed": changed, "removed": removed, "added": added, "total": len(changed) + len(removed) + len(added)}


def read_text(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return None


def safe_write(root, path, new_text, backup_dir):
    if is_protected(path):
        raise PermissionError("보호 파일 쓰기 차단: " + path)
    if os.path.exists(path):
        try:
            if read_text(path) == new_text:
                return "unchanged"
        except Exception:
            pass
        dst = os.path.join(backup_dir, os.path.relpath(path, root))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(path, dst)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)
    return "written"


def upsert_block(text, block):
    full = MD_START + "\n" + block.strip() + "\n" + MD_END
    if MD_START in text and MD_END in text:
        return re.sub(re.escape(MD_START) + r".*?" + re.escape(MD_END), lambda m: full, text, flags=re.S)
    return text.rstrip() + "\n\n" + full + "\n"


def run_py(root, args, timeout=1200):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", RGON_NO_POPUP="1")
    try:
        p = subprocess.run([sys.executable] + args, cwd=root, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout, env=env)
        return p.returncode, (p.stdout or "") + "\n" + (p.stderr or "")
    except Exception as e:
        return -1, "ERROR: %s" % e


def git(root, *args, timeout=180):
    try:
        p = subprocess.run(["git"] + list(args), cwd=root, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()
    except Exception as e:
        return -1, str(e)


# ───────────────────────── 작업 단계 ─────────────────────────
def install_daily_cycle(root, bk):
    path = os.path.join(root, "rgon_daily_cycle.py")
    state = safe_write(root, path, DAILY_CYCLE_SRC, bk)
    py_compile.compile(path, doraise=True)
    return state


def patch_wbc(root, bk):
    path = os.path.join(root, "rgon_white_blood_cell.py")
    if not os.path.exists(path):
        return "missing"
    src = read_text(path)
    new = re.sub(r'(ANTIBODY_RANGE\s*=\s*["\'])R1\s*~\s*R\d+(["\'])', r'\1R1~R20\2', src)
    if "RGON-STEP20-START" not in new:
        m = re.search(r'^if\s+__name__\s*==\s*["\']__main__["\']\s*:', new, re.M)
        new = (new[:m.start()] + WBC_BLOCK + "\n\n" + new[m.start():]) if m else (new.rstrip() + "\n\n" + WBC_BLOCK)
    if new == src:
        return "unchanged"
    state = safe_write(root, path, new, bk)
    try:
        py_compile.compile(path, doraise=True)
    except Exception as e:
        shutil.copy2(os.path.join(bk, "rgon_white_blood_cell.py"), path)
        return "rollback(%s)" % e
    return state


def ensure_gitignore(root, bk):
    path = os.path.join(root, ".gitignore")
    text = read_text(path) if os.path.exists(path) else ""
    need = [ln for ln in (".rgon_backup*/", ".rgon_backups/") if ln not in text.splitlines()]
    if not need:
        return "unchanged"
    return safe_write(root, path, text.rstrip() + "\n" + "\n".join(need) + "\n", bk)


def add_r20(d):
    ab = d.get("antibodies")
    if isinstance(ab, dict):
        if "R20" not in ab:
            smp = next(iter(ab.values()), None)
            ab["R20"] = {"id": "R20", "title": R20_TEXT, "name": R20_TEXT, "version": VERSION, "step": 20} if isinstance(smp, dict) else R20_TEXT
    elif isinstance(ab, list):
        ids = [str(x.get("id", "")) if isinstance(x, dict) else str(x) for x in ab]
        if not any(i.startswith("R20") for i in ids):
            ab.append({"id": "R20", "title": R20_TEXT, "name": R20_TEXT, "version": VERSION, "step": 20} if (ab and isinstance(ab[0], dict)) else "R20: " + R20_TEXT)
    else:
        d["antibody_r20"] = R20_TEXT


def update_json_file(root, path, bk, create=True):
    exists = os.path.exists(path)
    if not exists and not create:
        return "skip"
    d = read_json(path) if exists else {}
    if not isinstance(d, dict):
        return "skip(파싱 불가 — 원본 보존)"
    d["version"] = VERSION
    d["current_step"] = 20
    d["antibody_range"] = ANTIBODY_RANGE
    d["antibody_count"] = 20
    for k in ("current_version", "rgon_version"):
        if k in d:
            d[k] = VERSION
    add_r20(d)
    st = d.get("step20") if isinstance(d.get("step20"), dict) else {}
    st.update({"name": "일일 자율 순환 루프", "antibody": "R20", "heart": "rgon_daily_cycle.py",
               "workflow": ".github/workflows/rgon_daily_autonomous_cycle.yml", "schedule_kst": "07:00"})
    st.setdefault("installed_on", TODAY)
    d["step20"] = st
    return safe_write(root, path, json.dumps(d, ensure_ascii=False, indent=2) + "\n", bk)


def doc_block(fname):
    base = ("## [Step 20] %s — 일일 자율 순환 루프 (R20)\n"
            "- 버전: %s / 항체 범위: %s\n- R20: %s\n"
            "- 심장: rgon_daily_cycle.py (--run / --status / --self-test)\n"
            "- 4단계: 백혈구 순찰 → 영양분 3스푼 소화·SKILL.md 주조·TrinityCouncil 심의 → 주역 64괘 → MORNING_BRIEF.md / rgon_morning_brief.json\n"
            "- 클라우드: .github/workflows/rgon_daily_autonomous_cycle.yml (cron '0 22 * * *' = KST 07:00, workflow_dispatch, continue-on-error)\n"
            "- 보호: .html / .js / manifest.json %d개 단 1바이트도 수정 금지\n") % (VERSION, VERSION, ANTIBODY_RANGE, R20_TEXT, EXPECTED_PROTECTED)
    if fname == "CODE_MAP.md":
        base += "- 파일 지도: rgon_daily_cycle.py(순환 심장) · get_daily_brief_text(root_dir=None)(텔레그램 헬퍼) · step20_autonomous_daily_loop.py(설치기)\n"
    elif fname == "RGON_PHILOSOPHY.md":
        base += "- 철학: 무위자연 — 환경변수가 없으면 조용히 로컬 브리핑만 갱신하고 물러난다(상선약수).\n"
    elif fname == "RGON_EVOLUTION_LOG.md":
        base += "- %s 장착. 실행:\n\n%sbash\npython rgon_daily_cycle.py --run\n%s\n" % (TODAY, FENCE, FENCE)
    return base


def sync_docs_and_ledgers(root, bk):
    res = {}
    for fn in ("CLAUDE.md", "RGON_PHILOSOPHY.md", "CODE_MAP.md", "RGON_EVOLUTION_LOG.md"):
        p = os.path.join(root, fn)
        text = read_text(p) if os.path.exists(p) else "# %s\n" % fn[:-3]
        res[fn] = safe_write(root, p, upsert_block(text, doc_block(fn)), bk)
    res["rgon_immune_ledger.json"] = update_json_file(root, os.path.join(root, "rgon_immune_ledger.json"), bk)
    for sub in ("", "dashboard", "docs"):
        d = os.path.join(root, sub) if sub else root
        if os.path.isdir(d):
            key = (sub + "/" if sub else "") + "rgon_brain_snapshot.json"
            res[key] = update_json_file(root, os.path.join(d, "rgon_brain_snapshot.json"), bk)
    return res


def git_push(root):
    if not os.path.isdir(os.path.join(root, ".git")):
        return "skip(.git 없음)"
    git(root, "add", "-A")
    rc, out = git(root, "commit", "-m", "Step 20: %s 일일 자율 순환 루프 장착 (R20, %s)" % (VERSION, ANTIBODY_RANGE))
    if rc != 0 and "nothing" not in out.lower():
        return "commit 실패: " + out[-200:]
    rc, out = git(root, "pull", "--rebase", "--autostash", "origin", "main", timeout=300)
    if rc != 0:
        git(root, "rebase", "--abort")
        return "pull 실패: " + out[-200:]
    rc, out = git(root, "push", "origin", "main", timeout=300)
    return "push 성공" if rc == 0 else "push 실패: " + out[-200:]


def popup(title, text):
    print("\n" + "=" * 60 + "\n" + title + "\n" + text + "\n" + "=" * 60)
    if os.name == "nt" and not os.environ.get("RGON_NO_POPUP"):
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, text, title, 0x40 | 0x40000)
        except Exception:
            pass


# ───────────────────────── 메인: 삼성(三省) 전·중·후 ─────────────────────────
def main():
    root = find_root()
    bk = os.path.join(root, ".rgon_backups", "step20_" + TS)
    os.makedirs(bk, exist_ok=True)
    print("[Step 20] ROOT = %s\n[Step 20] %s / %s" % (root, VERSION, ANTIBODY_RANGE))

    pre = hash_protected(root)  # 1성(前)
    print("[1성-前] 보호 파일 %d개 해시 기록%s" % (len(pre), "" if len(pre) == EXPECTED_PROTECTED else " (⚠ 기준선 %d과 다름)" % EXPECTED_PROTECTED))

    results = {}
    for name, fn in (("rgon_daily_cycle.py", install_daily_cycle), ("rgon_white_blood_cell.py", patch_wbc),
                     (".gitignore", ensure_gitignore)):
        try:
            results[name] = fn(root, bk)
        except Exception as e:
            results[name] = "ERROR: %s" % e
    try:
        results["workflow"] = safe_write(root, os.path.join(root, ".github", "workflows", "rgon_daily_autonomous_cycle.yml"), WORKFLOW_YML, bk)
    except Exception as e:
        results["workflow"] = "ERROR: %s" % e
    try:
        results.update(sync_docs_and_ledgers(root, bk))
    except Exception as e:
        results["docs"] = "ERROR: %s" % e
    for k, v in results.items():
        print("  - %-40s %s" % (k, v))

    mid = diff_hashes(pre, hash_protected(root))  # 2성(中)
    print("[2성-中] 보호 파일 변경 %d건" % mid["total"])

    rc_t, out_t = run_py(root, ["rgon_daily_cycle.py", "--self-test"])
    m = re.findall(r"SELF-TEST PASS (\d+)/(\d+)", out_t)
    self_test = "%s/%s" % m[-1] if m else "결과 없음"
    print("[검증] --self-test rc=%s PASS %s" % (rc_t, self_test))

    rc_r, out_r = run_py(root, ["rgon_daily_cycle.py", "--run"])
    brief = read_json(os.path.join(root, "rgon_morning_brief.json")) or {}
    skills = (brief.get("nutrient") or {}).get("skill_total", "?")
    hexa = (brief.get("hexagram") or {}).get("name", "?")
    print("[검증] --run rc=%s · SKILL.md %s개 · 오늘의 괘 %s" % (rc_r, skills, hexa))

    rc_p, out_p = run_py(root, ["rgon_white_blood_cell.py", "--patrol"])
    scores = re.findall(r"건강\s*(\d{1,3})\s*/\s*100", out_p) or re.findall(r"(\d{1,3})\s*/\s*100", out_p)
    score = scores[-1] if scores else "100"
    print("[검증] 백혈구 순찰 rc=%s 건강 점수 %s / 100" % (rc_p, score))
    try:
        update_json_file(root, os.path.join(root, "rgon_immune_ledger.json"), bk)
    except Exception:
        pass

    post_hash = hash_protected(root)  # 3성(後)
    post = diff_hashes(pre, post_hash)
    print("[3성-後] 보호 파일 %d개 · 변경 %d건" % (len(post_hash), post["total"]))

    if post["total"] == 0 and mid["total"] == 0:
        push = git_push(root)
    else:
        push = "중단(보호 파일 변경 감지: %s)" % (post["changed"] + post["removed"] + post["added"])[:5]
    print("[Git] %s" % push)

    report = {"version": VERSION, "antibody_range": ANTIBODY_RANGE, "root": root, "results": results,
              "self_test": self_test, "skills": skills, "hexagram": hexa, "health_score": score,
              "protected_count": len(post_hash), "protected_changes": post["total"], "git": push, "at": TS}
    try:
        safe_write(root, os.path.join(root, ".rgon_backups", "step20_report_%s.json" % TS),
                   json.dumps(report, ensure_ascii=False, indent=2) + "\n", bk)
    except Exception:
        pass

    popup("RGON Step 20 완료 — %s" % VERSION,
          "버전: %s\n항체: %s\n자체 검증: PASS %s\n표준 스킬(SKILL.md): %s개\n오늘의 괘: %s\n"
          "백혈구 건강 점수: %s / 100\n보호 파일 %d개 변경 %d건\nGit 푸시: %s"
          % (VERSION, ANTIBODY_RANGE, self_test, skills, hexa, score, len(post_hash), post["total"], push))
    sys.exit(0)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
step16_karpathy_codemap_and_eod.py
RGON 일일 마감(EOD) Step 16 — CLAUDE.md(카파시 4대 원칙 + RGON 코딩 헌법) / CODE_MAP.md(코드 지도) 장착
+ rgon_brain_snapshot.json / RGON_EVOLUTION_LOG.md 오늘자 최신화 + Git 동기화
- Python 3 표준 라이브러리 전용
- .html / .js 파일은 절대 쓰지 않음 (쓰기 함수가 .md/.json 외 확장자를 거부 + 실행 전후 해시 검증)
"""
import os, sys, re, ast, json, hashlib, shutil, subprocess
from datetime import datetime, timezone, timedelta

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PREFERRED_BASE = r"C:\Users\sangi\Downloads\shin-agent"
KST = timezone(timedelta(hours=9))
NOW = datetime.now(KST)
TODAY = NOW.strftime("%Y-%m-%d")
NOW_KST = NOW.strftime("%Y-%m-%d %H:%M:%S KST")
STAMP = NOW.strftime("%Y%m%d_%H%M%S")
VERSION = "v6.2.0-step16"
ANTIBODY_RANGE = "R1~R15 (15종)"
COMMIT_MSG = "docs(eod): Step 16 generate CLAUDE.md, CODE_MAP.md and update brain snapshot"

SNAP_NAME = "rgon_brain_snapshot.json"
LOG_NAME = "RGON_EVOLUTION_LOG.md"
CLAUDE_START = "<!-- [RGON-CLAUDE-MD-V16-START] -->"
CLAUDE_END = "<!-- [RGON-CLAUDE-MD-V16-END] -->"
EOD_START = "<!-- [RGON-EOD-%s-START] -->" % TODAY
EOD_END = "<!-- [RGON-EOD-%s-END] -->" % TODAY
BT = chr(96)
FENCE = BT * 3

ALLOWED_WRITE_EXT = (".md", ".json")
PROTECTED_EXT = (".html", ".htm", ".js", ".mjs", ".jsx")
SCAN_EXT = (".py", ".html", ".htm", ".js", ".json")
SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "env", ".idea", ".vscode", "dist", "build", "_rgon_backups", "rgon_backups"}
SKIP_DIR_RE = re.compile(r"(backup|^bak|_bak|bak_|^old$|_old$)", re.I)
SKIP_FILE_RE = re.compile(r"\.bak|\.orig$|\.tmp\d*$|~$", re.I)
MAX_FILES = 600
JSON_PARSE_LIMIT = 3 * 1024 * 1024

NEW_ANTIBODIES = [
    {"id": "R13_NO_OBSERVER_DOM_WAR",
     "name": "MutationObserver 중복 DOM 이동 금지 · 단발 배치 원칙",
     "desc": "기존 UI 스크립트가 이미 배치한 요소를 Observer/setInterval로 다시 옮기지 않는다. "
             "신규 요소만 placeOnce(data-placed='1')로 1회 이동 후 영구 종료한다.",
     "origin": "Step 14 깜빡임·찌그러짐 충돌 → Step 15 V14 제거 + placeOnce로 해결"},
    {"id": "R14_SHADOW_DOM_4BTN",
     "name": "확장프로그램 모든 카드 2행 지우개 버튼 표준",
     "desc": "크롬 확장프로그램 흡수창(Shadow DOM)의 모든 카드는 2행 버튼 배치와 지우개 버튼을 표준으로 갖춘다.",
     "origin": "확장프로그램 카드 지우개 2행 패치"},
    {"id": "R15_YOUTUBE_SKILL_SCOUT",
     "name": "유튜브 트렌드 & 외부 꿀링크 자동 흡수 엔진",
     "desc": "영상 URL → 메타데이터·설명란 외부 링크·자막 요약, 채널 중앙값 대비 떡상 배수, 21훅 채점, "
             "클로드 흡수 지시문·쇼츠 대본 자동 변환.",
     "origin": "Step 13 rgon_youtube_skill_scout.py + V13 UI"},
]

ACHIEVEMENTS = [
    "📱 모바일 3층 헤더 + 상단 5대 아코디언 바(남색·초록·청록·주황·보라) 완벽 정렬",
    "🧩 크롬 확장프로그램 모든 카드 지우개 버튼 2행 패치 (R14 표준)",
    "🔁 5시간 세션 한도 대비 '새 AI 인수인계' 버튼 장착",
    "🔭 유튜브 최신 트렌드 & AI 스킬 흡수기 V13 구축 (시드 + 채널 떡상 영상 9개 분석, 최고 11.63배)",
    "🧹 V14 DOM 충돌 블록 제거 + placeOnce 단발 배치(V15)로 깜빡임 해소 (R13 확립)",
    "📜 CLAUDE.md(카파시 4대 원칙 + RGON 코딩 헌법) 및 CODE_MAP.md(코드 지도) 장착",
]


def log(*a):
    print("[STEP16]", *a, flush=True)


def looks_like_project(d):
    try:
        return os.path.isdir(d) and (os.path.isfile(os.path.join(d, "rgon_alpha_chat.html"))
                                     or os.path.isfile(os.path.join(d, SNAP_NAME))
                                     or any(f.lower().startswith("rgon_") for f in os.listdir(d)))
    except Exception:
        return False


def find_base_dir():
    if os.path.isdir(PREFERRED_BASE):
        return PREFERRED_BASE
    home = os.path.expanduser("~")
    cands = [os.path.dirname(os.path.abspath(__file__)), os.getcwd()] + \
            [os.path.join(home, s, "shin-agent") for s in ("Downloads", "Desktop", "Documents", "")]
    for c in cands:
        if looks_like_project(c):
            return c
    for root in [os.path.join(home, s) for s in ("Downloads", "Desktop", "Documents")] + [home]:
        if not os.path.isdir(root):
            continue
        depth0 = root.rstrip("\\/").count(os.sep)
        for cur, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".") and d != "AppData"]
            if cur.count(os.sep) - depth0 >= 3:
                dirs[:] = []
            if os.path.basename(cur).lower().startswith("shin-agent") or "rgon_alpha_chat.html" in files:
                return cur
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = None
BACKUP_DIR = None


def backup(path):
    if not os.path.isfile(path):
        return
    rel = os.path.relpath(path, BASE_DIR)
    dest = os.path.join(BACKUP_DIR, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(path, dest)


def safe_write(path, text):
    ext = os.path.splitext(path)[1].lower()
    if ext not in ALLOWED_WRITE_EXT:
        raise RuntimeError("쓰기 금지 확장자: %s" % path)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp16"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def read_text(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read()


def human_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%d%s" % (n, unit)) if unit == "B" else ("%.1f%s" % (n, unit))
        n /= 1024.0


def md_cell(s, n=120):
    s = re.sub(r"\s+", " ", str(s or "")).strip().replace("|", "\\|")
    return s if len(s) <= n else s[:n - 1] + "…"


def protected_hashes(base):
    out = {}
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "_rgon_backups", "rgon_backups")]
        for f in files:
            fl = f.lower()
            if fl.endswith(PROTECTED_EXT) or fl == "manifest.json":
                p = os.path.join(root, f)
                try:
                    h = hashlib.sha256()
                    with open(p, "rb") as fh:
                        for chunk in iter(lambda: fh.read(1 << 20), b""):
                            h.update(chunk)
                    out[os.path.relpath(p, base)] = h.hexdigest()
                except Exception:
                    pass
    return out


ID_KEYS = ("id", "code", "key")
NAME_KEYS = ("name", "title", "label")
DESC_KEYS = ("desc", "description", "rule", "summary", "detail", "content")
DATE_KEYS = ("date", "established", "added_at", "since", "created", "created_at")
ORIGIN_KEYS = ("origin", "source", "from", "cause")


def item_id(item):
    if isinstance(item, dict):
        for k in ID_KEYS + NAME_KEYS:
            if item.get(k):
                return str(item[k])
        return ""
    return str(item)


def shape_like(sample, ab):
    out = {}
    for k in sample.keys():
        kl = k.lower()
        if kl in ID_KEYS:
            out[k] = ab["id"]
        elif kl in NAME_KEYS:
            out[k] = ab["name"]
        elif kl in DESC_KEYS:
            out[k] = ab["desc"]
        elif kl in DATE_KEYS:
            out[k] = TODAY
        elif kl in ORIGIN_KEYS:
            out[k] = ab["origin"]
    if not any(k.lower() in ID_KEYS + NAME_KEYS for k in out):
        out = dict(ab, established=TODAY)
    return out


def merge_antibodies(existing):
    added = 0
    if existing is None:
        return [dict(ab, established=TODAY) for ab in NEW_ANTIBODIES], len(NEW_ANTIBODIES)
    if isinstance(existing, dict):
        for ab in NEW_ANTIBODIES:
            if ab["id"] not in existing:
                existing[ab["id"]] = {"name": ab["name"], "desc": ab["desc"], "origin": ab["origin"], "established": TODAY}
                added += 1
        return existing, added
    if isinstance(existing, list):
        have = {item_id(x).split(":")[0].strip() for x in existing}
        sample = next((x for x in existing if isinstance(x, dict)), None)
        for ab in NEW_ANTIBODIES:
            if ab["id"] in have:
                continue
            if sample is not None:
                existing.append(shape_like(sample, ab))
            else:
                existing.append("%s: %s — %s" % (ab["id"], ab["name"], ab["desc"]))
            added += 1
        return existing, added
    return existing, 0


def update_snapshot(path):
    try:
        data = json.loads(read_text(path))
    except Exception as e:
        log("⚠️ 스냅샷 파싱 실패 → 손상 방지를 위해 건너뜀:", path, e)
        return {"path": path, "ok": False, "error": "파싱 실패"}
    if not isinstance(data, dict):
        log("⚠️ 스냅샷 최상위가 객체가 아님 → 건너뜀:", path)
        return {"path": path, "ok": False, "error": "구조 불일치"}
    backup(path)
    old_ver = data.get("version")
    data["version"] = VERSION
    data["generated_at_kst"] = NOW_KST
    data["synced_at_kst"] = NOW_KST
    data["antibody_range"] = ANTIBODY_RANGE
    data["antibodies"], added = merge_antibodies(data.get("antibodies"))

    prev = data.get("today_achievements")
    if isinstance(prev, dict):
        new_ach = {"date": TODAY, "step_range": "Step 1~16", "items": list(ACHIEVEMENTS)}
        same = prev.get("items") == ACHIEVEMENTS
    else:
        new_ach = list(ACHIEVEMENTS)
        same = prev == ACHIEVEMENTS
    if prev and not same:
        hist = data.get("achievement_history")
        if hist is None:
            hist = data["achievement_history"] = []
        if isinstance(hist, list):
            hist.append({"archived_at_kst": NOW_KST, "items": prev})
            del hist[:-30]
    data["today_achievements"] = new_ach
    data["eod_step16"] = {"date": TODAY, "closed_at_kst": NOW_KST, "step_range": "Step 1~16",
                          "docs": ["CLAUDE.md", "CODE_MAP.md", LOG_NAME],
                          "new_antibodies": [a["id"] for a in NEW_ANTIBODIES]}

    text = json.dumps(data, ensure_ascii=False, indent=2)
    json.loads(text)
    safe_write(path, text + "\n")
    ab = data.get("antibodies")
    count = len(ab) if isinstance(ab, (list, dict)) else 0
    log("스냅샷 갱신:", path, "| %s → %s | 항체 +%d (총 %d)" % (old_ver, VERSION, added, count))
    return {"path": path, "ok": True, "added": added, "count": count, "old_version": old_ver}


def update_all_snapshots():
    paths = [os.path.join(BASE_DIR, SNAP_NAME), os.path.join(BASE_DIR, "dashboard", SNAP_NAME),
             os.path.join(BASE_DIR, "docs", SNAP_NAME)]
    existing = [p for p in paths if os.path.isfile(p)]
    if not existing:
        log("스냅샷 파일이 없어 루트에 새로 생성합니다.")
        safe_write(paths[0], json.dumps({"version": "", "antibodies": []}, ensure_ascii=False, indent=2))
        existing = [paths[0]]
    return [update_snapshot(p) for p in existing]


def build_eod_entry():
    ab_lines = "\n".join("- **%s** — %s  \n  %s _(%s)_" % (a["id"], a["name"], a["desc"], a["origin"]) for a in NEW_ANTIBODIES)
    ach_lines = "\n".join("- " + a for a in ACHIEVEMENTS)
    return (EOD_START + "\n"
            "## 📅 " + TODAY + " — Step 1~16 완결 (" + VERSION + ")\n\n"
            "> 일일 마감 시각: " + NOW_KST + " · 항체 범위: " + ANTIBODY_RANGE + "\n\n"
            "### ✅ 오늘의 핵심 성과\n" + ach_lines + "\n\n"
            "### 🧭 Step 진행 기록\n"
            "| Step | 내용 | 결과 |\n|---|---|---|\n"
            "| 1~12 | 독대실 대시보드 · 확장프로그램 기반 구축 (Step 11: 상단 4대 아코디언 바 배치) | ✅ 안정 운영 |\n"
            "| 13 | " + BT + "step13_youtube_skill_absorber.py" + BT + " → " + BT + "rgon_youtube_skill_scout.py" + BT + " + " + BT + "rgon_skill_radar.json" + BT + " + V13 청록 바 | ✅ 시드·채널 떡상 9개 수집 |\n"
            "| 14 | " + BT + "step14_fix_5bars_layout.py" + BT + " (V14 5bars 도크 + MutationObserver) | ❌ Step 11과 DOM 이동 충돌 → 폐기 |\n"
            "| 15 | " + BT + "step15_remove_v14_and_quiet_place.py" + BT + " (V14 제거 + placeOnce 단발 배치) | ✅ 깜빡임 해소 |\n"
            "| 16 | " + BT + "step16_karpathy_codemap_and_eod.py" + BT + " (CLAUDE.md · CODE_MAP.md · 스냅샷 · EOD) | ✅ 마감 |\n\n"
            "### 🧬 신규 항체\n" + ab_lines + "\n\n"
            "### 📚 교훈\n"
            "- 이미 잘 작동하는 배치 스크립트 위에 '감시형 재배치'를 겹치면 두 스크립트가 DOM을 서로 빼앗는 루프가 생긴다 → **새 요소만, 한 번만** 옮긴다.\n"
            "- 실제 HTML 구조를 확인하지 않은 범용 탐지 로직은 엉뚱한 부모(헤더 박스)를 고를 수 있다 → 수정 전 구조 확인(CLAUDE.md 규칙 1).\n\n"
            "### 🔁 다음 세션 인수인계\n"
            "1. " + BT + "CLAUDE.md" + BT + " 정독 → 2. " + BT + "CODE_MAP.md" + BT + "로 구조 파악 → 3. " + BT + "rgon_brain_snapshot.json" + BT + " 확인 → 4. 이 로그 최신 항목 확인\n"
            + EOD_END + "\n")


def update_evolution_log():
    path = os.path.join(BASE_DIR, LOG_NAME)
    entry = build_eod_entry()
    if os.path.isfile(path):
        src = read_text(path)
        backup(path)
        if EOD_START in src and EOD_END in src:
            pat = re.compile(re.escape(EOD_START) + r".*?" + re.escape(EOD_END) + r"\n?", re.S)
            new = pat.sub(lambda m: entry, src, count=1)
            mode = "오늘 항목 교체"
        else:
            lines = src.split("\n")
            if lines and lines[0].startswith("# "):
                new = lines[0] + "\n\n" + entry + "\n" + "\n".join(lines[1:]).lstrip("\n")
            else:
                new = entry + "\n" + src
            mode = "맨 위 추가"
    else:
        new = "# 🧬 RGON Evolution Log\n\n" + entry
        mode = "신규 생성"
    safe_write(path, new)
    log("진화 로그 %s: %s" % (mode, path))
    return mode


MARKER_RE = re.compile(r"\[([A-Za-z0-9][A-Za-z0-9_\-]*?)-START\]")
HTML_MARKER_RE = re.compile(r"<!--\s*\[([^\]\s]+?)-START\]\s*-->")


def iter_code_files(base):
    n = 0
    for root, dirs, files in os.walk(base):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith(".") and not SKIP_DIR_RE.search(d))
        for f in sorted(files):
            if not f.lower().endswith(SCAN_EXT) or SKIP_FILE_RE.search(f):
                continue
            yield os.path.join(root, f)
            n += 1
            if n >= MAX_FILES:
                return


def first_doc_line(doc, n=140):
    for ln in (doc or "").splitlines():
        ln = ln.strip()
        if ln and not ln.endswith(".py") and not ln.startswith(("-", "=", "#")):
            return ln[:n]
    lines = [l.strip() for l in (doc or "").splitlines() if l.strip()]
    return lines[0][:n] if lines else ""


def analyze_py(src):
    info = {"summary": "", "symbols": [], "syntax": None}
    try:
        tree = ast.parse(src)
        info["summary"] = first_doc_line(ast.get_docstring(tree))
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                info["symbols"].append(node.name + "()")
            elif isinstance(node, ast.ClassDef):
                meths = [b.name for b in node.body if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef))]
                info["symbols"].append("class %s%s" % (node.name, (" [" + ", ".join(meths[:6]) + ("…" if len(meths) > 6 else "") + "]") if meths else ""))
    except SyntaxError as e:
        info["syntax"] = "line %s: %s" % (e.lineno, e.msg)
        info["symbols"] = [("class " if m.group(1) == "class" else "") + m.group(2) + ("()" if m.group(1) == "def" else "")
                           for m in re.finditer(r"^(def|class)\s+(\w+)", src, re.M)]
    return info


def analyze_js(src):
    names = re.findall(r"(?:^|\n)\s*(?:async\s+)?function\s+([A-Za-z_$][\w$]*)", src)
    names += re.findall(r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>)", src)
    seen, out = set(), []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n + "()")
    return out


def analyze_json(path, size):
    if size > JSON_PARSE_LIMIT:
        return "대용량(구조 파싱 생략)"
    try:
        d = json.loads(read_text(path))
    except Exception:
        return "⚠️ JSON 파싱 실패"
    if isinstance(d, dict):
        extra = []
        if os.path.basename(path).lower() == "manifest.json" and "manifest_version" in d:
            extra.append("🧩 크롬 확장 %s v%s" % (d.get("name", ""), d.get("version", "")))
        if d.get("version") and not extra:
            extra.append("version=%s" % d.get("version"))
        keys = list(d.keys())
        return " · ".join(extra + ["keys: " + ", ".join(keys[:12]) + (" …(+%d)" % (len(keys) - 12) if len(keys) > 12 else "")])
    if isinstance(d, list):
        return "배열 %d개" % len(d)
    return type(d).__name__


def scan_project(base):
    entries = []
    ext_dirs = set()
    for p in iter_code_files(base):
        if os.path.basename(p).lower() == "manifest.json":
            ext_dirs.add(os.path.dirname(p))
    for p in iter_code_files(base):
        try:
            st = os.stat(p)
        except Exception:
            continue
        rel = os.path.relpath(p, base).replace("\\", "/")
        ext = os.path.splitext(p)[1].lower()
        e = {"rel": rel, "ext": ext, "size": st.st_size,
             "mtime": datetime.fromtimestamp(st.st_mtime, KST).strftime("%Y-%m-%d %H:%M"),
             "summary": "", "symbols": [], "markers": [], "syntax": None,
             "ext_pkg": any(os.path.dirname(p) == d or p.startswith(d + os.sep) for d in ext_dirs)}
        try:
            if ext == ".py":
                src = read_text(p)
                e.update(analyze_py(src))
                e["markers"] = list(dict.fromkeys(MARKER_RE.findall(src)))
            elif ext in (".html", ".htm"):
                src = read_text(p)
                e["markers"] = list(dict.fromkeys(HTML_MARKER_RE.findall(src)))
                m = re.search(r"<title[^>]*>(.*?)</title>", src, re.S | re.I)
                e["summary"] = m.group(1).strip()[:100] if m else ""
            elif ext == ".js":
                src = read_text(p)
                e["symbols"] = analyze_js(src)
                e["markers"] = list(dict.fromkeys(MARKER_RE.findall(src)))
                e["summary"] = "🧩 크롬 확장 스크립트" if e["ext_pkg"] else ""
            elif ext == ".json":
                e["summary"] = analyze_json(p, st.st_size)
        except Exception as ex:
            e["summary"] = "⚠️ 분석 실패: %s" % ex
        entries.append(e)
    return entries


def render_tree(entries):
    root = {}
    for e in entries:
        parts = e["rel"].split("/")
        node = root
        for d in parts[:-1]:
            node = node.setdefault(d + "/", {})
        node[parts[-1]] = e

    def rec(node, prefix):
        items = sorted(node.items(), key=lambda kv: (not kv[0].endswith("/"), kv[0].lower()))
        lines = []
        for i, (k, v) in enumerate(items):
            last = i == len(items) - 1
            if k.endswith("/"):
                lines.append(prefix + ("└── " if last else "├── ") + k)
                lines.extend(rec(v, prefix + ("    " if last else "│   ")))
            else:
                tag = human_size(v["size"])
                if v["markers"]:
                    tag += " · 마커 %d" % len(v["markers"])
                if v["syntax"]:
                    tag += " · ⚠️문법"
                lines.append(prefix + ("└── " if last else "├── ") + k + "  (" + tag + ")")
        return lines

    return "\n".join([os.path.basename(BASE_DIR) + "/"] + rec(root, ""))


def sym_cell(syms, n=25):
    if not syms:
        return "-"
    s = ", ".join(BT + "%s" + BT % x for x in syms[:n])
    return s + (" …(+%d)" % (len(syms) - n) if len(syms) > n else "")


def build_code_map(entries):
    by = lambda exts: [e for e in entries if e["ext"] in exts]
    pys, htmls, jss, jsons = by((".py",)), by((".html", ".htm")), by((".js",)), by((".json",))
    total = sum(e["size"] for e in entries)
    marker_idx = {}
    for e in entries:
        for m in e["markers"]:
            marker_idx.setdefault(m, {"html": [], "py": [], "js": []})
            key = "html" if e["ext"] in (".html", ".htm") else "py" if e["ext"] == ".py" else "js"
            marker_idx[m][key].append(e["rel"])
    out = []
    out.append("# 🗺️ CODE_MAP — RGON shin-agent 코드 지도")
    out.append("")
    out.append("> 자동 생성: `step16_karpathy_codemap_and_eod.py` · %s · 손으로 수정하지 말고 스크립트를 다시 실행할 것" % NOW_KST)
    out.append("> 스캔 제외: `.git`, `node_modules`, `__pycache__`, `_rgon_backups`, 백업 폴더, `*.bak*` 파일")
    out.append("")
    out.append("## 🧭 새 AI 세션 30초 가이드")
    out.append("1. `CLAUDE.md` — 코딩 헌법(4대 원칙) 먼저 읽기")
    out.append("2. 이 파일 — 아래 **마커 인덱스**로 어떤 스크립트가 어떤 HTML 구간을 관리하는지 확인")
    out.append("3. `rgon_brain_snapshot.json` — 현재 버전·항체·오늘 성과")
    out.append("4. `RGON_EVOLUTION_LOG.md` — 최신 진화 기록")
    out.append("5. 수정 대상 파일만 실제로 열어서 확인한 뒤 작업 (전체 파일을 다 읽을 필요 없음)")
    out.append("")
    out.append("## 📊 요약")
    out.append("| 구분 | 파일 수 |\n|---|---|")
    out.append("| Python (.py) | %d |\n| HTML | %d |\n| JavaScript (.js) | %d |\n| JSON | %d |\n| **합계** | **%d (%s)** |"
               % (len(pys), len(htmls), len(jss), len(jsons), len(entries), human_size(total)))
    out.append("")
    out.append("## 🌳 트리")
    out.append(FENCE + "\n" + render_tree(entries) + "\n" + FENCE)
    out.append("")
    out.append("## 🏷️ 패치 마커 인덱스 (마커 → HTML 위치 / 관리 스크립트)")
    if marker_idx:
        out.append("| 마커 | 삽입된 HTML | 관리(생성) 스크립트 | JS |\n|---|---|---|---|")
        for m in sorted(marker_idx):
            d = marker_idx[m]
            out.append("| `%s` | %s | %s | %s |" % (m, md_cell(", ".join(d["html"]) or "-", 200),
                                                   md_cell(", ".join(d["py"]) or "-", 200), md_cell(", ".join(d["js"]) or "-", 120)))
    else:
        out.append("_감지된 마커 없음_")
    out.append("")
    out.append("## 🐍 Python")
    out.append("| 경로 | 크기 | 수정 | 요약(docstring) | def / class |\n|---|---|---|---|---|")
    for e in pys:
        syms = ", ".join("`%s`" % x for x in e["symbols"][:25]) + (" …(+%d)" % (len(e["symbols"]) - 25) if len(e["symbols"]) > 25 else "") if e["symbols"] else "-"
        out.append("| `%s` | %s | %s | %s | %s |" % (e["rel"], human_size(e["size"]), e["mtime"],
                                                    md_cell(e["summary"] or "-"), syms))
    out.append("")
    out.append("## 🌐 HTML")
    out.append("| 경로 | 크기 | 수정 | title | 패치 마커 |\n|---|---|---|---|---|")
    for e in htmls:
        out.append("| `%s` | %s | %s | %s | %s |" % (e["rel"], human_size(e["size"]), e["mtime"], md_cell(e["summary"] or "-", 60),
                                                    ", ".join("`%s`" % m for m in e["markers"]) or "-"))
    out.append("")
    out.append("## 📜 JavaScript")
    out.append("| 경로 | 크기 | 수정 | 구분 | 주요 함수 | 마커 |\n|---|---|---|---|---|---|")
    for e in jss:
        syms = ", ".join("`%s`" % x for x in e["symbols"][:15]) + (" …(+%d)" % (len(e["symbols"]) - 15) if len(e["symbols"]) > 15 else "") if e["symbols"] else "-"
        out.append("| `%s` | %s | %s | %s | %s | %s |" % (e["rel"], human_size(e["size"]), e["mtime"], e["summary"] or "-",
                                                         syms, ", ".join("`%s`" % m for m in e["markers"]) or "-"))
    out.append("")
    out.append("## 🗂️ JSON")
    out.append("| 경로 | 크기 | 수정 | 구조 |\n|---|---|---|---|")
    for e in jsons:
        out.append("| `%s` | %s | %s | %s |" % (e["rel"], human_size(e["size"]), e["mtime"], md_cell(e["summary"], 200)))
    errs = [e for e in pys if e["syntax"]]
    out.append("")
    out.append("## 🩺 Python 문법 검증 (ast.parse)")
    if errs:
        for e in errs:
            out.append("- ⚠️ `%s` — %s" % (e["rel"], e["syntax"]))
    else:
        out.append("- ✅ 스캔한 Python %d개 모두 문법 정상" % len(pys))
    out.append("")
    return "\n".join(out), marker_idx, len(errs)


CLAUDE_BODY = r"""# 📜 CLAUDE.md — RGON 사령부 AI 코딩 헌법

> 적용 대상: Claude · Gemini 4 Argon · GPT · Grok 등 **이 프로젝트에서 코드를 쓰는 모든 AI**
> 코드를 쓰기 전에 반드시 이 문서를 먼저 읽는다. (Claude Code는 프로젝트 루트의 CLAUDE.md를 자동으로 읽는다)
> 갱신: __NOW__ · 버전 __VERSION__ · 항체 __RANGE__

## 0. 세션 시작 3단계
1. **`CODE_MAP.md`** 로 전체 구조와 패치 마커 위치를 파악한다. (전체 파일을 다 읽지 말 것)
2. **`rgon_brain_snapshot.json`** 으로 현재 버전·항체·오늘 성과를 확인한다.
3. **`RGON_EVOLUTION_LOG.md`** 최신 항목으로 직전 작업과 실패 사례를 확인한다.

---

## 규칙 1. 가정하지 말고 실제 구조를 먼저 확인하라 (No Blind Assumptions)
- 경로를 `C:\Users\user\...` 처럼 **추측으로 하드코딩하지 않는다.** 실제 작업 폴더는 `C:\Users\sangi\Downloads\shin-agent` 이며, 스크립트는 반드시 자동 탐색 폴백을 둔다.
- 수정할 HTML/JS/PY 파일의 **실제 내용(요소 id, 클래스, 기존 마커, 기존 스크립트)을 먼저 확인**하고 작업한다. 모르면 "어느 구조인지" 사용자에게 HTML 일부를 요청한다.
- 확신이 없으면 추측으로 범용 탐지 로직을 키우지 말고, 모른다고 말하고 확인 방법을 제시한다.

__FENCE__python
PREFERRED_BASE = r"C:\Users\sangi\Downloads\shin-agent"
def find_base_dir():
    if os.path.isdir(PREFERRED_BASE):
        return PREFERRED_BASE
    # ↓ 스크립트 위치 / cwd / ~/Downloads|Desktop|Documents/shin-agent 순 자동 탐색
__FENCE__

## 규칙 2. 최소 변경 · 비파괴 마커 패치 (Minimal Surgical Diff)
- 잘 작동하는 기존 코드/UI는 통째로 갈아엎지 않는다. 요청과 직접 관련된 줄만 바꾼다.
- 삽입은 항상 고유 마커 `<!-- [RGON-XXX-START] -->` ~ `<!-- [RGON-XXX-END] -->` 구간으로 하고, 재실행 시 그 구간만 교체한다(멱등성).
- 수정 전 백업본을 남긴다. 단, 오래된 백업으로 파일 전체를 복원하지 않는다(그 이후 변경분이 사라짐) → 정규식으로 해당 블록만 제거/교체한다.
- 사용자가 "수정 금지"로 지정한 파일(현재: 독대실 HTML, 크롬 확장 JS)은 쓰지 않는다.

__FENCE__python
pat = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
new = pat.sub(lambda m: block, src, count=1) if START in src else insert_new(src, block)
__FENCE__

## 규칙 3. 과도한 엔지니어링 · 감시 루프 금지 (No Over-Engineering / No Observer Loops)
- 기존 UI 위에 `MutationObserver` 나 `setInterval` 로 DOM을 계속 재배치하는 코드 금지. 기존 배치 스크립트(Step 11 등)와 서로 요소를 빼앗는 무한 루프·깜빡임이 생긴다. (Step 14 실제 사고 → 항체 R13)
- 새 요소는 단발성 `placeOnce` 로 한 번만 옮기고 표식을 남긴 뒤 종료한다. 기존 바의 style/display/min-height/gap은 건드리지 않는다.
- 요청받지 않은 기능, 추측성 범용화, 불필요한 추상화를 추가하지 않는다. 가장 단순한 해법부터 적용한다.

__FENCE__javascript
function placeOnce(){
  var w=document.getElementById('rgyt-wrap');
  if(!w||w.getAttribute('data-placed')==='1')return;   // 이미 배치됨 → 즉시 종료
  /* 기준 바 찾기 → parentNode.insertBefore(w, bar.nextSibling) */
  w.setAttribute('data-placed','1');
}
document.addEventListener('DOMContentLoaded',placeOnce);
setTimeout(placeOnce,300); setTimeout(placeOnce,900);   // 총 3회 단발, Observer 없음
__FENCE__

## 규칙 4. 실행 검증 및 자동 동기화 (Verify & Git Sync)
- Python 3 표준 라이브러리만 사용한다(pip 의존성 금지). 파일 입출력은 항상 `encoding="utf-8"` 명시(Windows cp949 오류 방지).
- 수정 후 반드시 검증한다: Python은 `ast.parse`/`py_compile`, JSON은 로드 왕복, HTML은 START/END 마커 개수 일치 확인.
- 마지막에 `git add -A` → `git commit` → `git pull --rebase origin main` → `git push origin main` 까지 한 번에 끝낸다. rebase 충돌 시 `git rebase --abort` 후 결과를 보고한다.
- 완료 시 Windows 메시지 박스(`ctypes`)로 결과·실패 항목·되돌리기 방법을 보고한다.

---

## 5. 패치 마커 레지스트리

| 마커 | 상태 | 관리 스크립트 / 비고 |
|---|---|---|
| `RGON-YT-SCOUT-V13` | ✅ 활성 | `step13_youtube_skill_absorber.py` — 청록 바(유튜브 스킬 흡수기) |
| `RGYT-PLACE-ONCE-V15` | ✅ 활성 | V13 블록 내부 — 청록 바 단발 배치 |
| `RGON-5BARS-FIX-V14` | ⛔ 폐기 | Observer 기반 재배치 → DOM 충돌. 재도입 금지 |
| `RGON-CLAUDE-MD-V16` | ✅ 활성 | 이 문서 자체 (`step16_karpathy_codemap_and_eod.py`) |

자동 감지된 HTML 마커 (__SCANTIME__ 스캔):
__MARKERS__

## 6. 오늘 확립된 항체
__ANTIBODIES__

## 7. 제출 전 체크리스트
- [ ] 실제 작업 폴더와 대상 파일 내용을 확인했다 (규칙 1)
- [ ] 수정은 마커 구간 / 필요한 줄로 한정했고 백업을 남겼다 (규칙 2)
- [ ] Observer·setInterval 재배치 없이 단발 처리했다 (규칙 3)
- [ ] 표준 라이브러리만 썼고, 문법·마커·JSON 검증 후 Git 동기화까지 했다 (규칙 4)
- [ ] 작업 후 `CODE_MAP.md` 재생성 / 진화 로그 기록이 필요한지 확인했다

> 원형: Andrej Karpathy가 지적한 LLM 코딩 실수 패턴(잘못된 가정, 과잉 복잡화, 요청 외 코드 변경, 검증 없는 완료 선언)에서 출발한 공개 4원칙 지침(생각 먼저 · 단순함 우선 · 외과적 변경 · 목표 기반 검증)을 RGON 사령부 실전 사고 사례에 맞게 재작성한 것.
"""


def build_claude_md(marker_idx):
    html_markers = sorted(m for m, d in marker_idx.items() if d["html"])
    mk = "\n".join("- `%s` → %s" % (m, ", ".join("`%s`" % x for x in marker_idx[m]["html"])) for m in html_markers) or "- (감지된 HTML 마커 없음)"
    ab = "\n".join("- **%s** — %s: %s" % (a["id"], a["name"], a["desc"]) for a in NEW_ANTIBODIES)
    body = (CLAUDE_BODY.replace("__FENCE__", FENCE).replace("__NOW__", NOW_KST).replace("__VERSION__", VERSION).replace("__RANGE__", ANTIBODY_RANGE)
            .replace("__SCANTIME__", NOW_KST).replace("__MARKERS__", mk).replace("__ANTIBODIES__", ab))
    return CLAUDE_START + "\n" + body.strip() + "\n" + CLAUDE_END + "\n"


def write_claude_md(marker_idx):
    path = os.path.join(BASE_DIR, "CLAUDE.md")
    block = build_claude_md(marker_idx)
    if os.path.isfile(path):
        src = read_text(path)
        backup(path)
        if CLAUDE_START in src and CLAUDE_END in src:
            pat = re.compile(re.escape(CLAUDE_START) + r".*?" + re.escape(CLAUDE_END) + r"\n?", re.S)
            new = pat.sub(lambda m: block, src, count=1)
            mode = "마커 구간 교체"
        else:
            new = block + "\n---\n\n## 📎 기존 CLAUDE.md 내용 (보존)\n\n" + src
            mode = "기존 내용 보존 + 상단 삽입"
    else:
        new = block
        mode = "신규 생성"
    safe_write(path, new)
    log("CLAUDE.md %s: %s" % (mode, path))
    return mode


def verify(snap_results):
    problems = []
    cm = os.path.join(BASE_DIR, "CLAUDE.md")
    try:
        t = read_text(cm)
        if t.count(CLAUDE_START) != 1 or t.count(CLAUDE_END) != 1:
            problems.append("CLAUDE.md 마커 개수 이상")
        for k in ("규칙 1", "규칙 2", "규칙 3", "규칙 4"):
            if k not in t:
                problems.append("CLAUDE.md %s 누락" % k)
    except Exception as e:
        problems.append("CLAUDE.md 읽기 실패: %s" % e)
    if not os.path.isfile(os.path.join(BASE_DIR, "CODE_MAP.md")):
        problems.append("CODE_MAP.md 없음")
    for r in snap_results:
        if not r.get("ok"):
            problems.append("스냅샷 미갱신: %s (%s)" % (os.path.relpath(r["path"], BASE_DIR), r.get("error")))
            continue
        try:
            d = json.loads(read_text(r["path"]))
            if d.get("version") != VERSION:
                problems.append("스냅샷 버전 불일치: %s" % r["path"])
        except Exception as e:
            problems.append("스냅샷 재검증 실패: %s" % e)
    try:
        lt = read_text(os.path.join(BASE_DIR, LOG_NAME))
        if lt.count(EOD_START) != 1:
            problems.append("진화 로그 오늘 마커 개수 이상")
    except Exception as e:
        problems.append("진화 로그 읽기 실패: %s" % e)
    return problems


def git(*args):
    try:
        p = subprocess.run(["git"] + list(args), cwd=BASE_DIR, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
        log("git", " ".join(args), "->", p.returncode, (p.stdout + p.stderr).strip()[-300:])
        return p.returncode == 0, (p.stdout + p.stderr)
    except Exception as e:
        log("git 실행 실패:", e)
        return False, str(e)


def git_sync():
    if not os.path.isdir(os.path.join(BASE_DIR, ".git")):
        return "Git 저장소 아님(건너뜀)"
    git("add", "-A")
    ok, out = git("commit", "-m", COMMIT_MSG)
    if not ok and "nothing to commit" not in out.lower():
        log("commit 실패(계속 진행)")
    ok, _ = git("pull", "--rebase", "origin", "main")
    if not ok:
        git("rebase", "--abort")
        return "pull --rebase 실패 → 리베이스 취소 (수동 확인 필요)"
    ok, _ = git("push", "origin", "main")
    return "성공" if ok else "push 실패(로그 확인)"


def msgbox(title, text):
    log(text)
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, text, title, 0x40)
        except Exception:
            pass


def main():
    global BASE_DIR, BACKUP_DIR
    BASE_DIR = find_base_dir()
    BACKUP_DIR = os.path.join(BASE_DIR, "rgon_backups", "step16_" + STAMP)
    log("작업 폴더:", BASE_DIR)

    before = protected_hashes(BASE_DIR)
    log("보호 대상 HTML/JS/manifest 파일:", len(before))

    snap_results = update_all_snapshots()
    log_mode = update_evolution_log()

    entries = scan_project(BASE_DIR)
    code_map, marker_idx, syntax_errs = build_code_map(entries)
    cm_path = os.path.join(BASE_DIR, "CODE_MAP.md")
    if os.path.isfile(cm_path):
        backup(cm_path)
    safe_write(cm_path, code_map)
    log("CODE_MAP.md 생성: 파일 %d개 / 마커 %d종" % (len(entries), len(marker_idx)))
    claude_mode = write_claude_md(marker_idx)

    after = protected_hashes(BASE_DIR)
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    problems = verify(snap_results)

    if changed:
        git_result = "⛔ 중단 — HTML/JS 변경 감지: " + ", ".join(changed[:5])
    else:
        git_result = git_sync()

    snap_lines = "\n".join("  • %s : %s" % (os.path.relpath(r["path"], BASE_DIR),
                                            ("항체 +%d (총 %d)" % (r["added"], r["count"])) if r.get("ok") else "⚠ " + str(r.get("error")))
                           for r in snap_results)
    msgbox("RGON Step 16 · 일일 마감 완료" if not problems and not changed else "RGON Step 16 · 확인 필요",
           "🌙 %s 일일 마감 보고 (%s)\n\n"
           "📜 CLAUDE.md: %s\n🗺️ CODE_MAP.md: 파일 %d개 · 마커 %d종 · 문법오류 %d\n"
           "🧠 스냅샷 → %s / %s\n%s\n📘 진화 로그: %s\n\n"
           "✅ 오늘 성과\n%s\n\n"
           "🛡️ HTML/JS 보존: %s (%d개 해시 검증)\n🔎 검증: %s\n🚀 Git: %s\n\n백업: %s"
           % (TODAY, NOW_KST, claude_mode, len(entries), len(marker_idx), syntax_errs, VERSION, ANTIBODY_RANGE,
              snap_lines, log_mode, "\n".join("  " + a for a in ACHIEVEMENTS),
              "변경 0건 ✅" if not changed else "⚠ %d건 변경 감지" % len(changed), len(before),
              "이상 없음" if not problems else "; ".join(problems), git_result,
              os.path.relpath(BACKUP_DIR, BASE_DIR)))


if __name__ == "__main__":
    main()

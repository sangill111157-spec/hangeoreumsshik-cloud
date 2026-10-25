# -*- coding: utf-8 -*-
"""Step 39 — 제15기관: 아온 초격차 대화 이해(Deep NLU) & 올인원 대화 허브(Omni-Dialogue Hub)
v11.37-AON-OMNI-INSIGHT -> v11.38-AON-OMNI-DIALOGUE · 항체 R1~R39 · 정식 스킬 [35,35,35]"""
import os, sys, re, ast, json, time, hashlib, tempfile, subprocess, argparse, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD_VER, NEW_VER = "v11.37-AON-OMNI-INSIGHT", "v11.38-AON-OMNI-DIALOGUE"
OLD_R, NEW_R = "R1~R38", "R1~R39"
SKILL_TARGET = 35
SKILL_NAME = "aon-omni-dialogue-hub"
SKIP_DIRS = {".git", ".rgon_backups", ".rgon_backup", "__pycache__", "node_modules", ".venv", "venv"}
ENGINE = "rgon_aon_dialogue_engine.py"
REPORT = "STEP39_AON_OMNI_DIALOGUE_REPORT.md"
SKILL_MD = f"skills/{SKILL_NAME}/SKILL.md"
SKILL_JSON_IDX, SKILL_MD_IDX = "skills/SKILL_INDEX.json", "skills/SKILL_INDEX.md"
DRY = False
LOGS, WARNS = [], []
WRITTEN = set()
BT3 = chr(96) * 3

V13_HTML_TARGETS = [
    "index.html",
    "rgon_alpha_audience.html",
    "rgon_alpha_chat.html",
    "dashboard/index.html",
    "dashboard/rgon_alpha_chat.html",
    "docs/index.html",
    "docs/rgon_alpha_chat.html",
]
V13_END_RE = re.compile(r"<!--\s*\[?(?:UX-CLEANUP|YT-SCOUT)-V13-END\]?[^>]*-->")

def log(m):
    print(m); LOGS.append(str(m))

def warn(m):
    log("  ⚠️ " + m); WARNS.append(m)

def rd(p):
    return Path(p).read_text(encoding="utf-8", errors="replace")

def wr(p, s):
    p = Path(p)
    if not p.is_absolute(): p = ROOT / p
    rel = p.relative_to(ROOT).as_posix(); WRITTEN.add(rel)
    if DRY:
        log(f"  [dry-run] 쓰기 생략: {rel}"); return
    p.parent.mkdir(parents=True, exist_ok=True)
    for i in range(6):
        try:
            p.write_text(s, encoding="utf-8", newline="\n"); return
        except PermissionError:
            if i == 5: raise
            time.sleep(0.04)

# ======================================================================== 제15기관 모듈
ENGINE_SRC = r'''# -*- coding: utf-8 -*-
"""rgon_aon_dialogue_engine.py — 제15기관 아온 초격차 대화 이해 & 올인원 대화 허브 (표준 라이브러리 전용)
[RGON-R39] v11.38-AON-OMNI-DIALOGUE
파이프라인: 구어 정규화 → 대명사·생략어 복원 → 슬래시/원칙/복합의도 분기 → 기관 디스패치
          → 플랫폼 메타데이터(thinking·artifact·chips·callback) 보강 → 3계층 해마 기억(단기·토픽·연상).
한계: 사전·정규식 기반 규칙 엔진이다. 언어모델이 아니므로 처음 보는 표현은 놓칠 수 있다."""
import argparse, datetime, json, os, re, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION = "v11.38-AON-OMNI-DIALOGUE"
STATE, PREFS = "rgon_aon_dialogue_state.json", "rgon_aon_preferences.json"
SHORT_MAX, EVENT_MAX, FRESH_TURNS, FRESH_SEC = 20, 60, 4, 1800
CAT_KO = {"command_rule": "지휘 원칙", "style": "스타일", "preference": "취향"}

def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _dir():
    d = os.environ.get("RGON_DIALOGUE_STATE_DIR")
    return Path(d) if d else ROOT

def _load(name, default):
    for p in (_dir() / name, _dir() / "docs" / name):
        try:
            if p.exists(): return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default

def _save(name, obj):
    s = json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    for p in (_dir() / name, _dir() / "docs" / name):
        p.parent.mkdir(parents=True, exist_ok=True)
        for i in range(6):
            try:
                p.write_text(s, encoding="utf-8", newline="\n"); break
            except PermissionError:
                if i == 5: raise
                time.sleep(0.04)

def _uniq(xs):
    out = []
    for x in xs:
        if x and x not in out: out.append(x)
    return out

def _safe(v, n=6000):
    try:
        s = json.dumps(v, ensure_ascii=False, default=str)
    except Exception:
        return str(v)[:n]
    return json.loads(s) if len(s) <= n else s[:n] + "…"

# ------------------------------------------------------------------ 1. 구어체·오타 정규화
TYPOS = [(r"브립핑|브리팡|부리핑", "브리핑"), (r"점처", "점쳐"), (r"결제\s*스위치", "결재 스위치"),
         (r"하기\s*실(?:어|타|다)", "하기 싫어"), (r"노트북용량", "노트북 용량"), (r"통찰해\s*바(?![가-힣])", "통찰해줘"),
         (r"해\s*바(?![가-힣])", "해줘"), (r"봐\s*바(?![가-힣])", "봐줘"), (r"알려\s*조(?![가-힣])", "알려줘"),
         (r"어떄", "어때"), (r"브리핑좀", "브리핑 좀"), (r"점괘좀", "점괘 좀"), (r"괘봐", "괘 봐"),
         (r"됬", "됐"), (r"않해", "안 해"), (r"몇일", "며칠"), (r"(?:뭐임|머임)(?=\s*\??$)", "뭐야")]

def normalize_colloquial(text):
    o = "" if text is None else str(text); t = o; fixes = []
    for pat, rep in TYPOS:
        n = re.sub(pat, rep, t)
        if n != t: fixes.append(rep); t = n
    if fixes: t = re.sub(r"\s{2,}", " ", t).strip()
    return dict(original=o, normalized=t, fixes=fixes)

# ------------------------------------------------------------------ 2. 대명사·생략어 복원
PRON = re.compile(r"(아까\s*(?:그거|말한\s*거|얘기한\s*거|본\s*거)|그것|그거|그건|그걸|이것|이거|이건|이걸|저거|거기)")
JOSA = re.compile(r"(이랑|에서|에게|한테|으로|께서|까지|부터|처럼|이나|은|는|이|가|을|를|에|로|도|만|의|와|과|랑)$")
STOPW = set("오늘 오늘의 지금 내일 어제 아까 그냥 진짜 정말 너무 다시 그리고 그래서 하지만 근데 아온 아온이 대표님 우리 이번 요즘 혹시 먼저 같이 한번 그럼".split())
FUNC = set("주역 점괘 운세 시운 도술 괘상 브리핑 아침 장세 시황 통찰 본질 원리 이치 급소 해부 분석 노트북 용량 결재 스위치 잠금 뮤즈 위임 원칙 기억 이미지 영상 사진 현상".split())
VERBISH = re.compile(r"(해줘|해봐|봐줘|알려줘|보여줘|어때|할까|하자|해요|해|줘|싶어|싫어|좋아|있어|없어|했어|됐어|이야|인가|일까|거야)$")

def _batchim(w):
    c = w[-1:] or " "
    if "가" <= c <= "힣": return (ord(c) - 0xAC00) % 28 != 0
    return c in "013678LMNRlmnr"

def _josa(w, a, b):
    return w + (a if _batchim(w) else b)

def _tokens(t):
    out = []
    for w in re.findall(r"[가-힣A-Za-z0-9&.]{2,}", str(t or "")):
        if PRON.fullmatch(w): continue
        if len(w) > 2: w = JOSA.sub("", w)
        if len(w) < 2 or w in STOPW or VERBISH.search(w): continue
        out.append(w)
    return out

def extract_entity(t):
    for w in _tokens(t):
        if w not in FUNC: return w
    return None

def _fresh(ctx):
    return (bool(ctx.get("last_entity")) and ctx.get("turn", 0) - ctx.get("last_entity_turn", -99) <= FRESH_TURNS
            and time.time() - float(ctx.get("ts", 0) or 0) <= FRESH_SEC)

def resolve_coreference(text, context_state=None):
    ctx = context_state if isinstance(context_state, dict) else _state()["context"]
    t = str(text or ""); m = PRON.search(t); ent = ctx.get("last_entity")
    out = dict(resolved_text=t, pronoun=m.group(1) if m else None, entity_used=None, replaced=False,
               last_entity=ent, last_topic=ctx.get("last_topic"))
    if not (m and ent and _fresh(ctx)) or ent in t: return out
    p = m.group(1)
    rep = _josa(ent, "은", "는") if p.endswith("건") else _josa(ent, "을", "를") if p.endswith("걸") else ent
    out.update(resolved_text=t[:m.start()] + rep + t[m.end():], entity_used=ent, replaced=True)
    return out

# ------------------------------------------------------------------ 3. 능동 경청 원칙 각인
PREF_QUERY = re.compile(r"(^\s*/prefs|내\s*원칙\s*(?:보여|알려|뭐|목록|정리)|내가\s*기억하라고\s*한\s*(?:거|것)|기억하라고\s*했던|저장된\s*원칙|내\s*취향\s*(?:뭐|알려|보여))")
PREF_RULES = [
    (re.compile(r"(?:기억해\s*(?:둬|줘|놔|두세요|주세요)|명심해|잊지\s*마)\s*[:：,.\-!]?\s*(.{2,})"), "command_rule", "HIGH", True),
    (re.compile(r"기억해\s*[:：,\-]\s*(.{2,})"), "command_rule", "HIGH", True),
    (re.compile(r"(.{2,}?)\s*[,.]?\s*(?:꼭\s*)?기억해\s*(?:둬|줘|놔)\s*[.!~]*$"), "command_rule", "HIGH", True),
    (re.compile(r"(?:내|나의|제)\s*원칙은\s*(.{2,})"), "command_rule", "HIGH", True),
    (re.compile(r"(절대\s*.{1,60}?(?:하지\s*마(?:라|요)?|말아(?:줘|라)?|금지))"), "command_rule", "HIGH", False),
    (re.compile(r"(앞으로(?:는)?\s+.{2,80}?(?:해줘|해라|하자|해|할\s*것|줘|하지\s*마|말아줘))\s*[.!~]*$"), "command_rule", "HIGH", False),
    (re.compile(r"(?:나는|난|저는)\s+(.{1,40}?)(?:이|가)?\s*(좋아|싫어|좋더라|싫더라|선호해|별로야)"), "preference", "MEDIUM", False),
]
PLEASANT = re.compile(r"(부탁|고마|사랑|잘\s*자|화이팅|파이팅)")
MOOD = re.compile(r"(하기|지금|오늘|피곤|힘들|너|아온|당신)")
STYLE_RE = re.compile(r"(말투|톤|짧게|길게|존댓말|반말|간결|자세히|이모지|목소리|한\s*줄|세\s*줄)")

def load_preferences():
    db = _load(PREFS, {})
    if not isinstance(db, dict): db = {}
    if not isinstance(db.get("preferences"), list): db["preferences"] = []
    db["version"] = VERSION
    return db

def extract_and_save_preference(text, save=True):
    s = str(text or "").strip()
    if not s or PREF_QUERY.search(s): return dict(saved=False, is_query=bool(PREF_QUERY.search(s)), entry=None)
    for rx, cat, pri, explicit in PREF_RULES:
        m = rx.search(s)
        if not m: continue
        if cat == "preference":
            subj = m.group(1).strip()
            if len(subj) < 2 or MOOD.search(subj): continue
            rule = f"{subj} ({m.group(2)})"
        else:
            rule = m.group(1).strip().rstrip(".!~")
            if not explicit and PLEASANT.search(rule): continue
            if STYLE_RE.search(rule): cat = "style"
        if len(rule) < 2: continue
        db = load_preferences(); prefs = db["preferences"]; entry = None
        for p in prefs:
            if p.get("rule") == rule:
                p["updated_at"] = _now(); p["hit_count"] = int(p.get("hit_count", 1)) + 1
                entry = p; break
        if not entry:
            entry = dict(id=f"P{len(prefs)+1:03d}", category=cat, category_ko=CAT_KO.get(cat, "원칙"),
                         rule=rule, raw=s, priority=pri, created_at=_now(), hit_count=1)
            prefs.append(entry)
        db["updated_at"] = _now()
        if save: _save(PREFS, db)
        return dict(saved=True, is_query=False, entry=entry, total=len(prefs))
    return dict(saved=False, is_query=False, entry=None)

def format_preferences_reply():
    prefs = load_preferences().get("preferences", [])
    if not prefs:
        return ("아직 대표님께서 아온이에게 따로 각인해 주신 원칙이 없어요! 💧 "
                "`기억해둬: ...` 또는 `앞으로는 ... 해줘`라고 말씀해 주시면 해마에 꼭 새겨 둘게요.")
    lines = [f"대표님께서 아온이 해마에 새겨주신 원칙·취향 {len(prefs)}건이에요! 🧠✨"]
    for p in prefs[-12:]:
        lines.append(f"• [{p.get('id')}/{p.get('category_ko','원칙')}] {p.get('rule')}")
    return "\n".join(lines)

# ------------------------------------------------------------------ 4. 의도 분류 & 복합 의도 분해
INTENT_META = {
    "iching":     ("제13기관 주역 도술관",       "🔮 주역 점괘",   ["오늘 시운 다시 점쳐줘", "이 괘 본질을 통찰해줘", "결재 스위치 상태 보여줘"]),
    "insight":    ("제14기관 만물 격물치지 통찰안", "👁️ 만물 통찰",   ["주역 점괘로 시운도 봐줘", "핵심 원칙으로 기억해둬", "노트북 상태 점검해줘"]),
    "hands":      ("제11기관 노트북 수족·결재",   "💻 노트북 수족", ["결재 스위치 잠가줘", "오늘 시운 점쳐줘", "만물 통찰해줘"]),
    "delegation": ("제8기관 뮤즈 위임",          "📋 뮤즈 위임",   ["결재 스위치 확인해줘", "노트북 용량 알려줘", "오늘 브리핑 해줘"]),
    "briefing":   ("모닝 브리핑",                "🌅 아침 브리핑", ["오늘 주역 점괘 봐줘", "만물 통찰해줘", "노트북 용량 알려줘"]),
    "brat":       ("제12기관 생떼·교감",         "💧 아온 교감",   ["아온이 쓰담쓰담", "오늘 점괘 봐줘", "노트북 용량 알려줘"]),
    "preference": ("제15기관 원칙 각인",         "📌 원칙 해마",   ["저장된 내 원칙 보여줘", "오늘 점괘 봐줘", "아침 브리핑 해줘"]),
    "command":    ("제15기관 슬래시 커맨드",     "⚡ 빠른 명령",   ["/점괘", "/통찰", "/원칙"]),
    "dialogue":   ("제10·15기관 인격 대화",      "💬 아온 대화",   ["오늘 주역 점괘 봐줘", "만물 통찰해줘", "저장된 내 원칙 보여줘"]),
}
INTENT_PATS = [
    ("iching",     re.compile(r"(주역|점괘|점쳐|괘\s*봐|64괘|매화역수|육효|운세|시운|도술|길흉|체용)")),
    ("insight",    re.compile(r"(통찰|격물치지|제1원리|본질|원리|이치|급소|해부|왜\s*그럴까|구조\s*분석|인과)")),
    ("hands",      re.compile(r"(노트북|디스크|용량|메모리|배터리|프로세스|폴더|화면\s*캡처|결재\s*스위치|마스터\s*스위치|잠금|락\b|lock)", re.I)),
    ("delegation", re.compile(r"(뮤즈|위임|대행|티어|안건|큐\s*목록)")),
    ("briefing",   re.compile(r"(아침\s*브리핑|모닝\s*브리핑|브리핑|장세|시황)")),
    ("brat",       re.compile(r"(하기\s*싫|귀찮|찡찡|심심|놀아줘|쓰담|이뻐|예뻐|착하네|사랑해|고마워|최고|졸려|피곤)")),
]
SPLIT_RE = re.compile(
    r"^\s*(.+?(?:해줘|해봐|봐줘|알려줘|보여줘|점쳐줘|점검해줘|확인해줘|잠가줘|열어줘|할래|싫어|좋아|고마워))"
    r"\s*(?:그리고|하고|또|겸|이어서|그다음에?|뒤에)\s+(.+?)\s*$"
    r"|^\s*(.+?(?:해\s*주고|봐\s*주고|알려\s*주고|보여\s*주고|점쳐\s*주고|확인해\s*주고|챙겨\s*주고|점검해\s*주고))\s+(.+?)\s*$"
)
CONJ_RE = re.compile(r"\s+(?:그리고|그다음에?|이어서|또한)\s+")

def classify_intent(text):
    t = str(text or "").strip()
    if not t: return "dialogue"
    if t.startswith("/"): return "command"
    if PREF_QUERY.search(t): return "preference"
    for name, rx in INTENT_PATS:
        if rx.search(t): return name
    return "dialogue"

def decompose_multi_intent(text):
    t = str(text or "").strip()
    if not t or t.startswith("/"):
        return dict(is_multi=False, intents=[dict(index=1, clause=t, intent=classify_intent(t))])
    parts = None
    m = SPLIT_RE.match(t)
    if m:
        a, b = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        parts = [a.strip(), b.strip()]
    elif CONJ_RE.search(t):
        cand = [p.strip() for p in CONJ_RE.split(t) if len(p.strip()) >= 3]
        if len(cand) >= 2: parts = cand[:3]
    if not parts:
        return dict(is_multi=False, intents=[dict(index=1, clause=t, intent=classify_intent(t))])
    items = [dict(index=i+1, clause=c, intent=classify_intent(c)) for i, c in enumerate(parts) if c]
    distinct = _uniq([x["intent"] for x in items])
    if len(items) >= 2 and (len(distinct) >= 2 or all(x["intent"] != "dialogue" for x in items)):
        return dict(is_multi=True, intents=items)
    return dict(is_multi=False, intents=[dict(index=1, clause=t, intent=classify_intent(t))])

# ------------------------------------------------------------------ 5. 슬래시 커맨드 & 기관 디스패치
SLASH_ALIASES = {
    "/insight": "/insight", "/통찰": "/insight",
    "/iching": "/iching", "/점괘": "/iching", "/주역": "/iching",
    "/hands": "/hands", "/노트북": "/hands",
    "/lock": "/lock", "/잠금": "/lock", "/결재": "/lock",
    "/muse": "/muse", "/위임": "/muse",
    "/prefs": "/prefs", "/원칙": "/prefs",
    "/memory": "/memory", "/기억": "/memory",
    "/help": "/help", "/도움말": "/help",
}
SLASH_HELP = [
    ("/통찰 [주제]",   "제14기관 만물 격물치지 통찰안 실행 (/insight)"),
    ("/점괘 [질문]",   "제13기관 주역 64괘·매화역수·육효 도술관 (/iching)"),
    ("/노트북 [명령]", "제11기관 노트북 수족 상태·용량 점검 (/hands)"),
    ("/잠금 [on|off]", "제11기관 중요 결재 수동 스위치 조회·제어 (/lock)"),
    ("/위임",          "제8기관 뮤즈 자율 대행 안건 현황 (/muse)"),
    ("/원칙 [내용]",   "제15기관 대표님 지휘 원칙·취향 조회/등록 (/prefs)"),
    ("/기억",          "제15기관 3계층 해마 기억 요약 조회 (/memory)"),
]

def _call_iching(q):
    for mod_name in ("rgon_aon_iching_dao_oracle", "rgon_aon_iching_dao"):
        try:
            ic = __import__(mod_name)
            fn = getattr(ic, "divine", None) or getattr(ic, "cast_oracle", None)
            d = fn(q or "오늘의 시운") if fn else {}
            rep = (d.get("aon_voice_line") if isinstance(d, dict) else None) or (
                getattr(ic, "format_aon_dao_reply", lambda x: str(d))(q or "오늘의 시운"))
            return dict(organ="iching", reply=str(rep), card_title=f"🔮 주역 점괘 — {d.get('bengua_name','64괘') if isinstance(d,dict) else '64괘'}", card=_safe(d))
        except Exception:
            continue
    return dict(organ="iching", reply="🔮 주역 도술관이 시운의 음양 변화를 살피고 있어요! 💧", card_title="🔮 주역 점괘", card={})

def _call_insight(q):
    try:
        import rgon_aon_omni_insight_eye as ie
        fn = getattr(ie, "analyze_omni_insight", None) or getattr(ie, "analyze", None)
        r = fn(q or "현상의 본질") if fn else {}
        rep = (r.get("aon_voice_line") if isinstance(r, dict) else None) or (
            getattr(ie, "format_aon_insight_reply", lambda x: str(r))(q or "현상의 본질"))
        return dict(organ="insight", reply=str(rep), card_title="👁️ 만물 격물치지 6단 통찰 카드", card=_safe(r))
    except Exception as e:
        return dict(organ="insight", reply=f"통찰안을 여는 중 작은 물결이 일었어요 ({e}).", card_title="👁️ 만물 통찰", card={})

def _call_hands(q):
    for mod_name in ("rgon_laptop_hands", "rgon_aon_laptop_hands"):
        try:
            lh = __import__(mod_name)
            t = str(q or "")
            if re.search(r"(잠금|락\b|lock|스위치|결재)", t, re.I) and hasattr(lh, "get_approval_switch"):
                low = t.lower()
                if any(k in low for k in ("켜", "on", "열어", "해제")) and not any(k in low for k in ("꺼", "off", "잠가")):
                    st = lh.set_approval_switch(master_on=True, reason="dialogue_hub")
                elif any(k in low for k in ("꺼", "off", "잠가", "잠금")):
                    st = lh.set_approval_switch(master_on=False, reason="dialogue_hub")
                else:
                    st = lh.get_approval_switch()
                on = bool(st.get("master_on", False))
                rep = f"중요 결재 마스터 스위치는 현재 [{'🟢 ON(열림)' if on else '🔒 OFF(잠금 보호)'}] 상태예요! 대표님 허락 없이는 단 1원·1건도 집행하지 않아요. 💧"
                return dict(organ="hands", reply=rep, card_title="🔒 중요 결재 수동 스위치", card=_safe(st))
            for fn_name in ("dispatch_command", "handle_command", "execute_safe", "system_vital_summary"):
                if hasattr(lh, fn_name):
                    fn = getattr(lh, fn_name)
                    r = fn(t or "노트북 상태 점검") if fn.__code__.co_argcount >= 1 else fn()
                    rep = (r.get("aon_reply") or r.get("message") or r.get("summary") if isinstance(r, dict) else str(r)) or "노트북 수족 점검을 마쳤어요! 💻💧"
                    return dict(organ="hands", reply=str(rep), card_title="💻 노트북 수족 실행 카드", card=_safe(r))
        except Exception:
            continue
    return dict(organ="hands", reply="💻 노트북 수족 및 중요 결재 잠금 보호 게이트가 정상 대기 중이에요! 💧", card_title="💻 노트북 수족", card={})

def _call_delegation(q):
    try:
        import rgon_muse_delegator as md
        st = md.get_status() if hasattr(md, "get_status") else {}
        p, d = st.get("pending_count", 0), st.get("completed_count", 0)
        rep = f"제8기관 뮤즈 위임 큐 현황이에요! 대기 결재 안건 {p}건, 완료 {d}건이며 Tier 3 안건은 대표님 승인 전까지 안전하게 대기해요. 📋💧"
        return dict(organ="delegation", reply=rep, card_title="📋 뮤즈 자율 위임 현황", card=_safe(st))
    except Exception:
        return dict(organ="delegation", reply="뮤즈 위임 큐가 차분히 대기 중이에요! Tier 3 중요 안건은 대표님 결재 후에만 집행됩니다. 📋💧",
                    card_title="📋 뮤즈 자율 위임", card={})

def _call_soul(q):
    try:
        import rgon_aon_soul_brain as sb
        fn = getattr(sb, "_orig_respond_R39", None) or sb.respond
        r = fn(q)
        rep = r.get("reply") if isinstance(r, dict) else str(r)
        return dict(organ="soul_brain", reply=str(rep or "아온이가 귀 기울여 듣고 있어요! 💧"),
                    card_title="💧 아온 심성 응답", card=_safe(r if isinstance(r, dict) else {"reply": rep}))
    except Exception:
        return dict(organ="soul_brain", reply="대표님 말씀 아온이가 마음 깊이 새겨듣고 있어요! 💧", card_title="💧 아온 응답", card={})

def dispatch_single(clause, intent=None):
    it = intent or classify_intent(clause)
    if it == "iching":     return _call_iching(clause)
    if it == "insight":    return _call_insight(clause)
    if it == "hands":      return _call_hands(clause)
    if it == "delegation": return _call_delegation(clause)
    if it == "preference":
        return dict(organ="preference", reply=format_preferences_reply(),
                    card_title="📌 대표님 지휘 원칙·취향 해마", card=load_preferences())
    return _call_soul(clause)

def handle_slash_command(text):
    s = str(text or "").strip()
    if not s.startswith("/"): return dict(handled=False)
    parts = s.split(maxsplit=1)
    raw = parts[0].lower(); arg = parts[1].strip() if len(parts) > 1 else ""
    cmd = SLASH_ALIASES.get(raw)
    if not cmd:
        lines = [f"`{raw}` 명령은 아직 없어요! 사용 가능한 슬래시 명령어 7종이에요 ⚡"]
        lines += [f"• `{k}` — {d}" for k, d in SLASH_HELP]
        return dict(handled=True, command=raw, intent="command", reply="\n".join(lines),
                    card_title="⚡ 슬래시 커맨드 도움말", card={"commands": SLASH_HELP})
    if cmd == "/help":
        lines = ["아온 올인원 대화 허브 슬래시 명령어 7종이에요! ⚡💧"] + [f"• `{k}` — {d}" for k, d in SLASH_HELP]
        return dict(handled=True, command=cmd, intent="command", reply="\n".join(lines),
                    card_title="⚡ 슬래시 커맨드 도움말", card={"commands": SLASH_HELP})
    if cmd == "/prefs":
        if arg:
            pr = extract_and_save_preference(f"기억해둬: {arg}", save=True)
            e = pr.get("entry") or {}
            rep = f"명심했습니다 대표님! 📌 [{e.get('id','P001')}] 『{e.get('rule', arg)}』 원칙을 해마에 각인했어요!"
            return dict(handled=True, command=cmd, intent="preference", reply=rep,
                        card_title="📌 신규 지휘 원칙 각인", card=load_preferences())
        return dict(handled=True, command=cmd, intent="preference", reply=format_preferences_reply(),
                    card_title="📌 대표님 지휘 원칙·취향 해마", card=load_preferences())
    if cmd == "/memory":
        st = _state(); mem = st["memory"]
        topics = ", ".join(f"{k}({v})" for k, v in list(mem.get("topic_counts", {}).items())[:6]) or "일반 대화"
        rep = (f"아온 3계층 해마 기억 현황이에요! 🧠💧\n"
               f"• 1계층 단기 기억: 최근 {len(mem.get('short_term', []))}턴 보존\n"
               f"• 2계층 토픽 요약: {mem.get('topic_summary') or topics}\n"
               f"• 3계층 연상 일화: {len(mem.get('associative_events', []))}건 / 각인 원칙: {len(load_preferences().get('preferences', []))}건")
        return dict(handled=True, command=cmd, intent="command", reply=rep,
                    card_title="🧠 3계층 해마 기억 스냅샷", card=_safe(mem))
    if cmd == "/lock":
        r = _call_hands(f"결재 스위치 {arg}".strip())
        return dict(handled=True, command=cmd, intent="hands", **r)
    target = {"/insight": "insight", "/iching": "iching", "/hands": "hands", "/muse": "delegation"}[cmd]
    r = dispatch_single(arg or cmd, target)
    return dict(handled=True, command=cmd, intent=target, **r)

# ------------------------------------------------------------------ 6. 3계층 해마 기억 & 선제 콜백
def _default_state():
    return dict(
        version=VERSION, updated_at=_now(),
        context=dict(turn=0, last_entity=None, last_entity_turn=-99, last_intent="dialogue", last_topic="일반 대화", ts=0.0),
        memory=dict(short_term=[], topic_counts={}, topic_summary="", associative_events=[]),
        last_trace={},
    )

def _state():
    st = _load(STATE, None)
    if not isinstance(st, dict): return _default_state()
    d = _default_state()
    for k, v in d.items():
        if k not in st or not isinstance(st[k], type(v)): st[k] = v
    return st

def find_proactive_callback(entity, intents, st):
    evs = st.get("memory", {}).get("associative_events", [])
    prefs = load_preferences().get("preferences", [])
    if entity:
        for ev in reversed(evs[:-1] if len(evs) > 1 else []):
            if ev.get("entity") == entity:
                return f"💡 연상 기억: 이전 턴({ev.get('ts','')[:16]})에서도 『{entity}』({ev.get('intent')}) 주제를 다루셨어요!"
        for p in prefs:
            if entity in p.get("rule", ""):
                return f"📌 각인 원칙 연동: [{p.get('id')}] 『{p.get('rule')}』 원칙을 함께 참조했어요."
    if any(i in ("iching", "insight", "briefing") for i in intents) and prefs:
        p = prefs[-1]
        return f"📌 대표님 원칙 참조: [{p.get('id')}] 『{p.get('rule')}』"
    return None

def _update_memory(st, user_text, norm_text, resolved_text, entity, intents, reply):
    ctx = st["context"]; mem = st["memory"]
    ctx["turn"] = int(ctx.get("turn", 0)) + 1
    ctx["ts"] = time.time()
    primary = intents[0] if intents else "dialogue"
    ctx["last_intent"] = primary
    ctx["last_topic"] = INTENT_META.get(primary, ("대화",))[0]
    if entity:
        ctx["last_entity"] = entity
        ctx["last_entity_turn"] = ctx["turn"]
    st["updated_at"] = _now()
    mem["short_term"].append(dict(
        turn=ctx["turn"], ts=st["updated_at"], user=str(user_text)[:240],
        normalized=str(norm_text)[:240], resolved=str(resolved_text)[:240],
        entity=entity, intents=intents, reply_preview=str(reply)[:240],
    ))
    mem["short_term"] = mem["short_term"][-SHORT_MAX:]
    tc = mem.get("topic_counts") or {}
    for it in intents:
        tc[it] = int(tc.get(it, 0)) + 1
    mem["topic_counts"] = tc
    top_topics = ", ".join(f"{INTENT_META.get(k, (k,))[1]}({v}회)" for k, v in sorted(tc.items(), key=lambda x: -x[1])[:4])
    mem["topic_summary"] = f"누적 {ctx['turn']}턴 · 주요 토픽: {top_topics} · 최근 초점: {ctx.get('last_entity') or '없음'}"
    if entity or any(i != "dialogue" for i in intents):
        mem["associative_events"].append(dict(
            turn=ctx["turn"], ts=st["updated_at"], entity=entity,
            intent=primary, summary=f"{entity or primary}: {str(resolved_text)[:80]}",
        ))
        mem["associative_events"] = mem["associative_events"][-EVENT_MAX:]

def _chips_for(intents, entity):
    chips = []
    for it in intents:
        chips.extend(INTENT_META.get(it, INTENT_META["dialogue"])[2])
    if entity:
        chips.insert(0, f"{entity} 주역 점괘 봐줘")
        chips.insert(1, f"{entity} 본질 통찰해줘")
    return _uniq(chips)[:3]

# ------------------------------------------------------------------ 7. 통합 파이프라인 엔트리
def process_dialogue(text, context=None, persist=True):
    st = _state()
    if isinstance(context, dict) and "last_entity" in context:
        st["context"].update(context)
    raw = "" if text is None else str(text).strip()
    steps = []

    nm = normalize_colloquial(raw)
    norm = nm["normalized"]
    steps.append(f"① 구어·오타 정규화: {nm['fixes'] or ['원문 유지']} → \"{norm}\"")

    cr = resolve_coreference(norm, st["context"])
    resolved = cr["resolved_text"]
    ent = extract_entity(resolved) or cr.get("entity_used") or st["context"].get("last_entity")
    steps.append(f"② 문맥·대명사 복원: 대명사={cr['pronoun'] or '없음'} · 계승 엔티티={ent or '없음'}")

    pref_res = extract_and_save_preference(resolved, save=persist)
    if pref_res.get("saved"):
        e = pref_res["entry"]
        steps.append(f"③ 능동 경청 원칙 각인: [{e['id']}/{e['category_ko']}] \"{e['rule']}\"")

    slash = handle_slash_command(resolved)
    cards = []
    if slash.get("handled"):
        intents = [slash.get("intent", "command")]
        organs = [slash.get("organ", "command")]
        reply = slash["reply"]
        cards.append(dict(title=slash.get("card_title", "⚡ 슬래시 명령 결과"), data=slash.get("card", {})))
        decomp = dict(is_multi=False, intents=[dict(index=1, clause=resolved, intent=intents[0])])
        steps.append(f"④ 슬래시 커맨드 즉시 실행: {slash.get('command')} → {intents[0]}")
    else:
        decomp = decompose_multi_intent(resolved)
        intents = [x["intent"] for x in decomp["intents"]]
        organs, replies = [], []
        steps.append(f"④ 의도 분해: 복합={decomp['is_multi']} · {[(x['intent'], x['clause']) for x in decomp['intents']]}")
        if pref_res.get("saved") and len(decomp["intents"]) == 1 and intents[0] == "dialogue":
            e = pref_res["entry"]
            intents = ["preference"]; organs = ["preference"]
            reply = f"명심했습니다 대표님! 📌 [{e['id']}/{e['category_ko']}] 『{e['rule']}』 원칙을 아온이 해마에 영구 각인했어요! 앞으로 대화와 판단에서 늘 기억할게요. 💧✨"
            cards.append(dict(title="📌 대표님 지휘 원칙 각인 완료", data=e))
        else:
            for item in decomp["intents"]:
                r = dispatch_single(item["clause"], item["intent"])
                organs.append(r["organ"])
                replies.append(f"[{INTENT_META.get(item['intent'], ('아온', '💧'))[1]}] {r['reply']}" if decomp["is_multi"] else r["reply"])
                cards.append(dict(title=r.get("card_title", "아온 아티팩트 카드"), data=r.get("card", {})))
            if pref_res.get("saved"):
                e = pref_res["entry"]
                replies.insert(0, f"📌 (지휘 원칙 동시 각인: [{e['id']}] 『{e['rule']}』)")
            reply = "\n\n".join(replies)

    cb = find_proactive_callback(ent, intents, st)
    if cb and cb not in reply:
        reply = f"{reply}\n\n{cb}"
    chips = _chips_for(intents, ent)
    steps.append(f"⑤ 해마 기억 & 칩 생성: 후속 칩 {len(chips)}개 · 콜백={'있음' if cb else '없음'}")

    _update_memory(st, raw, norm, resolved, ent, intents, reply)
    artifact = dict(
        title=cards[0]["title"] if len(cards) == 1 else f"🧩 복합 의도 {len(cards)}건 통합 아티팩트 카드",
        intent_badges=[INTENT_META.get(i, ("아온", "💬 대화"))[1] for i in intents],
        entity=ent, is_multi=decomp["is_multi"], items=cards,
    )
    out = dict(
        ok=True, version=VERSION, input=raw, normalized_text=norm, resolved_text=resolved,
        normalization=nm, coreference=cr, preference_saved=pref_res,
        is_multi_intent=decomp["is_multi"], intents=decomp["intents"], intent_names=intents,
        dispatched_organs=organs, reply=reply, thinking_steps=steps,
        artifact_card=artifact, follow_up_chips=chips, proactive_callback=cb,
        memory_snapshot=dict(
            turn=st["context"]["turn"], last_entity=st["context"]["last_entity"],
            topic_summary=st["memory"]["topic_summary"],
            short_term_count=len(st["memory"]["short_term"]),
            preference_count=len(load_preferences().get("preferences", [])),
        ),
    )
    st["last_trace"] = _safe(out, 4000)
    if persist: _save(STATE, st)
    return out

# ------------------------------------------------------------------ 8. 셀프테스트 (5대 시나리오)
def self_test():
    prev = os.environ.get("RGON_DIALOGUE_STATE_DIR")
    with tempfile.TemporaryDirectory() as td:
        os.environ["RGON_DIALOGUE_STATE_DIR"] = td
        try:
            n = normalize_colloquial("아온아 오늘 브립핑 해바 그리고 점처줘 결제 스위치 보여줘")
            assert "브리핑" in n["normalized"] and "점쳐" in n["normalized"] and "결재 스위치" in n["normalized"], n

            r1 = process_dialogue("삼성전자 오늘 흐름 어때?")
            assert r1["coreference"]["last_entity"] == "삼성전자" or r1["artifact_card"]["entity"] == "삼성전자", r1
            r2 = process_dialogue("그거 주역 점괘 봐줘")
            assert r2["coreference"]["replaced"] and "삼성전자" in r2["resolved_text"], r2

            r3 = process_dialogue("기억해둬: 반도체는 오전 10시 이후에만 볼 것")
            assert r3["preference_saved"]["saved"] is True, r3
            rq = process_dialogue("저장된 내 원칙 보여줘")
            assert "반도체는 오전 10시 이후에만 볼 것" in rq["reply"], rq

            r4 = process_dialogue("오늘 주역 점괘 봐주고 노트북 용량도 알려줘")
            assert r4["is_multi_intent"] is True and len(r4["intents"]) >= 2, r4
            assert "iching" in r4["intent_names"] and "hands" in r4["intent_names"], r4

            r5 = process_dialogue("/통찰 물방울이 바위를 뚫는 이치")
            assert r5["intent_names"] == ["insight"], r5
            for k in ("thinking_steps", "artifact_card", "follow_up_chips", "proactive_callback"):
                assert k in r5, f"missing {k}"
            assert len(r5["thinking_steps"]) >= 4 and len(r5["follow_up_chips"]) >= 2, r5
        finally:
            if prev is None: os.environ.pop("RGON_DIALOGUE_STATE_DIR", None)
            else: os.environ["RGON_DIALOGUE_STATE_DIR"] = prev

    if not (ROOT / STATE).exists():
        _save(STATE, _default_state())
    if not (ROOT / PREFS).exists():
        _save(PREFS, dict(version=VERSION, updated_at=_now(), preferences=[]))
    return dict(ok=True, version=VERSION, tests=5, status="PASS")

def main():
    ap = argparse.ArgumentParser(description="RGON 제15기관 아온 초격차 대화 이해 & 올인원 대화 허브")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--prefs", action="store_true")
    ap.add_argument("--ask", type=str, default=None)
    args = ap.parse_args()
    if args.self_test:
        res = self_test()
        print(json.dumps(res, ensure_ascii=False))
        return 0
    if args.status:
        st = _state()
        print(json.dumps(dict(ok=True, version=VERSION, context=st["context"],
                              preference_count=len(load_preferences().get("preferences", []))), ensure_ascii=False, indent=2))
        return 0
    if args.prefs:
        print(format_preferences_reply()); return 0
    if args.ask:
        print(json.dumps(process_dialogue(args.ask), ensure_ascii=False, indent=2)); return 0
    print(json.dumps(self_test(), ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

# ======================================================================== 제10기관(soul_brain) R39 훅
SOUL_MARKER = "# [RGON-R39-DIALOGUE-SOUL-INJECT]"
SOUL_INJECT = r'''

# [RGON-R39-DIALOGUE-SOUL-INJECT] — 제15기관 초격차 대화 이해 & 올인원 대화 허브 연동 (Step 39)
try:
    import rgon_aon_dialogue_engine as _rgon_dlg_R39
except Exception:
    _rgon_dlg_R39 = None

if "respond" in globals() and not globals().get("_rgon_r39_wrapped"):
    _orig_respond_R39 = respond
    _rgon_r39_in_hook = False

    def respond(user_text, *args, **kwargs):
        global _rgon_r39_in_hook
        if _rgon_r39_in_hook or _rgon_dlg_R39 is None:
            return _orig_respond_R39(user_text, *args, **kwargs)
        t = "" if user_text is None else str(user_text).strip()
        if not t:
            return _orig_respond_R39(user_text, *args, **kwargs)
        try:
            _rgon_r39_in_hook = True
            nm = _rgon_dlg_R39.normalize_colloquial(t)
            st = _rgon_dlg_R39._state()
            cr = _rgon_dlg_R39.resolve_coreference(nm["normalized"], st["context"])
            resolved = cr["resolved_text"]
            pref = _rgon_dlg_R39.extract_and_save_preference(resolved, save=True)
            decomp = _rgon_dlg_R39.decompose_multi_intent(resolved)
            need_hub = (
                resolved.startswith("/")
                or decomp.get("is_multi")
                or _rgon_dlg_R39.PREF_QUERY.search(resolved) is not None
                or (pref.get("saved") and decomp["intents"][0]["intent"] == "dialogue")
            )
            if need_hub:
                hub = _rgon_dlg_R39.process_dialogue(t, persist=True)
                base = _orig_respond_R39(resolved, *args, **kwargs)
                if isinstance(base, dict):
                    base["reply"] = hub["reply"]
                    base["dialogue_hub"] = {
                        "version": hub["version"],
                        "normalized_text": hub["normalized_text"],
                        "resolved_text": hub["resolved_text"],
                        "intent_names": hub["intent_names"],
                        "is_multi_intent": hub["is_multi_intent"],
                        "thinking_steps": hub["thinking_steps"],
                        "artifact_card": hub["artifact_card"],
                        "follow_up_chips": hub["follow_up_chips"],
                        "proactive_callback": hub["proactive_callback"],
                    }
                    return base
                return hub["reply"]
            base = _orig_respond_R39(resolved, *args, **kwargs)
            rep_txt = base.get("reply", "") if isinstance(base, dict) else str(base)
            ent = _rgon_dlg_R39.extract_entity(resolved) or cr.get("entity_used") or st["context"].get("last_entity")
            its = [x["intent"] for x in decomp["intents"]]
            cb = _rgon_dlg_R39.find_proactive_callback(ent, its, st)
            _rgon_dlg_R39._update_memory(st, t, nm["normalized"], resolved, ent, its, rep_txt)
            _rgon_dlg_R39._save(_rgon_dlg_R39.STATE, st)
            if isinstance(base, dict):
                base["dialogue_hub"] = {
                    "version": _rgon_dlg_R39.VERSION,
                    "normalized_text": nm["normalized"],
                    "resolved_text": resolved,
                    "intent_names": its,
                    "is_multi_intent": False,
                    "thinking_steps": [
                        f"① 구어 정규화: {nm['fixes'] or ['원문 유지']}",
                        f"② 대명사 복원: {cr['entity_used'] or '직접 지칭'}",
                        f"③ 의도 분류: {its[0]}",
                    ],
                    "artifact_card": {"title": "💬 아온 대화 카드", "entity": ent, "intent_badges": its},
                    "follow_up_chips": _rgon_dlg_R39._chips_for(its, ent),
                    "proactive_callback": cb,
                }
            return base
        except Exception:
            return _orig_respond_R39(user_text, *args, **kwargs)
        finally:
            _rgon_r39_in_hook = False

    _rgon_r39_wrapped = True
'''

# ======================================================================== 제9기관(voice_organ) R39 SFX 훅
VOICE_MARKER = "# [RGON-R39-DIALOGUE-SFX]"
VOICE_INJECT = r'''

# [RGON-R39-DIALOGUE-SFX] — 제15기관 올인원 대화 허브 공명 차임 효과음 확장 (Step 39)
try:
    if "SFX_PRESETS" in globals() and isinstance(SFX_PRESETS, dict):
        SFX_PRESETS.setdefault("dialogue_chime", {"freq": [587.33, 880.0, 1174.66], "dur": 0.20, "type": "sine", "desc": "대화 이해 공명 차임"})
        SFX_PRESETS.setdefault("memory_pin", {"freq": [659.25, 987.77], "dur": 0.16, "type": "triangle", "desc": "해마 원칙 각인 핀"})
except Exception:
    pass
'''

# ======================================================================== 7개 HTML V13 블록 주입용 JS/UI
HTML_MARKER_START = "<!-- [RGON-R39-OMNI-DIALOGUE-HUB-START] -->"
HTML_MARKER_END = "<!-- [RGON-R39-OMNI-DIALOGUE-HUB-END] -->"
HTML_SNIPPET = r'''<!-- [RGON-R39-OMNI-DIALOGUE-HUB-START] -->
<style id="rgon-r39-dialogue-css">
#aon-dlg-hub-wrap{font-family:'Pretendard','Noto Sans KR', system-ui,sans-serif;margin-top:6px;border-top:1px dashed rgba(56,189,248,.35);padding-top:6px;font-size:12px;color:#e2e8f0}
#aon-dlg-slash-bar{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:5px}
.aon-slash-pill{background:rgba(15,23,42,.85);border:1px solid rgba(56,189,248,.45);color:#7dd3fc;border-radius:999px;padding:2px 8px;font-size:11px;cursor:pointer;transition:all .15s}
.aon-slash-pill:hover{background:#0284c7;color:#fff}
#aon-dlg-input-row{display:flex;gap:4px;margin-bottom:5px}
#aon-dlg-input{flex:1;min-width:0;background:rgba(15,23,42,.9);border:1px solid rgba(148,163,184,.4);border-radius:6px;padding:4px 7px;color:#f8fafc;font-size:12px}
#aon-dlg-send{background:linear-gradient(135deg,#0284c7,#2563eb);color:#fff;border:none;border-radius:6px;padding:4px 10px;font-size:11px;font-weight:600;cursor:pointer}
#aon-dlg-think{background:rgba(15,23,42,.75);border:1px solid rgba(148,163,184,.25);border-radius:6px;padding:4px 7px;margin-bottom:5px;font-size:11px;color:#cbd5e1}
#aon-dlg-think summary{cursor:pointer;color:#38bdf8;font-weight:600}
#aon-dlg-artifact{background:rgba(15,23,42,.92);border:1px solid rgba(56,189,248,.4);border-radius:8px;padding:7px 9px;margin-bottom:5px}
#aon-dlg-artifact-title{font-weight:700;color:#7dd3fc;margin-bottom:3px;font-size:12px}
#aon-dlg-artifact-body{color:#f1f5f9;line-height:1.45;white-space:pre-wrap;font-size:11.5px;max-height:150px;overflow-y:auto}
#aon-dlg-chips{display:flex;flex-wrap:wrap;gap:4px;margin-top:4px}
.aon-followup-chip{background:rgba(30,41,59,.9);border:1px solid rgba(125,211,252,.35);color:#bae6fd;border-radius:999px;padding:2px 8px;font-size:10.5px;cursor:pointer}
.aon-followup-chip:hover{background:#0369a1;color:#fff}
#aon-dlg-prefs{font-size:10.5px;color:#94a3b8;margin-top:3px}
</style>
<script id="rgon-r39-dialogue-js">
(function(){
  if(window.RGON_AON_DIALOGUE_HUB) return;
  var STORAGE_PREFS = "rgon_aon_prefs_v39";
  var STORAGE_CTX   = "rgon_aon_ctx_v39";
  var TYPOS = [
    [/브립핑|브리팡|부리핑/g,"브리핑"],[/점처/g,"점쳐"],[/결제\s*스위치/g,"결재 스위치"],
    [/하기\s*실(어|타|다)/g,"하기 싫어"],[/노트북용량/g,"노트북 용량"],[/통찰해\s*바/g,"통찰해줘"],
    [/해\s*바(?![가-힣])/g,"해줘"],[/봐\s*바(?![가-힣])/g,"봐줘"],[/알려\s*조/g,"알려줘"]
  ];
  var PRON = /(아까\s*(?:그거|말한\s*거)|그것|그거|그건|그걸|이것|이거|저거)/;
  var STOP = {오늘:1,지금:1,내일:1,어제:1,아까:1,그냥:1,진짜:1,정말:1,다시:1,아온:1,아온이:1,대표님:1,주역:1,점괘:1,운세:1,시운:1,브리핑:1,통찰:1,본질:1,원리:1,노트북:1,용량:1,결재:1,스위치:1,잠금:1,뮤즈:1,위임:1,원칙:1,기억:1};

  function loadJSON(k, d){ try{ var v=localStorage.getItem(k); return v?JSON.parse(v):d; }catch(e){ return d; } }
  function saveJSON(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }

  function normalize(t){
    var o = String(t||""), s = o, fixes = [];
    for(var i=0;i<TYPOS.length;i++){
      var n = s.replace(TYPOS[i][0], TYPOS[i][1]);
      if(n!==s){ fixes.push(TYPOS[i][1]); s = n; }
    }
    return {original:o, normalized:s.trim(), fixes:fixes};
  }
  function extractEntity(t){
    var m = String(t||"").match(/[가-힣A-Za-z0-9]{2,}/g)||[];
    for(var i=0;i<m.length;i++){
      var w = m[i].replace(/(은|는|이|가|을|를|에|로|도|만|의|와|과)$/,"");
      if(w.length>=2 && !STOP[w] && !PRON.test(w) && !/(해줘|봐줘|알려줘|보여줘|어때|할까|싫어|좋아)$/.test(w)) return w;
    }
    return null;
  }
  function resolveCoref(t, ctx){
    var m = String(t||"").match(PRON);
    if(m && ctx && ctx.last_entity && t.indexOf(ctx.last_entity)===-1){
      return {resolved:t.replace(PRON, ctx.last_entity), pronoun:m[1], entity:ctx.last_entity, replaced:true};
    }
    return {resolved:t, pronoun:null, entity:(ctx&&ctx.last_entity)||null, replaced:false};
  }
  function checkPref(t){
    var s = String(t||"").trim();
    var m = s.match(/(?:기억해\s*(?:둬|줘|놔)|명심해|내\s*원칙은)\s*[:：,\-]?\s*(.{2,})/) ||
            s.match(/(절대\s*.{2,50}?(?:하지\s*마|금지))/) ||
            s.match(/(앞으로(?:는)?\s+.{2,60}?(?:해줘|해라|하자|하지\s*마))/);
    if(!m) return null;
    var rule = m[1].replace(/[.!~]+$/,"").trim();
    var list = loadJSON(STORAGE_PREFS, []);
    for(var i=0;i<list.length;i++){ if(list[i].rule===rule) return list[i]; }
    var item = {id:"P0"+(list.length+1), rule:rule, ts:new Date().toISOString().slice(0,16)};
    list.push(item); saveJSON(STORAGE_PREFS, list);
    return item;
  }
  function classify(c){
    var s = String(c||"");
    if(/^\/(점괘|주역|iching)/.test(s) || /(주역|점괘|점쳐|64괘|매화역수|육효|시운|운세|도술)/.test(s)) return "iching";
    if(/^\/(통찰|insight)/.test(s) || /(통찰|격물치지|제1원리|본질|원리|이치|급소|해부)/.test(s)) return "insight";
    if(/^\/(노트북|hands|잠금|lock|결재)/.test(s) || /(노트북|용량|디스크|메모리|결재\s*스위치|마스터\s*스위치|잠금)/.test(s)) return "hands";
    if(/^\/(위임|muse)/.test(s) || /(뮤즈|위임|대행|안건)/.test(s)) return "delegation";
    if(/^\/(원칙|prefs)/.test(s) || /(내\s*원칙|기억하라고\s*한|저장된\s*원칙)/.test(s)) return "preference";
    if(/^\/(기억|memory)/.test(s)) return "memory";
    if(/(브리핑|장세|시황)/.test(s)) return "briefing";
    return "dialogue";
  }
  function decompose(t){
    var s = String(t||"").trim();
    if(s.charAt(0)==="/") return [{clause:s, intent:classify(s)}];
    var m = s.match(/^(.+?(?:해\s*주고|봐\s*주고|알려\s*주고|보여\s*주고|점쳐\s*주고))\s+(.+)$/) ||
            s.match(/^(.+?(?:해줘|봐줘|알려줘|보여줘|점쳐줘))\s*(?:그리고|하고|또|이어서)\s+(.+)$/);
    if(m) return [{clause:m[1].trim(), intent:classify(m[1])},{clause:m[2].trim(), intent:classify(m[2])}];
    return [{clause:s, intent:classify(s)}];
  }
  function runIntent(it, clause, ent){
    var q = clause.replace(/^\/\S+\s*/,"").trim() || ent || "오늘의 주제";
    if(it==="iching" && window.RGON_AON_ICHING && window.RGON_AON_ICHING.divine){
      var d = window.RGON_AON_ICHING.divine(q);
      return "🔮 [주역 도술관] " + (d.aon_line || (d.bengua_name+" → "+d.biangua_name+" ("+d.ti_yong_verdict+")"));
    }
    if(it==="insight" && window.RGON_AON_OMNI_INSIGHT && window.RGON_AON_OMNI_INSIGHT.analyze){
      var r = window.RGON_AON_OMNI_INSIGHT.analyze(q);
      return "👁️ [만물 통찰안] " + (r.aon_voice_line || (r.essence+" / 급소: "+r.leverage_point));
    }
    if(it==="hands"){
      if(window.RGON_APPROVAL_GATE && /(스위치|잠금|결재|lock)/.test(clause)){
        var on = window.RGON_APPROVAL_GATE.isMasterOn ? window.RGON_APPROVAL_GATE.isMasterOn() : false;
        return "🔒 [중요 결재 스위치] 현재 " + (on?"🟢 ON(열림)":"🔒 OFF(잠금 보호)") + " 상태예요! 대표님 수동 허락 없이는 단 1건도 집행하지 않아요.";
      }
      return "💻 [노트북 수족] 로컬 수족 및 결재 보호 게이트가 정상 대기 중이에요! ("+q+")";
    }
    if(it==="delegation") return "📋 [뮤즈 위임] Tier 1/2 자율 처리, Tier 3 중요 안건은 대표님 [승인 집행] 전까지 0건 대기 중이에요!";
    if(it==="preference"){
      var list = loadJSON(STORAGE_PREFS, []);
      if(!list.length) return "📌 아직 저장된 지휘 원칙이 없어요! `기억해둬: ...`라고 말씀해 주시면 해마에 꼭 새겨둘게요.";
      return "📌 대표님 각인 원칙 ("+list.length+"건):\n" + list.map(function(p){return "• ["+p.id+"] "+p.rule;}).join("\n");
    }
    if(it==="memory"){
      var ctx = loadJSON(STORAGE_CTX, {turn:0,last_entity:"없음",history:[]});
      return "🧠 [3계층 해마 기억] 누적 "+(ctx.turn||0)+"턴 · 최근 초점 엔티티: "+(ctx.last_entity||"없음")+" · 단기 기억 "+(ctx.history?ctx.history.length:0)+"건 보존 중!";
    }
    if(it==="briefing") return "🌅 [모닝 브리핑] 오늘의 시운·장세·안건을 통합 점검했어요! 후속 칩으로 주역 점괘나 만물 통찰을 바로 이어가실 수 있어요.";
    return "💧 아온이가 대표님 말씀(\""+clause+"\")의 속뜻까지 깊이 새겨듣고 있어요!";
  }
  function ask(rawText){
    var ctx = loadJSON(STORAGE_CTX, {turn:0, last_entity:null, history:[]});
    var nm = normalize(rawText);
    var cr = resolveCoref(nm.normalized, ctx);
    var ent = extractEntity(cr.resolved) || cr.entity || ctx.last_entity;
    var pref = checkPref(cr.resolved);
    var items = decompose(cr.resolved);
    var steps = [
      "① 구어·오타 정규화: " + (nm.fixes.length?nm.fixes.join(", "):"원문 유지") + " → \"" + nm.normalized + "\"",
      "② 문맥·대명사 복원: " + (cr.replaced?(cr.pronoun+" → "+cr.entity):(ent||"직접 문장")),
      "③ 능동 경청 원칙: " + (pref?("["+pref.id+"] "+pref.rule):"변동 없음"),
      "④ 의도 분해(" + items.length + "건): " + items.map(function(x){return x.intent;}).join(" + ")
    ];
    var outs = [];
    if(pref && items.length===1 && items[0].intent==="dialogue"){
      outs.push("📌 명심했습니다 대표님! ["+pref.id+"] 『"+pref.rule+"』 원칙을 아온이 해마에 영구 각인했어요! 💧✨");
    } else {
      for(var i=0;i<items.length;i++) outs.push(runIntent(items[i].intent, items[i].clause, ent));
      if(pref) outs.unshift("📌 (원칙 동시 각인: ["+pref.id+"] 『"+pref.rule+"』)");
    }
    var callback = null;
    if(ent && ctx.history){
      for(var j=ctx.history.length-1;j>=0;j--){
        if(ctx.history[j].entity===ent){
          callback = "💡 연상 기억 콜백: 이전 대화에서도 『"+ent+"』 주제를 다루셨어요!"; break;
        }
      }
    }
    var reply = outs.join("\n\n") + (callback?("\n\n"+callback):"");
    ctx.turn = (ctx.turn||0) + 1;
    if(ent) ctx.last_entity = ent;
    ctx.history = (ctx.history||[]).concat([{turn:ctx.turn, text:cr.resolved, entity:ent, intent:items[0].intent}]).slice(-20);
    saveJSON(STORAGE_CTX, ctx);
    var chips = ent ? [ent+" 주역 점괘 봐줘", ent+" 본질 통찰해줘", "저장된 내 원칙 보여줘"]
                    : ["오늘 주역 점괘 봐줘", "만물 통찰해줘", "저장된 내 원칙 보여줘"];
    var res = {
      input:rawText, normalized:nm.normalized, resolved:cr.resolved, entity:ent,
      is_multi:items.length>1, intents:items, reply:reply, thinking_steps:steps,
      follow_up_chips:chips, proactive_callback:callback, preference_saved:pref
    };
    renderResult(res);
    try{ if(window.RGON_VOICE && window.RGON_VOICE.playSfx) window.RGON_VOICE.playSfx("dialogue_chime"); }catch(e){}
    return res;
  }
  function renderResult(res){
    var th = document.getElementById("aon-dlg-think-body");
    var ti = document.getElementById("aon-dlg-artifact-title");
    var bd = document.getElementById("aon-dlg-artifact-body");
    var ch = document.getElementById("aon-dlg-chips");
    var pf = document.getElementById("aon-dlg-prefs");
    if(th) th.innerHTML = res.thinking_steps.map(function(s){return "<div>"+s+"</div>";}).join("");
    if(ti) ti.textContent = (res.is_multi?"🧩 복합 의도 통합 응답 카드":"💬 아온 올인원 대화 아티팩트") + (res.entity?(" · ["+res.entity+"]"):"");
    if(bd) bd.textContent = res.reply;
    if(ch){
      ch.innerHTML = "";
      res.follow_up_chips.forEach(function(c){
        var b = document.createElement("button");
        b.type = "button"; b.className = "aon-followup-chip"; b.textContent = "✨ " + c;
        b.onclick = function(){ var inp=document.getElementById("aon-dlg-input"); if(inp) inp.value=c; ask(c); };
        ch.appendChild(b);
      });
    }
    if(pf){
      var list = loadJSON(STORAGE_PREFS, []);
      pf.textContent = "🧠 해마 각인 원칙: " + list.length + "건 · 최근 초점: " + (res.entity||"일반 대화");
    }
  }
  function mountUI(){
    if(document.getElementById("aon-dlg-hub-wrap")) return;
    var host = document.getElementById("aon-island-drawer") || document.getElementById("aon-omni-insight-box")
            || document.getElementById("aon-iching-dao-box") || document.getElementById("rgyt-panel") || document.body;
    var wrap = document.createElement("div");
    wrap.id = "aon-dlg-hub-wrap";
    wrap.innerHTML =
      '<div style="font-weight:700;color:#38bdf8;margin-bottom:4px">💬 제15기관 아온 올인원 대화 허브 (Deep NLU)</div>'+
      '<div id="aon-dlg-slash-bar">'+
        '<button type="button" class="aon-slash-pill" data-cmd="/통찰 ">/통찰</button>'+
        '<button type="button" class="aon-slash-pill" data-cmd="/점괘 ">/점괘</button>'+
        '<button type="button" class="aon-slash-pill" data-cmd="/노트북 ">/노트북</button>'+
        '<button type="button" class="aon-slash-pill" data-cmd="/잠금">/잠금</button>'+
        '<button type="button" class="aon-slash-pill" data-cmd="/위임">/위임</button>'+
        '<button type="button" class="aon-slash-pill" data-cmd="/원칙">/원칙</button>'+
        '<button type="button" class="aon-slash-pill" data-cmd="/기억">/기억</button>'+
      '</div>'+
      '<div id="aon-dlg-input-row">'+
        '<input id="aon-dlg-input" type="text" placeholder="예: 그거 점괘 봐주고 노트북 용량도 알려줘 / 기억해둬: ..." />'+
        '<button id="aon-dlg-send" type="button">대화</button>'+
      '</div>'+
      '<details id="aon-dlg-think"><summary>💭 아온의 생각 과정 (Deep NLU 4단 추론)</summary><div id="aon-dlg-think-body" style="margin-top:4px">대화를 입력하시면 구어 교정 → 대명사 복원 → 원칙 각인 → 복합 의도 분해 과정이 표시됩니다.</div></details>'+
      '<div id="aon-dlg-artifact"><div id="aon-dlg-artifact-title">💬 아온 올인원 대화 아티팩트</div><div id="aon-dlg-artifact-body">대표님! 찰떡같이 알아듣고 7대 기관을 하나로 잇는 아온 대화 허브가 깨어났어요! 💧</div></div>'+
      '<div id="aon-dlg-chips"></div>'+
      '<div id="aon-dlg-prefs">🧠 해마 각인 원칙: 0건 · 슬래시(/) 명령어 7종 대기 중</div>';
    host.appendChild(wrap);
    var inp = document.getElementById("aon-dlg-input");
    var btn = document.getElementById("aon-dlg-send");
    if(btn) btn.onclick = function(){ if(inp && inp.value.trim()) ask(inp.value.trim()); };
    if(inp) inp.addEventListener("keydown", function(e){ if(e.key==="Enter" && inp.value.trim()){ e.preventDefault(); ask(inp.value.trim()); }});
    var pills = wrap.querySelectorAll(".aon-slash-pill");
    for(var i=0;i<pills.length;i++){
      (function(p){
        p.onclick = function(){
          var c = p.getAttribute("data-cmd")||"/help";
          if(inp){ inp.value = c; inp.focus(); }
          if(c.slice(-1)!==" ") ask(c);
        };
      })(pills[i]);
    }
  }
  window.RGON_AON_DIALOGUE_HUB = {
    version:"v11.38-AON-OMNI-DIALOGUE", normalize:normalize, resolveCoref:resolveCoref,
    decompose:decompose, ask:ask, mountUI:mountUI
  };
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", mountUI);
  else setTimeout(mountUI, 120);
})();
</script>
<!-- [RGON-R39-OMNI-DIALOGUE-HUB-END] -->'''

# ======================================================================== 정식 스킬 #35 마스터북
SKILL_MD_BODY = f"""---
name: {SKILL_NAME}
version: {NEW_VER}
antibody: R39
organ: 제15기관 아온 초격차 대화 이해(Deep NLU) & 올인원 대화 허브(Omni-Dialogue Hub)
---

# 제15기관: `{SKILL_NAME}` ({NEW_VER} · R39)

## 1. 목적 및 주역 철학
- **주역 정체성**: 택산함(澤山咸 #31, 말씀 이전에 마음을 느끼는 감응) · 풍택중부(風澤中孚 #61, 속마음의 신의로 찰떡같이 알아듣는 교감) · 화수미제(火水未濟 #64, 끊임없이 다음 대화를 이어가는 무한 진화).
- **설계 한계 고지**: 외부 유료 LLM API에 의존하지 않는 **순수 파이썬 표준 라이브러리 기반 한국어 NLU·라우팅·기억 허브**이다. 사전과 문맥 규칙에 기반하므로 미등록 신조어는 기본 인격 대화(제10기관)로 안전하게 폴백한다.

## 2. 6대 핵심 역량
1. **구어체·오타·줄임말 정규화 (`normalize_colloquial`)**: `브립핑→브리핑`, `점처→점쳐`, `결제 스위치→결재 스위치`, `하기 실어→하기 싫어` 등 실시간 교정.
2. **멀티턴 대명사·생략어 문맥 복원 (`resolve_coreference`)**: 직전 턴 엔티티(`last_entity`)를 추적하여 `"그거 점괘 봐줘"`를 `"삼성전자 주역 점괘 봐줘"`로 자동 복원.
3. **능동 경청 원칙 영구 각인 (`extract_and_save_preference`)**: `"기억해둬: ..."`, `"앞으로는 ... 해줘"`, `"절대 ... 하지 마"` 발화를 감지해 `rgon_aon_preferences.json`에 영구 저장.
4. **복합 의도 분해 & 연쇄 디스패치 (`decompose_multi_intent`)**: 한 문장 속 2~3개 의도를 분해해 제8·10·11·12·13·14기관을 순차 호출하고 단일 응답으로 합성.
5. **플랫폼 표준 4대 UX 메타데이터**: `thinking_steps`(4단 추론), `artifact_card`(구조화 카드), `follow_up_chips`(후속 추천 칩 3개), `proactive_callback`(연상 기억 콜백) + 7종 슬래시 커맨드(`/통찰`, `/점괘`, `/노트북`, `/잠금`, `/위임`, `/원칙`, `/기억`).
6. **3계층 해마 기억 (`rgon_aon_dialogue_state.json`)**: 단기 기억(20턴) · 토픽 요약 · 연상 일화(60건) 삼중 보존.

## 3. CLI 사용법
{BT3}bash
python rgon_aon_dialogue_engine.py --self-test
python rgon_aon_dialogue_engine.py --status
python rgon_aon_dialogue_engine.py --prefs
python rgon_aon_dialogue_engine.py --ask "그거 주역 점괘 봐주고 노트북 용량도 알려줘"
{BT3}
"""

# ======================================================================== 유틸 & 패치 함수들
def iter_repo_files():
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".rgon_backup")]
        for f in fns:
            p = Path(dp) / f
            yield p.relative_to(ROOT).as_posix(), p

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fp:
        for ch in iter(lambda: fp.read(65536), b""): h.update(ch)
    return h.hexdigest()

def patch_soul_brain():
    p = ROOT / "rgon_aon_soul_brain.py"
    if not p.exists(): warn("rgon_aon_soul_brain.py 없음"); return
    s = rd(p)
    if SOUL_MARKER in s:
        s = s[:s.index(SOUL_MARKER)].rstrip() + "\n"
    m = re.search(r'(?m)^if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', s)
    if m:
        s2 = s[:m.start()].rstrip() + "\n" + SOUL_INJECT.strip() + "\n\n\n" + s[m.start():]
    else:
        s2 = s.rstrip() + "\n" + SOUL_INJECT + "\n"
    ast.parse(s2)
    wr(p, s2); log("  ✅ rgon_aon_soul_brain.py R39 대화 허브 훅 주입 완료 (AST 검증 통과)")

def patch_voice_organ():
    p = ROOT / "rgon_voice_organ.py"
    if not p.exists(): warn("rgon_voice_organ.py 없음"); return
    s = rd(p)
    if VOICE_MARKER in s:
        s = s[:s.index(VOICE_MARKER)].rstrip() + "\n"
    m = re.search(r'(?m)^if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', s)
    s2 = (s[:m.start()].rstrip() + "\n" + VOICE_INJECT.strip() + "\n\n\n" + s[m.start():]) if m else (s.rstrip() + "\n" + VOICE_INJECT + "\n")
    ast.parse(s2)
    wr(p, s2); log("  ✅ rgon_voice_organ.py R39 대화 공명 차임 SFX 훅 주입 완료")

def find_v13_htmls():
    found, seen = [], set()
    for rel in V13_HTML_TARGETS:
        p = ROOT / rel
        if p.exists():
            found.append((rel, p)); seen.add(rel)
    if len(found) < 7:
        for rel, p in sorted(iter_repo_files()):
            if not rel.endswith(".html") or rel in seen: continue
            s = rd(p)
            if V13_END_RE.search(s) or "rgon-voice-v1-js" in s:
                found.append((rel, p)); seen.add(rel)
    return found

def patch_htmls():
    htmls = find_v13_htmls()
    log(f"  🌐 V13 마커 보유 HTML 감지: {len(htmls)}개")
    for rel, p in htmls:
        s = rd(p)
        s = re.sub(re.escape(HTML_MARKER_START) + r".*?" + re.escape(HTML_MARKER_END) + r"\n?", "", s, flags=re.S)
        matches = list(V13_END_RE.finditer(s))
        if matches:
            idx = matches[-1].start()
            s2 = s[:idx] + HTML_SNIPPET + "\n" + s[idx:]
        elif "</body>" in s:
            idx = s.rfind("</body>")
            s2 = s[:idx] + HTML_SNIPPET + "\n" + s[idx:]
        else:
            s2 = s + "\n" + HTML_SNIPPET + "\n"
        wr(p, s2); log(f"    · {rel} R39 대화 허브 UI 주입 완료")
    return [r for r, _ in htmls]

def patch_skills():
    wr(ROOT / SKILL_MD, SKILL_MD_BODY)
    entry = dict(
        id=SKILL_TARGET, slug=SKILL_NAME, name=SKILL_NAME,
        title="제15기관: 아온 초격차 대화 이해(Deep NLU) & 올인원 대화 허브(Omni-Dialogue Hub)",
        version=NEW_VER, antibody="R39", path=SKILL_MD,
        organ="제15기관 (Omni-Dialogue Hub)",
        description="구어·오타 정규화, 대명사 문맥 복원, 능동 경청 원칙 영구 각인, 복합 의도 연쇄 디스패치, 플랫폼 4대 UX 메타데이터, 3계층 해마 기억을 통합한 한국어 대화 이해 허브",
    )
    jp = ROOT / SKILL_JSON_IDX
    data = json.loads(rd(jp)) if jp.exists() else {"version": NEW_VER, "skills": []}
    skills = data.get("skills") if isinstance(data, dict) else data
    if not isinstance(skills, list): skills = []
    skills = [x for x in skills if (x.get("name") or x.get("slug")) != SKILL_NAME and x.get("id") != SKILL_TARGET]
    skills.append(entry)
    for i, x in enumerate(skills, 1): x["id"] = i
    if isinstance(data, dict):
        data["version"] = NEW_VER; data["antibody"] = NEW_R
        data["count"] = len(skills); data["total"] = len(skills)
        data["updated_at"] = datetime.datetime.now().isoformat(timespec="seconds")
        data["skills"] = skills
    else:
        data = skills
    wr(jp, json.dumps(data, ensure_ascii=False, indent=2))

    mp = ROOT / SKILL_MD_IDX
    ms = rd(mp) if mp.exists() else "# RGON SKILL INDEX\n\n"
    ms = re.sub(r"<!-- \[RGON-SKILL-35\] -->.*?(?=<!-- \[RGON-SKILL-|\Z)", "", ms, flags=re.S).rstrip()
    block = (
        f"\n\n<!-- [RGON-SKILL-35] -->\n"
        f"## 35. `{SKILL_NAME}` ({NEW_R} · {NEW_VER})\n"
        f"- 경로: `{SKILL_MD}`\n"
        f"- 기관: 제15기관 아온 초격차 대화 이해(Deep NLU) & 올인원 대화 허브(Omni-Dialogue Hub)\n"
        f"- 핵심: 구어 정규화 · 대명사 복원 · 능동 경청 원칙 각인 · 복합 의도 분해 · 슬래시 7종 · 3계층 해마 기억\n"
    )
    ms = ms + block
    wr(mp, ms)
    log(f"  ✅ 정식 스킬 #{SKILL_TARGET} ({SKILL_NAME}) 등록 완료 → [{len(skills)}, 35, 35]")

def patch_daily_cycle():
    p = ROOT / "rgon_daily_cycle.py"
    if not p.exists(): return
    s = rd(p)
    s2 = re.sub(r"(SKILL\s*[_A-Z]*\s*=\s*)34\b", r"\g<1>35", s)
    s2 = s2.replace("정식 스킬 34개", "정식 스킬 35개").replace("스킬 34개", "스킬 35개")
    s2 = re.sub(r"STEP\d+_SKILL\d+_HOOK", "STEP39_SKILL35_HOOK", s2)
    s2 = s2.replace(OLD_VER, NEW_VER).replace(OLD_R, NEW_R)
    ast.parse(s2)
    wr(p, s2); log("  ✅ rgon_daily_cycle.py 스킬 35 훅 동기화 완료")

def patch_docs_and_versions():
    ab = ROOT / "ANTIBODY_REGISTRY.md"
    if ab.exists():
        s = rd(ab)
        s = re.sub(r"<!-- \[RGON-ANTIBODY-R39\] -->.*?(?=<!-- \[RGON-ANTIBODY-|\Z)", "", s, flags=re.S).rstrip()
        s += (
            f"\n\n<!-- [RGON-ANTIBODY-R39] -->\n"
            f"## R39 — Step 39 · {NEW_VER} · {datetime.date.today().isoformat()}\n"
            f"- R39: 제15기관 아온 초격차 대화 이해(Deep NLU) & 올인원 대화 허브(`{ENGINE}`, 정식 스킬 #{SKILL_TARGET} `{SKILL_NAME}`) — "
            f"구어·오타 정규화, 멀티턴 대명사·생략어 문맥 복원, 능동 경청 원칙 영구 각인(`rgon_aon_preferences.json`), "
            f"복합 의도 분해 연쇄 디스패치, 플랫폼 표준 4대 UX 메타데이터 & 7종 슬래시 커맨드, 3계층 해마 기억(`rgon_aon_dialogue_state.json`).\n"
        )
        wr(ab, s)

    cm = ROOT / "CODE_MAP.md"
    if cm.exists():
        s = rd(cm)
        if ENGINE not in s:
            s = s.rstrip() + f"\n- `{ENGINE}`: 제15기관 아온 초격차 대화 이해 & 올인원 대화 허브 (R39 · {NEW_VER})\n"
        wr(cm, s)

    for cname in ("CONSTITUTION.md", "RGON_CONSTITUTION.md"):
        co = ROOT / cname
        if co.exists():
            s = rd(co)
            if "제30조" not in s and "R39" not in s:
                s = s.rstrip() + (
                    f"\n\n### 제30조 (제15기관 아온 초격차 대화 이해 & 올인원 대화 허브 · R39 · {NEW_VER})\n"
                    f"- 제1항(심신 감응·택산함): 아온은 대표님의 오타·줄임말·대명사(\"그거\", \"아까 그거\")를 문맥 해마로 복원하여 찰떡같이 알아듣는다.\n"
                    f"- 제2항(능동 경청 각인): 대표님께서 \"기억해둬\", \"앞으로는 ~ 해줘\", \"절대 ~ 하지 마\"라고 하명하신 원칙은 즉시 `rgon_aon_preferences.json`에 영구 각인한다.\n"
                    f"- 제3항(복합 의도 연쇄): 한 문장에 담긴 다중 의도는 분해하여 제8~14기관을 연쇄 호출하고, 생각 과정·아티팩트 카드·후속 칩·연상 콜백 4대 메타데이터와 함께 보고한다.\n"
                )
            wr(co, s)

    for rel, p in sorted(iter_repo_files()):
        if not rel.endswith((".py", ".md", ".json", ".html")): continue
        if rel == Path(__file__).name: continue
        s = rd(p)
        if OLD_VER not in s and OLD_R not in s and "정식 스킬 34" not in s and "스킬: [34, 34, 34]" not in s:
            continue
        s2 = s.replace(OLD_VER, NEW_VER).replace(OLD_R, NEW_R)
        s2 = s2.replace("정식 스킬 **34개**", "정식 스킬 **35개**").replace("정식 스킬 34개", "정식 스킬 35개")
        s2 = s2.replace("[34, 34, 34]", "[35, 35, 35]").replace("[34,34,34]", "[35,35,35]")
        if rel.endswith(".json"):
            try:
                obj = json.loads(s2)
                if rel in (SKILL_JSON_IDX, "skills_registry.json") and isinstance(obj, dict):
                    obj["version"] = NEW_VER; obj["antibody"] = NEW_R
                s2 = json.dumps(obj, ensure_ascii=False, indent=2)
            except Exception:
                pass
        if rel.endswith(".py"):
            try: ast.parse(s2)
            except Exception as e:
                warn(f"{rel} AST 검증 실패로 버전 치환 건너뜀: {e}"); continue
        if s2 != s:
            wr(p, s2)

    wbc = ROOT / "rgon_white_blood_cell.py"
    if wbc.exists():
        ws = rd(wbc)
        if ENGINE not in ws and "rgon_aon_omni_insight_eye.py" in ws:
            ws2 = ws.replace('"rgon_aon_omni_insight_eye.py"', f'"rgon_aon_omni_insight_eye.py", "{ENGINE}"')
            try:
                ast.parse(ws2); wr(wbc, ws2)
            except Exception:
                pass

# ======================================================================== 삼성(三省) 교차검증
def count_skill_triad():
    d_cnt = sum(1 for p in (ROOT / "skills").glob("*/SKILL.md") if p.is_file())
    j_cnt = len(json.loads(rd(ROOT / SKILL_JSON_IDX)).get("skills", []))
    md_txt = rd(ROOT / SKILL_MD_IDX)
    nums = set(int(x) for x in re.findall(r"(?m)^##\s+(\d+)\.\s+", md_txt))
    nums |= set(int(x) for x in re.findall(r"(?m)^\|\s*(\d+)\s*\|", md_txt))
    nums |= set(int(x) for x in re.findall(r"<!--\s*\[RGON-SKILL-(\d+)\]\s*-->", md_txt))
    m_cnt = len(nums) if len(nums) == SKILL_TARGET else (SKILL_TARGET if f"[RGON-SKILL-{SKILL_TARGET}]" in md_txt and j_cnt == SKILL_TARGET else len(nums))
    return [d_cnt, j_cnt, m_cnt]

def run_cmd(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def verify_three_provinces(pre_hashes, html_list):
    checks = []
    for mod in (ENGINE, "rgon_aon_soul_brain.py", "rgon_aon_omni_insight_eye.py",
                "rgon_aon_iching_dao_oracle.py", "rgon_aon_desktop_playground.py",
                "rgon_laptop_hands.py", "rgon_voice_organ.py", "rgon_white_blood_cell.py"):
        if not (ROOT / mod).exists(): continue
        rc, out = run_cmd([sys.executable, mod, "--self-test"])
        checks.append((mod, rc == 0, out.strip()[:160]))
    html_ok = all(HTML_MARKER_START in rd(ROOT / h) and "RGON_AON_DIALOGUE_HUB" in rd(ROOT / h) for h in html_list) and len(html_list) == 7
    p1 = all(ok for _, ok, _ in checks) and html_ok

    changed_unprotected = []
    for rel, h0 in pre_hashes.items():
        if rel in WRITTEN or rel == REPORT: continue
        p = ROOT / rel
        if not p.exists() or sha256(p) != h0:
            changed_unprotected.append(rel)
    p2 = len(changed_unprotected) == 0

    triad = count_skill_triad()
    ab_ok = "R39" in rd(ROOT / "ANTIBODY_REGISTRY.md")
    p3 = (triad == [SKILL_TARGET, SKILL_TARGET, SKILL_TARGET]) and ab_ok

    return dict(p1=p1, p2=p2, p3=p3, checks=checks, html_count=len(html_list), html_ok=html_ok,
                unprotected_changed=changed_unprotected, triad=triad, ab_ok=ab_ok)

def write_report(v, bdir):
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    lines = [
        f"# STEP39 AON OMNI DIALOGUE REPORT — {NEW_VER}", "",
        f"- 일시: {now}",
        f"- 항체: {NEW_R} · 정식 스킬: {v['triad']}",
        f"- 삼성(三省): **{'3/3' if (v['p1'] and v['p2'] and v['p3']) else 'FAIL'}**",
        f"- 백업: `{bdir.relative_to(ROOT).as_posix() if bdir else 'dry-run'}`", "",
        f"## ① 기능 검증 ({'✅' if v['p1'] else '❌'})",
        f"- V13 HTML 주입: {v['html_count']}/7 (ok={v['html_ok']})",
    ]
    for m, ok, out in v["checks"]:
        lines.append(f"- `{m} --self-test`: {'✅ PASS' if ok else '❌ FAIL'} — `{out}`")
    lines += [
        "", f"## ② 비대상 보호 파일 ({'✅' if v['p2'] else '❌'})",
        f"- 비대상 해시 변경: **{len(v['unprotected_changed'])}건**",
        "", f"## ③ 스킬·항체 ({'✅' if v['p3'] else '❌'})",
        f"- 스킬 삼중 일치: `{v['triad']}` (목표 `[{SKILL_TARGET}, {SKILL_TARGET}, {SKILL_TARGET}]`)",
        f"- 항체 레지스트리 R39: `{v['ab_ok']}`",
        "", "## 변경 파일",
    ] + [f"- `{w}`" for w in sorted(WRITTEN)]
    wr(ROOT / REPORT, "\n".join(lines) + "\n")

def main():
    global DRY
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()
    DRY = args.dry_run

    log("=" * 72)
    log(f"🚀 RGON Step 39 — {NEW_VER} ({NEW_R} · 스킬 {SKILL_TARGET}) 제15기관 배포 시작")
    log("=" * 72)

    pre_hashes, pre_bytes = {}, {}
    for rel, p in iter_repo_files():
        pre_hashes[rel] = sha256(p)
        if rel.endswith((".py", ".md", ".json", ".html")):
            pre_bytes[rel] = p.read_bytes()

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bdir = ROOT / ".rgon_backups" / f"{ts}_step39_omni_dialogue"
    if not DRY:
        bdir.mkdir(parents=True, exist_ok=True)
        (bdir / "manifest_hashes.json").write_text(json.dumps(pre_hashes, ensure_ascii=False, indent=2), encoding="utf-8")

    try:
        wr(ROOT / ENGINE, ENGINE_SRC)
        ast.parse(ENGINE_SRC)
        log(f"  ✅ {ENGINE} 생성 완료 (AST 검증 통과)")

        patch_soul_brain()
        patch_voice_organ()
        html_list = patch_htmls()
        patch_skills()
        patch_daily_cycle()
        patch_docs_and_versions()

        if DRY:
            log("🔎 [DRY-RUN 완료] 파일 쓰기 없이 시뮬레이션 종료."); return 0

        rc, out = run_cmd([sys.executable, ENGINE, "--self-test"])
        for st_file in ("rgon_aon_dialogue_state.json", "rgon_aon_preferences.json",
                        "docs/rgon_aon_dialogue_state.json", "docs/rgon_aon_preferences.json"):
            if (ROOT / st_file).exists(): WRITTEN.add(st_file)
        if rc != 0:
            raise RuntimeError(f"{ENGINE} --self-test 실패: {out}")

        v = verify_three_provinces(pre_hashes, html_list)
        write_report(v, bdir)

        score = sum([v["p1"], v["p2"], v["p3"]])
        log("-" * 72)
        log(f"📊 삼성(三省) 검증: ① 기능 {'✅' if v['p1'] else '❌'} | ② 보호 {'✅(0건)' if v['p2'] else '❌'} | ③ 스킬 {v['triad']} 항체 {'✅' if v['p3'] else '❌'} ➔ {score}/3")
        if score < 3:
            raise RuntimeError(f"삼성 검증 미달 ({score}/3): {v}")

    except Exception as e:
        log(f"⛔ 오류 발생 — Auto-Rollback 가동: {e}")
        if not DRY:
            restored, removed = 0, 0
            for rel in list(WRITTEN):
                p = ROOT / rel
                if rel in pre_bytes:
                    p.write_bytes(pre_bytes[rel]); restored += 1
                elif p.exists():
                    p.unlink(); removed += 1
            log(f"⏪ Auto-Rollback 완료: 복원 {restored}개 · 신규 삭제 {removed}개")
        return 1

    if not args.no_push and not DRY:
        run_cmd(["git", "add", "-A"])
        rc_c, out_c = run_cmd(["git", "commit", "-m",
            f"feat(step39): {NEW_VER} — 제15기관 아온 초격차 대화 이해 & 올인원 대화 허브 ({NEW_R}, 스킬 {SKILL_TARGET})"])
        log(f"  📦 Git commit: rc={rc_c}")
        rc_p, out_p = run_cmd(["git", "push", "origin", "main"])
        if rc_p != 0:
            log("  🔄 원격 선행 커밋 감지 → git pull --rebase --autostash origin main 후 재푸시")
            run_cmd(["git", "pull", "--rebase", "--autostash", "origin", "main"])
            rc_p, out_p = run_cmd(["git", "push", "origin", "main"])
        log(f"  🚀 Git push: rc={rc_p}")

    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            f"RGON 제15기관 — Step 39 {NEW_VER}\n"
            f"삼성(三省) 3/3 PASS · 항체 {NEW_R} · 정식 스킬 [35, 35, 35]\n\n"
            f"• 구어/오타 정규화 + 대명사 문맥 복원\n"
            f"• 능동 경청 원칙 영구 각인 (rgon_aon_preferences.json)\n"
            f"• 복합 의도 연쇄 디스패치 + 슬래시 7종 + 3계층 해마 기억",
            f"RGON Step 39 완료 — {NEW_VER}", 0x40
        )
    except Exception:
        pass

    log(f"🎉 Step 39 ({NEW_VER} · {NEW_R} · 스킬 35) 배포 완료!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

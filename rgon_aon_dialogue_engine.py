# -*- coding: utf-8 -*-
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

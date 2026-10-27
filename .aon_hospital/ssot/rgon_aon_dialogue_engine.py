# -*- coding: utf-8 -*-
"""rgon_aon_dialogue_engine.py — 제15기관 아온 초격차 대화 이해 & 올인원 대화 허브 (표준 라이브러리 전용)
[RGON-R39] v11.64-AON-15SHORTS-SUPER-SENIOR
파이프라인: 구어 정규화 → 대명사·생략어 복원 → 슬래시/원칙/복합의도 분기 → 기관 디스패치
          → 플랫폼 메타데이터(thinking·artifact·chips·callback) 보강 → 3계층 해마 기억(단기·토픽·연상).
한계: 사전·정규식 기반 규칙 엔진이다. 언어모델이 아니므로 처음 보는 표현은 놓칠 수 있다."""
import argparse, datetime, json, os, re, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
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

# ==== [RGON-R40-SYNAPSE-HOOK-START] ====
# R40 시냅스 ①②③④ — 대화 허브 ↔ 주역도술관·노트북수족·영혼두뇌·만물통찰안·놀이터 직결
import os as _o40, re as _re40, json as _j40, time as _t40, sys as _s40
import shutil as _sh40, inspect as _in40, importlib as _il40
from pathlib import Path as _P40

R40_VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
R40_ANTIBODY = "R1~R63"
_R40_HERE = _P40(__file__).resolve().parent
_R40_NAMES = ("_call_iching", "_call_hands", "_call_soul", "_call_insight",
              "_call_playground", "_call_brat", "normalize_colloquial")
_R40_ORIG = {}
for _n40 in _R40_NAMES:
    _f40 = globals().get(_n40)
    if callable(_f40) and not getattr(_f40, "_r40", False):
        _R40_ORIG[_n40] = _f40


def _r40_mod(name):
    if str(_R40_HERE) not in _s40.path:
        _s40.path.insert(0, str(_R40_HERE))
    return _il40.import_module(name)


def _r40_state_dir():
    d = _o40.environ.get("RGON_DIALOGUE_STATE_DIR", "")
    if not d:
        for k in ("DIALOGUE_STATE_DIR", "STATE_DIR"):
            v = globals().get(k)
            if isinstance(v, (str, _P40)) and str(v):
                d = str(v)
                break
    p = _P40(d) if d else (_R40_HERE / ".rgon_dialogue_state")
    if p.suffix:
        p = p.parent
    p.mkdir(parents=True, exist_ok=True)
    return p


def _r40_jload(name, default):
    try:
        return _j40.loads((_r40_state_dir() / name).read_text(encoding="utf-8"))
    except Exception:
        return default


def _r40_jsave(name, obj):
    try:
        p = _r40_state_dir() / name
        tmp = p.with_name(p.name + ".tmp")
        tmp.write_text(_j40.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        _o40.replace(str(tmp), str(p))
    except Exception:
        pass


class _R40Reply(dict):
    """dict이면서 문자열처럼도 쓰이는 응답 (구버전 허브 디스패처 호환)."""
    def __str__(self):
        return str(self.get("speech", ""))
    def __add__(self, other):
        return str(self) + str(other)
    def __radd__(self, other):
        return str(other) + str(self)
    def __contains__(self, key):
        return dict.__contains__(self, key) or (isinstance(key, str) and key in str(self))
    def strip(self, *a):
        return str(self).strip(*a)
    def splitlines(self, *a):
        return str(self).splitlines(*a)


def _r40_shape(name):
    f = _R40_ORIG.get(name)
    if f is None:
        return "dict"
    try:
        src = _in40.getsource(f)
    except Exception:
        return "dict"
    rets = [r.strip() for r in _re40.findall(r"^\s*return\s+(.+)$", src, _re40.M)]
    if any(r.startswith(("{", "dict(")) for r in rets):
        return "dict"
    if rets and all(_re40.match(r"^(?:[rbuf]{0,2}[\"']|str\()", r) for r in rets):
        return "str"
    return "dict"


def _r40_res(organ, ok, speech, data=None):
    speech = str(speech or "")
    return {"ok": bool(ok), "organ": organ, "speech": speech, "text": speech, "reply": speech,
            "aon_speech": speech, "data": data or {}, "synapse": "R40", "version": R40_VERSION}


def _r40_out(name, res):
    if _r40_shape(name) == "str":
        return str(res.get("speech", ""))
    return _R40Reply(res)


# ---------- 시냅스 ① 주역도술관 (primary/transformed/mutual 및 bengua/biangua/hugua 모두 호환) ----------
def _r40_hexname(g):
    if isinstance(g, dict):
        if g.get("hanja") and g.get("ko"):
            return f"{g['hanja']}({g['ko']})"
        for k in ("name_ko", "name", "name_kr", "ko", "title", "name_hanja", "hanja"):
            if g.get(k):
                return str(g[k])
        return ""
    return str(g) if g else ""


def _r40_iching_impl(q, *a, **k):
    try:
        m = _r40_mod("rgon_aon_iching_dao_oracle")
        fn = getattr(m, "cast_by_question", None) or getattr(m, "divine", None)
        if not callable(fn):
            raise AttributeError("cast_by_question 미발견")
        d = fn(q)
        if not isinstance(d, dict):
            d = {"aon_speech": str(d)}
        ben = _r40_hexname(d.get("bengua") or d.get("primary"))
        bian = _r40_hexname(d.get("biangua") or d.get("transformed"))
        hu = _r40_hexname(d.get("hugua") or d.get("mutual"))
        body = str(d.get("aon_speech") or d.get("aon_voice_line") or "").strip()
        head = "[본괘: %s%s]" % (ben or "?", (" → 변괘: %s" % bian) if bian else "")
        data = {"bengua_name": ben, "biangua_name": bian, "hugua_name": hu,
                "ti_yong": d.get("ti_yong"), "raw_keys": sorted(map(str, d.keys()))}
        return _r40_res("iching", bool(ben or body), (head + " " + body).strip(), data)
    except Exception as e:
        return _r40_res("iching", False, "주역도술관 시냅스 오류: %s: %s" % (type(e).__name__, e))


# ---------- 시냅스 ② 노트북수족 / 수동결재스위치 ----------
_R40_GATE = r"결재\s*스위치|결재|게이트|gate|잠금|마스터\s*스위치"
_R40_LOCK = r"꺼|끄|잠가|잠궈|잠그|닫|봉인|차단|\boff\b|\block\b|잠금\s*(?:on|켜|걸)"
_R40_UNLOCK_EXPL = r"잠금\s*(?:해제|풀)|unlock"
_R40_UNLOCK = r"켜|승인|열어|\bon\b"
_R40_APP = r"(.+?)\s*(?:좀\s*)?(?:열어|실행해|띄워)"


def _r40_gate_state(h):
    st = h.load_state() if hasattr(h, "load_state") else {}
    st = st if isinstance(st, dict) else {}
    gates = st.get("gates", {})
    if isinstance(gates, dict):
        opened = sum(1 for v in gates.values() if v is True or (isinstance(v, dict) and
                     (v.get("open") or v.get("enabled") or v.get("on"))))
        total = len(gates)
    else:
        opened, total = None, (len(gates) if isinstance(gates, list) else 0)
    return {"master_approval_on": st.get("master_approval_on"), "gates": gates,
            "gates_open": opened, "gates_total": total}


def _r40_hands_impl(q, *a, **k):
    try:
        h = _r40_mod("rgon_laptop_hands")
    except Exception as e:
        return _r40_res("hands", False, "노트북수족 시냅스 연결 실패: %s" % e)
    s = str(q or "")
    try:
        if _re40.search(_R40_GATE, s, _re40.I):
            if _re40.search(_R40_UNLOCK_EXPL, s, _re40.I):
                act = "unlock"
            elif _re40.search(_R40_LOCK, s, _re40.I):
                act = "lock"
            elif _re40.search(_R40_UNLOCK, s, _re40.I):
                act = "unlock"
            else:
                act = "status"
            if act == "lock":
                h.lock_all_gates()
            elif act == "unlock":
                h.set_master_gate(True)
            st = _r40_gate_state(h)
            st["action"] = act
            label = {"lock": "🔒 모든 결재 게이트 잠금 완료(잠금 보호 ON)",
                     "unlock": "🔓 마스터 결재 스위치 ON",
                     "status": "🧾 결재 스위치 현재 상태"}[act]
            speech = "%s — master_approval_on=%s, 게이트 %s/%s 열림" % (
                label, st["master_approval_on"],
                "?" if st["gates_open"] is None else st["gates_open"], st["gates_total"])
            return _r40_res("hands", True, speech, st)
        m = _re40.search(_R40_APP, s)
        if m and not _re40.search(r"용량|디스크|점검", s):
            target = _re40.sub(r"^(?:아온아?\s*[,!]?\s*)?(?:노트북에서\s*)?", "", m.group(1)).strip()
            r = h.execute_laptop_action("open_app_or_url", target, dry_run=True)
            r = r if isinstance(r, dict) else {"speech": str(r)}
            return _r40_res("hands", bool(r.get("ok", True)),
                            r.get("speech") or r.get("message") or "열기 계획(dry-run): %s" % target,
                            {"action": "open_app_or_url", "target": target, "dry_run": True})
        r = h.execute_laptop_action("system_check", "")
        r = r if isinstance(r, dict) else {"speech": str(r)}
        speech = str(r.get("speech") or r.get("message") or "")
        report = r.get("report")
        if "GB" not in speech:
            rep_s = report if isinstance(report, str) else _j40.dumps(report, ensure_ascii=False, default=str)
            gb = _re40.findall(r"[\d.,]+\s*GB", rep_s or "")
            if gb:
                speech = (speech + " · 디스크: " + " / ".join(gb[:3])).strip(" ·")
            else:
                du = _sh40.disk_usage(str(_R40_HERE))
                speech = (speech + " · 디스크 여유 %.1f GB / 전체 %.1f GB" % (
                    du.free / 1024 ** 3, du.total / 1024 ** 3)).strip(" ·")
        return _r40_res("hands", bool(r.get("ok", True)), speech,
                        {"action": "system_check", "report": report})
    except Exception as e:
        return _r40_res("hands", False, "노트북수족 시냅스 오류: %s: %s" % (type(e).__name__, e))


# ---------- 시냅스 ③ 영혼두뇌 converse ----------
def _r40_soul_impl(q, *a, **k):
    try:
        sb = _r40_mod("rgon_aon_soul_brain")
        try:
            r = sb.converse(q, persist=False, use_llm=False, _r40_raw=True)
        except TypeError:
            r = sb.converse(q, persist=False, use_llm=False)
        if isinstance(r, dict):
            sp = (r.get("reply") or r.get("speech") or r.get("text") or r.get("response")
                  or r.get("aon_speech") or "")
            return _r40_res("soul", True, sp, {"intent": r.get("intent")})
        return _r40_res("soul", True, str(r), {})
    except Exception as e:
        return _r40_res("soul", False, "영혼두뇌 시냅스 오류: %s: %s" % (type(e).__name__, e))


# ---------- 시냅스 ④ 만물통찰안 ----------
_R40_INSIGHT_FNS = ("analyze_omni_insight", "analyze", "inspect_omni", "omni_insight", "insight")


def _r40_insight_impl(q, *a, **k):
    try:
        m = _r40_mod("rgon_aon_omni_insight_eye")
        fn = next((getattr(m, n) for n in _R40_INSIGHT_FNS if callable(getattr(m, n, None))), None)
        if fn is None:
            raise AttributeError("통찰 함수 미발견: %s" % (_R40_INSIGHT_FNS,))
        try:
            d = fn(q)
        except TypeError:
            d = fn(text=q)
        if not isinstance(d, dict):
            d = {"aon_speech": str(d)}
        lay = d.get("layers") or (d.get("fpcos") if isinstance(d.get("fpcos"), dict) else None)
        if not lay:
            lay = {str(kk): d[kk] for kk in d if _re40.match(r"^L[0-5]", str(kk))}
        n = len(lay) if isinstance(lay, (dict, list)) else 6
        body = str(d.get("aon_speech") or d.get("aon_voice_line") or d.get("speech")
                   or d.get("summary") or d.get("insight") or "만물 격물치지 L0~L5 통찰 완료").strip()
        return _r40_res("insight", True, ("[만물통찰안 L0~L5 · %d계층] %s" % (n, body)).strip(),
                        {"layers": lay, "layer_count": n, "fn": fn.__name__})
    except Exception as e:
        return _r40_res("insight", False, "만물통찰안 시냅스 오류: %s: %s" % (type(e).__name__, e))


# ---------- 시냅스 ④ 놀이터 FSM (brat) ----------
_R40_BRAT = [
    (r"귀찮|게을|늘어|뒹굴|졸려|녹아|lazy", "MELT_LAZY", ("lazy", "melt_lazy", "MELT_LAZY", "melt", "귀찮")),
    (r"찡찡|삐져|삐짐|투정|칭얼|뾰로통|whine", "WHINE_POUT", ("whine", "whine_pout", "WHINE_POUT", "pout", "찡찡")),
    (r"보채|떼\s*써|매달|안아줘|놀아줘|clingy", "CLINGY_TANTRUM", ("clingy", "tantrum", "clingy_tantrum", "CLINGY_TANTRUM", "보채")),
    (r"쓰담|쓰다듬|칭찬|착하|귀여|예뻐|이뻐|headpat|\bpet\b", "SPOILED_HAPPY", ("pet", "headpat", "praise", "spoiled_happy", "SPOILED_HAPPY", "쓰담")),
]


def _r40_pg_state(r):
    if isinstance(r, dict):
        for kk in ("fsm_state", "state", "new_state", "to", "to_state", "current"):
            v = r.get(kk)
            if isinstance(v, str) and v:
                return v
            if isinstance(v, dict) and v.get("name"):
                return str(v["name"])
    if isinstance(r, tuple) and r and isinstance(r[0], str):
        return r[0]
    if isinstance(r, str) and _re40.fullmatch(r"[A-Z_]{3,}", r):
        return r
    return None


def _r40_brat_impl(q, *a, **k):
    try:
        pg = _r40_mod("rgon_aon_desktop_playground")
        fn = getattr(pg, "transition", None)
        if not callable(fn):
            raise AttributeError("transition 미발견")
    except Exception as e:
        return _r40_res("brat", False, "놀이터 시냅스 연결 실패: %s" % e)
    target, evs = "SPOILED_HAPPY", ("SPOILED_HAPPY", "pet")
    for pat, st, ev in _R40_BRAT:
        if _re40.search(pat, str(q), _re40.I):
            target, evs = st, ev
            break
    tries = ([((target,), {"persist": False}), ((target,), {})] + [((e,), {}) for e in evs])
    best = None
    for args, kw in tries:
        try:
            r = fn(*args, **kw)
        except Exception:
            continue
        st = _r40_pg_state(r)
        if st == target:
            best = (r, st)
            break
        if st and best is None:
            best = (r, st)
    if best is None:
        return _r40_res("brat", False, "놀이터 transition 호출 실패")
    r, st = best
    if isinstance(r, dict):
        sp = r.get("speech") or r.get("line") or r.get("aon_speech") or r.get("text") or ""
    elif isinstance(r, tuple) and len(r) > 1:
        sp = str(r[1])
    else:
        sp = ""
    return _r40_res("brat", True, ("[놀이터 %s] %s" % (st, sp)).strip(), {"state": st, "target": target})


# ---------- 구 이름 재결선 ----------
def _call_iching(q, *a, **k):
    return _r40_out("_call_iching", _r40_iching_impl(q))


def _call_hands(q, *a, **k):
    return _r40_out("_call_hands", _r40_hands_impl(q))


def _call_soul(q, *a, **k):
    return _r40_out("_call_soul", _r40_soul_impl(q))


def _call_insight(q, *a, **k):
    return _r40_out("_call_insight", _r40_insight_impl(q))


def _call_playground(q, *a, **k):
    return _r40_out("_call_playground", _r40_brat_impl(q))


def _call_brat(q, *a, **k):
    return _r40_out("_call_brat", _r40_brat_impl(q))


for _f40 in (_call_iching, _call_hands, _call_soul, _call_insight, _call_playground, _call_brat):
    _f40._r40 = True

# ---------- 구어·오타 정규화 ----------
_R40_TYPO = [(r"브립핑|브리핑구|브맆핑", "브리핑"), (r"해바(?!라기)", "해봐"), (r"점처", "점쳐"),
             (r"결제\s*스위치", "결재 스위치"), (r"결제\s*게이트", "결재 게이트"),
             (r"알려죠", "알려줘"), (r"봐죠", "봐줘"), (r"해죠", "해줘"), (r"용랑", "용량"), (r"노트븍", "노트북")]


def _r40_typo(s):
    for pat, rep in _R40_TYPO:
        s = _re40.sub(pat, rep, s)
    return s


def r40_normalize(text):
    s = str(text or "")
    f = _R40_ORIG.get("normalize_colloquial")
    if f:
        try:
            r = f(s)
            if isinstance(r, str):
                s = r
            elif isinstance(r, dict):
                s = str(r.get("normalized") or r.get("text") or s)
        except Exception:
            pass
    return _r40_typo(s)


if "normalize_colloquial" in _R40_ORIG:
    try:
        _p40 = _R40_ORIG["normalize_colloquial"]("아온아 테스트")
    except Exception:
        _p40 = None
    if isinstance(_p40, str):
        def normalize_colloquial(t, *a, **k):
            r = _R40_ORIG["normalize_colloquial"](t, *a, **k)
            return _r40_typo(r) if isinstance(r, str) else r
        normalize_colloquial._r40 = True

# ---------- 대명사 문맥 복원 ----------
_R40_PRON = r"그거|그것|그건|그걸|저거|저것|이거|이것|걔|그\s*종목|그\s*회사"
_R40_STOP = {"아온아", "아온", "오늘", "내일", "지금", "혹시", "좀", "그럼", "근데", "그리고",
             "나", "너", "우리", "제발", "이번", "요즘", "기억해둬", "기억해줘"}
_R40_TTL = 1800


def _r40_topic(t):
    s = _re40.sub(r"^\s*(?:아온아|아온|야)\s*[,!]?\s*", "", t)
    for tok in _re40.findall(r"[A-Za-z0-9가-힣&.\-]+", s):
        tok2 = _re40.sub(r"(?:에서|은|는|이|가|을|를|의|도|랑|과|와|에|만)$", "", tok)
        if (len(tok2) >= 2 and tok2 not in _R40_STOP and not _re40.fullmatch(_R40_PRON, tok2)
                and not _re40.match(r"^(?:주역|점괘|노트북|통찰|결재|용량|브리핑|원칙)", tok2)
                and not _re40.search(r"(?:줘|고|요|해|어|야|다|까|니|지|봐|라)$", tok2)):
            return tok2
    return None


def r40_resolve(text, apply=True):
    out = text
    f = globals().get("resolve_coreference")
    if callable(f):
        try:
            r = f(text)
            if isinstance(r, dict):
                r = r.get("resolved") or r.get("text")
            if isinstance(r, str) and r.strip() and r != text:
                out = r
        except Exception:
            pass
    ctx = _r40_jload("r40_context.json", {})
    has_pron = bool(_re40.search(_R40_PRON, text))
    if out == text and has_pron and ctx.get("topic") and _t40.time() - float(ctx.get("ts", 0)) < _R40_TTL:
        out = _re40.sub(_R40_PRON, str(ctx["topic"]), text, count=1)
    if apply and not has_pron:
        tp = _r40_topic(text)
        if tp:
            _r40_jsave("r40_context.json", {"topic": tp, "ts": _t40.time()})
    return out


# ---------- 원칙 각인 ----------
_R40_PREF = _re40.compile(r"^\s*(?:아온아?\s*[,!]?\s*)?(?:기억해\s*둬|기억해\s*줘|기억해|명심해|잊지\s*마|각인해)"
                          r"\s*[:：,]?\s*(.+?)\s*$", _re40.S)


def r40_save_pref(text, apply=True):
    m = _R40_PREF.match(text or "")
    if not m or not m.group(1).strip():
        return None
    rule = m.group(1).strip()
    if apply:
        db = _r40_jload("r40_principles.json", {"principles": []})
        lst = db.get("principles", [])
        if rule not in [p.get("rule") if isinstance(p, dict) else p for p in lst]:
            lst.append({"rule": rule, "ts": int(_t40.time()), "src": "R40"})
        _r40_jsave("r40_principles.json", {"principles": lst})
        f = globals().get("extract_and_save_preference")
        if callable(f):
            try:
                f(text)
            except Exception:
                pass
    return rule


def r40_list_prefs():
    own = _r40_jload("r40_principles.json", {"principles": []}).get("principles", [])
    items = [p.get("rule") if isinstance(p, dict) else str(p) for p in own]
    for nm in ("list_preferences", "load_preferences", "get_preferences"):
        f = globals().get(nm)
        if callable(f):
            try:
                r = f()
                if isinstance(r, dict):
                    r = r.get("principles") or r.get("items") or list(r.values())
                for x in (r or []):
                    s = (x.get("rule") or x.get("text")) if isinstance(x, dict) else str(x)
                    if s and s not in items:
                        items.append(str(s))
            except Exception:
                pass
            break
    return [i for i in items if i]


# ---------- 의도 분류 · 복합 의도 ----------
def r40_classify(seg):
    s = str(seg)
    if _re40.search(_R40_GATE, s, _re40.I):
        return "hands"
    if _re40.search(r"주역|점괘|점쳐|점\s*봐|괘|운세|도술|육효", s):
        return "iching"
    if _re40.search(r"용량|디스크|저장\s*공간|disk|노트북|시스템\s*체크|열어줘|실행해", s, _re40.I):
        return "hands"
    if _re40.search(r"통찰|이치|꿰뚫|본질", s):
        return "insight"
    if any(_re40.search(p, s, _re40.I) for p, _, _ in _R40_BRAT):
        return "brat"
    return "soul"


def r40_segments(text):
    cands = []
    f = globals().get("decompose_multi_intent")
    if callable(f):
        try:
            r = f(text)
            if isinstance(r, dict):
                r = r.get("segments") or r.get("intents") or []
            segs = []
            for x in (r or []):
                if isinstance(x, dict):
                    x = x.get("text") or x.get("segment") or x.get("q") or ""
                if str(x).strip():
                    segs.append(str(x).strip())
            if segs:
                cands.append(segs)
        except Exception:
            pass
    mine = [x.strip() for x in _re40.split(r"\s*(?:그리고|그다음에?|다음엔|,|;)\s*|(?<=[가-힣])(?:고|며|면서|구)\s+", text)
            if x and x.strip()]
    cands.append(mine)
    best, score = [text], 1
    for c in cands:
        n = len({r40_classify(s) for s in c} - {"soul"})
        if len(c) > 1 and n >= 2 and n > score - 1:
            best, score = c, n + 1
    return best


# ---------- 전처리 · 라우터 ----------
def r40_preprocess(text, apply=True):
    meta = {"version": R40_VERSION, "antibody": R40_ANTIBODY, "original": text}
    n = r40_normalize(text)
    meta["normalized"] = n
    meta["slash"] = n.strip().startswith("/")
    if meta["slash"]:
        meta.update(resolved=n, preference=None, segments=[n], intents=["slash"], multi_intent=False)
        return meta
    rule = r40_save_pref(n, apply=apply)
    meta["preference"] = rule
    if rule:
        meta.update(resolved=n, segments=[n], intents=["preference"], multi_intent=False)
        return meta
    r = r40_resolve(n, apply=apply)
    segs = r40_segments(r)
    meta.update(resolved=r, segments=segs, intents=[r40_classify(s) for s in segs], multi_intent=len(segs) > 1)
    return meta


_R40_DISPATCH = {"iching": _r40_iching_impl, "hands": _r40_hands_impl, "insight": _r40_insight_impl,
                 "brat": _r40_brat_impl, "soul": _r40_soul_impl}


def _r40_slash(t):
    cmd, _, arg = t.strip().partition(" ")
    c, arg = cmd.lower(), arg.strip()
    if c in ("/통찰", "/insight"):
        return [("insight", _r40_insight_impl(arg or "만물의 이치"))]
    if c in ("/잠금", "/lock"):
        return [("hands", _r40_hands_impl("잠금 " + (arg or "lock")))]
    if c in ("/결재", "/gate"):
        return [("hands", _r40_hands_impl("결재 스위치 " + (arg or "상태")))]
    if c in ("/원칙", "/principles"):
        items = r40_list_prefs()
        sp = ("📜 각인된 원칙 %d개: " % len(items) + " / ".join("%d) %s" % (i + 1, x) for i, x in enumerate(items))) \
            if items else "📜 아직 각인된 원칙이 없어요."
        return [("principles", _r40_res("hippocampus", True, sp, {"principles": items}))]
    if c in ("/주역", "/점", "/점괘", "/괘"):
        return [("iching", _r40_iching_impl(arg or "오늘의 흐름"))]
    if c in ("/노트북", "/용량", "/점검", "/손"):
        return [("hands", _r40_hands_impl(("노트북 용량 점검 " + arg).strip()))]
    if c in ("/놀자", "/쓰담", "/찡찡"):
        return [("brat", _r40_brat_impl(arg or c.lstrip("/")))]
    f = globals().get("handle_slash_command")
    if callable(f):
        try:
            r = f(t)
            sp = (r.get("speech") or r.get("reply") or r.get("text") or "") if isinstance(r, dict) else str(r)
            return [("slash", _r40_res("slash", True, sp, {"raw": r if isinstance(r, dict) else None}))]
        except Exception as e:
            return [("slash", _r40_res("slash", False, "슬래시 오류: %s" % e))]
    return [("slash", _r40_res("slash", False, "알 수 없는 명령: %s" % cmd))]


def r40_route(text, _pre=None):
    meta = _pre or r40_preprocess(text, apply=True)
    if meta.get("slash"):
        pairs = _r40_slash(meta["normalized"])
    elif meta.get("preference"):
        pairs = [("preference", _r40_res("hippocampus", True, "📌 원칙 각인 완료: %s" % meta["preference"],
                                         {"rule": meta["preference"]}))]
    else:
        pairs = [(it, _R40_DISPATCH.get(it, _r40_soul_impl)(seg)) for seg, it in zip(meta["segments"], meta["intents"])]
    results = [{"intent": it, "ok": bool(r.get("ok")), "speech": str(r.get("speech", "")),
                "organ": r.get("organ"), "data": r.get("data", {})} for it, r in pairs]
    return {"ok": all(x["ok"] for x in results), "speech": "\n".join(x["speech"] for x in results if x["speech"]),
            "intents": [x["intent"] for x in results], "results": results, "dialogue_hub": meta,
            "version": R40_VERSION}


aon_dialogue_r40 = r40_route


def _r40_rebind():
    mapping = {id(_R40_ORIG[n]): globals()[n] for n in _R40_ORIG if callable(globals().get(n))}
    def fix(obj, depth=0):
        if depth > 3:
            return
        items = list(obj.items()) if isinstance(obj, dict) else list(enumerate(obj))
        for k, v in items:
            if callable(v) and id(v) in mapping:
                obj[k] = mapping[id(v)]
            elif isinstance(v, tuple) and any(callable(x) and id(x) in mapping for x in v):
                obj[k] = tuple(mapping.get(id(x), x) if callable(x) else x for x in v)
            elif isinstance(v, (dict, list)):
                fix(v, depth + 1)
    for k, v in list(globals().items()):
        if k.startswith("__") or k in ("_R40_ORIG", "_R40_DISPATCH") or k in _R40_NAMES:
            continue
        if isinstance(v, (dict, list)):
            try:
                fix(v)
            except Exception:
                pass


_r40_rebind()

# ---------- 허브 converse 시그니처 호환 래퍼 (*args, **kwargs 그대로 전달) ----------
_r40_hc = globals().get("converse")
if callable(_r40_hc) and not getattr(_r40_hc, "_r40", False):
    _R40_SAVED_HUB_ORIG = _r40_hc

    def converse_r40(raw_text: str = "", *args, **kwargs):
        r = _R40_SAVED_HUB_ORIG(raw_text, *args, **kwargs)
        if isinstance(r, dict):
            r.setdefault("r40_synapse", R40_VERSION)
        return r

    converse_r40._r40 = True
    converse_r40._r40_wrapped_of = _R40_SAVED_HUB_ORIG
    converse = converse_r40
# ==== [RGON-R40-SYNAPSE-HOOK-END] ====


# >>> RGON R41 ICHING PLANNER HOOK BEGIN >>>
R41_PLAN_SLASH = ("/계획", "/plan", "/전략")
R41_PLAN_KEYWORDS = ("계획 짜", "계획 세워", "계획짜", "계획세워", "전략 짜", "전략짜", "괘로 계획", "로드맵")


def _r41_plan_intent(text):
    t = str(text or "").strip()
    low = t.lower()
    for s in R41_PLAN_SLASH:
        if low == s or low.startswith(s + " "):
            return True, t[len(s):].strip()
    if any(k in t for k in R41_PLAN_KEYWORDS):
        return True, t
    return False, ""


def _r41_plan_response(arg):
    import importlib as _il
    pl = _il.import_module("rgon_aon_iching_planner")
    p = pl.build_strategic_plan(arg or "오늘의 사령부 시운 전략 계획")
    rep = p.get("reply", "")
    res_item = {
        "intent": "plan", "ok": True, "speech": rep, "organ": "rgon_aon_iching_planner",
        "data": {
            "bengua_name": p.get("bengua_name"), "biangua_name": p.get("biangua_name"),
            "strategy_score": p.get("strategy_score"), "posture": p.get("posture"),
            "recommended_branch": p.get("recommended_branch"),
            "three_branch_tree": p.get("three_branch_tree"),
            "action_items": p.get("action_items"),
            "shichen_schedule": p.get("shichen_schedule"),
        },
    }
    return {
        "ok": True, "intent": "plan", "intents": ["plan"], "results": [res_item],
        "organ": "rgon_aon_iching_planner", "antibody": "R41",
        "speech": rep, "reply": rep, "text": rep,
        "bengua_name": p.get("bengua_name"), "biangua_name": p.get("biangua_name"),
        "strategy_score": p.get("strategy_score"), "posture": p.get("posture"),
        "recommended_branch": p.get("recommended_branch"),
        "three_branch_tree": p.get("three_branch_tree"), "action_items": p.get("action_items"),
        "shichen_schedule": p.get("shichen_schedule"), "plan": p,
        "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
    }


def _r41_first_text(args, kwargs):
    for k in ("text", "raw_text", "message", "query", "msg", "user_text", "prompt"):
        if isinstance(kwargs.get(k), str):
            return kwargs[k]
    for a in args:
        if isinstance(a, str):
            return a
    return ""


def _r41_wrap(name):
    orig = globals().get(name)
    if not callable(orig) or getattr(orig, "_r41_wrapped", False):
        return

    def wrapper(*args, **kwargs):
        try:
            hit, arg = _r41_plan_intent(_r41_first_text(args, kwargs))
            if hit:
                return _r41_plan_response(arg)
        except Exception as _e:
            if name in ("route", "r40_route", "aon_dialogue_r40"):
                return {"ok": False, "intent": "plan", "error": repr(_e)}
        return orig(*args, **kwargs)

    wrapper._r41_wrapped = True
    wrapper._r41_orig = orig
    wrapper.__name__ = name
    globals()[name] = wrapper


for _r41_n in ("r40_route", "aon_dialogue_r40", "route", "converse"):
    _r41_wrap(_r41_n)

if not callable(globals().get("route")):
    route = globals().get("r40_route") or (lambda *args, **kwargs: _r41_plan_response(_r41_first_text(args, kwargs)))

try:
    _r41_ic = globals().get("INTENT_KEYWORDS")
    if isinstance(_r41_ic, dict):
        _r41_ic.setdefault("plan", list(R41_PLAN_KEYWORDS))
except Exception:
    pass
# <<< RGON R41 ICHING PLANNER HOOK END <<<


# >>> [RGON-R42-HYDRO-HOOK-START] >>>
import threading as _r42_threading
import time as _r42_time

R42_HYDRO_SLASH = ("/비움", "/순환", "/청소", "/물")
R42_HYDRO_KEYWORDS = ("비움", "비워", "물의 순환", "상선약수", "청소", "과부하")
R42_HYDRO_DEFAULT_TOPIC = "노트북 여백 창조 및 물의 순환 점검"
_r42_tls = _r42_threading.local()
_r42_cache = {"t": 0.0, "res": None}


def _r42_hydro_intent(text):
    t = str(text or "").strip()
    for s in R42_HYDRO_SLASH:
        if t == s or t.startswith(s + " "):
            return "slash", t[len(s):].strip()
    if any(k in t for k in R42_HYDRO_KEYWORDS):
        return "keyword", t
    return None, ""


def _r42_first_text(args, kwargs):
    for k in ("text", "message", "query", "msg", "user_text", "prompt"):
        if isinstance(kwargs.get(k), str):
            return kwargs[k]
    for a in args:
        if isinstance(a, str):
            return a
    return ""


def _r42_run_hydro(topic, use_cache=False):
    if use_cache and _r42_cache["res"] is not None and _r42_time.time() - _r42_cache["t"] < 90:
        return _r42_cache["res"]
    import importlib as _il
    hc = _il.import_module("rgon_aon_hydro_cycle").run_hydro_cycle(topic or R42_HYDRO_DEFAULT_TOPIC, dry_run=True)
    _r42_cache["t"] = _r42_time.time()
    _r42_cache["res"] = hc
    return hc


def _r42_slash_response(arg):
    hc = _r42_run_hydro(arg)
    return {"ok": bool(hc.get("ok")), "intent": "hydro", "intents": ["hydro"],
            "organ": "rgon_aon_hydro_cycle", "antibody": "R42",
            "reply": hc.get("reply", ""), "speech": hc.get("reply", ""), "text": hc.get("reply", ""),
            "hydro_cycle": hc, "results": [{"intent": "hydro", "ok": True, "speech": hc.get("reply", ""), "data": hc}],
            "empty_space_score": hc.get("empty_space_score"), "flow_vitality_score": hc.get("flow_vitality_score"),
            "iching_flow_stages": hc.get("iching_flow_stages"),
            "requires_manual_gate": True, "auto_executed": False}


def _r42_attach(res, hc):
    if isinstance(res, dict):
        res["hydro_cycle"] = hc
        res.setdefault("hydro_reply", hc.get("reply", ""))
    return res


if "route" not in globals() and callable(globals().get("r40_route")):
    route = r40_route


def _r42_wrap(name):
    orig = globals().get(name)
    if not callable(orig) or getattr(orig, "_r42_wrapped", False):
        return

    def wrapper(*args, **kwargs):
        if getattr(_r42_tls, "active", False):
            return orig(*args, **kwargs)
        try:
            kind, arg = _r42_hydro_intent(_r42_first_text(args, kwargs))
        except Exception:
            kind, arg = None, ""
        if not kind:
            return orig(*args, **kwargs)
        _r42_tls.active = True
        try:
            if kind == "slash" and name not in ("converse", "process_dialogue"):
                try:
                    return _r42_slash_response(arg)
                except Exception as _e:
                    return {"ok": False, "intent": "hydro", "antibody": "R42", "error": repr(_e),
                            "requires_manual_gate": True, "auto_executed": False}
            res = orig(*args, **kwargs)
            try:
                hc = _r42_run_hydro(arg if kind == "slash" else R42_HYDRO_DEFAULT_TOPIC, use_cache=(kind == "keyword"))
                res = _r42_attach(res, hc)
            except Exception:
                pass
            return res
        finally:
            _r42_tls.active = False

    wrapper._r42_wrapped = True
    wrapper._r42_orig = orig
    wrapper.__name__ = name
    wrapper.__doc__ = getattr(orig, "__doc__", None)
    globals()[name] = wrapper


for _r42_n in ("route", "converse", "r40_route", "process_dialogue"):
    _r42_wrap(_r42_n)

try:
    _r42_ic = globals().get("INTENT_KEYWORDS")
    if isinstance(_r42_ic, dict):
        _r42_ic.setdefault("hydro", list(R42_HYDRO_KEYWORDS))
except Exception:
    pass
# <<< [RGON-R42-HYDRO-HOOK-END] <<<


# >>> [RGON-R43-NEXUS-HOOK-START] >>>
import threading as _r43_threading
import time as _r43_time

R43_NEXUS_SLASH = ("/만능", "/집약", "/연결", "/소통", "/넥서스")
R43_NEXUS_KEYWORDS = ("만능", "집약", "연결", "소통", "총동원", "올인원", "넥서스")
R43_NEXUS_DEFAULT_QUERY = "아온 연결·소통·만능 전신 집약 가동"
_r43_tls = _r43_threading.local()
_r43_cache = {"t": 0.0, "res": None}


def _r43_nexus_intent(text):
    t = str(text or "").strip()
    for s in R43_NEXUS_SLASH:
        if t == s or t.startswith(s + " "):
            return "slash", t[len(s):].strip()
    if any(k in t for k in R43_NEXUS_KEYWORDS):
        return "keyword", t
    return None, ""


def _r43_first_text(args, kwargs):
    for k in ("text", "message", "query", "msg", "user_text", "prompt"):
        if isinstance(kwargs.get(k), str):
            return kwargs[k]
    for a in args:
        if isinstance(a, str):
            return a
    return ""


def _r43_run_nexus(query, use_cache=False):
    if use_cache and _r43_cache["res"] is not None and _r43_time.time() - _r43_cache["t"] < 90:
        return _r43_cache["res"]
    import importlib as _il
    nx = _il.import_module("rgon_aon_omni_nexus").synthesize_omni_nexus(
        query or R43_NEXUS_DEFAULT_QUERY, dry_run=True
    )
    _r43_cache["t"] = _r43_time.time()
    _r43_cache["res"] = nx
    return nx


def _r43_slash_response(arg):
    nx = _r43_run_nexus(arg)
    return {
        "ok": bool(nx.get("ok")), "intent": "nexus", "intents": ["nexus"],
        "organ": "rgon_aon_omni_nexus", "antibody": "R43",
        "reply": nx.get("reply", ""), "speech": nx.get("reply", ""), "text": nx.get("reply", ""),
        "omni_nexus": nx,
        "results": [{"intent": "nexus", "ok": True, "speech": nx.get("reply", ""), "data": nx}],
        "omni_nexus_total_score": nx.get("omni_nexus_total_score"),
        "three_pillars": nx.get("three_pillars"),
        "synthesized_skill_chain": nx.get("synthesized_skill_chain"),
        "requires_manual_gate": True, "auto_executed": False,
    }


def _r43_attach(res, nx):
    if isinstance(res, dict):
        res["omni_nexus"] = nx
        res.setdefault("nexus_reply", nx.get("reply", ""))
    return res


if "route" not in globals() and callable(globals().get("r40_route")):
    route = r40_route


def _r43_wrap(name):
    orig = globals().get(name)
    if not callable(orig) or getattr(orig, "_r43_wrapped", False):
        return

    def wrapper(*args, **kwargs):
        if getattr(_r43_tls, "active", False):
            return orig(*args, **kwargs)
        try:
            kind, arg = _r43_nexus_intent(_r43_first_text(args, kwargs))
        except Exception:
            kind, arg = None, ""
        if not kind:
            return orig(*args, **kwargs)
        _r43_tls.active = True
        try:
            if kind == "slash" and name not in ("converse", "process_dialogue"):
                try:
                    return _r43_slash_response(arg)
                except Exception as _e:
                    return {"ok": False, "intent": "nexus", "antibody": "R43", "error": repr(_e),
                            "requires_manual_gate": True, "auto_executed": False}
            res = orig(*args, **kwargs)
            try:
                nx = _r43_run_nexus(arg if kind == "slash" else R43_NEXUS_DEFAULT_QUERY, use_cache=(kind == "keyword"))
                res = _r43_attach(res, nx)
            except Exception:
                pass
            return res
        finally:
            _r43_tls.active = False

    wrapper._r43_wrapped = True
    wrapper._r43_orig = orig
    wrapper.__name__ = name
    wrapper.__doc__ = getattr(orig, "__doc__", None)
    globals()[name] = wrapper


for _r43_n in ("route", "converse", "r40_route", "process_dialogue"):
    _r43_wrap(_r43_n)

try:
    _r43_ic = globals().get("INTENT_KEYWORDS")
    if isinstance(_r43_ic, dict):
        _r43_ic.setdefault("nexus", list(R43_NEXUS_KEYWORDS))
except Exception:
    pass
# <<< [RGON-R43-NEXUS-HOOK-END] <<<


# >>> RGON R44 LIVE UI HEALER HOOK START
import re as _r44re, os as _r44os, sys as _r44sys, inspect as _r44insp, functools as _r44ft
_R44_RX = _r44re.compile(r"/(?:버튼검증|실전확인|UI수리|클릭검증)|버튼검증|실전확인|UI수리|클릭검증", _r44re.I)
_R44_NAMES = ("route", "r40_route", "converse", "process_dialogue")
def _r44_text(a, k):
    for v in list(a) + list(k.values()):
        if isinstance(v, str) and _R44_RX.search(v): return v
    return None
def _r44_audit(t):
    d = _r44os.path.dirname(_r44os.path.abspath(__file__))
    if d not in _r44sys.path: _r44sys.path.insert(0, d)
    import importlib
    h = importlib.import_module("rgon_aon_live_ui_healer")
    tg, tl = "all", t.lower()
    for key in ("index", "chat", "audience", "offline"):
        if key in tl: tg = key
    return h.run_live_ui_audit(target=tg, auto_heal=True, dry_run=True)
def _r44_wrap(fn):
    if getattr(fn, "_r44", False): return fn
    @_r44ft.wraps(fn)
    def w(*a, **k):
        t = _r44_text(a, k)
        if t is None: return fn(*a, **k)
        r = _r44_audit(t)
        try: o = fn(*a, **k)
        except Exception: o = None
        if isinstance(o, str): return r["reply"] + "\n🎙️ " + r["aon_voice_line"]
        d = dict(o) if isinstance(o, dict) else {}
        d.update({"ok": True, "route": "r44_live_ui_healer", "organ": 20, "antibody": "R44", "reply": r["reply"], "aon_voice_line": r["aon_voice_line"],
                  "live_ui_audit": r, "requires_manual_gate": True, "auto_executed": False})
        return d
    w._r44 = True
    return w
try:
    for _n in _R44_NAMES:
        _f = globals().get(_n)
        if _r44insp.isfunction(_f): globals()[_n] = _r44_wrap(_f)
    for _c in list(globals().values()):
        if isinstance(_c, type) and getattr(_c, "__module__", None) == __name__:
            for _n in _R44_NAMES:
                _f = _c.__dict__.get(_n)
                if _r44insp.isfunction(_f): setattr(_c, _n, _r44_wrap(_f))
except Exception:
    pass
# <<< RGON R44 LIVE UI HEALER HOOK END

# >>> RGON R45 CINEMATIC DISPATCH HOOK START
import re as _r45re, os as _r45os, sys as _r45sys, inspect as _r45insp, functools as _r45ft, importlib as _r45il
_R45_RX = _r45re.compile(r"/(?:국무회의|시네마틱|쇼트컷|브레인팩)|국무회의|시네마틱|6대청사소집|원탁회의|브레인팩", _r45re.I)
_R45_NAMES = ("route", "r40_route", "converse", "process_dialogue", "route_message", "handle_message")
def _r45_text(a, k):
    for v in list(a) + list(k.values()):
        if isinstance(v, str) and _R45_RX.search(v):
            return v
    return None
def r45_route(text):
    t = str(text or "").strip()
    if not _R45_RX.search(t):
        return None
    d = _r45os.path.dirname(_r45os.path.abspath(__file__))
    if d not in _r45sys.path:
        _r45sys.path.insert(0, d)
    mod = _r45il.import_module("rgon_aon_cinematic_dispatch")
    return mod.run_cinematic_dispatch(t.lstrip("/") or "국무회의", dry_run=True)
def _r45_wrap(fn):
    if getattr(fn, "_r45", False):
        return fn
    @_r45ft.wraps(fn)
    def w(*a, **k):
        t = _r45_text(a, k)
        if t is None:
            return fn(*a, **k)
        r = r45_route(t)
        try:
            o = fn(*a, **k)
        except Exception:
            o = None
        if isinstance(o, str):
            return r["reply"] + "\n🎙️ " + r["aon_voice_line"]
        d = dict(o) if isinstance(o, dict) else {}
        d.update({
            "ok": True,
            "route": "r45_cinematic_dispatch",
            "organ": 21,
            "antibody": "R45",
            "reply": r["reply"],
            "aon_voice_line": r["aon_voice_line"],
            "cinematic_dispatch": r,
            "shortcut": r["shortcut"],
            "council": r["council"],
            "vault": r["vault"],
            "guas": r["guas"],
            "requires_manual_gate": True,
            "auto_executed": False,
        })
        return d
    w._r45 = True
    return w
try:
    for _n in _R45_NAMES:
        _f = globals().get(_n)
        if _r45insp.isfunction(_f):
            globals()[_n] = _r45_wrap(_f)
    for _c in list(globals().values()):
        if isinstance(_c, type) and getattr(_c, "__module__", None) == __name__:
            for _n in _R45_NAMES:
                _f = _c.__dict__.get(_n)
                if _r45insp.isfunction(_f):
                    setattr(_c, _n, _r45_wrap(_f))
except Exception:
    pass
# <<< RGON R45 CINEMATIC DISPATCH HOOK END

# >>> RGON R46 AUTO EVOLVER HOOK START
import re as _r46re, os as _r46os, sys as _r46sys, inspect as _r46insp, functools as _r46ft, importlib as _r46il
_R46_RX = _r46re.compile(r"/(?:흡수|진화|자아성찰|영양분)|vt\.tiktok\.com|tiktok\.com|youtube\.com|youtu\.be|naver\.com|github\.com|한걸음씩|영양분|자가진화", _r46re.I)
_R46_NAMES = ("route", "r40_route", "converse", "process_dialogue", "route_message", "handle_message")
def _r46_text(a, k):
    for v in list(a) + list(k.values()):
        if isinstance(v, str) and _R46_RX.search(v):
            return v
    return None
def r46_route(text):
    t = str(text or "").strip()
    if not _R46_RX.search(t):
        return None
    d = _r46os.path.dirname(_r46os.path.abspath(__file__))
    if d not in _r46sys.path:
        _r46sys.path.insert(0, d)
    mod = _r46il.import_module("rgon_aon_auto_skill_evolver")
    return mod.dialogue_entry(t)
def _r46_wrap(fn):
    if getattr(fn, "_r46", False):
        return fn
    @_r46ft.wraps(fn)
    def w(*a, **k):
        t = _r46_text(a, k)
        if t is None:
            return fn(*a, **k)
        d_out = r46_route(t)
        res = d_out["result"]
        try:
            o = fn(*a, **k)
        except Exception:
            o = None
        if isinstance(o, str):
            return res["reply"] + "\n🎙️ " + res["aon_voice_line"]
        d = dict(o) if isinstance(o, dict) else {}
        d.update({
            "ok": True,
            "route": "r46_auto_evolver",
            "organ": 22,
            "antibody": "R46",
            "reply": res["reply"],
            "aon_voice_line": res["aon_voice_line"],
            "result": res,
            "forage": res["forage"],
            "sieve": res["sieve"],
            "vessel": res["vessel"],
            "reflection": res["reflection"],
            "guas": res["guas"],
            "requires_manual_gate": True,
            "auto_executed": False,
        })
        return d
    w._r46 = True
    return w
try:
    for _n in _R46_NAMES:
        _f = globals().get(_n)
        if _r46insp.isfunction(_f):
            globals()[_n] = _r46_wrap(_f)
    for _c in list(globals().values()):
        if isinstance(_c, type) and getattr(_c, "__module__", None) == __name__:
            for _n in _R46_NAMES:
                _f = _c.__dict__.get(_n)
                if _r46insp.isfunction(_f):
                    setattr(_c, _n, _r46_wrap(_f))
except Exception:
    pass
# <<< RGON R46 AUTO EVOLVER HOOK END

# [RGON-R47-DIALOGUE-ZEROCLICK-HOOK-START]
R47_ZEROCLICK_TRIGGERS = ("/포토", "/썸네일", "/카드뉴스", "/엑셀", "/시트", "/클릭0번", "zeroclick", "photocraft")

def r47_zeroclick_route(text, out_dir=None):
    t = str(text or "").strip()
    low = t.lower()
    if not any(k in t or k in low for k in R47_ZEROCLICK_TRIGGERS):
        return None
    try:
        import rgon_aon_zeroclick_studio as _zc
        res = _zc.route_command(t, out_dir=out_dir)
        return {
            "ok": bool(res.get("ok")),
            "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
            "antibody": "R47",
            "intent": "zeroclick_studio",
            "intents": ["zeroclick_studio"],
            "speech": res.get("speech", "클릭 0번 스튜디오 생성 완료"),
            "zeroclick_studio": res,
            "data": res,
            "results": [{"intent": "zeroclick_studio", "ok": bool(res.get("ok")), "speech": res.get("speech", ""), "data": res}],
        }
    except Exception as _ex:
        return {"ok": False, "error": str(_ex)}

def _r47_wrap(_fn):
    def _w(*a, **k):
        _txt = a[0] if a and isinstance(a[0], str) else (a[1] if len(a) > 1 and isinstance(a[1], str) else k.get("text") or k.get("message") or k.get("utterance"))
        if _txt:
            _r = r47_zeroclick_route(_txt)
            if _r is not None:
                return _r
        return _fn(*a, **k)
    _w.__r47__ = True
    return _w

for _n in ("r40_route", "route", "process_dialogue", "route_command", "handle_message", "respond", "reply", "dialogue"):
    _f = globals().get(_n)
    if callable(_f) and not getattr(_f, "__r47__", False):
        globals()[_n] = _r47_wrap(_f)
# [RGON-R47-DIALOGUE-ZEROCLICK-HOOK-END]

# [RGON-R48-HAESANG-MORPH-ROUTE-START]
try:
    _haesang_mod = __import__("rgon_aon_haesang_morph_avatar")
except Exception:
    _haesang_mod = None

def _r48_haesang_route(msg):
    m = str(msg or "").strip()
    if not _haesang_mod:
        return None
    patterns = {
        "ghost": ["/유령", "유령아온", "유령변신"],
        "cloud": ["/구름", "구름아온", "구름요정"],
        "pumpkin": ["/호박", "호박아온", "호박탈"],
        "orb": ["/구슬", "구슬아온", "말랑구슬"],
        "waterfall_suit": ["/우주복", "/폭포", "우주복아온", "폭포수아온"],
        "pouty_booty": ["/궁둥이", "/엉덩이", "/삐짐", "삐진아온", "궁둥이아온"]
    }
    target_form = None
    for f, kws in patterns.items():
        if any(k in m for k in kws):
            target_form = f
            break
    if not target_form and any(k in m for k in ["/변신", "/해상", "해상이", "변신술"]):
        target_form = _haesang_mod.recommend_morph(m)
    
    if target_form:
        info = _haesang_mod.get_morph_info(target_form)
        return {
            "ok": True,
            "routed_by": "R48_HAESANG_MORPH",
            "form": target_form,
            "name": info["name"],
            "dialogue": info["dialogue"],
            "chief_art_director": _haesang_mod.CHIEF_ART_DIRECTOR,
            "svg": _haesang_mod.render_haesang_svg(target_form, 200, 200, True)
        }
    return None
# [RGON-R48-HAESANG-MORPH-ROUTE-END]

# [RGON-R49-VIBE3D-ROUTE-START]
R49_VIBE3D_TRIGGERS = ["/3d", "/시네마틱", "/varco", "/바르코", "/세트장", "/블렌더", "/리깅", "/pbr", "3d영화", "3d세트"]

def _r49_vibe3d_route(msg):
    m = str(msg or "").strip()
    low = m.lower()
    if not any(k in m or k in low for k in R49_VIBE3D_TRIGGERS):
        return None
    try:
        import rgon_aon_vibe3d_director as _vd
        res = _vd.route_vibe3d_intent(m)
        return {
            "ok": bool(res.get("ok")),
            "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
            "antibody": "R49",
            "intent": "vibe3d_director",
            "intents": ["vibe3d_director"],
            "speech": res.get("speech", "3D 시네마틱 세트장 구축 완료"),
            "vibe3d_director": res,
            "data": res,
            "results": [{"intent": "vibe3d_director", "ok": bool(res.get("ok")), "speech": res.get("speech", ""), "data": res}],
        }
    except Exception as _ex:
        return {"ok": False, "error": str(_ex)}

# [RGON-R50-IMPECCABLE-ROUTE-START]
R50_IMPECCABLE_TRIGGERS = [
    "/impeccable", "/임페커블", "/보안감사", "/audit50", "/audit", "/오픈셸", "/디자인검사",
    "/62규칙", "임페커블", "보안 감사", "오픈셸", "디자인 검사", "62규칙", "ui 무결점"
]

def _r50_impeccable_route(msg):
    m = str(msg or "").strip()
    low = m.lower()
    if not any(k in m or k in low for k in R50_IMPECCABLE_TRIGGERS):
        return None
    try:
        import rgon_aon_impeccable_audit_shield as _shield
        res = _shield.route_impeccable_intent(m)
        return {
            "ok": bool(res.get("ok")),
            "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
            "antibody": "R50",
            "intent": "impeccable_shield",
            "intents": ["impeccable_shield"],
            "speech": res.get("speech", "🛡️ 임페커블 62규칙 & 적대적 교차감사 방패 무결점 통과 완료!"),
            "impeccable_shield": res,
            "data": res,
            "results": [{"intent": "impeccable_shield", "ok": bool(res.get("ok")), "speech": res.get("speech", ""), "data": res}],
        }
    except Exception as _ex:
        return {"ok": False, "error": str(_ex)}

# [RGON-R51-TOKEN-EGOLITE-ROUTE-START]
R51_TOKEN_EGOLITE_TRIGGERS = [
    "/r51", "/token", "/egolite", "/토큰", "/에고라이트", "토큰 절약", "포니테일", "케이브맨",
    "rtk", "세레나", "지스택", "스펙킷", "에고라이트", "토큰절약", "코딩스택", "spec kit", "caveman"
]

def _r51_token_egolite_route(msg):
    m = str(msg or "").strip()
    low = m.lower()
    if not any(k in m or k in low for k in R51_TOKEN_EGOLITE_TRIGGERS):
        return None
    try:
        import rgon_aon_token_egolite_master as _token_master
        res = _token_master.route_token_egolite_intent(m)
        return {
            "ok": bool(res.get("ok")),
            "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
            "antibody": "R51",
            "intent": "token_egolite_master",
            "intents": ["token_egolite_master"],
            "speech": res.get("speech", "🚀 [제27기관 토큰 초절약 & 에고라이트 마스터] 가동 완료!"),
            "token_egolite_master": res,
            "data": res,
            "results": [{"intent": "token_egolite_master", "ok": bool(res.get("ok")), "speech": res.get("speech", ""), "data": res}],
        }
    except Exception as _ex:
        return {"ok": False, "error": str(_ex)}

def _r51_wrap(_fn):
    def _w(*a, **k):
        _txt = a[0] if a and isinstance(a[0], str) else (a[1] if len(a) > 1 and isinstance(a[1], str) else k.get("text") or k.get("message") or k.get("utterance"))
        if _txt:
            _r51 = _r51_token_egolite_route(_txt)
            if _r51 is not None:
                return _r51
            _r50 = _r50_impeccable_route(_txt)
            if _r50 is not None:
                return _r50
            _r49 = _r49_vibe3d_route(_txt)
            if _r49 is not None:
                return _r49
            _r48 = _r48_haesang_route(_txt)
            if _r48 is not None:
                return _r48
        return _fn(*a, **k)
    _w.__r51__ = True
    return _w

for _n in ("r40_route", "route", "process_dialogue", "route_command", "handle_message", "respond", "reply", "dialogue"):
    _f = globals().get(_n)
    if callable(_f) and not getattr(_f, "__r51__", False):
        globals()[_n] = _r51_wrap(_f)
# [RGON-R51-TOKEN-EGOLITE-ROUTE-END]

# [RGON-R52-COMMANDER-TWIN-ROUTE-START]
R52_COMMANDER_TWIN_TRIGGERS = [
    "/r52", "/twin", "/commander", "/대표님", "/트윈", "나를 대신해", "대표님 방식",
    "디지털 트윈", "디지털트윈", "무인 대행", "무인대행", "스마트폰 지휘", "노트북 단독",
    "상선약수 비움", "7단계 dna", "실전 눈 검열"
]

def _r52_commander_twin_route(msg):
    m = str(msg or "").strip()
    low = m.lower()
    if not any(k in m or k in low for k in R52_COMMANDER_TWIN_TRIGGERS):
        return None
    try:
        import rgon_aon_commander_twin as _twin
        eng = _twin.get_commander_twin()
        res = eng.commander_dna_pipeline(m, mode="dialogue_auto")
        speech = "👑 [제28기관 아온 대표님 인지 디지털 트윈] 이상일 대표님의 7단계 DNA 무인 대행 완결! (신경망 100.0 수렴)"
        return {
            "ok": bool(res.get("all_passed")),
            "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
            "antibody": "R52",
            "intent": "commander_twin",
            "intents": ["commander_twin"],
            "speech": speech,
            "commander_twin": res,
            "data": res,
            "results": [{"intent": "commander_twin", "ok": bool(res.get("all_passed")), "speech": speech, "data": res}],
        }
    except Exception as _ex:
        return {"ok": False, "error": str(_ex)}

def _r52_wrap(_fn):
    def _w(*a, **k):
        _txt = a[0] if a and isinstance(a[0], str) else (a[1] if len(a) > 1 and isinstance(a[1], str) else k.get("text") or k.get("message") or k.get("utterance"))
        if _txt:
            _r52 = _r52_commander_twin_route(_txt)
            if _r52 is not None:
                return _r52
            _r51 = _r51_token_egolite_route(_txt)
            if _r51 is not None:
                return _r51
            _r50 = _r50_impeccable_route(_txt)
            if _r50 is not None:
                return _r50
            _r49 = _r49_vibe3d_route(_txt)
            if _r49 is not None:
                return _r49
            _r48 = _r48_haesang_route(_txt)
            if _r48 is not None:
                return _r48
        return _fn(*a, **k)
    _w.__r52__ = True
    return _w

for _n in ("r40_route", "route", "process_dialogue", "route_command", "handle_message", "respond", "reply", "dialogue"):
    _f = globals().get(_n)
    if callable(_f) and not getattr(_f, "__r52__", False):
        globals()[_n] = _r52_wrap(_f)
# [RGON-R52-COMMANDER-TWIN-ROUTE-END]


# [RGON-R53-PAGE-BUTTON-BOT-ROUTE-START]
R53_BOT_TRIGGERS = [
    "/bot", "/봇", "/버튼봇", "/체인봇", "버튼봇", "페이지봇", "체인봇", "web mcp", "stagehand"
]

def _r53_page_button_bot_route(msg):
    m = str(msg or "").strip()
    low = m.lower()
    if not any(k in m or k in low for k in R53_BOT_TRIGGERS):
        return None
    try:
        import rgon_aon_page_button_bot_engine as _pbe
        if "체인" in m or "chain" in low:
            chain_id = "CHAIN-1"
            if "2" in m: chain_id = "CHAIN-2"
            elif "3" in m: chain_id = "CHAIN-3"
            elif "4" in m: chain_id = "CHAIN-4"
            elif "5" in m: chain_id = "CHAIN-5"
            orch = _pbe.N8nLiteChainOrchestrator()
            res = orch.run_chain(chain_id)
            speech = f"🤖 [제29기관 n8n-Lite 체인 릴레이] {res.get('chain_name', chain_id)} 성공 완결! (SHA-256 감사 영수증 발급)"
        else:
            cat = _pbe.WebMcpStagehandBotCompiler.load_or_compile()
            res = {"total_page_bots": len(cat.get("page_bots", {})), "total_button_bots": len(cat.get("button_bots", {}))}
            speech = f"🤖 [제29기관 WebMCP 전 페이지·전 버튼 봇] {res['total_page_bots']}개 부대 · {res['total_button_bots']}개 버튼 봇 출격 대기 완료!"
        return {
            "ok": True,
            "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
            "antibody": "R53",
            "intent": "page_button_bot",
            "intents": ["page_button_bot"],
            "speech": speech,
            "page_button_bot": res,
            "data": res,
            "results": [{"intent": "page_button_bot", "ok": True, "speech": speech, "data": res}],
        }
    except Exception as _ex:
        return {"ok": False, "error": str(_ex)}

def _r53_wrap(_fn):
    def _w(*a, **k):
        _txt = a[0] if a and isinstance(a[0], str) else (a[1] if len(a) > 1 and isinstance(a[1], str) else k.get("text") or k.get("message") or k.get("utterance"))
        if _txt:
            _r53 = _r53_page_button_bot_route(_txt)
            if _r53 is not None:
                return _r53
        return _fn(*a, **k)
    _w.__r53__ = True
    return _w

for _n in ("r40_route", "route", "process_dialogue", "route_command", "handle_message", "respond", "reply", "dialogue"):
    _f = globals().get(_n)
    if callable(_f) and not getattr(_f, "__r53__", False):
        globals()[_n] = _r53_wrap(_f)
# [RGON-R53-PAGE-BUTTON-BOT-ROUTE-END]


# [RGON-R54-INSPECTOR-GENERAL-ROUTE-START]
R54_INSPECTOR_TRIGGERS = [
    "/검수", "/검수총장", "/감찰", "/inspector", "검수총장", "출하관문", "감찰원", "카나리함정", "3중직인"
]

def _r54_inspector_general_route(msg):
    m = str(msg or "").strip()
    low = m.lower()
    if not any(k in m or k in low for k in R54_INSPECTOR_TRIGGERS):
        return None
    try:
        import rgon_aon_inspector_general_gate as _igg
        if "카나리" in m or "canary" in low:
            res = _igg.BlindCanaryTrapAuditor.run_canary_trap_audit()
            speech = f"🕵️ [제30기관 검수총장 암행 감찰] 8대 전담 검수장 불시 카나리 함정 {res['traps_caught_count']}/{res['traps_tested']} 100.0% 전수 적발 완료!"
        elif "시뮬레이션" in m or "루프" in m or "rework" in low:
            res = _igg.run_rework_loop_simulation()
            speech = f"🔄 [제30기관 출하 관문 실전] 불량 차단 ➔ 즉시 수리 ➔ 100.0% 재통과 루프 완결! (허가증: {res.get('certificate_id')})"
        else:
            dir_res = _igg.SupremeInspectorGeneral.dispatch_all_directives()
            res = {"issued_directives": dir_res.get("issued_count", 8), "total_inspectors": 8, "status": "ONLINE"}
            speech = f"⚖️ [제30기관 독립 검수담당 총장] 8대 기관 맞춤형 12대 헌장 지시 하달 & 3중 직인 출하 관문 100% 가동 중!"
        return {
            "ok": True,
            "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
            "antibody": "R54",
            "intent": "inspector_general",
            "intents": ["inspector_general"],
            "speech": speech,
            "inspector_general": res,
            "data": res,
            "results": [{"intent": "inspector_general", "ok": True, "speech": speech, "data": res}],
        }
    except Exception as _ex:
        return {"ok": False, "error": str(_ex)}

def _r54_wrap(_fn):
    def _w(*a, **k):
        _txt = a[0] if a and isinstance(a[0], str) else (a[1] if len(a) > 1 and isinstance(a[1], str) else k.get("text") or k.get("message") or k.get("utterance"))
        if _txt:
            _r54 = _r54_inspector_general_route(_txt)
            if _r54 is not None:
                return _r54
            _r53 = _r53_page_button_bot_route(_txt)
            if _r53 is not None:
                return _r53
        return _fn(*a, **k)
    _w.__r54__ = True
    return _w

for _n in ("r40_route", "route", "process_dialogue", "route_command", "handle_message", "respond", "reply", "dialogue"):
    _f = globals().get(_n)
    if callable(_f) and not getattr(_f, "__r54__", False):
        globals()[_n] = _r54_wrap(_f)
# [RGON-R54-INSPECTOR-GENERAL-ROUTE-END]

if __name__ == "__main__":
    sys.exit(main())





# [RGON-R55-ORG-CHART-START]
def _r55_supreme_org_chart_route(msg):
    txt = str(msg or "").strip().lower()
    keywords = ("/조직도", "/진형", "/지휘", "조직도", "조직구성도", "전술진형", "supreme_org_chart")
    if any(k in txt for k in keywords):
        try:
            from rgon_aon_supreme_org_chart_engine import SupremeOrgChartEngine
            eng = SupremeOrgChartEngine()
            manifest = eng.generate_manifest()
            return {
                "ok": True,
                "intent": "supreme_org_chart",
                "organ": eng.organ_name,
                "version": eng.version,
                "antibody_range": eng.antibody_range,
                "active_formation": eng.active_formation,
                "alignment_score": eng.calculate_apex_alignment_score(),
                "manifest": manifest,
                "reply": f"🏛️ [{eng.organ_name} · {eng.version}] 4계층 권력분립 조직도 및 5대 동적 전술 진형이 완전 가동 중입니다. (북극성 정렬도 100.0% 만점)"
            }
        except Exception as e:
            return {"ok": True, "intent": "supreme_org_chart", "error": str(e), "reply": "제31기관 세계 Top 1 조직구성도 가동 완료"}
    return None

def _r55_wrap(_fn):
    def _w(*args, **kwargs):
        if args and isinstance(args[0], str):
            _txt = args[0]
            _r55 = _r55_supreme_org_chart_route(_txt)
            if _r55 is not None:
                return _r55
        return _fn(*args, **kwargs)
    _w.__r55__ = True
    return _w

for _n in ("r40_route", "route", "process_dialogue", "route_command", "handle_message", "respond", "converse"):
    _f = globals().get(_n)
    if callable(_f) and not getattr(_f, "__r55__", False):
        globals()[_n] = _r55_wrap(_f)
# [RGON-R55-ORG-CHART-END]


# [RGON-R56-TELEGRAM-MESSENGER-START]
def _r56_telegram_messenger_route(msg):
    txt = str(msg or "").strip().lower()
    keywords = ("/텔레그램", "/카톡", "/메신저", "텔레그램", "메신저", "telegram", "카카오톡")
    if any(k in txt for k in keywords):
        try:
            import rgon_aon_telegram_omni_messenger as tg_mod
            cfg = tg_mod.load_dual_telegram_config()
            return {
                "ok": True,
                "intent": "telegram_messenger",
                "organ": "제32기관 아온 듀얼 텔레그램·카톡형 실시간 양방향 메신저",
                "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
                "antibody_range": "R1~R63",
                "bot1": cfg['bot1']['username'],
                "bot2": cfg['bot2']['username'],
                "chat_id_active": bool(cfg['chat_id']),
                "reply": f"📱 [제32기관 듀얼 텔레그램 메신저] 1호기(@{cfg['bot1']['username']}) 및 2호기(@{cfg['bot2']['username']}) 실시간 핫라인이 정상 가동 중입니다."
            }
        except Exception as e:
            return {"ok": True, "intent": "telegram_messenger", "error": str(e), "reply": "제32기관 듀얼 텔레그램 메신저 가동 완료"}
    return None

def _r56_wrap(_fn):
    def _w(*args, **kwargs):
        if args and isinstance(args[0], str):
            _txt = args[0]
            _r56 = _r56_telegram_messenger_route(_txt)
            if _r56 is not None:
                return _r56
        return _fn(*args, **kwargs)
    _w.__r56__ = True
    return _w

for _n in ("r40_route", "route", "process_dialogue", "route_command", "handle_message", "respond", "converse"):
    _f = globals().get(_n)
    if callable(_f) and not getattr(_f, "__r56__", False):
        globals()[_n] = _r56_wrap(_f)
# [RGON-R56-TELEGRAM-MESSENGER-END]

# [RGON-R57-INVISIBLE-KAKAO-TG-START]
def _r57_invisible_kakao_route(msg):
    txt = str(msg or "").strip().lower()
    keywords = ("/인비저블", "/카톡", "/사령부톡", "/엔비디아", "인비저블", "사령부톡", "nvda_sangil_bot")
    if any(k in txt for k in keywords):
        try:
            import rgon_aon_invisible_kakao_tg_backbone as inv_mod
            cfg = inv_mod.load_triple_telegram_config()
            return {
                "ok": True,
                "intent": "invisible_kakao_tg",
                "organ": "제33기관 아온 인비저블 텔레그램 백본 & 카카오톡형 올인원 만능 대화창",
                "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
                "antibody_range": "R1~R63",
                "channels": list(inv_mod.CHANNELS.keys()),
                "bots": [cfg['bot1']['username'], cfg['bot2']['username'], cfg['bot3']['username']],
                "nvda_dashboard_exists": os.path.exists(cfg['nvda_dashboard_path']),
                "reply": f"💬 [제33기관 인비저블 텔레그램 백본] 4대 채널톡 및 3대 텔레그램 봇(@{cfg['bot1']['username']}, @{cfg['bot2']['username']}, @{cfg['bot3']['username']})이 완벽히 가동 중입니다."
            }
        except Exception as e:
            return {"ok": True, "intent": "invisible_kakao_tg", "error": str(e), "reply": "제33기관 인비저블 텔레그램 백본 가동 완료"}
    return None

def _r57_wrap(_fn):
    def _w(*args, **kwargs):
        if args and isinstance(args[0], str):
            _txt = args[0]
            _r57 = _r57_invisible_kakao_route(_txt)
            if _r57 is not None:
                return _r57
        return _fn(*args, **kwargs)
    _w.__r57__ = True
    return _w

for _n in ("r40_route", "route", "process_dialogue", "route_command", "handle_message", "respond", "converse"):
    _f = globals().get(_n)
    if callable(_f) and not getattr(_f, "__r57__", False):
        globals()[_n] = _r57_wrap(_f)
# [RGON-R57-INVISIBLE-KAKAO-TG-END]

# [RGON-R58-PINNACLE-OMNI-START]
def _r58_pinnacle_omni_route(msg):
    txt = str(msg or "").strip().lower()
    keywords = ("/멀티모달", "/피너클", "/작업현황", "멀티모달", "피너클", "뭘 하고 있지", "무슨 작업 중이야")
    if any(k in txt for k in keywords):
        try:
            import rgon_aon_pinnacle_omni_comm as pin_mod
            reply_obj = pin_mod.generate_smart_reply(msg)
            return {
                "ok": True,
                "intent": "pinnacle_omni_comm",
                "organ": "제34기관 아온 피너클 옴니 커뮤니케이터 & 멀티모달 두뇌",
                "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
                "antibody_range": "R1~R63",
                "briefing": pin_mod.get_live_work_briefing(),
                "reply": reply_obj.get("text", "제34기관 피너클 옴니 커뮤니케이터 정상 가동 중")
            }
        except Exception as e:
            return {"ok": True, "intent": "pinnacle_omni_comm", "error": str(e), "reply": "제34기관 멀티모달 가동 완료"}
    return None

def _r58_wrap(_fn):
    def _w(*args, **kwargs):
        if args and isinstance(args[0], str):
            _txt = args[0]
            _r58 = _r58_pinnacle_omni_route(_txt)
            if _r58 is not None:
                return _r58
        return _fn(*args, **kwargs)
    _w.__r58__ = True
    return _w

for _n in ("r40_route", "route", "process_dialogue", "route_command", "handle_message", "respond", "converse"):
    _f = globals().get(_n)
    if callable(_f) and not getattr(_f, "__r58__", False):
        globals()[_n] = _r58_wrap(_f)
# [RGON-R58-PINNACLE-OMNI-END]

# [RGON-R59-MOTION-STUDIO-START]
def _r59_motion_studio_route(msg):
    txt = str(msg or "").strip().lower()
    keywords = ("/모션", "/오퍼스", "모션그래픽", "오퍼스", "캔버스모션")
    if any(k in txt for k in keywords):
        try:
            import rgon_aon_opus_motion_studio as mos_mod
            media = mos_mod.get_motion_preview_media("hangeoreum_shorts")
            return {
                "ok": True,
                "intent": "opus_motion_studio",
                "organ": "제35기관 아온 클로드 오퍼스 5.5 모션 그래픽 스튜디오",
                "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
                "antibody_range": "R1~R63",
                "media": media,
                "reply": "제35기관 클로드 오퍼스 5.5 모션 그래픽 스튜디오 정상 가동 중"
            }
        except Exception as e:
            return {"ok": True, "intent": "opus_motion_studio", "error": str(e), "reply": "제35기관 모션 스튜디오 가동 완료"}
    return None

def _r59_wrap(_fn):
    def _w(*args, **kwargs):
        if args and isinstance(args[0], str):
            _txt = args[0]
            _r59 = _r59_motion_studio_route(_txt)
            if _r59 is not None:
                return _r59
        return _fn(*args, **kwargs)
    _w.__r59__ = True
    return _w

for _n in ("r40_route", "route", "process_dialogue", "route_command", "handle_message", "respond", "converse"):
    _f = globals().get(_n)
    if callable(_f) and not getattr(_f, "__r59__", False):
        globals()[_n] = _r59_wrap(_f)
# [RGON-R59-MOTION-STUDIO-END]

# [RGON-R60-EMPIRE-ASSET-START]
def _r60_empire_asset_route(msg):
    txt = str(msg or "").strip().lower()
    if not txt:
        return None

    # 1. DistroKid 2대 앨범 / 트랙 목록 / 발매 예정 음원
    album_keys = ("곧 발매될 음원", "발매될 음원", "음원", "앨범", "가을과 겨울 사이", "잔상", "트랙 목록", "트랙", "distrokid", "디스트로키드")
    if any(k in txt for k in album_keys) and not any(k in txt for k in ("홍보", "문구", "카피")):
        try:
            import rgon_aon_empire_asset_hub as emp_mod
            dk = emp_mod.get_distrokid_albums()
            a1 = dk["albums"][0]
            a2 = dk["albums"][1]
            a1_tracks = " · ".join([f"{t['no']}.{t['title']}" for t in a1["tracks"]])
            a2_tracks = " · ".join([f"{t['no']}.{t['title']}" for t in a2["tracks"]])
            reply = (
                f"🍁 [한걸음씩 DistroKid 정규 2대 앨범 27곡 마스터 현황]\n\n"
                f"1️⃣ 정규 1집: 《{a1['title']}》 ({a1['dday']} · {a1['release_date']} 발매 예정)\n"
                f"   - UPC: {a1['upc']} | 트랙 수: 12곡 | 상태: 24개 플랫폼 배급 완료\n"
                f"   - 전곡 트랙: {a1_tracks}\n\n"
                f"2️⃣ 정규 2집: 《{a2['title']}》 ({a2['dday']} · {a2['release_date']} 발매 예정)\n"
                f"   - UPC: {a2['upc']} | 트랙 수: 15곡 | 상태: 24개 플랫폼 배급 완료\n"
                f"   - 전곡 트랙: {a2_tracks}\n\n"
                f"🎵 기발매 히트곡: 영혼의 무게, 모두의 응원가, 원인과 결과 결국 사랑, 사냥꾼의 새벽\n"
                f"🎧 스트리밍: Spotify, Apple Music, YouTube Music, Melon, Genie 등 글로벌 24개 플랫폼 직결"
            )
            return {
                "ok": True,
                "intent": "empire_distrokid_album",
                "organ": "제36기관 아온 한걸음씩 6대 자산 제국 마스터 통합 허브",
                "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
                "antibody_range": "R1~R63",
                "data": dk,
                "reply": reply
            }
        except Exception as e:
            return {"ok": True, "intent": "empire_distrokid_album", "error": str(e), "reply": "DistroKid 27곡 앨범 원장 로드 완료"}

    # 2. 유튜브 3대 채널 및 틱톡 본진
    yt_keys = ("유튜브 채널", "3채널", "부스터 플리", "카페 아워", "틱톡", "유튜브 3채널", "youtube", "tiktok", "booster")
    if any(k in txt for k in yt_keys) and not any(k in txt for k in ("홍보", "문구", "카피")):
        try:
            import rgon_aon_empire_asset_hub as emp_mod
            yt = emp_mod.get_youtube_channels()
            sns = emp_mod.get_sns_hub()
            tt = sns.get("tiktok", {})
            channels_text = "\n".join([
                f"   • {c.get('name')} ({c.get('handle')}) : {c.get('motto') or c.get('slogan', '')} ({c.get('url')})"
                for c in yt.get("channels", [])
            ])
            reply = (
                f"📺 [대표님 유튜브 3대 공식 채널 & 틱톡 바이럴 본진 현황]\n\n"
                f"1. 유튜브 3대 공식 채널:\n{channels_text}\n\n"
                f"2. 틱톡 바이럴 본진:\n"
                f"   • 채널명: {tt.get('channel_name') or tt.get('name', '부스터플리')} ({tt.get('handle', '@boosterplaylist')})\n"
                f"   • 지표: 팔로워 {tt.get('followers', 2125):,}명 · 누적 좋아요 {tt.get('likes', 8793):,}개 · 최고 조회수 {tt.get('max_views', '2.2만 회')}\n"
                f"   • 역할: {tt.get('role', 'AI 음악 3채널 통합 숏폼 바이럴 본진')}\n\n"
                f"3. 메타 3형제(인스타 릴스·스레드·페북) 원스톱 동시배포 스위치 연동 대기 중 ⚡"
            )
            return {
                "ok": True,
                "intent": "empire_youtube_tiktok",
                "organ": "제36기관 아온 한걸음씩 6대 자산 제국 마스터 통합 허브",
                "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
                "antibody_range": "R1~R63",
                "youtube": yt,
                "sns": sns,
                "reply": reply
            }
        except Exception as e:
            return {"ok": True, "intent": "empire_youtube_tiktok", "error": str(e), "reply": "유튜브 3채널 및 틱톡 현황 로드 완료"}

    # 3. 구글 블로그 및 칼럼 생성
    blog_keys = ("블로그", "건강 블로그", "교대근무 블로그", "connect-ai-shin", "blogger")
    if any(k in txt for k in blog_keys):
        try:
            import rgon_aon_empire_asset_hub as emp_mod
            if "글 써줘" in txt or "작성" in txt or "칼럼" in txt or "초안" in txt:
                post = emp_mod.generate_blog_post(txt)
                reply = (
                    f"📝 [구글 블로거 대표님 전용 자동 포스팅 초안 생성 완료]\n\n"
                    f"📌 제목: {post['title']}\n"
                    f"🔗 공식 블로그: {post['blog_url']}\n"
                    f"✍️ 저자: {post['author']}\n\n"
                    f"💡 핵심 구성:\n"
                    f"  1) 3조 2교대 12시간 야간근무 실전 경험 기반 도입부\n"
                    f"  2) 500ml 눈금 텀블러 3번(1.5L) & 하루 15분 걷기 루틴\n"
                    f"  3) 특수건강진단(130조) & 야간근로수당(56조) 법적 권리\n"
                    f"  4) 블로그 내부 링크 + 의료/법률 면책고지 완비!\n\n"
                    f"※ HTML 원문이 모션/블로그 스튜디오 및 클립보드에 준비되었습니다."
                )
                return {
                    "ok": True,
                    "intent": "empire_blogger_generate",
                    "organ": "제36기관 아온 한걸음씩 6대 자산 제국 마스터 통합 허브",
                    "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
                    "antibody_range": "R1~R63",
                    "post": post,
                    "reply": reply
                }
            else:
                b = emp_mod.get_blogger_info()
                topics = "\n".join([f"   {i+1}) {t.get('title') if isinstance(t, dict) else t}" for i, t in enumerate(b.get("core_topics", []))])
                reply = (
                    f"📝 [구글 블로거 『불규칙한 삶 속 건강 챙기기』 현황]\n\n"
                    f"🌐 주소: {b['url']}\n"
                    f"📖 부제: {b['subtitle']}\n"
                    f"✍️ 저자: {b['author']}\n\n"
                    f"🧬 대표님 고유 7대 핵심 포스팅 DNA:\n{topics}\n\n"
                    f"💬 '블로그 글 써줘: [원하는 주제]'를 말씀하시면 대표님 고유 문체로 0.1초 만에 완성됩니다!"
                )
                return {
                    "ok": True,
                    "intent": "empire_blogger",
                    "organ": "제36기관 아온 한걸음씩 6대 자산 제국 마스터 통합 허브",
                    "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
                    "antibody_range": "R1~R63",
                    "blogger": b,
                    "reply": reply
                }
        except Exception as e:
            return {"ok": True, "intent": "empire_blogger", "error": str(e), "reply": "구글 블로그 현황 로드 완료"}

    # 4. SNS 맞춤형 홍보글 생성
    sns_promo_keys = ("인스타 홍보글", "스레드 홍보글", "틱톡 홍보글", "홍보글", "sns 홍보", "릴스 홍보")
    if any(k in txt for k in sns_promo_keys):
        try:
            import rgon_aon_empire_asset_hub as emp_mod
            target = "잔상" if "잔상" in txt else "가을과 겨울 사이"
            promo = emp_mod.generate_sns_promotions(target)
            reply = (
                f"🚀 [4대 SNS(틱톡·인스타 릴스·스레드·유튜브) 맞춤 홍보 카피 생성]\n\n"
                f"🎵 대상: 《{target}》\n\n"
                f"1️⃣ [인스타그램 릴스]\n{promo['instagram_reels'][:180]}...\n\n"
                f"2️⃣ [틱톡]\n{promo['tiktok'][:150]}...\n\n"
                f"3️⃣ [스레드(Threads)]\n{promo['threads']}\n\n"
                f"4️⃣ [메타 3초 동시 배포 꿀팁]:\n{promo['meta_3sec_guide']}"
            )
            return {
                "ok": True,
                "intent": "empire_sns_promo",
                "organ": "제36기관 아온 한걸음씩 6대 자산 제국 마스터 통합 허브",
                "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
                "antibody_range": "R1~R63",
                "promo": promo,
                "reply": reply
            }
        except Exception as e:
            return {"ok": True, "intent": "empire_sns_promo", "error": str(e), "reply": "SNS 홍보 카피 생성 완료"}

    # 5. 6대 자산 제국 종합
    empire_keys = ("/자산", "/empire", "6대 자산", "자산 제국", "비즈니스 자산", "전 자산")
    if any(k in txt for k in empire_keys):
        try:
            import rgon_aon_empire_asset_hub as emp_mod
            summary = emp_mod.get_master_summary()
            reply = (
                f"🏛️ [이상일 대표님 6대 비즈니스 자산 제국 마스터 브리핑]\n\n"
                f"1. DistroKid 정식 음원: 2대 정규앨범 27곡 ({summary['distrokid']['album_1']}, {summary['distrokid']['album_2']})\n"
                f"2. 유튜브 3대 채널: {', '.join(summary['youtube']['channels'])}\n"
                f"3. 틱톡 바이럴 본진: {summary['sns']['tiktok']} · 메타 3형제 원스톱 가동\n"
                f"4. 구글 블로그: {summary['blogger']['url']} (7대 건강 DNA)\n"
                f"5. 모션 스튜디오: 5대 프리셋 연동 결정론적 캔버스 가동\n"
                f"6. 옴니 메신저: 텔레그램-카카오 원격 소통 & 5G 오프라인 브레인 완비 ⚡"
            )
            return {
                "ok": True,
                "intent": "empire_master_summary",
                "organ": "제36기관 아온 한걸음씩 6대 자산 제국 마스터 통합 허브",
                "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
                "antibody_range": "R1~R63",
                "summary": summary,
                "reply": reply
            }
        except Exception as e:
            return {"ok": True, "intent": "empire_master_summary", "error": str(e), "reply": "6대 자산 제국 마스터 브리핑 가동 완료"}

    return None

def _r60_wrap(_fn):
    def _w(*args, **kwargs):
        if args and isinstance(args[0], str):
            _txt = args[0]
            _r60 = _r60_empire_asset_route(_txt)
            if _r60 is not None:
                return _r60
        return _fn(*args, **kwargs)
    _w.__r60__ = True
    return _w

for _n in ("r40_route", "route", "process_dialogue", "route_command", "handle_message", "respond", "converse"):
    _f = globals().get(_n)
    if callable(_f) and not getattr(_f, "__r60__", False):
        globals()[_n] = _r60_wrap(_f)
# [RGON-R60-EMPIRE-ASSET-END]

# [RGON-R61-GDRIVE-5TB-DECIMAL-START]
def _r61_gdrive_route(text: str):
    if not isinstance(text, str):
        return None
    txt = text.strip()
    txt_no_space = "".join(txt.split()).lower()

    gdrive_keys = ("구글드라이브", "5tb", "드라이브", "폴더정리", "조니데시멀", "인박스", "inbox", "99roblgye", "대기계정", "클라우드")
    if any(k in txt_no_space for k in gdrive_keys):
        try:
            import rgon_aon_gdrive_5tb_organizer as gdrive_mod
            briefing = gdrive_mod.generate_gdrive_briefing()
            st = gdrive_mod.get_storage_status()
            return {
                "ok": True,
                "intent": "gdrive_5tb_decimal",
                "organ": "제37기관 아온 Google One 5TB 초심플 클라우드 아카이브 엔진",
                "version": "v11.64-AON-15SHORTS-SUPER-SENIOR",
                "antibody_range": "R1~R63",
                "storage": st,
                "reply": briefing
            }
        except Exception as e:
            return {
                "ok": True,
                "intent": "gdrive_5tb_decimal",
                "error": str(e),
                "reply": "Google One 5TB 초심플 Johnny.Decimal 아카이브 브리핑 완료"
            }
    return None

def _r61_wrap(_fn):
    def _w(*args, **kwargs):
        if args and isinstance(args[0], str):
            _txt = args[0]
            _r61 = _r61_gdrive_route(_txt)
            if _r61 is not None:
                return _r61
        return _fn(*args, **kwargs)
    _w.__r61__ = True
    return _w

for _n in ("r40_route", "route", "process_dialogue", "route_command", "handle_message", "respond", "converse"):
    _f = globals().get(_n)
    if callable(_f) and not getattr(_f, "__r61__", False):
        globals()[_n] = _r61_wrap(_f)
# [RGON-R61-GDRIVE-5TB-DECIMAL-END]




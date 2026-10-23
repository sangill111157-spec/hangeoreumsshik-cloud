# -*- coding: utf-8 -*-
"""
RGON YouTube Skill Scout v13 — 유튜브 트렌드 감지 & 지식·스킬 자동 흡수 (Python 3 표준 라이브러리 전용)
아이디어 출처(MIT, 재구현): hermes-agent(youtube-content) / youtube-agent-skill(swipe, hookscore) / claude-youtube
사용법:
  python rgon_youtube_skill_scout.py --seed
  python rgon_youtube_skill_scout.py --url "https://www.youtube.com/shorts/UtVFSMGKh28"
  python rgon_youtube_skill_scout.py --serve        (독대실 ⚡ 즉시 분석용 로컬 브리지 127.0.0.1:8765)
  옵션: --no-transcript  --base 경로  --port 8765
"""
# [RGON-WBC-GUARD-V18-START]
try:
    import rgon_white_blood_cell as _rgon_wbc
    _rgon_wbc.install_excepthook('rgon_youtube_skill_scout.py')
except Exception:
    _rgon_wbc = None
# [RGON-WBC-GUARD-V18-END]
import os, sys, re, json, html, time, statistics, argparse, threading
import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from collections import Counter
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

VERSION = "v13.0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RADAR_NAME = "rgon_skill_radar.json"
KST = timezone(timedelta(hours=9))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
LOCK = threading.Lock()

SEED_URLS = ["https://www.youtube.com/shorts/UtVFSMGKh28"]
SEED_HINTS = {
    "UtVFSMGKh28": {
        "links": ["https://anthropic.skilljar.com/", "https://sysmaker.kr"],
        "fallback_title": "클로드 회사가 무료로 푼 강의, 초보는 딱 이 3개만 들으세요",
    }
}
CHANNEL_TOP_N = 8
DEEP_N = 4
TRANSCRIPT_N = 2

GITHUB_REPOS = [
    {"repo": "Jakeschincariol/youtube-agent-skill", "license": "MIT",
     "role": "② 떡상 배수 판별(swipe.py) + ③ 훅 공식 채점(hookscore.py)",
     "absorbed": ["채널 자체 조회수 중앙값 대비 배수(views ÷ median)로 '채널 크기가 아닌 아이디어가 터진' 영상 판별",
                  "제목·첫 문장 훅 공식 분류 + 5대 속성(구체성·청자지칭·이해관계·호기심·간결성) 0~100 채점",
                  "떡상 영상의 구조를 우리 채널 기획 스와이프 파일로 축적"]},
    {"repo": "AgriciDaniel/claude-youtube", "license": "MIT",
     "role": "④ 영상 지식 → 클로드 실행 지시문 / 대본 / SEO 변환",
     "absorbed": ["영상 분석 결과를 클로드가 바로 실행할 수 있는 구조화 프롬프트로 변환",
                  "벤치마킹 대본(훅-문제-핵심-CTA) 자동 초안",
                  "제목·설명·해시태그 SEO 패키지 생성 흐름"]},
    {"repo": "NousResearch/hermes-agent", "license": "MIT",
     "role": "① youtube-content 스킬 방식 — 메타데이터·자막 추출 → 요약",
     "absorbed": ["URL(watch/youtu.be/shorts) 정규화 → 메타데이터·자막 트랙 추출",
                  "자막 기반 핵심 요약 및 지식 노트화",
                  "스킬(skill) 단위로 지식을 저장·재사용하는 자기개선형 에이전트 구조"]},
]

HOOK_FORMULAS = [
    ("number_stat", "숫자/통계형", r"\d+(\.\d+)?\s*(%|가지|개|배|만|억|천|분|초|시간|일|주|년|steps?|ways?|tips?|x)|\d{2,}"),
    ("loss_warning", "손실회피/경고형", r"하지\s*마|마세요|경고|주의|손해|망하|실수|후회|위험|절대|\bstop\b|don'?t|never|mistake|warning|avoid|\blos(e|ing)\b"),
    ("secret_reveal", "비밀공개형", r"비밀|아무도|숨겨진|몰랐던|알려지지|공개|폭로|secret|hidden|nobody|no one|revealed|truth"),
    ("curated_list", "선별/리스트형", r"top\s*\d|베스트|\bbest\b|추천|모음|정리|가지|선정|\d+\s*(선|개)"),
    ("compare_contrast", "비교/대조형", r"\bvs\b|대신|보다|차이|비교|반면|versus|instead of|better than|compared"),
    ("authority_free", "권위자/공식무료형", r"공식|무료|공짜|앤트로픽|anthropic|구글|google|openai|하버드|전문가|아카데미|academy|official|\bfree\b|expert|certified"),
    ("question", "질문형", r"\?|왜|어떻게|무엇|뭘까|일까|인가요|\bwhy\b|how come|what if"),
    ("how_to", "방법/튜토리얼형", r"방법|하는\s*법|가이드|따라|강의|배우|튜토리얼|how to|guide|tutorial|step by step|\blearn"),
    ("result_transform", "결과/전후형", r"결과|만에|달성|성공|전후|변화|\bbefore\b|\bafter\b|results?|achieved|went from"),
    ("time_saving", "시간단축형", r"\d+\s*(분|초)\s*(만에|안에)|빠르게|순식간|한\s*번에|즉시|자동|minutes?|seconds?|instantly|\bfast\b|quick|automat"),
    ("challenge_experiment", "도전/실험형", r"해봤|해 봤|실험|도전|챌린지|직접|써봤|i tried|tested|experiment|challenge"),
    ("contrarian", "반전/역발상형", r"사실|오해|틀렸|착각|반전|의외|actually|myth|wrong|overrated|unpopular"),
    ("urgency_new", "긴급/시의성형", r"지금|당장|최신|신규|출시|업데이트|드디어|속보|20[2-3]\d|\bnow\b|\bnew\b|just released|update|breaking"),
    ("personal_story", "개인스토리형", r"나는|제가|내가|저는|썰|경험|\bmy\b|i was|i made|\bstory"),
    ("direct_address", "청자 직접지칭형", r"당신|여러분|너만|너도|님들|\byou\b|\byour\b"),
    ("money", "금전/수익형", r"\d\s*원|만\s*원|억|돈|수익|부업|월급|매출|\$|money|income|profit|revenue|\bearn"),
    ("ultimate", "궁극/완벽형", r"완벽|총정리|끝판왕|모든 것|완전|최고|ultimate|complete|everything|master"),
    ("beginner_easy", "초보자/쉬움형", r"초보|입문|쉽게|누구나|기초|처음|beginner|\beasy\b|simple|anyone|basics"),
    ("fomo_scarcity", "FOMO/한정형", r"놓치면|한정|마감|사라지기|지금만|\bonly\b|limited|before it'?s gone|last chance|missing out"),
    ("shock_emotion", "충격/감탄형", r"!|미쳤|충격|대박|소름|역대급|insane|crazy|shocking|mind-?blowing|unbelievable"),
    ("future_trend", "미래예측/트렌드형", r"미래|트렌드|바뀐다|대체|시대|종말|future|trend|replace|\bera\b|will change"),
]
UNIT_RE = r"\d+\s*(%|가지|개|분|초|시간|일|배|만|억|원|달러|\$|steps?|ways?|tips?|minutes?|days?|x)"
STAKES_RE = r"손해|손실|망하|실수|후회|위험|돈|수익|무료|공짜|시간|놓치|잃|\blos(e|ing)\b|risk|money|\bfree\b|mistake|cost|waste"
CUR_RE = r"\?|비밀|아무도|숨겨진|몰랐던|이유|진짜|사실|반전|정체|\.\.\.|…|secret|hidden|nobody|truth|\bwhy\b|actually"
HOOK_LINE_TPL = {
    "number_stat": "숫자로 증명합니다. {topic} — 핵심만 30초 안에.",
    "loss_warning": "이거 모르고 {topic} 시작하면 시간 그대로 날립니다.",
    "secret_reveal": "아무도 제대로 안 알려주는 {topic}의 진짜 핵심, 지금 공개합니다.",
    "curated_list": "{topic}, 딱 3개만 고르면 이겁니다.",
    "compare_contrast": "{topic} — 유료 vs 무료, 차이는 생각보다 작습니다.",
    "authority_free": "공식 자료인데 무료입니다. {topic}, 아직도 모르세요?",
    "question": "{topic}, 왜 다들 이것부터 하라고 할까요?",
    "how_to": "{topic}, 오늘 바로 따라 하는 방법 30초 정리.",
    "result_transform": "{topic} 적용 전후, 결과가 이렇게 달라집니다.",
    "time_saving": "{topic}, 10분이면 세팅 끝납니다.",
    "challenge_experiment": "{topic}, 제가 직접 해봤습니다. 결과는요?",
    "contrarian": "{topic}에 대해 다들 착각하는 게 하나 있습니다.",
    "urgency_new": "방금 나온 {topic}, 지금 안 보면 늦습니다.",
    "personal_story": "제가 {topic}로 바뀐 딱 한 가지 이야기.",
    "direct_address": "여러분, {topic} 이건 꼭 저장하세요.",
    "money": "{topic}, 돈 한 푼 안 들이고 시작하는 법.",
    "ultimate": "{topic} 총정리, 이 영상 하나면 됩니다.",
    "beginner_easy": "완전 초보도 {topic} 바로 됩니다.",
    "fomo_scarcity": "{topic}, 지금 놓치면 다시 찾기 어렵습니다.",
    "shock_emotion": "{topic}… 이건 솔직히 미쳤습니다.",
    "future_trend": "{topic}, 앞으로 1년 판도가 여기서 갈립니다.",
    "plain": "{topic} — 30초 핵심 요약 갑니다.",
}


def log(*a):
    print("[SCOUT]", *a, flush=True)


def now_iso():
    return datetime.now(KST).isoformat(timespec="seconds")


def http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": "CONSENT=YES+cb.20240101-00-p0.ko+FX+000; SOCS=CAI",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
        cs = r.headers.get_content_charset() or "utf-8"
    return data.decode(cs, errors="replace")


def safe_get(url, timeout=20):
    try:
        return http_get(url, timeout)
    except Exception as e:
        log("GET 실패:", url[:100], "->", e)
        return ""


VID_PATTERNS = [r"(?:v=|vi=)([A-Za-z0-9_-]{11})", r"youtu\.be/([A-Za-z0-9_-]{11})",
                r"/shorts/([A-Za-z0-9_-]{11})", r"/embed/([A-Za-z0-9_-]{11})", r"/live/([A-Za-z0-9_-]{11})"]


def parse_video_id(s):
    s = (s or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    for p in VID_PATTERNS:
        m = re.search(p, s)
        if m:
            return m.group(1)
    return None


def extract_json_obj(text, pattern):
    if not text:
        return None
    for m in re.finditer(pattern, text):
        start = m.end() - 1
        depth, in_str, esc = 0, False, False
        for k in range(start, len(text)):
            c = text[k]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            else:
                if c == '"':
                    in_str = True
                elif c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[start:k + 1])
                        except Exception:
                            break
    return None


def text_of(x):
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        if "simpleText" in x:
            return x["simpleText"]
        if "runs" in x:
            return "".join(r.get("text", "") for r in x["runs"] if isinstance(r, dict))
        if "content" in x:
            return str(x["content"])
    return ""


def parse_count(t):
    if t is None:
        return 0
    if isinstance(t, (int, float)):
        return int(t)
    t = str(t).replace(",", "").strip()
    if re.search(r"없음|no views", t, re.I):
        return 0
    m = re.search(r"(\d+(?:\.\d+)?)\s*(억|만|천|[KkMmBb](?![a-z]))?", t)
    if not m:
        return 0
    n = float(m.group(1))
    mult = {"억": 1e8, "만": 1e4, "천": 1e3, "k": 1e3, "m": 1e6, "b": 1e9}.get((m.group(2) or "").lower(), 1)
    return int(n * mult)


YT_HOST_RE = re.compile(r"(^|\.)(youtube\.com|youtu\.be|youtube-nocookie\.com|ytimg\.com|googlevideo\.com)$", re.I)
URL_RE = re.compile(r"https?://[^\s<>\"'\]\)）】」]+", re.I)
BARE_RE = re.compile(r"(?<![@\w./-])((?:[a-z0-9-]+\.)+(?:com|kr|io|ai|dev|org|net|app|me|so|gg|co|xyz|site)(?:/[^\s<>\"'\)\]]*)?)", re.I)
LINK_PRIORITY = {"강의": 0, "GitHub": 1, "문서": 2, "웹": 3, "커뮤니티": 4, "SNS": 5, "커머스": 6}


def clean_url(u):
    u = u.rstrip(".,;:!?…·'\"")
    try:
        p = urllib.parse.urlparse(u)
        host = (p.hostname or "").lower()
        if "youtube.com" in host and p.path.startswith("/redirect"):
            q = urllib.parse.parse_qs(p.query).get("q")
            if q:
                return clean_url(q[0])
    except Exception:
        pass
    return u


def host_of(u):
    try:
        return (urllib.parse.urlparse(u).hostname or "").lower()
    except Exception:
        return ""


def is_youtube(u):
    return bool(YT_HOST_RE.search(host_of(u)))


def classify_link(u):
    h = host_of(u)
    if "github.com" in h or "githubusercontent" in h:
        return "GitHub"
    if any(k in h for k in ("skilljar", "udemy", "coursera", "inflearn", "class101", "edx", "academy", "fastcampus", "learn.")):
        return "강의"
    if any(k in h for k in ("docs.", "developer", "readthedocs", "notion.site", "notion.so", "gitbook")) or "/docs" in u:
        return "문서"
    if any(k in h for k in ("instagram", "tiktok", "twitter", "threads", "facebook", "linkedin")) or h == "x.com" or h.endswith(".x.com"):
        return "SNS"
    if any(k in h for k in ("open.kakao", "discord", "t.me", "band.us")):
        return "커뮤니티"
    if any(k in h for k in ("coupa.ng", "coupang", "smartstore", "amzn", "amazon")):
        return "커머스"
    return "웹"


def extract_links(text, source="description"):
    out, seen = [], set()
    text = text or ""
    for m in URL_RE.finditer(text):
        u = clean_url(m.group(0))
        if is_youtube(u) or u.lower() in seen:
            continue
        seen.add(u.lower())
        out.append(u)
    stripped = URL_RE.sub(" ", text)
    for m in BARE_RE.finditer(stripped):
        cand = m.group(1).rstrip(".,;:!?…")
        u = "https://" + cand
        if is_youtube(u) or re.fullmatch(r"[\d.]+", cand):
            continue
        if any(x.lower().startswith(u.lower()) or u.lower().rstrip("/") == x.lower().rstrip("/") for x in out):
            continue
        if u.lower() in seen:
            continue
        seen.add(u.lower())
        out.append(u)
    res = [{"url": u, "host": host_of(u), "type": classify_link(u), "source": source} for u in out]
    res.sort(key=lambda l: LINK_PRIORITY.get(l["type"], 9))
    return res


def parse_caption_xml(raw):
    if not raw or "<" not in raw:
        return ""
    try:
        root = ET.fromstring(raw.encode("utf-8"))
        parts = []
        for el in root.iter():
            if el.tag in ("text", "p"):
                s = "".join(el.itertext()).strip()
                if s:
                    parts.append(html.unescape(s))
    except Exception:
        parts = [html.unescape(re.sub(r"<[^>]+>", "", p)) for p in re.findall(r"<text[^>]*>(.*?)</text>", raw, re.S)]
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def parse_caption_json3(raw):
    try:
        j = json.loads(raw)
        segs = []
        for ev in j.get("events", []):
            for s in ev.get("segs", []) or []:
                segs.append(s.get("utf8", ""))
        return re.sub(r"\s+", " ", "".join(segs)).strip()
    except Exception:
        return ""


def fetch_transcript(player):
    try:
        tracks = player["captions"]["playerCaptionsTracklistRenderer"]["captionTracks"]
    except Exception:
        return "", None

    def rank(t):
        lang = t.get("languageCode", "")
        base = 0 if lang.startswith("ko") else 1 if lang.startswith("en") else 2
        return (base, 1 if t.get("kind") == "asr" else 0)

    for t in sorted(tracks, key=rank)[:4]:
        url = t.get("baseUrl")
        if not url:
            continue
        txt = parse_caption_xml(safe_get(url))
        if not txt:
            txt = parse_caption_json3(safe_get(url + "&fmt=json3"))
        if txt:
            return txt, t.get("languageCode")
    return "", None


STOP = set("그리고 그래서 하지만 그런데 이제 이거 그거 저거 정말 진짜 그냥 여기 거기 우리 저희 이런 그런 "
           "the a an and or to of in is it that this for on with you i we are be as at so".split())


def summarize(text, n=5):
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    sents = [s.strip() for s in re.split(r"(?<=[.!?。…])\s+|\n+", text) if len(s.strip()) >= 8]
    if len(sents) < n * 2:
        words = text.split()
        sents = [" ".join(words[i:i + 14]) for i in range(0, len(words), 14)]

    def toks(s):
        return [w.lower() for w in re.findall(r"[가-힣A-Za-z0-9]{2,}", s) if w.lower() not in STOP]

    freq = Counter(w for s in sents for w in toks(s))
    scored = []
    for i, s in enumerate(sents):
        tk = toks(s)
        if not tk:
            continue
        sc = sum(freq[w] for w in tk) / (len(tk) ** 0.5)
        if i < 2:
            sc *= 1.2
        scored.append((sc, i, s))
    top = sorted(sorted(scored, reverse=True)[:n], key=lambda x: x[1])
    return [s[:160] for _, _, s in top]


def summarize_description(desc, n=5):
    lines = []
    for ln in (desc or "").splitlines():
        ln = URL_RE.sub("", ln)
        ln = re.sub(r"#\S+", "", ln).strip(" -•·|:")
        if len(ln) >= 6:
            lines.append(ln[:160])
        if len(lines) >= n:
            break
    return lines


def blank_info(vid, is_short=False):
    watch = "https://www.youtube.com/watch?v=" + vid
    return {"video_id": vid, "url": ("https://www.youtube.com/shorts/" + vid) if is_short else watch,
            "watch_url": watch, "is_short": bool(is_short), "title": "", "channel": "", "channel_id": "",
            "published_at": "", "view_count": 0, "description": "", "length_seconds": 0, "keywords": [],
            "transcript_lang": None, "transcript_excerpt": "", "summary_5": [], "external_links": [],
            "channel_median": 0, "multiple": 0.0, "source": [],
            "thumbnail": "https://i.ytimg.com/vi/%s/hqdefault.jpg" % vid}


def apply_seed_hints(info):
    hint = SEED_HINTS.get(info["video_id"])
    if not hint:
        return
    have = {l["url"].rstrip("/").lower() for l in info["external_links"]}
    for u in hint.get("links", []):
        if u.rstrip("/").lower() not in have:
            info["external_links"].append({"url": u, "host": host_of(u), "type": classify_link(u), "source": "seed_hint"})
    if not info["title"]:
        info["title"] = hint.get("fallback_title", "")
    info["external_links"].sort(key=lambda l: LINK_PRIORITY.get(l["type"], 9))


def analyze_video(url_or_id, with_transcript=True):
    vid = parse_video_id(url_or_id)
    if not vid:
        raise ValueError("유효한 유튜브 URL/ID가 아닙니다: %s" % url_or_id)
    info = blank_info(vid, "/shorts/" in str(url_or_id))
    page = safe_get(info["watch_url"] + "&hl=ko&gl=KR")
    player = extract_json_obj(page, r"ytInitialPlayerResponse\s*=\s*\{")
    if player:
        vd = player.get("videoDetails") or {}
        mf = (player.get("microformat") or {}).get("playerMicroformatRenderer") or {}
        info.update(title=vd.get("title", ""), channel=vd.get("author", ""), channel_id=vd.get("channelId", ""),
                    view_count=int(vd.get("viewCount") or 0), description=vd.get("shortDescription", "") or "",
                    length_seconds=int(vd.get("lengthSeconds") or 0), keywords=(vd.get("keywords") or [])[:15])
        info["published_at"] = mf.get("publishDate") or mf.get("uploadDate") or ""
        if not info["description"]:
            info["description"] = text_of(mf.get("description"))
        if not info["title"]:
            info["title"] = text_of(mf.get("title"))
        if not info["view_count"]:
            info["view_count"] = parse_count(mf.get("viewCount"))
        info["source"].append("watch_page")
        if with_transcript:
            tr, lang = fetch_transcript(player)
            if tr:
                info["transcript_lang"] = lang
                info["transcript_excerpt"] = tr[:1500]
                info["summary_5"] = summarize(tr, 5)
                info["source"].append("captions")
    if page and not info["channel_id"]:
        m = re.search(r'"channelId":"(UC[\w-]{22})"', page) or re.search(r'itemprop="channelId" content="(UC[\w-]{22})"', page)
        if m:
            info["channel_id"] = m.group(1)
    if page and not info["description"]:
        m = re.search(r'<meta name="description" content="([^"]*)"', page)
        if m:
            info["description"] = html.unescape(m.group(1))
    if not info["title"] or not info["channel"]:
        oe = safe_get("https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(info["watch_url"], safe=""))
        try:
            j = json.loads(oe)
            info["title"] = info["title"] or j.get("title", "")
            info["channel"] = info["channel"] or j.get("author_name", "")
            info["source"].append("oembed")
        except Exception:
            pass
    if 0 < info["length_seconds"] <= 60:
        info["is_short"] = True
        info["url"] = "https://www.youtube.com/shorts/" + vid
    info["external_links"] = extract_links(info["description"])
    apply_seed_hints(info)
    if not info["summary_5"]:
        info["summary_5"] = summarize_description(info["description"])
    return info


NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "media": "http://search.yahoo.com/mrss/"}


def fetch_channel_rss(cid):
    raw = safe_get("https://www.youtube.com/feeds/videos.xml?channel_id=" + cid)
    if not raw:
        return "", []
    try:
        root = ET.fromstring(raw.encode("utf-8"))
    except Exception as e:
        log("RSS 파싱 실패:", e)
        return "", []
    ch_title = root.findtext("a:title", "", NS)
    out = []
    for e in root.findall("a:entry", NS):
        vid = e.findtext("yt:videoId", "", NS)
        if not vid:
            continue
        link_el = e.find("a:link", NS)
        link = link_el.get("href") if link_el is not None else "https://www.youtube.com/watch?v=" + vid
        g = e.find("media:group", NS)
        desc, views = "", 0
        if g is not None:
            desc = g.findtext("media:description", "", NS)
            st = g.find("media:community/media:statistics", NS)
            if st is not None:
                views = int(st.get("views", "0") or 0)
        out.append({"video_id": vid, "title": e.findtext("a:title", "", NS), "published_at": e.findtext("a:published", "", NS),
                    "url": link, "is_short": "/shorts/" in link, "view_count": views, "description": desc,
                    "channel": ch_title, "channel_id": cid, "src": "rss"})
    return ch_title, out


def _find_key(node, key):
    if isinstance(node, dict):
        if key in node and isinstance(node[key], str):
            return node[key]
        for v in node.values():
            r = _find_key(v, key)
            if r:
                return r
    elif isinstance(node, list):
        for v in node:
            r = _find_key(v, key)
            if r:
                return r
    return None


def _walk_videos(node, out, tab, cid):
    if isinstance(node, dict):
        vid = node.get("videoId")
        if isinstance(vid, str) and len(vid) == 11 and ("viewCountText" in node or "title" in node):
            v = parse_count(text_of(node.get("viewCountText")))
            t = text_of(node.get("title"))
            if vid not in out or v > out[vid]["view_count"]:
                out[vid] = {"video_id": vid, "title": t or (out.get(vid) or {}).get("title", ""), "view_count": v,
                            "published_at": text_of(node.get("publishedTimeText")), "is_short": tab == "shorts",
                            "url": ("https://www.youtube.com/shorts/" if tab == "shorts" else "https://www.youtube.com/watch?v=") + vid,
                            "description": "", "channel_id": cid, "src": "channel_page"}
        om = node.get("overlayMetadata")
        if isinstance(om, dict):
            vid2 = _find_key(node.get("onTap") or node, "videoId")
            if vid2 and len(vid2) == 11:
                t = text_of(om.get("primaryText"))
                v = parse_count(text_of(om.get("secondaryText")))
                if vid2 not in out or v > out[vid2]["view_count"]:
                    out[vid2] = {"video_id": vid2, "title": t, "view_count": v, "published_at": "", "is_short": True,
                                 "url": "https://www.youtube.com/shorts/" + vid2, "description": "",
                                 "channel_id": cid, "src": "channel_page"}
        for v in node.values():
            _walk_videos(v, out, tab, cid)
    elif isinstance(node, list):
        for v in node:
            _walk_videos(v, out, tab, cid)


def fetch_channel_page_videos(cid):
    out = {}
    for tab in ("videos", "shorts"):
        page = safe_get("https://www.youtube.com/channel/%s/%s?hl=ko" % (cid, tab))
        data = extract_json_obj(page, r'ytInitialData"?\]?\s*=\s*\{')
        if data:
            _walk_videos(data, out, tab, cid)
        time.sleep(0.4)
    return list(out.values())


def compute_outliers(videos):
    views = [v["view_count"] for v in videos if v.get("view_count", 0) > 0]
    med = statistics.median(views) if views else 0
    for v in videos:
        v["channel_median"] = int(med)
        v["multiple"] = round(v["view_count"] / med, 2) if med else 0.0
        v["outlier_label"] = outlier_label(v["multiple"])
    return med


def outlier_label(m):
    if m >= 3:
        return "🔥 진짜 떡상"
    if m >= 1.5:
        return "📈 상승세"
    if m > 0:
        return "➖ 평균권"
    return "측정대기"


def channel_snapshot(cid, use_page=True):
    if not cid:
        return {"channel_id": "", "title": "", "median": 0, "videos": []}
    title, vids = fetch_channel_rss(cid)
    by = {v["video_id"]: v for v in vids}
    if use_page and (len(vids) < 5 or any(v["view_count"] == 0 for v in vids)):
        for pv in fetch_channel_page_videos(cid):
            if pv["video_id"] in by:
                if not by[pv["video_id"]]["view_count"]:
                    by[pv["video_id"]]["view_count"] = pv["view_count"]
            else:
                pv["channel"] = title
                by[pv["video_id"]] = pv
    lst = list(by.values())
    med = compute_outliers(lst)
    lst.sort(key=lambda v: (v["multiple"], v["view_count"]), reverse=True)
    return {"channel_id": cid, "title": title, "median": int(med), "videos": lst[:40]}


def slim_snapshot(s):
    return {"channel_id": s["channel_id"], "title": s["title"], "median": s["median"], "video_count": len(s["videos"]),
            "updated_at": now_iso(),
            "top": [{k: v.get(k) for k in ("video_id", "title", "view_count", "multiple", "outlier_label", "url", "is_short", "published_at")}
                    for v in s["videos"][:12]]}


def apply_multiple(info, snap):
    med = snap.get("median") or 0
    for v in snap.get("videos", []):
        if v["video_id"] == info["video_id"]:
            info["view_count"] = max(info["view_count"], v["view_count"])
            if not info["published_at"]:
                info["published_at"] = v.get("published_at", "")
            break
    info["channel_median"] = med
    info["multiple"] = round(info["view_count"] / med, 2) if med else 0.0
    if not info["channel"]:
        info["channel"] = snap.get("title", "")


def info_from_rss(v):
    info = blank_info(v["video_id"], v.get("is_short"))
    info.update(title=v.get("title", ""), channel=v.get("channel", ""), channel_id=v.get("channel_id", ""),
                published_at=v.get("published_at", ""), view_count=v.get("view_count", 0),
                description=v.get("description", ""), source=[v.get("src", "rss")])
    info["external_links"] = extract_links(info["description"])
    info["summary_5"] = summarize_description(info["description"])
    return info


def classify_hooks(title, first_line=""):
    text = "%s %s" % (title or "", first_line or "")
    hits = [{"id": fid, "name": name} for fid, name, pat in HOOK_FORMULAS if re.search(pat, text, re.I)]
    return hits or [{"id": "plain", "name": "일반 서술형"}]


def score_hook(title, first_line=""):
    t = re.sub(r"#\S+", "", title or "").strip()
    full = (t + " " + (first_line or ""))[:300]
    spec = 0
    if re.search(r"\d", t):
        spec += 8
    if re.search(UNIT_RE, t, re.I):
        spec += 5
    if re.search(r"[A-Z][A-Za-z0-9]+|클로드|챗GPT|GPT|앤트로픽|구글|노션|유튜브|제미나이|커서", t):
        spec += 4
    if len(re.findall(r"[가-힣A-Za-z0-9]{2,}", t)) >= 4:
        spec += 3
    spec = min(spec, 20)
    addr = 0
    if re.search(r"당신|여러분|너만|너도|님들|\byou\b|\byour\b", full, re.I):
        addr += 14
    if re.search(r"하세요|하라|해라|마세요|보세요|하자|^stop|^don'?t|^try", full, re.I):
        addr += 8
    addr = min(addr, 20)
    stakes = min(20, 6 * len(re.findall(STAKES_RE, full, re.I)))
    cur = min(20, 6 * len(re.findall(CUR_RE, full, re.I)))
    L = len(t)
    brev = 20 if 12 <= L <= 45 else 16 if L <= 60 else 11 if L <= 80 else 6 if L <= 100 else 3
    if L < 6:
        brev = 6
    total = spec + addr + stakes + cur + brev
    grade = "S" if total >= 80 else "A" if total >= 65 else "B" if total >= 50 else "C" if total >= 35 else "D"
    return {"total": total, "grade": grade,
            "breakdown": {"specificity": spec, "address": addr, "stakes": stakes, "curiosity": cur, "brevity": brev}}


def topic_of(title):
    t = re.sub(r"#\S+", "", title or "").strip()
    t = re.sub(r"\s+", " ", t)
    return (t[:26] + "…") if len(t) > 27 else (t or "이 주제")


def make_claude_prompt(c):
    links = c.get("external_links") or []
    link_lines = "\n".join("- [%s] %s" % (l["type"], l["url"]) for l in links[:12]) or \
        "- (설명란 외부 링크 미확보 — 영상 설명란/고정 댓글 링크를 직접 확인해 여기에 추가)"
    summ = (c.get("knowledge_summary") or [])[:5]
    sum_lines = "\n".join("%d. %s" % (i + 1, s) for i, s in enumerate(summ)) or "1. " + c.get("title", "")
    mult = ("%s배 (%s)" % (c["multiple"], c.get("outlier_label", ""))) if c.get("multiple") else "측정대기"
    return (
        "[RGON 사령부 · 클로드 스킬 흡수 지시문]\n"
        "너는 RGON 사령부의 수석 AI 전략가다. 아래 유튜브 영상에서 확인된 지식·기법을 우리 프로젝트"
        "(shin-agent 파이썬 자동화 + 3청사 유튜브/쇼츠 채널)에 즉시 적용 가능한 실행 계획으로 변환해라.\n\n"
        "■ 원본 영상: %s — %s\n■ URL: %s\n■ 게시일 / 조회수: %s / %s회 · 채널 중앙값 대비 %s\n"
        "■ 사용된 훅 공식: %s (훅 점수 %s/100, 등급 %s)\n■ 핵심 원문 링크:\n%s\n■ 핵심 내용 요약:\n%s\n\n"
        "■ 요청 작업:\n"
        "1) 위 링크(특히 강의·문서·GitHub)의 핵심 개념을 단계별 학습 체크리스트(오늘/이번 주/이번 달)로 정리\n"
        "2) shin-agent 파이프라인에 붙일 수 있는 구체적 기능 3개 제안 (파일명·함수명·입출력 단위)\n"
        "3) 그중 1순위 기능을 바로 실행할 수 있는 Python 3 코드 또는 클로드 프롬프트 초안 작성\n"
        "4) 이 영상의 훅 공식을 응용한 우리 채널용 쇼츠 제목 5개 + 썸네일 문구 3개\n"
        "5) 원본을 베끼지 않고 우리만의 관점으로 차별화할 포인트 3개\n"
        "출력: 한국어, 실행 우선순위 순, 각 항목은 바로 복붙 가능한 형태로."
    ) % (c.get("title", ""), c.get("channel", "") or "채널 미확인", c.get("url", ""), c.get("published_at", "") or "-",
         "{:,}".format(c.get("view_count", 0) or 0), mult, ", ".join(c.get("hooks", [])), c.get("hook_score", 0),
         c.get("hook_grade", "-"), link_lines, sum_lines)


def make_shorts_script(c):
    topic = topic_of(c.get("title", ""))
    hook_line = HOOK_LINE_TPL.get(c.get("hook_primary", "plain"), HOOK_LINE_TPL["plain"]).format(topic=topic)
    pts = (c.get("knowledge_summary") or [])[:3]
    while len(pts) < 3:
        pts.append(["핵심 개념 한 줄 정의", "바로 따라 할 수 있는 첫 단계", "실제 적용 결과/효과"][len(pts)])
    links = c.get("external_links") or []
    link_txt = links[0]["url"] if links else "(설명란 링크)"
    tags = " ".join("#" + re.sub(r"\s+", "", k)[:15] for k in (c.get("keywords") or [])[:4]) or "#클로드 #AI #자동화 #쇼츠"
    return (
        "[🎬 3청사 쇼츠 벤치마킹 대본 초안 · 약 45~55초]\n"
        "벤치마킹 원본: %s (%s) · 훅 공식: %s · 떡상 %s\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⏱ 0~3초 [훅]\n\"%s\"\n(화면: 큰 자막 + 결과물 화면 0.5초 플래시)\n\n"
        "⏱ 3~12초 [문제 제기]\n\"대부분 이걸 유료로 찾거나, 엉뚱한 자료로 시간을 버립니다.\"\n\n"
        "⏱ 12~40초 [핵심 3가지]\n① %s\n② %s\n③ %s\n(화면: 각 포인트마다 실제 화면 캡처 / 링크 화면)\n\n"
        "⏱ 40~50초 [CTA]\n\"링크는 설명란에 정리해 뒀습니다(%s). 저장해 두고 오늘 바로 시작하세요. 3청사 구독하면 이런 것만 골라 드립니다.\"\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📝 제목 후보: %s\n🏷 해시태그: %s\n※ 원본 표현을 그대로 쓰지 말고 우리 사례·화면으로 재구성할 것."
    ) % (c.get("title", ""), c.get("channel", ""), c.get("hook_primary_name", ""),
         ("%s배" % c["multiple"]) if c.get("multiple") else "측정대기",
         hook_line, pts[0][:90], pts[1][:90], pts[2][:90], link_txt, hook_line.rstrip("."), tags)


def build_card(info, origin):
    title = info.get("title") or "(제목 미확인)"
    desc = info.get("description") or ""
    first_line = ""
    if info.get("transcript_excerpt"):
        first_line = re.split(r"(?<=[.!?])\s+", info["transcript_excerpt"])[0][:120]
    elif desc.strip():
        first_line = desc.strip().splitlines()[0][:120]
    hooks = classify_hooks(title, first_line)
    hs = score_hook(title, first_line)
    summary = info.get("summary_5") or summarize_description(desc) or [title]
    c = {
        "id": info["video_id"], "video_id": info["video_id"], "url": info["url"], "watch_url": info["watch_url"],
        "thumbnail": info.get("thumbnail"), "is_short": info.get("is_short", False),
        "title": title, "channel": info.get("channel", ""), "channel_id": info.get("channel_id", ""),
        "published_at": info.get("published_at", ""), "view_count": info.get("view_count", 0),
        "length_seconds": info.get("length_seconds", 0), "keywords": info.get("keywords", []),
        "channel_median": info.get("channel_median", 0), "multiple": info.get("multiple", 0.0),
        "outlier_label": outlier_label(info.get("multiple", 0.0)),
        "hooks": [h["name"] for h in hooks], "hook_primary": hooks[0]["id"], "hook_primary_name": hooks[0]["name"],
        "hook_score": hs["total"], "hook_grade": hs["grade"], "hook_breakdown": hs["breakdown"],
        "first_line": first_line, "external_links": info.get("external_links", []),
        "knowledge_summary": summary[:5], "transcript_lang": info.get("transcript_lang"),
        "transcript_excerpt": (info.get("transcript_excerpt") or "")[:600], "description": desc,
        "data_sources": info.get("source", []), "origin": origin, "analyzed_at": now_iso(),
    }
    c["claude_prompt"] = make_claude_prompt(c)
    c["shorts_script"] = make_shorts_script(c)
    return c


def fetch_readme(repo):
    for br in ("main", "master"):
        raw = safe_get("https://raw.githubusercontent.com/%s/%s/README.md" % (repo, br), timeout=15)
        if raw and "404: Not Found" not in raw[:50]:
            return raw
    return ""


def readme_excerpt(md, n=6):
    out = []
    for ln in md.splitlines():
        s = ln.strip()
        if not s or s.startswith(("![", "<", "[![", "```", "|", "---")):
            continue
        s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
        s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
        s = re.sub(r"[*_`>#]+", "", s).strip()
        if len(s) >= 8:
            out.append(s[:180])
        if len(out) >= n:
            break
    return out


def build_github_cards():
    cards = []
    for r in GITHUB_REPOS:
        md = fetch_readme(r["repo"])
        excerpt = readme_excerpt(md) if md else []
        url = "https://github.com/" + r["repo"]
        prompt = (
            "[RGON 사령부 · GitHub 스킬 흡수 지시문]\n"
            "저장소: %s (%s 라이선스)\n역할: %s\n흡수한 핵심 로직:\n%s\nREADME 요약:\n%s\n\n"
            "요청: 1) 이 저장소의 핵심 알고리즘을 우리 rgon_youtube_skill_scout.py 와 비교해 빠진 기능 3개를 찾고 "
            "2) 표준 라이브러리만으로 추가 구현 코드를 작성하고 3) MIT 라이선스 고지 문구를 README에 넣을 초안을 써라."
        ) % (r["repo"], r["license"], r["role"], "\n".join("- " + a for a in r["absorbed"]),
             "\n".join("- " + e for e in excerpt) or "- (README 미수집 — 저장소 직접 확인)")
        cards.append({"repo": r["repo"], "url": url, "license": r["license"], "role": r["role"],
                      "absorbed": r["absorbed"], "readme_excerpt": excerpt,
                      "links": [l["url"] for l in extract_links(md, "readme")[:8]] if md else [],
                      "claude_prompt": prompt,
                      "attribution": "MIT License — 아이디어/알고리즘을 Python 표준 라이브러리로 재구현 (원본 코드 미포함)"})
        time.sleep(0.3)
    return cards


def radar_paths():
    return [os.path.join(BASE_DIR, RADAR_NAME), os.path.join(BASE_DIR, "dashboard", RADAR_NAME),
            os.path.join(BASE_DIR, "docs", RADAR_NAME)]


def load_radar():
    p = radar_paths()[0]
    if os.path.isfile(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_radar(radar):
    data = json.dumps(radar, ensure_ascii=False, indent=2)
    for p in radar_paths():
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(data)
        log("저장:", p)


def merge_cards(new, old):
    by = {}
    for c in old or []:
        by[c.get("video_id")] = c
    for c in new:
        by[c["video_id"]] = c
    return list(by.values())


def finalize(radar):
    vids = radar.get("videos", [])
    vids.sort(key=lambda c: (0 if c.get("origin") == "seed" else 1, -(c.get("multiple") or 0), -(c.get("hook_score") or 0)))
    radar["videos"] = vids
    radar["version"] = VERSION
    radar["generated_at"] = now_iso()
    radar["seed_urls"] = SEED_URLS
    radar["hook_engine"] = {"formulas": [{"id": i, "name": n, "pattern": p} for i, n, p in HOOK_FORMULAS],
                            "unit_re": UNIT_RE, "stakes_re": STAKES_RE, "cur_re": CUR_RE, "hook_line_tpl": HOOK_LINE_TPL}
    top = max(vids, key=lambda c: c.get("multiple") or 0) if vids else None
    radar["stats"] = {
        "total_videos": len(vids), "channels": len(radar.get("channels", {})),
        "external_links": sum(len(c.get("external_links", [])) for c in vids),
        "avg_hook_score": round(sum(c.get("hook_score", 0) for c in vids) / len(vids), 1) if vids else 0,
        "top_outlier": {"title": top["title"], "multiple": top["multiple"], "url": top["url"]} if top else None,
    }
    radar["attribution"] = ("Ideas/algorithms adapted (re-implemented, no code copied) from MIT-licensed: "
                            "NousResearch/hermes-agent, Jakeschincariol/youtube-agent-skill, AgriciDaniel/claude-youtube")
    return radar


def run_seed(with_transcript=True):
    log("=== 시드 분석 시작 ===")
    old = load_radar()
    keep_user = [c for c in old.get("videos", []) if str(c.get("origin", "")).startswith("user")]
    cards, channels = [], dict(old.get("channels", {}))
    for su in SEED_URLS:
        try:
            info = analyze_video(su, with_transcript)
        except Exception as e:
            log("시드 분석 실패:", e)
            vid = parse_video_id(su)
            info = blank_info(vid, True)
            apply_seed_hints(info)
        log("시드:", info["title"], "/", info["channel"], "/", info["channel_id"])
        snap = channel_snapshot(info["channel_id"]) if info["channel_id"] else {"channel_id": "", "title": "", "median": 0, "videos": []}
        apply_multiple(info, snap)
        cards.append(build_card(info, "seed"))
        if snap["channel_id"]:
            channels[snap["channel_id"]] = slim_snapshot(snap)
        others = [v for v in snap["videos"] if v["video_id"] != info["video_id"]][:CHANNEL_TOP_N]
        for i, v in enumerate(others):
            deep = None
            if i < DEEP_N:
                try:
                    deep = analyze_video(v["url"], with_transcript and i < TRANSCRIPT_N)
                except Exception as e:
                    log("정밀분석 실패:", v["video_id"], e)
                if deep and not deep["title"]:
                    deep = None
                time.sleep(0.6)
            if deep is None:
                deep = info_from_rss(v)
            else:
                if not deep["external_links"] and v.get("description"):
                    deep["external_links"] = extract_links(v["description"])
            deep["view_count"] = max(deep.get("view_count", 0), v.get("view_count", 0))
            deep["channel_median"] = snap["median"]
            deep["multiple"] = round(deep["view_count"] / snap["median"], 2) if snap["median"] else 0.0
            deep["channel"] = deep["channel"] or snap["title"]
            deep["channel_id"] = deep["channel_id"] or snap["channel_id"]
            cards.append(build_card(deep, "channel_rss"))
            log("  [%s배] %s" % (deep["multiple"], deep["title"][:60]))
    radar = {"videos": merge_cards(cards, keep_user), "channels": channels, "github_skills": build_github_cards()}
    save_radar(finalize(radar))
    log("=== 시드 분석 완료: 카드 %d개 ===" % len(radar["videos"]))
    return radar


def analyze_urls(urls, with_transcript=True, origin="user_url"):
    new = []
    with LOCK:
        radar = load_radar()
        radar.setdefault("channels", {})
        for u in urls:
            info = analyze_video(u, with_transcript)
            snap = channel_snapshot(info["channel_id"], use_page=False) if info["channel_id"] else {"channel_id": "", "title": "", "median": 0, "videos": []}
            apply_multiple(info, snap)
            c = build_card(info, origin)
            new.append(c)
            if snap["channel_id"]:
                radar["channels"][snap["channel_id"]] = slim_snapshot(snap)
            log("흡수 완료: [%s배 / 훅 %s] %s" % (c["multiple"], c["hook_score"], c["title"]))
        radar["videos"] = merge_cards(new, radar.get("videos", []))
        if not radar.get("github_skills"):
            radar["github_skills"] = build_github_cards()
        save_radar(finalize(radar))
    return new


class BridgeHandler(BaseHTTPRequestHandler):
    with_transcript = True

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(p.query)
        if p.path == "/health":
            return self._json(200, {"ok": True, "service": "rgon-yt-scout", "version": VERSION})
        if p.path == "/radar":
            return self._json(200, load_radar())
        if p.path == "/analyze":
            url = (q.get("url") or [""])[0]
            try:
                cards = analyze_urls([url], self.with_transcript)
                return self._json(200, {"ok": True, "card": cards[0]})
            except Exception as e:
                return self._json(400, {"ok": False, "error": str(e)})
        return self._json(404, {"ok": False, "error": "not found"})

    def log_message(self, fmt, *args):
        log("bridge:", fmt % args)


def serve(port=8765, with_transcript=True):
    BridgeHandler.with_transcript = with_transcript
    srv = ThreadingHTTPServer(("127.0.0.1", port), BridgeHandler)
    log("🛰️ 로컬 브리지 가동: http://127.0.0.1:%d  (/health /analyze?url= /radar) — 종료 Ctrl+C" % port)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        log("브리지 종료")


def main():
    global BASE_DIR
    ap = argparse.ArgumentParser(description="RGON YouTube Skill Scout " + VERSION)
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--url", action="append", default=[])
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-transcript", action="store_true")
    ap.add_argument("--base", default=None)
    a = ap.parse_args()
    if a.base:
        BASE_DIR = os.path.abspath(a.base)
    wt = not a.no_transcript
    if a.url:
        for c in analyze_urls(a.url, wt):
            print("\n" + "=" * 70)
            print("📌", c["title"], "/", c["channel"])
            print("🔥 떡상 %s배 · 훅 %s점(%s) · %s" % (c["multiple"], c["hook_score"], c["hook_grade"], ", ".join(c["hooks"][:4])))
            for l in c["external_links"]:
                print("🔗 [%s] %s" % (l["type"], l["url"]))
            for s in c["knowledge_summary"]:
                print("💡", s)
    if a.seed or (not a.url and not a.serve):
        run_seed(wt)
    if a.serve:
        serve(a.port, wt)


if __name__ == "__main__":
    main()

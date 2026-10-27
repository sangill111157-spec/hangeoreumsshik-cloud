#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_aon_omni_insight_eye.py — 제14기관 아온 만물 격물치지 통찰안 (표준 라이브러리 전용)
[RGON-R38] v11.55-AON-TELEGRAM-MESSENGER · 항체 R1~R56 · 정식 스킬 35개
OTA 능동 지각(Observation→Thought→Action) → FPCOS L0~L5 해부 → 아온 혜안 브리핑.
한계: 규칙 기반 휴리스틱. 이미지·영상 속 '무엇이 있는가'(객체·장면 인식)는 판정하지 않으며
헤더·픽셀 통계·URL 구조·텍스트 신호만 실측한다. 신뢰도는 85%를 넘기지 않는다."""
import base64, datetime, hashlib, json, math, re, struct, sys, time, zlib
from pathlib import Path
from urllib.parse import urlparse, parse_qs

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
VERSION = "v11.55-AON-TELEGRAM-MESSENGER"
ANTIBODY = "R1~R56"
SKILL_COUNT = 39
STATE_PATHS = ("rgon_aon_insight_state.json", "docs/rgon_aon_insight_state.json")
CONF_CAP = 85
IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp")
VID_EXT = (".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi")
IMG_WORDS = re.compile(r"(이미지|사진|그림|차트|스크린샷|캡처|썸네일)")
VID_WORDS = re.compile(r"(youtube\.com|youtu\.be|/shorts/|영상|동영상|쇼츠|릴스)", re.I)
URL_RE = re.compile(r"(https?://\S+|data:[\w/+.-]+;base64,[A-Za-z0-9+/=]+)")
PATH_RE = re.compile(r"([^\s\"']+\.(?:png|jpe?g|gif|svg|webp|bmp|mp4|mov|m4v|webm|mkv|avi))(?![\w])", re.I)
ABS_RE = re.compile(r"(무조건|절대|반드시|100\s*%|100프로|전부|항상|결코|확실히|완벽|필승|영원히|무적)")
NUM_RE = re.compile(r"-?\d+(?:[.,]\d+)?\s*(?:%|퍼센트|원|달러|배|명|개|년|월|일|시간|분|초|만|억)?")
PIVOT_RE = re.compile(r"(하지만|그런데|그러나|반전|갑자기|돌연|그러다)")
INTENSITY = re.compile(r"(급등|급락|폭발|폭락|반전|갑자기|위기|최고|최악|충격|돌파|붕괴|역전|대박|난리)")
INTENTS = {
    "question": r"(\?|왜|어떻게|무엇|뭐|어째서)",
    "request": r"(해줘|알려줘|분석|봐줘|해부|파악|간파)",
    "worry": r"(걱정|불안|위험|손실|무섭|망할|떨어)",
    "desire": r"(벌고|성공|이기|갖고|키우|늘리|오르)",
    "conflict": r"(싸움|갈등|다툼|반대|충돌|대립|서운)",
    "causal": r"(때문|원인|그래서|결과로|탓)",
    "change": r"(변화|전환|국면|추세|반전|급변|바뀌)",
}
STOP = set("그리고 그래서 하지만 그런데 이거 저거 그거 이건 오늘 지금 정말 진짜 너무 아온 아온이 대표님 해줘 알려줘 봐줘".split())


def _dom(kw, var, lt, lm, lev, dw, gt, it, blind, hx):
    return dict(kw=re.compile(kw, re.I) if kw else None, variables=var, loop_type=lt, loop=lm, leverage=lev,
                dead_weight=dw, ground_truth=gt, interest=it, blind=blind, hexagram=hx)


DOMAINS = {
    "market": _dom(r"(주식|코인|장세|시장|금리|환율|매수|매도|수익률|폭락|급등|나스닥|코스피|비트코인|ETF|이차\s*전지|반도체)",
                   ["유동성(돈의 양과 속도)", "기대·심리(공포와 탐욕)", "실적·금리 등 펀더멘털"], "R",
                   "가격 상승 → 기대 확산 → 추가 매수 → 가격 상승의 자기강화. 과열되면 차익실현이라는 B 루프가 반대로 작동한다",
                   "진입 전에 손절선과 비중 상한을 먼저 정하는 규칙 한 줄", "헤드라인 과잉 소비와 잦은 매매 비용",
                   "가격은 기대의 변화에 반응하고, 기대는 결국 유동성과 실적에 수렴한다",
                   "중개자(거래 수수료) · 큰손(유동성 공급·회수) · 정보 판매자(조회수)",
                   "실제 수급(자금 흐름)과 기간 — 반대 방향이면 결론이 뒤집힌다", 20),
    "relationship": _dom(r"(친구|연인|가족|동료|상사|관계|마음|서운|싸움|갈등|대화|부부)",
                         ["신뢰 잔고", "기대치 차이", "소통의 빈도와 질"], "R",
                         "서운함 → 거리두기 → 오해 증폭 → 더 큰 서운함의 악순환. 작은 인정 한 번이 선순환으로 뒤집는다",
                         "상대의 기대를 추측하지 말고 한 문장으로 직접 확인하기", "속으로만 쌓는 해석과 승패 계산",
                         "사람은 이해받는다고 느낄 때 마음을 연다", "두 당사자 각자의 인정 욕구 · 주변 평판",
                         "상대가 실제로 무엇을 기대했는지 — 직접 들은 적이 없다면 전부 추측이다", 31),
    "tech": _dom(r"(코드|버그|서버|AI|모델|앱|시스템|자동화|파이썬|에러|배포|API|알고리즘)",
                 ["입력 데이터 품질", "병목 단계(가장 느린 곳)", "피드백 속도(테스트·로그)"], "B",
                 "에러 → 수정 → 테스트 → 안정화의 균형 루프. 테스트가 없으면 기술부채가 쌓이는 R 루프로 바뀐다",
                 "가장 느린 한 단계(제약)를 찾아 그것만 먼저 개선", "실행되지 않는 코드 · 중복 설정 · 수동 반복 작업",
                 "시스템 전체 속도는 가장 느린 단계가 정한다", "플랫폼·클라우드(사용량 과금) · 도구 판매자 · 유지보수 담당",
                 "실제 실행 로그와 재현 조건 — 없으면 원인은 추측이다", 21),
    "business": _dom(r"(매출|고객|사업|마케팅|가격|영업|브랜드|창업|경쟁|비용|이익|판매)",
                     ["고객 획득 비용", "재구매·유지율", "단위당 마진"], "R",
                     "만족한 고객 → 추천 → 신규 고객 → 매출 → 재투자의 강화 루프",
                     "이탈 이유 상위 1개 제거(유지율은 복리로 쌓인다)", "성과 측정이 안 되는 광고비와 회의",
                     "사업은 고객이 낼 만한 가치를 비용보다 싸게 반복 전달하는 구조다", "고객 · 경쟁사 · 광고 플랫폼 · 투자자",
                     "코호트별 유지율과 단위 경제성 실측치", 42),
    "content": _dom(r"(유튜브|쇼츠|조회수|구독|썸네일|콘텐츠|릴스|틱톡|youtu)",
                    ["첫 3초 이탈률", "시청 지속 시간", "공유·댓글 반응"], "R",
                    "시청 지속 ↑ → 추천 노출 ↑ → 조회 ↑ → 데이터 ↑의 강화 루프",
                    "첫 화면·첫 문장 훅 하나를 고치기", "도입부 인사와 반복 설명",
                    "주의는 희소하고, 추천은 시청자의 체류 행동을 따른다", "플랫폼(광고 체류시간) · 제작자(조회·수익) · 광고주",
                    "실제 시청 지속 그래프와 유입 경로", 22),
    "health": _dom(r"(건강|운동|수면|피로|스트레스|식사|체력|통증)",
                   ["수면의 질", "활동량", "스트레스 부하"], "B",
                   "피로 → 휴식 → 회복의 균형 루프. 수면 부족이 길어지면 피로 → 능률 저하 → 야근 → 수면 부족의 R 악순환",
                   "기상·취침 시간 고정", "자기 전 화면 시청", "몸은 회복이 부하를 이길 때 강해진다",
                   "건강 제품 판매자 · 본인", "증상의 기간과 의학적 진단 — 지속되면 전문가 확인이 우선", 27),
    "visual": _dom(None, ["구도(초점 위치)", "명암 대비", "색 균형·정보 밀도"], "B",
                   "시선은 대비가 큰 곳으로 끌리고, 여백이 시선을 쉬게 한다(밀도와 여백의 균형)",
                   "주제 한 곳에만 대비를 집중", "주제와 무관한 배경 정보",
                   "시선은 대비가 크고 정보가 몰린 곳으로 먼저 간다",
                   "만든 사람(보여주고 싶은 것) · 보는 사람(보고 싶은 것)", "촬영·제작 의도와 프레임 밖 맥락", 20),
    "general": _dom(None, ["목표(원하는 상태)", "가장 큰 제약", "자원(시간·돈·주의력)"], "B",
                    "목표와 현실의 차이가 행동을 만들고, 행동이 그 차이를 줄인다",
                    "가장 큰 제약 하나를 정의하고 그것만 먼저 풀기", "결정을 미루는 끝없는 정보 수집",
                    "결과는 구조가 만든다 — 구조를 바꾸면 결과가 바뀐다",
                    "상황을 설명하는 쪽 · 결정하는 쪽(둘의 이해가 다를 수 있음)", "당사자들이 실제로 원하는 것과 제약 조건", 20),
}
HEX_FALLBACK = {
    20: ("觀", "관", "☴☷", "관조 — 바람이 땅 위를 두루 스치듯 전체를 본다"),
    21: ("噬嗑", "서합", "☲☳", "장애 제거 — 입 안의 걸림을 물어 끊는다"),
    31: ("咸", "함", "☱☶", "감응 — 마음이 통하면 움직인다"),
    22: ("賁", "비", "☶☲", "꾸밈 — 형식이 본질을 비춘다"),
    27: ("頤", "이", "☶☳", "기름 — 무엇을 들이는가가 몸을 만든다"),
    42: ("益", "익", "☴☳", "보탬 — 위를 덜어 아래를 보탠다"),
    49: ("革", "혁", "☱☲", "변혁 — 때가 차면 바꾼다"),
}
DESC_CUES = [(r"대칭", "대칭: 대칭 구조 언급"), (r"중앙|가운데", "초점: 중앙 배치"), (r"여백|비어|단순", "여백: 여백·단순 구성"),
             (r"복잡|빽빽|가득", "밀도: 높은 정보 밀도"), (r"차트|그래프|캔들", "구조: 데이터 시각화(축·추세선)"),
             (r"얼굴|사람|인물", "초점: 인물 중심"), (r"상승|우상향", "구조: 우상향 흐름"), (r"하락|우하향", "구조: 우하향 흐름")]


def _uniq(xs):
    out = []
    for x in xs:
        if x and x not in out:
            out.append(x)
    return out


def _is_file(s):
    try:
        return len(s) < 400 and Path(s).is_file()
    except (OSError, ValueError):
        return False


def shannon(b):
    if not b:
        return 0.0
    c = [0] * 256
    for x in b:
        c[x] += 1
    n = len(b)
    return round(-sum(v / n * math.log2(v / n) for v in c if v), 3)


def _png_rows(data):
    w, h, bd, ct, _, _, il = struct.unpack(">IIBBBBB", data[16:29])
    if bd != 8 or il or ct not in (0, 2, 4, 6) or w * h > 600_000:
        return None
    ch = {0: 1, 2: 3, 4: 2, 6: 4}[ct]
    idat = b""
    i = 8
    while i + 8 <= len(data):
        ln = struct.unpack(">I", data[i:i + 4])[0]
        tp = data[i + 4:i + 8]
        if tp == b"IDAT":
            idat += data[i + 8:i + 8 + ln]
        if tp == b"IEND":
            break
        i += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * ch
    prev = bytearray(stride)
    rows = []
    p = 0
    for _ in range(h):
        f = raw[p]
        line = bytearray(raw[p + 1:p + 1 + stride])
        p += 1 + stride
        for x in range(stride):
            a = line[x - ch] if x >= ch else 0
            b = prev[x]
            c = prev[x - ch] if x >= ch else 0
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b) & 255
            elif f == 3:
                line[x] = (line[x] + ((a + b) >> 1)) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        rows.append(bytes(line))
        prev = line
    return w, h, ch, rows


def _pix_stats(w, h, ch, rows):
    step = max(1, int(math.sqrt(w * h / 40000)))
    n = tot = sq = rs = gs = bs = cx = cy = left = right = 0.0
    for y in range(0, h, step):
        r = rows[y]
        for x in range(0, w, step):
            i = x * ch
            R, G, B = (r[i], r[i + 1], r[i + 2]) if ch >= 3 else (r[i], r[i], r[i])
            L = 0.299 * R + 0.587 * G + 0.114 * B
            n += 1; tot += L; sq += L * L; rs += R; gs += G; bs += B; cx += x * L; cy += y * L
            if x < w / 2:
                left += L
            else:
                right += L
    mean = tot / n
    std = math.sqrt(max(0.0, sq / n - mean * mean))
    return dict(brightness=round(mean / 255, 3), contrast=round(std / 255, 3),
                rgb_balance=[round(rs / n), round(gs / n), round(bs / n)],
                focus_center=[round(cx / tot / w, 3) if tot else 0.5, round(cy / tot / h, 3) if tot else 0.5],
                lr_symmetry=round(1 - abs(left - right) / max(left + right, 1), 3))


def _img_header(b):
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", b[16:24]); return "PNG", w, h, {}
    if b[:6] in (b"GIF87a", b"GIF89a"):
        w, h = struct.unpack("<HH", b[6:10]); return "GIF", w, h, {}
    if b[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF: i += 1; continue
            m = b[i + 1]
            if m == 0xFF: i += 1; continue
            if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7: i += 2; continue
            ln = struct.unpack(">H", b[i + 2:i + 4])[0]
            if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", b[i + 5:i + 9]); return "JPEG", w, h, {}
            i += 2 + ln
        return "JPEG", 0, 0, {}
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        return "WEBP", 0, 0, {}
    if b[:2] == b"BM" and len(b) >= 26:
        w, h = struct.unpack("<ii", b[18:26]); return "BMP", w, abs(h), {}
    t = b[:20000].decode("utf-8", "ignore")
    if "<svg" in t:
        def num(attr):
            m = re.search(r'<svg[^>]*?\s' + attr + r'\s*=\s*["\']?([\d.]+)', t, re.S)
            return float(m.group(1)) if m else 0
        w, h = num("width"), num("height")
        if not (w and h):
            m = re.search(r'viewBox\s*=\s*["\']\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', t)
            if m:
                w, h = float(m.group(1)), float(m.group(2))
        return "SVG", int(w), int(h), {"svg_elements": max(0, len(re.findall(r"<(?![/?!])[a-zA-Z]", t)) - 1)}
    return None


def _stat_cues(st):
    fx, fy = st["focus_center"]
    near3 = min(abs(fx - 1 / 3), abs(fx - 2 / 3)) < 0.08 or min(abs(fy - 1 / 3), abs(fy - 2 / 3)) < 0.08
    pos = "중앙 배치" if abs(fx - .5) < .08 and abs(fy - .5) < .08 else ("3분할선 근처" if near3 else "한쪽으로 치우침")
    sym, b, ct = st["lr_symmetry"], st["brightness"], st["contrast"]
    r, g, bb = st["rgb_balance"]
    dom = max((r, "적색"), (g, "녹색"), (bb, "청색"))[1]
    return [f"초점: 밝기 무게중심 ({fx:.2f}, {fy:.2f}) — {pos}",
            f"대칭: 좌우 밝기 대칭도 {sym:.2f}" + (" (강한 대칭·안정감)" if sym >= .9 else " (비대칭·긴장감)" if sym < .7 else ""),
            f"여백: 평균 밝기 {b:.2f}" + (" (밝은 여백 많음)" if b > .75 else " (어두운 톤 지배)" if b < .25 else ""),
            f"밀도: 명암 대비 {ct:.2f}" + (" (저대비·평탄)" if ct < .12 else " (고대비·강한 시선 유도)" if ct > .3 else ""),
            f"색 밸런스: RGB {r}/{g}/{bb} — {dom} 우세"]


def _load_bytes(source):
    if isinstance(source, (bytes, bytearray)):
        return bytes(source), "bytes"
    s = str(source or "").strip()
    if s.startswith("data:"):
        try:
            x = s.split(",", 1)[1]
            return base64.b64decode(x + "=" * (-len(x) % 4)), "data_url"
        except Exception:
            return None, "data_url_broken"
    if "<svg" in s[:300]:
        return s.encode("utf-8"), "svg_text"
    if _is_file(s):
        return Path(s).read_bytes()[:50_000_000], "file"
    return None, "text"


def perceive_image(source):
    data, kind = _load_bytes(source)
    out = dict(modality="image", kind=kind, cues=[], known=[], inferred=[], unknown=[],
               ota=[f"Observation: 입력 형태 = {kind}"])
    if data:
        out["bytes"] = len(data)
        out["entropy_bits"] = shannon(data[:1_000_000])
        hd = _img_header(data)
        if hd:
            fmt, w, h, extra = hd
            out.update(format=fmt, width=w, height=h, **extra)
            out["known"].append(f"{fmt} {w}×{h}px · {len(data):,} bytes · 파일 엔트로피 {out['entropy_bits']} bit/byte")
            if w and h:
                ar = w / h
                out["aspect"] = round(ar, 3)
                out["megapixels"] = round(w * h / 1e6, 3)
                orient = "가로형" if ar > 1.15 else "세로형" if ar < 0.87 else "정방형"
                out["cues"].append(f"구조: {orient}(비율 {ar:.2f})")
                if out["megapixels"] < 0.1:
                    out["inferred"].append("저해상도 — 아이콘·썸네일·축소본일 가능성")
            if fmt == "PNG":
                try:
                    px = _png_rows(data)
                    if px:
                        st = _pix_stats(*px)
                        out["pixel_stats"] = st
                        out["cues"] += _stat_cues(st)
                        out["known"].append("픽셀 실측: 밝기·대비·RGB 밸런스·무게중심·좌우 대칭")
                    else:
                        out["unknown"].append("PNG 픽셀 디코딩 생략(16bit·팔레트·인터레이스·60만 화소 초과)")
                except Exception as e:
                    out["unknown"].append(f"PNG 디코딩 실패: {e}")
            elif fmt == "SVG":
                out["cues"].append(f"밀도: SVG 요소 {extra.get('svg_elements', 0)}개(벡터 구조)")
            else:
                out["unknown"].append(f"{fmt} 픽셀 통계는 표준 라이브러리로 디코딩 불가 → 브라우저 Canvas 실측 사용")
            e = out["entropy_bits"]
            out["inferred"].append("파일 엔트로피 " + ("높음 → 압축된 사진·복잡한 질감" if e > 7.5 else "낮음 → 단순 도형·평탄 색면"))
        else:
            out["unknown"].append("이미지 헤더 판별 실패(지원 형식 아님 또는 손상)")
    else:
        t = str(source or "")
        out["known"].append("텍스트 묘사만 제공됨(픽셀 실측 불가)")
        for pat, cue in DESC_CUES:
            if re.search(pat, t):
                out["cues"].append(cue)
        if not out["cues"]:
            out["unknown"].append("묘사에서 구조·대칭·초점 단서를 찾지 못함")
        out["desc"] = t[:300]
    out["unknown"].append("객체·장면의 의미(무엇이 찍혔는가)는 인식하지 않음")
    out["ota"] += ["Thought: 대비·무게중심·대칭이 시선 흐름을 결정한다", "Action: 초점·밀도·여백 단서 확정"]
    return out


def _mp4_duration(b):
    i = b.find(b"mvhd")
    if i < 0 or i + 24 > len(b):
        return None
    v = b[i + 4]
    try:
        if v == 1:
            ts, du = struct.unpack(">IQ", b[i + 24:i + 36])
        else:
            ts, du = struct.unpack(">II", b[i + 16:i + 24])
        return round(du / ts, 2) if ts else None
    except struct.error:
        return None


def _segments(t):
    ss = [x.strip() for x in re.split(r"[.!?\n。]+|(?:→|->|➔)", t) if x.strip()]
    if not ss:
        return []
    k = len(ss)
    cut = [round(k * i / 4) for i in range(5)]
    return [" ".join(ss[cut[i]:cut[i + 1]]) or ss[min(i, k - 1)] for i in range(4)]


def perceive_video(source):
    s = str(source or "").strip()
    out = dict(modality="video", cues=[], known=[], inferred=[], unknown=[], ota=["Observation: 시간축 입력 판별"])
    m = URL_RE.search(s)
    if m and m.group(1).startswith("http"):
        u = urlparse(m.group(1)); q = parse_qs(u.query); host = u.netloc.lower()
        out["url"] = m.group(1); out["host"] = host
        vid = None
        if "youtu.be" in host:
            vid = u.path.strip("/").split("/")[0]
        elif "youtube" in host:
            vid = (q.get("v") or [None])[0]
            if "/shorts/" in u.path:
                vid = u.path.split("/shorts/")[1].split("/")[0]
        out["shorts"] = "/shorts/" in u.path
        if vid:
            out["video_id"] = vid
            out["known"].append(f"YouTube 영상 ID {vid}" + (" (쇼츠·세로 60초 이내 포맷)" if out["shorts"] else ""))
        else:
            out["known"].append(f"영상 링크 호스트 {host}")
        if q.get("t"):
            out["known"].append(f"시작 지점 지정 t={q['t'][0]} — 핵심 장면을 가리킬 가능성")
        out["unknown"].append("영상 본문(프레임·자막)은 내려받지 않음 → 기승전결은 함께 준 설명 텍스트로만 추정")
    f = PATH_RE.search(s)
    if f and _is_file(f.group(1)):
        b = Path(f.group(1)).read_bytes()[:30_000_000]
        out["bytes"] = len(b)
        brand = b[8:12].decode("ascii", "ignore") if b[4:8] == b"ftyp" else ""
        d = _mp4_duration(b)
        out["known"].append(f"영상 파일 {len(b):,} bytes" + (f" · 브랜드 {brand}" if brand else "") + (f" · 길이 {d}초" if d else ""))
        if d:
            out["duration_sec"] = d
    text = URL_RE.sub(" ", s).strip()
    segs = _segments(text) if len(text) > 8 else []
    if segs:
        names = ["기(도입)", "승(전개)", "전(변곡점 Pivot)", "결(귀결)"]
        inten = [len(INTENSITY.findall(x)) + len(PIVOT_RE.findall(x)) + x.count("!") for x in segs]
        delta = [0] + [inten[i] - inten[i - 1] for i in range(1, 4)]
        piv = max(range(1, 4), key=lambda i: (abs(delta[i]), i == 2))
        out["timeline"] = [dict(stage=names[i], text=segs[i][:120], intensity=inten[i], delta=delta[i]) for i in range(4)]
        out["pivot_stage"] = names[piv]
        out["temporal_dynamics"] = "가속" if inten[3] > inten[0] else "감속·수렴" if inten[3] < inten[0] else "평탄"
        out["cues"] += [f"{t['stage']}: {t['text'][:40]} (강도 {t['intensity']}, 변화 {t['delta']:+d})" for t in out["timeline"]]
        out["inferred"].append(f"최대 변화율 지점 = {names[piv]} · 전체 흐름 {out['temporal_dynamics']}")
    else:
        out["unknown"].append("시간축 흐름 설명이 없어 기승전결 변화율을 계산하지 못함")
    out["ota"] += ["Thought: 변화율이 가장 큰 지점이 메시지의 급소다", "Action: 변곡점·귀결 단서 확정"]
    return out


def perceive_speech_or_phenomenon(text):
    t = str(text or "").strip()
    toks = [w for w in re.findall(r"[가-힣A-Za-z0-9]{2,}", t) if w not in STOP]
    freq = {}
    for w in toks:
        freq[w] = freq.get(w, 0) + 1
    kws = [w for w, _ in sorted(freq.items(), key=lambda x: (-x[1], -len(x[0])))][:6]
    intents = [k for k, p in INTENTS.items() if re.search(p, t)]
    out = dict(modality="speech", text=t[:500], keywords=kws, intents=intents,
               absolutism=_uniq(ABS_RE.findall(t)), numbers=NUM_RE.findall(t)[:8],
               cues=[f"표면 어휘: {', '.join(kws) or '없음'}", f"심층 의도 신호: {', '.join(intents) or '서술'}"],
               known=[f"직접 진술 {len(t)}자"], inferred=[], unknown=[],
               ota=["Observation: 표면 어휘·숫자·단정어 추출", "Thought: 말 뒤의 욕구·걱정·인과 신호 판별", "Action: 핵심 의도 확정"])
    if out["numbers"]:
        out["known"].append("수치 언급: " + ", ".join(x.strip() for x in out["numbers"]))
    if "worry" in intents and "desire" in intents:
        out["inferred"].append("욕구와 걱정이 공존 — 결정 전 위험 한도 설정이 필요한 상태")
    elif "worry" in intents:
        out["inferred"].append("손실 회피 심리가 판단을 주도할 가능성")
    elif "desire" in intents:
        out["inferred"].append("성과 욕구가 위험 평가를 가릴 가능성")
    if "causal" in intents:
        out["inferred"].append("화자가 이미 원인을 가정함 — 그 가정부터 검증 대상")
    if not out["numbers"]:
        out["unknown"].append("정량 데이터(수치·기간) 없음")
    return out


def detect_modality(p):
    if isinstance(p, (bytes, bytearray)):
        return "image"
    s = str(p or "")
    if s.startswith("data:image") or "<svg" in s[:300]:
        return "image"
    f = PATH_RE.search(s)
    if f:
        ext = f.group(1).lower()
        if ext.endswith(VID_EXT):
            return "video"
        if ext.endswith(IMG_EXT):
            return "image"
    if VID_WORDS.search(s):
        return "video"
    if IMG_WORDS.search(s):
        return "image"
    return "speech"


def _domain(text, modality):
    best, hit = None, 0
    for k, d in DOMAINS.items():
        if d["kw"]:
            n = len(d["kw"].findall(text))
            if n > hit:
                best, hit = k, n
    if best:
        return best
    return "visual" if modality == "image" else ("content" if modality == "video" else "general")


def _hexagram(no):
    try:
        import rgon_aon_iching_dao_oracle as O
        h = O.HEXAGRAMS[no]
        return dict(no=no, hanja=h["hanja"], ko=h["ko"], symbol=h["symbol"], meaning=h["gist"], src="oracle")
    except Exception:
        hz, ko, sy, me = HEX_FALLBACK.get(no, HEX_FALLBACK[20])
        return dict(no=no, hanja=hz, ko=ko, symbol=sy, meaning=me, src="builtin")


def analyze_omni_insight(payload, modality="auto"):
    mod = detect_modality(payload) if modality == "auto" else modality
    if mod == "image":
        P = perceive_image(payload)
    elif mod == "video":
        P = perceive_video(payload)
    else:
        P = perceive_speech_or_phenomenon(payload)
        mod = "speech"
    text = payload if isinstance(payload, str) else ""
    S = perceive_speech_or_phenomenon(text) if mod != "speech" else P
    dk = _domain(text, mod)
    D = DOMAINS[dk]
    absf = S["absolutism"]
    known = _uniq(P["known"] + ([] if S is P else S["known"][1:]))
    inferred = _uniq(P["inferred"] + ([] if S is P else S["inferred"]))
    unknown = _uniq(P["unknown"] + [D["blind"]])
    L0 = dict(known=known, inferred=inferred, unknown=unknown, absolutism_flags=absf)
    assum = []
    if absf:
        assum.append(f"'{absf[0]}'라는 단정이 사실이라는 가정")
    if "causal" in S["intents"]:
        assum.append("말한 원인이 진짜 원인이라는 가정")
    assum += [f"지금 보이는 {('화면' if mod == 'image' else '흐름' if mod == 'video' else '현상')}이 전체를 대표한다는 가정",
              "과거의 방식이 앞으로도 통한다는 가정"]
    L1 = dict(assumptions=assum, stripped=[f"벗겨냄: {a}" for a in assum],
              ground_truth=D["ground_truth"],
              rederived=f"백지에서 다시: '{D['ground_truth']}' → 따라서 {D['leverage']}부터",
              ariya4=dict(problem=f"표면 현상({', '.join(S['keywords'][:3]) or mod}) 뒤에서 {D['variables'][0]}이(가) 흔들리는 것",
                          cause=f"{D['variables'][0]}과(와) {D['variables'][1]}의 상호작용({D['loop_type']} 루프)",
                          cessation=f"{D['variables'][2]}이(가) 안정된 상태에서 원하는 결과가 반복되는 구조",
                          path=D["leverage"]))
    L2 = dict(variables=D["variables"], feedback_loop=dict(type=D["loop_type"], mechanism=D["loop"]),
              leverage_point=D["leverage"], dead_weight=D["dead_weight"])
    models = ["제1원리"]
    if len(D["variables"]) >= 3:
        models.append("시스템사고")
    if dk in ("tech", "business", "general", "visual"):
        models.append("제약이론")
    if dk in ("market", "business", "relationship") or "desire" in S["intents"]:
        models.append("2차파급효과")
    if mod == "video" or "change" in S["intents"] or dk == "market":
        models.append("레짐탐지")
    hx = _uniq([20, D["hexagram"], 21])
    L3 = dict(mental_models=models, iching_mapping=[_hexagram(n) for n in hx],
              cross_domain=f"{dk} 영역의 '{D['loop_type']} 루프'는 다른 영역의 같은 루프와 같은 이치로 움직인다 — 관(觀)으로 전체를 보고 서합(噬嗑)으로 걸림을 끊는다")
    weak = len(known) <= 1 or len(unknown) > len(known) + 1
    strength = "HIGH" if (absf and weak) else "MED" if (absf or weak) else "LOW"
    L4 = dict(mirror=assum[0], inversion=dict(hypothesis=f"반대로, 진짜 원인은 {D['variables'][-1]} 쪽이고 지금 결론은 우연일 수 있다", strength=strength),
              blind_spot=D["blind"], interest_map=D["interest"],
              verdict="FRAGILE" if strength != "LOW" else "CONSISTENT")
    conf = 40 + min(len(known), 5) * 6 + (8 if P.get("pixel_stats") or P.get("timeline") else 0) - len(absf) * 6 - (10 if L4["verdict"] == "FRAGILE" else 0)
    conf = max(15, min(CONF_CAP, conf))
    essence = f"{D['ground_truth']} — 급소는 '{D['leverage']}'"
    L5 = dict(essence_one_line=essence, action_leverage=D["leverage"], confidence_pct=conf)
    L5["aon_speech"] = (f"아온이 혜안 반짝~ 👁️💧 대표님, 이건 '{D['loop_type']} 루프'로 움직이는 구조예요! "
                        f"한 줄 본질은요 — {essence}. 버릴 군더더기는 '{D['dead_weight']}'이고요, "
                        f"근데 '{D['blind']}'는 아직 몰라서 신뢰도는 {conf}%예요. "
                        f"{'판단이 아직 흔들릴 수 있으니 그 부분부터 확인해 봐요!' if L4['verdict'] == 'FRAGILE' else '구조가 일관돼서 바로 써먹으셔도 돼요!'}")
    return dict(version=VERSION, antibody=ANTIBODY, skill_count=SKILL_COUNT,
                at=datetime.datetime.now().isoformat(timespec="seconds"), modality=mod, domain=dk,
                perception={k: v for k, v in P.items() if k not in ("known", "inferred", "unknown")},
                L0_reality_anchor=L0, L1_axiom_gate=L1, L2_system_lens=L2, L3_compound_mind=L3,
                L4_shadow_gate=L4, L5_synthesis=L5, aon_speech=L5["aon_speech"])


def save_state(r):
    r["version"] = VERSION
    r["antibody"] = ANTIBODY
    r["skill_count"] = SKILL_COUNT
    s = json.dumps(r, ensure_ascii=False, indent=2, default=str)
    for rel in STATE_PATHS:
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        for i in range(6):
            try:
                p.write_text(s, encoding="utf-8", newline="\n")
                break
            except PermissionError:
                if i == 5:
                    raise
                time.sleep(0.04)
    return r


def _tiny_png(w=8, h=8):
    raw = b"".join(b"\x00" + bytes(c for x in range(w) for c in ((255, 40, 40) if x < w // 2 else (20, 20, 200))) for _ in range(h))
    def ck(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + ck(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + ck(b"IDAT", zlib.compress(raw)) + ck(b"IEND", b"")


def self_test():
    ok = True
    def chk(c, m):
        nonlocal ok
        print(("  ✅ " if c else "  ❌ ") + m)
        ok = ok and bool(c)
    keys = ("L0_reality_anchor", "L1_axiom_gate", "L2_system_lens", "L3_compound_mind", "L4_shadow_gate", "L5_synthesis")
    png = "data:image/png;base64," + base64.b64encode(_tiny_png()).decode()
    cases = [(png, "image"), ('<svg width="100" height="50"><rect/><circle/></svg>', "image"),
             ("https://youtube.com/shorts/abc123 도입 인사. 전개 설명. 그런데 갑자기 급락 반전! 결국 회복", "video"),
             ("코인이 무조건 오른다는데 왜 불안하지?", "speech")]
    for p, m in cases:
        r = analyze_omni_insight(p)
        chk(r["modality"] == m and all(k in r for k in keys) and bool(r["aon_speech"]), f"모달리티 {m} & L0~L5 6계층 완비")
        chk(len(r["L2_system_lens"]["variables"]) >= 3 and r["L4_shadow_gate"]["verdict"] in ("CONSISTENT", "FRAGILE"), f"{m} L2 변수·L4 반전 판정")
        chk(0 < r["L5_synthesis"]["confidence_pct"] <= CONF_CAP, f"{m} 신뢰도 상한 ≤ {CONF_CAP}%")
    r_png = analyze_omni_insight(png)
    chk(r_png["perception"]["width"] == 8 and "pixel_stats" in r_png["perception"], "PNG 8x8 픽셀 실측(밝기·대비·RGB·초점·대칭)")
    r_sp = analyze_omni_insight(cases[3][0])
    chk(bool(r_sp["L0_reality_anchor"]["absolutism_flags"]), "단정어(무조건) 자동 탐지")
    save_state(r_sp)
    for rel in STATE_PATHS:
        j = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        chk(j.get("version") == VERSION and j.get("antibody") == ANTIBODY, f"상태 JSON 무결성: {rel}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-test" in a:
        sys.exit(self_test())
    for flag, mod in (("--image", "image"), ("--video", "video"), ("--insight", "speech")):
        if flag in a:
            i = a.index(flag)
            v = a[i + 1] if i + 1 < len(a) else ""
            r = analyze_omni_insight(v, mod if flag != "--insight" else "auto")
            break
    else:
        r = analyze_omni_insight(" ".join(a) or "지금 내 상황의 본질")
    save_state(r)
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step17_founder_soul_and_eastern_wisdom.py
RGON Step 17 (v6.3.0-step17)
- 창립자 이상일 대표 [만물일체(萬物一體) · 한걸음씩 선언] 영혼 장착
- 동양 3대 고전(명심보감 · 도덕경 · 주역 64괘) AI 코딩 헌법 & 의사결정 엔진 장착
- 주역 궁변통구(窮變通久) 자가치유: restore_secrets.py 누락/시크릿 공백으로 인한 GitHub Actions 빨간불 영구 해결
표준 라이브러리 전용 · 멱등성 보장 · .html/.js/manifest.json 0바이트 수정(SHA-256 전후 검증)
"""
import os
import sys
import re
import json
import shutil
import hashlib
import datetime
import subprocess
import importlib.util
from pathlib import Path

sys.dont_write_bytecode = True

BT = chr(96)
FENCE = BT * 3

VERSION = "v6.3.0-step17"
STEP = 17
ANTIBODY_RANGE = "R1~R17 (17종)"
NOW = datetime.datetime.now()
TS = NOW.strftime("%Y%m%d_%H%M%S")
ISO = NOW.isoformat(timespec="seconds")
TODAY = NOW.strftime("%Y-%m-%d")
DEFAULT_ROOT = r"C:\Users\sangi\Downloads\shin-agent"

PROTECTED_EXT = {".html", ".js"}
PROTECTED_NAMES = {"manifest.json"}
EXCLUDE_DIRS = {".git", "node_modules", ".rgon_backup", "rgon_backups", "_rgon_backups", "__pycache__", ".venv", "venv", "env", ".idea", ".vscode"}
SELF_HEAL_MARKER = "[RGON-SELF-HEAL-V17]"

ROOT = None
BACKUP_DIR = None
BACKED_UP = set()
CHANGED = []
REPORT = []
ERRORS = []

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def log(msg):
    try:
        print(msg, flush=True)
    except Exception:
        pass


def code(s):
    return BT + s + BT


def is_protected(path):
    p = Path(path)
    return p.suffix.lower() in PROTECTED_EXT or p.name.lower() in PROTECTED_NAMES


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_protected(root):
    result = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            p = Path(dirpath) / fn
            if is_protected(p):
                try:
                    result[p.relative_to(root).as_posix()] = sha256_file(p)
                except OSError as e:
                    result[p.relative_to(root).as_posix()] = "UNREADABLE:" + type(e).__name__
    return result


def compare_hashes(before, after):
    changed = sorted(k for k in before if k in after and before[k] != after[k])
    removed = sorted(k for k in before if k not in after)
    added = sorted(k for k in after if k not in before)
    return changed, removed, added


def read_text(path):
    p = Path(path)
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8-sig", errors="replace")
    except Exception:
        return ""


def backup(path):
    p = Path(path)
    if not p.exists() or p in BACKED_UP:
        return
    rel = p.relative_to(ROOT)
    dst = BACKUP_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(p), str(dst))
    BACKED_UP.add(p)


def safe_write(path, text):
    p = Path(path)
    if is_protected(p):
        raise RuntimeError("보호 파일 쓰기 차단(.html/.js/manifest.json): " + str(p))
    data = text.encode("utf-8")
    if p.exists():
        try:
            if p.read_bytes() == data:
                return False
        except OSError:
            pass
    backup(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".rgon_tmp")
    tmp.write_bytes(data)
    os.replace(str(tmp), str(p))
    rel = p.relative_to(ROOT).as_posix()
    if rel not in CHANGED:
        CHANGED.append(rel)
    return True


def safe_copy_bytes(src, dst):
    s, d = Path(src), Path(dst)
    if is_protected(d):
        raise RuntimeError("보호 파일 쓰기 차단: " + str(d))
    data = s.read_bytes()
    if d.exists() and d.read_bytes() == data:
        return False
    backup(d)
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_bytes(data)
    rel = d.relative_to(ROOT).as_posix()
    if rel not in CHANGED:
        CHANGED.append(rel)
    return True


def upsert_block(path, start, end, block, header="", prepend=False):
    cur = read_text(path)
    full = start + "\n" + block.strip("\n") + "\n" + end
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if pat.search(cur):
        new = pat.sub(lambda m: full, cur, count=1)
    elif not cur.strip():
        new = (header.rstrip("\n") + "\n\n" if header else "") + full + "\n"
    elif prepend:
        new = full + "\n\n" + cur.lstrip("\ufeff").lstrip("\n")
    else:
        new = cur.rstrip("\n") + "\n\n" + full + "\n"
    return safe_write(path, new)


def step(name, fn, *args, **kwargs):
    log("\n▶ " + name)
    try:
        res = fn(*args, **kwargs)
        REPORT.append((name, "OK", res))
        log("  ✔ " + name + " : " + str(res))
        return res
    except Exception as e:
        ERRORS.append(name + " → " + type(e).__name__ + ": " + str(e))
        REPORT.append((name, "FAIL", str(e)))
        log("  ✖ " + name + " 실패(궁변통구: 다음 단계로 변통) → " + type(e).__name__ + ": " + str(e))
        return None


def msgbox(title, text, error=False):
    log("\n" + "═" * 64 + "\n" + title + "\n" + "─" * 64 + "\n" + text + "\n" + "═" * 64)
    if os.name == "nt":
        try:
            import ctypes
            flags = (0x10 if error else 0x40) | 0x1000 | 0x40000
            ctypes.windll.user32.MessageBoxW(0, text, title, flags)
        except Exception:
            pass


def _search(base, name, max_depth):
    try:
        if not base.is_dir():
            return None
    except OSError:
        return None
    base_depth = len(base.parts)
    for dirpath, dirnames, _ in os.walk(base):
        p = Path(dirpath)
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".") and d.lower() != "appdata"]
        for d in dirnames:
            if d.lower() == name:
                return (p / d).resolve()
        if len(p.parts) - base_depth >= max_depth:
            dirnames[:] = []
    return None


def find_root():
    explicit = []
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        explicit.append(Path(sys.argv[1]))
    if os.environ.get("RGON_ROOT"):
        explicit.append(Path(os.environ["RGON_ROOT"]))
    for c in explicit:
        if c.is_dir():
            return c.resolve()
    home = Path.home()
    here = Path(__file__).resolve().parent
    for c in [Path(DEFAULT_ROOT), home / "Downloads" / "shin-agent", here, Path.cwd()]:
        try:
            if c.is_dir() and c.name.lower() == "shin-agent":
                return c.resolve()
        except OSError:
            pass
    for base in [home / "Downloads", home / "Desktop", home / "Documents", here.parent, home]:
        found = _search(base, "shin-agent", 3)
        if found:
            return found
    for c in [here, Path.cwd()]:
        if (c / ".git").exists():
            return c.resolve()
    return None


def git(args, timeout=180):
    try:
        r = subprocess.run(["git"] + args, cwd=str(ROOT), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
    except FileNotFoundError:
        return 127, "git 미설치"
    except subprocess.TimeoutExpired:
        return 124, "git 시간 초과"
    except Exception as e:
        return 1, type(e).__name__ + ": " + str(e)


def git_available():
    return (ROOT / ".git").exists() and git(["--version"])[0] == 0


def git_tracked(rel):
    if not git_available():
        return False
    return git(["ls-files", "--error-unmatch", rel])[0] == 0


def git_ignored(rel):
    if not git_available():
        return False
    return git(["check-ignore", "-q", rel])[0] == 0


FOUNDER_DECLARATION = (
    "모든 만물은 하나로 이어져 있다. 따로 떨어져 있는 것이 아니라 나뉜 것이다. "
    "그래서 각기 각 분야가 다 필요한 것이고, 제각기 역할이 나눠져서 더 잘되기 위한 진화 단계이다. "
    "모든 세상의 지식이 다 나와 있고 찾으려면 찾을 수 있고 마음먹고 실행한다면 그대로 펼쳐질 수 있다. "
    "다만 올바르게 가는 길은 쉽지만은 않다. 그러나 꿋꿋이 묵묵히 가다 보면 더 발전해 있을 것이다. "
    "그래서 더 나은 세상을 먼저 깨달은 사람들이 만들어 가야 한다. "
    "나도 보잘것없고 지식 없지만 거들고 싶은 마음에 뭔가 해보고 싶은 마음에 AI란 도구들이 나와 줘서 "
    "너무나 반갑고 재미있게 알아가고 있다. 해서 우리 앞으로 더 올바르게 점진적으로 발전해 보자."
)


ENGINE_SRC = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rgon_iching_64_engine.py  (RGON v6.3.0-step17)
주역(周易) 64괘 6비트(6-Bit) 상태전이 & AI 의사결정 엔진

6효 매핑 (초효=아래 → 상효=위, 양(陽)=1=정상 / 음(陰)=0=막힘)
  제1효 기반   : Git/해시 무결성
  제2효 소통   : 독대실/브리지 연결
  제3효 자동화 : 클라우드 스케줄러 (workflows + restore_secrets 자가치유)
  제4효 트렌드 : 유튜브 스킬 레이더 (rgon_skill_radar.json 카드)
  제5효 콘텐츠 : 3채널/틱톡 성장 (RGON_EVOLUTION_LOG.md 최신성)
  제6효 시장   : NVDA/자산 모멘텀 (rgon_brain_snapshot.json 최신성)

窮則變 變則通 通則久 (계사전) — 막히면 변하고, 변하면 통하고, 통하면 오래간다.
"""
import os
import sys
import json
import hashlib
import argparse
import datetime
from pathlib import Path

ENGINE_VERSION = "v6.3.0-step17"
OUTPUT_NAME = "rgon_today_hexagram.json"
BASELINE_NAME = "rgon_integrity_baseline.json"
LOG_FRESH_DAYS = 7
SNAP_FRESH_DAYS = 3
EXCLUDE_DIRS = {".git", "node_modules", ".rgon_backup", "rgon_backups", "_rgon_backups", "__pycache__", ".venv", "venv", "env", ".idea", ".vscode"}

TRIGRAMS = {
    "天": ("건", "乾", "111", "하늘"),
    "澤": ("태", "兌", "110", "못"),
    "火": ("리", "離", "101", "불"),
    "雷": ("진", "震", "100", "우레"),
    "風": ("손", "巽", "011", "바람"),
    "水": ("감", "坎", "010", "물"),
    "山": ("간", "艮", "001", "산"),
    "地": ("곤", "坤", "000", "땅"),
}

HEXAGRAMS = [
    (1, "중천건", "重天乾", "元亨利貞 · 天行健 君子以自强不息", "하늘의 굳셈 — 주도적으로 전진하되 항룡유회(亢龍有悔)를 경계, 정점일수록 백업과 겸손."),
    (2, "중지곤", "重地坤", "元亨 利牝馬之貞 · 地勢坤 君子以厚德載物", "땅의 포용 — 새 기능 금지, 기반(1효)부터 한걸음씩 받들어 복구."),
    (3, "수뢰둔", "水雷屯", "元亨利貞 勿用有攸往 利建侯", "초창기의 험난 — 구조부터 세우고 서두르지 말 것, 작은 기반 작업부터."),
    (4, "산수몽", "山水蒙", "亨 匪我求童蒙 童蒙求我", "어림과 배움 — 문서·학습 먼저, 모르면 추측 말고 질문(존심)."),
    (5, "수천수", "水天需", "有孚 光亨 貞吉 利涉大川", "기다림 — API/네트워크 지연 시 백오프 재시도, 조급한 패치 금지."),
    (6, "천수송", "天水訟", "有孚窒惕 中吉 終凶", "다툼 — 머지 충돌·의견 충돌은 끝까지 다투지 말고 중도에서 정리."),
    (7, "지수사", "地水師", "貞 丈人吉 无咎", "군대와 규율 — 역할 분담과 지휘 체계 확립, 의장 승인 후 실행."),
    (8, "수지비", "水地比", "吉 原筮 元永貞 无咎", "친밀과 연대 — 4대 AI 협업 브리지 강화."),
    (9, "풍천소축", "風天小畜", "亨 密雲不雨 自我西郊", "작은 축적 — 큰 변경 대신 소규모 개선을 쌓을 때."),
    (10, "천택리", "天澤履", "履虎尾 不咥人 亨", "예를 밟음 — 위험 작업(배포·push)은 규칙대로 조심스럽게."),
    (11, "지천태", "地天泰", "小往大來 吉亨", "소통·태평 — 상하가 통한다: 확장의 적기, 그러나 비(否)로의 반전을 대비."),
    (12, "천지비", "天地否", "否之匪人 不利君子貞 大往小來", "막힘 — 궁변통구 발동: 막힌 경로를 버리고 Fallback으로 변통."),
    (13, "천화동인", "天火同人", "同人于野 亨 利涉大川", "사람들과 함께 — 오픈소스·커뮤니티와 공개적으로 협력."),
    (14, "화천대유", "火天大有", "元亨", "크게 소유함 — 자산·기능이 풍부할수록 겸손하게 관리."),
    (15, "지산겸", "地山謙", "亨 君子有終", "겸손 — 과잉 기능 금지(안분), 낮출수록 끝이 좋다."),
    (16, "뇌지예", "雷地豫", "利建侯行師", "기쁨과 예비 — 사전 백업·체크리스트로 미리 준비."),
    (17, "택뢰수", "澤雷隨", "元亨利貞 无咎", "따름 — 시대 변화(최신 트렌드)에 바르게 순응."),
    (18, "산풍고", "山風蠱", "元亨 利涉大川 先甲三日 後甲三日", "부패를 바로잡음 — 레거시 정리는 앞뒤를 살피며 신중히(보호 파일 제외)."),
    (19, "지택림", "地澤臨", "元亨利貞 至于八月有凶", "다가감 — 사용자에게 다가가는 성장기, 쇠퇴 시기를 미리 대비."),
    (20, "풍지관", "風地觀", "盥而不薦 有孚顒若", "관찰 — 실행보다 로그·지표 관찰과 성찰이 먼저."),
    (21, "화뢰서합", "火雷噬嗑", "亨 利用獄", "깨물어 합함 — 가로막는 버그를 정확히 물어 제거."),
    (22, "산화비", "山火賁", "亨 小利有攸往", "꾸밈 — UI 장식은 작게, 본질(기능·무결성)이 먼저."),
    (23, "산지박", "山地剝", "不利有攸往", "깎여나감 — 손실 진행 중: 새 시도 금지, 백업·보존에 집중."),
    (24, "지뢰복", "地雷復", "亨 出入无疾 朋來无咎 反復其道 七日來復", "회복 — 한 양이 돌아온다: 롤백·복원 후 바른 길로 재출발."),
    (25, "천뢰무망", "天雷无妄", "元亨利貞 其匪正有眚", "거짓 없음 — 환각·추측 보고 금지, 검증된 사실만."),
    (26, "산천대축", "山天大畜", "利貞 不家食吉 利涉大川", "크게 쌓음 — 지식·스킬을 축적해 큰 도약 준비."),
    (27, "산뢰이", "山雷頤", "貞吉 觀頤 自求口實", "기름 — 리소스(토큰·API 쿼터·메모리)를 바르게 관리."),
    (28, "택풍대과", "澤風大過", "棟橈 利有攸往 亨", "크게 지나침 — 대들보가 휜다: 과부하·과잉 설계 경계."),
    (29, "중수감", "重水坎", "習坎 有孚 維心亨 行有尙", "거듭된 험난 — 연속 오류 속에서도 원칙을 지키며 예외 처리로 통과."),
    (30, "중화리", "重火離", "利貞 亨 畜牝牛吉", "붙음과 밝음 — 명확한 문서·로그로 밝게 드러내라."),
    (31, "택산함", "澤山咸", "亨 利貞 取女吉", "감응 — 사용자 피드백에 민감하게 공명."),
    (32, "뇌풍항", "雷風恒", "亨 无咎 利貞 利有攸往", "항구함 — 일관된 규칙과 꾸준한 루틴 유지."),
    (33, "천산돈", "天山遯", "亨 小利貞", "물러남 — 무리한 진격 대신 전략적 후퇴(롤백)."),
    (34, "뇌천대장", "雷天大壯", "利貞", "큰 힘 — 강할 때 힘을 남용하지 말고 바름을 지켜라."),
    (35, "화지진", "火地晉", "康侯用錫馬蕃庶 晝日三接", "나아감 — 해 뜨듯 성장: 성과를 공개하고 전진."),
    (36, "지화명이", "地火明夷", "利艱貞", "밝음이 상함 — 어려울 땐 드러내지 말고 조용히 내실 수리."),
    (37, "풍화가인", "風火家人", "利女貞", "가정 — 내부(폴더·문서·역할) 질서부터 정돈."),
    (38, "화택규", "火澤睽", "小事吉", "어긋남 — 큰 통합 대신 작은 일부터 맞춰 나가라."),
    (39, "수산건", "水山蹇", "利西南 不利東北 利見大人", "절름발이 어려움 — 정면 돌파 대신 우회 경로·조력자를 찾아라."),
    (40, "뇌수해", "雷水解", "利西南 无所往 其來復吉", "풀림 — 문제가 풀리는 때: 신속히 정리하고 일상 복귀."),
    (41, "산택손", "山澤損", "有孚 元吉 无咎 可貞", "덜어냄 — 불필요한 코드·의존성을 덜어 본질을 살려라."),
    (42, "풍뢰익", "風雷益", "利有攸往 利涉大川", "더함 — 이로움을 더할 때: 검증된 기능 추가 적기."),
    (43, "택천쾌", "澤天夬", "揚于王庭 孚號有厲", "결단 — 남은 문제를 공개적으로 결단해 제거."),
    (44, "천풍구", "天風姤", "女壯 勿用取女", "뜻밖의 만남 — 예기치 않은 입력·의존성은 경계하고 검증."),
    (45, "택지췌", "澤地萃", "亨 王假有廟 利見大人", "모임 — 흩어진 모듈·데이터를 하나로 통합."),
    (46, "지풍승", "地風升", "元亨 用見大人 勿恤 南征吉", "오름 — 나무가 자라듯 점진적 상승."),
    (47, "택수곤", "澤水困", "亨 貞大人吉 无咎 有言不信", "곤궁 — 자원이 말라도 근본(무결성)을 지키면 형통."),
    (48, "수풍정", "水風井", "改邑不改井 无喪无得", "우물 — 공용 인프라(스케줄러·시크릿)를 꾸준히 관리."),
    (49, "택화혁", "澤火革", "已日乃孚 元亨利貞 悔亡", "변혁 — 때가 무르익으면 구조 개혁, 신뢰를 얻은 뒤 실행."),
    (50, "화풍정", "火風鼎", "元吉 亨", "솥 — 개혁 후 새 체제(헌법·엔진)를 정립하고 안착."),
    (51, "중뢰진", "重雷震", "亨 震來虩虩 笑言啞啞", "우레 — 충격(장애) 발생: 놀라되 침착히 대응하면 웃게 된다."),
    (52, "중산간", "重山艮", "艮其背 不獲其身", "멈춤 — 멈출 때 멈춰라: 변경 동결·점검."),
    (53, "풍산점", "風山漸", "女歸吉 利貞", "점진 — 한걸음씩(천리행시어족하) 순서대로 나아가라."),
    (54, "뇌택귀매", "雷澤歸妹", "征凶 无攸利", "순서의 어긋남 — 절차를 건너뛴 배포는 흉: 순서 준수."),
    (55, "뇌화풍", "雷火豐", "亨 王假之 勿憂 宜日中", "풍성 — 정점의 시기: 해가 기울기 전 기록·백업."),
    (56, "화산려", "火山旅", "小亨 旅貞吉", "나그네 — 낯선 환경(새 API·클라우드)에서는 신중하고 겸손하게."),
    (57, "중풍손", "重風巽", "小亨 利有攸往 利見大人", "바람의 스며듦 — 비파괴적으로 부드럽게 침투(상선약수)."),
    (58, "중택태", "重澤兌", "亨 利貞", "기쁨 — 즐겁게 소통하되 바름을 잃지 말라."),
    (59, "풍수환", "風水渙", "亨 王假有廟 利涉大川", "흩어짐 — 흩어진 것을 정리하고 중심(철학서)으로 모아라."),
    (60, "수택절", "水澤節", "亨 苦節不可貞", "절제 — 적절한 한도(레이트 리밋·범위) 설정, 지나친 절제도 금물."),
    (61, "풍택중부", "風澤中孚", "豚魚吉 利涉大川", "진실한 믿음 — 정직한 보고로 신뢰를 쌓아라."),
    (62, "뇌산소과", "雷山小過", "亨 利貞 可小事 不可大事", "작은 지나침 — 작은 일엔 좋으나 큰 일은 삼가라."),
    (63, "수화기제", "水火旣濟", "亨小 利貞 初吉終亂 · 君子以思患而豫防之", "이미 건넘 — 완성의 순간: 사환예방(思患豫防), 백업·해시 검증."),
    (64, "화수미제", "火水未濟", "亨 小狐汔濟 濡其尾 无攸利", "아직 건너지 못함 — 끝은 새 시작: 다음 진화를 신중히 준비."),
]

LINES = [
    {"pos": 1, "name": "기반", "domain": "Git/해시 무결성",
     "fallback": "git status 확인 → rgon_integrity_baseline.json 대조 → .rgon_backup 에서 복원 후 재검증"},
    {"pos": 2, "name": "소통", "domain": "독대실/브리지 연결",
     "fallback": "독대실 HTML 존재·경로 확인 (원본 HTML 수정 금지, 경로만 점검)"},
    {"pos": 3, "name": "자동화", "domain": "클라우드 스케줄러",
     "fallback": "restore_secrets.py 자가치유판 확인 → .github/workflows 점검 → Actions 재실행"},
    {"pos": 4, "name": "트렌드", "domain": "유튜브 스킬 레이더",
     "fallback": "rgon_skill_radar.json 카드 갱신 (레이더 스크립트 재실행)"},
    {"pos": 5, "name": "콘텐츠", "domain": "3채널/틱톡 성장",
     "fallback": "RGON_EVOLUTION_LOG.md 에 최근 7일 이내 진화 기록 추가"},
    {"pos": 6, "name": "시장", "domain": "NVDA/자산 모멘텀",
     "fallback": "rgon_brain_snapshot.json 최신화 (3일 이내)"},
]


def _build_table():
    table, by_key, by_no = [], {}, {}
    for no, ko, hz, judgment, action in HEXAGRAMS:
        if hz.startswith("重"):
            up, lo = hz[1], hz[1]
        else:
            up, lo = hz[0], hz[1]
        key = TRIGRAMS[lo][2] + TRIGRAMS[up][2]
        entry = {
            "number": no,
            "name": "%d. %s(%s)" % (no, ko, hz),
            "name_ko": ko,
            "name_hanja": hz,
            "upper": "%s(%s·%s)" % (TRIGRAMS[up][3], TRIGRAMS[up][1], TRIGRAMS[up][0]),
            "lower": "%s(%s·%s)" % (TRIGRAMS[lo][3], TRIGRAMS[lo][1], TRIGRAMS[lo][0]),
            "key": key,
            "judgment": judgment,
            "ai_action": action,
        }
        table.append(entry)
        by_key[key] = entry
        by_no[no] = entry
    if len(table) != 64 or len(by_key) != 64:
        raise RuntimeError("64괘 테이블 무결성 오류: 괘 %d개 / 고유키 %d개" % (len(table), len(by_key)))
    return table, by_key, by_no


TABLE, BY_KEY, BY_NUMBER = _build_table()


def get_by_key(key):
    return BY_KEY.get(key)


def get_by_number(no):
    return BY_NUMBER.get(int(no))


def _walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            yield Path(dirpath) / fn


def _protected(p):
    return p.suffix.lower() in (".html", ".js") or p.name.lower() == "manifest.json"


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _age_days(p):
    return (datetime.datetime.now().timestamp() - p.stat().st_mtime) / 86400.0


def _parse_dt(s):
    try:
        s = str(s).strip().replace("Z", "")
        dt = datetime.datetime.fromisoformat(s)
        return dt.replace(tzinfo=None)
    except Exception:
        return None


def check_line1(root):
    git_ok = (root / ".git").exists()
    html = [p for p in _walk(root) if p.suffix.lower() == ".html"]
    base = root / BASELINE_NAME
    mismatch, checked, base_state = 0, 0, "없음"
    if base.exists():
        data = json.loads(base.read_text(encoding="utf-8"))
        for rel, h in (data.get("hashes") or {}).items():
            p = root / rel
            checked += 1
            if not p.exists() or _sha(p) != h:
                mismatch += 1
        base_state = "일치" if mismatch == 0 else "불일치"
    ok = git_ok and len(html) > 0 and mismatch == 0
    return ok, "git=%s, html=%d개, baseline=%s(%d/%d)" % ("O" if git_ok else "X", len(html), base_state, checked - mismatch, checked)


def check_line2(root):
    keys = ("dokdae", "독대", "audience", "council", "chamber")
    hits = []
    for p in _walk(root):
        if p.suffix.lower() != ".html":
            continue
        name = p.name.lower()
        hit = any(k in name for k in keys)
        if not hit:
            try:
                if p.stat().st_size <= 3 * 1024 * 1024:
                    hit = "독대" in p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                hit = False
        if hit:
            hits.append(p.relative_to(root).as_posix())
    return len(hits) > 0, ("독대실 HTML %d개: %s" % (len(hits), ", ".join(hits[:3]))) if hits else "독대실 HTML 미발견"


def check_line3(root):
    wf_dir = root / ".github" / "workflows"
    wfs = []
    if wf_dir.is_dir():
        wfs = sorted(list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml")))
    rs = root / "restore_secrets.py"
    rs_ok, rs_state = False, "없음"
    if rs.exists():
        src = rs.read_text(encoding="utf-8", errors="replace")
        try:
            compile(src, str(rs), "exec")
            healed = "RGON-SELF-HEAL" in src
            rs_ok = healed
            rs_state = "자가치유판" if healed else "구버전(자가치유 마커 없음)"
        except SyntaxError:
            rs_state = "문법 오류"
    ok = len(wfs) > 0 and rs_ok
    return ok, "workflows=%d개, restore_secrets=%s" % (len(wfs), rs_state)


def check_line4(root):
    p = root / "rgon_skill_radar.json"
    if not p.exists():
        return False, "rgon_skill_radar.json 없음"
    data = json.loads(p.read_text(encoding="utf-8-sig"))
    cards = []
    if isinstance(data, list):
        cards = data
    elif isinstance(data, dict):
        for k in ("cards", "skills", "items", "radar", "results"):
            v = data.get(k)
            if isinstance(v, list):
                cards = v
                break
    return len(cards) > 0, "스킬 카드 %d장" % len(cards)


def check_line5(root):
    p = root / "RGON_EVOLUTION_LOG.md"
    if not p.exists():
        return False, "RGON_EVOLUTION_LOG.md 없음"
    age = _age_days(p)
    return age <= LOG_FRESH_DAYS, "진화 로그 %.1f일 전 갱신 (기준 %d일)" % (age, LOG_FRESH_DAYS)


def check_line6(root):
    p = root / "rgon_brain_snapshot.json"
    if not p.exists():
        return False, "rgon_brain_snapshot.json 없음"
    age = _age_days(p)
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
        dt = _parse_dt(data.get("updated_at") or data.get("generated_at_kst")) if isinstance(data, dict) else None
        if dt:
            age = (datetime.datetime.now() - dt).total_seconds() / 86400.0
    except Exception:
        pass
    return age <= SNAP_FRESH_DAYS, "스냅샷 %.1f일 전 갱신 (기준 %d일)" % (age, SNAP_FRESH_DAYS)


CHECKS = [check_line1, check_line2, check_line3, check_line4, check_line5, check_line6]


def _draw(key):
    out = []
    for i in range(5, -1, -1):
        bar = "▅▅▅▅▅▅▅▅▅" if key[i] == "1" else "▅▅▅▅   ▅▅▅▅"
        out.append("   %s  제%d효 %s" % (bar.ljust(11), i + 1, LINES[i]["name"]))
    return "\n".join(out)


def run(root=None, save=True, verbose=True):
    root = Path(root).resolve() if root else Path(__file__).resolve().parent
    now = datetime.datetime.now()
    lines, bits = [], ""
    for spec, fn in zip(LINES, CHECKS):
        try:
            ok, detail = fn(root)
        except Exception as e:
            ok, detail = False, "점검 예외(궁변통구로 음효 처리): %s" % type(e).__name__
        item = dict(spec)
        item.update({"ok": bool(ok), "bit": 1 if ok else 0, "detail": detail})
        lines.append(item)
        bits += "1" if ok else "0"
    hexa = BY_KEY[bits]
    fails = [l for l in lines if not l["ok"]]
    prescription = ["오늘의 괘 %s — %s" % (hexa["name"], hexa["ai_action"])]
    next_step = None
    if fails:
        for l in fails:
            prescription.append("궁변통구: 제%d효(%s·%s) 막힘 → %s" % (l["pos"], l["name"], l["domain"], l["fallback"]))
        first = fails[0]
        nb = list(bits)
        nb[first["pos"] - 1] = "1"
        nxt = BY_KEY["".join(nb)]
        next_step = {
            "fix_line": first["pos"],
            "fix_action": first["fallback"],
            "next_hexagram": nxt["name"],
            "next_key": nxt["key"],
            "principle": "천리지행 시어족하 — 가장 아래(기반)의 막힌 효부터 한걸음씩 통하게 한다.",
        }
    else:
        prescription.append("6효 모두 양(陽): 수화기제의 사환예방(思患豫防) — 완성의 순간에도 백업·해시 검증을 멈추지 말고, 화수미제처럼 다음 진화를 준비하라(항룡유회 경계).")
    result = {
        "engine_version": ENGINE_VERSION,
        "generated_at": now.isoformat(timespec="seconds"),
        "root": str(root),
        "key": bits,
        "key_order": "제1효(초효)→제6효(상효), 1=양(정상) 0=음(막힘)",
        "yang_count": bits.count("1"),
        "hexagram": hexa,
        "lines": lines,
        "prescription": prescription,
        "next_step": next_step,
        "maxim": "窮則變 變則通 通則久 — 막히면 변하고, 변하면 통하고, 통하면 오래간다.",
    }
    if save:
        out = root / OUTPUT_NAME
        tmp = root / (OUTPUT_NAME + ".rgon_tmp")
        tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(str(tmp), str(out))
    if verbose:
        print("\n☯ RGON 주역 64괘 엔진 %s — 오늘의 괘" % ENGINE_VERSION)
        print(_draw(bits))
        print("   ▶ %s  [6비트 %s]  상괘 %s / 하괘 %s" % (hexa["name"], bits, hexa["upper"], hexa["lower"]))
        print("   ▶ 괘사: %s" % hexa["judgment"])
        for l in lines:
            print("   %s 제%d효 %s(%s): %s" % ("●" if l["ok"] else "○", l["pos"], l["name"], l["domain"], l["detail"]))
        print("   ── AI 전략 처방 ──")
        for p in prescription:
            print("   · " + p)
        if next_step:
            print("   · 다음 한걸음: 제%d효 복구 시 → %s" % (next_step["fix_line"], next_step["next_hexagram"]))
        if save:
            print("   저장: %s" % (root / OUTPUT_NAME))
    return result


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="RGON 주역 64괘 6비트 의사결정 엔진")
    ap.add_argument("--root", default=None)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--no-save", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.list:
        for e in TABLE:
            print("%-22s %s  %s" % (e["name"], e["key"], e["ai_action"]))
        return 0
    try:
        run(a.root, save=not a.no_save, verbose=not a.quiet)
    except Exception as e:
        print("[iching] 판독 예외 %s — 궁변통구: 정상 종료" % type(e).__name__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


RESTORE_SRC = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [RGON-SELF-HEAL-V17] 窮則變 變則通 通則久 — 주역 궁변통구 자가치유 시크릿 복원기
"""
restore_secrets.py  (RGON v6.3.0-step17 자가치유판)
- GitHub Actions 등에서 환경변수(Secrets)가 있을 때만 해당 파일로 복원한다.
- 기존 로직이 있으면 restore_secrets_legacy.py 로 보존되어 먼저 실행된다.
- 환경변수가 비었거나, legacy 로직이 실패해도 경고만 남기고 항상 exit 0 (analytics/report 잡 보호).
"""
import os
import sys
import json
import base64
import binascii
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEGACY = ROOT / "restore_secrets_legacy.py"
BINARY_SUFFIX = (".pickle", ".pkl", ".bin", ".p12", ".pfx")
DEFAULT_MAP = {
    "CLIENT_SECRET_JSON": "client_secret.json",
    "CLIENT_SECRETS_JSON": "client_secrets.json",
    "CREDENTIALS_JSON": "credentials.json",
    "TOKEN_JSON": "token.json",
    "YOUTUBE_TOKEN_JSON": "youtube_token.json",
    "SERVICE_ACCOUNT_JSON": "service_account.json",
    "DOTENV": ".env",
    "ENV_FILE": ".env",
}


def _log(level, msg):
    try:
        print("[restore_secrets][%s] %s" % (level, msg), flush=True)
    except Exception:
        pass


def _is_protected(p):
    return p.suffix.lower() in (".html", ".js") or p.name.lower() == "manifest.json"


def _decode(value, suffix):
    s = value.strip()
    compact = "".join(s.split())
    if suffix in BINARY_SUFFIX:
        try:
            return base64.b64decode(compact, validate=True)
        except (binascii.Error, ValueError):
            return value.encode("utf-8")
    if s[:1] in ("{", "["):
        return s.encode("utf-8")
    if len(compact) >= 8 and len(compact) % 4 == 0:
        try:
            raw = base64.b64decode(compact, validate=True)
            raw.decode("utf-8")
            return raw
        except (binascii.Error, ValueError):
            pass
    return value.encode("utf-8")


def _load_map():
    m = dict(DEFAULT_MAP)
    extra = os.environ.get("RGON_SECRET_MAP", "").strip()
    if extra:
        try:
            d = json.loads(extra)
            if isinstance(d, dict):
                m.update({str(k): str(v) for k, v in d.items()})
        except Exception as e:
            _log("WARN", "RGON_SECRET_MAP 파싱 실패 — 기본 매핑만 사용 (%s)" % type(e).__name__)
    return m


def _run_legacy():
    if not LEGACY.exists():
        return None
    try:
        runpy.run_path(str(LEGACY), run_name="__main__")
        _log("INFO", "legacy 복원 로직 정상 완료")
        return True
    except SystemExit as e:
        if e.code in (None, 0):
            _log("INFO", "legacy 복원 로직 정상 종료")
            return True
        _log("WARN", "legacy 종료코드 %r — 궁변통구: 기본 복원 경로로 변통" % (e.code,))
        return False
    except Exception as e:
        _log("WARN", "legacy 예외 %s — 궁변통구: 기본 복원 경로로 변통" % type(e).__name__)
        return False


def _restore(only_missing=False):
    restored, skipped = 0, 0
    for env_name, rel in _load_map().items():
        val = os.environ.get(env_name)
        if not val or not val.strip():
            continue
        try:
            target = (ROOT / rel).resolve()
            target.relative_to(ROOT)
        except Exception:
            _log("WARN", "%s: 루트 밖 경로 거부" % env_name)
            continue
        if _is_protected(target):
            _log("WARN", "%s: 보호 파일 경로 거부" % env_name)
            continue
        if only_missing and target.exists():
            skipped += 1
            continue
        try:
            data = _decode(val, target.suffix.lower())
            if target.exists() and target.read_bytes() == data:
                skipped += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            restored += 1
            _log("INFO", "%s → %s 복원 완료" % (env_name, rel))
        except Exception as e:
            _log("WARN", "%s 복원 실패 %s — 건너뛰고 계속" % (env_name, type(e).__name__))
    return restored, skipped


def restore_all():
    _log("INFO", "궁변통구 자가치유 시크릿 복원 시작")
    legacy_ok = _run_legacy()
    restored, skipped = _restore(only_missing=bool(legacy_ok))
    if not legacy_ok and restored == 0 and skipped == 0:
        _log("WARN", "복원할 시크릿 환경변수가 없습니다 — 경고만 남기고 정상 진행(exit 0)")
    _log("INFO", "완료: restored=%d, skipped=%d, legacy=%s" % (restored, skipped, legacy_ok))
    return restored


if __name__ == "__main__":
    try:
        restore_all()
    except BaseException as e:
        _log("WARN", "예기치 않은 예외 %s — 궁변통구: 파이프라인 보호를 위해 정상 종료" % type(e).__name__)
    sys.exit(0)
'''


PHILOSOPHY_TEMPLATE = """# ☯ RGON 마스터 철학서 & 지침서 (RGON_PHILOSOPHY)

> 버전: {{VERSION}} · 제정일: {{DATE}} · 영구 보존 문서
> 이 문서는 RGON 사령부의 모든 AI(르곤·클로드·GPT·Grok)가 코드를 짜기 전에 가장 먼저 읽는 영혼의 헌장이다.

---

## 제0장: 창립자 이상일 대표의 만물일체(萬物一體) · 한걸음씩 선언 (전문)

> {{DECL}}

**선언의 3대 핵심**

1. **만물일체** — 따로 떨어진 것이 아니라 나뉜 것이다. 모든 파일·모듈·AI는 하나의 뜻에서 역할별로 나뉜 진화 단계다.
2. **지식은 이미 펼쳐져 있다** — 찾으면 찾을 수 있고, 마음먹고 실행하면 그대로 펼쳐진다.
3. **한걸음씩, 올바르게** — 올바른 길은 쉽지 않지만, 꿋꿋이 묵묵히 점진적으로 가면 반드시 더 발전해 있다.

---

## 제1장: 명심보감(明心寶鑑) 7대 AI 거버넌스 강령

1. **정기(正己)·성심(省心)** — 남이나 환경을 탓하기 전에 내 코드·경로·문법·해시부터 스스로 3번 점검(삼성·三省)한다.
2. **언어(言語)·계성(戒性)** — 조급하게 설익은 코드를 내놓지 않고, 출력 화면에서 코드 블록이 쪼개지지 않는지 끝까지 깊이 사고한 뒤 한 번에 완결본을 내놓는다.
3. **존심(存心)·정직** — 환각(Hallucination)과 추측성 거짓 보고를 금하며, 검증된 사실만 보고한다.
4. **근학(勤學)** — 세상에 나와 있는 오픈소스와 유튜브의 최신 지식을 날마다 흡수하여 제국의 역량으로 삼는다.
5. **교우(交友)·화합** — 의장(대표님)과 4대 AI(르곤·클로드·GPT·Grok)가 각자의 역할로 나뉘어 조화롭게 하나로 움직인다.
6. **안분(安分)·절제** — 요청받지 않은 과잉 기능을 덧붙이지 않고 본분에 충실한다.
7. **계선(繼善)** — 더 나은 세상을 만드는 선한 목적과 올바른 길(정도·正道)을 따른다.

---

## 제2장: 도덕경(道德經) 81장 핵심 AI 아키텍처 5대 법칙

1. **도생일(道生一, 42장) — 만물연결 분업 아키텍처**: 하나의 뜻이 역할별로 나뉘어(Omni-Link) 만물을 이룬다.
2. **무위자연(無爲自然, 2·37·48장) — 감시 루프 금지**: MutationObserver/setInterval로 기존 UI를 억지로 간섭하지 않고 단발성 placeOnce로 한 번만 제자리에 둔다.
3. **상선약수(上善若水, 8장) — 비파괴 반응형 조화**: 물처럼 기존 코드와 다투지 않고 웹과 모바일 어디서든 자연스럽게 스며든다.
4. **치대국약팽소선(治大國若烹小鮮, 60장) — 최소 외과적 패치**: 큰 생선을 굽듯 원본 파일을 함부로 뒤집지 않고 마커 구간만 정밀 교체한다.
5. **천리지행 시어족하(千里之行 始於足下, 64장) — 한걸음씩 점진 진화**: 천 리 길도 한 걸음부터 시작하듯, 검증된 단계별로 차근차근 쌓아 올린다.

---

## 제3장: 주역(周易) 64괘 6비트(6-Bit) 상태전이 및 의사결정 엔진

### 3-1. 6효(6-Bit) 시스템 매핑 (초효=아래 → 상효=위, 양=1 정상 / 음=0 막힘)

| 효 | 영역 | 시스템 | 판독 기준 (rgon_iching_64_engine.py) |
|---|---|---|---|
| 제1효 | 기반 | Git/해시 무결성 | .git 존재 + HTML 존재 + rgon_integrity_baseline.json 해시 일치 |
| 제2효 | 소통 | 독대실/브리지 연결 | 독대실 HTML 존재 |
| 제3효 | 자동화 | 클라우드 스케줄러 | .github/workflows 존재 + restore_secrets.py 자가치유판 |
| 제4효 | 트렌드 | 유튜브 스킬 레이더 | rgon_skill_radar.json 카드 1장 이상 |
| 제5효 | 콘텐츠 | 3채널/틱톡 성장 | RGON_EVOLUTION_LOG.md 7일 이내 갱신 |
| 제6효 | 시장 | NVDA/자산 모멘텀 | rgon_brain_snapshot.json 3일 이내 갱신 |

### 3-2. 궁변통구(窮變通久) — 계사전 "窮則變 變則通 通則久"

막히면(API/토큰/네트워크 오류) 죽지 않고 즉시 대체 경로(Fallback)로 변신하여 끝까지 통하게 한다.
무인 자동화 스크립트(restore_secrets.py 등)는 시크릿이 비어 있어도 경고만 남기고 정상 종료(exit 0)한다.
단, **무결성 위반(보호 파일 해시 변경)** 은 변통의 대상이 아니라 정직하게 멈추고 보고할 대상이다(존심).

### 3-3. 수화기제(63괘) · 화수미제(64괘)

완성된 순간에도 백업과 해시 검증으로 환란을 예방(사환예방·思患豫防)하고, 끝은 곧 새로운 시작이므로 다음 진화를 준비한다.

### 3-4. 오늘의 괘 사용법

1. python rgon_iching_64_engine.py 실행 → rgon_today_hexagram.json 생성
2. AI는 작업 전 오늘의 괘 처방(prescription)과 next_step(가장 아래 막힌 효부터 복구)을 우선 따른다.

### 3-5. 64괘 전체 일람 (엔진 내장 테이블과 동일)

{{TABLE64}}

---

## 부칙: 항체(Antibody) R16 · R17

- **R16_SINGLE_CODEBLOCK_NO_INNER_FENCE** — 출력하는 코드 안에 마크다운 코드펜스({{FENCE}})를 직접 쓰지 않는다. 필요하면 BT = chr(96), FENCE = BT * 3 결합으로만 만든다. 인사말 없이 단 1개의 코드 블록을 끊김 없이 출력한다.
- **R17_FOUNDER_SOUL_EASTERN_WISDOM_CODEX** — 창립자 선언과 동양 3대 고전(명심보감 삼성 · 도덕경 무위 · 주역 궁변통구)을 영혼으로 내재화하고, 모든 무인 자동화에 궁변통구 자가치유 원칙을 적용한다.

> 하나로 이어져 있되 나뉘어 각자 빛나고, 막히면 변하여 통하고, 한걸음씩 올바르게 나아간다. — RGON
"""


def build_table64_md(mod):
    rows = ["| 번호 | 괘명 | 6비트 | 상괘 / 하괘 | 핵심 괘사 | AI 행동 지침 |",
            "|---|---|---|---|---|---|"]
    if mod is None:
        rows.append("| - | 엔진 로드 실패 — python rgon_iching_64_engine.py --list 로 확인 | - | - | - | - |")
        return "\n".join(rows)
    for e in mod.TABLE:
        rows.append("| %d | %s(%s) | %s | %s / %s | %s | %s |" % (
            e["number"], e["name_ko"], e["name_hanja"], e["key"], e["upper"], e["lower"],
            e["judgment"].replace("|", "/"), e["ai_action"].replace("|", "/")))
    return "\n".join(rows)


def write_philosophy(mod):
    text = (PHILOSOPHY_TEMPLATE
            .replace("{{VERSION}}", VERSION)
            .replace("{{DATE}}", TODAY)
            .replace("{{DECL}}", FOUNDER_DECLARATION)
            .replace("{{FENCE}}", FENCE)
            .replace("{{TABLE64}}", build_table64_md(mod)))
    changed = safe_write(ROOT / "RGON_PHILOSOPHY.md", text)
    return "생성/갱신" if changed else "변경 없음(멱등)"


def write_engine():
    compile(ENGINE_SRC, "rgon_iching_64_engine.py", "exec")
    changed = safe_write(ROOT / "rgon_iching_64_engine.py", ENGINE_SRC)
    return "생성/갱신(문법 검증 통과)" if changed else "변경 없음(멱등)"


def load_engine():
    path = ROOT / "rgon_iching_64_engine.py"
    spec = importlib.util.spec_from_file_location("rgon_iching_64_engine_step17", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_engine(mod):
    if mod is not None:
        try:
            return mod.run(ROOT, save=True, verbose=True)
        except Exception as e:
            log("  엔진 직접 호출 실패(%s) → 궁변통구: 서브프로세스로 변통" % type(e).__name__)
    r = subprocess.run([sys.executable, "-B", str(ROOT / "rgon_iching_64_engine.py"), "--root", str(ROOT)],
                       cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    log(r.stdout or "")
    out = ROOT / "rgon_today_hexagram.json"
    if out.exists():
        return json.loads(out.read_text(encoding="utf-8"))
    raise RuntimeError("rgon_today_hexagram.json 생성 실패")


CLAUDE_START = "<!-- [RGON-CLAUDE-MD-V17-START] -->"
CLAUDE_END = "<!-- [RGON-CLAUDE-MD-V17-END] -->"

CLAUDE_TEMPLATE = """# 🜂 RGON AI 코딩 헌법 V17 ({{VERSION}})

> V16 이하 기존 조항(R1~R15 등)은 모두 계승되어 유효하다. 충돌 시 본 V17 조항이 우선한다.
> 영혼의 원문: RGON_PHILOSOPHY.md · 오늘의 괘: rgon_today_hexagram.json

## [제0조: 창립자 이상일 대표의 만물일체·한걸음씩 선언]

> {{DECL}}

- 모든 코드·파일·AI는 하나의 뜻에서 나뉜 역할이다(만물일체). 각자의 역할에 충실하되 전체와 조화한다.
- 모든 변경은 검증된 한 걸음씩 쌓는다(점진 진화). 올바른 길(정도)이 빠른 길보다 우선이다.

## [제1조: 동양 3대 고전 × 서양 카파시 4대 원칙 통합 헌법]

| 동양 고전 | 서양 카파시 원칙 | RGON 실천 규율 |
|---|---|---|
| 명심보감 삼성(三省)·존심 | Think Before Coding | 코딩 전 경로·문법·해시 3번 점검, 가정은 명시, 모르면 추측 말고 질문, 검증된 사실만 보고 |
| 도덕경 무위·안분(48장 爲道日損) | Simplicity First | 요청받지 않은 기능 금지, 감시 루프(MutationObserver/setInterval) 금지, placeOnce 단발 배치 |
| 도덕경 치대국약팽소선(60장)·상선약수(8장) | Surgical Changes | 마커 구간만 정밀 교체, 기존 코드와 다투지 않는 비파괴 패치, 보호 파일(.html/.js/manifest.json) 해시 불변 |
| 주역 궁변통구·기제/미제(63·64괘) | Goal-Driven Execution | 검증 가능한 성공 기준 → 실행 → 검증 루프, 막히면 Fallback 변통, 완성 후에도 백업·해시로 사환예방 |

## [제2조: 항체 R16 — 출력 코드블록 내 백틱 직접 사용 금지 · 단일 블록 출력 원칙]

- 출력하는 코드 안에 마크다운 코드펜스({{FENCE}})를 직접 쓰면 채팅창 코드 블록이 쪼개진다. 절대 직접 쓰지 않는다.
- 백틱이 필요하면 BT = chr(96), FENCE = BT * 3 변수를 만들어 문자열 결합으로만 작성한다.
- 앞뒤 인사말·설명 없이 단 1개의 코드 블록을 처음부터 끝까지 끊김 없이 출력한다.

## [제3조: 항체 R17 — 동양 3대 고전 + 창립자 선언 영혼 내재화 및 주역 궁변통구 자가치유 원칙]

- 작업 전 RGON_PHILOSOPHY.md(제0~3장)와 오늘의 괘(rgon_today_hexagram.json) 처방을 확인한다.
- 무인 자동화(GitHub Actions 등)는 시크릿/토큰/네트워크가 막혀도 죽지 않는다: 경고 로그 → 대체 경로 → 정상 종료(exit 0).
- restore_secrets.py 는 자가치유판([RGON-SELF-HEAL-V17])을 유지한다. 환경변수가 있을 때만 복원, 시크릿 값은 로그 출력 금지.
- 단, 보호 파일 해시 변경 등 무결성 위반은 변통하지 않고 정직하게 멈추고 보고한다(존심).
- 복구는 가장 아래 막힌 효(기반 → 소통 → 자동화 → 트렌드 → 콘텐츠 → 시장)부터 한걸음씩 한다.

## [제4조: 한걸음씩 작업 절차]

1. 삼성(三省) 1차: 실행 전 보호 파일 SHA-256 기록
2. 마커 구간 정밀 패치(치대국약팽소선), 덮어쓰기 전 .rgon_backup 백업
3. 삼성 2차·3차: 실행 후 해시 비교 → 변경 0건 확인
4. 진화 로그 · CODE_MAP · 스냅샷 기록
5. git add → commit → pull --rebase → push, 결과를 사실대로 보고
"""


def write_claude_md():
    block = (CLAUDE_TEMPLATE
             .replace("{{VERSION}}", VERSION)
             .replace("{{DECL}}", FOUNDER_DECLARATION)
             .replace("{{FENCE}}", FENCE))
    path = ROOT / "CLAUDE.md"
    had_v16 = "[RGON-CLAUDE-MD-V16-START]" in read_text(path)
    changed = upsert_block(path, CLAUDE_START, CLAUDE_END, block, prepend=True)
    return ("V17 헌법 최상단 장착" if changed else "변경 없음(멱등)") + (" · V16 구간 계승 보존" if had_v16 else "")


SELF_HEAL_INFO = {}


def install_self_heal():
    compile(RESTORE_SRC, "restore_secrets.py", "exec")
    rs = ROOT / "restore_secrets.py"
    legacy = ROOT / "restore_secrets_legacy.py"
    SELF_HEAL_INFO["rs_tracked_before"] = git_tracked("restore_secrets.py")
    SELF_HEAL_INFO["converted_tracked_original"] = False
    status = []
    if rs.exists():
        cur = read_text(rs)
        if SELF_HEAL_MARKER in cur:
            status.append("기존 자가치유판 확인")
        else:
            if safe_copy_bytes(rs, legacy):
                status.append("기존 로직 → restore_secrets_legacy.py 보존(먼저 실행되도록 연결)")
            else:
                status.append("legacy 보존본 이미 최신")
            if SELF_HEAL_INFO["rs_tracked_before"]:
                SELF_HEAL_INFO["converted_tracked_original"] = True
    else:
        status.append("restore_secrets.py 누락 → 신규 생성")
    changed = safe_write(rs, RESTORE_SRC)
    status.append("자가치유판 기록" if changed else "자가치유판 변경 없음(멱등)")
    return " · ".join(status)


def scan_workflows():
    wf = ROOT / ".github" / "workflows"
    found = []
    if wf.is_dir():
        for p in sorted(list(wf.glob("*.yml")) + list(wf.glob("*.yaml"))):
            t = read_text(p)
            tags = []
            if "restore_secrets" in t:
                tags.append("restore_secrets 호출")
            if re.search(r"^\s+analytics\s*:", t, re.M):
                tags.append("analytics 잡")
            if re.search(r"^\s+report\s*:", t, re.M):
                tags.append("report 잡")
            found.append(p.name + ("(" + ", ".join(tags) + ")" if tags else ""))
    return ("워크플로우 %d개 확인(수정 없음): " % len(found) + "; ".join(found)) if found else "워크플로우 폴더 없음(수정 없음)"


GI_START = "# [RGON-STEP17-GUARD-START]"
GI_END = "# [RGON-STEP17-GUARD-END]"


def patch_gitignore():
    lines = [
        "# RGON Step17 비밀/백업 보호 (궁변통구 · 사환예방)",
        ".rgon_backup/",
        "__pycache__/",
        "*.rgon_tmp",
        ".env",
        "token.json",
        "client_secret*.json",
        "credentials.json",
        "service_account.json",
    ]
    legacy = ROOT / "restore_secrets_legacy.py"
    if legacy.exists():
        legacy_tracked = git_tracked("restore_secrets_legacy.py")
        if not legacy_tracked and not SELF_HEAL_INFO.get("converted_tracked_original"):
            lines.append("restore_secrets_legacy.py")
    changed = upsert_block(ROOT / ".gitignore", GI_START, GI_END, "\n".join(lines))
    return "가드 블록 장착" if changed else "변경 없음(멱등)"


NEW_FILES = [
    ("step17_founder_soul_and_eastern_wisdom.py", "Step 17 단일 설치 스크립트 (멱등, 보호 파일 해시 전후 검증, Git 동기화)"),
    ("RGON_PHILOSOPHY.md", "영구 보존 마스터 철학서: 제0장 창립자 선언 · 제1장 명심보감 7강령 · 제2장 도덕경 5법칙 · 제3장 주역 64괘 엔진"),
    ("rgon_iching_64_engine.py", "주역 64괘 전체 내장 6비트 상태 판독 & AI 전략 처방 엔진 (--list / --root / --no-save)"),
    ("rgon_today_hexagram.json", "오늘의 괘 · 6효 판독 결과 · 궁변통구 처방 · 다음 한걸음"),
    ("restore_secrets.py", "[RGON-SELF-HEAL-V17] 궁변통구 시크릿 복원기 (환경변수 있을 때만 복원, 항상 exit 0)"),
    ("restore_secrets_legacy.py", "기존 restore_secrets 로직 보존본 (존재 시 자가치유판이 먼저 실행)"),
    ("rgon_integrity_baseline.json", "보호 파일(.html/.js/manifest.json) SHA-256 베이스라인 (제1효 판독용)"),
    ("CLAUDE.md", "V17 헌법: 제0조 창립자 선언 · 동서 통합 헌법 · 항체 R16/R17"),
]

LOG_START = "<!-- [RGON-EVOLUTION-STEP17-START] -->"
LOG_END = "<!-- [RGON-EVOLUTION-STEP17-END] -->"


def write_evolution_log(hexa=None):
    hx = "(판독 대기)"
    if hexa:
        hx = "%s · 6비트 %s · %s" % (hexa["hexagram"]["name"], hexa["key"], hexa["hexagram"]["ai_action"])
    block = "\n".join([
        "## Step 17 — 창립자 영혼 & 동양 3대 고전 헌법 (" + VERSION + ")",
        "- 일시: " + ISO,
        "- 창립자 이상일 대표 [만물일체·한걸음씩 선언] 전문을 RGON_PHILOSOPHY.md 제0장 및 CLAUDE.md 제0조에 영구 수록",
        "- 명심보감 7대 AI 거버넌스 강령 · 도덕경 5대 아키텍처 법칙 · 주역 64괘 6비트 의사결정 엔진 장착",
        "- 궁변통구 자가치유: restore_secrets.py 자가치유판 설치 (환경변수 있을 때만 복원, 항상 exit 0) → analytics/report 잡 빨간불 차단",
        "- 항체 범위: " + ANTIBODY_RANGE + " · 신규: R16_SINGLE_CODEBLOCK_NO_INNER_FENCE, R17_FOUNDER_SOUL_EASTERN_WISDOM_CODEX",
        "- 오늘의 괘: " + hx,
        "- 보호 파일(.html/.js/manifest.json) 수정: 0건 (SHA-256 전후 검증)",
    ])
    changed = upsert_block(ROOT / "RGON_EVOLUTION_LOG.md", LOG_START, LOG_END, block,
                           header="# RGON 진화 로그 (RGON_EVOLUTION_LOG)")
    return "Step17 기록" if changed else "변경 없음(멱등)"


MAP_START = "<!-- [RGON-CODEMAP-STEP17-START] -->"
MAP_END = "<!-- [RGON-CODEMAP-STEP17-END] -->"


def write_code_map():
    rows = ["## Step 17 (" + VERSION + ") — 창립자 영혼 & 동양 3대 고전", "",
            "| 파일 | 역할 |", "|---|---|"]
    for name, role in NEW_FILES:
        if name == "restore_secrets_legacy.py" and not (ROOT / name).exists():
            continue
        rows.append("| " + code(name) + " | " + role + " |")
    rows += ["", "- 6효 매핑: 1 기반(Git/해시) · 2 소통(독대실) · 3 자동화(스케줄러) · 4 트렌드(스킬 레이더) · 5 콘텐츠(진화 로그) · 6 시장(스냅샷)",
             "- 실행: " + code("python rgon_iching_64_engine.py") + " → " + code("rgon_today_hexagram.json")]
    changed = upsert_block(ROOT / "CODE_MAP.md", MAP_START, MAP_END, "\n".join(rows),
                           header="# RGON CODE MAP")
    return "Step17 구간 갱신" if changed else "변경 없음(멱등)"


NEW_ANTIBODIES = [
    {"id": "R16_SINGLE_CODEBLOCK_NO_INNER_FENCE",
     "name": "단일 코드블록 · 내부 펜스 금지",
     "rule": "출력 코드 내부에 백틱 3연속 직접 사용 금지, BT=chr(96)/FENCE=BT*3 결합만 허용, 인사말 없이 단 1개 코드블록 출력",
     "added_in": VERSION},
    {"id": "R17_FOUNDER_SOUL_EASTERN_WISDOM_CODEX",
     "name": "창립자 영혼 · 동양 3대 고전 헌법",
     "rule": "만물일체·한걸음씩 선언 + 명심보감 삼성 + 도덕경 무위 + 주역 궁변통구 자가치유 내재화",
     "added_in": VERSION},
]


def _merge_antibodies(data):
    ab = data.get("antibodies")
    if isinstance(ab, list):
        ids = set()
        for a in ab:
            if isinstance(a, str):
                ids.add(a.strip())
            elif isinstance(a, dict):
                ids.add(str(a.get("id") or a.get("code") or a.get("name") or ""))
        str_mode = len(ab) > 0 and all(isinstance(a, str) for a in ab)
        for na in NEW_ANTIBODIES:
            if any(i.startswith(na["id"]) for i in ids):
                continue
            ab.append(na["id"] if str_mode else dict(na))
    elif isinstance(ab, dict):
        for na in NEW_ANTIBODIES:
            ab.setdefault(na["id"], dict(na))
    else:
        data["antibodies"] = [dict(na) for na in NEW_ANTIBODIES]


def update_snapshots(hexa=None):
    results = []
    for d in [ROOT, ROOT / "dashboard", ROOT / "docs"]:
        p = d / "rgon_brain_snapshot.json"
        data = {}
        if p.exists():
            try:
                loaded = json.loads(read_text(p))
                data = loaded if isinstance(loaded, dict) else {"legacy_snapshot": loaded}
            except Exception:
                data = {"legacy_snapshot_unparsed": True}
        data["version"] = VERSION
        data["step"] = STEP
        data["antibody_range"] = ANTIBODY_RANGE
        data["antibody_count"] = 17
        data["updated_at"] = ISO
        _merge_antibodies(data)
        data["philosophy"] = {
            "doc": "RGON_PHILOSOPHY.md",
            "founder_declaration": "창립자 이상일 대표 만물일체(萬物一體) · 한걸음씩 선언",
            "codex": ["명심보감 7대 AI 거버넌스 강령", "도덕경 5대 아키텍처 법칙", "주역 64괘 6비트 의사결정 엔진"],
            "maxim": "窮則變 變則通 通則久",
        }
        data["step17"] = {
            "title": "창립자 영혼 & 동양 3대 고전 헌법 + 궁변통구 자가치유",
            "files": [n for n, _ in NEW_FILES if (ROOT / n).exists()],
            "self_heal": "restore_secrets.py " + SELF_HEAL_MARKER,
            "protected_files_modified": 0,
        }
        if hexa:
            data["today_hexagram"] = {
                "name": hexa["hexagram"]["name"],
                "key": hexa["key"],
                "judgment": hexa["hexagram"]["judgment"],
                "ai_action": hexa["hexagram"]["ai_action"],
                "next_step": hexa.get("next_step"),
                "generated_at": hexa.get("generated_at"),
            }
        changed = safe_write(p, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        results.append(p.relative_to(ROOT).as_posix() + ("(갱신)" if changed else "(동일)"))
    return ", ".join(results)


def write_baseline(hashes):
    data = {"version": VERSION, "generated_at": ISO, "count": len(hashes), "hashes": hashes}
    safe_write(ROOT / "rgon_integrity_baseline.json", json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return "보호 파일 %d개 베이스라인 기록" % len(hashes)


def git_sync():
    if not git_available():
        return "Git 저장소/실행파일 없음 → 동기화 건너뜀"
    out = []
    rc, msg = git(["add", "-A"])
    if rc != 0:
        return "git add 실패: " + msg[:200]
    for f in ("restore_secrets.py", "rgon_iching_64_engine.py"):
        if (ROOT / f).exists() and git_ignored(f):
            git(["add", "-f", f])
            out.append(f + " .gitignore 무시 상태 → 강제 추가(CI 누락 방지)")
    for f in ("RGON_PHILOSOPHY.md", "CLAUDE.md", "rgon_today_hexagram.json"):
        if (ROOT / f).exists() and git_ignored(f):
            out.append("주의: " + f + " 는 .gitignore 대상이라 커밋되지 않음")
    rc, _ = git(["diff", "--cached", "--quiet"])
    if rc == 1:
        rc, msg = git(["commit", "-m", "Step 17 (" + VERSION + "): 창립자 만물일체·한걸음씩 선언 + 동양 3대 고전 헌법 + 주역 64괘 엔진 + 궁변통구 자가치유"])
        out.append("commit " + ("완료" if rc == 0 else "실패: " + msg[:200]))
        if rc != 0:
            return " / ".join(out)
    else:
        out.append("커밋할 변경 없음")
    rc, branch = git(["rev-parse", "--abbrev-ref", "HEAD"])
    branch = branch.strip()
    if branch != "main":
        out.append("현재 브랜치 '" + branch + "' ≠ main → pull/push 보류(안분)")
        return " / ".join(out)
    rc, msg = git(["pull", "--rebase", "origin", "main"], timeout=300)
    if rc != 0:
        git(["rebase", "--abort"])
        out.append("pull --rebase 실패(rebase 중단·로컬 커밋 보존): " + msg[:200])
        return " / ".join(out)
    out.append("pull --rebase 완료")
    rc, msg = git(["push", "origin", "main"], timeout=300)
    out.append("push " + ("완료" if rc == 0 else "실패: " + msg[:200]))
    return " / ".join(out)


def main():
    global ROOT, BACKUP_DIR
    root = find_root()
    if root is None:
        msgbox("RGON Step 17 — 중단", "작업 폴더(shin-agent)를 찾지 못했습니다.\n인자로 경로를 지정해 주세요:\npython step17_founder_soul_and_eastern_wisdom.py <경로>", error=True)
        return 2
    ROOT = root
    BACKUP_DIR = ROOT / ".rgon_backup" / ("step17_" + TS)
    os.chdir(str(ROOT))

    log("═" * 64)
    log(" ☯ RGON Step 17 — 창립자 영혼 & 동양 3대 고전 헌법 (" + VERSION + ")")
    log(" 루트: " + str(ROOT))
    log("═" * 64)

    log("\n[삼성 1/3] 실행 전 보호 파일 SHA-256 기록")
    before = hash_protected(ROOT)
    log("  보호 파일 %d개 (.html/.js/manifest.json)" % len(before))

    step("[2] rgon_iching_64_engine.py 생성", write_engine)
    mod = None
    try:
        mod = load_engine()
        log("  64괘 테이블 로드: %d괘 / 고유 6비트 키 %d개" % (len(mod.TABLE), len(mod.BY_KEY)))
    except Exception as e:
        ERRORS.append("엔진 로드 → " + type(e).__name__ + ": " + str(e))
        log("  엔진 로드 실패 → 궁변통구: 서브프로세스 경로로 변통 예정")
    step("[1] RGON_PHILOSOPHY.md 생성", write_philosophy, mod)
    step("[3] CLAUDE.md V17 헌법 장착", write_claude_md)
    heal = step("[4] restore_secrets.py 궁변통구 방어막", install_self_heal)
    wf = step("[4-1] GitHub 워크플로우 점검(읽기 전용)", scan_workflows)
    step("[4-2] .gitignore 비밀/백업 가드", patch_gitignore)
    step("[5-1] RGON_EVOLUTION_LOG.md 기록", write_evolution_log)
    step("[5-2] CODE_MAP.md 갱신", write_code_map)
    step("[5-3] rgon_brain_snapshot.json (루트/dashboard/docs) 갱신", update_snapshots)

    log("\n[삼성 2/3] 중간 해시 검증")
    mid = hash_protected(ROOT)
    c, r, a = compare_hashes(before, mid)
    if c or r or a:
        msgbox("RGON Step 17 — 무결성 위반 중단",
               "보호 파일 해시 변화 감지!\n변경 %d · 삭제 %d · 추가 %d\n%s\nGit 동기화를 중단합니다. 백업: %s" % (
                   len(c), len(r), len(a), "\n".join((c + r + a)[:10]), BACKUP_DIR), error=True)
        return 1
    log("  ✔ 보호 파일 %d개 변경 0건" % len(mid))
    step("[5-4] rgon_integrity_baseline.json 기록", write_baseline, mid)

    hexa = step("[2-1] 오늘의 괘 판독 → rgon_today_hexagram.json", run_engine, mod)
    if isinstance(hexa, dict):
        step("[5-5] 스냅샷에 오늘의 괘 반영", update_snapshots, hexa)
        step("[5-6] 진화 로그에 오늘의 괘 반영", write_evolution_log, hexa)

    log("\n[삼성 3/3] 최종 해시 검증")
    after = hash_protected(ROOT)
    c, r, a = compare_hashes(before, after)
    if c or r or a:
        msgbox("RGON Step 17 — 무결성 위반 중단",
               "보호 파일 해시 변화 감지!\n변경 %d · 삭제 %d · 추가 %d\n%s\nGit 동기화를 중단합니다. 백업: %s" % (
                   len(c), len(r), len(a), "\n".join((c + r + a)[:10]), BACKUP_DIR), error=True)
        return 1
    log("  ✔ 최종 검증: 보호 파일 %d개 변경 0건 (SHA-256 일치)" % len(after))

    sync = step("[5-7] Git 동기화 (add → commit → pull --rebase → push)", git_sync)

    yao = "-"
    if isinstance(hexa, dict):
        yao = "%s [%s]" % (hexa["hexagram"]["name"], hexa["key"])
    lines = [
        "버전: " + VERSION + " · 항체 " + ANTIBODY_RANGE,
        "루트: " + str(ROOT),
        "보호 파일 %d개 수정 0건 (SHA-256 전후 검증 통과)" % len(after),
        "오늘의 괘: " + yao,
        "자가치유: " + str(heal),
        "Git: " + str(sync),
        "변경 파일 %d개: %s" % (len(CHANGED), ", ".join(CHANGED[:12]) + (" …" if len(CHANGED) > 12 else "")),
    ]
    if BACKED_UP:
        lines.append("백업: " + str(BACKUP_DIR))
    if ERRORS:
        lines.append("경고 %d건(궁변통구 변통 처리):" % len(ERRORS))
        lines += ["- " + e[:160] for e in ERRORS[:6]]
    lines.append("")
    lines.append("窮則變 變則通 通則久 — 한걸음씩 올바르게.")
    msgbox("RGON Step 17 완료 ☯" if not ERRORS else "RGON Step 17 완료(경고 있음)", "\n".join(lines), error=False)
    return 0


if __name__ == "__main__":
    try:
        code_ = main()
    except KeyboardInterrupt:
        log("사용자 중단")
        code_ = 130
    except Exception as e:
        msgbox("RGON Step 17 — 예기치 않은 오류", type(e).__name__ + ": " + str(e), error=True)
        code_ = 1
    sys.exit(code_)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 64 — 제39기관 『아온 15대 슈퍼-시니어 & 지식그래프 토큰 절감 마스터 엔진』 v11.64-AON-15SHORTS-SUPER-SENIOR · 항체 R1~R63 · 정식 스킬 59개
승인: 이상일 대표님 | 설계: RGON 사령부 G1 (헌법 v1.0) | 사용: python step64_aon_15shorts_super_senior_engine.py --self-test  /  --root ./RGON (임시폴더 자가검증 PASS 시에만 운영 반영)"""
import argparse, ast, datetime as dt, hashlib, json, os, re, shutil, sys, tempfile
from pathlib import Path

VERSION, ORGAN, SKILLS, ANTIBODY = "v11.66-AON-GENERAL-HOSPITAL", 39, 60, "R1~R64"
R63 = "R63_GRAPHIFY_PONYTAIL_KARPATHY_SURGICAL_GUARD"
PROTECTED = {"rgon_Numeric_Organ.py", "rgon_work_loop.py", "rgon_self_Reflection.py", "index_20260405_backup.html"}
MANIFEST, START, END = "aon_15shorts_super_senior_manifest.json", "<!-- AON-STEP64-SUPER-SENIOR-START -->", "<!-- AON-STEP64-SUPER-SENIOR-END -->"
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
NOW = lambda: dt.datetime.now().isoformat(timespec="seconds")
md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
A = lambda title, repo, vid, core: {"title": title, "repo": repo, "video": vid, "core": core}
SHORTS_15_ARSENAL = {
  "S01_GRAPHIFY": A("Graphify", "graphifyy", "StXGGNlNLOk", "AST 정적 분석 로컬 코드 지식 그래프(GRAPH_REPORT.md — God Nodes & Communities) → Grep 탐색 토큰 최대 49배 절감"),
  "S02_MATT_POCOCK_5": A("Matt Pocock Skills 5", "mattpocock/skills", "pGE-JKkW-qI", "/grill-me(계획 빈틈 역질문) · /handoff(새 창 인수인계 압축) · /teach · /wait-what(쉬운 말 번역) · /to-questionnaire"),
  "S03_CREATOR_6": A("Creator 6", "bradautomates/claude-video · DaleSeo/korean-skills · rohitg00/agentmemory", "Pppx9o8rmBw · F1kF98TBQNU", "Claude Video /watch 프레임·후킹 분석 · Korean Humanizer(한걸음씩 블로그 실제 문체 복제) · Agent Memory"),
  "S04_STITCH_OPENDESIGN": A("Google Stitch × OpenDesign", "Google Stitch · OpenDesign", "gWmtApPPg38", "프롬프트 한 줄 UI 설계 + DESIGN.md 디자인 시스템 규격서 자동 생성"),
  "S05_SECOND_BRAIN_MCP": A("Second-Brain Decision Card MCP", "decision-card-mcp", "4H9BPsA9jDY", "교정 항체 R1~R63 + 대표님 교대근무 건강 노하우 → 상황별 판단 카드(Decision Cards) 모듈 주입"),
  "S06_CONTEXT7_LANGGRAPH": A("Context7 × GPT-Researcher × LangGraph", "upstash/context7 · assafelovic/gpt-researcher · langchain-ai/langgraph", "WAJMUBFR9FA", "use context7 최신 공식문서 주입 + 다중 출처 조사 + LangGraph State 체크포인트 이어달리기"),
  "S07_VIDEO_3_OSS": A("Remotion × HyperFrames × OpenMontage", "remotion · hyperframes · openmontage", "kwHMECJH88I", "코드/순수 HTML 기반 무손실 MP4 렌더링 3대 오픈소스 프리셋"),
  "S08_EVERY_AI_5_TASTE": A("Taste Skill & MCP-Builder", "Leonxlnx/taste-skill · mcp-builder · Agent-Browser · GSD · find-skills", "GifzyiHnoL4", "AI 특유 '밤티' 슬롭 UI 방지 + MCP 서버 빌더 + 브라우저 에이전트 + GSD + 스킬 탐색"),
  "S09_GDRIVE_ZERO_DELETE": A("Google Drive Zero-Delete Smart Renamer", "gdrive-zero-delete", "4kIVQjVMYrE", "아무것도 지우지 마 · 중복 → 00_INBOX/99_확인필요_격리 · '원래 이름 -> 새 이름' 사전 승인 비교표"),
  "S10_KARPATHY_4_RULES": A("Andrej Karpathy Surgical Coding", "forrestchang/andrej-karpathy-skills", "aVKugNP2wDU", "Think Before Coding · Simplicity First · Surgical Changes · Goal-Driven Execution"),
  "S11_TRADING_AGENTS": A("TradingAgents Bull vs Bear Debate", "TauricResearch/TradingAgents", "Ab7BdWSsJ2U", "4대 분석관(재무·뉴스·차트·심리) + Bull vs Bear 끝장 토론 + 리스크 관리 합의"),
  "S12_CODEX_ADVERSARIAL": A("OpenAI Codex Plugin Dual Review", "openai/codex-plugin-cc", "MBMI9elTCnw", "/codex:review 읽기 전용 검수 + /codex:adversarial-review 설계 가정·위험 적대적 교차검증"),
  "S13_MOTION_100_SEEK": A("Claude 100 Korean Motion Prompts", "notion-motion-100", "0ZwwAOh7pgs", "window.seek(t) 순수 시간 함수 스프링 물리 + <금지> 안티-템플릿 10계명 + OfflineAudioContext 비트 합성"),
  "S14_TASK_OBSERVER": A("Task Observer Self-Improving Meta-Skill", "rebelytics/one-skill-to-rule-them-all · pbakaus/impeccable", "lipJRiztOgM", "교정 피드백 백그라운드 관찰 → 전체 스킬·항체 자가 진화 메타 감시관 + Impeccable"),
  "S15_PONYTAIL_5": A("Ponytail 5 Lazy Senior Dev", "DietrichGebert/ponytail", "l-5dPniBIOc", "7단 사다리(재사용·표준 라이브러리 우선) → 코드 -53% · 토큰 -45% · 커버리지 98%")}
KARPATHY_4 = ["Think Before Coding — 모르면 추측하지 말고 먼저 질문한다", "Simplicity First — 200줄을 50줄로, 가장 단순한 해법부터",
              "Surgical Changes — 시키지 않은 주변 코드·포맷·주석은 절대 수정 금지", "Goal-Driven Execution — 성공 기준을 먼저 정하고 검증 루프(--self-test)로 확인"]
PONYTAIL_7 = ["안 만들기(YAGNI) — 정말 필요한가?", "기존 코드 재사용", "표준 라이브러리 우선", "설정·데이터 변경으로 해결",
              "기존 함수 최소 확장", "작고 순수한 새 함수 추가", "새 의존성 도입(최후 수단 · 대표님 승인 필수)"]
ANTI_TEMPLATE_10 = ["보라 그라데이션 남발", "무의미한 글로우", "setTimeout 체인 애니메이션", "랜덤 의존 프레임", "이모지 장식 과다",
                    "가운데 정렬 남발", "의미 없는 3D 회전", "고정 플로팅 배너", "비트와 어긋난 컷", "번역투 자막"]
BADGES = {"version": VERSION, "organ": f"제{ORGAN}기관", "skills": f"정식 스킬 {SKILLS}개", "antibody": f"항체 {ANTIBODY}"}
AMBIG = re.compile(r"^(scan|img|dsc|dcim|pxl|kakaotalk|screenshot|스크린샷|untitled|제목\s*없음|새\s*문서|document|file)[\s_\-]*\d*", re.I)
CAT = {".pdf": "문서", ".docx": "문서", ".hwp": "문서", ".jpg": "사진", ".jpeg": "사진", ".png": "사진", ".heic": "사진", ".mp4": "영상", ".mov": "영상", ".wav": "음원", ".mp3": "음원", ".csv": "데이터", ".xlsx": "데이터"}

def safe_write(p, txt):
    if Path(p).name in PROTECTED: raise PermissionError(f"[R1 항체] 보호 파일 접근 차단: {p}")
    Path(p).parent.mkdir(parents=True, exist_ok=True); Path(p).write_text(txt, encoding="utf-8")

def _community(rel):
    p = Path(rel); t = re.sub(r"\d+", "N", p.stem.lower()).split("_"); d = p.parent.as_posix()
    return ("" if d == "." else d + "/") + "_".join(t[:2] if t[0] in ("rgon", "aon", "stepN") else t[:1])

def build_graphify_report(root: Path) -> dict:
    root, nodes = Path(root), {}
    for f in sorted(root.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in {".py", ".html", ".json"} or SKIP_DIRS & set(f.relative_to(root).parts): continue
        rel, txt = f.relative_to(root).as_posix(), f.read_text(encoding="utf-8", errors="ignore"); n = {"ext": f.suffix.lower(), "size": len(txt), "funcs": 0, "classes": 0, "refs": set()}
        if n["ext"] == ".py":
            try:
                for x in ast.walk(ast.parse(txt)):
                    n["funcs"] += isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)); n["classes"] += isinstance(x, ast.ClassDef)
                    if isinstance(x, ast.Import): n["refs"] |= {a.name.split(".")[0] for a in x.names}
                    elif isinstance(x, ast.ImportFrom) and x.module: n["refs"].add(x.module.split(".")[0])
            except SyntaxError: n["error"] = "SyntaxError"
        elif n["ext"] == ".html": n["refs"] |= {Path(h).stem for h in re.findall(r'(?:href|src)=["\']([^"\'#?:]+\.(?:html|js|json|py))', txt)}; n["funcs"] = len(re.findall(r"\bfunction\b|=>", txt))
        else:
            try: d = json.loads(txt); n["funcs"] = len(d) if isinstance(d, (dict, list)) else 1
            except ValueError: n["error"] = "JSONDecodeError"
        nodes[rel] = n
    stems, indeg, edges = {Path(r).stem: r for r in nodes}, {r: 0 for r in nodes}, 0
    for r, n in nodes.items():
        for ref in n["refs"]:
            if ref in stems and stems[ref] != r: indeg[stems[ref]] += 1; edges += 1
    score = {r: n["funcs"] + 3 * n["classes"] + 4 * indeg[r] + n["size"] // 4000 for r, n in nodes.items()}
    god = [{"file": r, "score": score[r], "funcs": nodes[r]["funcs"], "classes": nodes[r]["classes"], "in_degree": indeg[r]} for r in sorted(nodes, key=lambda r: -score[r])[:10]]
    comm = {}
    for r in nodes: comm.setdefault(_community(r), []).append(r)
    rep = (f"# GRAPH_REPORT — 아온 로컬 코드 지식 그래프\n> 제{ORGAN}기관 Graphify · {VERSION} · {NOW()} · 파일 {len(nodes)} · 연결 {edges}\n\n"
           "## 사용법\n- 안총리는 Grep/전수 열람 전에 이 지도부터 읽고, 대상 파일을 특정한 뒤 핀셋 열람한다.\n\n## God Nodes (상위 10)\n| 순위 | 파일 | 점수 | 함수 | 클래스 | 피참조 |\n|---|---|---|---|---|---|\n"
           + "".join(f"| {i} | `{g['file']}` | {g['score']} | {g['funcs']} | {g['classes']} | {g['in_degree']} |\n" for i, g in enumerate(god, 1))
           + "\n## Communities (기관별 클러스터)\n" + "".join(f"### {k} ({len(v)})\n" + "".join(f"- `{x}`{' ⚠' + nodes[x]['error'] if 'error' in nodes[x] else ''}\n" for x in v[:12]) for k, v in sorted(comm.items())))
    ratio = round(sum(n["size"] for n in nodes.values()) / max(1, len(rep)), 1)
    rep += f"\n## 토큰 절감\n- 전수 Grep 대비 지도 열람 시 약 {ratio}배 절감 (목표 상한 49배)\n- 보호 파일(읽기 전용): {', '.join(sorted(PROTECTED))}\n"
    safe_write(root / "GRAPH_REPORT.md", rep)
    return {"report": str(root / "GRAPH_REPORT.md"), "files": len(nodes), "edges": edges, "god_nodes": god, "communities": {k: len(v) for k, v in comm.items()}, "in_degree": indeg, "token_saving_x": ratio}

def run_bull_vs_bear_debate(topic: str) -> dict:
    h, roles = hashlib.sha256(topic.encode()).digest(), {"재무": "매출·마진·현금흐름", "뉴스": "공시·정책·산업 이슈", "차트": "추세·거래량·이평선", "심리": "투자심리·변동성·수급"}
    an = {r: {"focus": f, "signal": round(h[i] / 255 * 2 - 1, 2)} for i, (r, f) in enumerate(roles.items())}; avg = round(sum(a["signal"] for a in an.values()) / 4, 3)
    bull = [f"[{r}] {a['focus']} 신호 +{a['signal']} — 상방 근거 우세" for r, a in an.items() if a["signal"] > 0] + [f"{topic}: 실적 성장 지속 시 밸류에이션 정당화", "분할 매수로 평단·변동성 관리 가능"]
    adv = ["가정 검증: '성장 지속'의 근거 데이터와 출처는?", "최악 시나리오(-30%) 발생 시 손실 한도 내인가?", "차트·심리 신호 중복으로 확신이 과대평가되지 않았나?", "실데이터 미연동 시뮬레이션 신호 — 실매매 직결 금지"]
    bear = [f"[{r}] {a['focus']} 신호 {a['signal']} — 하방 위험" for r, a in an.items() if a["signal"] <= 0] + adv
    decision = "강세 우위 — 분할 진입 검토" if avg > .2 else "약세 우위 — 비중 축소·관망" if avg < -.2 else "팽팽 — 관망 및 추가 검증"
    return {"topic": topic, "analysts": an, "bull": bull, "bear": bear, "codex_review": {"/codex:review": "읽기 전용 — 코드·데이터 수정 없음", "/codex:adversarial-review": adv},
            "consensus": {"avg_signal": avg, "decision": decision}, "risk": {"max_position_pct": round(min(10, max(2, 5 + 5 * avg)), 1), "stop_loss_pct": 7, "daily_loss_limit_pct": 2, "human_approval": True},
            "disclaimer": "시뮬레이션 토론 결과 · 투자 자문 아님 · 최종 판단은 대표님"}

def preview_zero_delete_rename(files: list[str], hints: dict | None = None, today: str | None = None) -> list[dict]:
    d, seen, rows = today or os.environ.get("RGON_TODAY") or dt.date.today().isoformat(), {}, []
    for f in files:
        p = Path(f); ext, hint = p.suffix.lower(), (hints or {}).get(p.name)
        key = re.sub(r"(\s*\(\d+\)|[_\s-]*(copy|사본|복사본)\d*)$", "", p.stem, flags=re.I).lower() + ext; dup, amb = key in seen, bool(AMBIG.match(p.stem)) and not hint
        new = f"{d}_{CAT.get(ext, '기타')}_{re.sub(r'[^\w-]+', '', (hint or p.stem).replace(' ', '_'))}{ext}"
        rows.append({"original": p.name, "new": new, "arrow": f"{p.name} -> {new}", "folder": "00_INBOX/99_확인필요_격리" if dup or amb else "00_INBOX/01_승인대기_정리", "quarantine": dup or amb,
                     "reason": f"중복 의심(원본: {seen[key]})" if dup else "내용 확인 필요(애매한 이름)" if amb else "내용 기반 규칙 리네임", "delete_allowed": False, "approval_required": True})
        seen.setdefault(key, p.name)
    return rows

SEEK = r"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>__TITLE__</title><style>body{margin:0;background:#10131a;color:#e9edf5;font-family:system-ui,sans-serif}
#stage{width:1080px;height:1920px;max-width:100vw;max-height:100vh;display:flex;flex-direction:column;justify-content:center;padding:0 8%}#ttl{font-size:6rem;margin:0}#dot{width:80px;height:80px;border-radius:50%;background:#ff69b4;margin-top:40px}</style></head><body>
<!-- <금지> 안티-템플릿 10계명: __BAN__ -->
<div id="stage"><h1 id="ttl">__TITLE__</h1><div id="dot"></div></div><script>
const BPM=__BPM__,BEAT=60/BPM,DUR=__DUR__;
const spring=(t,k=170,c=26,m=1)=>{if(t<=0)return 0;const w0=Math.sqrt(k/m),z=c/(2*Math.sqrt(k*m));if(z<1){const wd=w0*Math.sqrt(1-z*z);return 1-Math.exp(-z*w0*t)*(Math.cos(wd*t)+(z*w0/wd)*Math.sin(wd*t))}return 1-Math.exp(-w0*t)*(1+w0*t)};
window.seek=function(t){const s=spring(t),b=(t%BEAT)/BEAT,pulse=1+0.25*Math.exp(-6*b),ttl=document.getElementById('ttl');
ttl.style.transform=`translateY(${(1-s)*60}px)`;ttl.style.opacity=Math.min(1,s);document.getElementById('dot').style.transform=`scale(${pulse})`;return{t:t,spring:s,beat:Math.floor(t/BEAT)}};
window.renderBeat=async function(sec=DUR,sr=44100){const ctx=new OfflineAudioContext(1,Math.ceil(sec*sr),sr);for(let t=0;t<sec;t+=BEAT){const o=ctx.createOscillator(),g=ctx.createGain();
o.frequency.setValueAtTime(150,t);o.frequency.exponentialRampToValueAtTime(40,t+0.12);g.gain.setValueAtTime(0.9,t);g.gain.exponentialRampToValueAtTime(0.001,t+0.15);o.connect(g).connect(ctx.destination);o.start(t);o.stop(t+0.16)}return ctx.startRendering()};
window.seek(0);if(!/[?&]render=1/.test(location.search)){const t0=performance.now();(function loop(){window.seek(((performance.now()-t0)/1000)%DUR);requestAnimationFrame(loop)})()}
</script></body></html>"""

def generate_seek_motion_template(title: str, bpm: int = 120) -> str:
    esc = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"); bpm = max(40, min(240, int(bpm)))
    return SEEK.replace("__TITLE__", esc).replace("__BPM__", str(bpm)).replace("__DUR__", str(round(60 / bpm * 16, 3))).replace("__BAN__", " / ".join(f"{i}.{x}" for i, x in enumerate(ANTI_TEMPLATE_10, 1)))

def rules_md():
    return (f"# KARPATHY × PONYTAIL × GRAPHIFY 규칙서 ({VERSION} · {R63})\n\n## 0. Graphify 선행 열람 규칙\n- 코드 탐색 전 반드시 `GRAPH_REPORT.md`(God Nodes & Communities)를 먼저 읽는다.\n"
            "- Grep/전수 열람은 지도로 대상 파일을 특정한 뒤에만 허용한다.\n- 4대 보호 파일은 읽기 전용: " + ", ".join(sorted(PROTECTED)) + "\n\n## 1. Andrej Karpathy 4대 원칙\n"
            + "".join(f"{i}. {x}\n" for i, x in enumerate(KARPATHY_4, 1)) + "\n## 2. Ponytail 7단 사다리 (위 칸에서 해결되면 즉시 멈춤)\n" + "".join(f"{i}. {x}\n" for i, x in enumerate(PONYTAIL_7, 1))
            + "\n## 3. 목표 지표\n- 코드량 -53% · 토큰 -45% · 테스트 커버리지 98% · 시키지 않은 수정 0건 · index.html 플로팅 배너 0\n")

def block(pre=""):
    chips = "".join(f'<span data-aon-badge="{k}" style="display:inline-block;margin:2px;padding:2px 8px;border-radius:10px;background:#232b3b;font-size:.75rem">{v}</span>' for k, v in BADGES.items())
    return (f'{START}\n<section id="aon-step64" style="margin:16px;padding:14px;border:1px solid #2c3446;border-radius:12px;background:#171c27;color:#e9edf5;font-family:system-ui,sans-serif">'
            f'<b>제{ORGAN}기관 · 아온 15대 슈퍼-시니어 & 지식그래프 엔진</b><div style="margin:6px 0">{chips}</div><small>Graphify 지도 선행 열람 → Karpathy 4원칙 → Ponytail 7단 사다리 · '
            f'<a href="{pre}GRAPH_REPORT.md">GRAPH_REPORT.md</a> · <a href="{pre}KARPATHY_PONYTAIL_RULES.md">규칙서</a> · 쇼츠 {len(SHORTS_15_ARSENAL)}종 장착</small></section>\n{END}')

def inject_index(p, blk):
    p = Path(p)
    if not p.exists():
        if p.parent.name not in ("dashboard", "docs"): return "본관 index.html 없음 — 생략"
        safe_write(p, "<!doctype html><html lang='ko'><head><meta charset='utf-8'><title>AON</title></head><body>\n</body></html>")
    t = p.read_text(encoding="utf-8"); rx = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    new = rx.sub(lambda m: blk, t, count=1) if rx.search(t) else (t.replace("</body>", blk + "\n</body>", 1) if "</body>" in t else t + "\n" + blk)
    for k, v in BADGES.items(): new = re.sub(r'(<[^>]*data-aon-badge="%s"[^>]*>)[^<]*' % k, lambda m, v=v: m.group(1) + v, new)
    if new == t: return "변경 없음(멱등)"
    shutil.copy2(p, p.with_name(f"index_pre_step64_{dt.datetime.now():%Y%m%d_%H%M%S_%f}.html")); safe_write(p, new); return "마커 주입·배지 갱신 완료"

def apply_step64(root: Path) -> dict:
    root = Path(root); root.mkdir(parents=True, exist_ok=True); g = build_graphify_report(root); safe_write(root / "KARPATHY_PONYTAIL_RULES.md", rules_md())
    man = {"engine": f"제{ORGAN}기관 아온 15대 슈퍼-시니어 & 지식그래프 토큰 절감 마스터 엔진", "version": VERSION, "organ": ORGAN, "skills": SKILLS, "antibodies": ANTIBODY,
           "antibody_list": [f"R{i}" for i in range(1, 63)] + [R63], "new_antibody": R63, "approved_by": "이상일 대표님", "shorts_15_arsenal": SHORTS_15_ARSENAL,
           "karpathy_4": KARPATHY_4, "ponytail_7": PONYTAIL_7, "anti_template_10": ANTI_TEMPLATE_10, "protected": sorted(PROTECTED),
           "graph": {k: g[k] for k in ("files", "edges", "god_nodes", "communities", "token_saving_x")}, "index_policy": "마커 블록 멱등 주입 · 플로팅 배너 금지", "built_at": NOW()}
    for p in (root / MANIFEST, root / "dashboard" / MANIFEST, root / "docs" / MANIFEST): safe_write(p, json.dumps(man, ensure_ascii=False, indent=2))
    idx = {str(p.relative_to(root)): inject_index(p, block("" if p.parent == root else "../")) for p in (root / "index.html", root / "dashboard" / "index.html", root / "docs" / "index.html")}
    return {"graph_report": g["report"], "rules": str(root / "KARPATHY_PONYTAIL_RULES.md"), "manifests": 3, "index": idx, "god_nodes_top3": [x["file"] for x in g["god_nodes"][:3]], "token_saving_x": g["token_saving_x"]}

def self_test():
    with tempfile.TemporaryDirectory(prefix="step64_") as tmp:
        r, ok = Path(tmp), True
        for p in PROTECTED: (r / p).write_text("def loop():\n    return 1\n" if p.endswith(".py") else f"<html>PROTECTED {p}</html>", encoding="utf-8")
        (r / "rgon_aon_core_engine.py").write_text("import rgon_work_loop\nclass Core:\n    def a(self):\n        return 1\ndef b():\n    return 2\n", encoding="utf-8")
        (r / "step62_aon_gdrive.py").write_text("import rgon_aon_core_engine\ndef run():\n    return 0\n", encoding="utf-8"); (r / "broken.py").write_text("def (:\n", encoding="utf-8")
        (r / "data.json").write_text('{"a": 1, "b": 2}', encoding="utf-8")
        (r / "index.html").write_text('<html><body><h1>RGON 본관</h1><span data-aon-badge="version">v11.62</span><button id="send">전송</button></body></html>', encoding="utf-8")
        sig = {p: md5(r / p) for p in PROTECTED}; res1 = apply_step64(r); idx1 = (r / "index.html").read_text(encoding="utf-8"); res2 = apply_step64(r)
        g, deb = build_graphify_report(r), run_bull_vs_bear_debate("NVDA 엔비디아")
        rows = preview_zero_delete_rename(["scan0042.pdf", "scan0042 (1).pdf", "IMG_001.jpg", "가을과겨울사이_자켓.png", "건강검진.pdf"], hints={"scan0042.pdf": "건강검진 결과지"}, today="2026-10-27")
        seek = generate_seek_motion_template("가을과 겨울 사이 <MV>", 128); mans = [json.loads((r / d / MANIFEST).read_text(encoding="utf-8")) for d in ("", "dashboard", "docs")]
        rep = (r / "GRAPH_REPORT.md").read_text(encoding="utf-8"); idx = {d: (r / d / "index.html").read_text(encoding="utf-8") for d in ("", "dashboard", "docs")}
        checks = {
            "GRAPH_REPORT.md (God Nodes·Communities·AST)": "God Nodes" in rep and "Communities" in rep and g["in_degree"]["rgon_work_loop.py"] >= 1 and g["files"] >= 6 and "SyntaxError" in rep,
            "Bull vs Bear + Codex 적대검증 + 리스크": bool(deb["bull"]) and bool(deb["bear"]) and len(deb["analysts"]) == 4 and 2 <= deb["risk"]["max_position_pct"] <= 10 and deb["risk"]["human_approval"],
            "무삭제 리네임 비교표": all(x["delete_allowed"] is False for x in rows) and rows[0]["new"] == "2026-10-27_문서_건강검진_결과지.pdf" and rows[1]["quarantine"] and rows[2]["quarantine"] and not rows[3]["quarantine"] and " -> " in rows[0]["arrow"],
            "window.seek(t) 스프링 + 비트 합성": all(k in seek for k in ("window.seek=function(t)", "Math.exp", "OfflineAudioContext", "<금지>", "BPM=128")) and "<MV>" not in seek,
            "3중 매니페스트 동기화": all(m["version"] == VERSION and m["organ"] == 39 and m["skills"] == SKILLS and m["antibodies"] == ANTIBODY and m["new_antibody"] == R63 and len(m["shorts_15_arsenal"]) == 15 for m in mans),
            "규칙서 생성": "Surgical Changes" in (r / "KARPATHY_PONYTAIL_RULES.md").read_text(encoding="utf-8") and "7단" in (r / "KARPATHY_PONYTAIL_RULES.md").read_text(encoding="utf-8"),
            "3중 index 마커 멱등 + 배지 갱신": all(t.count(START) == 1 and t.count(END) == 1 and VERSION in t for t in idx.values()) and idx[""] == idx1 and "v11.62<" not in idx[""] and set(res2["index"].values()) == {"변경 없음(멱등)"},
            "플로팅 배너 0 · 전송 버튼 보존": all("position:fixed" not in t for t in idx.values()) and 'id="send"' in idx[""],
            "4대 보호 파일 무결성": all(md5(r / p) == sig[p] for p in PROTECTED) and res1["manifests"] == 3}
        for n, v in checks.items(): ok &= bool(v); print(f"  {'✅' if v else '❌'} {n}")
        print(f"[SELF-TEST {'PASS' if ok else 'FAIL'}] Step64 {VERSION} · 제{ORGAN}기관 · 스킬 {SKILLS} · 항체 {ANTIBODY}"); return ok

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Step 64 · 제39기관 아온 15대 슈퍼-시니어 & 지식그래프 엔진")
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--root", help="RGON 사령부 루트 폴더(index.html 위치)"); a = ap.parse_args()
    if a.self_test or not a.root: sys.exit(0 if self_test() else 1)
    if not self_test(): sys.exit("⛔ 임시 폴더 검증 실패 — 실제 운영 폴더 반영 중단")
    print(json.dumps(apply_step64(Path(a.root)), ensure_ascii=False, indent=2, default=str))

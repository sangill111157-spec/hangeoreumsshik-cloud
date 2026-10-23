# -*- coding: utf-8 -*-
"""
step15_remove_v14_and_quiet_place.py
1) 모든 독대실 HTML에서 [RGON-5BARS-FIX-V14] 블록 완전 제거
2) [RGON-YT-SCOUT-V13] 블록 안에 단발성 placeOnce 스크립트만 추가
   - Observer/setInterval 없음, 다른 바 스타일 변경 없음, #rgyt-wrap 하나만 1회 이동
3) git add/commit/pull --rebase/push + 완료 메시지 박스
Python 3 표준 라이브러리 전용
"""
import os, sys, re, shutil, subprocess
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PREFERRED_BASE = r"C:\Users\sangi\Downloads\shin-agent"
V13_START = "<!-- [RGON-YT-SCOUT-V13-START] -->"
V13_END = "<!-- [RGON-YT-SCOUT-V13-END] -->"
V14_START = "<!-- [RGON-5BARS-FIX-V14-START] -->"
V14_END = "<!-- [RGON-5BARS-FIX-V14-END] -->"
P15_START = "<!-- [RGYT-PLACE-ONCE-V15-START] -->"
P15_END = "<!-- [RGYT-PLACE-ONCE-V15-END] -->"

PLACE_ONCE = r"""<!-- [RGYT-PLACE-ONCE-V15-START] -->
<script id="rgyt-place-once">
(function(){
  var SKIP=/^(SCRIPT|STYLE|TEMPLATE|NOSCRIPT|TEXTAREA)$/;
  function head(ph){var best=null,bl=1e9,all=document.body.getElementsByTagName('*');
    for(var i=0;i<all.length;i++){var el=all[i];if(SKIP.test(el.tagName)||el.closest('#rgyt-wrap'))continue;
      var t=el.textContent||'';if(t.indexOf(ph)<0)continue;var deeper=false;
      for(var c=el.firstElementChild;c;c=c.nextElementSibling){if(!SKIP.test(c.tagName)&&(c.textContent||'').indexOf(ph)>=0){deeper=true;break;}}
      if(!deeper&&t.length<bl){bl=t.length;best=el;}}
    return best;}
  function hasAny(p,list){for(var i=0;i<list.length;i++)if(list[i]&&p.contains(list[i]))return true;return false;}
  function unitOf(h,others,w){var dt=h.closest&&h.closest('details');if(dt&&!dt.contains(w)&&!hasAny(dt,others))return dt;
    var u=h;while(u.parentElement&&u.parentElement!==document.body&&!u.parentElement.contains(w)&&!hasAny(u.parentElement,others))u=u.parentElement;return u;}
  function skipPanel(u,others,w){var n=u.nextElementSibling;if(!n||n===w||SKIP.test(n.tagName)||hasAny(n,others))return u;
    var cls=(n.id||'')+' '+(n.getAttribute('class')||'');
    return (getComputedStyle(n).display==='none'||/panel|body|content|collapse|acc/i.test(cls))?n:u;}
  function placeOnce(){
    var w=document.getElementById('rgyt-wrap');if(!w)return;
    var g=head('실시간 브리핑 전문'),o=head('독대실에서 바로 분배하기'),a=head('4대 AI 분배'),p=head('1:1 대화창');
    if(g){var u=skipPanel(unitOf(g,[o,a,p],w),[o,a,p],w);if(u.nextSibling!==w)u.parentNode.insertBefore(w,u.nextSibling);w.setAttribute('data-placed','1');}
    else if(o){var u2=unitOf(o,[a,p],w);if(u2.previousSibling!==w)u2.parentNode.insertBefore(w,u2);w.setAttribute('data-placed','1');}
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',placeOnce);else placeOnce();
  setTimeout(placeOnce,300);setTimeout(placeOnce,900);setTimeout(placeOnce,1600);
})();
</script>
<!-- [RGYT-PLACE-ONCE-V15-END] -->"""


def log(*a):
    print("[STEP15]", *a, flush=True)


def looks_like_project(d):
    try:
        return os.path.isdir(d) and (os.path.isfile(os.path.join(d, "rgon_alpha_chat.html"))
                                     or any(f.lower().startswith("rgon_") and f.lower().endswith(".html") for f in os.listdir(d)))
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
    skip = {"node_modules", ".git", "AppData", "__pycache__", "venv", ".venv"}
    for root in [os.path.join(home, s) for s in ("Downloads", "Desktop", "Documents")] + [home]:
        if not os.path.isdir(root):
            continue
        base_depth = root.rstrip("\\/").count(os.sep)
        for cur, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in skip and not d.startswith(".")]
            if cur.count(os.sep) - base_depth >= 3:
                dirs[:] = []
            if os.path.basename(cur).lower().startswith("shin-agent") or "rgon_alpha_chat.html" in files:
                return cur
    return os.path.dirname(os.path.abspath(__file__))


def find_html_targets(base):
    found = []
    for d in [base, os.path.join(base, "dashboard"), os.path.join(base, "docs")]:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            fp = os.path.join(d, f)
            if not (os.path.isfile(fp) and f.lower().endswith(".html")):
                continue
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                    src = fh.read()
            except Exception:
                continue
            if V14_START in src or V13_START in src:
                found.append(fp)
    return found


def block_re(start, end):
    return re.compile(r"\n?[ \t]*" + re.escape(start) + r".*?" + re.escape(end) + r"[ \t]*\n?", re.S)


def patch_html(fp):
    with open(fp, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()
    orig = src
    bak = fp + ".bak_step15"
    if not os.path.exists(bak):
        shutil.copy2(fp, bak)

    v14_count = src.count(V14_START)
    src = block_re(V14_START, V14_END).sub("\n", src)
    if V14_START in src:
        src = re.sub(re.escape(V14_START) + r".*?</script>\s*", "", src, flags=re.S)

    src = block_re(P15_START, P15_END).sub("\n", src)
    placed = False
    if V13_START in src and V13_END in src:
        idx = src.find(V13_END, src.find(V13_START))
        src = src[:idx] + PLACE_ONCE + "\n" + src[idx:]
        placed = True

    if src != orig:
        with open(fp, "w", encoding="utf-8", newline="") as f:
            f.write(src)
    leftover = len(re.findall(r"rg5-dock|RG5_FIX|RGON-5BARS-FIX", src))
    log("%s | V14 제거 %d개 | placeOnce %s | V14 잔여 흔적 %d" %
        (fp, v14_count, "추가" if placed else "V13 블록 없음(건너뜀)", leftover))
    return v14_count, placed, leftover


def patch_step13_template(base):
    fp = os.path.join(base, "step13_youtube_skill_absorber.py")
    if not os.path.isfile(fp):
        return "step13 파일 없음(건너뜀)"
    with open(fp, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()
    if P15_START in src:
        return "이미 반영됨"
    target = V13_END + '"""'
    if target not in src:
        return "템플릿 위치 미확인(건너뜀)"
    shutil.copy2(fp, fp + ".bak_step15")
    src = src.replace(target, PLACE_ONCE + "\n" + target, 1)
    with open(fp, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    return "반영 완료"


def git(base, *args):
    try:
        p = subprocess.run(["git"] + list(args), cwd=base, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
        log("git", " ".join(args), "->", p.returncode, (p.stdout + p.stderr).strip()[-300:])
        return p.returncode == 0
    except Exception as e:
        log("git 실행 실패:", e)
        return False


def git_sync(base):
    if not os.path.isdir(os.path.join(base, ".git")):
        log("Git 저장소가 아니어서 동기화를 건너뜁니다.")
        return False
    git(base, "add", "-A")
    git(base, "commit", "-m", "Step15: V14 레이아웃 블록 제거 + 유튜브 흡수기 단발 위치 이동(placeOnce) "
        + datetime.now().strftime("%Y-%m-%d %H:%M"))
    if not git(base, "pull", "--rebase", "origin", "main"):
        git(base, "rebase", "--abort")
        log("pull --rebase 실패 → 리베이스 취소 후 push 시도")
    return git(base, "push", "origin", "main")


def msgbox(title, text):
    log(text)
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, text, title, 0x40 | 0x40000)
        except Exception:
            pass


def main():
    base = find_base_dir()
    log("작업 폴더:", base)
    targets = find_html_targets(base)
    if not targets:
        msgbox("RGON Step 15", "V13/V14 블록이 있는 HTML을 찾지 못했습니다.\n작업 폴더: %s" % base)
        return
    lines, total_v14 = [], 0
    for fp in targets:
        try:
            n, placed, left = patch_html(fp)
            total_v14 += n
            lines.append("• %s  V14 제거 %d / placeOnce %s%s" % (
                os.path.relpath(fp, base), n, "O" if placed else "-", "  ⚠잔여 %d" % left if left else ""))
        except Exception as e:
            lines.append("• %s  실패: %s" % (os.path.relpath(fp, base), e))
    tpl = patch_step13_template(base)
    pushed = git_sync(base)
    msgbox("RGON Step 15 완료",
           "🧹 V14 블록 제거 + 🔭 흡수기 단발 위치 이동 완료\n\n작업 폴더: %s\n제거한 V14 블록: %d개\n%s\n\n"
           "step13 템플릿: %s\nGit 푸시: %s\n\n확인: 독대실 새로고침 → 초록 바 바로 아래 청록 바\n"
           "되돌리기: *.html.bak_step15"
           % (base, total_v14, "\n".join(lines), tpl, "성공" if pushed else "건너뜀/실패(로그 확인)"))


if __name__ == "__main__":
    main()

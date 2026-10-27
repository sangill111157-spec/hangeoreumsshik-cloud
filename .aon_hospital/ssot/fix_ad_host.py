from pathlib import Path
import subprocess
import sys

p = Path(r"C:\Users\sangi\Downloads\shin-agent\upgrade_all_in_one_ad.py")
code = p.read_text(encoding="utf-8")

old_func = """  function getMessageHost(input) {
    if (OPTIONS.messagesSelector) {
      const custom = querySafely(OPTIONS.messagesSelector);
      if (custom) return custom;
    }

    for (const selector of MESSAGE_SELECTORS) {
      const candidate = querySafely(selector);
      if (
        candidate &&
        candidate !== input &&
        !candidate.contains(input)
      ) {
        return candidate;
      }
    }

    if (STATE.fallbackLog?.isConnected) return STATE.fallbackLog;

    const log = el("div", "rgon-ad-log");
    log.setAttribute("role", "log");
    log.setAttribute("aria-label", "르곤 알파 광고 기획 대화");

    const anchor = input.closest("form") || input.parentElement;

    if (anchor?.parentNode && anchor !== document.body) {
      anchor.parentNode.insertBefore(log, anchor);
    } else {
      document.body.appendChild(log);
    }

    STATE.fallbackLog = log;
    return log;
  }"""

new_func = """  function getMessageHost(input) {
    // 1. 기존 말풍선('르곤-알파' 또는 '이상일 대표님')이 들어있는 실제 스크롤 컨테이너를 최우선 탐색
    const allDivs = Array.from(document.querySelectorAll("div, main, section"));
    for (const d of allDivs) {
      if (d.contains(input)) continue;
      const txt = d.textContent || "";
      if ((txt.includes("르곤-알파") || txt.includes("대시보드 총괄사령관")) && d.children.length >= 1) {
        const style = getComputedStyle(d);
        if (style.overflowY === "auto" || style.overflowY === "scroll" || d.id.includes("chat") || d.id.includes("feed") || d.id.includes("msg") || d.className.includes("chat") || d.className.includes("feed") || d.className.includes("messages")) {
          return d;
        }
      }
    }

    // 2. '대시보드 총괄사령관' 배지가 있는 가장 마지막 말풍선 카드의 부모 컨테이너 반환
    const badges = Array.from(document.querySelectorAll("*")).filter(
      n => n.children.length === 0 && (n.textContent || "").trim() === "대시보드 총괄사령관"
    );
    if (badges.length > 0) {
      let card = badges[badges.length - 1];
      while (card && card.parentElement && card.parentElement !== document.body) {
        const parent = card.parentElement;
        if (!parent.contains(input) && parent.clientHeight > 120) {
          return parent;
        }
        card = parent;
      }
    }

    // 3. 기존 셀렉터 탐색
    for (const selector of MESSAGE_SELECTORS) {
      const candidate = querySafely(selector);
      if (candidate && candidate !== input && !candidate.contains(input)) {
        return candidate;
      }
    }

    // 4. 최후 수단: 화면 중앙 상단에 눈에 보이는 고정/인라인 컨테이너 생성
    if (STATE.fallbackLog?.isConnected) return STATE.fallbackLog;
    const log = el("div", "rgon-ad-log");
    log.style.cssText = "max-width:920px; margin:16px auto 120px auto; padding:12px; position:relative; z-index:50;";
    const firstInputBar = input.closest("div[style*='fixed'], footer, form") || input.parentElement?.parentElement || input.parentElement;
    if (firstInputBar?.parentNode) {
      firstInputBar.parentNode.insertBefore(log, firstInputBar);
    } else {
      document.body.prepend(log);
    }
    STATE.fallbackLog = log;
    return log;
  }"""

if old_func not in code:
    raise RuntimeError("getMessageHost 함수를 찾지 못했습니다.")

code = code.replace(old_func, new_func, 1)
code = code.replace('VERSION = "rgon-ad-studio-20261019-v1"', 'VERSION = "rgon-ad-studio-20261019-v2"')
p.write_text(code, encoding="utf-8")

subprocess.run([sys.executable, "-X", "utf8", str(p)], check=True)
print("FIX AD HOST COMPLETE!")

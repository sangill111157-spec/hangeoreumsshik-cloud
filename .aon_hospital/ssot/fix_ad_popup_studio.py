from pathlib import Path
import subprocess
import sys

p = Path(r"C:\Users\sangi\Downloads\shin-agent\upgrade_all_in_one_ad.py")
code = p.read_text(encoding="utf-8")

old_append = """  function appendPlan(host, text, payload) {
    const user = el("div", "rgon-ad-user", text);
    const assistant = el("article", "rgon-ad-assistant");

    assistant.dataset.rgonAdId = payload.id;
    assistant.appendChild(
      el("h3", "", `르곤-알파 · ${payload.topic} 10초 광고 기획안`)
    );

    const sections = [
      ["🎯 [0~3초 시선강탈 훅(Hook)]", payload.plan.hook],
      ["🔥 [3~7초 핵심 반전 & 디테일(Body)]", payload.plan.body],
      ["🚀 [7~10초 강렬한 클로징(CTA)]", payload.plan.cta],
      ["🎙️ [10초 음성 나레이션 대본]", payload.plan.narration]
    ];

    for (const [title, content] of sections) {
      const section = el("section", "rgon-ad-section");
      section.append(el("strong", "", title), el("p", "", content));
      assistant.appendChild(section);
    }

    const studio = createStudio(payload);
    host.append(user, assistant, studio);

    requestAnimationFrame(() => {
      studio.scrollIntoView({ behavior:"smooth", block:"nearest" });
    });
  }"""

new_append = """  function appendPlan(host, text, payload) {
    // 기존 채팅창 리렌더링에 절대 지워지지 않는 화면 정중앙 전용 올인원 광고 스튜디오 오버레이 생성
    document.getElementById("rgon-ad-floating-center")?.remove();

    const overlay = el("div", "");
    overlay.id = "rgon-ad-floating-center";
    overlay.style.cssText =
      "position:fixed; inset:0; z-index:2147483000; background:rgba(2,6,23,0.82); " +
      "backdrop-filter:blur(6px); display:flex; align-items:center; justify-content:center; " +
      "padding:18px; box-sizing:border-box; overflow-y:auto;";

    const modalCard = el("div", "");
    modalCard.style.cssText =
      "width:min(980px, 96vw); max-height:92vh; overflow-y:auto; background:#0f172a; " +
      "border:2px solid #38bdf8; border-radius:20px; padding:22px; box-sizing:border-box; " +
      "box-shadow:0 25px 70px rgba(0,0,0,0.85); color:#f8fafc; font-family:system-ui,-apple-system,'Malgun Gothic',sans-serif;";

    const topBar = el("div", "");
    topBar.style.cssText =
      "display:flex; align-items:center; justify-content:space-between; gap:12px; " +
      "padding-bottom:14px; margin-bottom:16px; border-bottom:1px solid #334155;";

    const titleEl = el("h2", "", `🎬 르곤-알파 · '${payload.topic}' 10초 올인원 광고 제작 스튜디오`);
    titleEl.style.cssText = "margin:0; font-size:20px; color:#38bdf8; font-weight:800;";

    const closeBtn = el("button", "rgon-ad-btn", "✖ 스튜디오 닫기");
    closeBtn.type = "button";
    closeBtn.style.cssText = "background:#7f1d1d; border-color:#ef4444; color:#fff; font-weight:700;";
    closeBtn.addEventListener("click", () => {
      STATE.activeRun?.cancel?.();
      overlay.remove();
    });

    topBar.append(titleEl, closeBtn);

    const grid = el("div", "");
    grid.style.cssText =
      "display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:18px; align-items:start;";

    const leftCol = el("div", "");
    const user = el("div", "rgon-ad-user", `👑 지시: ${text}`);
    user.style.margin = "0 0 12px 0";

    const assistant = el("article", "rgon-ad-assistant");
    assistant.style.margin = "0";
    assistant.dataset.rgonAdId = payload.id;
    assistant.appendChild(
      el("h3", "", `📋 ${payload.topic} 10초 광고 기획안 & 콘티`)
    );

    const sections = [
      ["🎯 [0~3초 시선강탈 훅(Hook)]", payload.plan.hook],
      ["🔥 [3~7초 핵심 반전 & 디테일(Body)]", payload.plan.body],
      ["🚀 [7~10초 강렬한 클로징(CTA)]", payload.plan.cta],
      ["🎙️ [10초 음성 나레이션 대본]", payload.plan.narration]
    ];

    for (const [title, content] of sections) {
      const section = el("section", "rgon-ad-section");
      section.append(el("strong", "", title), el("p", "", content));
      assistant.appendChild(section);
    }

    leftCol.append(user, assistant);

    const studio = createStudio(payload);
    studio.style.margin = "0";

    grid.append(leftCol, studio);
    modalCard.append(topBar, grid);
    overlay.appendChild(modalCard);
    document.body.appendChild(overlay);

    // 일반 채팅창에도 흔적을 남김
    try {
      if (host && host !== document.body) {
        const reopen = el("button", "rgon-ad-btn", `🎬 '${payload.topic}' 10초 광고 스튜디오 다시 열기`);
        reopen.type = "button";
        reopen.style.margin = "8px 0";
        reopen.addEventListener("click", () => appendPlan(host, text, payload));
        host.appendChild(reopen);
      }
    } catch (_) {}
  }"""

if old_append not in code:
    raise RuntimeError("appendPlan 함수를 찾지 못했습니다.")

code = code.replace(old_append, new_append, 1)
code = code.replace('VERSION = "rgon-ad-studio-20261019-v2"', 'VERSION = "rgon-ad-studio-20261019-v3"')
code = code.replace('VERSION = "rgon-ad-studio-20261019-v1"', 'VERSION = "rgon-ad-studio-20261019-v3"')
p.write_text(code, encoding="utf-8")

subprocess.run([sys.executable, "-X", "utf8", str(p)], check=True)
print("FIX AD POPUP STUDIO v3 COMPLETE!")

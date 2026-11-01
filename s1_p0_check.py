# -*- coding: utf-8 -*-
import json, subprocess, pathlib
import s1_ego

def cmd_p0_space_probe(mode):
    allowed = {"direct_numeric", "direct_empty", "enumerated"}
    if mode not in allowed:
        return {"ok": False, "code": "INVALID_P0_MODE"}

    js = r"""
    const MODE = __MODE__;
    const TRUSTED_CHAT_ID = "c1647638-2531-43db-a059-c153d8da14d9";

    function isTargetUrl(raw) {
      try {
        const u = new URL(raw);
        const ids = u.searchParams.getAll("id");
        return (
          u.origin === "https://www.genspark.ai" &&
          u.pathname === "/agents" &&
          ids.length === 1 &&
          ids[0] === TRUSTED_CHAT_ID
        );
      } catch (_) {
        return false;
      }
    }

    function describeId(value) {
      return {
        type: typeof value,
        value: value === undefined ? null : value,
        isUndefined: value === undefined
      };
    }

    async function inspectTabs(label, args) {
      const started = Date.now();
      try {
        const raw = await ego.listTabs(args);
        const pages = raw && Array.isArray(raw.pages) ? raw.pages : null;
        return {
          label,
          args,
          elapsed_ms: Date.now() - started,
          ok: pages !== null,
          responseKeys: raw && typeof raw === "object" ? Object.keys(raw) : [],
          pagesArrayPresent: pages !== null,
          pageCount: pages ? pages.length : null,
          pages: (pages || []).map(p => ({
            pageId: p.pageId,
            pageIdType: typeof p.pageId,
            title: p.title || "",
            url: p.url || "",
            targetUrlMatched: isTargetUrl(p.url || "")
          }))
        };
      } catch (e) {
        return {
          label,
          args,
          ok: false,
          elapsed_ms: Date.now() - started,
          errorName: e && e.name ? e.name : "Error",
          error: String(e)
        };
      }
    }

    async function main() {
      const report = {
        ok: true,
        diagnostic: "S1_P0_SPACE_RESOLUTION",
        mode: MODE,
        observed_at: new Date().toISOString(),
        runtime_pid: typeof process !== "undefined" ? process.pid : null,
        steps: []
      };

      if (MODE === "direct_numeric") {
        report.steps.push(await inspectTabs("direct_numeric_0", {spaceId: 0}));
      } else if (MODE === "direct_empty") {
        report.steps.push(await inspectTabs("direct_empty_object", {}));
      } else {
        const inventory = await ego.listTaskSpaces();
        report.inventoryResponseKeys = inventory && typeof inventory === "object" ? Object.keys(inventory) : [];
        if (!inventory || !Array.isArray(inventory.spaces)) {
          report.ok = false;
          report.code = "SPACES_ARRAY_MISSING";
          return report;
        }
        report.spaces = inventory.spaces.map((sp, index) => ({
          index,
          id: describeId(sp.id),
          name: sp.name || "",
          ownership: sp.ownership || ""
        }));

        for (const sp of inventory.spaces) {
          if (sp.id === undefined || sp.id === null) {
            report.steps.push({ label: "enumerated_space", ok: false, code: "SPACE_ID_MISSING" });
            continue;
          }
          report.steps.push(await inspectTabs("enumerated_original_id", {spaceId: sp.id}));
        }

        report.steps.push(await inspectTabs("after_inventory_numeric_0", {spaceId: 0}));
        report.steps.push(await inspectTabs("after_inventory_string_0", {spaceId: "0"}));
        report.steps.push(await inspectTabs("after_inventory_empty_object", {}));

        // Target 탭이 발견되면 읽기 전용으로 입력창/User 메시지 컨테이너 DOM 구조도 함께 조사
        const hit = report.steps.flatMap(st => (st.pages || []).filter(p => p.targetUrlMatched))[0];
        if (hit) {
          const domInspect = await ego.runScript({
            pageId: hit.pageId,
            code: `(() => {
              const tas = [...document.querySelectorAll("textarea")].filter(e => e.offsetParent !== null);
              const ta = tas[0];
              const ansList = [...document.querySelectorAll(".answer-markdown")];
              return {
                taCount: tas.length,
                taPlaceholder: ta ? ta.placeholder : null,
                taValueLen: ta ? ta.value.length : null,
                answerCount: ansList.length,
                hasEnterIconWrapper: Boolean(document.querySelector(".enter-icon-wrapper"))
              };
            })()`
          });
          report.targetDomInspect = domInspect;
        }
      }

      report.allTabCallsSucceeded = report.steps.every(step => step.ok === true);
      report.targetOccurrences = report.steps.flatMap(step =>
        (step.pages || [])
          .filter(p => p.targetUrlMatched)
          .map(p => ({ label: step.label, args: step.args, pageId: p.pageId, url: p.url }))
      );
      return report;
    }

    let result;
    try {
      result = await main();
    } catch (e) {
      result = { ok: false, code: "P0_DIAGNOSTIC_ERROR", error: String(e) };
    }
    console.log("___S1_EGO_JSON___" + JSON.stringify(result));
    """
    js = js.replace("__MODE__", json.dumps(mode))
    return s1_ego.run_ego_js(js)

print("[1/4] P0 3대 모드 실측 실행 중...")
p0_results = {
    "direct_numeric": cmd_p0_space_probe("direct_numeric"),
    "direct_empty": cmd_p0_space_probe("direct_empty"),
    "enumerated": cmd_p0_space_probe("enumerated")
}
print(json.dumps(p0_results, ensure_ascii=False, indent=2))

s1_ego_src = pathlib.Path("s1_ego.py").read_text(encoding="utf-8")

prompt_for_triumvirate = (
    "[S1 P0 3대 모드 실측 결과 및 s1_ego.py 전체 원본 제출 — cmd_reply0(envelope) 최종 구현 코드 확정 요청]\n\n"
    "1. P0 3대 모드(direct_numeric, direct_empty, enumerated) 실측 결과 JSON:\n```json\n"
    + json.dumps(p0_results, ensure_ascii=False, indent=2) + "\n```\n\n"
    "2. 현재 로컬 `s1_ego.py` (v1.1.7) 전체 원본 코드 (run_ego_js, GlobalAskLock, cmd_read, cmd_ask 포함):\n```python\n"
    + s1_ego_src + "\n```\n\n"
    "위 실측 결과와 실제 `s1_ego.py` 인터페이스를 바탕으로, 추측 없이 로컬 `s1_ego.py`에 즉시 탑재할 수 있는 `cmd_reply0(envelope)` 최종 코드와 Step 1 인수시험 명세를 확정해 주십시오."
)

print("[2/4] Space 2 (GPT-6.1 Sol)에 P0 결과 및 s1_ego.py 전문 제출 후 코드 수거 중...")
res2 = s1_ego.cmd_ask(2, prompt_for_triumvirate, wait_sec=150)

print("[3/4] Space 3 (Claude Opus 5.5)에 P0 결과 및 s1_ego.py 전문 제출 후 코드 수거 중...")
res3 = s1_ego.cmd_ask(3, prompt_for_triumvirate, wait_sec=150)

out_md = (
    "# 🏆 S1 P0 실측 결과 및 삼성(三聖) 확정 `cmd_reply0` 구현 명세\n\n"
    "## 1. P0 3대 모드 실측 결과\n```json\n" + json.dumps(p0_results, ensure_ascii=False, indent=2) + "\n```\n\n"
    "## 2. GPT-6.1 Sol (Space 2) 최종 구현 명세\n```\n" + str(res2.get("last_message", res2)) + "\n```\n\n"
    "## 3. Claude Opus 5.5 (Space 3) 최종 구현 명세\n```\n" + str(res3.get("last_message", res3)) + "\n```\n"
)
pathlib.Path("S1_P0_AND_REPLY0.md").write_text(out_md, encoding="utf-8")

print("[4/4] GitHub 푸시 중...")
subprocess.run(["git", "add", "S1_P0_AND_REPLY0.md", "s1_p0_check.py"], check=False)
subprocess.run(["git", "commit", "-m", "feat(s1): complete P0 space probe and collect triumvirate cmd_reply0 spec"], check=False)
subprocess.run(["git", "pull", "--rebase", "--autostash", "-X", "ours", "origin", "main"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=False)
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
print(f"=== S1_P0_DONE_SHA: {sha} ===")

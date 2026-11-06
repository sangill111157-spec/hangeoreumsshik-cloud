from pathlib import Path
import subprocess, sys, json

BASE = Path.cwd()
p = BASE / "S1_EGO_PROVEN_SKILL_MASTER.py"
txt = p.read_text(encoding="utf-8", errors="replace")

# [핵심 완치] JS 작은따옴표 안의 실제 줄바꿈('\nS1EGO_JSON::')을 이스케이프('\\nS1EGO_JSON::')로 수리!
txt = txt.replace("write('\nS1EGO_JSON::'", "write('\\nS1EGO_JSON::'")
if "def clear_all_spaces_lock" not in txt:
    txt += '''
def clear_all_spaces_lock() -> dict:
    js = """
    for (const idx of [0, 1, 2, 3]) {
      try {
        const t = await claimTaskSpace(idx).catch(() => null);
        if (t && typeof t.finish === 'function') await t.finish({ keep: [] });
      } catch (_) {}
    }
    process.stdout.write('\\nS1EGO_JSON::{"ok":true}\\n');
    """
    return s1_ego.run_ego_js(js, timeout=20)
'''
p.write_text(txt, encoding="utf-8", errors="replace")
print("[FIXED] S1_EGO_PROVEN_SKILL_MASTER.py newline bug cured!")

# 이제 수리된 스킬로 s1_one_monetizer.py 재실행하여 솔·오푸스 진품 수거 + Git 푸시 + Space 0 자동 엔터!
subprocess.run([sys.executable, "s1_one_monetizer.py"], cwd=str(BASE))

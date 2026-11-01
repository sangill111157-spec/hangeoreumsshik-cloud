import re

p = 's1_zero_paste_daemon.py'
s = open(p, encoding='utf-8').read()

old_ego = '''def ego(js_template, cfg):
    code = js_template.replace("__CFG_JSON__", json.dumps(cfg))
    r = subprocess.run(EGO_CMD, input=code, text=True, encoding="utf-8", errors="replace",
                       capture_output=True, timeout=EGO_TIMEOUT, cwd=str(BASE), shell=True)
    for line in reversed((r.stdout or "").splitlines()):
        if line.startswith("S1JSON::"):
            return json.loads(line[len("S1JSON::"):])
    raise RuntimeError(f"ego 응답 없음 rc={r.returncode} stderr={(r.stderr or '')[-500:]}")'''

new_ego = '''def ego(js_template, cfg):
    import shutil
    code = js_template.replace("__CFG_JSON__", json.dumps(cfg))
    tmp_js = BASE / "_s1_ego_exec.js"
    tmp_js.write_text(code, encoding="utf-8")
    ego_bin = shutil.which("ego-browser") or shutil.which("ego-browser.cmd") or "ego-browser.cmd"
    # 줄바꿈/따옴표 영향이 0%인 AsyncFunction 파일 로더1줄 호출
    loader = "const fs=await import('node:fs'); const c=fs.readFileSync('_s1_ego_exec.js','utf8'); const AF=Object.getPrototypeOf(async function(){}).constructor; await (new AF(c))();"
    r = subprocess.run([ego_bin, "nodejs", loader], text=True, encoding="utf-8", errors="replace",
                       capture_output=True, timeout=EGO_TIMEOUT, cwd=str(BASE))
    for line in reversed((r.stdout or "").splitlines()):
        if line.startswith("S1JSON::"):
            return json.loads(line[len("S1JSON::"):])
    raise RuntimeError(f"ego 응답 없음 rc={r.returncode} stdout={(r.stdout or '')[-300:]} stderr={(r.stderr or '')[-500:]}")'''

if old_ego in s:
    s = s.replace(old_ego, new_ego)
else:
    s = re.sub(r"def ego\(js_template, cfg\):.*?raise RuntimeError\([^\n]+\)", new_ego, s, flags=re.S)

open(p, 'w', encoding='utf-8').write(s)
print("EGO_LOADER_PATCH_OK")

p = 's1_zero_paste_daemon.py'
s = open(p, encoding='utf-8').read()
s = s.replace('["ego-browser.cmd", "nodejs", "-"]', '["ego-browser", "nodejs", "-"]')
s = s.replace('cwd=str(BASE))', 'cwd=str(BASE), shell=True)')
open(p, 'w', encoding='utf-8').write(s)
print("PATCH_OK")

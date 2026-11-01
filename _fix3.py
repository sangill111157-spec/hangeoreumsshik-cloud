p = 's1_zero_paste_daemon.py'
s = open(p, encoding='utf-8').read()
s = s.replace("readFileSync('_s1_ego_exec.js'", "readFileSync('C:/Users/sangi/Downloads/shin-agent/_s1_ego_exec.js'")
open(p, 'w', encoding='utf-8').write(s)
print("ABS_PATH_PATCH_OK")

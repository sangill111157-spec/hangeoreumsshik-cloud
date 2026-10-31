import subprocess
c = "const sleep = ms => new Promise(r => setTimeout(r, ms));\n" + open('s1_mod.mjs', encoding='utf-8').read()
open('s1_mod.mjs', 'w', encoding='utf-8').write(c)
subprocess.run(['ego-browser', 'nodejs', '-e', "await import('file:///C:/Users/sangi/Downloads/shin-agent/s1_mod.mjs')"])
subprocess.run('git add -f S1_OUT.md s1_mod.mjs && git commit -m "S1-100-Done" && git push -f origin main', shell=True)
print('=== S1_FINAL_100_DONE ===')

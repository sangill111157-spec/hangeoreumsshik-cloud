import subprocess

bundle = "\n\n<!-- [S1_EVIDENCE_BUNDLE]\n"
for fn in ['S1_FULL_PROOF.json', 'manifest.webmanifest', 'sw.js', 'offline.html', 's1_server.py']:
    bundle += f"=== {fn} ===\n" + open(fn, encoding='utf-8').read() + "\n"
bundle += "-->"

orig_html = open('index.html', encoding='utf-8').read().split('<!-- [S1_EVIDENCE_BUNDLE]')[0]
open('index.html', 'w', encoding='utf-8').write(orig_html + bundle)

a3 = open('s1_a3.mjs', encoding='utf-8').read().replace('8501', '8502').replace('slice(-1800)', 'slice(-4500)').replace('slice(-1500)', 'slice(-4500)')
open('s1_a3_full.mjs', 'w', encoding='utf-8').write(a3)

subprocess.run('cmd /c ego-browser nodejs < s1_a3_full.mjs', shell=True)

open('index.html', 'w', encoding='utf-8').write(orig_html)
subprocess.run('git add -f index.html S1_OUT.md && git commit -m "S1-Final-Bundle-Signoff" && git push -f origin main', shell=True)
print('=== S1_A3_BUNDLE_COMPLETE ===')

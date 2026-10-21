
import os, subprocess

p = "<style>#rgon-tools-drawer,#rgon-omni-top-drawer{width:100%!important;flex:0 0 100%!important}#dokdae-feed{display:flex!important;flex-direction:column!important;width:100%!important;flex:0 0 100%!important;min-height:46vh!important;max-height:62vh!important;overflow-y:auto!important}#dokdae-feed *{word-break:keep-all!important;writing-mode:horizontal-tb!important}</style><script>setInterval(function(){var f=document.getElementById('dokdae-feed'),t=document.getElementById('rgon-tools-drawer');if(f){var d=f.closest('details');while(d&&d.parentNode){d.parentNode.insertBefore(f,d.nextSibling);d=f.closest('details');}}if(t&&f&&f.parentNode&&t.parentNode!==f.parentNode){f.parentNode.insertBefore(t,f);}document.querySelectorAll('div,span').forEach(function(e){if(e.children.length<=2&&/5G\s*터널|^🟢$/.test((e.textContent||'').trim()))e.style.setProperty('display','none','important');});},400);</script>"

for fn in ["rgon_alpha_chat.html","dashboard/rgon_alpha_chat.html","docs/rgon_alpha_chat.html"]:

    if os.path.exists(fn):

        s = open(fn, encoding="utf-8").read()

        open(fn, "w", encoding="utf-8").write(s.replace("</body>", p + "</body>"))

        print("OK:", fn)

subprocess.run(["git","add","-A"])

subprocess.run(["git","commit","-m","fix: rescue dokdae feed full width"])

subprocess.run(["git","push","origin","main"])

print("ALL RESCUE DONE!")


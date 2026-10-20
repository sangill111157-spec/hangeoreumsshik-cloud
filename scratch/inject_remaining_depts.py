import os

dept_dir = r"c:\Users\sangi\Downloads\shin-agent\dashboard\departments"

btn_media = '''      <a href="../rgon_alpha_chat.html" class="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 via-yellow-500 to-amber-600 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-black text-xs transition flex items-center gap-1.5 shadow-lg shadow-amber-500/25 active:scale-95">
        <span>💬 르곤-알파 1:1 독대실 ➔</span>
      </a>\n'''

btn_treasury = '''        <a href="../rgon_alpha_chat.html" class="px-3.5 py-2 rounded-xl bg-gradient-to-r from-amber-500 via-yellow-500 to-amber-600 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-black text-xs transition flex items-center gap-1.5 shadow-lg shadow-amber-500/25 active:scale-95">
          <span>💬 르곤-알파 1:1 독대실 ➔</span>
        </a>\n'''

btn_vault = '''      <a href="../rgon_alpha_chat.html" class="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 via-yellow-500 to-amber-600 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-black text-xs transition flex items-center gap-1.5 shadow-lg shadow-amber-500/25 active:scale-95">
        <span>💬 르곤-알파 1:1 독대실 ➔</span>
      </a>\n'''

# 1. dept_media.html
path_media = os.path.join(dept_dir, "dept_media.html")
with open(path_media, "r", encoding="utf-8") as f:
    c = f.read()
if "💬 르곤-알파 1:1 독대실 ➔" not in c:
    target = '<a href="/?v=850&tab=command" class="px-4 py-2 rounded-xl bg-gradient-to-r from-pink-600'
    c = c.replace(target, btn_media + "      " + target)
    with open(path_media, "w", encoding="utf-8") as f:
        f.write(c)
    print("dept_media.html updated")

# 2. dept_treasury.html
path_treasury = os.path.join(dept_dir, "dept_treasury.html")
with open(path_treasury, "r", encoding="utf-8") as f:
    c = f.read()
if "💬 르곤-알파 1:1 독대실 ➔" not in c:
    target = '<a href="/?v=1000" class="px-4 py-2 rounded-xl bg-slate-800'
    c = c.replace(target, btn_treasury + "        " + target)
    with open(path_treasury, "w", encoding="utf-8") as f:
        f.write(c)
    print("dept_treasury.html updated")

# 3. dept_vault.html
path_vault = os.path.join(dept_dir, "dept_vault.html")
with open(path_vault, "r", encoding="utf-8") as f:
    c = f.read()
if "💬 르곤-알파 1:1 독대실 ➔" not in c:
    target = '<a href="/?v=850&tab=command" class="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600'
    c = c.replace(target, btn_vault + "      " + target)
    with open(path_vault, "w", encoding="utf-8") as f:
        f.write(c)
    print("dept_vault.html updated")

print("REMAINING_DEPTS_COMPLETE")

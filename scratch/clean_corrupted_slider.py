import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Locate and clean up the corrupted slider fragment before GitHub Actions
corrupted_pat = re.compile(
    r'<!-- 2 Columns: Cloud Runs Monitor & Financial Constitution -->\s*'
    r'<div class="space-y-1">.*?<input type="range" id="dash-voice-rate-slider".*?</div>\s*</div>\s*</div>\s*',
    re.DOTALL
)

if corrupted_pat.search(html):
    html = corrupted_pat.sub('<!-- 2 Columns: Cloud Runs Monitor & Financial Constitution -->\n', html)
    print("Cleaned up corrupted dash-voice-rate-slider fragment!")
else:
    print("corrupted_pat did not match, trying alternative search...")
    # find dash-voice-rate-slider position and clean surrounding
    pos = html.find('dash-voice-rate-slider')
    if pos != -1:
        start_c = html.rfind('<!-- 2 Columns: Cloud Runs Monitor & Financial Constitution -->', 0, pos)
        grid_pos = html.find('<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">', pos)
        if start_c != -1 and grid_pos != -1:
            html = html[:start_c] + '<!-- 2 Columns: Cloud Runs Monitor & Financial Constitution -->\n      ' + html[grid_pos:]
            print("Cleaned up corrupted segment using position slicing!")

# 2. Check where tab-command ends
# The GitHub actions & Finance calculator grid starts at: <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
# inside tab-command.
# Let's inspect the transition between tab-command and tab-suno.

tab_suno_marker = '<!-- ══════════════════════════════════════════════════════════════\n     TAB 2. 🎹 Suno AI & 썸네일 프로듀싱 스튜디오'
if tab_suno_marker not in html:
    tab_suno_marker = '<div id="tab-suno"'

pos_suno = html.find(tab_suno_marker)
pos_command = html.find('<div id="tab-command"')
print(f"tab-command: {pos_command}, tab-suno: {pos_suno}")

# Segment between tab-command and tab-suno
cmd_segment = html[pos_command:pos_suno]

# We want cmd_segment to contain all command widgets, then properly close tab-command with </div>
# Let's count div balance in cmd_segment
open_divs = len(re.findall(r'<div[^>]*>', cmd_segment))
close_divs = len(re.findall(r'</div>', cmd_segment))
diff = open_divs - close_divs
print(f"In tab-command segment: open_divs={open_divs}, close_divs={close_divs}, diff={diff}")

# If open_divs > close_divs, we need to append (open_divs - close_divs) </div> at the end of tab-command
# If open_divs < close_divs, we have excess </div> that prematurely closed it.

# Let's write a robust segment repair
with open('dashboard/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Saved intermediate index.html")

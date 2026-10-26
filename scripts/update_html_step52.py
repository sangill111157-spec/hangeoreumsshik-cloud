# -*- coding: utf-8 -*-
import re
from pathlib import Path

files = [
    Path("index.html"),
    Path("dashboard/index.html"),
    Path("docs/index.html"),
    Path("rgon_alpha_chat.html"),
    Path("dashboard/rgon_alpha_chat.html"),
    Path("docs/rgon_alpha_chat.html"),
    Path("rgon_alpha_audience.html"),
]

r52_bridge = """<!-- [RGON-R52-COMMANDER-TWIN-V1-START] -->
<div id="rgon-r52-commander-twin" style="display: none !important;" data-version="v11.51-AON-COMMANDER-TWIN" data-antibody="R52" data-organ="rgon_aon_commander_twin.py" aria-hidden="true"></div>
<!-- [RGON-R52-COMMANDER-TWIN-V1-END] -->"""

for f in files:
    if not f.exists():
        continue
    content = f.read_text(encoding="utf-8")
    
    # 1. Update Version String
    content = content.replace("v11.50-AON-TOKEN-EGOLITE-MASTER", "v11.51-AON-COMMANDER-TWIN")
    
    # 2. Update Antibody Range
    content = content.replace("R1~R51", "R1~R52")
    content = content.replace("R51", "R52")
    
    # 3. Update Skill Count
    content = re.sub(r'\"skills\":\s*47', '"skills": 48', content)
    content = re.sub(r'\"antibodies\":\s*51', '"antibodies": 52', content)
    content = re.sub(r'var\s+SK\s*=\s*D\.skills\|\|47', 'var SK=D.skills||48', content)
    content = re.sub(r'AB\s*=\s*D\.antibodies\|\|51', 'AB=D.antibodies||52', content)
    content = re.sub(r'보유\s*스킬\s*\(47\)', '보유 스킬 (48)', content)
    content = re.sub(r'🍯\s*스킬\s*47개', '🍯스킬 48개', content)
    
    # 4. Insert R52 Hidden Bridge before </body> if not present
    if "rgon-r52-commander-twin" not in content:
        if "</body>" in content:
            content = content.replace("</body>", f"{r52_bridge}\n</body>")
        else:
            content += f"\n{r52_bridge}\n"
            
    # 5. Add /twin command tag to dialogue hub if not present
    old_tags = '<button class="rgnlu-tag" data-cmd="/토큰">/토큰</button>'
    new_tags = '<button class="rgnlu-tag" data-cmd="/토큰">/토큰</button> <button class="rgnlu-tag" data-cmd="/twin">/twin</button>'
    if old_tags in content and '/twin' not in content:
        content = content.replace(old_tags, new_tags)
        
    f.write_text(content, encoding="utf-8")
    print(f"Updated: {f}")

print("ALL HTML FILES UPDATED FOR STEP 52")
